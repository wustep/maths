/* Independent check of the mass-stationary aspect algebra.
 *
 * For Q ∈ (0,1), D>0, R>1:
 *   M1 = Q+(Q-1)D,  M3=(Q-1)R^3 + Q D R
 *   M1>0 and M3>0  ⇒  R < Q/(1-Q).
 * At R=12 this forces Q > 12/13.
 *
 * Also recomputes I,D,V for an explicit 2-atom at (1,12) with
 * equal-in-z masses and checks the kernel identities
 *   V(1)=D/2+M_{-1}/2,  V(R)=R^2/2+M_3/(2R)
 * (those identities do not need criticality).
 *
 * Build: gcc -O2 -o verify_aspect verify_aspect.c -lm
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

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
    /* Algebra grid */
    int qn, empty_bad = 0, nonempty_bad = 0;
    for (qn = 895; qn < 1000; qn++) {
        double Q = qn / 1000.0;
        double lo = ((1.0 - Q) / Q) * 144.0;
        double hi = Q / (1.0 - Q);
        if (Q <= 12.0 / 13.0 + 1e-15) {
            if (lo < hi - 1e-12)
                empty_bad++;
        } else {
            if (lo >= hi + 1e-12)
                nonempty_bad++;
            else {
                /* pick midpoint D and check both moments positive ⇒ R<Q/(1-Q) */
                double D = 0.5 * (lo + hi);
                double M1 = Q + (Q - 1.0) * D;
                double M3 = (Q - 1.0) * 1728.0 + Q * D * 12.0;
                check(M1 > 0.0 && M3 > 0.0, "moments at midpoint");
                check(12.0 < Q / (1.0 - Q) + 1e-12, "R < Q/(1-Q)");
            }
        }
    }
    check(empty_bad == 0, "D-interval empty for Q<=12/13");
    check(nonempty_bad == 0, "D-interval nonempty for Q>12/13");

    /* Kernel identities on a 2-atom, not necessarily critical */
    double r1 = 1.0, r2 = 12.0;
    double z1 = 0.5, z2 = 0.5; /* equal D-mass: m_i = z_i / r_i^2, then renormalise */
    double m1 = z1 / (r1 * r1);
    double m2 = z2 / (r2 * r2);
    double s = m1 + m2;
    m1 /= s;
    m2 /= s;
    double D = m1 * r1 * r1 + m2 * r2 * r2;
    double Mm1 = m1 / r1 + m2 / r2;
    double M3 = m1 * r1 * r1 * r1 + m2 * r2 * r2 * r2;
    double V1 = m1 * g_kernel(r1, r1) + m2 * g_kernel(r1, r2);
    double V2 = m1 * g_kernel(r2, r1) + m2 * g_kernel(r2, r2);
    double I = m1 * V1 + m2 * V2;
    double Q = I / D;
    check(fabs(V1 - (D / 2.0 + Mm1 / 2.0)) < 1e-12, "V(1) identity");
    check(fabs(V2 - (r2 * r2 / 2.0 + M3 / (2.0 * r2))) < 1e-12, "V(R) identity");
    check(Q > 12.0 / 13.0, "this 2-atom sits above 12/13 (not a bound)");

    FILE *out = fopen("certs/aspect_c.txt", "w");
    if (!out) {
        fprintf(stderr, "FAIL: cannot write certs/aspect_c.txt\n");
        return 1;
    }
    fprintf(out, "empty_bad %d\n", empty_bad);
    fprintf(out, "nonempty_bad %d\n", nonempty_bad);
    fprintf(out, "two_atom_Q %.16e\n", Q);
    fprintf(out, "V1_err %.16e\n", fabs(V1 - (D / 2.0 + Mm1 / 2.0)));
    fprintf(out, "V2_err %.16e\n", fabs(V2 - (r2 * r2 / 2.0 + M3 / (2.0 * r2))));
    fprintf(out, "ok %d\n", fail ? 0 : 1);
    fclose(out);

    if (fail) {
        fprintf(stderr, "verify_aspect.c FAIL\n");
        return 1;
    }
    printf("verify_aspect.c PASS  two-atom Q=%.6f  cut=%.6f\n", Q, 12.0 / 13.0);
    return 0;
}
