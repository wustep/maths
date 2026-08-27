/* Exhaustive non-sum three-rail minima.
 *
 * Rails x_i < x_{i+3} always. Optional rungs x_i < x_{i+4} and
 * x_i < x_{i+5}. Mask: low (n-4) bits break +4, next (n-5) break +5.
 *
 * gcc -O3 -o three_rail_census three_rail_census.c
 */
#include <stdio.h>
#include <stdlib.h>

#define MAXN 16
#include "delta_core.h"

static void build(uint32_t mask) {
    int n4 = N > 4 ? N - 4 : 0;
    int n5 = N > 5 ? N - 5 : 0;
    memset(succ, 0, sizeof(uint32_t) * (size_t)N);
    for (int i = 0; i < N - 3; i++) succ[i] |= 1u << (i + 3);
    for (int i = 0; i < n4; i++)
        if (((mask >> i) & 1u) == 0) succ[i] |= 1u << (i + 4);
    for (int i = 0; i < n5; i++)
        if (((mask >> (n4 + i)) & 1u) == 0) succ[i] |= 1u << (i + 5);
    close_and_down();
}

static void print_bits(uint32_t mask, int nbits) {
    int first = 1;
    for (int i = 0; i < nbits; i++)
        if ((mask >> i) & 1u) {
            if (!first) putchar(',');
            printf("%d", i);
            first = 0;
        }
    if (first) printf("-");
}

int main(int argc, char **argv) {
    int n0 = argc > 1 ? atoi(argv[1]) : 8;
    int n1 = argc > 2 ? atoi(argv[2]) : 15;
    if (n0 < 6 || n1 > MAXN || n0 > n1) {
        fprintf(stderr, "usage: three_rail_census n0 n1  (6..%d)\n", MAXN);
        return 1;
    }
    printf("n\tmin\tbroken4\tbroken5\te\tn_non_sum\tn_below_6_17\tn_below_1_3\n");
    for (N = n0; N <= n1; N++) {
        int n4 = N > 4 ? N - 4 : 0;
        int n5 = N > 5 ? N - 5 : 0;
        int nbits = n4 + n5;
        if (nbits > 31) {
            fprintf(stderr, "n=%d too many optional rungs\n", N);
            return 1;
        }
        uint32_t lim = 1u << nbits;
        uint64_t best_n = 1, best_d = 1, best_e = 0;
        uint32_t best_mask = 0;
        uint64_t n_seen = 0, n_below617 = 0, n_below13 = 0;
        for (uint32_t mask = 0; mask < lim; mask++) {
            build(mask);
            if (n_summands() != 1) continue;
            Delta d = evaluate();
            n_seen++;
            if (d.num * 17 < d.den * 6) n_below617++;
            if (d.num * 3 < d.den) n_below13++;
            if (n_seen == 1 || d.num * best_d < best_n * d.den) {
                best_n = d.num;
                best_d = d.den;
                best_e = d.e;
                best_mask = mask;
            }
            if ((mask & 0x3ffff) == 0)
                fprintf(stderr, "n=%d mask=%u/%u best=%llu/%llu\n", N, mask,
                        lim, (unsigned long long)best_n,
                        (unsigned long long)best_d);
        }
        printf("%d\t%llu/%llu\t", N, (unsigned long long)best_n,
               (unsigned long long)best_d);
        print_bits(best_mask & ((n4 ? (1u << n4) : 0) - 1u), n4);
        putchar('\t');
        print_bits(best_mask >> n4, n5);
        printf("\t%llu\t%llu\t%llu\t%llu\n", (unsigned long long)best_e,
               (unsigned long long)n_seen, (unsigned long long)n_below617,
               (unsigned long long)n_below13);
        fflush(stdout);
    }
    return 0;
}
