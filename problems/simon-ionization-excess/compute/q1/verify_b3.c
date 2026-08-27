/* Closed-form replay of HPS b(2), b(3) and published Nc envelopes.
 *
 * Not a new bound. Independent long-double evaluation of
 *   b(3) = (2/3) * cbrt(1+sqrt(2)) / ((1+sqrt(2))^{2/3} - 1)
 *   b(2) = (sqrt(2)+1)/2
 * from Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, (2.7)–(2.9).
 *
 * Also writes certs/bound_table.csv for integer Z = 1..200:
 *   Lieb            floor(2Z)     (Nc < 2Z+1 and Nc integer => Nc <= 2Z)
 *   Nam             1.22 Z + 3 Z^{1/3}
 *   HPS s=2 (Z>=2)  b(2) Z + 2.96 Z^{1/3}
 *   HPS s=3 (Z>=4)  Prop. 2.5 RHS
 *   HPS simplified  1.1185 Z + 4 Z^{1/3}   (Z>=4)
 *
 * Build: gcc -O2 -o verify_b3 verify_b3.c -lm
 */

#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#ifndef M_SQRT2l
#define M_SQRT2l 1.4142135623730950488016887242096981L
#endif

static void die(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg);
    exit(1);
}

static void ensure_certs(void) {
    if (mkdir("certs", 0755) != 0 && errno != EEXIST) {
        perror("mkdir certs");
        exit(1);
    }
}

static long double b2_closed(void) {
    return 0.5L * (sqrtl(2.0L) + 1.0L);
}

static long double b3_closed(void) {
    long double one_plus = 1.0L + sqrtl(2.0L);
    return (2.0L / 3.0L) * cbrtl(one_plus) / (powl(one_plus, 2.0L / 3.0L) - 1.0L);
}

static long double lieb_env(int z) {
    /* Nc < 2Z+1, Nc integer => Nc <= floor(2Z). For integer Z this is 2Z. */
    return floorl(2.0L * (long double)z);
}

static long double nam_env(int z) {
    long double zz = (long double)z;
    return 1.22L * zz + 3.0L * cbrtl(zz);
}

static long double hps_s2_env(int z, long double b2) {
    long double zz = (long double)z;
    return b2 * zz + 2.96L * cbrtl(zz);
}

static long double hps_s3_env(int z, long double b3) {
    /* HPS Prop. 2.5 / (2.9), stated for Z >= 4. */
    long double zz = (long double)z;
    long double z13 = cbrtl(zz);
    long double z_m13 = 1.0L / z13;
    long double z_m23 = z_m13 * z_m13;
    return b3 * zz + 3.90L * z13 + 0.0134L + 0.184L * z_m13 + 0.0196L * z_m23;
}

static long double hps_simp_env(int z) {
    long double zz = (long double)z;
    return 1.1185L * zz + 4.0L * cbrtl(zz);
}

int main(void) {
    long double b2 = b2_closed();
    long double b3 = b3_closed();

    printf("verify_b3.c  closed-form long double  (not a new bound)\n");
    printf("b2 = %.21Lf\n", b2);
    printf("b3 = %.21Lf\n", b3);

    if (!(b3 > 1.1184L && b3 < 1.1185L)) {
        fprintf(stderr, "b3 = %.21Lf is not in (1.1184, 1.1185)\n", b3);
        return 1;
    }
    if (!(b2 > 1.2071L && b2 < 1.2072L)) {
        fprintf(stderr, "b2 = %.21Lf is not in (1.2071, 1.2072)\n", b2);
        return 1;
    }
    printf("assert 1.1184 < b3 < 1.1185  PASS\n");
    printf("assert 1.2071 < b2 < 1.2072  PASS\n");

    ensure_certs();

    FILE *txt = fopen("certs/verify_b3.txt", "w");
    if (!txt) {
        die("cannot write certs/verify_b3.txt");
    }
    fprintf(txt, "verify_b3.c — closed-form HPS constants (long double)\n");
    fprintf(txt, "Not a new bound. Replay of arXiv:2504.18487v1 Prop. 2.4–2.5.\n\n");
    fprintf(txt, "b2 = %.21Lf\n", b2);
    fprintf(txt, "b3 = %.21Lf\n", b3);
    fprintf(txt, "assert 1.2071 < b2 < 1.2072 : PASS\n");
    fprintf(txt, "assert 1.1184 < b3 < 1.1185 : PASS\n\n");
    fprintf(txt, "b(s) = max_{0<=t<=1} (1 + t^{s-1}) / (1 + t^s)\n");
    fprintf(txt, "b(2) = (sqrt(2)+1)/2\n");
    fprintf(txt, "b(3) = (2/3) * cbrt(1+sqrt(2)) / ((1+sqrt(2))^{2/3} - 1)\n\n");
    fprintf(txt, "Wrote certs/bound_table.csv for integer Z=1..200.\n");
    fclose(txt);

    FILE *js = fopen("certs/b3_c.json", "w");
    if (!js) {
        die("cannot write certs/b3_c.json");
    }
    fprintf(js, "{\n");
    fprintf(js, "  \"algorithm\": \"closed-form long double\",\n");
    fprintf(js, "  \"b2\": \"%.21Lf\",\n", b2);
    fprintf(js, "  \"b3\": \"%.21Lf\"\n", b3);
    fprintf(js, "}\n");
    fclose(js);

    FILE *csv = fopen("certs/bound_table.csv", "w");
    if (!csv) {
        die("cannot write certs/bound_table.csv");
    }
    fprintf(csv, "Z,lieb,nam,hps_s2,hps_s3,hps_simplified,best_published,best_name\n");

    for (int z = 1; z <= 200; z++) {
        long double lieb = lieb_env(z);
        long double nam = nam_env(z);
        int have_s2 = z >= 2;
        int have_s3 = z >= 4;
        int have_simp = z >= 4;
        long double s2 = have_s2 ? hps_s2_env(z, b2) : 0.0L;
        long double s3 = have_s3 ? hps_s3_env(z, b3) : 0.0L;
        long double simp = have_simp ? hps_simp_env(z) : 0.0L;

        long double best = lieb;
        const char *name = "lieb";
        if (nam < best) {
            best = nam;
            name = "nam";
        }
        if (have_s2 && s2 < best) {
            best = s2;
            name = "hps_s2";
        }
        if (have_s3 && s3 < best) {
            best = s3;
            name = "hps_s3";
        }
        if (have_simp && simp < best) {
            best = simp;
            name = "hps_simplified";
        }

        fprintf(csv, "%d,%.18Lf,%.18Lf,", z, lieb, nam);
        if (have_s2) {
            fprintf(csv, "%.18Lf,", s2);
        } else {
            fprintf(csv, ",");
        }
        if (have_s3) {
            fprintf(csv, "%.18Lf,", s3);
        } else {
            fprintf(csv, ",");
        }
        if (have_simp) {
            fprintf(csv, "%.18Lf,", simp);
        } else {
            fprintf(csv, ",");
        }
        fprintf(csv, "%.18Lf,%s\n", best, name);
    }
    fclose(csv);

    printf("wrote certs/verify_b3.txt\n");
    printf("wrote certs/b3_c.json\n");
    printf("wrote certs/bound_table.csv\n");
    printf("verify_b3.c PASS\n");
    return 0;
}
