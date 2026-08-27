/* Independent C mesh of the {b,1} ray for pure Example 4.

   Algorithm is the same 2-D sample as verify.py (linspace, independent
   C3), but a different language and a nested loop rather than a numpy
   broadcast.  Exit 0 iff every cell with mean <= CLAIMED_C has
   Gilmer ratio >= 1.

   gcc -O3 -std=c11 -o verify_c verify.c -lm
*/

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define CLAIMED_C 0.38304
#define NB 4500
#define NA 3500
#define B_LO 0.02
#define B_HI 0.499
#define A_LO 0.0
#define A_HI 0.499
#define LN2 0.693147180559945309417232121458176568

static double hbin(double p) {
    if (p <= 0.0 || p >= 1.0) {
        return 0.0;
    }
    return -(p * log(p) + (1.0 - p) * log(1.0 - p)) / LN2;
}

static double a_ex4(double t) {
    if (t >= 0.5) {
        return 1.0;
    }
    double thresh = 1.0 - 1.0 / sqrt(2.0);
    if (t <= thresh) {
        return 0.0;
    }
    double tb = 1.0 - t;
    double num = 1.0 - 2.0 * tb * tb;
    double den = 2.0 * t * tb;
    if (num <= 0.0 || den <= 0.0) {
        return 0.0;
    }
    return sqrt(num / den);
}

static double h_or_ex4(double b) {
    double bb = 1.0 - b;
    double aa = a_ex4(b);
    double pi0 = bb * bb + aa * aa * (bb - bb * bb);
    return hbin(1.0 - pi0);
}

int main(void) {
    double min_ratio = 1e300;
    double at_mean = 0.0, at_a = 0.0, at_b = 0.0;
    long n_keep = 0;
    long n_bad = 0;

    for (int i = 0; i < NB; i++) {
        double b = B_LO + (B_HI - B_LO) * (double)i / (double)(NB - 1);
        double hb = hbin(b);
        double hp = h_or_ex4(b);
        for (int j = 0; j < NA; j++) {
            double a = A_LO + (A_HI - A_LO) * (double)j / (double)(NA - 1);
            double mean = a + (1.0 - a) * b;
            if (mean > CLAIMED_C) {
                continue;
            }
            double eh = (1.0 - a) * hb;
            if (eh <= 1e-16) {
                continue;
            }
            double e_ind = (1.0 - a) * (1.0 - a) * hp;
            double e_cor = (1.0 - a) * hp;
            double ep = e_ind < e_cor ? e_ind : e_cor;
            double ratio = ep / eh;
            n_keep++;
            if (ratio < min_ratio) {
                min_ratio = ratio;
                at_mean = mean;
                at_a = a;
                at_b = b;
            }
            if (ratio < 1.0) {
                n_bad++;
            }
        }
    }

    printf("{\"min_ratio\": %.16f, \"n\": %ld, \"n_bad\": %ld, "
           "\"at_mean\": %.16f, \"at_a\": %.16f, \"at_b\": %.16f}\n",
           min_ratio, n_keep, n_bad, at_mean, at_a, at_b);
    if (n_bad != 0 || min_ratio < 1.0 || n_keep == 0) {
        return 1;
    }
    return 0;
}
