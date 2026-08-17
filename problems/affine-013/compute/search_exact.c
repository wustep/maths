/* Exact max T on n-subsets of {0,...,D} containing 0.
 *
 * Incremental combinations + incremental T via delta-on-add.
 * Compile: cc -O3 -o search_exact search_exact.c
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

static int D, N;
static int present[128];
static int pts[64];
static int best_T;
static int best_set[64];
static int n_best;
static long long seen;

static int delta_add(int p) {
    int d = 1; /* (p,p,p) */
    int x, y, tot, num;
    for (y = 0; y <= D; y++) if (present[y]) {
        tot = p + 2 * y;
        if (tot % 3 == 0) {
            int z = tot / 3;
            if (z >= 0 && z <= D && present[z]) d++;
        }
    }
    for (x = 0; x <= D; x++) if (present[x]) {
        tot = x + 2 * p;
        if (tot % 3 == 0) {
            int z = tot / 3;
            if (z >= 0 && z <= D && present[z]) d++;
        }
    }
    tot = 3 * p;
    for (x = 0; x <= D; x++) if (present[x]) {
        num = tot - x;
        if ((num & 1) == 0) {
            y = num / 2;
            if (y >= 0 && y <= D && present[y]) d++;
        }
    }
    return d;
}

static int interval_t(int n) {
    int a0 = (n + 2) / 3;
    int a1 = (n + 1) / 3;
    int a2 = n / 3;
    return a0 * a0 + a1 * a1 + a2 * a2;
}

static void rec(int start, int remaining, int tcur) {
    if (remaining == 0) {
        seen++;
        if (tcur > best_T) {
            best_T = tcur;
            n_best = 1;
            memcpy(best_set, pts, (size_t)N * sizeof(int));
        } else if (tcur == best_T) {
            n_best++;
        }
        return;
    }
    int last_ok = D - remaining + 1;
    int p;
    for (p = start; p <= last_ok; p++) {
        int dlt = delta_add(p);
        present[p] = 1;
        pts[N - remaining] = p;
        rec(p + 1, remaining - 1, tcur + dlt);
        present[p] = 0;
    }
}

int main(int argc, char **argv) {
    int nmin = 1, nmax = 10, dmult = 3, dfix = 0;
    int n;
    if (argc >= 3) { nmin = atoi(argv[1]); nmax = atoi(argv[2]); }
    if (argc >= 4) dmult = atoi(argv[3]);
    if (argc >= 5) dfix = atoi(argv[4]);
    printf("n dmax T I ratio I_ratio beat seen n_best\n");
    for (n = nmin; n <= nmax; n++) {
        N = n;
        D = dfix ? dfix : n * dmult;
        if (n <= 6 && D < 18) D = 18;
        if (D > 120) D = 120;
        memset(present, 0, sizeof present);
        present[0] = 1;
        pts[0] = 0;
        best_T = interval_t(n);
        n_best = 0;
        seen = 0;
        rec(1, n - 1, 1);
        printf("%d %d %d %d %.6f %.6f %d %lld %d\n",
               n, D, best_T, interval_t(n),
               best_T / (double)(n * n),
               interval_t(n) / (double)(n * n),
               best_T > interval_t(n),
               seen, n_best);
        fflush(stdout);
        printf("  set:");
        for (int i = 0; i < n; i++) printf(" %d", best_set[i]);
        printf("\n");
        fflush(stdout);
    }
    return 0;
}
