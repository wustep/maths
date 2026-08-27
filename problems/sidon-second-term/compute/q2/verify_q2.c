/* Exact Hou–Zhao Lemma 2.1 check via GMP. Symmetric certificates only.
 *
 * Input (from dump_cert.py):
 *   R m L
 *   then R mixing weights as num den
 *   then R*m kernel entries as num den
 *   then R*(L*m) boundary weights as num den
 *
 * Covering is a nested (q,i) sum. This file does not read JSON and does
 * not share code with the Python verifiers.
 *
 *   gcc -O2 -o verify_q2 verify_q2.c -lgmp
 *   ./verify_q2 certs/FILE.txt 94325 100000
 */
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

static void die(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg);
    exit(1);
}

static void read_mpq(FILE *f, mpq_t x) {
    mpz_t num, den;
    mpz_inits(num, den, NULL);
    if (gmp_fscanf(f, "%Zd %Zd", num, den) != 2) {
        die("parse fraction");
    }
    mpq_set_num(x, num);
    mpq_set_den(x, den);
    mpq_canonicalize(x);
    mpz_clears(num, den, NULL);
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: %s dump.txt beat_num beat_den\n", argv[0]);
        return 2;
    }
    FILE *in = fopen(argv[1], "r");
    if (!in) {
        die("open dump");
    }
    int R, m, L;
    if (fscanf(in, "%d %d %d", &R, &m, &L) != 3) {
        die("header");
    }
    if (R <= 0 || m <= 0 || L <= 0 || R > 64 || m > 512 || L > 32) {
        die("bounds");
    }
    int n = L * m;
    mpq_t *lam = calloc((size_t)R, sizeof(mpq_t));
    mpq_t *p = calloc((size_t)R * (size_t)m, sizeof(mpq_t));
    mpq_t *w = calloc((size_t)R * (size_t)n, sizeof(mpq_t));
    if (!lam || !p || !w) {
        die("alloc");
    }
    for (int r = 0; r < R; r++) {
        mpq_init(lam[r]);
        read_mpq(in, lam[r]);
        if (mpq_sgn(lam[r]) < 0) {
            die("negative mix");
        }
    }
    mpq_t mixsum;
    mpq_init(mixsum);
    for (int r = 0; r < R; r++) {
        mpq_add(mixsum, mixsum, lam[r]);
    }
    if (mpq_cmp_ui(mixsum, 1, 1) != 0) {
        die("mix not 1");
    }
    for (int r = 0; r < R; r++) {
        mpq_t psum;
        mpq_init(psum);
        for (int i = 0; i < m; i++) {
            mpq_init(p[r * m + i]);
            read_mpq(in, p[r * m + i]);
            if (mpq_sgn(p[r * m + i]) < 0) {
                die("negative kernel");
            }
            mpq_add(psum, psum, p[r * m + i]);
        }
        if (mpq_cmp_ui(psum, 1, 1) != 0) {
            die("kernel mass");
        }
        for (int i = 0; i < m; i++) {
            if (mpq_cmp(p[r * m + i], p[r * m + (m - 1 - i)]) != 0) {
                die("kernel not symmetric");
            }
        }
        mpq_clear(psum);
    }
    for (int r = 0; r < R; r++) {
        for (int j = 0; j < n; j++) {
            mpq_init(w[r * n + j]);
            read_mpq(in, w[r * n + j]);
        }
    }

    mpq_t one, acc, term, pi, wj, slackmin;
    mpq_inits(one, acc, term, pi, wj, slackmin, NULL);
    mpq_set_ui(one, 1, 1);
    mpq_set_ui(slackmin, 1, 1);
    for (int q = 0; q <= n; q++) {
        mpq_set_ui(acc, 0, 1);
        for (int r = 0; r < R; r++) {
            for (int i = 0; i < m; i++) {
                int j = q + i;
                mpq_set(pi, p[r * m + i]);
                if (j < n) {
                    mpq_set(wj, w[r * n + j]);
                } else {
                    mpq_set_ui(wj, 1, 1);
                }
                mpq_mul(term, lam[r], pi);
                mpq_mul(term, term, wj);
                mpq_add(acc, acc, term);
            }
        }
        mpq_sub(acc, acc, one);
        if (mpq_sgn(acc) < 0) {
            die("covering");
        }
        if (mpq_cmp(acc, slackmin) < 0) {
            mpq_set(slackmin, acc);
        }
    }

    mpq_t a, b, energy, tmp;
    mpq_inits(a, b, energy, tmp, NULL);
    mpq_set_ui(a, 0, 1);
    mpq_set_ui(energy, 0, 1);
    for (int r = 0; r < R; r++) {
        mpq_set_ui(acc, 0, 1);
        for (int i = 0; i < m; i++) {
            mpq_mul(term, p[r * m + i], p[r * m + i]);
            mpq_add(acc, acc, term);
        }
        mpq_mul(acc, acc, lam[r]);
        mpq_add(a, a, acc);
        mpq_set_ui(acc, 0, 1);
        for (int j = 0; j < n; j++) {
            mpq_mul(term, w[r * n + j], w[r * n + j]);
            mpq_add(acc, acc, term);
        }
        mpq_mul(acc, acc, lam[r]);
        mpq_add(energy, energy, acc);
    }
    mpq_set_ui(tmp, (unsigned long)m, 1);
    mpq_mul(a, a, tmp);
    mpq_div(energy, energy, tmp);
    mpq_set_ui(tmp, (unsigned long)L, 1);
    mpq_sub(energy, energy, tmp);
    mpq_add(energy, energy, energy);
    mpq_add(b, energy, one);
    if (mpq_sgn(b) <= 0) {
        die("b not positive");
    }
    mpq_t ab, target, t2;
    mpq_inits(ab, target, t2, NULL);
    mpq_mul(ab, a, b);
    mpq_set_ui(target, (unsigned long)strtoul(argv[2], NULL, 10),
               (unsigned long)strtoul(argv[3], NULL, 10));
    mpq_canonicalize(target);
    mpq_mul(t2, target, target);
    if (mpq_cmp(ab, t2) >= 0) {
        die("did not beat target");
    }

    gmp_printf("dump %s\n", argv[1]);
    gmp_printf("R %d m %d L %d\n", R, m, L);
    gmp_printf("min_slack %Qd\n", slackmin);
    gmp_printf("a %Qd\n", a);
    gmp_printf("b %Qd\n", b);
    gmp_printf("ab %Qd\n", ab);
    gmp_printf("beats %Qd YES\n", target);
    printf("PASS\n");
    return 0;
}
