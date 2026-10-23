/* Exact completion of a named midpoint cover, for odd primes below 128.
 * gcc -O3 -std=c11 -Wall -Wextra -Werror cover_search.c -o cover_search
 * Usage: cover_search P LIMIT NODES AP FORBID_AP [ROOT_MASK]
 *
 * Same completeness argument as q5: ordered counts are popcounts of
 * S intersect (s-S); a count of 1 or 2 forces another unordered pair.
 * Masks are 128-bit so primes 67, 71, 73, 79 fit. Repair options are
 * tried one-point first, and the exact cover test runs at remaining
 * <= 7. A cover-node cap may skip a prune (never an exclusion).
 * AP avoidance is affine invariant. Memo collisions evict; eviction
 * costs time, never completeness. Default storage: 128 MiB.
 */
#define _POSIX_C_SOURCE 200809L
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#ifndef COVER_MEMO_BITS
#define COVER_MEMO_BITS 23
#endif

typedef __uint128_t Mask;
typedef struct { int n, sum; Mask option[64]; } Constraint;
static int p, bound, forbidden_ap;
static Mask universe, pair[128][64], *image, *memo;
static uint64_t nodes, node_limit, memo_hits, cover_prunes, ap_prunes, support_prunes;
static int stopped;
static Mask witness;
static struct timespec t_start;
static double wall_limit;
#define BIT(i) ((Mask)1 << (i))
#define IMG(c, e, x) image[(((size_t)(c) * (size_t)p + (size_t)(e)) * (size_t)p + (size_t)(x))]
#define M128(hi, lo) (((Mask)(UINT64_C(hi)) << 64) | (Mask)(UINT64_C(lo)))

static int bits(Mask m) {
    return __builtin_popcountll((uint64_t)m) + __builtin_popcountll((uint64_t)(m >> 64));
}
static int ctz(Mask m) {
    uint64_t lo = (uint64_t)m;
    if (lo) return __builtin_ctzll(lo);
    return 64 + __builtin_ctzll((uint64_t)(m >> 64));
}
static Mask rotate(Mask m, int n) {
    return n ? ((m << n) | (m >> (p - n))) & universe : m;
}
static int out_of_time(void) {
    if (wall_limit <= 0) return 0;
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    double elapsed = (now.tv_sec - t_start.tv_sec) + (now.tv_nsec - t_start.tv_nsec) * 1e-9;
    return elapsed >= wall_limit;
}
static Mask negative(Mask x) {
    /* Reverse 128 bits, then rotate so bit i maps to (p-i) mod p. */
    x = ((x >> 1) & M128(0x5555555555555555, 0x5555555555555555))
      | ((x & M128(0x5555555555555555, 0x5555555555555555)) << 1);
    x = ((x >> 2) & M128(0x3333333333333333, 0x3333333333333333))
      | ((x & M128(0x3333333333333333, 0x3333333333333333)) << 2);
    x = ((x >> 4) & M128(0x0f0f0f0f0f0f0f0f, 0x0f0f0f0f0f0f0f0f))
      | ((x & M128(0x0f0f0f0f0f0f0f0f, 0x0f0f0f0f0f0f0f0f)) << 4);
    x = ((x >> 8) & M128(0x00ff00ff00ff00ff, 0x00ff00ff00ff00ff))
      | ((x & M128(0x00ff00ff00ff00ff, 0x00ff00ff00ff00ff)) << 8);
    x = ((x >> 16) & M128(0x0000ffff0000ffff, 0x0000ffff0000ffff))
      | ((x & M128(0x0000ffff0000ffff, 0x0000ffff0000ffff)) << 16);
    x = ((x >> 32) & M128(0x00000000ffffffff, 0x00000000ffffffff))
      | ((x & M128(0x00000000ffffffff, 0x00000000ffffffff)) << 32);
    x = (x >> 64) | (x << 64);
    return rotate(x >> (128 - p), 1);
}
static int has_ap(Mask mask, int length) {
    if (!length || bits(mask) < length) return 0;
    for (int d = 1; d <= (p - 1) / 2; ++d) {
        Mask starts = mask;
        for (int i = 1; i < length && starts; ++i)
            starts &= rotate(mask, i * d % p);
        if (starts) return 1;
    }
    return 0;
}
static Mask canonical(Mask mask) {
    int a[128], k = 0;
    for (Mask m = mask; m; m &= m - 1) a[k++] = ctz(m);
    Mask best = mask;
    for (int i = 0; i < k; ++i) for (int j = 0; j < k; ++j) {
        int c = a[i], e = a[j];
        if (c == e || !(mask & BIT((2 * c + p - e) % p))) continue;
        Mask mapped = 0;
        for (int t = 0; t < k; ++t) mapped |= IMG(c, e, a[t]);
        if (mapped < best) best = mapped;
    }
    return best;
}
static int seen(Mask key) {
    uint64_t h = (uint64_t)key ^ (uint64_t)(key >> 64);
    h ^= h >> 30; h *= UINT64_C(0xbf58476d1ce4e5b9);
    h ^= h >> 27; h *= UINT64_C(0x94d049bb133111eb);
    h ^= h >> 31;
    size_t i = h & ((1U << COVER_MEMO_BITS) - 1);
    if (memo[i] == key) return 1;
    memo[i] = key;
    return 0;
}
static uint64_t cover_nodes;
static int cover(const Constraint *c, int n, Mask chosen, int budget) {
    if (++cover_nodes > 200000) return 1;
    int best = -1, best_n = 65;
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
static void sort_options(Constraint *c) {
    for (int i = 1; i < c->n; ++i) {
        Mask x = c->option[i];
        int xb = bits(x), j = i;
        while (j) {
            Mask y = c->option[j - 1];
            int yb = bits(y);
            if (yb < xb || (yb == xb && y <= x)) break;
            c->option[j] = y;
            --j;
        }
        c->option[j] = x;
    }
}
static int search(Mask mask) {
    if (nodes == node_limit) { stopped = 1; return 0; }
    ++nodes;
    if ((nodes & 4095) == 0 && out_of_time()) { stopped = 1; return 0; }
    if ((nodes % 100000) == 0) {
        fprintf(stderr, "nodes=%" PRIu64 " memo_hits=%" PRIu64 " cover_prunes=%" PRIu64 "\n",
                nodes, memo_hits, cover_prunes);
        fflush(stderr);
    }
    int remaining = bound - bits(mask);
    if (remaining < 0) return 0;
    if (has_ap(mask, forbidden_ap)) { ++ap_prunes; return 0; }
    Constraint c[128];
    int n = 0, best = 0, support = 0;
    Mask reflected = negative(mask);
    for (int s = 0; s < p; ++s) {
        int count = bits(mask & rotate(reflected, s));
        support += count != 0;
        if (count != 1 && count != 2) continue;
        c[n].n = 0;
        c[n].sum = s;
        for (int j = 0; j < (p + 1) / 2; ++j) {
            Mask addition = pair[s][j] & ~mask;
            if (addition && bits(addition) <= remaining) {
                if (c[n].n >= 64) return 0;
                c[n].option[c[n].n++] = addition;
            }
        }
        if (!c[n].n) return 0;
        sort_options(&c[n]);
        int diagonal = (int)((mask >> ((s * ((p + 1) / 2)) % p)) & 1);
        int better = c[n].n < c[best].n;
        if (!better && c[n].n == c[best].n) {
            int best_diag = (int)((mask >> ((c[best].sum * ((p + 1) / 2)) % p)) & 1);
            better = diagonal && !best_diag;
        }
        if (better) best = n;
        ++n;
    }
    if (support > bound * (bound + 1) / 4) { ++support_prunes; return 0; }
    if (!n) { witness = mask; return 1; }
    cover_nodes = 0;
    if (remaining <= 7 && !cover(c, n, 0, remaining)) { ++cover_prunes; return 0; }
    if (seen(canonical(mask))) { ++memo_hits; return 0; }
    for (int j = 0; j < c[best].n; ++j) {
        if (search(mask | c[best].option[j])) return 1;
        if (stopped) return 0;
    }
    return 0;
}
static void print_hex(Mask m) {
    uint64_t hi = (uint64_t)(m >> 64);
    uint64_t lo = (uint64_t)m;
    if (hi) printf("0x%" PRIx64 "%016" PRIx64, hi, lo);
    else printf("0x%" PRIx64, lo);
}
static int parse_mask(const char *s, Mask *out) {
    if (s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) s += 2;
    if (!*s) return 0;
    Mask v = 0;
    int n = 0;
    for (; *s; ++s, ++n) {
        int d;
        if (*s >= '0' && *s <= '9') d = *s - '0';
        else if (*s >= 'a' && *s <= 'f') d = *s - 'a' + 10;
        else if (*s >= 'A' && *s <= 'F') d = *s - 'A' + 10;
        else return 0;
        if (n >= 32) return 0;
        v = (v << 4) | (Mask)d;
    }
    *out = v;
    return 1;
}
int main(int argc, char **argv) {
    if (argc != 6 && argc != 7) {
        fprintf(stderr, "usage: %s P LIMIT NODES AP FORBID_AP [ROOT_MASK]\n", argv[0]);
        return 2;
    }
    p = atoi(argv[1]); bound = atoi(argv[2]); node_limit = strtoull(argv[3], NULL, 10);
    int initial_ap = atoi(argv[4]); forbidden_ap = atoi(argv[5]);
    if (p < 3 || p >= 128 || p % 2 == 0 || bound < 2 || bound > p || !node_limit ||
        initial_ap < 3 || initial_ap > p || (forbidden_ap && (forbidden_ap < 3 || forbidden_ap > p)))
        return 2;
    for (int d = 2; d * d <= p; ++d) if (p % d == 0) return 2;
    struct rlimit cap = {1536UL * 1024 * 1024, 1536UL * 1024 * 1024};
    if (setrlimit(RLIMIT_AS, &cap)) return 2;
    universe = BIT(p) - 1;
    int sizes[128];
    memset(sizes, 0, sizeof sizes);
    for (int a = 0; a < p; ++a) for (int b = a; b < p; ++b) {
        int s = (a + b) % p;
        if (sizes[s] >= 64) return 2;
        pair[s][sizes[s]++] = BIT(a) | BIT(b);
    }
    image = calloc((size_t)p * (size_t)p * (size_t)p, sizeof(*image));
    if (!image) return 2;
    for (int c = 0; c < p; ++c) for (int e = 0; e < p; ++e) if (c != e) {
        int inverse = 1;
        while ((e + p - c) * inverse % p != 1) ++inverse;
        for (int x = 0; x < p; ++x)
            IMG(c, e, x) = BIT((x + p - c) * inverse % p);
    }
    memo = calloc(1U << COVER_MEMO_BITS, sizeof(*memo));
    if (!memo) { free(image); return 2; }
    char *limit_env = getenv("COVER_SECONDS");
    wall_limit = limit_env ? atof(limit_env) : 0;
    Mask root = 1;
    for (int i = 1; i < initial_ap; ++i)
        root |= BIT(i % 2 ? (i + 1) / 2 : p - i / 2);
    if (argc == 7 && !parse_mask(argv[6], &root)) { free(memo); free(image); return 2; }
    if ((root & ~universe) || !root) { free(memo); free(image); return 2; }
    struct timespec end;
    clock_gettime(CLOCK_MONOTONIC, &t_start);
    int found = search(root);
    clock_gettime(CLOCK_MONOTONIC, &end);
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    printf("{\"p\":%d,\"bound\":%d,\"initial_ap\":%d,\"forbid_ap\":%d,\"root_mask\":\"",
           p, bound, initial_ap, forbidden_ap);
    print_hex(root);
    printf("\",\"status\":\"%s\",\"node_limit\":%" PRIu64 ",\"nodes\":%" PRIu64 ",\"memo_hits\":%" PRIu64 ","
           "\"cover_prunes\":%" PRIu64 ",\"ap_prunes\":%" PRIu64 ",\"support_prunes\":%" PRIu64 ","
           "\"seconds\":%.6f,\"max_rss_kib\":%ld,\"witness\":[",
           found ? "SAT" : stopped ? "UNKNOWN" : "UNSAT",
           node_limit, nodes, memo_hits, cover_prunes, ap_prunes, support_prunes,
           end.tv_sec - t_start.tv_sec + (end.tv_nsec - t_start.tv_nsec) * 1e-9, usage.ru_maxrss);
    int first = 1;
    for (int x = 0; x < p; ++x) if (witness & BIT(x)) { printf("%s%d", first ? "" : ",", x); first = 0; }
    puts("]}");
    free(memo);
    free(image);
    return stopped ? 3 : 0;
}
