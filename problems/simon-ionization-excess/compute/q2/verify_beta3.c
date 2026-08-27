/* Face-enumeration lower bound of the discrete mid-radius Rayleigh
 *
 *   φ(m) = (m^T A m) / (c · m)    on { m ≥ 0, 1·m = 1 }
 *
 * Equivalent, for a candidate γ: min m^T M m ≥ 0 on the simplex, where
 *   M = A − γ (c 1^T + 1 c^T)/2.
 *
 * Exhaustive over all 2^n − 1 faces. On face S the critical point of
 * the quadratic m^T M m subject to 1·m = 1 is
 *   m = M_S^{-1} 1 / (1^T M_S^{-1} 1),
 * value = 1 / (1^T M_S^{-1} 1), provided m > 0 on S.
 * Vertices: value = M_ii.
 *
 * The global min of a quadratic on a compact convex polytope is attained
 * at a face-critical point (or a vertex). Singular faces have their min
 * on a proper subface (already enumerated).
 *
 * Input: matrix path (default certs/beta3_matrix.txt)
 *   line 1: n gamma_target
 *   line 2: c_0 ... c_{n-1}
 *   next n lines: rows of A
 *
 * Output: faces path (default certs/beta3_faces.txt)
 *
 * Usage: verify_beta3 [matrix.txt] [faces.txt]
 *
 * Build: gcc -O3 -o verify_beta3 verify_beta3.c -lm
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NMAX 32
#define EPS 1e-12
#define MARGIN 1e-10

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
    /* Gauss-Jordan with partial pivot. Returns 0 on success. */
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
            return -1; /* singular */
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
        if (!(c[i] > 0))
            die("c must be positive");
    }
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            if (fscanf(f, "%lf", &A[i][j]) != 1)
                die("bad A");
        }
    }
    fclose(f);
    /* M = A - γ (c 1^T + 1 c^T)/2 */
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            M[i][j] = A[i][j] - 0.5 * gamma_t * (c[i] + c[j]);
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    const char *mat_path = argc > 1 ? argv[1] : "certs/beta3_matrix.txt";
    const char *faces_path = argc > 2 ? argv[2] : "certs/beta3_faces.txt";
    load_matrix(mat_path);

    double min_val = 1e300;
    double min_phi = 1e300;
    unsigned long long nfaces = (1ULL << n) - 1ULL;
    unsigned long long interior = 0;
    unsigned long long singular = 0;
    unsigned long long mask;

    /* vertices of M and of the Rayleigh */
    int i;
    for (i = 0; i < n; i++) {
        if (M[i][i] < min_val)
            min_val = M[i][i];
        double phi_i = A[i][i] / c[i];
        if (phi_i < min_phi)
            min_phi = phi_i;
    }

    for (mask = 1; mask <= nfaces; mask++) {
        if ((mask & ((1ULL << 22) - 1)) == 0) {
            fprintf(stderr, "  ... mask %llu / %llu  minM=%.4e\n",
                    (unsigned long long)mask, (unsigned long long)nfaces,
                    min_val);
            fflush(stderr);
        }
        int idx[NMAX];
        int k = 0;
        int b;
        for (b = 0; b < n; b++) {
            if (mask & (1ULL << b))
                idx[k++] = b;
        }
        if (k <= 1)
            continue; /* vertices already done */

        double G[NMAX][NMAX];
        double rhs[NMAX];
        double x[NMAX];
        int p, q;
        for (p = 0; p < k; p++) {
            for (q = 0; q < k; q++)
                G[p][q] = M[idx[p]][idx[q]];
            rhs[p] = 1.0;
        }
        if (solve_system(k, G, rhs, x) != 0) {
            singular++;
            continue;
        }
        /* residual */
        double rmax = 0.0;
        for (p = 0; p < k; p++) {
            double acc = 0.0;
            for (q = 0; q < k; q++)
                acc += G[p][q] * x[q];
            /* G was overwritten by solve? recompute from M */
            acc = 0.0;
            for (q = 0; q < k; q++)
                acc += M[idx[p]][idx[q]] * x[q];
            double res = fabs(acc - 1.0);
            if (res > rmax)
                rmax = res;
        }
        if (rmax > 1e-8) {
            singular++;
            continue;
        }
        /* m = x / (1·x) lies in the relative interior iff every x_p
         * is nonzero and they all share a sign (all + or all −). */
        int interior_pt = 1;
        int sgn = 0;
        double s = 0.0;
        for (p = 0; p < k; p++) {
            if (fabs(x[p]) <= EPS) {
                interior_pt = 0;
                break;
            }
            int sp = (x[p] > 0.0) ? 1 : -1;
            if (sgn == 0)
                sgn = sp;
            else if (sp != sgn) {
                interior_pt = 0;
                break;
            }
            s += x[p];
        }
        if (!interior_pt || fabs(s) <= EPS)
            continue;
        interior++;
        /* value of m^T M m at m = x/s  is 1/s */
        double val = 1.0 / s;
        if (val < min_val)
            min_val = val;

        /* Rayleigh at this point (same m) */
        double mA = 0.0, mc = 0.0;
        for (p = 0; p < k; p++) {
            double mi = x[p] / s;
            mc += mi * c[idx[p]];
            for (q = 0; q < k; q++)
                mA += mi * (x[q] / s) * A[idx[p]][idx[q]];
        }
        if (mc > 0) {
            double phi = mA / mc;
            if (phi < min_phi)
                min_phi = phi;
        }
    }

    double min_val_safe = min_val - MARGIN;
    double min_phi_safe = min_phi - MARGIN;
    int ok = (min_val_safe >= 0.0);

    FILE *out = fopen(faces_path, "w");
    if (!out)
        die("cannot write faces");
    fprintf(out, "n %d\n", n);
    fprintf(out, "gamma_target %.16e\n", gamma_t);
    fprintf(out, "n_faces %llu\n", (unsigned long long)nfaces);
    fprintf(out, "interior_critical %llu\n", interior);
    fprintf(out, "singular_or_illconditioned %llu\n", singular);
    fprintf(out, "min_mMm %.16e\n", min_val);
    fprintf(out, "min_mMm_safe %.16e\n", min_val_safe);
    fprintf(out, "min_phi %.16e\n", min_phi);
    fprintf(out, "min_phi_safe %.16e\n", min_phi_safe);
    fprintf(out, "copositive %d\n", ok);
    fclose(out);

    printf("n=%d  gamma_target=%.10f  min m^T M m = %.8e  (safe %.8e)\n", n,
           gamma_t, min_val, min_val_safe);
    printf("min Rayleigh phi = %.10f  (safe %.10f)\n", min_phi, min_phi_safe);
    printf("interior critical points: %llu   singular skips: %llu\n", interior,
           singular);
    if (!ok) {
        fprintf(stderr, "FAIL: M not certified copositive on the simplex\n");
        return 1;
    }
    printf("verify_beta3.c PASS (M copositive at gamma_target)\n");
    return 0;
}
