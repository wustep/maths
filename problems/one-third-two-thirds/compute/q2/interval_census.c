/* Naturally labelled interval orders (2+2-free), exact δ.
 *
 * down-sets totally ordered by inclusion; identity is a linear extension.
 * Counts must match OEIS A367494 (n=0..): 1,1,2,7,37,272,2637,32469,493602,
 * 9062503, 197409097.
 *
 * gcc -O3 -o interval_census interval_census.c
 */
#include <stdio.h>
#include <stdlib.h>

#define MAXN 12
#include "delta_core.h"

static uint32_t g_down[MAXN];
static uint64_t n_all, n_nonchain, n_not_semi, n_below13;
static uint64_t n_not_semi_below13;
static uint64_t best_n, best_d, best_e;
static uint64_t best_ns_n, best_ns_d, best_ns_e;
static uint32_t best_down[MAXN], best_ns_down[MAXN];
static int have_best, have_ns;

static int ok_interval(int k, uint32_t mask) {
    uint32_t m = mask;
    while (m) {
        uint32_t b = m & -m;
        int j = lsb_i(b);
        if (g_down[j] & ~mask) return 0;
        m ^= b;
    }
    for (int i = 0; i < k; i++) {
        uint32_t prev = g_down[i];
        if ((mask & prev) != prev && (prev & mask) != mask) return 0;
    }
    return 1;
}

static void consider(void) {
    n_all++;
    memcpy(downv, g_down, sizeof(uint32_t) * (size_t)N);
    memset(succ, 0, sizeof(uint32_t) * (size_t)N);
    for (int j = 0; j < N; j++) {
        uint32_t d = downv[j];
        while (d) {
            uint32_t b = d & -d;
            succ[lsb_i(b)] |= 1u << j;
            d ^= b;
        }
    }
    uint32_t full = (1u << N) - 1;
    int n_inc = 0;
    for (int i = 0; i < N; i++) {
        compv[i] = downv[i] | succ[i];
        incomp[i] = full ^ compv[i] ^ (1u << i);
        n_inc += popcnt(incomp[i]);
    }
    if (n_inc == 0) return;
    n_nonchain++;
    Delta d = evaluate();
    int not_semi = contains_3plus1();
    if (not_semi) n_not_semi++;
    if (d.num * 3 < d.den) {
        n_below13++;
        if (not_semi) n_not_semi_below13++;
    }
    if (!have_best || d.num * best_d < best_n * d.den) {
        have_best = 1;
        best_n = d.num;
        best_d = d.den;
        best_e = d.e;
        memcpy(best_down, g_down, sizeof(uint32_t) * (size_t)N);
    }
    if (not_semi && (!have_ns || d.num * best_ns_d < best_ns_n * d.den)) {
        have_ns = 1;
        best_ns_n = d.num;
        best_ns_d = d.den;
        best_ns_e = d.e;
        memcpy(best_ns_down, g_down, sizeof(uint32_t) * (size_t)N);
    }
}

static void rec(int k) {
    if (k == N) {
        consider();
        return;
    }
    uint32_t full = (1u << k) - 1;
    for (uint32_t mask = 0; mask <= full; mask++) {
        if (!ok_interval(k, mask)) continue;
        g_down[k] = mask;
        rec(k + 1);
        g_down[k] = 0;
    }
}

static void print_down(const uint32_t *d) {
    for (int i = 0; i < N; i++) {
        if (i) putchar(',');
        printf("%u", d[i]);
    }
}

int main(int argc, char **argv) {
    int n0 = argc > 1 ? atoi(argv[1]) : 3;
    int n1 = argc > 2 ? atoi(argv[2]) : 10;
    if (n0 < 3 || n1 > MAXN || n0 > n1) {
        fprintf(stderr, "usage: interval_census n0 n1  (3..%d)\n", MAXN);
        return 1;
    }
    printf("n\tn_all\tn_nonchain\tn_not_semi\tmin\tmin_e\tmin_not_semi\t"
           "min_ns_e\tn_below_1_3\tmin_down\tmin_ns_down\n");
    for (N = n0; N <= n1; N++) {
        n_all = n_nonchain = n_not_semi = n_below13 = n_not_semi_below13 = 0;
        have_best = have_ns = 0;
        memset(g_down, 0, sizeof g_down);
        rec(0);
        printf("%d\t%llu\t%llu\t%llu\t%llu/%llu\t%llu\t", N,
               (unsigned long long)n_all, (unsigned long long)n_nonchain,
               (unsigned long long)n_not_semi, (unsigned long long)best_n,
               (unsigned long long)best_d, (unsigned long long)best_e);
        if (have_ns)
            printf("%llu/%llu\t%llu\t", (unsigned long long)best_ns_n,
                   (unsigned long long)best_ns_d,
                   (unsigned long long)best_ns_e);
        else
            printf("-\t-\t");
        printf("%llu\t", (unsigned long long)n_below13);
        print_down(best_down);
        putchar('\t');
        if (have_ns)
            print_down(best_ns_down);
        else
            printf("-");
        putchar('\n');
        fflush(stdout);
        fprintf(stderr, "n=%d done all=%llu below_1/3=%llu\n", N,
                (unsigned long long)n_all, (unsigned long long)n_below13);
        if (n_below13) {
            fprintf(stderr, "interval order below 1/3 at n=%d\n", N);
            return 2;
        }
    }
    return 0;
}
