/* Independent C scan of f(b)=1-(1-b)h(b) on the saturation interval.

   Different language and a nested grid + golden-section refine, not
   mpmath findroot.  Exit 0 iff the numerical min sits in
   (0.38304, 0.38306) and strictly below 1/2.

   gcc -O3 -std=c11 -o verify_ceiling verify_ceiling.c -lm
*/

#include <math.h>
#include <stdio.h>

#define LN2 0.693147180559945309417232121458176568
#define CLAIMED_C 0.38304
#define NGRID 200000

static double hbin(double p) {
    if (p <= 0.0 || p >= 1.0) {
        return 0.0;
    }
    return -(p * log(p) + (1.0 - p) * log(1.0 - p)) / LN2;
}

static double f_of(double b) {
    return 1.0 - (1.0 - b) * hbin(b);
}

int main(void) {
    double thresh = 1.0 - 1.0 / sqrt(2.0);
    double lo = thresh + 1e-12;
    double hi = 0.5;
    double best_b = lo;
    double best_f = f_of(lo);

    for (int i = 0; i <= NGRID; i++) {
        double b = lo + (hi - lo) * (double)i / (double)NGRID;
        double fb = f_of(b);
        if (fb < best_f) {
            best_f = fb;
            best_b = b;
        }
    }

    /* golden-section refine around the grid min */
    double a = best_b - 4.0 * (hi - lo) / (double)NGRID;
    double c = best_b + 4.0 * (hi - lo) / (double)NGRID;
    if (a < lo) {
        a = lo;
    }
    if (c > hi) {
        c = hi;
    }
    const double phi = 0.5 * (3.0 - sqrt(5.0));
    double x1 = a + phi * (c - a);
    double x2 = c - phi * (c - a);
    double f1 = f_of(x1);
    double f2 = f_of(x2);
    for (int k = 0; k < 80; k++) {
        if (f1 < f2) {
            c = x2;
            x2 = x1;
            f2 = f1;
            x1 = a + phi * (c - a);
            f1 = f_of(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = c - phi * (c - a);
            f2 = f_of(x2);
        }
    }
    double mid = 0.5 * (a + c);
    double fmin = f_of(mid);
    double f_thresh = f_of(thresh);
    double f_half = f_of(0.5);
    int ok = (fmin > CLAIMED_C) && (fmin < 0.38306) && (fmin < 0.5)
             && (f_thresh > fmin) && (f_half > fmin);

    printf(
        "{\"b_star\": %.16g, \"ceiling\": %.16g, \"f_thresh\": %.16g, "
        "\"f_half\": %.16g, \"claimed_below\": %s, \"half_above\": %s, "
        "\"ok\": %s}\n",
        mid, fmin, f_thresh, f_half,
        (fmin > CLAIMED_C) ? "true" : "false",
        (0.5 > fmin) ? "true" : "false",
        ok ? "true" : "false");
    return ok ? 0 : 1;
}
