/* Gray-code face enumerator for the mid-radius Rayleigh.
 *
 * Same certificate as verify_beta3.c: min m^T M m on every face-critical
 * point of the simplex, M = A − γ (c 1^T + 1 c^T)/2.
 *
 * Walks the nonempty subsets in binary-reflected Gray order. Each step
 * adds or removes one index, so the inverse of M_S is a rank-1 / border
 * update (O(k^2)) instead of Gauss-Jordan from scratch (O(k^3)).
 *
 * Rebuilds the inverse if M xs drifts from 1. RAM is O(n^2). One thread.
 *
 * Usage: verify_gray matrix.txt faces.txt [start_i]
 * start_i is the 1-based Gray counter (not the bitmask). 0 / omitted
 * starts from the empty set, or resumes from faces.txt if that file
 * already has gray_i < n_faces and min_mMm > 0. Checkpoints every 2^24.
 *
 * gcc -O3 -march=native -o verify_gray verify_gray.c -lm
 */
#include <math.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define NMAX 40
#define EPS 1e-12
#define MARGIN 1e-10
#define SING_EPS 1e-14
#define RESID_CHECK 256u
#define CKPT (1u << 24)

static int n;
static double gamma_t;
static double c[NMAX];
static double A[NMAX][NMAX];
static double M[NMAX][NMAX];

static int k;
static int idx[NMAX];
static double Inv[NMAX][NMAX];
static double xs[NMAX]; /* Inv * 1, valid iff inv_ok */
static int inv_ok;

static double min_val = 1e300;
static double min_phi = 1e300;
static unsigned long long interior;
static unsigned long long singular;
static unsigned long long nfaces;
static unsigned long long start_i;
static unsigned long long g_ii;
static const char *g_faces;
static volatile sig_atomic_t g_stop;

static void on_sig(int sig) {
    (void)sig;
    g_stop = 1;
}

static unsigned long long rss_kb(void) {
    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    unsigned long long kb = 0;
    if (!f)
        return 0;
    while (fgets(line, sizeof line, f)) {
        if (sscanf(line, "VmRSS: %llu", &kb) == 1)
            break;
    }
    fclose(f);
    return kb;
}

static void die(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg);
    exit(1);
}

static int solve_system(int kk, double G[NMAX][NMAX], double b[NMAX],
                        double x[NMAX]) {
    double aug[NMAX][NMAX + 1];
    int i, j, p, r;
    for (i = 0; i < kk; i++) {
        for (j = 0; j < kk; j++)
            aug[i][j] = G[i][j];
        aug[i][kk] = b[i];
    }
    for (p = 0; p < kk; p++) {
        int piv = p;
        double best = fabs(aug[p][p]);
        for (i = p + 1; i < kk; i++) {
            double v = fabs(aug[i][p]);
            if (v > best) {
                best = v;
                piv = i;
            }
        }
        if (best < SING_EPS)
            return -1;
        if (piv != p) {
            for (j = p; j <= kk; j++) {
                double tmp = aug[p][j];
                aug[p][j] = aug[piv][j];
                aug[piv][j] = tmp;
            }
        }
        double diag = aug[p][p];
        for (j = p; j <= kk; j++)
            aug[p][j] /= diag;
        for (i = 0; i < kk; i++) {
            if (i == p)
                continue;
            double f = aug[i][p];
            for (j = p; j <= kk; j++)
                aug[i][j] -= f * aug[p][j];
        }
    }
    for (r = 0; r < kk; r++)
        x[r] = aug[r][kk];
    return 0;
}

static int rebuild_inv(void) {
    /* Invert M_S in one Gauss-Jordan pass on [M|I]. */
    double aug[NMAX][2 * NMAX];
    int i, j, p;
    if (k <= 0) {
        inv_ok = 0;
        return -1;
    }
    if (k == 1) {
        if (fabs(M[idx[0]][idx[0]]) < SING_EPS) {
            inv_ok = 0;
            return -1;
        }
        Inv[0][0] = 1.0 / M[idx[0]][idx[0]];
        xs[0] = Inv[0][0];
        inv_ok = 1;
        return 0;
    }
    for (i = 0; i < k; i++) {
        for (j = 0; j < k; j++)
            aug[i][j] = M[idx[i]][idx[j]];
        for (j = 0; j < k; j++)
            aug[i][k + j] = (i == j) ? 1.0 : 0.0;
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
        if (best < SING_EPS) {
            inv_ok = 0;
            return -1;
        }
        if (piv != p) {
            for (j = p; j < 2 * k; j++) {
                double tmp = aug[p][j];
                aug[p][j] = aug[piv][j];
                aug[piv][j] = tmp;
            }
        }
        double diag = aug[p][p];
        for (j = p; j < 2 * k; j++)
            aug[p][j] /= diag;
        for (i = 0; i < k; i++) {
            if (i == p)
                continue;
            double f = aug[i][p];
            for (j = p; j < 2 * k; j++)
                aug[i][j] -= f * aug[p][j];
        }
    }
    for (i = 0; i < k; i++) {
        double acc = 0.0;
        for (j = 0; j < k; j++) {
            Inv[i][j] = aug[i][k + j];
            acc += Inv[i][j];
        }
        xs[i] = acc;
    }
    inv_ok = 1;
    return 0;
}

static int residual_bad(void) {
    int t, s;
    if (!inv_ok || k < 2)
        return 0;
    for (t = 0; t < k; t++) {
        double acc = 0.0;
        for (s = 0; s < k; s++)
            acc += M[idx[t]][idx[s]] * xs[s];
        if (fabs(acc - 1.0) > 1e-8)
            return 1;
    }
    return 0;
}

static void add_index(int p) {
    int t, s;
    double b[NMAX], u[NMAX];
    if (k == 0) {
        idx[0] = p;
        k = 1;
        if (fabs(M[p][p]) < SING_EPS) {
            inv_ok = 0;
            return;
        }
        Inv[0][0] = 1.0 / M[p][p];
        xs[0] = Inv[0][0];
        inv_ok = 1;
        return;
    }
    if (!inv_ok) {
        idx[k++] = p;
        rebuild_inv();
        return;
    }
    for (t = 0; t < k; t++)
        b[t] = M[idx[t]][p];
    for (t = 0; t < k; t++) {
        double acc = 0.0;
        for (s = 0; s < k; s++)
            acc += Inv[t][s] * b[s];
        u[t] = acc;
    }
    double schur = M[p][p];
    for (t = 0; t < k; t++)
        schur -= b[t] * u[t];
    if (fabs(schur) < SING_EPS) {
        idx[k++] = p;
        inv_ok = 0;
        return;
    }
    double invs = 1.0 / schur;
    for (t = 0; t < k; t++)
        for (s = 0; s < k; s++)
            Inv[t][s] += u[t] * u[s] * invs;
    for (t = 0; t < k; t++) {
        double v = -u[t] * invs;
        Inv[t][k] = v;
        Inv[k][t] = v;
    }
    Inv[k][k] = invs;
    {
        double u1 = 0.0;
        for (t = 0; t < k; t++)
            u1 += u[t];
        double scale = (u1 - 1.0) * invs;
        for (t = 0; t < k; t++)
            xs[t] += u[t] * scale;
        xs[k] = (1.0 - u1) * invs;
    }
    idx[k++] = p;
    inv_ok = 1;
}

static void remove_index(int p) {
    int t, s, pos = -1;
    for (t = 0; t < k; t++) {
        if (idx[t] == p) {
            pos = t;
            break;
        }
    }
    if (pos < 0)
        die("remove missing index");
    if (k == 1) {
        k = 0;
        inv_ok = 0;
        return;
    }
    if (!inv_ok) {
        idx[pos] = idx[k - 1];
        k--;
        rebuild_inv();
        return;
    }
    int last = k - 1;
    if (pos != last) {
        int tmpi = idx[pos];
        idx[pos] = idx[last];
        idx[last] = tmpi;
        for (s = 0; s < k; s++) {
            double tmp = Inv[pos][s];
            Inv[pos][s] = Inv[last][s];
            Inv[last][s] = tmp;
        }
        for (s = 0; s < k; s++) {
            double tmp = Inv[s][pos];
            Inv[s][pos] = Inv[s][last];
            Inv[s][last] = tmp;
        }
        {
            double tmp = xs[pos];
            xs[pos] = xs[last];
            xs[last] = tmp;
        }
    }
    double w = Inv[last][last];
    if (fabs(w) < SING_EPS) {
        k--;
        inv_ok = 0;
        return;
    }
    double invw = 1.0 / w;
    for (t = 0; t < last; t++) {
        double ut = Inv[t][last];
        for (s = 0; s < last; s++)
            Inv[t][s] -= ut * Inv[last][s] * invw;
    }
    {
        double u1 = 0.0;
        for (t = 0; t < last; t++)
            u1 += Inv[t][last];
        for (t = 0; t < last; t++)
            xs[t] = xs[t] - Inv[t][last] - Inv[t][last] * u1 * invw;
    }
    k--;
    inv_ok = 1;
}

static void consider_face(void) {
    int t, s;
    if (k <= 1)
        return;
    if (!inv_ok) {
        singular++;
        return;
    }
    double sum = 0.0;
    int sgn = 0;
    int interior_pt = 1;
    for (t = 0; t < k; t++) {
        double xt = xs[t];
        if (fabs(xt) <= EPS) {
            interior_pt = 0;
            break;
        }
        int sp = (xt > 0.0) ? 1 : -1;
        if (sgn == 0)
            sgn = sp;
        else if (sp != sgn) {
            interior_pt = 0;
            break;
        }
        sum += xt;
    }
    if (!interior_pt || fabs(sum) <= EPS)
        return;
    interior++;
    double val = 1.0 / sum;
    if (val < min_val)
        min_val = val;
    double mA = 0.0, mc = 0.0;
    for (t = 0; t < k; t++) {
        double mi = xs[t] / sum;
        mc += mi * c[idx[t]];
        for (s = 0; s < k; s++)
            mA += mi * (xs[s] / sum) * A[idx[t]][idx[s]];
    }
    if (mc > 0.0) {
        double phi = mA / mc;
        if (phi < min_phi)
            min_phi = phi;
    }
}

static void write_faces(const char *path, unsigned long long cur_i) {
    double min_val_safe = min_val - MARGIN;
    double min_phi_safe = min_phi - MARGIN;
    int ok = (min_val_safe >= 0.0);
    FILE *out = fopen(path, "w");
    if (!out)
        die("cannot write faces");
    fprintf(out, "n %d\n", n);
    fprintf(out, "gamma_target %.16e\n", gamma_t);
    fprintf(out, "n_faces %llu\n", nfaces);
    fprintf(out, "gray_i %llu\n", cur_i);
    fprintf(out, "interior_critical %llu\n", interior);
    fprintf(out, "singular_or_illconditioned %llu\n", singular);
    fprintf(out, "min_mMm %.16e\n", min_val);
    fprintf(out, "min_mMm_safe %.16e\n", min_val_safe);
    fprintf(out, "min_phi %.16e\n", min_phi);
    fprintf(out, "min_phi_safe %.16e\n", min_phi_safe);
    fprintf(out, "copositive %d\n", ok);
    fclose(out);
    {
        const char *bak = getenv("GRAY_BACKUP");
        if (bak && bak[0]) {
            FILE *b = fopen(bak, "w");
            if (b) {
                fprintf(b, "n %d\n", n);
                fprintf(b, "gamma_target %.16e\n", gamma_t);
                fprintf(b, "n_faces %llu\n", nfaces);
                fprintf(b, "gray_i %llu\n", cur_i);
                fprintf(b, "interior_critical %llu\n", interior);
                fprintf(b, "singular_or_illconditioned %llu\n", singular);
                fprintf(b, "min_mMm %.16e\n", min_val);
                fprintf(b, "min_mMm_safe %.16e\n", min_val_safe);
                fprintf(b, "min_phi %.16e\n", min_phi);
                fprintf(b, "min_phi_safe %.16e\n", min_phi_safe);
                fprintf(b, "copositive %d\n", ok);
                fclose(b);
            }
        }
    }
}

static int load_checkpoint(const char *path) {
    FILE *f = fopen(path, "r");
    char key[64];
    if (!f)
        return 0;
    unsigned long long gi = 0;
    double mv = 0.0, mpv = 0.0;
    unsigned long long ic = 0, sg = 0;
    int cop = 0;
    int got_gi = 0;
    while (fscanf(f, "%63s", key) == 1) {
        if (strcmp(key, "gray_i") == 0) {
            if (fscanf(f, "%llu", &gi) != 1)
                break;
            got_gi = 1;
        } else if (strcmp(key, "min_mMm") == 0) {
            if (fscanf(f, "%lf", &mv) != 1)
                break;
        } else if (strcmp(key, "min_phi") == 0) {
            if (fscanf(f, "%lf", &mpv) != 1)
                break;
        } else if (strcmp(key, "interior_critical") == 0) {
            if (fscanf(f, "%llu", &ic) != 1)
                break;
        } else if (strcmp(key, "singular_or_illconditioned") == 0) {
            if (fscanf(f, "%llu", &sg) != 1)
                break;
        } else if (strcmp(key, "copositive") == 0) {
            if (fscanf(f, "%d", &cop) != 1)
                break;
        } else {
            char skip[256];
            if (fscanf(f, "%255s", skip) != 1)
                break;
        }
    }
    fclose(f);
    if (!got_gi || gi == 0 || mv <= 0.0 || !cop)
        return 0;
    start_i = gi;
    min_val = mv;
    min_phi = mpv;
    interior = ic;
    singular = sg;
    fprintf(stderr, "resume gray_i=%llu minM=%.4e minphi=%.8f\n", gi, mv, mpv);
    return 1;
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
    g_faces = faces_path;
    load_matrix(mat_path);
    nfaces = (1ULL << n) - 1ULL;
    start_i = 0;
    if (argc > 3)
        start_i = strtoull(argv[3], NULL, 10);
    else
        load_checkpoint(faces_path);

    signal(SIGTERM, on_sig);
    signal(SIGINT, on_sig);

    int i;
    if (start_i == 0) {
        for (i = 0; i < n; i++) {
            if (M[i][i] < min_val)
                min_val = M[i][i];
            double phi_i = A[i][i] / c[i];
            if (phi_i < min_phi)
                min_phi = phi_i;
        }
    }

    k = 0;
    inv_ok = 0;
    struct timespec t0;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    unsigned long long gray = 0;
    unsigned long long ii;
    /* Fast-forward: apply Gray bits of start_i without considering faces. */
    if (start_i > 0) {
        gray = start_i ^ (start_i >> 1);
        int b;
        for (b = 0; b < n; b++) {
            if (gray & (1ULL << b))
                add_index(b);
        }
        if (!inv_ok)
            rebuild_inv();
        /* The start_i face is already in the checkpoint mins / counts. */
    }

    for (ii = start_i + 1; ii <= nfaces; ii++) {
        g_ii = ii;
        int bit = __builtin_ctzll(ii);
        int adding = !((gray >> bit) & 1ULL);
        gray ^= (1ULL << bit);
        if (adding)
            add_index(bit);
        else
            remove_index(bit);
        if ((ii & (RESID_CHECK - 1u)) == 0 && residual_bad())
            rebuild_inv();
        consider_face();
        if (g_stop) {
            write_faces(faces_path, ii);
            fprintf(stderr, "stopped gray_i=%llu rss_kb=%llu\n", ii, rss_kb());
            return 2;
        }
        if ((ii & (CKPT - 1u)) == 0) {
            struct timespec t1;
            clock_gettime(CLOCK_MONOTONIC, &t1);
            double sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
            double rate = (ii - start_i) / (sec > 1e-9 ? sec : 1e-9);
            double eta = (nfaces - ii) / (rate > 1.0 ? rate : 1.0);
            fprintf(stderr,
                    "  ... gray_i %llu / %llu  minM=%.4e  "
                    "%.3e/s  eta=%.1fs  rss_kb=%llu\n",
                    ii, nfaces, min_val, rate, eta, rss_kb());
            fflush(stderr);
            write_faces(faces_path, ii);
        }
    }

    write_faces(faces_path, nfaces);
    double min_val_safe = min_val - MARGIN;
    double min_phi_safe = min_phi - MARGIN;
    int ok = (min_val_safe >= 0.0);
    printf("n=%d  gamma_target=%.10f  min m^T M m = %.8e  (safe %.8e)\n", n,
           gamma_t, min_val, min_val_safe);
    printf("min Rayleigh phi = %.10f  (safe %.10f)\n", min_phi, min_phi_safe);
    printf("interior critical points: %llu   singular skips: %llu\n", interior,
           singular);
    if (!ok) {
        fprintf(stderr, "FAIL: M not certified copositive on the simplex\n");
        return 1;
    }
    printf("verify_gray.c PASS (M copositive at gamma_target)\n");
    return 0;
}
