/* Exact completion of a named midpoint cover, for odd primes below 64.
 * gcc -O3 -std=c11 -Wall -Wextra -Werror cover_search.c -o cover_search
 * Usage: cover_search P LIMIT NODES AP FORBID_AP [ROOT_MASK]
 * The default root is the first AP entries of 0,1,-1,2,-2,... .
 * FORBID_AP=0 imposes no restriction. Otherwise all such progressions are
 * forbidden; this is conditional evidence, not an unrestricted exclusion.
 * ROOT_MASK overrides the root, and is a named case (never WLOG by itself).
 *
 * Ordered counts are popcounts of S intersect (s-S). A count of 1 or 2
 * forces a second unordered pair. At <=6 free places we test whether one
 * union of repair pairs can cover every currently unique sum. This test
 * ignores new sums: failure prunes, success merely permits further search.
 * All branches strictly add vertices. A fixed cache stores full affine
 * canonical masks; collisions only evict entries. AP avoidance is affine
 * invariant. Memoization concerns existence of ANY admissible superset of a
 * state, so the fixed root need not be preserved by the canonical map.
 */
#define _POSIX_C_SOURCE 200809L
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <time.h>

typedef uint64_t Mask;
typedef struct { int n; Mask option[32]; } Constraint;
static int p, bound, forbidden_ap;
static Mask universe, pair[64][32], image[64][64][64], *memo;
static uint64_t nodes, node_limit, memo_hits, cover_prunes, ap_prunes, support_prunes;
static int stopped;
static Mask witness;
static int bits(Mask m) { return __builtin_popcountll(m); }
static Mask rotate(Mask m, int n) {
    return n ? ((m << n) | (m >> (p-n))) & universe : m;
}
static Mask negative(Mask x) {
    x = ((x >> 1) & UINT64_C(0x5555555555555555)) | ((x & UINT64_C(0x5555555555555555)) << 1);
    x = ((x >> 2) & UINT64_C(0x3333333333333333)) | ((x & UINT64_C(0x3333333333333333)) << 2);
    x = ((x >> 4) & UINT64_C(0x0f0f0f0f0f0f0f0f)) | ((x & UINT64_C(0x0f0f0f0f0f0f0f0f)) << 4);
    x = ((x >> 8) & UINT64_C(0x00ff00ff00ff00ff)) | ((x & UINT64_C(0x00ff00ff00ff00ff)) << 8);
    x = ((x >> 16) & UINT64_C(0x0000ffff0000ffff)) | ((x & UINT64_C(0x0000ffff0000ffff)) << 16);
    x = (x >> 32) | (x << 32);
    return rotate(x >> (64-p), 1);
}
static int has_ap(Mask mask, int length) {
    if (!length || bits(mask) < length) return 0;
    for (int d = 1; d <= (p-1)/2; ++d) {
        Mask starts = mask;
        for (int i = 1; i < length && starts; ++i)
            starts &= rotate(mask, i*d % p);
        if (starts) return 1;
    }
    return 0;
}
static Mask canonical(Mask mask) {
    int a[64], k = 0;
    for (Mask m = mask; m; m &= m-1) a[k++] = __builtin_ctzll(m);
    Mask best = mask;
    for (int i = 0; i < k; ++i) for (int j = 0; j < k; ++j) {
        int c = a[i], e = a[j];
        if (c == e || !(mask & (UINT64_C(1) << ((2*c+p-e)%p)))) continue;
        Mask mapped = 0;
        for (int t = 0; t < k; ++t) mapped |= image[c][e][a[t]];
        if (mapped < best) best = mapped;
    }
    return best;
}
static int seen(Mask key) {
    Mask h = key;
    h ^= h >> 30; h *= UINT64_C(0xbf58476d1ce4e5b9);
    h ^= h >> 27; h *= UINT64_C(0x94d049bb133111eb);
    h ^= h >> 31;
    size_t i = h & ((1U << 24)-1);
    if (memo[i] == key) return 1;
    memo[i] = key;
    return 0;
}
static int cover(const Constraint *c, int n, Mask chosen, int budget) {
    int best = -1, best_n = 33;
    for (int i = 0; i < n; ++i) {
        int satisfied = 0, count = 0;
        for (int j = 0; j < c[i].n; ++j) {
            Mask extra = c[i].option[j] & ~chosen;
            if (!extra) { satisfied = 1; break; }
            count += bits(chosen | extra) <= budget;
        }
        if (satisfied) continue;
        if (!count) return 0;
        if (count < best_n) { best = i; best_n = count; }
    }
    if (best < 0) return 1;
    for (int j = 0; j < c[best].n; ++j) {
        Mask next = chosen | c[best].option[j];
        if (bits(next) <= budget && cover(c, n, next, budget)) return 1;
    }
    return 0;
}
static int search(Mask mask) {
    if (nodes == node_limit) { stopped = 1; return 0; }
    ++nodes;
    int remaining = bound - bits(mask);
    if (remaining < 0) return 0;
    if (has_ap(mask, forbidden_ap)) { ++ap_prunes; return 0; }
    Constraint c[64];
    int n = 0, best = 0, support = 0;
    Mask reflected = negative(mask);
    for (int s = 0; s < p; ++s) {
        int count = bits(mask & rotate(reflected, s));
        support += count != 0;
        if (count != 1 && count != 2) continue;
        c[n].n = 0;
        /* Pairs for one sum partition the residues. Their nonempty missing
         * endpoint sets are disjoint, so no duplicate/superset removal is needed. */
        for (int j = 0; j < (p+1)/2; ++j) {
            Mask addition = pair[s][j] & ~mask;
            if (addition && bits(addition) <= remaining) c[n].option[c[n].n++] = addition;
        }
        if (!c[n].n) return 0;
        if (c[n].n < c[best].n) best = n;
        ++n;
    }
    if (support > bound*(bound+1)/4) { ++support_prunes; return 0; }
    if (!n) { witness = mask; return 1; }
    if (remaining <= 6 && !cover(c, n, 0, remaining)) { ++cover_prunes; return 0; }
    if (seen(canonical(mask))) { ++memo_hits; return 0; }
    for (int j = 0; j < c[best].n; ++j) {
        if (search(mask | c[best].option[j])) return 1;
        if (stopped) return 0;
    }
    return 0;
}
int main(int argc, char **argv) {
    if (argc != 6 && argc != 7) {
        fprintf(stderr, "usage: %s P LIMIT NODES AP FORBID_AP [ROOT_MASK]\n", argv[0]); return 2;
    }
    p = atoi(argv[1]); bound = atoi(argv[2]); node_limit = strtoull(argv[3], NULL, 10);
    int initial_ap = atoi(argv[4]); forbidden_ap = atoi(argv[5]);
    if (p < 3 || p >= 64 || p%2 == 0 || bound < 2 || bound > p || !node_limit ||
        initial_ap < 3 || initial_ap > p || (forbidden_ap && (forbidden_ap < 3 || forbidden_ap > p))) return 2;
    for (int d = 2; d*d <= p; ++d) if (p%d == 0) return 2;
    struct rlimit cap = {1536UL*1024*1024, 1536UL*1024*1024};
    if (setrlimit(RLIMIT_AS, &cap)) return 2;
    universe = (UINT64_C(1) << p)-1;
    int sizes[64] = {0};
    for (int a = 0; a < p; ++a) for (int b = a; b < p; ++b) {
        int s = (a+b)%p;
        pair[s][sizes[s]++] = (UINT64_C(1) << a) | (UINT64_C(1) << b);
    }
    for (int c = 0; c < p; ++c) for (int e = 0; e < p; ++e) if (c != e) {
        int inverse = 1;
        while ((e+p-c)*inverse % p != 1) ++inverse;
        for (int x = 0; x < p; ++x)
            image[c][e][x] = UINT64_C(1) << ((x+p-c)*inverse % p);
    }
    memo = calloc(1U << 24, sizeof(*memo));
    if (!memo) return 2;
    Mask root = 1;
    for (int i = 1; i < initial_ap; ++i)
        root |= UINT64_C(1) << (i%2 ? (i+1)/2 : p-i/2);
    if (argc == 7) root = strtoull(argv[6], NULL, 0);
    if ((root & ~universe) || !root) { free(memo); return 2; }
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    int found = search(root);
    clock_gettime(CLOCK_MONOTONIC, &end);
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    printf("{\"p\":%d,\"bound\":%d,\"initial_ap\":%d,\"forbid_ap\":%d,\"root_mask\":\"0x%" PRIx64 "\","
           "\"status\":\"%s\",\"node_limit\":%" PRIu64 ",\"nodes\":%" PRIu64 ",\"memo_hits\":%" PRIu64 ","
           "\"cover_prunes\":%" PRIu64 ",\"ap_prunes\":%" PRIu64 ",\"support_prunes\":%" PRIu64 ","
           "\"seconds\":%.6f,\"max_rss_kib\":%ld,\"witness\":[",
           p, bound, initial_ap, forbidden_ap, root, found ? "SAT" : stopped ? "UNKNOWN" : "UNSAT",
           node_limit, nodes, memo_hits, cover_prunes, ap_prunes, support_prunes,
           end.tv_sec-start.tv_sec + (end.tv_nsec-start.tv_nsec)*1e-9, usage.ru_maxrss);
    int first = 1;
    for (int x = 0; x < p; ++x) if (witness & (UINT64_C(1) << x)) { printf("%s%d", first ? "" : ",", x); first = 0; }
    puts("]}");
    free(memo);
    return stopped ? 3 : 0;
}
