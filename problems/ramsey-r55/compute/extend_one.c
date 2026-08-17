/* One-vertex extension of a (5,5,n)-graph given as bitsets on stdin.

   Input format (text): first line n, then n lines of neighbourhood
   bitmasks as decimal uint64 (vertex 0..n-1, n<=62).

   gcc -O3 -std=c11 -o extend_one extend_one.c
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 62
#define MAXK 20000

static int N;
static int DEG_LO, DEG_HI;
static uint64_t adj[MAXN];
static uint64_t k4[MAXK], i4[MAXK];
static int nk4, ni4;
static int assign[MAXN];
static int sat_found;
static unsigned long long nodes, conflicts, decisions;
static uint64_t models[256];
static int nmodels;

static void list_k4(uint64_t *g, uint64_t *out, int *nout) {
    int a, b, c, d;
    *nout = 0;
    for (a = 0; a < N; a++) {
        for (b = a + 1; b < N; b++) {
            if (!((g[a] >> b) & 1ULL)) continue;
            uint64_t cab = g[a] & g[b];
            for (c = b + 1; c < N; c++) {
                if (!((cab >> c) & 1ULL)) continue;
                uint64_t cabc = cab & g[c];
                for (d = c + 1; d < N; d++) {
                    if ((cabc >> d) & 1ULL) {
                        if (*nout >= MAXK) {
                            fprintf(stderr, "MAXK\n");
                            exit(2);
                        }
                        out[(*nout)++] =
                            (1ULL << a) | (1ULL << b) | (1ULL << c) | (1ULL << d);
                    }
                }
            }
        }
    }
}

static int propagate(void) {
    int changed = 1;
    while (changed) {
        changed = 0;
        int ones = 0, zeros = 0;
        for (int i = 0; i < N; i++) {
            if (assign[i] == 1) ones++;
            else if (assign[i] == 0) zeros++;
        }
        if (ones > DEG_HI) return 0;
        if (zeros > N - DEG_LO) return 0;
        if (ones == DEG_HI) {
            for (int i = 0; i < N; i++)
                if (assign[i] == -1) {
                    assign[i] = 0;
                    changed = 1;
                }
            if (changed) continue;
        }
        if (zeros == N - DEG_LO) {
            for (int i = 0; i < N; i++)
                if (assign[i] == -1) {
                    assign[i] = 1;
                    changed = 1;
                }
            if (changed) continue;
        }
        for (int t = 0; t < nk4; t++) {
            uint64_t m = k4[t];
            int in_s = 0, nundef = 0, last = -1;
            while (m) {
                uint64_t b = m & -m;
                int v = __builtin_ctzll(b);
                if (assign[v] == 1) in_s++;
                else if (assign[v] == -1) {
                    nundef++;
                    last = v;
                }
                m ^= b;
            }
            if (in_s == 4) return 0;
            if (in_s == 3 && nundef == 1 && assign[last] != 0) {
                if (assign[last] == 1) return 0;
                assign[last] = 0;
                changed = 1;
            }
        }
        for (int t = 0; t < ni4; t++) {
            uint64_t m = i4[t];
            int out_s = 0, nundef = 0, last = -1;
            while (m) {
                uint64_t b = m & -m;
                int v = __builtin_ctzll(b);
                if (assign[v] == 0) out_s++;
                else if (assign[v] == -1) {
                    nundef++;
                    last = v;
                }
                m ^= b;
            }
            if (out_s == 4) return 0;
            if (out_s == 3 && nundef == 1 && assign[last] != 1) {
                if (assign[last] == 0) return 0;
                assign[last] = 1;
                changed = 1;
            }
        }
    }
    return 1;
}

static int rec(void) {
    nodes++;
    int snap[MAXN];
    memcpy(snap, assign, N * sizeof(int));
    if (!propagate()) {
        conflicts++;
        memcpy(assign, snap, N * sizeof(int));
        return 0;
    }
    int best = -1, bests = -1;
    for (int i = 0; i < N; i++) {
        if (assign[i] != -1) continue;
        uint64_t bit = 1ULL << i;
        int sc = 0;
        for (int t = 0; t < nk4; t++)
            if (k4[t] & bit) sc++;
        for (int t = 0; t < ni4; t++)
            if (i4[t] & bit) sc++;
        if (sc > bests) {
            bests = sc;
            best = i;
        }
    }
    if (best < 0) {
        int ones = 0;
        uint64_t mask = 0;
        for (int i = 0; i < N; i++)
            if (assign[i] == 1) {
                ones++;
                mask |= 1ULL << i;
            }
        if (ones >= DEG_LO && ones <= DEG_HI) {
            sat_found = 1;
            if (nmodels < 256) models[nmodels++] = mask;
            /* collect all */
            memcpy(assign, snap, N * sizeof(int));
            return 0; /* continue search */
        }
        conflicts++;
        memcpy(assign, snap, N * sizeof(int));
        return 0;
    }
    int after[MAXN];
    memcpy(after, assign, N * sizeof(int));
    for (int val = 1; val >= 0; val--) {
        memcpy(assign, after, N * sizeof(int));
        decisions++;
        assign[best] = val;
        rec();
    }
    memcpy(assign, snap, N * sizeof(int));
    return 0;
}

int main(void) {
    if (scanf("%d", &N) != 1 || N < 1 || N > MAXN) {
        fprintf(stderr, "bad n\n");
        return 2;
    }
    DEG_LO = (N + 1) - 25;
    if (DEG_LO < 0) DEG_LO = 0;
    DEG_HI = 24;
    if (DEG_HI > N) DEG_HI = N;
    uint64_t full = (N == 64) ? ~0ULL : ((1ULL << N) - 1ULL);
    for (int i = 0; i < N; i++) {
        unsigned long long x;
        if (scanf("%llu", &x) != 1) {
            fprintf(stderr, "bad adj\n");
            return 2;
        }
        adj[i] = (uint64_t)x;
    }
    uint64_t cadj[MAXN];
    for (int i = 0; i < N; i++) cadj[i] = (full ^ (1ULL << i)) ^ adj[i];
    list_k4(adj, k4, &nk4);
    list_k4(cadj, i4, &ni4);
    for (int i = 0; i < N; i++) assign[i] = -1;
    rec();
    printf("n=%d k4=%d i4=%d extensions=%d decisions=%llu conflicts=%llu "
           "nodes=%llu deg=[%d,%d]\n",
           N, nk4, ni4, nmodels, decisions, conflicts, nodes, DEG_LO, DEG_HI);
    for (int i = 0; i < nmodels; i++) {
        printf("EXT %d 0x%llx pop=%d\n", i, (unsigned long long)models[i],
               __builtin_popcountll(models[i]));
    }
    return nmodels ? 1 : 0;
}
