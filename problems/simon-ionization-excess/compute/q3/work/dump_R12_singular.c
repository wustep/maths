/* List singular/ill-conditioned faces of the R=12 n=22 compact matrix.
 * Same solver as q2/verify_beta3.c; prints masks that were skipped.
 * Does not overwrite q2 artifacts.
 *
 * Build: gcc -O3 -o dump_R12_singular dump_R12_singular.c -lm
 * Run:   ./dump_R12_singular ../../q2/certs/beta3_mid_R12_n22.txt
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define NMAX 32
#define EPS 1e-12

static int n;
static double gamma_t;
static double c[NMAX];
static double A[NMAX][NMAX];
static double M[NMAX][NMAX];

static void die(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg);
    exit(1);
}

static int solve_system(int k, double G[NMAX][NMAX], double b[NMAX],
                        double x[NMAX]) {
    double aug[NMAX][NMAX + 1];
    int i, j, p, r;
    for (i = 0; i < k; i++) {
        for (j = 0; j < k; j++)
            aug[i][j] = G[i][j];
        aug[i][k] = b[i];
    }
    for (p = 0; p < k; p++) {
        int piv = p;
        double best = fabs(aug[p][p]);
        for (i = p + 1; i < k; i++) {
            double v = fabs(aug[i][p]);
            if (v > best) {
                best = v;
                piv = i;
            }
        }
        if (best < 1e-14)
            return -1;
        if (piv != p) {
            for (j = p; j <= k; j++) {
                double tmp = aug[p][j];
                aug[p][j] = aug[piv][j];
                aug[piv][j] = tmp;
            }
        }
        double diag = aug[p][p];
        for (j = p; j <= k; j++)
            aug[p][j] /= diag;
        for (i = 0; i < k; i++) {
            if (i == p)
                continue;
            double f = aug[i][p];
            for (j = p; j <= k; j++)
                aug[i][j] -= f * aug[p][j];
        }
    }
    for (r = 0; r < k; r++)
        x[r] = aug[r][k];
    return 0;
}

static int load_matrix(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f)
        die("cannot open matrix");
    if (fscanf(f, "%d %lf", &n, &gamma_t) != 2)
        die("bad header");
    if (n < 1 || n > NMAX)
        die("n out of range");
    int i, j;
    for (i = 0; i < n; i++) {
        if (fscanf(f, "%lf", &c[i]) != 1)
            die("bad c");
    }
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            if (fscanf(f, "%lf", &A[i][j]) != 1)
                die("bad A");
        }
    }
    fclose(f);
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            M[i][j] = A[i][j] - 0.5 * gamma_t * (c[i] + c[j]);
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    const char *mat_path = argc > 1 ? argv[1] : "../../q2/certs/beta3_mid_R12_n22.txt";
    load_matrix(mat_path);

    unsigned long long nfaces = (1ULL << n) - 1ULL;
    unsigned long long mask;
    unsigned long long singular = 0;

    printf("# n=%d gamma=%.16e nfaces=%llu\n", n, gamma_t, nfaces);
    printf("# columns: mask k reason rmax min_abs_eig_est n_pos n_neg val_pinv phi_pinv\n");

    for (mask = 1; mask <= nfaces; mask++) {
        int idx[NMAX];
        int k = 0;
        int b;
        for (b = 0; b < n; b++) {
            if (mask & (1ULL << b))
                idx[k++] = b;
        }
        if (k <= 1)
            continue;

        double G[NMAX][NMAX];
        double rhs[NMAX];
        double x[NMAX];
        int p, q;
        for (p = 0; p < k; p++) {
            for (q = 0; q < k; q++)
                G[p][q] = M[idx[p]][idx[q]];
            rhs[p] = 1.0;
        }
        int sing = 0;
        const char *reason = "ok";
        if (solve_system(k, G, rhs, x) != 0) {
            sing = 1;
            reason = "pivot";
        } else {
            double rmax = 0.0;
            for (p = 0; p < k; p++) {
                double acc = 0.0;
                for (q = 0; q < k; q++)
                    acc += M[idx[p]][idx[q]] * x[q];
                double res = fabs(acc - 1.0);
                if (res > rmax)
                    rmax = res;
            }
            if (rmax > 1e-8) {
                sing = 1;
                reason = "resid";
            }
            if (sing) {
                double s = 0.0;
                int npos = 0, nneg = 0;
                for (p = 0; p < k; p++) {
                    s += x[p];
                    if (x[p] > EPS)
                        npos++;
                    else if (x[p] < -EPS)
                        nneg++;
                }
                double val = (fabs(s) > EPS) ? (1.0 / s) : 0.0 / 0.0;
                printf("%llu %d %s %.3e %.6e %d %d %.6e\n", mask, k, reason,
                       rmax, s, npos, nneg, val);
                singular++;
            }
            continue;
        }
        if (sing) {
            printf("%llu %d %s nan nan 0 0 nan\n", mask, k, reason);
            singular++;
        }
    }
    fprintf(stderr, "singular_or_illconditioned %llu\n", singular);
    return 0;
}
