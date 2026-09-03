/* Independent check of the mass-stationary aspect algebra at R=10.
 *
 *   M1 = Q+(Q-1)D,  M3=(Q-1)R^3 + Q D R
 *   M1>0 and M3>0  ⇒  R < Q/(1-Q).
 * At R=10 this forces Q > 10/11.
 *
 * Build: gcc -O2 -o verify_aspect verify_aspect.c -lm
 */
#include <math.h>
#include <stdio.h>

static int fail = 0;

static void check(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg);
        fail = 1;
    }
}

static double g_kernel(double r, double u) {
    double m = r >= u ? r : u;
    return (r * r * r + u * u * u) / (2.0 * m);
}

int main(void) {
    const double R = 10.0;
    const double cut = 10.0 / 11.0;
    int qn, empty_bad = 0, nonempty_bad = 0;
    for (qn = 890; qn < 1000; qn++) {
        double Q = qn / 1000.0;
        double lo = ((1.0 - Q) / Q) * (R * R);
        double hi = Q / (1.0 - Q);
        if (Q <= cut + 1e-15) {
            if (lo < hi - 1e-12)
                empty_bad++;
        } else if (lo >= hi + 1e-12)
            nonempty_bad++;
        else {
            double D = 0.5 * (lo + hi);
            double M1 = Q + (Q - 1.0) * D;
            double M3 = (Q - 1.0) * (R * R * R) + Q * D * R;
            check(M1 > 0.0 && M3 > 0.0, "moments at midpoint");
            check(R < Q / (1.0 - Q) + 1e-12, "R < Q/(1-Q)");
        }
    }
    check(empty_bad == 0, "D-interval empty for Q<=10/11");
    check(nonempty_bad == 0, "D-interval nonempty for Q>10/11");

    double r1 = 1.0, r2 = R;
    double m1 = 0.5 / (r1 * r1);
    double m2 = 0.5 / (r2 * r2);
    double s = m1 + m2;
    m1 /= s;
    m2 /= s;
    double D = m1 * r1 * r1 + m2 * r2 * r2;
    double Mm1 = m1 / r1 + m2 / r2;
    double M3 = m1 * r1 * r1 * r1 + m2 * r2 * r2 * r2;
    double V1 = m1 * g_kernel(r1, r1) + m2 * g_kernel(r1, r2);
    double V2 = m1 * g_kernel(r2, r1) + m2 * g_kernel(r2, r2);
    double Q = (m1 * V1 + m2 * V2) / D;
    check(fabs(V1 - (D / 2.0 + Mm1 / 2.0)) < 1e-12, "V(1) identity");
    check(fabs(V2 - (r2 * r2 / 2.0 + M3 / (2.0 * r2))) < 1e-12, "V(R) identity");
    check(Q > cut, "this 2-atom sits above 10/11 (not a bound)");

    FILE *out = fopen("certs/aspect_c.txt", "w");
    if (!out)
        return 1;
    fprintf(out, "empty_bad %d\n", empty_bad);
    fprintf(out, "nonempty_bad %d\n", nonempty_bad);
    fprintf(out, "two_atom_Q %.16e\n", Q);
    fprintf(out, "cut %.16e\n", cut);
    fprintf(out, "ok %d\n", fail ? 0 : 1);
    fclose(out);

    if (fail) {
        fprintf(stderr, "verify_aspect.c FAIL\n");
        return 1;
    }
    printf("verify_aspect.c PASS  two-atom Q=%.6f  cut=%.6f\n", Q, cut);
    return 0;
}
