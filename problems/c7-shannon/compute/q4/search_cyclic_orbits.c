/* Pack cyclic-coordinate 5-orbits.

   The map (a,b,c,d,e) |-> (b,c,d,e,a) partitions all but the 7 constant
   words into 3360 orbits of size 5. Seventy-four independent orbits are
   370 vertices. Seventy-three plus {00000,22222,44444} are 368.

   gcc -O3 -o q4/search_cyclic_orbits q4/search_cyclic_orbits.c
   ./q4/search_cyclic_orbits
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807
#define NORB 3360
#define GREEDY_TRIALS 200
#define BW 53

typedef uint64_t BS[BW];

static int coord[NV][5];
static int neigh[NV][243];
static int orbit_of[NV];
static int orbit_min[NORB];
static int n_orb;
static int constants[7];

static int encode_c(const int c[5]) {
    return ((((c[0] * 7 + c[1]) * 7 + c[2]) * 7 + c[3]) * 7 + c[4]);
}

static int rotate_v(int v) {
    int c[5] = {coord[v][1], coord[v][2], coord[v][3], coord[v][4], coord[v][0]};
    return encode_c(c);
}

static void fill_tables(void) {
    int cube[243][5], n = 0;
    for (int o0 = -1; o0 <= 1; o0++)
        for (int o1 = -1; o1 <= 1; o1++)
            for (int o2 = -1; o2 <= 1; o2++)
                for (int o3 = -1; o3 <= 1; o3++)
                    for (int o4 = -1; o4 <= 1; o4++) {
                        cube[n][0] = o0;
                        cube[n][1] = o1;
                        cube[n][2] = o2;
                        cube[n][3] = o3;
                        cube[n][4] = o4;
                        n++;
                    }
    for (int v = 0; v < NV; v++) {
        int x = v;
        for (int i = 4; i >= 0; i--) {
            coord[v][i] = x % 7;
            x /= 7;
        }
        for (int t = 0; t < 243; t++) {
            int c[5];
            for (int i = 0; i < 5; i++)
                c[i] = (coord[v][i] + cube[t][i] + 7) % 7;
            neigh[v][t] = encode_c(c);
        }
    }
    memset(orbit_of, -1, sizeof orbit_of);
    n_orb = 0;
    int nc = 0;
    for (int v = 0; v < NV; v++) {
        int eq = 1;
        for (int i = 1; i < 5; i++)
            if (coord[v][i] != coord[v][0]) eq = 0;
        if (eq) {
            constants[nc++] = v;
            continue;
        }
        if (orbit_of[v] >= 0) continue;
        int w = v, mn = v;
        for (int t = 0; t < 5; t++) {
            if (w < mn) mn = w;
            w = rotate_v(w);
        }
        int id = n_orb++;
        orbit_min[id] = mn;
        w = v;
        for (int t = 0; t < 5; t++) {
            orbit_of[w] = id;
            w = rotate_v(w);
        }
    }
}

static void bs_zero(BS a) { memset(a, 0, sizeof(BS)); }
static inline void bs_set(BS a, int i) { a[i >> 6] |= 1ull << (i & 63); }
static inline int bs_get(const BS a, int i) {
    return (int)((a[i >> 6] >> (i & 63)) & 1ull);
}
static inline void bs_andnot(BS a, const BS b) {
    for (int i = 0; i < BW; i++) a[i] &= ~b[i];
}
static void bs_fill_norb(BS a) {
    bs_zero(a);
    for (int i = 0; i < NORB; i++) bs_set(a, i);
}

static void write_orbits(const char *path, const int *ids, int n, int with_const) {
    FILE *f = fopen(path, "w");
    if (!f) return;
    int count = 0;
    if (with_const) {
        int cs[3] = {0, 2, 4};
        for (int t = 0; t < 3; t++) {
            int v = constants[cs[t]];
            fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                    coord[v][3], coord[v][4]);
            count++;
        }
    }
    for (int i = 0; i < n; i++) {
        int w = orbit_min[ids[i]];
        for (int t = 0; t < 5; t++) {
            fprintf(f, "%d %d %d %d %d\n", coord[w][0], coord[w][1], coord[w][2],
                    coord[w][3], coord[w][4]);
            count++;
            w = rotate_v(w);
        }
    }
    fclose(f);
    printf("wrote %s size=%d\n", path, count);
}

int main(void) {
    clock_t t0 = clock();
    fill_tables();
    printf("n_orb=%d constants=%d %d %d %d %d %d %d\n", n_orb, constants[0],
           constants[1], constants[2], constants[3], constants[4], constants[5],
           constants[6]);
    if (n_orb != NORB) {
        fprintf(stderr, "orbit count %d != %d\n", n_orb, NORB);
        return 1;
    }

    BS *adj = (BS *)malloc(sizeof(BS) * NORB);
    if (!adj) return 1;
    for (int i = 0; i < NORB; i++) bs_zero(adj[i]);
    int self_bad = 0;
    for (int v = 0; v < NV; v++) {
        int a = orbit_of[v];
        if (a < 0) continue;
        for (int k = 0; k < 243; k++) {
            int u = neigh[v][k];
            if (u == v) continue;
            int b = orbit_of[u];
            if (b < 0) continue;
            if (a == b)
                self_bad++;
            else {
                bs_set(adj[a], b);
                bs_set(adj[b], a);
            }
        }
    }
    /* An internally adjacent 5-orbit cannot be used. */
    int alive[NORB];
    int n_alive = 0;
    memset(alive, 1, sizeof alive);
    for (int v = 0; v < NV; v++) {
        int a = orbit_of[v];
        if (a < 0) continue;
        for (int k = 0; k < 243; k++) {
            int u = neigh[v][k];
            if (u == v) continue;
            if (orbit_of[u] == a) alive[a] = 0;
        }
    }
    for (int i = 0; i < NORB; i++)
        if (alive[i]) n_alive++;
    printf("internally_independent_orbits=%d self_adj_pairs=%d\n", n_alive,
           self_bad);

    /* Constants 00000,22222,44444: drop orbits that meet their cubes. */
    uint8_t blocked_c[NV];
    memset(blocked_c, 0, sizeof blocked_c);
    int cs[3] = {constants[0], constants[2], constants[4]};
    for (int t = 0; t < 3; t++)
        for (int k = 0; k < 243; k++) blocked_c[neigh[cs[t]][k]] = 1;
    int alive_c[NORB];
    int n_alive_c = 0;
    memcpy(alive_c, alive, sizeof alive);
    for (int i = 0; i < NORB; i++) {
        if (!alive_c[i]) continue;
        int w = orbit_min[i], hit = 0;
        for (int t = 0; t < 5; t++) {
            if (blocked_c[w]) hit = 1;
            w = rotate_v(w);
        }
        if (hit) alive_c[i] = 0;
        else n_alive_c++;
    }
    printf("orbits_free_of_024=%d\n", n_alive_c);

    unsigned rng = 1;
    int best = 0, bestS[NORB], bestn = 0;
    int bestc = 0, bestcS[NORB], bestcn = 0;
    int order[NORB];
    for (int trial = 0; trial < GREEDY_TRIALS; trial++) {
        for (int i = 0; i < NORB; i++) order[i] = i;
        for (int i = NORB - 1; i > 0; i--) {
            rng = rng * 1664525u + 1013904223u;
            int j = (int)(rng % (unsigned)(i + 1));
            int tmp = order[i];
            order[i] = order[j];
            order[j] = tmp;
        }
        BS left;
        bs_fill_norb(left);
        for (int i = 0; i < NORB; i++)
            if (!alive[i]) left[i >> 6] &= ~(1ull << (i & 63));
        int S[NORB], n = 0;
        for (int t = 0; t < NORB; t++) {
            int v = order[t];
            if (!bs_get(left, v)) continue;
            S[n++] = v;
            left[v >> 6] &= ~(1ull << (v & 63));
            bs_andnot(left, adj[v]);
        }
        if (n > best) {
            best = n;
            bestn = n;
            memcpy(bestS, S, (size_t)n * sizeof(int));
            printf("greedy orbits=%d size=%d trial=%d\n", n, n * 5, trial);
            fflush(stdout);
        }

        bs_fill_norb(left);
        for (int i = 0; i < NORB; i++)
            if (!alive_c[i]) left[i >> 6] &= ~(1ull << (i & 63));
        n = 0;
        for (int t = 0; t < NORB; t++) {
            int v = order[t];
            if (!bs_get(left, v)) continue;
            S[n++] = v;
            left[v >> 6] &= ~(1ull << (v & 63));
            bs_andnot(left, adj[v]);
        }
        if (n > bestc) {
            bestc = n;
            bestcn = n;
            memcpy(bestcS, S, (size_t)n * sizeof(int));
            printf("greedy+024 orbits=%d total=%d trial=%d\n", n, n * 5 + 3,
                   trial);
            fflush(stdout);
        }
    }

    if (best * 5 >= 368) write_orbits("q4/R_cyclic.txt", bestS, bestn, 0);
    if (bestc * 5 + 3 >= 368)
        write_orbits("q4/R_cyclic024.txt", bestcS, bestcn, 1);

    FILE *df = fopen("q4/cyclic_orbits.adj", "w");
    if (df) {
        fprintf(df, "%d\n", NORB);
        for (int i = 0; i < NORB; i++) {
            fprintf(df, "%d %d", i, alive[i]);
            for (int j = i + 1; j < NORB; j++)
                if (bs_get(adj[i], j)) fprintf(df, " %d", j);
            fprintf(df, "\n");
        }
        fclose(df);
    }

    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE best_orbits=%d best_size=%d best024_orbits=%d best024_total=%d "
           "t=%.2fs\n",
           best, best * 5, bestc, bestc * 5 + 3, sec);
    free(adj);
    return 0;
}
