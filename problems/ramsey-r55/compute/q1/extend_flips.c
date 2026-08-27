/* One-edge-flip neighbourhood of the 656 known (5,5,42)-graphs, then
   the one-vertex extension SAT on every surviving flip.

   gcc -O3 -std=c11 -o extend_flips extend_flips.c
   ./extend_flips ../refs/r55_42some.g6
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 18
#define DEG_HI 24
#define MAXK 8000

static uint64_t nbr[N];
static uint64_t k4[MAXK];
static uint64_t i4[MAXK];
static int nk4, ni4;
static int assign[N];
static unsigned long long nodes, conflicts, decisions;
static int sat_found;
static uint64_t last_model;

static int pop64(uint64_t x) { return __builtin_popcountll(x); }

static int has_triangle_in_mask(const uint64_t *adj, uint64_t mask) {
    uint64_t m = mask;
    while (m) {
        uint64_t ubit = m & -m;
        int u = __builtin_ctzll(ubit);
        uint64_t r = adj[u] & (m ^ ubit);
        while (r) {
            uint64_t vbit = r & -r;
            int v = __builtin_ctzll(vbit);
            if (adj[v] & r) return 1;
            r ^= vbit;
        }
        m ^= ubit;
    }
    return 0;
}

static int flip_preserves(const uint64_t *adj, int u, int v, int is_edge) {
    if (is_edge) {
        uint64_t full = (1ULL << N) - 1ULL;
        uint64_t common_non = full ^ (adj[u] | adj[v] | (1ULL << u) | (1ULL << v));
        uint64_t cadj[N];
        for (int i = 0; i < N; i++) cadj[i] = (full ^ (1ULL << i)) ^ adj[i];
        return !has_triangle_in_mask(cadj, common_non);
    }
    return !has_triangle_in_mask(adj, adj[u] & adj[v]);
}

static void list_k4(uint64_t *adj, uint64_t *out, int *nout) {
    int a, b, c, d;
    *nout = 0;
    for (a = 0; a < N; a++) {
        for (b = a + 1; b < N; b++) {
            if (!((adj[a] >> b) & 1ULL)) continue;
            uint64_t cab = adj[a] & adj[b];
            for (c = b + 1; c < N; c++) {
                if (!((cab >> c) & 1ULL)) continue;
                uint64_t cabc = cab & adj[c];
                for (d = c + 1; d < N; d++) {
                    if ((cabc >> d) & 1ULL) {
                        if (*nout >= MAXK) {
                            fprintf(stderr, "MAXK overflow\n");
                            exit(2);
                        }
                        out[(*nout)++] =
                            (1ULL << a) | (1ULL << b) | (1ULL << c) | (1ULL << d);
                    }
                }
            }
        }
    }
}

static int propagate(void) {
    int changed = 1;
    while (changed) {
        changed = 0;
        int ones = 0, zeros = 0;
        for (int i = 0; i < N; i++) {
            if (assign[i] == 1) ones++;
            else if (assign[i] == 0) zeros++;
        }
        if (ones > DEG_HI) return 0;
        if (zeros > N - DEG_LO) return 0;
        if (ones == DEG_HI) {
            for (int i = 0; i < N; i++)
                if (assign[i] == -1) {
                    assign[i] = 0;
                    changed = 1;
                }
            if (changed) continue;
        }
        if (zeros == N - DEG_LO) {
            for (int i = 0; i < N; i++)
                if (assign[i] == -1) {
                    assign[i] = 1;
                    changed = 1;
                }
            if (changed) continue;
        }
        for (int t = 0; t < nk4; t++) {
            uint64_t m = k4[t];
            int in_s = 0, nundef = 0, last = -1;
            while (m) {
                uint64_t b = m & -m;
                int v = __builtin_ctzll(b);
                if (assign[v] == 1) in_s++;
                else if (assign[v] == -1) {
                    nundef++;
                    last = v;
                }
                m ^= b;
            }
            if (in_s == 4) return 0;
            if (in_s == 3 && nundef == 1 && assign[last] != 0) {
                if (assign[last] == 1) return 0;
                assign[last] = 0;
                changed = 1;
            }
        }
        for (int t = 0; t < ni4; t++) {
            uint64_t m = i4[t];
            int out_s = 0, nundef = 0, last = -1;
            while (m) {
                uint64_t b = m & -m;
                int v = __builtin_ctzll(b);
                if (assign[v] == 0) out_s++;
                else if (assign[v] == -1) {
                    nundef++;
                    last = v;
                }
                m ^= b;
            }
            if (out_s == 4) return 0;
            if (out_s == 3 && nundef == 1 && assign[last] != 1) {
                if (assign[last] == 0) return 0;
                assign[last] = 1;
                changed = 1;
            }
        }
    }
    return 1;
}

static int rec(void) {
    nodes++;
    int snap[N];
    memcpy(snap, assign, sizeof(snap));
    if (!propagate()) {
        conflicts++;
        memcpy(assign, snap, sizeof(snap));
        return 0;
    }
    int best = -1, bests = -1;
    for (int i = 0; i < N; i++) {
        if (assign[i] != -1) continue;
        uint64_t bit = 1ULL << i;
        int sc = 0;
        for (int t = 0; t < nk4; t++)
            if (k4[t] & bit) sc++;
        for (int t = 0; t < ni4; t++)
            if (i4[t] & bit) sc++;
        if (sc > bests) {
            bests = sc;
            best = i;
        }
    }
    if (best < 0) {
        int ones = 0;
        uint64_t mask = 0;
        for (int i = 0; i < N; i++)
            if (assign[i] == 1) {
                ones++;
                mask |= 1ULL << i;
            }
        if (ones >= DEG_LO && ones <= DEG_HI) {
            sat_found = 1;
            last_model = mask;
        }
        memcpy(assign, snap, sizeof(snap));
        return 0;
    }
    int after[N];
    memcpy(after, assign, sizeof(after));
    for (int val = 1; val >= 0; val--) {
        memcpy(assign, after, sizeof(after));
        decisions++;
        assign[best] = val;
        rec();
        if (sat_found) {
            memcpy(assign, snap, sizeof(snap));
            return 0;
        }
    }
    memcpy(assign, snap, sizeof(snap));
    return 0;
}

static int extends(uint64_t *adj) {
    uint64_t full = (1ULL << N) - 1ULL;
    uint64_t cadj[N];
    for (int i = 0; i < N; i++) cadj[i] = (full ^ (1ULL << i)) ^ adj[i];
    memcpy(nbr, adj, sizeof(nbr));
    list_k4(adj, k4, &nk4);
    list_k4(cadj, i4, &ni4);
    for (int i = 0; i < N; i++) assign[i] = -1;
    nodes = conflicts = decisions = 0;
    sat_found = 0;
    last_model = 0;
    rec();
    return sat_found;
}

static int parse_graph6(const char *s, uint64_t *out) {
    if (!s || !s[0]) return -1;
    int n = (unsigned char)s[0] - 63;
    if (n != N) return -1;
    memset(out, 0, N * sizeof(uint64_t));
    int bitpos = 0;
    for (int j = 1; j < N; j++) {
        for (int i = 0; i < j; i++) {
            int byte = bitpos / 6;
            int off = 5 - (bitpos % 6);
            int bit = (((unsigned char)s[1 + byte] - 63) >> off) & 1;
            if (bit) {
                out[i] |= 1ULL << j;
                out[j] |= 1ULL << i;
            }
            bitpos++;
        }
    }
    return 0;
}

static void complement_of(const uint64_t *in, uint64_t *out) {
    uint64_t full = (1ULL << N) - 1ULL;
    for (int i = 0; i < N; i++) out[i] = (full ^ (1ULL << i)) ^ in[i];
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../refs/r55_42some.g6";
    FILE *f = fopen(path, "r");
    if (!f) {
        perror(path);
        return 2;
    }
    char line[512];
    int idx = 0;
    unsigned long long n_flip_ok = 0, n_ext = 0, n_tried = 0;
    clock_t t0 = clock();
    printf("idx side op u v sat nodes\n");
    while (fgets(line, sizeof(line), f)) {
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n' || line[L - 1] == '\r')) line[--L] = 0;
        if (!L) continue;
        uint64_t adj[N], cadj[N];
        if (parse_graph6(line, adj) != 0) {
            fprintf(stderr, "bad graph6 line %d\n", idx);
            return 2;
        }
        complement_of(adj, cadj);
        for (int side = 0; side < 2; side++) {
            uint64_t g[N];
            memcpy(g, side ? cadj : adj, sizeof(g));
            for (int u = 0; u < N; u++) {
                for (int v = u + 1; v < N; v++) {
                    n_tried++;
                    int is_edge = (int)((g[u] >> v) & 1ULL);
                    if (!flip_preserves(g, u, v, is_edge)) continue;
                    n_flip_ok++;
                    g[u] ^= 1ULL << v;
                    g[v] ^= 1ULL << u;
                    int sat = extends(g);
                    if (sat) {
                        n_ext++;
                        printf("%d %s %s %d %d 1 %llu model=0x%llx pop=%d\n", idx,
                               side ? "comp" : "stored", is_edge ? "del" : "add",
                               u, v, nodes, (unsigned long long)last_model,
                               pop64(last_model));
                        fflush(stdout);
                    }
                    g[u] ^= 1ULL << v;
                    g[v] ^= 1ULL << u;
                }
            }
        }
        if ((idx + 1) % 20 == 0) {
            fprintf(stderr, "progress %d/328 flip_ok=%llu ext=%llu\n", idx + 1,
                    n_flip_ok, n_ext);
        }
        idx++;
    }
    fclose(f);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE graphs_pairs=%d tried=%llu flip_ok=%llu extensions=%llu sec=%.3f\n",
           idx, n_tried, n_flip_ok, n_ext, sec);
    return 0; /* completed; extensions are in the log */
}
