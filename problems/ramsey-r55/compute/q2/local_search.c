/* Tabu search for a (5,5,43)-graph.  The objective is the exact number of
   5-cliques plus independent 5-sets.  Each restart begins with a published
   (5,5,42)-graph (or its complement) and a random 43rd vertex.

   This is a construction search only.  Failure is residue, never a bound.

   gcc -O3 -std=c11 -o local_search local_search.c
   ./local_search ../refs/r55_42some.g6 1 100 200000
*/

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N 43
#define OLDN 42
#define NFIVE 962598
#define NEDGE 903

static uint64_t adj[N];
static uint64_t best_adj[N];
static uint64_t bad_list[NFIVE];
static int bad_pos[NFIVE];
static int choose_c[N + 1][6];
static int edge_id[N][N], edge_u[NEDGE], edge_v[NEDGE];
static uint64_t rng_state;

static uint64_t rng64(void) {
    uint64_t x = rng_state;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return rng_state = x;
}

static int rank5(uint64_t mask) {
    int rank = 0, i = 1;
    while (mask) {
        uint64_t bit = mask & -mask;
        int v = __builtin_ctzll(bit);
        rank += choose_c[v][i++];
        mask ^= bit;
    }
    return rank;
}

static int bad5(uint64_t mask) {
    int edges = 0;
    uint64_t m = mask;
    while (m) {
        uint64_t ub = m & -m;
        int u = __builtin_ctzll(ub);
        edges += __builtin_popcountll(adj[u] & (m ^ ub));
        m ^= ub;
    }
    return edges == 0 || edges == 10;
}

static int initialise_bad(void) {
    memset(bad_pos, 0xff, sizeof(bad_pos));
    int nbad = 0;
    for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++)
    for (int c = b + 1; c < N; c++) for (int d = c + 1; d < N; d++)
    for (int e = d + 1; e < N; e++) {
        uint64_t mask = (1ULL << a) | (1ULL << b) | (1ULL << c) |
                        (1ULL << d) | (1ULL << e);
        if (bad5(mask)) {
            int rank = choose_c[a][1] + choose_c[b][2] + choose_c[c][3] +
                       choose_c[d][4] + choose_c[e][5];
            bad_pos[rank] = nbad;
            bad_list[nbad++] = mask;
        }
    }
    return nbad;
}

static void add_bad(uint64_t mask, int *nbad) {
    int rank = rank5(mask);
    if (bad_pos[rank] >= 0) return;
    bad_pos[rank] = *nbad;
    bad_list[(*nbad)++] = mask;
}

static void remove_bad(uint64_t mask, int *nbad) {
    int rank = rank5(mask), pos = bad_pos[rank];
    if (pos < 0) return;
    uint64_t last = bad_list[--(*nbad)];
    bad_list[pos] = last;
    bad_pos[rank5(last)] = pos;
    bad_pos[rank] = -1;
}

static int count_triangles(uint64_t mask) {
    int count = 0;
    uint64_t m = mask;
    while (m) {
        uint64_t ub = m & -m;
        int u = __builtin_ctzll(ub);
        uint64_t r = adj[u] & (m ^ ub);
        while (r) {
            uint64_t vb = r & -r;
            int v = __builtin_ctzll(vb);
            count += __builtin_popcountll(adj[v] & r);
            r ^= vb;
        }
        m ^= ub;
    }
    return count;
}

static int count_independent_triangles(uint64_t mask) {
    int count = 0;
    uint64_t m = mask;
    while (m) {
        uint64_t ub = m & -m;
        int u = __builtin_ctzll(ub);
        uint64_t r = (m ^ ub) & ~adj[u];
        while (r) {
            uint64_t vb = r & -r;
            int v = __builtin_ctzll(vb);
            count += __builtin_popcountll(r & ~adj[v] & ~vb);
            r ^= vb;
        }
        m ^= ub;
    }
    return count;
}

static int flip_delta(int u, int v) {
    uint64_t full = (1ULL << N) - 1ULL;
    int was_edge = (adj[u] >> v) & 1ULL;
    uint64_t common = adj[u] & adj[v] & ~(1ULL << u) & ~(1ULL << v);
    uint64_t common_non = full & ~adj[u] & ~adj[v] &
                          ~(1ULL << u) & ~(1ULL << v);
    int kc = count_triangles(common);
    int ic = count_independent_triangles(common_non);
    return was_edge ? ic - kc : kc - ic;
}

static void apply_flip(int u, int v, int *nbad) {
    int was_edge = (adj[u] >> v) & 1ULL;
    int other[OLDN - 1], no = 0;
    for (int w = 0; w < N; w++) if (w != u && w != v) other[no++] = w;
    for (int ia = 0; ia < no; ia++) for (int ib = ia + 1; ib < no; ib++)
    for (int ic = ib + 1; ic < no; ic++) {
        int a = other[ia], b = other[ib], c = other[ic];
        uint64_t triple = (1ULL << a) | (1ULL << b) | (1ULL << c);
        int all_edges = ((adj[u] & adj[v] & triple) == triple) &&
                        ((adj[a] >> b) & 1ULL) && ((adj[a] >> c) & 1ULL) &&
                        ((adj[b] >> c) & 1ULL);
        int all_non = (((adj[u] | adj[v]) & triple) == 0) &&
                      !((adj[a] >> b) & 1ULL) && !((adj[a] >> c) & 1ULL) &&
                      !((adj[b] >> c) & 1ULL);
        if (!all_edges && !all_non) continue;
        uint64_t five = triple | (1ULL << u) | (1ULL << v);
        if (was_edge) {
            if (all_edges) remove_bad(five, nbad);
            if (all_non) add_bad(five, nbad);
        } else {
            if (all_non) remove_bad(five, nbad);
            if (all_edges) add_bad(five, nbad);
        }
    }
    adj[u] ^= 1ULL << v;
    adj[v] ^= 1ULL << u;
}

static int parse_graph6(const char *s, uint64_t *out) {
    if (!s || (unsigned char)s[0] - 63 != OLDN) return -1;
    memset(out, 0, N * sizeof(uint64_t));
    int bitpos = 0;
    for (int j = 1; j < OLDN; j++) for (int i = 0; i < j; i++) {
        int byte = bitpos / 6, off = 5 - bitpos % 6;
        int bit = (((unsigned char)s[1 + byte] - 63) >> off) & 1;
        if (bit) { out[i] |= 1ULL << j; out[j] |= 1ULL << i; }
        bitpos++;
    }
    return 0;
}

static void complement42(uint64_t *g) {
    uint64_t full = (1ULL << OLDN) - 1ULL;
    for (int i = 0; i < OLDN; i++) g[i] = (full ^ (1ULL << i)) ^ g[i];
}

static void random_new_vertex(void) {
    int vertices[OLDN];
    for (int i = 0; i < OLDN; i++) vertices[i] = i;
    for (int i = OLDN - 1; i; i--) {
        int j = (int)(rng64() % (uint64_t)(i + 1));
        int t = vertices[i]; vertices[i] = vertices[j]; vertices[j] = t;
    }
    int degree = 18 + (int)(rng64() % 7);
    adj[42] = 0;
    for (int i = 0; i < degree; i++) {
        int v = vertices[i];
        adj[42] |= 1ULL << v;
        adj[v] |= 1ULL << 42;
    }
}

static void print_graph6(void) {
    putchar((char)(N + 63));
    int value = 0, bits = 0;
    for (int j = 1; j < N; j++) for (int i = 0; i < j; i++) {
        value = (value << 1) | (int)((adj[i] >> j) & 1ULL);
        if (++bits == 6) { putchar((char)(value + 63)); value = bits = 0; }
    }
    if (bits) { value <<= 6 - bits; putchar((char)(value + 63)); }
    putchar('\n');
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../refs/r55_42some.g6";
    uint64_t seed = argc > 2 ? strtoull(argv[2], 0, 10) : 1;
    int restarts = argc > 3 ? atoi(argv[3]) : 100;
    int max_steps = argc > 4 ? atoi(argv[4]) : 200000;
    rng_state = seed ? seed : 1;
    memset(choose_c, 0, sizeof(choose_c));
    for (int n = 0; n <= N; n++) {
        choose_c[n][0] = 1;
        for (int k = 1; k <= 5 && k <= n; k++)
            choose_c[n][k] = choose_c[n-1][k-1] + choose_c[n-1][k];
    }
    int eid = 0;
    for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) {
        edge_id[u][v] = edge_id[v][u] = eid;
        edge_u[eid] = u; edge_v[eid] = v; eid++;
    }
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return 2; }
    char lines[328][512]; int nlines = 0;
    while (nlines < 328 && fgets(lines[nlines], sizeof(lines[0]), f)) nlines++;
    fclose(f);
    int global_best = INT_MAX;
    clock_t t0 = clock();
    for (int restart = 0; restart < restarts; restart++) {
        int src = (int)(rng64() % (uint64_t)nlines);
        if (parse_graph6(lines[src], adj)) return 2;
        int side = rng64() & 1;
        if (side) complement42(adj);
        random_new_vertex();
        int nbad = initialise_bad();
        int best = nbad, stale = 0;
        int tabu[NEDGE]; memset(tabu, 0, sizeof(tabu));
        if (nbad < global_best) {
            global_best = nbad;
            memcpy(best_adj, adj, sizeof(best_adj));
            printf("BEST score=%d restart=%d step=0 src=%d side=%d\n",
                   nbad, restart, src, side); fflush(stdout);
        }
        for (int step = 1; step <= max_steps && nbad; step++) {
            uint64_t violation = bad_list[rng64() % (uint64_t)nbad];
            int verts[5], nv = 0;
            while (violation) {
                uint64_t bit = violation & -violation;
                verts[nv++] = __builtin_ctzll(bit); violation ^= bit;
            }
            int chosen = -1, chosen_delta = INT_MAX;
            for (int i = 0; i < 5; i++) for (int j = i + 1; j < 5; j++) {
                int e = edge_id[verts[i]][verts[j]];
                int delta = flip_delta(verts[i], verts[j]);
                int allowed = tabu[e] <= step || nbad + delta < global_best;
                if (allowed && (delta < chosen_delta ||
                    (delta == chosen_delta && (rng64() & 1)))) {
                    chosen = e; chosen_delta = delta;
                }
            }
            if (chosen < 0) {
                int i = (int)(rng64() % 5), j = (i + 1 + (int)(rng64() % 4)) % 5;
                chosen = edge_id[verts[i]][verts[j]];
            }
            int before = nbad;
            apply_flip(edge_u[chosen], edge_v[chosen], &nbad);
            if (nbad - before != flip_delta(edge_u[chosen], edge_v[chosen]) * -1) {
                /* flip_delta is now evaluated in the reverse direction. */
                fprintf(stderr, "delta mismatch before=%d after=%d reverse=%d\n",
                        before, nbad, flip_delta(edge_u[chosen], edge_v[chosen]));
                return 3;
            }
            tabu[chosen] = step + 7 + (int)(rng64() % 13);
            if (nbad < best) { best = nbad; stale = 0; } else stale++;
            if (nbad < global_best) {
                global_best = nbad;
                memcpy(best_adj, adj, sizeof(best_adj));
                printf("BEST score=%d restart=%d step=%d src=%d side=%d\n",
                       nbad, restart, step, src, side); fflush(stdout);
            }
            if (stale > 20000) break;
        }
        if (!nbad) {
            printf("HIT seed=%llu restart=%d src=%d side=%d graph6=",
                   (unsigned long long)seed, restart, src, side);
            print_graph6();
            return 0;
        }
        if ((restart + 1) % 10 == 0) {
            double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
            fprintf(stderr, "progress %d/%d global_best=%d sec=%.1f\n",
                    restart + 1, restarts, global_best, sec);
        }
    }
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE seed=%llu restarts=%d max_steps=%d best=%d sec=%.3f\n",
           (unsigned long long)seed, restarts, max_steps, global_best, sec);
    memcpy(adj, best_adj, sizeof(adj));
    int final_bad = initialise_bad();
    printf("BEST_GRAPH score=%d graph6=", final_bad);
    print_graph6();
    for (int i = 0; i < final_bad; i++)
        printf("BAD mask=0x%llx\n", (unsigned long long)bad_list[i]);
    return 0;
}
