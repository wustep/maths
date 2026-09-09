/* Fixed-size witness search. No failed run implies a lower bound.
 * gcc -O3 -std=c11 -Wall -Wextra -Werror anneal.c -lm -o anneal
 * Usage: anneal PRIME SIZE RESTARTS STEPS SEED
 * Independent certification must recompute ordered representation counts.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static uint64_t state;
static uint64_t next(void) {
    state ^= state << 13; state ^= state >> 7; state ^= state << 17;
    return state;
}
static int below(int n) { return (int)(next() % (unsigned)n); }
static double uniform(void) { return (next() >> 11) * 0x1.0p-53; }
static int p, k, a[200], counts[200], present[200], unique, support;
static void change(int sum, int delta) {
    unique -= counts[sum] == 1; support -= counts[sum] != 0;
    counts[sum] += delta;
    unique += counts[sum] == 1; support += counts[sum] != 0;
}
static void swap_point(int index, int value) {
    int old = a[index];
    for (int j = 0; j < k; ++j) if (j != index) change((old + a[j]) % p, -1);
    change((old + old) % p, -1);
    present[old] = 0;
    a[index] = value; present[value] = 1;
    for (int j = 0; j < k; ++j) if (j != index) change((value + a[j]) % p, 1);
    change((value + value) % p, 1);
}
static int compare(const void *x, const void *y) { return *(const int*)x - *(const int*)y; }
static void print_set(int *values) {
    int sorted[200]; memcpy(sorted, values, (size_t)k * sizeof(int));
    qsort(sorted, (size_t)k, sizeof(int), compare);
    putchar('[');
    for (int j = 0; j < k; ++j) printf("%s%d", j ? "," : "", sorted[j]);
    putchar(']');
}
int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: %s PRIME SIZE RESTARTS STEPS SEED\n", argv[0]); return 2; }
    p = atoi(argv[1]); k = atoi(argv[2]);
    int restarts = atoi(argv[3]), steps = atoi(argv[4]);
    state = strtoull(argv[5], NULL, 10); uint64_t seed = state;
    if (p < 3 || p > 199 || k < 3 || k > p || restarts < 1 || steps < 1 || !state) return 2;
    for (int d = 2; d*d <= p; ++d) if (p % d == 0) return 2;
    if (k == p) { for (int i=0;i<k;++i) a[i]=i; printf("{\"status\":\"SAT\",\"p\":%d,\"cardinality\":%d,\"witness\":",p,k); print_set(a); puts("}"); return 0; }
    int best[200] = {0}, best_unique = p+1, best_support = p+1;
    uint64_t proposals = 0; clock_t started = clock();
    for (int restart = 0; restart < restarts; ++restart) {
        memset(present, 0, sizeof present); memset(counts, 0, sizeof counts);
        for (int i = 0; i < k; ++i) {
            int x;
            do { x = below(restart % 4 == 0 ? k + (p-k)/4 : p); } while (present[x]);
            a[i] = x; present[x] = 1;
        }
        unique = support = 0;
        for (int i = 0; i < k; ++i) for (int j = i; j < k; ++j) change((a[i]+a[j])%p,1);
        for (int step = 0; step <= steps; ++step) {
            if (unique < best_unique || (unique == best_unique && support < best_support)) {
                best_unique = unique; best_support = support; memcpy(best,a,(size_t)k*sizeof(int));
                fprintf(stderr,"best unique=%d support=%d restart=%d proposals=%llu\n",unique,support,restart,(unsigned long long)proposals);
            }
            if (unique == 0 || step == steps) break;
            int index = below(k), value;
            do { value = below(p); } while (present[value]);
            int old = a[index], old_unique = unique, old_support = support;
            swap_point(index,value); ++proposals;
            double delta = unique-old_unique + 0.025*(support-old_support);
            double temperature = 2.5 * exp(-5.5 * (double)step / steps);
            if (delta > 0 && uniform() >= exp(-delta/temperature)) swap_point(index,old);
        }
        if (unique == 0) break;
    }
    printf("{\"status\":\"%s\",\"p\":%d,\"cardinality\":%d,\"seed\":%llu,\"requested_restarts\":%d,\"steps_per_restart\":%d,\"proposals\":%llu,\"best_unique\":%d,\"sumset_size\":%d,\"cpu_seconds\":%.6f,\"witness\":",
           best_unique == 0 ? "SAT" : "UNKNOWN",p,k,(unsigned long long)seed,restarts,steps,(unsigned long long)proposals,best_unique,best_support,(double)(clock()-started)/CLOCKS_PER_SEC);
    print_set(best); puts("}");
    return best_unique == 0 ? 0 : 3;
}
