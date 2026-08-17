/* Exhaustive labeled census of Pisa graphs (strong + Delta == 0).

   Pair {i,j} has 3 states: i->j, j->i, missing.  n <= 12, bitmasks in uint32.
   Reports: total oriented, strong, Delta>=0, Pisa, and missing-degree-type counts.

   Compile: gcc -O3 -march=native -fopenmp -o enum_pisa enum_pisa.c
   Usage:   ./enum_pisa n
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n;
static int npairs;
static int pair_u[64], pair_v[64];

static inline int popcnt(uint32_t x) { return __builtin_popcount(x); }

static int is_strong(const uint32_t *out) {
    uint32_t inn[12] = {0};
    uint32_t full = (1u << n) - 1u;
    for (int v = 0; v < n; v++) {
        uint32_t m = out[v];
        while (m) {
            int w = __builtin_ctz(m);
            inn[w] |= 1u << v;
            m &= m - 1;
        }
    }
    /* out-reach from 0 */
    uint32_t seen = 1u;
    uint32_t frontier = 1u;
    while (frontier) {
        uint32_t nxt = 0;
        uint32_t f = frontier;
        while (f) {
            int v = __builtin_ctz(f);
            nxt |= out[v];
            f &= f - 1;
        }
        nxt &= ~seen;
        seen |= nxt;
        frontier = nxt;
    }
    if (seen != full) return 0;
    /* in-reach from 0 (= out-reach in reverse) */
    seen = 1u;
    frontier = 1u;
    while (frontier) {
        uint32_t nxt = 0;
        uint32_t f = frontier;
        while (f) {
            int v = __builtin_ctz(f);
            nxt |= inn[v];
            f &= f - 1;
        }
        nxt &= ~seen;
        seen |= nxt;
        frontier = nxt;
    }
    return seen == full;
}

static int delta_of(const uint32_t *out) {
    int dlt = -n;
    for (int v = 0; v < n; v++) {
        uint32_t first = out[v];
        uint32_t second = 0;
        uint32_t m = first;
        while (m) {
            int u = __builtin_ctz(m);
            second |= out[u];
            m &= m - 1;
        }
        second &= ~first;
        second &= ~(1u << v);
        int marg = popcnt(second) - popcnt(first);
        if (marg > dlt) dlt = marg;
    }
    return dlt;
}

static void missing_deg(const uint32_t *out, int *deg) {
    uint32_t full = (1u << n) - 1u;
    for (int v = 0; v < n; v++) {
        uint32_t present = out[v];
        for (int w = 0; w < n; w++) {
            if ((out[w] >> v) & 1u) present |= 1u << w;
        }
        deg[v] = popcnt(full ^ (1u << v) ^ present);
    }
}

/* Pack a nonincreasing missing-degree sequence into a 32-bit key (4 bits each). */
static uint32_t miss_key(const uint32_t *out) {
    int deg[12];
    missing_deg(out, deg);
    /* insertion sort descending */
    for (int i = 1; i < n; i++) {
        int x = deg[i], j = i;
        while (j > 0 && deg[j - 1] < x) {
            deg[j] = deg[j - 1];
            j--;
        }
        deg[j] = x;
    }
    uint32_t key = 0;
    for (int i = 0; i < n; i++) key = (key << 4) | (uint32_t)deg[i];
    return key;
}

typedef struct {
    uint32_t key;
    uint64_t count;
} KeyCount;

#define MAXKEYS 256

static void add_key(KeyCount *tab, int *ntab, uint32_t key) {
    for (int i = 0; i < *ntab; i++) {
        if (tab[i].key == key) {
            tab[i].count++;
            return;
        }
    }
    if (*ntab >= MAXKEYS) {
        fprintf(stderr, "too many missing-degree types\n");
        exit(1);
    }
    tab[*ntab].key = key;
    tab[*ntab].count = 1;
    (*ntab)++;
}

static void merge_keys(KeyCount *dst, int *ndst, const KeyCount *src, int nsrc) {
    for (int i = 0; i < nsrc; i++) {
        int found = 0;
        for (int j = 0; j < *ndst; j++) {
            if (dst[j].key == src[i].key) {
                dst[j].count += src[i].count;
                found = 1;
                break;
            }
        }
        if (!found) {
            if (*ndst >= MAXKEYS) {
                fprintf(stderr, "too many missing-degree types\n");
                exit(1);
            }
            dst[*ndst] = src[i];
            (*ndst)++;
        }
    }
}

static void print_key(uint32_t key) {
    int deg[12];
    for (int i = n - 1; i >= 0; i--) {
        deg[i] = key & 0xF;
        key >>= 4;
    }
    printf("[");
    for (int i = 0; i < n; i++) {
        if (i) printf(",");
        printf("%d", deg[i]);
    }
    printf("]");
}

/* Write a compact JSON census for n=4 and n=5 as well when run as
   `enum_pisa n`.  (n=6,7 are the Halkiewicz numbers we replay.) */

int main(int argc, char **argv) {
    n = (argc >= 2) ? atoi(argv[1]) : 6;
    if (n < 1 || n > 12) {
        fprintf(stderr, "n in 1..12\n");
        return 1;
    }
    npairs = n * (n - 1) / 2;
    int p = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            pair_u[p] = i;
            pair_v[p] = j;
            p++;
        }

    uint64_t total = 1;
    for (int i = 0; i < npairs; i++) total *= 3ull;
    fprintf(stderr, "n=%d pairs=%d labeled=%llu\n", n, npairs,
            (unsigned long long)total);

    uint64_t n_oriented = total; /* every ternary string is an oriented graph */
    uint64_t n_strong = 0, n_dlt_ge0 = 0, n_pisa = 0, n_tight = 0;
    KeyCount keys[MAXKEYS];
    int nkeys = 0;

#ifdef _OPENMP
#pragma omp parallel
#endif
    {
        uint64_t s_strong = 0, s_dlt = 0, s_pisa = 0, s_tight = 0;
        KeyCount lkeys[MAXKEYS];
        int lnkeys = 0;
        uint32_t out[12];

#ifdef _OPENMP
#pragma omp for schedule(static)
#endif
        for (int64_t code = 0; code < (int64_t)total; code++) {
            memset(out, 0, sizeof(uint32_t) * (size_t)n);
            int64_t c = code;
            for (int k = 0; k < npairs; k++) {
                int d = (int)(c % 3);
                c /= 3;
                int u = pair_u[k], v = pair_v[k];
                if (d == 0) out[u] |= 1u << v;
                else if (d == 1) out[v] |= 1u << u;
            }
            int dlt = delta_of(out);
            if (dlt >= 0) s_dlt++;
            int strong = is_strong(out);
            if (strong) s_strong++;
            if (strong && dlt == 0) {
                s_pisa++;
                /* tight: every margin 0.  Since max=0, check none negative. */
                int tight = 1;
                for (int v = 0; v < n; v++) {
                    uint32_t first = out[v];
                    uint32_t second = 0;
                    uint32_t m = first;
                    while (m) {
                        int u = __builtin_ctz(m);
                        second |= out[u];
                        m &= m - 1;
                    }
                    second &= ~first;
                    second &= ~(1u << v);
                    if (popcnt(second) != popcnt(first)) {
                        tight = 0;
                        break;
                    }
                }
                if (tight) s_tight++;
                add_key(lkeys, &lnkeys, miss_key(out));
            }
        }

#ifdef _OPENMP
#pragma omp critical
#endif
        {
            n_strong += s_strong;
            n_dlt_ge0 += s_dlt;
            n_pisa += s_pisa;
            n_tight += s_tight;
            merge_keys(keys, &nkeys, lkeys, lnkeys);
        }
    }

    printf("{\n");
    printf("  \"n\": %d,\n", n);
    printf("  \"labeled_oriented\": %llu,\n", (unsigned long long)n_oriented);
    printf("  \"strong\": %llu,\n", (unsigned long long)n_strong);
    printf("  \"delta_ge0\": %llu,\n", (unsigned long long)n_dlt_ge0);
    printf("  \"pisa\": %llu,\n", (unsigned long long)n_pisa);
    printf("  \"pisa_tight\": %llu,\n", (unsigned long long)n_tight);
    printf("  \"missing_degree_types\": [\n");
    for (int i = 0; i < nkeys; i++) {
        printf("    {\"missing_deg\": ");
        print_key(keys[i].key);
        printf(", \"count\": %llu}%s\n", (unsigned long long)keys[i].count,
               (i + 1 < nkeys) ? "," : "");
    }
    printf("  ]\n");
    printf("}\n");
    return 0;
}
