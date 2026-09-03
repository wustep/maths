/*
 * poly_search.c -- exhaustive search for integer polynomials with many
 * distinct integer roots and small straight-line cost (Smale 1998, Problem 4).
 *
 * Programs start from {1, x}; each step is +, -, or * of two earlier values.
 * The enumeration is the canonical pending-queue order (as in q1); every
 * distinct value sequence of a program with pairwise distinct values is
 * visited exactly once.  Dropping duplicate values never increases length,
 * so tau(f) is the least depth at which f appears.
 *
 * Coefficients are exact signed 128-bit integers.  Each polynomial carries
 * an upper bound b(f) on the sum of absolute coefficients (log2), with
 * b(f+g) <= b(f)+b(g), b(fg) <= b(f) b(g), so overflow is impossible while
 * b < 2^125.  A product with a larger bound is not formed: at the last
 * depth it is reported as a pair (f, g), since Z(fg) <= Z(f) + Z(g), and
 * at earlier depths the bound argument shows it cannot occur for D <= 7.
 *
 * Every node whose polynomial has degree >= need[depth] passes through
 * three rigorous filters (primitive part; number of roots modulo tiny primes
 * counted with multiplicity; Descartes' rule on f(x) and f(-x)) and, if it
 * survives, is written to stdout for exact root counting in Python.
 *
 * Build: gcc -O3 -march=native -fopenmp -o poly_search poly_search.c
 * Usage: ./poly_search D need0 need1 ... needD  > candidates.txt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <omp.h>

typedef __int128 i128;
#define MAXDEG 128
#define MAXD 8
typedef struct { int deg; double lb; i128 c[MAXDEG + 1]; } poly_t;   /* lb = log2 bound on sum |c_i|; deg = -1 for zero */

static uint64_t mix64(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
static uint64_t phash(const poly_t *p) { uint64_t h = 0x1234 + (uint64_t)(p->deg + 1); for (int i = 0; i <= p->deg; i++) { h = mix64(h ^ (uint64_t)p->c[i]); h = mix64(h ^ (uint64_t)((unsigned __int128)p->c[i] >> 64)); } return h; }
static bool peq(const poly_t *a, const poly_t *b) { if (a->deg != b->deg) return false; for (int i = 0; i <= a->deg; i++) if (a->c[i] != b->c[i]) return false; return true; }
static void pnorm(poly_t *p) { while (p->deg >= 0 && p->c[p->deg] == 0) p->deg--; }
static const double LB_LIMIT = 125.0;
static double lb_of(const poly_t *p) { /* exact log2 of sum |c_i|, rounded up */ long double s = 0; for (int i = 0; i <= p->deg; i++) { i128 v = p->c[i]; if (v < 0) v = -v; s += (long double)v; } return s <= 1 ? 0.0 : (double)log2l(s) + 1e-9; }
static bool padd(const poly_t *a, const poly_t *b, poly_t *r, int sign) {
    double lb = log2(exp2(a->lb) + exp2(b->lb)) + 1e-9;
    if (lb >= LB_LIMIT) return false;
    int d = a->deg > b->deg ? a->deg : b->deg; r->deg = d;
    for (int i = 0; i <= d; i++) { i128 x = i <= a->deg ? a->c[i] : 0, y = i <= b->deg ? b->c[i] : 0; r->c[i] = sign > 0 ? x + y : x - y; }
    pnorm(r); r->lb = lb_of(r); return true;
}
static bool pmul(const poly_t *a, const poly_t *b, poly_t *r) {
    if (a->deg < 0 || b->deg < 0) { r->deg = -1; r->lb = 0; return true; }
    double lb = a->lb + b->lb + 1e-9;
    if (lb >= LB_LIMIT) return false;
    int d = a->deg + b->deg; if (d > MAXDEG) { fprintf(stderr, "FATAL degree overflow\n"); exit(2); }
    r->deg = d; for (int i = 0; i <= d; i++) r->c[i] = 0;
    for (int i = 0; i <= a->deg; i++) if (a->c[i]) for (int j = 0; j <= b->deg; j++) r->c[i + j] += a->c[i] * b->c[j];
    pnorm(r); r->lb = lb_of(r); return true;
}
static void pprint(const poly_t *p, char *buf, size_t cap) {
    size_t pos = 0; pos += (size_t)snprintf(buf + pos, cap - pos, "[");
    for (int i = 0; i <= p->deg; i++) {
        i128 v = p->c[i]; bool neg = v < 0; unsigned __int128 u = neg ? (unsigned __int128)(-v) : (unsigned __int128)v;
        char tmp[64]; int k = 63; tmp[k] = 0; if (u == 0) tmp[--k] = '0'; while (u) { tmp[--k] = (char)('0' + (int)(u % 10)); u /= 10; }
        pos += (size_t)snprintf(buf + pos, cap - pos, "%s%s%s", i ? "," : "", neg ? "-" : "", tmp + k);
    }
    snprintf(buf + pos, cap - pos, "]");
}

/* ---- rigorous cheap upper bounds on the number of distinct integer roots ---- */
static i128 gcd128(i128 a, i128 b) { if (a < 0) a = -a; if (b < 0) b = -b; while (b) { i128 t = a % b; a = b; b = t; } return a; }
static int zbound(const poly_t *f0) {
    /* returns an upper bound on Z(f) (distinct integer roots); f0 nonzero */
    poly_t f = *f0;
    int m = 0; while (m <= f.deg && f.c[m] == 0) m++;   /* x^m divides f */
    int zero_root = m > 0 ? 1 : 0;
    if (m == f.deg) return zero_root;                   /* monomial */
    /* strip x^m and the content */
    int d = f.deg - m; i128 g = 0;
    for (int i = 0; i <= d; i++) { f.c[i] = f.c[i + m]; g = gcd128(g, f.c[i]); }
    f.deg = d; for (int i = 0; i <= d; i++) f.c[i] /= g;
    int best = d;
    /* Descartes: positive roots <= sign changes of f, negative roots <= sign changes of f(-x) */
    int vp = 0, vn = 0, last = 0, lastn = 0;
    for (int i = 0; i <= d; i++) {
        if (f.c[i] == 0) continue;
        int s = f.c[i] > 0 ? 1 : -1; if (last && s != last) vp++; last = s;
        int sn = (i & 1) ? -s : s; if (lastn && sn != lastn) vn++; lastn = sn;
    }
    if (vp + vn < best) best = vp + vn;
    /* Cauchy bound: every root r has |r| <= B = 1 + max|a_i| / |a_d| */
    i128 an = f.c[d]; if (an < 0) an = -an; i128 mx = 0;
    for (int i = 0; i < d; i++) { i128 v = f.c[i]; if (v < 0) v = -v; if (v > mx) mx = v; }
    i128 B = 1 + mx / an;
    /* roots modulo small primes q counted with multiplicity, each residue class
       capped by the number A = ceil((2B+1)/q) of integers in [-B, B] in that
       class: distinct integer roots give coprime linear factors whose product
       divides f over Z, hence modulo q. */
    static const int primes[] = { 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101 };
    for (int pi = 0; pi < 26 && best > 0; pi++) {
        int q = primes[pi]; int64_t r[MAXDEG + 1]; int dq = -1;
        for (int i = 0; i <= d; i++) { int64_t v = (int64_t)(f.c[i] % q); if (v < 0) v += q; r[i] = v; if (v) dq = i; }
        if (dq < 0) continue;   /* cannot happen for primitive f */
        i128 A128 = (2 * B + 1 + q - 1) / q; int A = A128 > 1000000 ? 1000000 : (int)A128;
        int count = 0;
        for (int s = 0; s < q; s++) {
            int mult = 0;
            for (;;) {
                int64_t val = 0; for (int i = dq; i >= 0; i--) val = (val * s + r[i]) % q;
                if (val != 0 || dq < 1) break;
                int64_t b = r[dq]; int64_t quo[MAXDEG + 1]; quo[dq - 1] = b;
                for (int i = dq - 1; i >= 1; i--) { b = (r[i] + b * s) % q; quo[i - 1] = b; }
                for (int i = 0; i < dq; i++) r[i] = quo[i];
                dq--; mult++;
            }
            count += mult < A ? mult : A;
            if (count >= best) break;
        }
        if (count < best) best = count;
    }
    /* distinct roots modulo a prime q > 2B: integer roots in [-B, B] map injectively
       to residues, so Z(f) - [0 is a root] <= deg gcd(f, x^q - x) mod q. */
    if (best > 0 && B < 20000000) {
        int64_t q = (int64_t)(2 * B + 2); if (q < 3) q = 3;
        for (;; q++) { bool pr = true; for (int64_t t = 2; t * t <= q; t++) if (q % t == 0) { pr = false; break; } if (pr) break; }
        int64_t fq[MAXDEG + 1]; int dq = -1;
        for (int i = 0; i <= d; i++) { int64_t v = (int64_t)(f.c[i] % q); if (v < 0) v += q; fq[i] = v; if (v) dq = i; }
        if (dq >= 1) {
            /* make monic */
            int64_t inv = 1, base = fq[dq] % q, e = q - 2; while (e) { if (e & 1) inv = inv * base % q; base = base * base % q; e >>= 1; }
            for (int i = 0; i <= dq; i++) fq[i] = fq[i] * inv % q;
            /* x^q mod fq by square-and-multiply */
            int64_t acc[MAXDEG + 1], xx[MAXDEG + 1], tmp[2 * MAXDEG + 1];
            memset(acc, 0, sizeof acc); acc[0] = 1; memset(xx, 0, sizeof xx); if (dq > 1) xx[1] = 1; else xx[0] = (q - fq[0]) % q;   /* x mod fq */
            int64_t ee = q;
            #define REDUCE() do { for (int i = 2 * dq - 2; i >= dq; i--) { int64_t cf = tmp[i] % q; if (!cf) continue; for (int j = 0; j <= dq; j++) tmp[i - dq + j] = (tmp[i - dq + j] - cf * fq[j]) % q; } } while (0)
            #define MULMOD(A, Bv) do { memset(tmp, 0, sizeof tmp); for (int i = 0; i < dq; i++) if (A[i]) for (int j = 0; j < dq; j++) tmp[i + j] = (tmp[i + j] + A[i] * Bv[j]) % q; REDUCE(); for (int i = 0; i < dq; i++) { int64_t v = tmp[i] % q; if (v < 0) v += q; A[i] = v; } } while (0)
            while (ee) { if (ee & 1) MULMOD(acc, xx); MULMOD(xx, xx); ee >>= 1; }
            /* h = acc - x; gcd(fq, h) degree = number of distinct roots mod q */
            int64_t h[MAXDEG + 1]; memcpy(h, acc, sizeof h); if (dq > 1) { h[1] = (h[1] - 1 + q) % q; } else { h[0] = (h[0] - (q - fq[0]) % q + q) % q; }
            int dh = dq - 1; while (dh >= 0 && h[dh] == 0) dh--;
            /* Euclid on (fq, h) */
            int64_t a[MAXDEG + 1], b[MAXDEG + 1]; int da = dq, db = dh; memcpy(a, fq, sizeof a); memcpy(b, h, sizeof b);
            while (db >= 0) {
                /* a = a mod b */
                int64_t invb = 1, bb = b[db] % q, e2 = q - 2; while (e2) { if (e2 & 1) invb = invb * bb % q; bb = bb * bb % q; e2 >>= 1; }
                for (int i = da; i >= db; i--) { int64_t cf = a[i] * invb % q; if (!cf) continue; for (int j = 0; j <= db; j++) a[i - db + j] = ((a[i - db + j] - cf * b[j]) % q + q) % q; }
                da = db - 1; while (da >= 0 && a[da] == 0) da--;
                /* swap */
                int64_t sw[MAXDEG + 1]; memcpy(sw, a, sizeof sw); memcpy(a, b, sizeof a); memcpy(b, sw, sizeof b); int ds = da; da = db; db = ds;
            }
            int distinct = da < 0 ? 0 : da;   /* gcd degree */
            if (distinct < best) best = distinct;
        } else if (dq == 0) best = 0;
    }
    return best + zero_root;
}

/* ---- search state (per thread) ---- */
#define HBITS 15
#define HSIZE (1u << HBITS)
#define MAXQ 12000
typedef struct {
    poly_t *queue; int qlen;
    poly_t set[MAXD + 3]; int nset; int setpos[MAXD + 3]; int setz[MAXD + 3];
    uint8_t hstate[HSIZE]; poly_t *hvals;
    uint32_t hslot_stack[MAXQ + 64]; int hslot_top;
    int qblock[MAXD + 3], hmark[MAXD + 3];
    uint64_t nodes[MAXD + 3], cand[MAXD + 3], wide[MAXD + 3];
} ctx_t;
static int g_depth; static int g_need[MAXD + 3];

static uint32_t hfind(ctx_t *c, const poly_t *p) { uint32_t s = (uint32_t)(phash(p) & (HSIZE - 1)); while (c->hstate[s]) { if (peq(&c->hvals[s], p)) return s; s = (s + 1) & (HSIZE - 1); } return s; }
static void enqueue(ctx_t *c, const poly_t *p) { uint32_t s = hfind(c, p); if (!c->hstate[s]) { if (c->qlen >= MAXQ) { fprintf(stderr, "FATAL queue overflow\n"); exit(2); } c->queue[c->qlen++] = *p; c->hvals[s] = *p; c->hstate[s] = 1; c->hslot_stack[c->hslot_top++] = s; } }
static void report(ctx_t *c, const poly_t *p, int steps, const char *tag) {
    char buf[8192]; pprint(p, buf, sizeof buf);
    char prog[16384]; size_t pos = 0;
    for (int i = 0; i < c->nset; i++) { char b2[8192]; pprint(&c->set[i], b2, sizeof b2); pos += (size_t)snprintf(prog + pos, sizeof prog - pos, "%s%s", i ? ";" : "", b2); }
    #pragma omp critical(out)
    { printf("%s %d %s %s\n", tag, steps, buf, prog); fflush(stdout); }
}
static void push(ctx_t *c, int pos) {
    int d = c->nset; c->qblock[d] = c->qlen; c->hmark[d] = c->hslot_top;
    c->set[d] = c->queue[pos]; c->setpos[d] = pos; c->nset = d + 1;
    c->hstate[hfind(c, &c->set[d])] = 2;
    int steps = d - 1;
    poly_t r;
    for (int i = 0; i <= d; i++) {
        if (padd(&c->set[d], &c->set[i], &r, +1)) enqueue(c, &r);
        if (pmul(&c->set[d], &c->set[i], &r)) enqueue(c, &r);
        else { c->wide[steps + 1]++; if (steps + 1 <= g_depth) { char b1[8192], b2[8192]; pprint(&c->set[d], b1, sizeof b1); pprint(&c->set[i], b2, sizeof b2);
            #pragma omp critical(out)
            { printf("WIDE %d %s %s\n", steps + 1, b1, b2); fflush(stdout); } } }
        if (i != d) { if (padd(&c->set[d], &c->set[i], &r, -1)) enqueue(c, &r); if (padd(&c->set[i], &c->set[d], &r, -1)) enqueue(c, &r); }
        else { r.deg = -1; r.lb = 0; enqueue(c, &r); }
    }
}
static void pop(ctx_t *c) {
    int d = c->nset - 1;
    while (c->hslot_top > c->hmark[d]) { uint32_t s = c->hslot_stack[--c->hslot_top]; c->hstate[s] = 0; }
    c->qlen = c->qblock[d];
    c->hstate[hfind(c, &c->set[d])] = 1;
    c->nset = d;
}
static void examine(ctx_t *c, int steps) {
    const poly_t *p = &c->set[c->nset - 1];
    if (p->deg < g_need[steps]) return;
    int zb = zbound(p);
    if (zb >= g_need[steps]) { c->cand[steps]++; report(c, p, steps, "CAND"); }
}
static void dfs(ctx_t *c, int qstart) {
    int end = c->qlen;
    for (int pos = qstart; pos < end; pos++) {
        push(c, pos);
        int steps = c->nset - 2;
        c->nodes[steps]++;
        examine(c, steps);
        if (steps < g_depth) dfs(c, pos + 1);
        pop(c);
    }
}
static void ctx_init(ctx_t *c) {
    memset(c, 0, sizeof *c);
    c->queue = malloc(sizeof(poly_t) * MAXQ); c->hvals = malloc(sizeof(poly_t) * HSIZE);
    if (!c->queue || !c->hvals) { fprintf(stderr, "FATAL malloc\n"); exit(2); }
    c->set[0].deg = 0; c->set[0].c[0] = 1; c->set[0].lb = 0; c->set[1].deg = 1; c->set[1].c[0] = 0; c->set[1].c[1] = 1; c->set[1].lb = 0; c->nset = 2;
    for (int i = 0; i < 2; i++) { uint32_t s = hfind(c, &c->set[i]); c->hvals[s] = c->set[i]; c->hstate[s] = 2; }
    poly_t r;
    for (int i = 0; i < 2; i++) for (int j = i; j < 2; j++) {
        padd(&c->set[i], &c->set[j], &r, +1); enqueue(c, &r);
        pmul(&c->set[i], &c->set[j], &r); enqueue(c, &r);
        if (i != j) { padd(&c->set[i], &c->set[j], &r, -1); enqueue(c, &r); padd(&c->set[j], &c->set[i], &r, -1); enqueue(c, &r); }
        else { r.deg = -1; r.lb = 0; enqueue(c, &r); }
    }
}
/* tasks: prefixes at split depth, replayed by queue position */
typedef struct { int pos[MAXD + 3]; int n; } task_t;
static task_t *tasks; static int ntasks, taskcap; static int g_split = 3;
static void collect(ctx_t *c, int qstart) {
    int steps = c->nset - 2;
    if (steps == g_split) { if (ntasks == taskcap) { taskcap = taskcap ? 2 * taskcap : 1024; tasks = realloc(tasks, sizeof(task_t) * (size_t)taskcap); } task_t *t = &tasks[ntasks++]; t->n = c->nset; for (int i = 0; i < c->nset; i++) t->pos[i] = c->setpos[i]; return; }
    int end = c->qlen;
    for (int pos = qstart; pos < end; pos++) { push(c, pos); int s = c->nset - 2; c->nodes[s]++; examine(c, s); collect(c, pos + 1); pop(c); }
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: poly_search D need1 ... needD [--split S] [--threads T]\n"); return 1; }
    g_depth = atoi(argv[1]);
    if (g_depth > MAXD - 1) { fprintf(stderr, "D too large\n"); return 1; }
    for (int d = 1; d <= g_depth; d++) g_need[d] = atoi(argv[1 + d]);
    int nthreads = 0;
    for (int i = 2 + g_depth; i + 1 < argc; i += 2) { if (!strcmp(argv[i], "--split")) g_split = atoi(argv[i + 1]); else if (!strcmp(argv[i], "--threads")) nthreads = atoi(argv[i + 1]); }
    if (nthreads) omp_set_num_threads(nthreads);
    if (g_split > g_depth) g_split = g_depth;
    ctx_t *c0 = malloc(sizeof(ctx_t)); ctx_init(c0);
    collect(c0, 0);
    fprintf(stderr, "split %d: %d tasks\n", g_split, ntasks);
    uint64_t nodes[MAXD + 3], cand[MAXD + 3], wide[MAXD + 3]; memcpy(nodes, c0->nodes, sizeof nodes); memcpy(cand, c0->cand, sizeof cand); memcpy(wide, c0->wide, sizeof wide);
    #pragma omp parallel
    {
        ctx_t *c = malloc(sizeof(ctx_t)); ctx_init(c);
        #pragma omp for schedule(dynamic, 1)
        for (int k = 0; k < ntasks; k++) {
            task_t *t = &tasks[k];
            for (int i = 2; i < t->n; i++) push(c, t->pos[i]);
            if (g_split < g_depth) dfs(c, t->pos[t->n - 1] + 1);
            for (int i = 2; i < t->n; i++) pop(c);
        }
        #pragma omp critical(stats)
        { for (int d = 0; d <= MAXD + 2; d++) { nodes[d] += c->nodes[d]; cand[d] += c->cand[d]; wide[d] += c->wide[d]; } }
    }
    fprintf(stderr, "nodes:");
    for (int d = 1; d <= g_depth; d++) fprintf(stderr, " %llu", (unsigned long long)nodes[d]);
    fprintf(stderr, "\ncandidates:");
    for (int d = 1; d <= g_depth; d++) fprintf(stderr, " %llu", (unsigned long long)cand[d]);
    fprintf(stderr, "\nwide products skipped:");
    for (int d = 1; d <= g_depth; d++) fprintf(stderr, " %llu", (unsigned long long)wide[d]);
    fprintf(stderr, "\n");
    printf("STATS nodes");
    for (int d = 1; d <= g_depth; d++) printf(" %llu", (unsigned long long)nodes[d]);
    printf("\n");
    return 0;
}
