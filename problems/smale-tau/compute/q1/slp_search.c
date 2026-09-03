/*
 * slp_search.c -- exhaustive search over integer straight-line programs.
 *
 * A straight-line program (SLP) is x_0 = 1, x_k = x_i o x_j (i, j < k) with
 * o in {+, -, *}.  tau(N) is the least k with x_k = N (OEIS A173419; Shub and
 * Smale 1995; Smale 1998, Problem 4).
 *
 * Normalisation (Markstrom, arXiv:1306.3091, Appendix A): an optimal program
 * for N > 0 may be assumed to have pairwise distinct, strictly positive
 * values (replace every value by its absolute value, which is again a
 * program of the same length, then remove duplicates).  We enumerate value
 * sequences in a canonical order: the queue of one-step derivable values
 * grows in blocks, and successive choices must have strictly increasing
 * queue positions (the "pending queue" order of Rokicki, OEIS A217032
 * digest).  Every normalised program has exactly one order satisfying this
 * rule (its lexicographically least valid order), so the enumeration is
 * exhaustive.  See README.md for the argument.
 *
 * Arithmetic is exact: values below 2^128 are native, larger values use a
 * limb bignum.  Nothing is dropped, saturated, or reduced mod 2^64.
 *
 * Modes:
 *   --count D [--table B]
 *        enumerate all programs of <= D steps; print the number of distinct
 *        positive integers reached within d steps for d <= D (Markstrom
 *        Fig. 1), and with --table B the least length tau(n) for n <= B.
 *   --steps L --targets FILE
 *        decide, for every target N (< 2^128) in FILE, whether tau(N) <= L.
 *        Prefixes of length L-3 are enumerated; a complete 3-step endgame
 *        decides the rest.  Prints a witness program for every hit.
 *   --endgame-test FILE --targets TFILE
 *        push the prefix values listed in FILE (one per line, after 1) and
 *        report the endgame answer for each target (for cross-checking).
 *
 * Build: gcc -O3 -march=native -fopenmp -o slp_search slp_search.c
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <omp.h>

typedef unsigned __int128 u128;

/* ------------------------------------------------------------------ */
/* Values.  big == 0: the value is (hi:lo) < 2^128.  big != 0: offset  */
/* into a per-context limb arena: arena[big] = n, arena[big+1..big+n] */
/* = little-endian 64-bit limbs, top limb nonzero, value >= 2^128.     */
/* ------------------------------------------------------------------ */
typedef struct { uint64_t lo, hi; uint32_t big; } val_t;

#define ARENA_WORDS (1u << 20)
#define MAXLIMBS 1100   /* 2^(2^16) would need 1025 limbs; depth <= 16 is asserted */

#define HBITS 14
#define HSIZE (1u << HBITS)
#define HMASK (HSIZE - 1)
enum { ST_EMPTY = 0, ST_INQ = 1, ST_INSET = 2 };

#define MAXQ 8192
#define MAXDEPTH 16

typedef struct ctx {
    uint64_t *arena; uint32_t arena_top;
    val_t hval[HSIZE]; uint8_t hstate[HSIZE];
    uint32_t hslot_stack[MAXQ]; int hslot_top;
    val_t queue[MAXQ]; int qlen;
    int qblock_start[MAXDEPTH + 2]; uint32_t arena_mark[MAXDEPTH + 2]; int hslot_mark[MAXDEPTH + 2];
    val_t set[MAXDEPTH + 2]; int nset; int setpos[MAXDEPTH + 2];
    uint64_t nodes[MAXDEPTH + 2]; uint64_t leaves; uint64_t pruned; uint64_t filtered;
    val_t sqh_val[HSIZE]; uint8_t sqh_used[HSIZE]; uint32_t sqh_slots[MAXQ]; int sqh_n;
} ctx_t;

static inline uint64_t mix64(uint64_t x) {
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x;
}
static inline int limbs_n(const ctx_t *c, const val_t *v) { return (int)c->arena[v->big]; }
static inline const uint64_t *limbs(const ctx_t *c, const val_t *v) { return &c->arena[v->big + 1]; }

static inline uint64_t vhash(const ctx_t *c, const val_t *v) {
    if (!v->big) return mix64(v->lo ^ mix64(v->hi + 0x9e3779b97f4a7c15ULL));
    int n = limbs_n(c, v); const uint64_t *L = limbs(c, v);
    uint64_t h = 0x12345678abcdefULL + (uint64_t)n;
    for (int i = 0; i < n; i++) h = mix64(h ^ L[i]);
    return h;
}
static inline bool veq(const ctx_t *c, const val_t *a, const val_t *b) {
    if (a->big == 0 && b->big == 0) return a->lo == b->lo && a->hi == b->hi;
    if (a->big == 0 || b->big == 0) return false;
    int n = limbs_n(c, a); if (n != limbs_n(c, b)) return false;
    return memcmp(limbs(c, a), limbs(c, b), (size_t)n * 8) == 0;
}
static inline int vcmp(const ctx_t *c, const val_t *a, const val_t *b) {
    if (a->big == 0 && b->big == 0) {
        if (a->hi != b->hi) return a->hi < b->hi ? -1 : 1;
        if (a->lo != b->lo) return a->lo < b->lo ? -1 : 1;
        return 0;
    }
    if (a->big == 0) return -1;
    if (b->big == 0) return 1;
    int na = limbs_n(c, a), nb = limbs_n(c, b);
    if (na != nb) return na < nb ? -1 : 1;
    const uint64_t *A = limbs(c, a), *B = limbs(c, b);
    for (int i = na - 1; i >= 0; i--) if (A[i] != B[i]) return A[i] < B[i] ? -1 : 1;
    return 0;
}
static inline bool viszero(const val_t *v) { return v->big == 0 && v->lo == 0 && v->hi == 0; }
static inline int bitlen128(uint64_t lo, uint64_t hi) {
    if (hi) return 128 - __builtin_clzll(hi);
    if (lo) return 64 - __builtin_clzll(lo);
    return 0;
}
static inline int vbitlen(const ctx_t *c, const val_t *v) {
    if (!v->big) return bitlen128(v->lo, v->hi);
    int n = limbs_n(c, v); return 64 * (n - 1) + 64 - __builtin_clzll(limbs(c, v)[n - 1]);
}
static inline void to_limbs(const ctx_t *c, const val_t *v, uint64_t *out, int *n) {
    if (!v->big) { out[0] = v->lo; out[1] = v->hi; *n = v->hi ? 2 : (v->lo ? 1 : 0); return; }
    *n = limbs_n(c, v); memcpy(out, limbs(c, v), (size_t)(*n) * 8);
}
static inline val_t from_limbs(ctx_t *c, uint64_t *L, int n) {
    while (n > 0 && L[n - 1] == 0) n--;
    val_t r;
    if (n <= 2) { r.lo = n >= 1 ? L[0] : 0; r.hi = n >= 2 ? L[1] : 0; r.big = 0; return r; }
    if (c->arena_top + (uint32_t)n + 1 >= ARENA_WORDS) { fprintf(stderr, "FATAL arena overflow\n"); exit(2); }
    r.lo = 0; r.hi = 0; r.big = c->arena_top;
    c->arena[c->arena_top] = (uint64_t)n;
    memcpy(&c->arena[c->arena_top + 1], L, (size_t)n * 8);
    c->arena_top += (uint32_t)n + 1;
    return r;
}
static val_t vadd(ctx_t *c, const val_t *a, const val_t *b) {
    if (!a->big && !b->big) {
        u128 x = ((u128)a->hi << 64) | a->lo, y = ((u128)b->hi << 64) | b->lo, s = x + y;
        if (s >= x) { val_t r = { (uint64_t)s, (uint64_t)(s >> 64), 0 }; return r; }
        uint64_t L[3] = { (uint64_t)s, (uint64_t)(s >> 64), 1 };
        return from_limbs(c, L, 3);
    }
    uint64_t A[MAXLIMBS], B[MAXLIMBS], R[MAXLIMBS + 1]; int na, nb;
    to_limbs(c, a, A, &na); to_limbs(c, b, B, &nb);
    int n = na > nb ? na : nb; if (n + 1 > MAXLIMBS) { fprintf(stderr, "FATAL limb overflow add\n"); exit(2); }
    u128 carry = 0;
    for (int i = 0; i < n; i++) { u128 s = carry + (i < na ? A[i] : 0) + (i < nb ? B[i] : 0); R[i] = (uint64_t)s; carry = s >> 64; }
    R[n] = (uint64_t)carry;
    return from_limbs(c, R, n + 1);
}
static val_t vsub(ctx_t *c, const val_t *a, const val_t *b) {   /* a >= b */
    if (!a->big && !b->big) {
        u128 x = ((u128)a->hi << 64) | a->lo, y = ((u128)b->hi << 64) | b->lo, d = x - y;
        val_t r = { (uint64_t)d, (uint64_t)(d >> 64), 0 }; return r;
    }
    uint64_t A[MAXLIMBS], B[MAXLIMBS], R[MAXLIMBS]; int na, nb;
    to_limbs(c, a, A, &na); to_limbs(c, b, B, &nb);
    int64_t borrow = 0;
    for (int i = 0; i < na; i++) {
        __int128 d = (__int128)A[i] - (i < nb ? B[i] : 0) - borrow;
        if (d < 0) { d += ((__int128)1 << 64); borrow = 1; } else borrow = 0;
        R[i] = (uint64_t)d;
    }
    if (borrow) { fprintf(stderr, "FATAL vsub negative\n"); exit(2); }
    return from_limbs(c, R, na);
}
static val_t vmul(ctx_t *c, const val_t *a, const val_t *b) {
    if (!a->big && !b->big && !a->hi && !b->hi) {
        u128 p = (u128)a->lo * b->lo;
        val_t r = { (uint64_t)p, (uint64_t)(p >> 64), 0 }; return r;
    }
    uint64_t A[MAXLIMBS], B[MAXLIMBS], R[2 * MAXLIMBS]; int na, nb;
    to_limbs(c, a, A, &na); to_limbs(c, b, B, &nb);
    if (na + nb > MAXLIMBS) { fprintf(stderr, "FATAL limb overflow mul (%d+%d)\n", na, nb); exit(2); }
    memset(R, 0, (size_t)(na + nb) * 8);
    for (int i = 0; i < na; i++) {
        u128 carry = 0;
        for (int j = 0; j < nb; j++) { u128 t = (u128)A[i] * B[j] + R[i + j] + carry; R[i + j] = (uint64_t)t; carry = t >> 64; }
        R[i + nb] = (uint64_t)carry;
    }
    return from_limbs(c, R, na + nb);
}
/* q = a / b if b divides a (b > 0); exact for all sizes */
static bool vdivexact(ctx_t *c, const val_t *a, const val_t *b, val_t *q) {
    if (viszero(b)) return false;
    if (!a->big && !b->big) {
        u128 x = ((u128)a->hi << 64) | a->lo, y = ((u128)b->hi << 64) | b->lo;
        if (x % y) return false;
        u128 r = x / y; q->lo = (uint64_t)r; q->hi = (uint64_t)(r >> 64); q->big = 0; return true;
    }
    if (vcmp(c, a, b) < 0) return false;
    uint64_t A[MAXLIMBS], B[MAXLIMBS]; int na, nb;
    to_limbs(c, a, A, &na); to_limbs(c, b, B, &nb);
    if (nb == 1) {
        uint64_t Q[MAXLIMBS]; u128 rem = 0;
        for (int i = na - 1; i >= 0; i--) { u128 cur = (rem << 64) | A[i]; Q[i] = (uint64_t)(cur / B[0]); rem = cur % B[0]; }
        if (rem) return false;
        *q = from_limbs(c, Q, na); return true;
    }
    /* binary long division (rare path: both operands >= 2^64) */
    int shift = vbitlen(c, a) - vbitlen(c, b);
    uint64_t R[MAXLIMBS], D[MAXLIMBS + 1], Q[MAXLIMBS];
    memcpy(R, A, (size_t)na * 8); memset(Q, 0, (size_t)na * 8);
    int nd = na + 1; memset(D, 0, (size_t)nd * 8);
    int ws = shift / 64, bs = shift % 64;
    for (int i = 0; i < nb; i++) { D[i + ws] |= B[i] << bs; if (bs && i + ws + 1 < nd) D[i + ws + 1] |= B[i] >> (64 - bs); }
    for (int s = shift; s >= 0; s--) {
        int ge = 1;
        for (int i = na - 1; i >= 0; i--) { if (R[i] != D[i]) { ge = R[i] > D[i]; break; } }
        if (ge && D[na] == 0) {
            int64_t borrow = 0;
            for (int i = 0; i < na; i++) { __int128 d = (__int128)R[i] - D[i] - borrow; if (d < 0) { d += ((__int128)1 << 64); borrow = 1; } else borrow = 0; R[i] = (uint64_t)d; }
            Q[s / 64] |= 1ULL << (s % 64);
        }
        for (int i = 0; i < nd; i++) D[i] = (D[i] >> 1) | (i + 1 < nd ? D[i + 1] << 63 : 0);
    }
    for (int i = 0; i < na; i++) if (R[i]) return false;
    *q = from_limbs(c, Q, na); return true;
}
static bool vhalf(ctx_t *c, const val_t *a, val_t *q) {
    if (!a->big) { if (a->lo & 1) return false; u128 x = (((u128)a->hi << 64) | a->lo) >> 1; q->lo = (uint64_t)x; q->hi = (uint64_t)(x >> 64); q->big = 0; return true; }
    if (limbs(c, a)[0] & 1) return false;
    uint64_t A[MAXLIMBS]; int na; to_limbs(c, a, A, &na);
    for (int i = 0; i < na; i++) A[i] = (A[i] >> 1) | (i + 1 < na ? A[i + 1] << 63 : 0);
    *q = from_limbs(c, A, na); return true;
}
static inline val_t vsmall(uint64_t x) { val_t r = { x, 0, 0 }; return r; }

/* exact integer square root test for values < 2^128 */
static bool visqrt128(const val_t *a, val_t *r) {
    if (a->big) return false;
    u128 x = ((u128)a->hi << 64) | a->lo, res = 0, bit = (u128)1 << 126;
    while (bit > x) bit >>= 2;
    while (bit) { if (x >= res + bit) { x -= res + bit; res = (res >> 1) + bit; } else res >>= 1; bit >>= 2; }
    if (x) return false;
    r->lo = (uint64_t)res; r->hi = (uint64_t)(res >> 64); r->big = 0; return true;
}

/* ---- membership hash (queue + set), LIFO deletion ---- */
static inline uint32_t hfind(ctx_t *c, const val_t *v) {
    uint32_t s = (uint32_t)(vhash(c, v) & HMASK);
    while (c->hstate[s] != ST_EMPTY) { if (veq(c, &c->hval[s], v)) return s; s = (s + 1) & HMASK; }
    return s;
}
static inline int hstate_of(ctx_t *c, const val_t *v) { return c->hstate[hfind(c, v)]; }
static inline void hinsert_at(ctx_t *c, uint32_t s, const val_t *v, int st) {
    if (c->hslot_top >= MAXQ) { fprintf(stderr, "FATAL hash stack overflow\n"); exit(2); }
    c->hval[s] = *v; c->hstate[s] = (uint8_t)st; c->hslot_stack[c->hslot_top++] = s;
}
/* ---- squares hash (per leaf) ---- */
static inline void sqh_clear(ctx_t *c) { for (int i = 0; i < c->sqh_n; i++) c->sqh_used[c->sqh_slots[i]] = 0; c->sqh_n = 0; }
static inline void sqh_insert(ctx_t *c, const val_t *v) {
    uint32_t s = (uint32_t)(vhash(c, v) & HMASK);
    while (c->sqh_used[s]) { if (veq(c, &c->sqh_val[s], v)) return; s = (s + 1) & HMASK; }
    c->sqh_val[s] = *v; c->sqh_used[s] = 1; c->sqh_slots[c->sqh_n++] = s;
}
static inline bool sqh_has(ctx_t *c, const val_t *v) {
    uint32_t s = (uint32_t)(vhash(c, v) & HMASK);
    while (c->sqh_used[s]) { if (veq(c, &c->sqh_val[s], v)) return true; s = (s + 1) & HMASK; }
    return false;
}

/* ------------------------------------------------------------------ */
/* Targets (all < 2^128, so val_t is context independent)              */
/* ------------------------------------------------------------------ */
#define MAXT 1024
typedef struct { char name[512]; char dec[512]; val_t v; int bits; int best; char witness[8192]; uint64_t *div; uint64_t divcap; val_t *divv; uint64_t primes[64]; int exps[64]; int np; uint64_t ndiv; uint64_t m5; bool is_power; } target_t;
static target_t targets[MAXT]; static int ntargets = 0;
static int g_minbits = 1 << 30;

static bool parse_u128(const char *s, val_t *out) {
    u128 x = 0; int digits = 0;
    for (const char *p = s; *p; p++) {
        if (*p < '0' || *p > '9') continue;
        if (x > (((u128)-1) - 9) / 10) return false;
        x = x * 10 + (u128)(*p - '0'); digits++;
    }
    if (!digits) return false;
    out->lo = (uint64_t)x; out->hi = (uint64_t)(x >> 64); out->big = 0; return true;
}
static void print_val(ctx_t *c, const val_t *v, char *buf, size_t cap) {
    uint64_t A[MAXLIMBS]; int na; to_limbs(c, v, A, &na);
    if (na == 0) { snprintf(buf, cap, "0"); return; }
    char chunks[MAXLIMBS * 2][20]; int nch = 0;
    while (na > 0) {
        u128 rem = 0;
        for (int i = na - 1; i >= 0; i--) { u128 cur = (rem << 64) | A[i]; A[i] = (uint64_t)(cur / 1000000000000000000ULL); rem = cur % 1000000000000000000ULL; }
        while (na > 0 && A[na - 1] == 0) na--;
        snprintf(chunks[nch++], 20, "%018llu", (unsigned long long)rem);
    }
    const char *first = chunks[nch - 1]; while (*first == '0' && *(first + 1)) first++;
    size_t pos = (size_t)snprintf(buf, cap, "%s", first);
    for (int i = nch - 2; i >= 0 && pos < cap; i--) pos += (size_t)snprintf(buf + pos, cap - pos, "%s", chunks[i]);
}

/* ------------------------------------------------------------------ */
/* Search state                                                         */
/* ------------------------------------------------------------------ */
static int g_depth = 0, g_steps = 0, g_split = 5;
static bool g_countmode = false, g_endgame_test = false;
static uint64_t g_table_bound = 0;

static void ctx_init(ctx_t *c) {
    memset(c, 0, sizeof *c);
    c->arena = (uint64_t *)malloc(sizeof(uint64_t) * ARENA_WORDS);
    if (!c->arena) { fprintf(stderr, "FATAL malloc\n"); exit(2); }
    c->arena_top = 1;
    c->set[0] = vsmall(1); c->nset = 1; c->setpos[0] = -1;
    uint32_t s = hfind(c, &c->set[0]); hinsert_at(c, s, &c->set[0], ST_INSET);
    val_t two = vsmall(2);
    c->queue[c->qlen++] = two; s = hfind(c, &two); hinsert_at(c, s, &two, ST_INQ);
}
static inline void enqueue(ctx_t *c, const val_t *r) {
    uint32_t s = hfind(c, r);
    if (c->hstate[s] == ST_EMPTY) {
        if (c->qlen >= MAXQ) { fprintf(stderr, "FATAL queue overflow\n"); exit(2); }
        c->queue[c->qlen++] = *r; hinsert_at(c, s, r, ST_INQ);
    }
}
static inline void push_value(ctx_t *c, const val_t *v, int pos) {
    int d = c->nset;
    if (d > MAXDEPTH) { fprintf(stderr, "FATAL depth\n"); exit(2); }
    c->qblock_start[d] = c->qlen; c->arena_mark[d] = c->arena_top; c->hslot_mark[d] = c->hslot_top;
    c->set[d] = *v; c->setpos[d] = pos; c->nset = d + 1;
    c->hstate[hfind(c, v)] = ST_INSET;
    for (int i = 0; i <= d; i++) {
        const val_t *w = &c->set[i]; val_t r;
        r = vadd(c, v, w); enqueue(c, &r);
        r = vmul(c, v, w); enqueue(c, &r);
        int cmp = vcmp(c, v, w);
        if (cmp != 0) { r = cmp > 0 ? vsub(c, v, w) : vsub(c, w, v); enqueue(c, &r); }
    }
}
static inline void pop_value(ctx_t *c) {
    int d = c->nset - 1;
    while (c->hslot_top > c->hslot_mark[d]) { uint32_t s = c->hslot_stack[--c->hslot_top]; c->hstate[s] = ST_EMPTY; }
    c->qlen = c->qblock_start[d];
    c->hstate[hfind(c, &c->set[d])] = ST_INQ;
    c->arena_top = c->arena_mark[d];
    c->nset = d;
}

/* ---- witness: values list plus one derivation per step ---- */
static void explain_program(ctx_t *c, const val_t *extra, int nextra, char *out, size_t cap) {
    val_t vals[MAXDEPTH + 8]; int n = 0;
    for (int i = 0; i < c->nset; i++) vals[n++] = c->set[i];
    for (int i = 0; i < nextra; i++) vals[n++] = extra[i];
    size_t pos = 0;
    pos += (size_t)snprintf(out + pos, cap - pos, "{\"values\": [");
    for (int k = 0; k < n; k++) { char b[2048]; print_val(c, &vals[k], b, sizeof b); pos += (size_t)snprintf(out + pos, cap - pos, "%s\"%s\"", k ? "," : "", b); }
    pos += (size_t)snprintf(out + pos, cap - pos, "], \"ops\": [");
    bool first = true;
    for (int k = 1; k < n; k++) {
        bool done = false;
        for (int i = 0; i < k && !done; i++) for (int j = i; j < k && !done; j++) {
            val_t r = vadd(c, &vals[i], &vals[j]);
            if (veq(c, &r, &vals[k])) { pos += (size_t)snprintf(out + pos, cap - pos, "%s[%d,%d,\"+\"]", first ? "" : ",", i, j); done = true; first = false; break; }
            r = vmul(c, &vals[i], &vals[j]);
            if (veq(c, &r, &vals[k])) { pos += (size_t)snprintf(out + pos, cap - pos, "%s[%d,%d,\"*\"]", first ? "" : ",", i, j); done = true; first = false; break; }
            int cmp = vcmp(c, &vals[i], &vals[j]);
            if (cmp != 0) {
                r = cmp > 0 ? vsub(c, &vals[i], &vals[j]) : vsub(c, &vals[j], &vals[i]);
                if (veq(c, &r, &vals[k])) { pos += (size_t)snprintf(out + pos, cap - pos, "%s[%d,%d,\"-\"]", first ? "" : ",", cmp > 0 ? i : j, cmp > 0 ? j : i); done = true; first = false; break; }
            }
        }
        if (!done) { pos += (size_t)snprintf(out + pos, cap - pos, "%s[\"?\"]", first ? "" : ","); first = false; }
    }
    snprintf(out + pos, cap - pos, "]}");
}
static void record_hit(ctx_t *c, int t, int steps, const val_t *extra, int nextra) {
    uint32_t mark = c->arena_top;
    #pragma omp critical(hit)
    {
        if (steps < targets[t].best) { targets[t].best = steps; explain_program(c, extra, nextra, targets[t].witness, sizeof targets[t].witness); }
    }
    c->arena_top = mark;
}

/* ------------------------------------------------------------------ */
/* Divisor sets: for every target N (< 2^128) the set of all divisors,  */
/* so "x | N" is a hash lookup instead of a 128-bit division.           */
/* ------------------------------------------------------------------ */
/* deterministic Miller-Rabin for 64-bit integers */
static uint64_t mulmod64(uint64_t a, uint64_t b, uint64_t m) { return (uint64_t)(((u128)a * b) % m); }
static uint64_t powmod64(uint64_t a, uint64_t e, uint64_t m) { uint64_t r = 1; a %= m; while (e) { if (e & 1) r = mulmod64(r, a, m); a = mulmod64(a, a, m); e >>= 1; } return r; }
static bool is_prime64(uint64_t n) {
    if (n < 2) return false;
    static const uint64_t small[] = { 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37 };
    for (int i = 0; i < 12; i++) { if (n == small[i]) return true; if (n % small[i] == 0) return false; }
    uint64_t d = n - 1; int s = 0; while (!(d & 1)) { d >>= 1; s++; }
    for (int i = 0; i < 12; i++) {
        uint64_t x = powmod64(small[i], d, n);
        if (x == 1 || x == n - 1) continue;
        bool comp = true;
        for (int r = 1; r < s; r++) { x = mulmod64(x, x, n); if (x == n - 1) { comp = false; break; } }
        if (comp) return false;
    }
    return true;
}
static void build_divisors(target_t *t) {
    u128 N = ((u128)t->v.hi << 64) | t->v.lo;
    /* trial-divide N (targets are smooth: factorials, primorials); fall back
       to trial division up to 2^20 then treat the cofactor as prime if it is
       (it always is for our targets; verified by the Python replay). */
    u128 m = N; uint64_t primes[64]; int exps[64]; int np = 0;
    for (uint64_t p = 2; p < 2000000 && (u128)p * p <= m; p += (p == 2 ? 1 : 2)) {
        if (m % p == 0) { int e = 0; while (m % p == 0) { m /= p; e++; } primes[np] = p; exps[np] = e; np++; }
    }
    if (m > 1) {
        if (m >> 64) { fprintf(stderr, "FATAL: target cofactor too large to factor: %s\n", t->dec); exit(2); }
        if (!is_prime64((uint64_t)m)) { fprintf(stderr, "FATAL: target cofactor %llu is composite; cannot build divisor set for %s\n", (unsigned long long)m, t->dec); exit(2); }
        primes[np] = (uint64_t)m; exps[np] = 1; np++;
    }
    uint64_t ndiv = 1; for (int i = 0; i < np; i++) ndiv *= (uint64_t)(exps[i] + 1);
    t->np = np; for (int i = 0; i < np; i++) { t->primes[i] = primes[i]; t->exps[i] = exps[i]; }
    t->ndiv = ndiv;
    if (ndiv > 400000) { t->div = NULL; t->divv = NULL; t->divcap = 0; return; }   /* use trial division instead */
    uint64_t cap = 4; while (cap < 2 * ndiv) cap <<= 1;
    t->divcap = cap; t->divv = calloc(cap, sizeof(val_t)); t->div = calloc(cap, sizeof(uint64_t));
    if (!t->divv || !t->div) { fprintf(stderr, "FATAL calloc divisors\n"); exit(2); }
    /* enumerate divisors */
    int idx[64] = {0};
    for (;;) {
        u128 d = 1; for (int i = 0; i < np; i++) for (int e = 0; e < idx[i]; e++) d *= primes[i];
        val_t dv = { (uint64_t)d, (uint64_t)(d >> 64), 0 };
        uint64_t h = mix64(dv.lo ^ mix64(dv.hi + 0x9e3779b97f4a7c15ULL)) & (cap - 1);
        while (t->div[h]) h = (h + 1) & (cap - 1);
        t->div[h] = 1; t->divv[h] = dv;
        int i = 0; while (i < np) { if (++idx[i] <= exps[i]) break; idx[i] = 0; i++; }
        if (i == np) break;
    }
}
static inline bool divides_target(const target_t *t, const val_t *x) {
    if (x->big) return false;
    if (!t->div) {   /* trial division by the target's primes */
        u128 y = ((u128)x->hi << 64) | x->lo;
        if (y == 0) return false;
        for (int i = 0; i < t->np; i++) {
            uint64_t p = t->primes[i]; int e = 0;
            if (y >> 64) { while (y % p == 0 && e < t->exps[i]) { y /= p; e++; } }
            else { uint64_t z = (uint64_t)y; while (z % p == 0 && e < t->exps[i]) { z /= p; e++; } y = z; }
            if (y == 1) return true;
        }
        return y == 1;
    }
    uint64_t h = mix64(x->lo ^ mix64(x->hi + 0x9e3779b97f4a7c15ULL)) & (t->divcap - 1);
    while (t->div[h]) { if (t->divv[h].lo == x->lo && t->divv[h].hi == x->hi) return true; h = (h + 1) & (t->divcap - 1); }
    return false;
}
/* quotient N / x, assuming x | N */
static inline val_t target_quot(const target_t *t, const val_t *x) {
    u128 N = ((u128)t->v.hi << 64) | t->v.lo, X = ((u128)x->hi << 64) | x->lo, q = N / X;
    val_t r = { (uint64_t)q, (uint64_t)(q >> 64), 0 }; return r;
}

/* remainder a mod b for arbitrary sizes (b > 0); slow generic path */
static val_t vmod(ctx_t *c, const val_t *a, const val_t *b) {
    if (!a->big && !b->big) {
        u128 x = ((u128)a->hi << 64) | a->lo, y = ((u128)b->hi << 64) | b->lo, r = x % y;
        val_t v = { (uint64_t)r, (uint64_t)(r >> 64), 0 }; return v;
    }
    if (vcmp(c, a, b) < 0) return *a;
    uint64_t A[MAXLIMBS], B[MAXLIMBS]; int na, nb;
    to_limbs(c, a, A, &na); to_limbs(c, b, B, &nb);
    if (nb == 1) { u128 rem = 0; for (int i = na - 1; i >= 0; i--) { u128 cur = (rem << 64) | A[i]; rem = cur % B[0]; } val_t v = { (uint64_t)rem, (uint64_t)(rem >> 64), 0 }; return v; }
    int shift = vbitlen(c, a) - vbitlen(c, b);
    uint64_t R[MAXLIMBS], D[MAXLIMBS + 1];
    memcpy(R, A, (size_t)na * 8);
    int nd = na + 1; memset(D, 0, (size_t)nd * 8);
    int ws = shift / 64, bs = shift % 64;
    for (int i = 0; i < nb; i++) { D[i + ws] |= B[i] << bs; if (bs && i + ws + 1 < nd) D[i + ws + 1] |= B[i] >> (64 - bs); }
    for (int s = shift; s >= 0; s--) {
        int ge = 1;
        for (int i = na - 1; i >= 0; i--) { if (R[i] != D[i]) { ge = R[i] > D[i]; break; } }
        if (ge && D[na] == 0) {
            int64_t borrow = 0;
            for (int i = 0; i < na; i++) { __int128 d = (__int128)R[i] - D[i] - borrow; if (d < 0) { d += ((__int128)1 << 64); borrow = 1; } else borrow = 0; R[i] = (uint64_t)d; }
        }
        for (int i = 0; i < nd; i++) D[i] = (D[i] >> 1) | (i + 1 < nd ? D[i + 1] << 63 : 0);
    }
    return from_limbs(c, R, na);
}

/* ------------------------------------------------------------------ */
/* Endgame: is target t reachable from the current set in <= 3 steps?   */
/* Complete case analysis (README.md).  Q = queue entries in state      */
/* ST_INQ = values derivable in one step and not in the set.            */
/*                                                                      */
/* Size filters.  Let M = max S, qmax = max Q (<= M^2).  In three steps */
/* the largest values are y1 <= M^2, y2 <= M^4, N <= M^8, but N = M^8   */
/* needs N = y2*y2 and N = y1^3 needs a cube; for a target that is       */
/* neither a square nor a cube, N <= M^5.  Every candidate is checked   */
/* against the range of the set it must belong to before a hash lookup. */
/* ------------------------------------------------------------------ */
#define HIT1() do { record_hit(c, t, d + 1, N, 1); return true; } while (0)
#define HIT2(y1v) do { val_t ex[2] = { (y1v), *N }; record_hit(c, t, d + 2, ex, 2); return true; } while (0)
#define HIT3(y1v, y2v) do { val_t ex[3] = { (y1v), (y2v), *N }; record_hit(c, t, d + 3, ex, 3); return true; } while (0)

typedef struct {
    val_t rem[MAXDEPTH + 2][MAXDEPTH + 2]; uint32_t remdone[MAXDEPTH + 2];  /* rem[i][j] = set[i] mod set[j], lazily */
    val_t smax, qmin, qmax; int qcount;
} leafinfo_t;

static inline const val_t *residue(ctx_t *c, leafinfo_t *li, int i, int j) {
    if (!(li->remdone[i] & (1u << j))) { li->rem[i][j] = vmod(c, &c->set[i], &c->set[j]); li->remdone[i] |= 1u << j; }
    return &li->rem[i][j];
}
static inline bool in_range(ctx_t *c, const val_t *x, const val_t *lo, const val_t *hi) { return vcmp(c, x, lo) >= 0 && vcmp(c, x, hi) <= 0; }
#define INQ(x)   (in_range(c, &(x), &li->qmin, &li->qmax) && hstate_of(c, &(x)) == ST_INQ)
#define INSET(x) (vcmp(c, &(x), &li->smax) <= 0 && hstate_of(c, &(x)) == ST_INSET)

static bool endgame(ctx_t *c, int t, leafinfo_t *li) {
    target_t *T = &targets[t];
    const val_t *N = &T->v;
    int d = c->nset - 1, ns = c->nset;
    if (INSET((*N))) { record_hit(c, t, d, NULL, 0); return true; }
    if (INQ((*N))) HIT1();
    val_t y1, y2, tmp, tmp2;
    const val_t one = vsmall(1);

    /* ---- case B: N = y1 o b (b in S) or y1 + y1 or y1 * y1, y1 in Q ---- */
    for (int i = 0; i < ns; i++) {
        const val_t *b = &c->set[i];
        int cmp = vcmp(c, N, b);
        if (cmp > 0) { y1 = vsub(c, N, b); if (INQ(y1)) HIT2(y1); }
        if (cmp < 0) { y1 = vsub(c, b, N); if (INQ(y1)) HIT2(y1); }
        y1 = vadd(c, N, b); if (INQ(y1)) HIT2(y1);
        if (divides_target(T, b)) { y1 = target_quot(T, b); if (INQ(y1)) HIT2(y1); }
    }
    if (vhalf(c, N, &y1) && INQ(y1)) HIT2(y1);
    if (visqrt128(N, &y1) && INQ(y1)) HIT2(y1);

    /* ---- case C-ii: N = y2 o y1, y1 in Q, y2 derived from S u {y1}, y2 not in S ---- */
    /* thresholds: (a) needs N - y1 or N + y1 or y1 - N or N / y1 in Q. */
    for (int q = 0; q < c->qlen; q++) {
        y1 = c->queue[q];
        if (c->hstate[hfind(c, &y1)] != ST_INQ) continue;
        int cmp = vcmp(c, N, &y1);
        bool y1divN = (cmp > 0) && divides_target(T, &y1);
        val_t quot; if (y1divN) quot = target_quot(T, &y1);
        /* (a) y2 in Q */
        if (cmp > 0) { y2 = vsub(c, N, &y1); if (INQ(y2)) HIT3(y1, y2); }
        if (cmp < 0) { y2 = vsub(c, &y1, N); if (INQ(y2)) HIT3(y1, y2); }
        y2 = vadd(c, N, &y1); if (INQ(y2)) HIT3(y1, y2);
        if (y1divN && INQ(quot)) HIT3(y1, quot);
        /* (b) y2 = y1 o cc, cc in S; solve for cc (see README) */
        tmp = vadd(c, &y1, &y1);                                   /* 2 y1 */
        int c2 = vcmp(c, N, &tmp);
        if (c2 > 0) { tmp2 = vsub(c, N, &tmp); if (INSET(tmp2)) { y2 = vadd(c, &y1, &tmp2); HIT3(y1, y2); } }
        if (c2 < 0) { tmp2 = vsub(c, &tmp, N); if (INSET(tmp2)) { y2 = cmp > 0 ? vsub(c, N, &y1) : vsub(c, &y1, N); HIT3(y1, y2); } }
        tmp2 = vadd(c, N, &tmp); if (INSET(tmp2)) { y2 = vsub(c, &tmp2, &y1); HIT3(y1, y2); }
        if (y1divN) {
            int cq = vcmp(c, &quot, &y1);
            if (cq > 0) { tmp2 = vsub(c, &quot, &y1); if (INSET(tmp2)) { y2 = quot; HIT3(y1, y2); } }
            if (cq < 0) { tmp2 = vsub(c, &y1, &quot); if (INSET(tmp2)) { y2 = quot; HIT3(y1, y2); } }
            tmp2 = vadd(c, &quot, &y1); if (INSET(tmp2)) { y2 = quot; HIT3(y1, y2); }
            if (vcmp(c, &quot, &one) > 0) { tmp2 = vsub(c, &quot, &one); if (INSET(tmp2)) { y2 = vsub(c, N, &y1); HIT3(y1, y2); } }
            tmp2 = vadd(c, &quot, &one); if (INSET(tmp2)) { y2 = vadd(c, N, &y1); HIT3(y1, y2); }
            if (!y1.big) { val_t sq = vmul(c, &y1, &y1); if (divides_target(T, &sq)) { tmp2 = target_quot(T, &sq); if (INSET(tmp2)) { y2 = quot; HIT3(y1, y2); } } }
        }
        /* (c) cc = y1: y2 = 2 y1 or y1^2; N in {3 y1, 2 y1^2, y1^2 + y1, y1^2 - y1, y1^3} */
        if (cmp > 0) {
            tmp2 = vadd(c, &tmp, &y1); if (veq(c, &tmp2, N)) { y2 = tmp; HIT3(y1, y2); }
            if (vbitlen(c, &y1) * 2 <= T->bits + 1) {
                val_t sq = vmul(c, &y1, &y1);
                tmp2 = vadd(c, &sq, &sq); if (veq(c, &tmp2, N)) { y2 = tmp; HIT3(y1, y2); }
                tmp2 = vadd(c, &sq, &y1); if (veq(c, &tmp2, N)) { y2 = sq; HIT3(y1, y2); }
                if (vcmp(c, &sq, &y1) > 0) { tmp2 = vsub(c, &sq, &y1); if (veq(c, &tmp2, N)) { y2 = sq; HIT3(y1, y2); } }
                if (vbitlen(c, &y1) * 3 <= T->bits + 2) { tmp2 = vmul(c, &sq, &y1); if (veq(c, &tmp2, N)) { y2 = sq; HIT3(y1, y2); } }
            }
        }
    }

    /* ---- case C-i: N = y2 o z, z in S u {y2}; y2 = y1 o cc, cc in S u {y1}; y1 in Q ---- */
    enum { K_NMINUSB, K_NPLUSB, K_BMINUSN, K_NDIVB, K_NHALF, K_NSQRT };
    val_t C2[4 * (MAXDEPTH + 2) + 2]; int kind[4 * (MAXDEPTH + 2) + 2], bidx[4 * (MAXDEPTH + 2) + 2]; int n2 = 0;
    for (int i = 0; i < ns; i++) {
        const val_t *b = &c->set[i];
        int cmp = vcmp(c, N, b);
        if (cmp > 0) { C2[n2] = vsub(c, N, b); kind[n2] = K_NMINUSB; bidx[n2++] = i; }
        if (cmp < 0) { C2[n2] = vsub(c, b, N); kind[n2] = K_BMINUSN; bidx[n2++] = i; }
        C2[n2] = vadd(c, N, b); kind[n2] = K_NPLUSB; bidx[n2++] = i;
        if (divides_target(T, b)) { C2[n2] = target_quot(T, b); kind[n2] = K_NDIVB; bidx[n2++] = i; }
    }
    if (vhalf(c, N, &tmp)) { C2[n2] = tmp; kind[n2] = K_NHALF; bidx[n2++] = -1; }
    if (visqrt128(N, &tmp)) { C2[n2] = tmp; kind[n2] = K_NSQRT; bidx[n2++] = -1; }
    /* additive sub-case needs y2 <= qmax + smax; multiplicative needs y2 <= qmax * smax */
    val_t addlim = vadd(c, &li->qmax, &li->smax);          /* y2 = y1 + cc or |y1 - cc|, cc in S */
    val_t mullim = vmul(c, &li->qmax, &li->smax);          /* y2 = y1 * cc, cc in S */
    val_t dbllim = vadd(c, &li->qmax, &li->qmax);          /* y2 = y1 + y1 */
    val_t sqlim = vmul(c, &li->qmax, &li->qmax);           /* y2 = y1 * y1 */
    val_t nmod[MAXDEPTH + 2]; uint32_t nmoddone = 0;
    for (int k = 0; k < n2; k++) {
        y2 = C2[k];
        if (viszero(&y2)) continue;
        bool canadd = vcmp(c, &y2, &addlim) <= 0, canmul = vcmp(c, &y2, &mullim) <= 0;
        bool candbl = vcmp(c, &y2, &dbllim) <= 0, cansq = vcmp(c, &y2, &sqlim) <= 0;
        if (!canadd && !canmul && !candbl && !cansq) continue;
        if (hstate_of(c, &y2) != ST_EMPTY) continue;   /* y2 in S or Q: shorter cases */
        for (int j = 0; j < ns; j++) {
            const val_t *cc = &c->set[j];
            if (canadd) {
                int cmp = vcmp(c, &y2, cc);
                if (cmp > 0) { y1 = vsub(c, &y2, cc); if (INQ(y1)) HIT3(y1, y2); }
                if (cmp < 0) { y1 = vsub(c, cc, &y2); if (INQ(y1)) HIT3(y1, y2); }
                y1 = vadd(c, &y2, cc); if (INQ(y1)) HIT3(y1, y2);
            }
            if (j == 0 || !canmul) continue;
            /* y2 = y1 * cc : does cc divide y2 ?  Decided by residues, no division. */
            bool div = false; int bi = bidx[k];
            if (kind[k] == K_NMINUSB || kind[k] == K_BMINUSN || kind[k] == K_NPLUSB) {
                if (!(nmoddone & (1u << j))) { nmod[j] = vmod(c, N, cc); nmoddone |= 1u << j; }
                const val_t *rb = residue(c, li, bi, j);
                if (kind[k] == K_NPLUSB) { tmp = vadd(c, &nmod[j], rb); div = viszero(&tmp) || veq(c, &tmp, cc); }
                else div = veq(c, &nmod[j], rb);
            } else if (kind[k] == K_NDIVB) { if (!c->set[bi].big && !cc->big) { tmp = vmul(c, &c->set[bi], cc); div = divides_target(T, &tmp); } }
            else if (kind[k] == K_NHALF) { if (!cc->big) { tmp = vadd(c, cc, cc); div = divides_target(T, &tmp); } }
            else div = vdivexact(c, &y2, cc, &tmp);
            if (div) {
                if (!y2.big || (!cc->big && !cc->hi)) {   /* fast exact division */
                    if (!vdivexact(c, &y2, cc, &y1)) { fprintf(stderr, "FATAL residue logic\n"); exit(4); }
                    if (INQ(y1)) HIT3(y1, y2);
                } else {   /* both operands large: find y1 in Q by bit length and multiply back */
                    int need = vbitlen(c, &y2) - vbitlen(c, cc);
                    for (int q = 0; q < c->qlen; q++) {
                        if (c->hstate[hfind(c, &c->queue[q])] != ST_INQ) continue;
                        int bl = vbitlen(c, &c->queue[q]); if (bl != need && bl != need + 1) continue;
                        tmp = vmul(c, &c->queue[q], cc); if (veq(c, &tmp, &y2)) HIT3(c->queue[q], y2);
                    }
                }
            }
        }
        /* cc = y1: y2 = 2 y1 or y1^2 */
        if (candbl && vhalf(c, &y2, &y1) && INQ(y1)) HIT3(y1, y2);
        if (cansq) {
            if (!y2.big) { if (visqrt128(&y2, &y1) && INQ(y1)) HIT3(y1, y2); }
            else {
                for (int q = 0; q < c->qlen; q++) if (c->hstate[hfind(c, &c->queue[q])] == ST_INQ && vbitlen(c, &c->queue[q]) * 2 >= vbitlen(c, &y2) - 1) { tmp = vmul(c, &c->queue[q], &c->queue[q]); if (veq(c, &tmp, &y2)) HIT3(c->queue[q], y2); }
            }
        }
    }
    return false;
}

/* per target: least M (capped at 2^25) with M^5 >= N, and whether N is a square or a cube */
static void fifth_root_threshold(target_t *t) {
    u128 N = ((u128)t->v.hi << 64) | t->v.lo;
    uint64_t lo = 1, hi = 1ull << 25;   /* (2^25)^5 = 2^125 fits in 128 bits */
    while (lo < hi) { uint64_t mid = lo + (hi - lo) / 2; u128 p = (u128)mid * mid; p = p * p * mid; if (p >= N) hi = mid; else lo = mid + 1; }
    t->m5 = lo;
    val_t r; t->is_power = visqrt128(&t->v, &r);
    if (!t->is_power) {   /* binary search for the cube root */
        uint64_t a = 1, b = 1ull << 42;
        while (a < b) { uint64_t mid = a + (b - a) / 2; u128 cube = (u128)mid * mid * mid; if (cube >= N) b = mid; else a = mid + 1; }
        if ((u128)a * a * a == N) t->is_power = true;
    }
}

static void run_endgames(ctx_t *c) {
    c->leaves++;
    leafinfo_t li;
    memset(li.remdone, 0, sizeof li.remdone);
    uint32_t mark0 = c->arena_top;
    int ns = c->nset;
    li.smax = c->set[0];
    for (int i = 1; i < ns; i++) if (vcmp(c, &c->set[i], &li.smax) > 0) li.smax = c->set[i];
    bool first = true; li.qcount = 0;
    for (int q = 0; q < c->qlen; q++) {
        if (c->hstate[hfind(c, &c->queue[q])] != ST_INQ) continue;
        li.qcount++;
        if (first) { li.qmin = li.qmax = c->queue[q]; first = false; continue; }
        if (vcmp(c, &c->queue[q], &li.qmin) < 0) li.qmin = c->queue[q];
        if (vcmp(c, &c->queue[q], &li.qmax) > 0) li.qmax = c->queue[q];
    }
    int smax_bits = vbitlen(c, &li.smax);
    uint32_t mark = c->arena_top;
    for (int t = 0; t < ntargets; t++) {
        if (targets[t].best <= g_depth) continue;
        /* size filter: for a non-square non-cube target, reachable in 3 steps needs smax^5 >= N */
        if (!targets[t].is_power && smax_bits < 27 && !li.smax.big && !li.smax.hi && li.smax.lo < targets[t].m5) { c->filtered++; continue; }
        endgame(c, t, &li);
        c->arena_top = mark;
    }
    c->arena_top = mark0;
}

/* ------------------------------------------------------------------ */
/* Count mode: exact reached set (all sizes)                            */
/* ------------------------------------------------------------------ */
static uint64_t *g_reach = NULL; static uint8_t *g_reach_depth = NULL; static uint64_t g_reach_cap = 0, g_reach_n = 0;
static uint64_t g_depth_new[MAXDEPTH + 2];
/* big values (>= 2^64): stored exactly in a growable arena with a hash index */
static uint64_t *g_big_arena = NULL; static uint64_t g_big_top = 1, g_big_cap = 0;
static uint64_t *g_big_idx = NULL; static uint8_t *g_big_depth = NULL; static uint64_t g_big_cap_idx = 0, g_big_n = 0;

static void reach_insert_small(uint64_t x, int depth) {
    uint64_t h = mix64(x) & (g_reach_cap - 1);
    while (g_reach[h] != 0) {
        if (g_reach[h] == x) { if (depth < g_reach_depth[h]) { g_depth_new[g_reach_depth[h]]--; g_reach_depth[h] = (uint8_t)depth; g_depth_new[depth]++; } return; }
        h = (h + 1) & (g_reach_cap - 1);
    }
    g_reach[h] = x; g_reach_depth[h] = (uint8_t)depth; g_reach_n++; g_depth_new[depth]++;
    if (g_reach_n * 2 > g_reach_cap) { fprintf(stderr, "FATAL reach table too full\n"); exit(2); }
}
static void reach_insert_big(uint64_t *L, int n, int depth) {
    uint64_t hv = 0x9876543210ULL + (uint64_t)n; for (int i = 0; i < n; i++) hv = mix64(hv ^ L[i]);
    uint64_t h = hv & (g_big_cap_idx - 1);
    while (g_big_idx[h] != 0) {
        uint64_t off = g_big_idx[h];
        if (g_big_arena[off] == (uint64_t)n && memcmp(&g_big_arena[off + 1], L, (size_t)n * 8) == 0) {
            if (depth < g_big_depth[h]) { g_depth_new[g_big_depth[h]]--; g_big_depth[h] = (uint8_t)depth; g_depth_new[depth]++; }
            return;
        }
        h = (h + 1) & (g_big_cap_idx - 1);
    }
    if (g_big_top + (uint64_t)n + 1 >= g_big_cap) { g_big_cap = g_big_cap ? g_big_cap * 2 : (1ull << 22); g_big_arena = realloc(g_big_arena, g_big_cap * 8); if (!g_big_arena) { fprintf(stderr, "FATAL realloc\n"); exit(2); } }
    g_big_arena[g_big_top] = (uint64_t)n; memcpy(&g_big_arena[g_big_top + 1], L, (size_t)n * 8);
    g_big_idx[h] = g_big_top; g_big_depth[h] = (uint8_t)depth; g_big_top += (uint64_t)n + 1; g_big_n++; g_depth_new[depth]++;
    if (g_big_n * 2 > g_big_cap_idx) { fprintf(stderr, "FATAL big index too full\n"); exit(2); }
}
static void count_record(ctx_t *c, int steps) {
    const val_t *v = &c->set[c->nset - 1];
    #pragma omp critical(reach)
    {
        if (!v->big && !v->hi) reach_insert_small(v->lo, steps);
        else { uint64_t L[MAXLIMBS]; int n; to_limbs(c, v, L, &n); reach_insert_big(L, n, steps); }
    }
}

/* ------------------------------------------------------------------ */
/* DFS                                                                  */
/* ------------------------------------------------------------------ */
static void dfs(ctx_t *c, int qstart);
static inline void visit(ctx_t *c, int pos) {
    val_t v = c->queue[pos];
    push_value(c, &v, pos);
    int steps = c->nset - 1;
    c->nodes[steps]++;
    if (g_countmode) count_record(c, steps);
    else for (int t = 0; t < ntargets; t++) if (veq(c, &v, &targets[t].v)) record_hit(c, t, steps, NULL, 0);
    if (steps < g_depth) {
        bool prune = false;
        if (!g_countmode) {
            /* Markstrom's bound: r steps can at most raise the maximum M to M^(2^r) */
            int r = g_steps - steps;
            int mb = 0; for (int i = 0; i < c->nset; i++) { int b = vbitlen(c, &c->set[i]); if (b > mb) mb = b; }
            if (mb < 2) mb = 2;
            if (((long)mb << r) <= (long)g_minbits - 1) prune = true;
        }
        if (prune) c->pruned++; else dfs(c, pos + 1);
    } else if (!g_countmode) run_endgames(c);
    pop_value(c);
}
static void dfs(ctx_t *c, int qstart) {
    int end = c->qlen;
    for (int pos = qstart; pos < end; pos++) visit(c, pos);
}

/* ---- parallel driver: prefixes to the split depth become tasks ---- */
typedef struct { int pos[MAXDEPTH + 2]; uint64_t h[MAXDEPTH + 2]; int n; } task_t;
static task_t *g_tasks = NULL; static int g_ntasks = 0, g_task_cap = 0;
static void collect(ctx_t *c, int qstart) {
    int steps = c->nset - 1;
    if (steps == g_split) {
        if (g_ntasks == g_task_cap) { g_task_cap = g_task_cap ? 2 * g_task_cap : 1024; g_tasks = realloc(g_tasks, sizeof(task_t) * (size_t)g_task_cap); if (!g_tasks) { fprintf(stderr, "FATAL realloc\n"); exit(2); } }
        task_t *t = &g_tasks[g_ntasks++];
        t->n = c->nset; for (int i = 0; i < c->nset; i++) { t->pos[i] = c->setpos[i]; t->h[i] = vhash(c, &c->set[i]); }
        return;
    }
    int end = c->qlen;
    for (int pos = qstart; pos < end; pos++) {
        val_t v = c->queue[pos];
        push_value(c, &v, pos);
        int s = c->nset - 1; c->nodes[s]++;
        if (g_countmode) count_record(c, s);
        else for (int t = 0; t < ntargets; t++) if (veq(c, &v, &targets[t].v)) record_hit(c, t, s, NULL, 0);
        collect(c, pos + 1);
        pop_value(c);
    }
}
static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec; }

static void load_targets(const char *tfile) {
    FILE *f = fopen(tfile, "r"); if (!f) { perror("targets"); exit(1); }
    char line[512];
    while (fgets(line, sizeof line, f)) {
        char *p = line; while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\n' || !*p) continue;
        char *nl = strchr(p, '\n'); if (nl) *nl = 0;
        target_t *t = &targets[ntargets];
        char *sp = strchr(p, ' ');
        if (sp) { *sp = 0; snprintf(t->name, sizeof t->name, "%s", p); p = sp + 1; while (*p == ' ') p++; }
        else t->name[0] = 0;
        snprintf(t->dec, sizeof t->dec, "%s", p);
        if (!parse_u128(p, &t->v)) { fprintf(stderr, "target not a positive integer below 2^128: %s\n", p); exit(1); }
        if (viszero(&t->v)) { fprintf(stderr, "target 0 not allowed\n"); exit(1); }
        t->bits = bitlen128(t->v.lo, t->v.hi);
        if (!t->name[0]) snprintf(t->name, sizeof t->name, "%s", t->dec);
        t->best = 1 << 30; t->witness[0] = 0;
        if (t->bits < g_minbits) g_minbits = t->bits;
        build_divisors(t); fifth_root_threshold(t);
        if (++ntargets >= MAXT) { fprintf(stderr, "too many targets\n"); exit(1); }
    }
    fclose(f);
    if (ntargets == 0) { fprintf(stderr, "no targets\n"); exit(1); }
}

int main(int argc, char **argv) {
    const char *tfile = NULL, *pfile = NULL; int nthreads = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--count") && i + 1 < argc) { g_countmode = true; g_depth = atoi(argv[++i]); g_steps = g_depth; }
        else if (!strcmp(argv[i], "--steps") && i + 1 < argc) g_steps = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--targets") && i + 1 < argc) tfile = argv[++i];
        else if (!strcmp(argv[i], "--threads") && i + 1 < argc) nthreads = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--split") && i + 1 < argc) g_split = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--table") && i + 1 < argc) g_table_bound = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--endgame-test") && i + 1 < argc) { g_endgame_test = true; pfile = argv[++i]; }
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 1; }
    }
    if (nthreads) omp_set_num_threads(nthreads);
    ctx_t *c0 = malloc(sizeof(ctx_t)); ctx_init(c0);

    if (g_endgame_test) {
        if (!tfile) { fprintf(stderr, "need --targets\n"); return 1; }
        load_targets(tfile);
        FILE *f = fopen(pfile, "r"); if (!f) { perror("prefix"); return 1; }
        char line[512];
        while (fgets(line, sizeof line, f)) {
            val_t v; if (!parse_u128(line, &v)) continue;
            int pos = -1; for (int q = 0; q < c0->qlen; q++) if (veq(c0, &c0->queue[q], &v) && c0->hstate[hfind(c0, &v)] == ST_INQ) { pos = q; break; }
            if (pos < 0) { fprintf(stderr, "prefix value %s is not derivable from the current set\n", line); return 1; }
            push_value(c0, &v, pos);
        }
        fclose(f);
        g_depth = c0->nset - 1; g_steps = g_depth + 3;
        for (int t = 0; t < ntargets; t++) { targets[t].best = 1 << 30; }
        run_endgames(c0);
        printf("{\"prefix_steps\": %d, \"results\": [", g_depth);
        for (int t = 0; t < ntargets; t++) printf("%s{\"value\": \"%s\", \"steps\": %d}", t ? "," : "", targets[t].dec, targets[t].best <= g_steps ? targets[t].best : -1);
        printf("]}\n");
        return 0;
    }
    if (!g_countmode) {
        if (!tfile || g_steps < 4 || g_steps > MAXDEPTH) { fprintf(stderr, "need --steps L (4..%d) --targets FILE\n", MAXDEPTH); return 1; }
        g_depth = g_steps - 3;
        load_targets(tfile);
    } else {
        if (g_depth < 1 || g_depth > 12) { fprintf(stderr, "--count D with 1 <= D <= 12\n"); return 1; }
        g_reach_cap = 1ull << (g_depth >= 11 ? 30 : (g_depth >= 10 ? 27 : 24));
        g_reach = calloc(g_reach_cap, sizeof(uint64_t)); g_reach_depth = calloc(g_reach_cap, 1);
        g_big_cap_idx = 1ull << 24; g_big_idx = calloc(g_big_cap_idx, sizeof(uint64_t)); g_big_depth = calloc(g_big_cap_idx, 1);
        if (!g_reach || !g_reach_depth || !g_big_idx || !g_big_depth) { fprintf(stderr, "FATAL calloc\n"); return 2; }
        reach_insert_small(1, 0);
    }
    double t0 = now();
    if (g_split > g_depth) g_split = g_depth;
    collect(c0, 0);
    fprintf(stderr, "split depth %d: %d tasks (%.1fs)\n", g_split, g_ntasks, now() - t0);
    uint64_t total_nodes[MAXDEPTH + 2]; uint64_t total_leaves = 0, total_pruned = 0, total_filtered = 0;
    for (int d = 0; d <= MAXDEPTH + 1; d++) total_nodes[d] = c0->nodes[d];
    int done = 0;
    #pragma omp parallel
    {
        ctx_t *c = malloc(sizeof(ctx_t)); ctx_init(c);
        #pragma omp for schedule(dynamic, 1)
        for (int k = 0; k < g_ntasks; k++) {
            task_t *tk = &g_tasks[k];
            for (int i = 1; i < tk->n; i++) {
                int pos = tk->pos[i];
                if (pos >= c->qlen || vhash(c, &c->queue[pos]) != tk->h[i]) { fprintf(stderr, "FATAL replay mismatch\n"); exit(3); }
                val_t v = c->queue[pos]; push_value(c, &v, pos);
            }
            if (g_split == g_depth) { if (!g_countmode) run_endgames(c); }
            else dfs(c, tk->pos[tk->n - 1] + 1);
            for (int i = 1; i < tk->n; i++) pop_value(c);
            int dn;
            #pragma omp atomic capture
            dn = ++done;
            if ((dn & 63) == 0) fprintf(stderr, "  %d/%d tasks, %.0fs\n", dn, g_ntasks, now() - t0);
        }
        #pragma omp critical(stats)
        { for (int d = 0; d <= MAXDEPTH + 1; d++) total_nodes[d] += c->nodes[d]; total_leaves += c->leaves; total_pruned += c->pruned; total_filtered += c->filtered; }
        free(c->arena); free(c);
    }
    double t1 = now();
    printf("{\n  \"mode\": \"%s\", \"steps\": %d, \"prefix_depth\": %d, \"threads\": %d, \"seconds\": %.1f,\n", g_countmode ? "count" : "decide", g_steps, g_depth, omp_get_max_threads(), t1 - t0);
    printf("  \"nodes_per_depth\": [");
    for (int d = 1; d <= g_depth; d++) printf("%s%llu", d > 1 ? "," : "", (unsigned long long)total_nodes[d]);
    printf("],\n  \"leaves\": %llu, \"pruned\": %llu, \"leaf_target_pairs_filtered_by_size\": %llu", (unsigned long long)total_leaves, (unsigned long long)total_pruned, (unsigned long long)total_filtered);
    if (g_countmode) {
        printf(",\n  \"reached_cumulative\": [");
        uint64_t cum = 0;
        for (int d = 0; d <= g_depth; d++) { cum += g_depth_new[d]; printf("%s%llu", d ? "," : "", (unsigned long long)cum); }
        printf("],\n  \"reached_below_2_64\": %llu, \"reached_at_least_2_64\": %llu", (unsigned long long)g_reach_n, (unsigned long long)g_big_n);
        if (g_table_bound) {
            printf(",\n  \"tau_table_bound\": %llu,\n  \"tau\": [", (unsigned long long)g_table_bound);
            for (uint64_t n = 1; n <= g_table_bound; n++) {
                uint64_t h = mix64(n) & (g_reach_cap - 1); int dep = -1;
                while (g_reach[h] != 0) { if (g_reach[h] == n) { dep = g_reach_depth[h]; break; } h = (h + 1) & (g_reach_cap - 1); }
                printf("%s%d", n > 1 ? "," : "", dep);
            }
            printf("]");
        }
    } else {
        printf(",\n  \"targets\": [\n");
        for (int t = 0; t < ntargets; t++) {
            printf("    {\"name\": \"%s\", \"value\": \"%s\", \"bits\": %d, ", targets[t].name, targets[t].dec, targets[t].bits);
            if (targets[t].best <= g_steps) printf("\"found_steps\": %d, \"program\": %s}", targets[t].best, targets[t].witness);
            else printf("\"found_steps\": null, \"not_reachable_within\": %d}", g_steps);
            printf("%s\n", t + 1 < ntargets ? "," : "");
        }
        printf("  ]");
    }
    printf("\n}\n");
    return 0;
}
