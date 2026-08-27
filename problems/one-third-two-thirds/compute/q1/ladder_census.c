/* Exhaustive non-sum broken-rung ladder minima.
 *
 * Same definition as ladders.py: rails i < i+2, rungs i < i+3 except
 * the broken set, then transitive closure. gcc -O3.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 24

static int N;
static uint32_t succ[MAXN], downv[MAXN];

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

static int n_summands(void) {
    uint32_t full = (1u << N) - 1;
    uint32_t unseen = full;
    int count = 0;
    while (unseen) {
        uint32_t bit = unseen & -unseen;
        int root = lsb_i(bit);
        uint32_t frontier = bit;
        unseen ^= bit;
        while (frontier) {
            int x = lsb_i(frontier);
            frontier ^= frontier & -frontier;
            uint32_t inc = full ^ downv[x] ^ succ[x] ^ (1u << x);
            uint32_t add = inc & unseen;
            unseen ^= add;
            frontier |= add;
            (void)root;
        }
        count++;
    }
    return count;
}

static void build(uint32_t broken_mask) {
    memset(succ, 0, sizeof succ);
    for (int i = 0; i < N - 2; i++) succ[i] |= 1u << (i + 2);
    for (int i = 0; i < N - 3; i++)
        if (((broken_mask >> i) & 1u) == 0) succ[i] |= 1u << (i + 3);
    for (int k = 0; k < N; k++)
        for (int i = 0; i < N; i++)
            if ((succ[i] >> k) & 1u) succ[i] |= succ[k];
    memset(downv, 0, sizeof downv);
    for (int i = 0; i < N; i++) {
        uint32_t s = succ[i];
        while (s) {
            uint32_t b = s & -s;
            downv[lsb_i(b)] |= 1u << i;
            s ^= b;
        }
    }
}

static uint64_t Fbuf[1 << MAXN];
static uint64_t Bbuf[1 << MAXN];
static uint32_t ideals[1 << MAXN];
static uint32_t sorted[1 << MAXN];
static unsigned char seen[1 << MAXN];

static void evaluate(uint64_t *best_n, uint64_t *best_d, uint64_t *best_e,
                     uint32_t *best_mask, uint32_t mask) {
    uint32_t full = (1u << N) - 1;
    /* ideals via BFS */
    memset(seen, 0, 1u << N);
    int ni = 0;
    ideals[ni++] = 0;
    seen[0] = 1;
    for (int qi = 0; qi < ni; qi++) {
        uint32_t I = ideals[qi];
        uint32_t mins = minima_of(full ^ I);
        uint32_t m = mins;
        while (m) {
            uint32_t b = m & -m;
            uint32_t nxt = I | b;
            if (!seen[nxt]) {
                seen[nxt] = 1;
                ideals[ni++] = nxt;
            }
            m ^= b;
        }
    }
    memset(Fbuf, 0, sizeof(uint64_t) << N);
    Fbuf[0] = 1;
    /* process by popcount */
    int start[MAXN + 2] = {0}, cntp[MAXN + 1] = {0};
    for (int i = 0; i < ni; i++) cntp[popcnt(ideals[i])]++;
    for (int p = 0; p <= N; p++) start[p + 1] = start[p] + cntp[p];
    int cur[MAXN + 1];
    memcpy(cur, start, sizeof cur);
    for (int i = 0; i < ni; i++) {
        int p = popcnt(ideals[i]);
        sorted[cur[p]++] = ideals[i];
    }
    for (int i = 0; i < ni; i++) {
        uint32_t S = sorted[i];
        if (!S) continue;
        uint64_t tot = 0;
        uint32_t mx = maxima_of(S), m = mx;
        while (m) {
            uint32_t b = m & -m;
            tot += Fbuf[S ^ b];
            m ^= b;
        }
        Fbuf[S] = tot;
    }
    uint64_t e = Fbuf[full];
    memset(Bbuf, 0, sizeof(uint64_t) << N);
    Bbuf[full] = 1;
    for (int i = ni - 1; i >= 0; i--) {
        uint32_t S = sorted[i];
        if (S == full) continue;
        uint32_t mins = minima_of(full ^ S), m = mins;
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
    uint32_t incomp[MAXN];
    for (int i = 0; i < N; i++)
        incomp[i] = full ^ downv[i] ^ succ[i] ^ (1u << i);
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
    for (int x = 0; x < N; x++) {
        uint32_t ys = incomp[x];
        while (ys) {
            uint32_t b = ys & -ys;
            int y = lsb_i(b);
            if (x < y) {
                uint64_t a = C[x][y], c = C[y][x];
                uint64_t mn = a < c ? a : c;
                if (mn * bd > bn * e) {
                    bn = mn;
                    bd = e;
                }
            }
            ys ^= b;
        }
    }
    if (bn * (*best_d) < (*best_n) * bd) {
        *best_n = bn;
        *best_d = bd;
        *best_e = e;
        *best_mask = mask;
    }
}

int main(int argc, char **argv) {
    int n0 = argc > 1 ? atoi(argv[1]) : 15;
    int n1 = argc > 2 ? atoi(argv[2]) : 18;
    if (n0 < 3 || n1 > MAXN || n0 > n1) {
        fprintf(stderr, "usage: ladder_census n0 n1  (3..%d)\n", MAXN);
        return 1;
    }
    printf("n\tmin\tbroken\te\n");
    for (N = n0; N <= n1; N++) {
        int nr = N - 3;
        if (nr < 0) nr = 0;
        uint64_t lim = 1ull << nr;
        uint64_t best_n = 1, best_d = 2, best_e = 0;
        uint32_t best_mask = 0;
        for (uint64_t mask = 0; mask < lim; mask++) {
            build((uint32_t)mask);
            if (n_summands() != 1) continue;
            evaluate(&best_n, &best_d, &best_e, &best_mask, (uint32_t)mask);
        }
        printf("%d\t%llu/%llu\t", N,
               (unsigned long long)best_n, (unsigned long long)best_d);
        int first = 1;
        for (int i = 0; i < nr; i++)
            if ((best_mask >> i) & 1u) {
                if (!first) putchar(',');
                printf("%d", i);
                first = 0;
            }
        if (first) printf("-");
        printf("\t%llu\n", (unsigned long long)best_e);
        fflush(stdout);
    }
    return 0;
}
