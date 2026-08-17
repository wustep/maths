/* Read graph6 undirected graphs (geng) and exhaust orientations.

   For each input graph G, try all 2^{e(G)} orientations and count those
   that are Pisa (strong + Delta==0).  Reports missing-degree types.

   gcc -O3 -march=native -o enum_pisa_geng enum_pisa_geng.c
   geng -q 8 | ./enum_pisa_geng
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int popcnt(uint32_t x) { return __builtin_popcount(x); }

static int parse_graph6(const char *s, int *n_out, uint32_t *und) {
    if (!s || s[0] == 0 || s[0] == '>') return -1;
    int n = (unsigned char)s[0] - 63;
    if (n < 1 || n > 32) return -1;
    int npairs = n * (n - 1) / 2;
    int nbytes = (npairs + 5) / 6;
    if ((int)strlen(s) < 1 + nbytes) return -1;
    memset(und, 0, sizeof(uint32_t) * (size_t)n);
    /* graph6 stores the upper triangle column-by-column, top to bottom. */
    int bit = 0, bi = 0;
    int val = 0;
    for (int j = 1; j < n; j++) {
        for (int i = 0; i < j; i++) {
            if (bit == 0) {
                val = (unsigned char)s[1 + bi] - 63;
                bi++;
                bit = 6;
            }
            bit--;
            if (val & (1 << bit)) {
                und[i] |= 1u << j;
                und[j] |= 1u << i;
            }
        }
    }
    *n_out = n;
    return 0;
}

static int is_strong(int n, const uint32_t *out) {
    uint32_t inn[32] = {0};
    uint32_t full = (n == 32) ? ~0u : ((1u << n) - 1u);
    for (int v = 0; v < n; v++) {
        uint32_t m = out[v];
        while (m) {
            int w = __builtin_ctz(m);
            inn[w] |= 1u << v;
            m &= m - 1;
        }
    }
    uint32_t seen = 1u, frontier = 1u;
    while (frontier) {
        uint32_t nxt = 0, f = frontier;
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
    seen = 1u;
    frontier = 1u;
    while (frontier) {
        uint32_t nxt = 0, f = frontier;
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

static int delta_of(int n, const uint32_t *out) {
    int dlt = -n;
    for (int v = 0; v < n; v++) {
        uint32_t first = out[v];
        uint32_t second = 0, m = first;
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

static uint32_t miss_key(int n, const uint32_t *out) {
    int deg[32];
    uint32_t full = (n == 32) ? ~0u : ((1u << n) - 1u);
    for (int v = 0; v < n; v++) {
        uint32_t present = out[v];
        for (int w = 0; w < n; w++)
            if ((out[w] >> v) & 1u) present |= 1u << w;
        deg[v] = popcnt(full ^ (1u << v) ^ present);
    }
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

#define MAXKEYS 512
typedef struct { uint32_t key; uint64_t count; uint64_t graphs; } KeyCount;

static void add_key(KeyCount *tab, int *nt, uint32_t key, uint64_t c) {
    for (int i = 0; i < *nt; i++)
        if (tab[i].key == key) {
            tab[i].count += c;
            tab[i].graphs += 1;
            return;
        }
    tab[*nt].key = key;
    tab[*nt].count = c;
    tab[*nt].graphs = 1;
    (*nt)++;
}

static void print_key(int n, uint32_t key) {
    int deg[32];
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

int main(void) {
    char line[256];
    uint32_t und[32];
    uint32_t out[32];
    int n = 0;
    uint64_t ngraphs = 0, norient = 0, npisa = 0, nstrong = 0;
    KeyCount keys[MAXKEYS];
    int nkeys = 0;
    int pair_u[256], pair_v[256];

    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n' || line[L - 1] == '\r')) line[--L] = 0;
        if (L == 0 || line[0] == '>') continue;
        int nn;
        if (parse_graph6(line, &nn, und) != 0) continue;
        n = nn;
        int e = 0;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if ((und[i] >> j) & 1u) {
                    pair_u[e] = i;
                    pair_v[e] = j;
                    e++;
                }
        ngraphs++;
        uint64_t orients = 1ull << e;
        norient += orients;
        uint64_t local_pisa = 0;
        for (uint64_t mask = 0; mask < orients; mask++) {
            memset(out, 0, sizeof(uint32_t) * (size_t)n);
            for (int k = 0; k < e; k++) {
                int u = pair_u[k], v = pair_v[k];
                if (mask & (1ull << k)) out[u] |= 1u << v;
                else out[v] |= 1u << u;
            }
            int dlt = delta_of(n, out);
            if (dlt != 0) continue;
            if (!is_strong(n, out)) continue;
            local_pisa++;
            add_key(keys, &nkeys, miss_key(n, out), 1);
        }
        if (local_pisa) {
            /* mark this undirected graph once per type already done inside add_key;
               keep a separate graph counter via nkeys side effect. */
        }
        npisa += local_pisa;
        if ((ngraphs % 200) == 0) {
            fprintf(stderr, "graphs=%llu pisa=%llu types=%d last_e=%d\n",
                    (unsigned long long)ngraphs, (unsigned long long)npisa,
                    nkeys, e);
        }
        (void)nstrong;
    }

    printf("{\n");
    printf("  \"n\": %d,\n", n);
    printf("  \"unlabeled_undirected\": %llu,\n", (unsigned long long)ngraphs);
    printf("  \"orientations_of_reps\": %llu,\n", (unsigned long long)norient);
    printf("  \"pisa_on_reps\": %llu,\n", (unsigned long long)npisa);
    printf("  \"note\": \"counts are over geng representatives, not labeled graphs\",\n");
    printf("  \"missing_degree_types\": [\n");
    for (int i = 0; i < nkeys; i++) {
        printf("    {\"missing_deg\": ");
        print_key(n, keys[i].key);
        printf(", \"pisa_orients\": %llu, \"undirected_graphs\": %llu}%s\n",
               (unsigned long long)keys[i].count,
               (unsigned long long)keys[i].graphs,
               (i + 1 < nkeys) ? "," : "");
    }
    printf("  ]\n}\n");
    return 0;
}
