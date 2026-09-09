/* Neighborhood search around 14-set seeds. Failure is not a lower bound.
 * gcc -O3 -std=c11 -Wall -Wextra -Werror seed_search.c -o seed_search
 * Usage: seed_search PRIME SIZE SWAPS
 * Enumerates every swap-neighborhood of the hardcoded seeds (near-miss,
 * 14-subsets of both 15-sets). Reports SAT on a valid set, else UNKNOWN.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int p, k;
static uint64_t evaluated, best_unique = 1000, best_mask;
static int unique_count(uint64_t mask) {
    int present[64] = {0}, n = 0, a[64], unique = 0;
    for (int x = 0; x < p; ++x) if (mask & (UINT64_C(1) << x)) { present[x] = 1; a[n++] = x; }
    if (n != k) return 1000;
    for (int s = 0; s < p; ++s) {
        int count = 0;
        for (int i = 0; i < n; ++i) count += present[(s + p - a[i]) % p];
        unique += count == 1 || count == 2;
    }
    return unique;
}
static void consider(uint64_t mask) {
    ++evaluated;
    int u = unique_count(mask);
    if ((uint64_t)u < best_unique) { best_unique = (uint64_t)u; best_mask = mask; }
}
static void choose_from(uint64_t base, int *pool, int n, int need, int start, uint64_t chosen,
                        void (*use)(uint64_t)) {
    if (need == 0) { use(base | chosen); return; }
    for (int i = start; i <= n - need; ++i)
        choose_from(base, pool, n, need-1, i+1, chosen | (UINT64_C(1) << pool[i]), use);
}
static uint64_t current_base;
static int add_pool[64], add_n, add_need;
static void add_then_consider(uint64_t dropped) {
    choose_from(current_base & ~dropped, add_pool, add_n, add_need, 0, 0, consider);
}
static void neighborhood(uint64_t seed, int swaps) {
    int selected[64], nsel = 0, missing[64], nmiss = 0;
    for (int x = 0; x < p; ++x) {
        if (seed & (UINT64_C(1) << x)) selected[nsel++] = x;
        else missing[nmiss++] = x;
    }
    consider(seed);
    current_base = seed;
    add_n = nmiss;
    memcpy(add_pool, missing, (size_t)nmiss * sizeof(int));
    for (int width = 1; width <= swaps; ++width) {
        add_need = width;
        choose_from(0, selected, nsel, width, 0, 0, add_then_consider);
    }
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: %s PRIME SIZE SWAPS\n", argv[0]); return 2; }
    p = atoi(argv[1]); k = atoi(argv[2]); int swaps = atoi(argv[3]);
    if (p != 59 || k != 14 || swaps < 1 || swaps > 3) return 2;
    clock_t started = clock();
    int local15[] = {0,1,25,28,32,36,43,46,47,49,52,53,55,57,58};
    int oeis15[] = {0,1,2,3,4,5,9,10,16,25,27,32,42,44,48};
    int near14[] = {0,1,3,4,5,9,13,15,16,21,29,33,45,58};
    uint64_t seeds[64]; int nseed = 0;
    uint64_t near = 0; for (int i = 0; i < 14; ++i) near |= UINT64_C(1) << near14[i];
    seeds[nseed++] = near;
    uint64_t L = 0, O = 0;
    for (int i = 0; i < 15; ++i) { L |= UINT64_C(1) << local15[i]; O |= UINT64_C(1) << oeis15[i]; }
    for (int i = 0; i < 15; ++i) {
        seeds[nseed++] = L & ~(UINT64_C(1) << local15[i]);
        seeds[nseed++] = O & ~(UINT64_C(1) << oeis15[i]);
    }
    for (int i = 0; i < nseed && best_unique; ++i) neighborhood(seeds[i], swaps);
    printf("{\"status\":\"%s\",\"p\":59,\"cardinality\":14,\"swaps\":%d,\"seeds\":%d,"
           "\"evaluated\":%llu,\"best_unique\":%llu,\"cpu_seconds\":%.6f,\"witness\":[",
           best_unique == 0 ? "SAT" : "UNKNOWN", swaps, nseed,
           (unsigned long long)evaluated, (unsigned long long)best_unique,
           (double)(clock()-started)/CLOCKS_PER_SEC);
    int first = 1;
    for (int x = 0; x < p; ++x) if (best_mask & (UINT64_C(1) << x)) {
        printf("%s%d", first ? "" : ",", x); first = 0;
    }
    puts("]}");
    return best_unique == 0 ? 0 : 3;
}
