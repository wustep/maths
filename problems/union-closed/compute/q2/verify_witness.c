/* Independent C replay of the constructed 2-mixture witness.

   Same numbers as witness_mixture.py, different language, explicit
   four-term expansion of each 2-atomic product.  Exit 0 iff the
   CIID Example-4 ratio is < 1 at mean 0.38304.

   gcc -O3 -std=c11 -o verify_witness verify_witness.c -lm
*/

#include <math.h>
#include <stdio.h>

#define LN2 0.693147180559945309417232121458176568
#define CLAIMED 0.38304
#define BSTAR 0.29649392356933757
#define MEAN0 0.45
#define ATOM1 0.01

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

static double h_or_ex4(double s, double t) {
    double sb = 1.0 - s;
    double tb = 1.0 - t;
    double aa = a_ex4(s) * a_ex4(t);
    double mn = sb < tb ? sb : tb;
    double pi0 = sb * tb + aa * (mn - sb * tb);
    return hbin(1.0 - pi0);
}

static double prod_ex4(const double *v, const double *w, int n) {
    double acc = 0.0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            acc += w[i] * w[j] * h_or_ex4(v[i], v[j]);
        }
    }
    return acc;
}

int main(void) {
    double a = (MEAN0 - BSTAR) / (1.0 - BSTAR);
    double v0[2] = {BSTAR, 1.0};
    double w0[2] = {1.0 - a, a};
    double v1[1] = {ATOM1};
    double w1[1] = {1.0};
    double m0 = w0[0] * v0[0] + w0[1] * v0[1];
    double m1 = ATOM1;
    double eh0 = w0[0] * hbin(v0[0]) + w0[1] * hbin(v0[1]);
    double eh1 = hbin(ATOM1);
    double e0 = prod_ex4(v0, w0, 2);
    double e1 = prod_ex4(v1, w1, 1);
    double q = (m0 - CLAIMED) / (m0 - m1);
    double mean = (1.0 - q) * m0 + q * m1;
    double eh = (1.0 - q) * eh0 + q * eh1;
    double eor = (1.0 - q) * e0 + q * e1;
    double ratio = eor / eh;
    int ok = (ratio < 1.0) && (fabs(mean - CLAIMED) < 1e-12);

    printf(
        "{\"mean\": %.16g, \"ratio\": %.16g, \"q\": %.16g, "
        "\"fails_pure_ex4\": %s, \"ok\": %s}\n",
        mean, ratio, q,
        (ratio < 1.0) ? "true" : "false",
        ok ? "true" : "false");
    return ok ? 0 : 1;
}
