/* List every n in [2, X] with F(n) > n^alpha.
 *
 *   cc -O3 -std=c11 -o f_exceptions f_exceptions.c -lm
 *   ./f_exceptions 0.4 1000000
 *
 * Uses an LPF sieve and searches a in 1..n/2, short-interval first.
 * A finite exception list is residue, not a bound.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s alpha X\n", argv[0]);
        return 2;
    }
    const double alpha = atof(argv[1]);
    const uint32_t X = (uint32_t)strtoul(argv[2], NULL, 10);
    /* Optional exact rational: argv[3]=p argv[4]=q means test F^q > n^p. */
    const int use_rat = (argc >= 5);
    const int rp = use_rat ? atoi(argv[3]) : 0;
    const int rq = use_rat ? atoi(argv[4]) : 0;
    uint32_t *P = calloc((size_t)X + 1, sizeof(uint32_t));
    if (!P) {
        fprintf(stderr, "oom\n");
        return 1;
    }
    P[1] = 1;
    for (uint32_t i = 2; i <= X; i++) {
        if (P[i] == 0) {
            for (uint32_t j = i; j <= X; j += i) P[j] = i;
        }
    }

    uint32_t n_exc = 0;
    uint32_t first = 0, last = 0;
    printf("alpha=%.6f X=%u exact=%d p=%d q=%d\n", alpha, X, use_rat, rp, rq);
    printf("exceptions:");
    for (uint32_t n = 2; n <= X; n++) {
        double y = pow((double)n, alpha);
        uint32_t found = 0;
        uint32_t amax = n / 2;
        unsigned __int128 np = 1;
        if (use_rat) {
            for (int i = 0; i < rp; i++) np *= n;
        }
        for (uint32_t a = 1; a <= amax; a++) {
            uint32_t pa = P[a];
            uint32_t pb = P[n - a];
            uint32_t mx = pa > pb ? pa : pb;
            if (use_rat) {
                unsigned __int128 lhs = 1;
                for (int i = 0; i < rq; i++) lhs *= mx;
                if (lhs <= np) {
                    found = 1;
                    break;
                }
            } else if ((double)mx <= y) {
                found = 1;
                break;
            }
        }
        if (!found) {
            if (n_exc == 0) first = n;
            last = n;
            n_exc++;
            if (n_exc <= 80) printf(" %u", n);
        }
    }
    printf("\n");
    printf("n_exceptions=%u first=%u last=%u\n", n_exc, first, last);
    free(P);
    return 0;
}
