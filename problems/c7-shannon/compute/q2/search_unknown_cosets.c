/* Finish the 8-coset leftovers: Cayley graphs C dumped as unknown.

   gcc -O3 -o q2/search_unknown_cosets q2/search_unknown_cosets.c
   ./q2/search_unknown_cosets q2/coset_unknown.conn
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define QN 343
#define BW 6
typedef uint64_t BS[BW];

static void bs_zero(BS a) { memset(a, 0, sizeof(BS)); }
static inline void bs_set(BS a, int i) { a[i >> 6] |= 1ull << (i & 63); }
static inline int bs_get(const BS a, int i) {
    return (int)((a[i >> 6] >> (i & 63)) & 1ull);
}
static inline void bs_andnot(BS a, const BS b) {
    for (int i = 0; i < BW; i++) a[i] &= ~b[i];
}
static inline int bs_count(const BS a) {
    int s = 0;
    for (int i = 0; i < BW; i++) s += __builtin_popcountll(a[i]);
    return s;
}
static inline int bs_first(const BS a) {
    for (int i = 0; i < BW; i++)
        if (a[i]) return i * 64 + __builtin_ctzll(a[i]);
    return -1;
}

static int add_cid(int i, int d) {
    int i0 = i / 49, i1 = (i / 7) % 7, i2 = i % 7;
    int d0 = d / 49, d1 = (d / 7) % 7, d2 = d % 7;
    return ((i0 + d0) % 7) * 49 + ((i1 + d1) % 7) * 7 + (i2 + d2) % 7;
}

static int color_ub(const BS *adj, const BS cand) {
    int color[QN];
    for (int i = 0; i < QN; i++) color[i] = -1;
    int ncolors = 0;
    BS left;
    memcpy(left, cand, sizeof(BS));
    while (1) {
        int v = bs_first(left);
        if (v < 0) break;
        uint8_t used[64];
        memset(used, 0, sizeof used);
        for (int u = 0; u < QN; u++) {
            if (u == v || !bs_get(cand, u) || color[u] < 0) continue;
            if (!bs_get(adj[v], u) && color[u] < 64) used[color[u]] = 1;
        }
        int c = 0;
        while (c < 64 && used[c]) c++;
        color[v] = c;
        if (c + 1 > ncolors) ncolors = c + 1;
        left[v >> 6] &= ~(1ull << (v & 63));
    }
    return ncolors;
}

static int rec_nodes, rec_cap;

static int rec(const BS *adj, BS cand, int sofar, int target) {
    if (sofar >= target) return 1;
    if (++rec_nodes > rec_cap) return -1;
    int rem = bs_count(cand);
    if (sofar + rem < target) return 0;
    if (rem == 0) return 0;
    int best_v = -1, best_d = -1;
    BS tmp;
    memcpy(tmp, cand, sizeof(BS));
    while (1) {
        int v = bs_first(tmp);
        if (v < 0) break;
        tmp[v >> 6] &= ~(1ull << (v & 63));
        int d = 0;
        for (int i = 0; i < BW; i++) d += __builtin_popcountll(cand[i] & adj[v][i]);
        if (d > best_d) {
            best_d = d;
            best_v = v;
        }
    }
    int v = best_v;
    BS next;
    memcpy(next, cand, sizeof(BS));
    next[v >> 6] &= ~(1ull << (v & 63));
    bs_andnot(next, adj[v]);
    int a = rec(adj, next, sofar + 1, target);
    if (a != 0) return a;
    cand[v >> 6] &= ~(1ull << (v & 63));
    return rec(adj, cand, sofar, target);
}

static int greedy(const BS *adj, unsigned *rng, const BS cand0) {
    int order[QN], n = 0;
    for (int i = 0; i < QN; i++)
        if (bs_get(cand0, i)) order[n++] = i;
    for (int i = n - 1; i > 0; i--) {
        *rng = *rng * 1664525u + 1013904223u;
        int j = (int)(*rng % (unsigned)(i + 1));
        int t = order[i];
        order[i] = order[j];
        order[j] = t;
    }
    uint8_t banned[QN];
    memset(banned, 0, sizeof banned);
    int take = 0;
    for (int t = 0; t < n; t++) {
        int v = order[t];
        if (banned[v]) continue;
        take++;
        banned[v] = 1;
        for (int u = 0; u < QN; u++)
            if (bs_get(adj[v], u)) banned[u] = 1;
    }
    return take;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "q2/coset_unknown.conn";
    FILE *f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "missing %s\n", path);
        return 1;
    }
    clock_t t0 = clock();
    char line[400];
    int n = 0, n_yes = 0, n_no = 0, n_unk = 0, n_color = 0, n_greedy = 0;
    unsigned rng = 1;
    BS adj[QN];
    while (fgets(line, sizeof line, f)) {
        if (line[0] != '0' && line[0] != '1') continue;
        if (strlen(line) < QN) continue;
        n++;
        uint8_t conn[QN];
        for (int i = 0; i < QN; i++) conn[i] = (uint8_t)(line[i] == '1');
        for (int i = 0; i < QN; i++) {
            bs_zero(adj[i]);
            for (int d = 0; d < QN; d++) {
                if (!conn[d] || d == 0) continue;
                bs_set(adj[i], add_cid(i, d));
            }
        }
        BS cand;
        memset(cand, 0, sizeof cand);
        for (int i = 0; i < QN; i++) {
            cand[i >> 6] |= 1ull << (i & 63);
        }
        cand[5] &= (1ull << 23) - 1;
        int ub = color_ub(adj, cand);
        if (ub < 8) {
            n_no++;
            n_color++;
            continue;
        }
        int bestg = 0;
        for (int t = 0; t < 40; t++) {
            int g = greedy(adj, &rng, cand);
            if (g > bestg) bestg = g;
        }
        if (bestg >= 8) {
            n_yes++;
            n_greedy++;
            printf("YES greedy line %d pack=%d\n", n, bestg);
            fflush(stdout);
            continue;
        }
        /* search 7 more in non-neighbourhood of 0 */
        cand[0] &= ~1ull;
        bs_andnot(cand, adj[0]);
        rec_nodes = 0;
        rec_cap = 400000;
        int r = rec(adj, cand, 1, 8);
        if (r == 1) {
            n_yes++;
            printf("YES rec line %d\n", n);
            fflush(stdout);
        } else if (r == 0) {
            n_no++;
        } else {
            n_unk++;
        }
        if (n % 200 == 0) {
            printf("  %d yes=%d no=%d color=%d unk=%d t=%.1fs\n", n, n_yes, n_no,
                   n_color, n_unk, (double)(clock() - t0) / CLOCKS_PER_SEC);
            fflush(stdout);
        }
    }
    fclose(f);
    printf("DONE n=%d yes=%d no=%d color_kill=%d greedy_hit=%d unk=%d t=%.1fs\n",
           n, n_yes, n_no, n_color, n_greedy, n_unk,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    return n_yes ? 0 : 0;
}
