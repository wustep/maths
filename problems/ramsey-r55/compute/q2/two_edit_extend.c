/* Exhaust every unordered pair of edge toggles around the published 656
   (5,5,42)-graphs, including pairs whose one-toggle intermediate is illegal.
   Every final (5,5,42)-graph is tested for a one-vertex extension.

   gcc -O3 -std=c11 -o two_edit_extend two_edit_extend.c
   ./two_edit_extend ../refs/r55_42some.g6
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 18
#define DEG_HI 24
#define NEDGES ((N * (N - 1)) / 2)
#define MAXK 8000

typedef struct { unsigned char u, v, was_edge, single_ok; } Flip;

static uint64_t k4[MAXK], i4[MAXK];
static int nk4, ni4, assign_v[N];
static unsigned long long ext_nodes, ext_conflicts, ext_decisions;
static int sat_found;
static uint64_t last_model;

static int pop64(uint64_t x) { return __builtin_popcountll(x); }

static int has_triangle_in_mask(const uint64_t *adj, uint64_t mask) {
    uint64_t m = mask;
    while (m) {
        uint64_t ub = m & -m;
        int u = __builtin_ctzll(ub);
        uint64_t r = adj[u] & (m ^ ub);
        while (r) {
            uint64_t vb = r & -r;
            int v = __builtin_ctzll(vb);
            if (adj[v] & r) return 1;
            r ^= vb;
        }
        m ^= ub;
    }
    return 0;
}

static int has_independent_triangle_in_mask(const uint64_t *adj, uint64_t mask) {
    uint64_t m = mask;
    while (m) {
        uint64_t ub = m & -m;
        int u = __builtin_ctzll(ub);
        uint64_t r = (m ^ ub) & ~adj[u];
        while (r) {
            uint64_t vb = r & -r;
            int v = __builtin_ctzll(vb);
            if (r & ~adj[v] & ~(vb | ub)) return 1;
            r ^= vb;
        }
        m ^= ub;
    }
    return 0;
}

/* The starting graph is (5,5).  A new K5 must contain a newly added edge;
   a new independent 5-set must contain a newly deleted edge. */
static int final_preserves(const uint64_t *adj, const Flip *a, const Flip *b) {
    const Flip *fs[2] = {a, b};
    uint64_t full = (1ULL << N) - 1ULL;
    for (int z = 0; z < 2; z++) {
        int u = fs[z]->u, v = fs[z]->v;
        if (!fs[z]->was_edge) {
            if (has_triangle_in_mask(adj, adj[u] & adj[v])) return 0;
        } else {
            uint64_t common_non = full & ~adj[u] & ~adj[v];
            common_non &= ~((1ULL << u) | (1ULL << v));
            if (has_independent_triangle_in_mask(adj, common_non)) return 0;
        }
    }
    return 1;
}

static int single_preserves(const uint64_t *adj, const Flip *f) {
    int u = f->u, v = f->v;
    if (!f->was_edge)
        return !has_triangle_in_mask(adj, adj[u] & adj[v]);
    uint64_t full = (1ULL << N) - 1ULL;
    uint64_t common_non = full & ~adj[u] & ~adj[v];
    common_non &= ~((1ULL << u) | (1ULL << v));
    return !has_independent_triangle_in_mask(adj, common_non);
}

static void list_k4(const uint64_t *adj, uint64_t *out, int *nout) {
    *nout = 0;
    for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) {
        if (!((adj[a] >> b) & 1ULL)) continue;
        uint64_t ab = adj[a] & adj[b];
        for (int c = b + 1; c < N; c++) {
            if (!((ab >> c) & 1ULL)) continue;
            uint64_t abc = ab & adj[c];
            for (int d = c + 1; d < N; d++) if ((abc >> d) & 1ULL) {
                if (*nout >= MAXK) {
                    fprintf(stderr, "MAXK overflow\n");
                    exit(2);
                }
                out[(*nout)++] = (1ULL << a) | (1ULL << b) |
                                  (1ULL << c) | (1ULL << d);
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
            if (assign_v[i] == 1) ones++;
            else if (assign_v[i] == 0) zeros++;
        }
        if (ones > DEG_HI || zeros > N - DEG_LO) return 0;
        if (ones == DEG_HI) {
            for (int i = 0; i < N; i++) if (assign_v[i] < 0) {
                assign_v[i] = 0; changed = 1;
            }
            if (changed) continue;
        }
        if (zeros == N - DEG_LO) {
            for (int i = 0; i < N; i++) if (assign_v[i] < 0) {
                assign_v[i] = 1; changed = 1;
            }
            if (changed) continue;
        }
        for (int family = 0; family < 2; family++) {
            uint64_t *sets = family ? i4 : k4;
            int nsets = family ? ni4 : nk4;
            int forbidden = family ? 0 : 1;
            int forced = 1 - forbidden;
            for (int t = 0; t < nsets; t++) {
                uint64_t m = sets[t];
                int count = 0, undef = 0, last = -1;
                while (m) {
                    uint64_t bit = m & -m;
                    int v = __builtin_ctzll(bit);
                    if (assign_v[v] == forbidden) count++;
                    else if (assign_v[v] < 0) { undef++; last = v; }
                    m ^= bit;
                }
                if (count == 4) return 0;
                if (count == 3 && undef == 1) {
                    if (assign_v[last] == forbidden) return 0;
                    if (assign_v[last] < 0) {
                        assign_v[last] = forced; changed = 1;
                    }
                }
            }
        }
    }
    return 1;
}

static void extend_rec(void) {
    ext_nodes++;
    int snap[N];
    memcpy(snap, assign_v, sizeof(snap));
    if (!propagate()) {
        ext_conflicts++;
        memcpy(assign_v, snap, sizeof(snap));
        return;
    }
    int best = -1, best_score = -1;
    for (int i = 0; i < N; i++) if (assign_v[i] < 0) {
        uint64_t bit = 1ULL << i;
        int score = 0;
        for (int t = 0; t < nk4; t++) if (k4[t] & bit) score++;
        for (int t = 0; t < ni4; t++) if (i4[t] & bit) score++;
        if (score > best_score) { best = i; best_score = score; }
    }
    if (best < 0) {
        int ones = 0;
        uint64_t model = 0;
        for (int i = 0; i < N; i++) if (assign_v[i] == 1) {
            ones++; model |= 1ULL << i;
        }
        if (ones >= DEG_LO && ones <= DEG_HI) {
            sat_found = 1; last_model = model;
        }
        memcpy(assign_v, snap, sizeof(snap));
        return;
    }
    int after[N];
    memcpy(after, assign_v, sizeof(after));
    for (int value = 1; value >= 0 && !sat_found; value--) {
        memcpy(assign_v, after, sizeof(after));
        ext_decisions++;
        assign_v[best] = value;
        extend_rec();
    }
    memcpy(assign_v, snap, sizeof(snap));
}

static int extends(const uint64_t *adj) {
    uint64_t full = (1ULL << N) - 1ULL, cadj[N];
    for (int i = 0; i < N; i++) cadj[i] = (full ^ (1ULL << i)) ^ adj[i];
    list_k4(adj, k4, &nk4);
    list_k4(cadj, i4, &ni4);
    for (int i = 0; i < N; i++) assign_v[i] = -1;
    ext_nodes = ext_conflicts = ext_decisions = 0;
    sat_found = 0; last_model = 0;
    extend_rec();
    return sat_found;
}

static int parse_graph6(const char *s, uint64_t *out) {
    if (!s || (unsigned char)s[0] - 63 != N) return -1;
    memset(out, 0, N * sizeof(uint64_t));
    int bitpos = 0;
    for (int j = 1; j < N; j++) for (int i = 0; i < j; i++) {
        int byte = bitpos / 6, off = 5 - bitpos % 6;
        int bit = (((unsigned char)s[1 + byte] - 63) >> off) & 1;
        if (bit) { out[i] |= 1ULL << j; out[j] |= 1ULL << i; }
        bitpos++;
    }
    return 0;
}

static void complement_of(const uint64_t *in, uint64_t *out) {
    uint64_t full = (1ULL << N) - 1ULL;
    for (int i = 0; i < N; i++) out[i] = (full ^ (1ULL << i)) ^ in[i];
}

static void print_witness(const uint64_t *adj, int idx, int side,
                          const Flip *a, const Flip *b) {
    printf("HIT idx=%d side=%s flips=%d-%d,%d-%d model=0x%llx pop=%d",
           idx, side ? "comp" : "stored", a->u, a->v, b->u, b->v,
           (unsigned long long)last_model, pop64(last_model));
    for (int i = 0; i < N; i++) printf(" row%d=0x%llx", i,
        (unsigned long long)adj[i]);
    printf("\n");
    fflush(stdout);
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../refs/r55_42some.g6";
    int limit = argc > 2 ? atoi(argv[2]) : 328;
    int classify_only = argc > 3 && !strcmp(argv[3], "classify");
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return 2; }
    char line[512];
    int idx = 0;
    unsigned long long pairs = 0, final_ok = 0, extensions = 0;
    unsigned long long path0 = 0, path1 = 0, path2 = 0;
    unsigned long long sum_nodes = 0;
    clock_t t0 = clock();
    while (idx < limit && fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (!len) continue;
        uint64_t stored[N], comp[N];
        if (parse_graph6(line, stored)) { fprintf(stderr, "bad graph6 %d\n", idx); return 2; }
        complement_of(stored, comp);
        for (int side = 0; side < 2; side++) {
            uint64_t g[N];
            memcpy(g, side ? comp : stored, sizeof(g));
            Flip flips[NEDGES];
            int nf = 0;
            for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) {
                flips[nf] = (Flip){(unsigned char)u, (unsigned char)v,
                                   (unsigned char)((g[u] >> v) & 1ULL), 0};
                flips[nf].single_ok = (unsigned char)single_preserves(g, &flips[nf]);
                nf++;
            }
            for (int x = 0; x < nf; x++) {
                Flip *a = &flips[x];
                g[a->u] ^= 1ULL << a->v; g[a->v] ^= 1ULL << a->u;
                for (int y = x + 1; y < nf; y++) {
                    Flip *b = &flips[y];
                    pairs++;
                    g[b->u] ^= 1ULL << b->v; g[b->v] ^= 1ULL << b->u;
                    if (final_preserves(g, a, b)) {
                        final_ok++;
                        int paths = a->single_ok + b->single_ok;
                        if (paths == 0) path0++;
                        else if (paths == 1) path1++;
                        else path2++;
                        if (!classify_only) {
                            if (extends(g)) {
                                extensions++;
                                print_witness(g, idx, side, a, b);
                            }
                            sum_nodes += ext_nodes;
                        }
                    }
                    g[b->u] ^= 1ULL << b->v; g[b->v] ^= 1ULL << b->u;
                }
                g[a->u] ^= 1ULL << a->v; g[a->v] ^= 1ULL << a->u;
            }
        }
        idx++;
        if (idx % 8 == 0 || idx == limit) {
            double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
            fprintf(stderr,
                "progress %d/%d pairs=%llu final_ok=%llu ext=%llu sec=%.1f\n",
                idx, limit, pairs, final_ok, extensions, sec);
        }
    }
    fclose(f);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE graph_pairs=%d toggle_pairs=%llu final_ok=%llu path0=%llu "
           "path1=%llu path2=%llu extensions=%llu extension_nodes=%llu "
           "mode=%s sec=%.3f\n", idx, pairs, final_ok, path0, path1, path2,
           extensions, sum_nodes, classify_only ? "classify" : "extend", sec);
    return 0;
}
