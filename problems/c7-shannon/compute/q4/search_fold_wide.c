/* Wider fold-and-repair than the 2016-08-16 Python grid.

   Geometric orbits t*(1,q,q^2,q^3,q^4) in Z/n, n=360..420, more
   shifts and fold denominators. Keep isolates of the folded image,
   greedy-extend the residual. Writes a set iff total >= 368.

   gcc -O3 -o q4/search_fold_wide q4/search_fold_wide.c
   ./q4/search_fold_wide
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807

static int coord[NV][5];
static int neigh[NV][243];

static int encode_c(const int c[5]) {
    return ((((c[0] * 7 + c[1]) * 7 + c[2]) * 7 + c[3]) * 7 + c[4]);
}

static void fill_tables(void) {
    for (int v = 0; v < NV; v++) {
        int x = v;
        for (int i = 4; i >= 0; i--) {
            coord[v][i] = x % 7;
            x /= 7;
        }
        int n = 0, o0, o1, o2, o3, o4;
        for (o0 = -1; o0 <= 1; o0++)
            for (o1 = -1; o1 <= 1; o1++)
                for (o2 = -1; o2 <= 1; o2++)
                    for (o3 = -1; o3 <= 1; o3++)
                        for (o4 = -1; o4 <= 1; o4++) {
                            int c[5];
                            c[0] = (coord[v][0] + o0 + 7) % 7;
                            c[1] = (coord[v][1] + o1 + 7) % 7;
                            c[2] = (coord[v][2] + o2 + 7) % 7;
                            c[3] = (coord[v][3] + o3 + 7) % 7;
                            c[4] = (coord[v][4] + o4 + 7) % 7;
                            neigh[v][n++] = encode_c(c);
                        }
    }
}

static int circ_n(int x, int n) {
    x %= n;
    if (x < 0) x += n;
    return x <= n - x ? x : n - x;
}

static int k_of(int n, int q) {
    int pows[5];
    pows[0] = 1;
    for (int i = 1; i < 5; i++) pows[i] = (int)((long)pows[i - 1] * q % n);
    int best = n;
    for (int t = 1; t < n; t++) {
        int mx = 0;
        for (int i = 0; i < 5; i++) {
            int d = circ_n((int)((long)t * pows[i] % n), n);
            if (d > mx) mx = d;
        }
        if (mx < best) best = mx;
    }
    return best;
}

static int adj_uv(int u, int v) {
    if (u == v) return 0;
    for (int i = 0; i < 5; i++) {
        int d = coord[u][i] - coord[v][i];
        if (d < 0) d = -d;
        if (d > 3) d = 7 - d;
        if (d > 1) return 0;
    }
    return 1;
}

static int score_orbit(int n, int q, const int shift[5], int den, int *out_n) {
    int pows[5];
    pows[0] = 1;
    for (int i = 1; i < 5; i++) pows[i] = (int)((long)pows[i - 1] * q % n);
    uint8_t seen[NV];
    memset(seen, 0, sizeof seen);
    int words[512], nw = 0;
    for (int t = 0; t < n; t++) {
        int c[5], ok = 1;
        for (int i = 0; i < 5; i++) {
            int x = (int)(((long)t * pows[i] + shift[i]) % n);
            int let = (2 * x) / den;
            if (let < 0 || let > 6) {
                ok = 0;
                break;
            }
            c[i] = let;
        }
        if (!ok) {
            *out_n = 0;
            return 0;
        }
        int v = encode_c(c);
        if (!seen[v]) {
            seen[v] = 1;
            if (nw < 512) words[nw++] = v;
        }
    }
    /* isolates */
    uint8_t iso[NV];
    memset(iso, 0, sizeof iso);
    int M[512], nM = 0;
    for (int i = 0; i < nw; i++) {
        int bad = 0;
        for (int j = 0; j < nw; j++)
            if (i != j && adj_uv(words[i], words[j])) {
                bad = 1;
                break;
            }
        if (!bad) {
            iso[words[i]] = 1;
            M[nM++] = words[i];
        }
    }
    int blocked[NV];
    memset(blocked, 0, sizeof blocked);
    for (int i = 0; i < nM; i++)
        for (int k = 0; k < 243; k++) blocked[neigh[M[i]][k]] = 1;
    int ext = 0;
    for (int v = 0; v < NV; v++) {
        if (blocked[v]) continue;
        ext++;
        for (int k = 0; k < 243; k++) blocked[neigh[v][k]] = 1;
    }
    *out_n = nM + ext;
    return nM;
}

int main(void) {
    clock_t t0 = clock();
    fill_tables();
    int best = 0, n_try = 0;
    int shifts[][5] = {
        {0, 0, 0, 0, 0},
        {40, 123, 40, 123, 40},
        {1, 0, 0, 0, 0},
        {0, 1, 0, 0, 0},
        {20, 60, 20, 60, 20},
        {54, 0, 54, 0, 54},
        {0, 54, 0, 54, 0},
        {17, 51, 17, 51, 17},
        {80, 246, 80, 246, 80},
    };
    int nsh = 9;
    for (int n = 360; n <= 420; n++) {
        int need = (2 * n + 6) / 7;
        int qs[8], nq = 0, bestk = -1;
        int qmax = n - 2 < 50 ? n - 2 : 50;
        for (int q = 2; q <= qmax; q++) {
            int k = k_of(n, q);
            if (k > bestk) bestk = k;
            if (k >= need - 6 && nq < 8) qs[nq++] = q;
        }
        if (!nq) continue;
        int dens[8];
        int nd = 0;
        dens[nd++] = 2 * bestk;
        dens[nd++] = 2 * bestk - 1;
        dens[nd++] = 2 * bestk + 1;
        dens[nd++] = 109;
        dens[nd++] = 108;
        dens[nd++] = 110;
        for (int qi = 0; qi < nq; qi++) {
            int q = qs[qi];
            for (int si = 0; si < nsh; si++) {
                for (int di = 0; di < nd; di++) {
                    int den = dens[di];
                    if (den < 8) continue;
                    int tot = 0;
                    int m = score_orbit(n, q, shifts[si], den, &tot);
                    n_try++;
                    if (tot > best) {
                        best = tot;
                        printf("best=%d M=%d n=%d q=%d den=%d shift=%d,%d,%d,%d,%d\n",
                               tot, m, n, q, den, shifts[si][0], shifts[si][1],
                               shifts[si][2], shifts[si][3], shifts[si][4]);
                        fflush(stdout);
                    }
                    if (tot >= 368) {
                        printf("HIT total=%d n=%d q=%d den=%d\n", tot, n, q, den);
                        return 0;
                    }
                }
            }
        }
        printf("n=%d need=%d bestk=%d nq=%d running_best=%d tries=%d t=%.1fs\n", n,
               need, bestk, nq, best, n_try,
               (double)(clock() - t0) / CLOCKS_PER_SEC);
        fflush(stdout);
    }
    printf("DONE tries=%d best=%d t=%.2fs\n", n_try, best,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
