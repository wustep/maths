/* Pack cosets of a good 2-dimensional F7-subspace (shape 4).

   V ≤ F7^5, dim 2, V ∩ {-1,0,1}^5 = {0}. The quotient F7^5 / V has 343
   points. An independent set of 8 quotient points is 392 vertices.

   gcc -O3 -o q1/search_cosets q1/search_cosets.c
   ./q1/search_cosets
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define N 7
#define DIM 5
#define NV 16807
#define QN 343

static int SMALL[243][DIM];
static int nsmall;

static int rank2_ok(const int a[DIM], const int b[DIM]) {
    /* not scalar multiples */
    int seen = 0, ratio = -1;
    for (int i = 0; i < DIM; i++) {
        if (a[i] == 0 && b[i] == 0) continue;
        if (a[i] == 0 || b[i] == 0) return 1;
        int r = 0;
        /* b[i] = r * a[i] */
        for (int t = 0; t < 7; t++)
            if ((t * a[i]) % 7 == b[i]) {
                r = t;
                break;
            }
        if (!seen) {
            ratio = r;
            seen = 1;
        } else if (r != ratio)
            return 1;
    }
    return 0;
}

static int is_good(const int a[DIM], const int b[DIM]) {
    for (int s = 0; s < 7; s++)
        for (int t = 0; t < 7; t++) {
            if (s == 0 && t == 0) continue;
            int ok_small = 1;
            for (int i = 0; i < DIM; i++) {
                int x = (s * a[i] + t * b[i]) % 7;
                if (x > 1 && x < 6) {
                    ok_small = 0;
                    break;
                }
            }
            if (ok_small) return 0;
        }
    return 1;
}

static int invert5(int M[5][5], int Inv[5][5]) {
    int a[5][10];
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) a[i][j] = M[i][j];
        for (int j = 0; j < 5; j++) a[i][5 + j] = (i == j);
    }
    for (int col = 0; col < 5; col++) {
        int piv = -1;
        for (int i = col; i < 5; i++)
            if (a[i][col] % 7) {
                piv = i;
                break;
            }
        if (piv < 0) return 0;
        if (piv != col) {
            for (int j = 0; j < 10; j++) {
                int tmp = a[col][j];
                a[col][j] = a[piv][j];
                a[piv][j] = tmp;
            }
        }
        int inv = 0;
        for (int t = 1; t < 7; t++)
            if ((t * a[col][col]) % 7 == 1) {
                inv = t;
                break;
            }
        for (int j = 0; j < 10; j++) a[col][j] = (a[col][j] * inv) % 7;
        for (int i = 0; i < 5; i++) {
            if (i == col) continue;
            int f = a[i][col];
            if (!f) continue;
            for (int j = 0; j < 10; j++)
                a[i][j] = (a[i][j] - f * a[col][j] % 7 + 14) % 7;
        }
    }
    for (int i = 0; i < 5; i++)
        for (int j = 0; j < 5; j++) Inv[i][j] = a[i][5 + j];
    return 1;
}

static int qcoord(const int Inv[5][5], const int x[DIM]) {
    int y[5] = {0};
    for (int i = 0; i < 5; i++)
        for (int j = 0; j < 5; j++) y[i] = (y[i] + Inv[i][j] * x[j]) % 7;
    return y[2] * 49 + y[3] * 7 + y[4];
}

static int greedy_mis(int n, const uint64_t *adj, unsigned seed) {
    /* n=343, adj[i] is not a bitset of 343; use uint64_t adj[(n*n+63)/64] */
    int order[QN];
    for (int i = 0; i < n; i++) order[i] = i;
    unsigned rng = seed;
    for (int i = n - 1; i > 0; i--) {
        rng = rng * 1664525u + 1013904223u;
        int j = rng % (unsigned)(i + 1);
        int tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }
    uint8_t banned[QN];
    memset(banned, 0, n);
    int nt = 0;
    for (int t = 0; t < n; t++) {
        int v = order[t];
        if (banned[v]) continue;
        nt++;
        for (int u = 0; u < n; u++) {
            int bit = v * n + u;
            if (adj[bit / 64] & (1ull << (bit % 64))) banned[u] = 1;
        }
        banned[v] = 1;
    }
    return nt;
}

int main(void) {
    nsmall = 0;
    int o[5];
    for (o[0] = -1; o[0] <= 1; o[0]++)
    for (o[1] = -1; o[1] <= 1; o[1]++)
    for (o[2] = -1; o[2] <= 1; o[2]++)
    for (o[3] = -1; o[3] <= 1; o[3]++)
    for (o[4] = -1; o[4] <= 1; o[4]++) {
        for (int i = 0; i < 5; i++) SMALL[nsmall][i] = (o[i] + 7) % 7;
        nsmall++;
    }

    int best = 0, n_good = 0, checked = 0;
    uint64_t adj[(QN * QN + 63) / 64];

    for (int p0 = 0; p0 < 5; p0++)
    for (int p1 = p0 + 1; p1 < 5; p1++) {
        int free_idx[3], nf = 0;
        for (int j = 0; j < 5; j++)
            if (j != p0 && j != p1) free_idx[nf++] = j;
        int fill[6];
        int nfill = 1;
        for (int k = 0; k < 6; k++) nfill *= 7; /* 7^6 */
        for (int code = 0; code < nfill; code++) {
            int x = code;
            for (int k = 0; k < 6; k++) {
                fill[k] = x % 7;
                x /= 7;
            }
            int a[DIM] = {0}, b[DIM] = {0};
            a[p0] = 1;
            b[p1] = 1;
            a[free_idx[0]] = fill[0];
            a[free_idx[1]] = fill[1];
            a[free_idx[2]] = fill[2];
            b[free_idx[0]] = fill[3];
            b[free_idx[1]] = fill[4];
            b[free_idx[2]] = fill[5];
            checked++;
            if (!rank2_ok(a, b)) continue;
            if (!is_good(a, b)) continue;
            n_good++;
            int M[5][5], Inv[5][5];
            memset(M, 0, sizeof M);
            for (int j = 0; j < 5; j++) {
                M[0][j] = a[j];
                M[1][j] = b[j];
            }
            int ok = 0;
            for (int t0 = 0; t0 < 5 && !ok; t0++)
            for (int t1 = t0 + 1; t1 < 5 && !ok; t1++)
            for (int t2 = t1 + 1; t2 < 5 && !ok; t2++) {
                memset(M, 0, sizeof M);
                for (int j = 0; j < 5; j++) {
                    M[0][j] = a[j];
                    M[1][j] = b[j];
                }
                M[2][t0] = 1;
                M[3][t1] = 1;
                M[4][t2] = 1;
                if (invert5(M, Inv)) ok = 1;
            }
            if (!ok) continue;

            int forbidden[QN];
            memset(forbidden, 0, sizeof forbidden);
            int nforb = 0;
            int forblist[243];
            for (int s = 0; s < nsmall; s++) {
                int q = qcoord(Inv, SMALL[s]);
                if (!forbidden[q]) {
                    forbidden[q] = 1;
                    forblist[nforb++] = q;
                }
            }
            memset(adj, 0, sizeof adj);
            for (int i = 0; i < QN; i++) {
                int a0 = i / 49, r = i % 49, a1 = r / 7, a2 = r % 7;
                for (int fi = 0; fi < nforb; fi++) {
                    int f = forblist[fi];
                    if (f == 0) continue;
                    int b0 = f / 49, rr = f % 49, b1 = rr / 7, b2 = rr % 7;
                    int d0 = (a0 - b0 + 7) % 7;
                    int d1 = (a1 - b1 + 7) % 7;
                    int d2 = (a2 - b2 + 7) % 7;
                    int j = d0 * 49 + d1 * 7 + d2;
                    if (j == i) continue;
                    int bit = i * QN + j;
                    adj[bit / 64] |= 1ull << (bit % 64);
                }
            }
            int local_best = 0;
            for (int trial = 0; trial < 8; trial++) {
                int pack = greedy_mis(QN, adj, 1u + (unsigned)n_good * 17u + (unsigned)trial);
                if (pack > local_best) local_best = pack;
            }
            if (local_best > best) {
                best = local_best;
                printf("good #%d V=(%d%d%d%d%d / %d%d%d%d%d) forb=%d cosets=%d total=%d\n",
                       n_good, a[0], a[1], a[2], a[3], a[4], b[0], b[1], b[2], b[3],
                       b[4], nforb, local_best, 49 * local_best);
                fflush(stdout);
            }
            if (n_good <= 3 || n_good % 200 == 0) {
                printf("  good=%d checked=%d best_cosets=%d\n", n_good, checked, best);
                fflush(stdout);
            }
            if (best >= 8) {
                printf("HIT cosets=%d total=%d\n", best, 49 * best);
                /* materialising the set is left to Python if this prints */
            }
        }
    }
    printf("DONE checked=%d good=%d best_cosets=%d best_total=%d\n", checked, n_good,
           best, 49 * best);
    return 0;
}
