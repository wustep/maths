/* Shared exact δ engine for q2 enumerators.
 *
 * Generation-stamp ideals, no 2^N memset per poset. That is what made
 * the q1 ladder enumerator stall at n=22: each subset zeroed 2^n words.
 *
 * succ[] / downv[] are the caller's relation; evaluate() fills F, B, C
 * on the ideal lattice and returns the reduced (num, den, e) of δ.
 */
#ifndef DELTA_CORE_H
#define DELTA_CORE_H

#include <stdint.h>
#include <string.h>

#ifndef MAXN
#define MAXN 22
#endif

static int N;
static uint32_t succ[MAXN], downv[MAXN], incomp[MAXN], compv[MAXN];

static uint32_t ideals[1 << MAXN];
static uint32_t sorted[1 << MAXN];
static uint64_t Fbuf[1 << MAXN];
static uint64_t Bbuf[1 << MAXN];
static uint32_t seen_stamp[1 << MAXN];
static uint32_t STAMP;

static int popcnt(uint32_t x) { return __builtin_popcount(x); }
static int lsb_i(uint32_t x) { return __builtin_ctz(x); }

static uint32_t minima_of(uint32_t mask) {
    uint32_t out = 0, m = mask;
    while (m) {
        uint32_t b = m & -m;
        int i = lsb_i(b);
        if ((downv[i] & mask) == 0) out |= b;
        m ^= b;
    }
    return out;
}

static uint32_t maxima_of(uint32_t mask) {
    uint32_t out = 0, m = mask;
    while (m) {
        uint32_t b = m & -m;
        int i = lsb_i(b);
        if ((succ[i] & mask) == 0) out |= b;
        m ^= b;
    }
    return out;
}

static void close_and_down(void) {
    for (int k = 0; k < N; k++)
        for (int i = 0; i < N; i++)
            if ((succ[i] >> k) & 1u) succ[i] |= succ[k];
    memset(downv, 0, sizeof(uint32_t) * (size_t)N);
    for (int i = 0; i < N; i++) {
        uint32_t s = succ[i];
        while (s) {
            uint32_t b = s & -s;
            downv[lsb_i(b)] |= 1u << i;
            s ^= b;
        }
    }
    uint32_t full = (N == 32) ? 0xffffffffu : ((1u << N) - 1);
    for (int i = 0; i < N; i++) {
        compv[i] = downv[i] | succ[i];
        incomp[i] = full ^ compv[i] ^ (1u << i);
    }
}

static int n_summands(void) {
    uint32_t full = (1u << N) - 1;
    uint32_t unseen = full;
    int count = 0;
    while (unseen) {
        uint32_t bit = unseen & -unseen;
        uint32_t frontier = bit;
        unseen ^= bit;
        while (frontier) {
            int x = lsb_i(frontier);
            frontier ^= frontier & -frontier;
            uint32_t inc = full ^ downv[x] ^ succ[x] ^ (1u << x);
            uint32_t add = inc & unseen;
            unseen ^= add;
            frontier |= add;
        }
        count++;
    }
    return count;
}

static uint64_t ugcd(uint64_t a, uint64_t b) {
    while (b) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a ? a : 1;
}

typedef struct {
    uint64_t num, den, e;
    int x, y;
    int n_ideals;
} Delta;

/* Forward–backward pair counts on the ideal lattice. */
static Delta evaluate(void) {
    uint32_t full = (1u << N) - 1;
    STAMP++;
    if (STAMP == 0) {
        memset(seen_stamp, 0, sizeof seen_stamp);
        STAMP = 1;
    }
    int ni = 0;
    ideals[ni++] = 0;
    seen_stamp[0] = STAMP;
    for (int qi = 0; qi < ni; qi++) {
        uint32_t I = ideals[qi];
        uint32_t m = minima_of(full ^ I);
        while (m) {
            uint32_t b = m & -m;
            uint32_t nxt = I | b;
            if (seen_stamp[nxt] != STAMP) {
                seen_stamp[nxt] = STAMP;
                ideals[ni++] = nxt;
            }
            m ^= b;
        }
    }
    int start[MAXN + 2] = {0}, cntp[MAXN + 1] = {0};
    for (int i = 0; i < ni; i++) cntp[popcnt(ideals[i])]++;
    for (int p = 0; p <= N; p++) start[p + 1] = start[p] + cntp[p];
    int cur[MAXN + 1];
    memcpy(cur, start, sizeof cur);
    for (int i = 0; i < ni; i++) {
        int p = popcnt(ideals[i]);
        sorted[cur[p]++] = ideals[i];
    }
    Fbuf[0] = 1;
    for (int i = 1; i < ni; i++) {
        uint32_t S = sorted[i];
        uint64_t tot = 0;
        uint32_t m = maxima_of(S);
        while (m) {
            uint32_t b = m & -m;
            tot += Fbuf[S ^ b];
            m ^= b;
        }
        Fbuf[S] = tot;
    }
    uint64_t e = Fbuf[full];
    Bbuf[full] = 1;
    for (int i = ni - 2; i >= 0; i--) {
        uint32_t S = sorted[i];
        uint32_t m = minima_of(full ^ S);
        uint64_t tot = 0;
        while (m) {
            uint32_t b = m & -m;
            tot += Bbuf[S | b];
            m ^= b;
        }
        Bbuf[S] = tot;
    }
    uint64_t C[MAXN][MAXN];
    memset(C, 0, sizeof C);
    for (int ii = 0; ii < ni; ii++) {
        uint32_t I = ideals[ii];
        uint64_t fI = Fbuf[I];
        if (!fI && I) continue;
        for (int x = 0; x < N; x++) {
            if (((I >> x) & 1) == 0) continue;
            uint32_t ys = incomp[x] & ~I;
            while (ys) {
                uint32_t b = ys & -ys;
                int y = lsb_i(b);
                if ((downv[y] & ~I) == 0) C[x][y] += fI * Bbuf[I | b];
                ys ^= b;
            }
        }
    }
    uint64_t bn = 0, bd = 1;
    int bx = -1, by = -1;
    int n_inc = 0;
    for (int x = 0; x < N; x++) {
        uint32_t ys = incomp[x];
        while (ys) {
            uint32_t b = ys & -ys;
            int y = lsb_i(b);
            if (x < y) {
                n_inc++;
                uint64_t a = C[x][y], c = C[y][x];
                uint64_t mn = a < c ? a : c;
                if (mn * bd > bn * e) {
                    bn = mn;
                    bd = e;
                    bx = x;
                    by = y;
                }
            }
            ys ^= b;
        }
    }
    Delta d;
    if (n_inc == 0) {
        d.num = 1;
        d.den = 1;
        d.e = e;
        d.x = d.y = -1;
        d.n_ideals = ni;
        return d;
    }
    uint64_t g = ugcd(bn, bd);
    d.num = bn / g;
    d.den = bd / g;
    d.e = e;
    d.x = bx;
    d.y = by;
    d.n_ideals = ni;
    return d;
}

static int contains_3plus1(void) {
    uint32_t full = (1u << N) - 1;
    for (int a = 0; a < N; a++) {
        uint32_t m = succ[a];
        while (m) {
            int b = lsb_i(m);
            uint32_t t = succ[b];
            while (t) {
                int c = lsb_i(t);
                uint32_t blocked = (1u << a) | (1u << b) | (1u << c) |
                                   compv[a] | compv[b] | compv[c];
                if (full & ~blocked) return 1;
                t ^= t & -t;
            }
            m ^= m & -m;
        }
    }
    return 0;
}

#endif
