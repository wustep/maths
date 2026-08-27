/* Exhaustive non-sum broken-rung ladder minima. Same definition as
 * q1/ladders.py: rails i < i+2, rungs i < i+3 except the broken set.
 *
 * Stamp-based evaluate() — no 2^n memset — so n=22 (2^19 subsets) finishes.
 * gcc -O3 -o ladder_census ladder_census.c
 */
#include <stdio.h>
#include <stdlib.h>

#define MAXN 22
#include "delta_core.h"

static void build(uint32_t broken_mask) {
    memset(succ, 0, sizeof(uint32_t) * (size_t)N);
    for (int i = 0; i < N - 2; i++) succ[i] |= 1u << (i + 2);
    for (int i = 0; i < N - 3; i++)
        if (((broken_mask >> i) & 1u) == 0) succ[i] |= 1u << (i + 3);
    close_and_down();
}

static void print_broken(uint32_t mask, int nr) {
    int first = 1;
    for (int i = 0; i < nr; i++)
        if ((mask >> i) & 1u) {
            if (!first) putchar(',');
            printf("%d", i);
            first = 0;
        }
    if (first) printf("-");
}

int main(int argc, char **argv) {
    int n0 = argc > 1 ? atoi(argv[1]) : 22;
    int n1 = argc > 2 ? atoi(argv[2]) : n0;
    if (n0 < 3 || n1 > MAXN || n0 > n1) {
        fprintf(stderr, "usage: ladder_census n0 n1  (3..%d)\n", MAXN);
        return 1;
    }
    printf("n\tmin\tbroken\te\tn_non_sum\tn_below_1_3\n");
    for (N = n0; N <= n1; N++) {
        int nr = N - 3;
        if (nr < 0) nr = 0;
        if (nr > 31) {
            fprintf(stderr, "n=%d has more than 31 optional rungs\n", N);
            return 1;
        }
        uint32_t lim = 1u << nr;
        uint64_t best_n = 1, best_d = 1;
        uint64_t best_e = 0;
        uint32_t best_mask = 0;
        uint64_t n_seen = 0, n_below = 0;
        for (uint32_t mask = 0; mask < lim; mask++) {
            build(mask);
            if (n_summands() != 1) continue;
            Delta d = evaluate();
            n_seen++;
            if (d.num * 3 < d.den) n_below++;
            if (n_seen == 1 || d.num * best_d < best_n * d.den) {
                best_n = d.num;
                best_d = d.den;
                best_e = d.e;
                best_mask = mask;
            }
            if ((mask & 0xffff) == 0)
                fprintf(stderr, "n=%d mask=%u/%u best=%llu/%llu\n", N, mask,
                        lim, (unsigned long long)best_n,
                        (unsigned long long)best_d);
        }
        printf("%d\t%llu/%llu\t", N, (unsigned long long)best_n,
               (unsigned long long)best_d);
        print_broken(best_mask, nr);
        printf("\t%llu\t%llu\t%llu\n", (unsigned long long)best_e,
               (unsigned long long)n_seen, (unsigned long long)n_below);
        fflush(stdout);
    }
    return 0;
}
