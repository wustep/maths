/* Independent exhaustive C mesh for the q3 {b,1} claim.

   Unlike verify.py, this program visits every retained grid point.
   It exits 0 only when each point of mean <= 0.38305 has ratio > 1.

   gcc -O3 -std=c11 -o verify_c verify.c -lm
*/

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define CLAIMED_C 0.38305
#define NB 9000
#define NA 7000
#define B_LO 0.02
#define B_HI 0.499
#define A_LO 0.0
#define A_HI 0.499
#define MEAN_TOL 1e-15
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
    double threshold = 1.0 - 1.0 / sqrt(2.0);
    if (t <= threshold) {
        return 0.0;
    }
    double tb = 1.0 - t;
    double numerator = 1.0 - 2.0 * tb * tb;
    double denominator = 2.0 * t * tb;
    if (numerator <= 0.0 || denominator <= 0.0) {
        return 0.0;
    }
    return sqrt(numerator / denominator);
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
    int at_i = -1, at_j = -1;
    long long n_keep = 0;
    long long n_bad = 0;

    for (int i = 0; i < NB; i++) {
        double b = B_LO + (B_HI - B_LO) * (double)i / (double)(NB - 1);
        double hb = hbin(b);
        double hp = h_or_ex4(b);
        for (int j = 0; j < NA; j++) {
            double a = A_LO + (A_HI - A_LO) * (double)j / (double)(NA - 1);
            double mean = b + (1.0 - b) * a;
            if (mean > CLAIMED_C + MEAN_TOL) {
                break;
            }
            double eh = (1.0 - a) * hb;
            if (eh <= 1e-16) {
                continue;
            }
            double e_independent = (1.0 - a) * (1.0 - a) * hp;
            double e_correlated = (1.0 - a) * hp;
            double numerator = e_independent < e_correlated ? e_independent : e_correlated;
            double ratio = numerator / eh;
            n_keep++;
            if (ratio < min_ratio) {
                min_ratio = ratio;
                at_mean = mean;
                at_a = a;
                at_b = b;
                at_i = i;
                at_j = j;
            }
            if (ratio <= 1.0) {
                n_bad++;
            }
        }
    }

    char output[2048];
    int used = snprintf(
        output,
        sizeof(output),
        "{\n"
        "  \"implementation\": \"C exhaustive nested-loop mesh\",\n"
        "  \"claimed_c\": %.17g,\n"
        "  \"grid\": {\"n_b\": %d, \"n_a\": %d, \"b_lo\": %.17g, "
        "\"b_hi\": %.17g, \"a_lo\": %.17g, \"a_hi\": %.17g, "
        "\"total_cells\": %lld, \"retained_cells\": %lld, "
        "\"mean_tolerance\": %.17g},\n"
        "  \"min_ratio\": %.17g,\n"
        "  \"n_bad_cells\": %lld,\n"
        "  \"at\": {\"i_b\": %d, \"i_a\": %d, \"b\": %.17g, "
        "\"a\": %.17g, \"mean\": %.17g},\n"
        "  \"all_ok\": %s\n"
        "}\n",
        CLAIMED_C,
        NB,
        NA,
        B_LO,
        B_HI,
        A_LO,
        A_HI,
        (long long)NB * (long long)NA,
        n_keep,
        MEAN_TOL,
        min_ratio,
        n_bad,
        at_i,
        at_j,
        at_b,
        at_a,
        at_mean,
        (n_bad == 0 && min_ratio > 1.0 && n_keep > 0) ? "true" : "false"
    );
    if (used < 0 || (size_t)used >= sizeof(output)) {
        return 2;
    }

    FILE *certificate = fopen("certs/c_mesh.json", "w");
    if (certificate == NULL) {
        perror("certs/c_mesh.json");
        return 2;
    }
    fputs(output, certificate);
    fclose(certificate);
    fputs(output, stdout);

    if (n_bad != 0 || min_ratio <= 1.0 || n_keep == 0) {
        return 1;
    }
    return 0;
}
