/* Hamming distance 11 around the 367-set (5-out / 6-in).

   q1 SAT finished every odd distance ≤ 9 and timed out at r=5.
   Split on the added vertices' blocker numbers:

   A. At least one added vertex has 5 blockers. The removal set is that
      vertex's blocker 5-set. 3712 determined cases, exact MIS on the
      freed graph. Complete.
   B. At least one added vertex has 4 blockers, none has 5. Removal is
      those 4 plus one extra seed vertex. ~1.1e6 cases. Complete.
   C. Every added vertex has ≤ 3 blockers: left to SAT
      (search_hamming11_sat.py). Residue if that SAT times out.

   gcc -O3 -o q2/search_hamming11 q2/search_hamming11.c
   ./q2/search_hamming11 R367.txt
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define NV 16807
#define DIM 5
#define SEEDN 367

static int coord[NV][DIM];
static int neigh[NV][243];
static int seed[SEEDN];
static int in_seed[NV];
static int seed_index[NV];
static int nblock[NV];
static int block_list[NV][12];
static int n_by_nb[12];
static int *by_nb[12];

static int encode_coords(const int c[DIM]) {
    int v = 0;
    for (int i = 0; i < DIM; i++) v = v * 7 + c[i];
    return v;
}

static void fill_tables(void) {
    for (int v = 0; v < NV; v++) {
        int x = v;
        for (int i = DIM - 1; i >= 0; i--) {
            coord[v][i] = x % 7;
            x /= 7;
        }
        int n = 0;
        int o0, o1, o2, o3, o4;
        for (o0 = -1; o0 <= 1; o0++)
        for (o1 = -1; o1 <= 1; o1++)
        for (o2 = -1; o2 <= 1; o2++)
        for (o3 = -1; o3 <= 1; o3++)
        for (o4 = -1; o4 <= 1; o4++) {
            int c[DIM];
            c[0] = (coord[v][0] + o0 + 7) % 7;
            c[1] = (coord[v][1] + o1 + 7) % 7;
            c[2] = (coord[v][2] + o2 + 7) % 7;
            c[3] = (coord[v][3] + o3 + 7) % 7;
            c[4] = (coord[v][4] + o4 + 7) % 7;
            neigh[v][n++] = encode_coords(c);
        }
    }
}

static int load_seed(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    int n = 0;
    char line[256];
    while (fgets(line, sizeof line, f)) {
        int c[5];
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\0' || *p == '\n') continue;
        if (p[0] >= '0' && p[0] <= '6' && p[1] >= '0' && p[1] <= '6') {
            for (int i = 0; i < 5; i++) c[i] = p[i] - '0';
        } else {
            for (int i = 0; i < 5; i++) {
                int x, cons = 0;
                if (sscanf(p, "%d%n", &x, &cons) != 1) {
                    fclose(f);
                    return -1;
                }
                c[i] = x;
                p += cons;
            }
        }
        seed[n++] = encode_coords(c);
    }
    fclose(f);
    return n;
}

static int adj_uv(int u, int v) {
    if (u == v) return 0;
    for (int i = 0; i < 5; i++) {
        int d = coord[u][i] - coord[v][i];
        if (d < 0) d = -d;
        if (d > 3) d = 7 - d;
        if (d > 1) return 0;
    }
    return 1;
}

static int exact_mis(const int *verts, int n) {
    if (n <= 0) return 0;
    if (n > 64) {
        int take = 0;
        uint8_t used[256];
        memset(used, 0, (size_t)n);
        for (int i = 0; i < n; i++) {
            if (used[i]) continue;
            take++;
            for (int j = i + 1; j < n; j++)
                if (!used[j] && adj_uv(verts[i], verts[j])) used[j] = 1;
            used[i] = 1;
        }
        return take;
    }
    uint64_t neighm[64];
    memset(neighm, 0, sizeof neighm);
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (adj_uv(verts[i], verts[j])) {
                neighm[i] |= 1ull << j;
                neighm[j] |= 1ull << i;
            }
    int best = 0;
    int nodes = 0;
    uint64_t full = (n == 64) ? ~0ull : ((1ull << n) - 1);
    /* iterative-style recursion via gcc nested function */
    void rec(uint64_t cand, int sofar) {
        if (++nodes > 400000) return;
        if (sofar + __builtin_popcountll(cand) <= best) return;
        if (cand == 0) {
            if (sofar > best) best = sofar;
            return;
        }
        int v = __builtin_ctzll(cand);
        rec(cand & ~neighm[v] & ~(1ull << v), sofar + 1);
        rec(cand & ~(1ull << v), sofar);
    }
    rec(full, 0);
    return best;
}

static int subset_of(int v, const uint8_t *inR) {
    for (int i = 0; i < nblock[v]; i++)
        if (!inR[block_list[v][i]]) return 0;
    return 1;
}

static void collect_freed(const uint8_t *inR, int *out, int *n) {
    int m = 0;
    for (int nb = 1; nb <= 5; nb++) {
        for (int t = 0; t < n_by_nb[nb]; t++) {
            int v = by_nb[nb][t];
            if (subset_of(v, inR)) out[m++] = v;
        }
    }
    *n = m;
}

static void write_set(const char *path, const int *kept, int nk, const int *add,
                      int na) {
    FILE *f = fopen(path, "w");
    if (!f) return;
    for (int i = 0; i < nk; i++) {
        int v = kept[i];
        fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                coord[v][3], coord[v][4]);
    }
    for (int i = 0; i < na; i++) {
        int v = add[i];
        fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                coord[v][3], coord[v][4]);
    }
    fclose(f);
    printf("wrote %s size=%d\n", path, nk + na);
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "R367.txt";
    clock_t t0 = clock();
    fill_tables();
    int n0 = load_seed(path);
    if (n0 != SEEDN) {
        fprintf(stderr, "bad seed n=%d\n", n0);
        return 1;
    }
    memset(in_seed, 0, sizeof in_seed);
    memset(seed_index, -1, sizeof seed_index);
    for (int i = 0; i < SEEDN; i++) {
        in_seed[seed[i]] = 1;
        seed_index[seed[i]] = i;
    }
    memset(nblock, 0, sizeof nblock);
    for (int i = 0; i < SEEDN; i++) {
        for (int k = 0; k < 243; k++) {
            int u = neigh[seed[i]][k];
            if (in_seed[u]) continue;
            if (nblock[u] < 12) block_list[u][nblock[u]++] = i;
        }
    }
    memset(n_by_nb, 0, sizeof n_by_nb);
    for (int v = 0; v < NV; v++) {
        if (in_seed[v]) continue;
        int nb = nblock[v];
        if (nb >= 0 && nb < 12) n_by_nb[nb]++;
    }
    printf("blocker_hist");
    for (int nb = 0; nb < 12; nb++) printf(" %d:%d", nb, n_by_nb[nb]);
    printf("\n");
    for (int nb = 0; nb < 12; nb++) {
        by_nb[nb] = malloc(sizeof(int) * (n_by_nb[nb] + 1));
        n_by_nb[nb] = 0;
    }
    for (int v = 0; v < NV; v++) {
        if (in_seed[v]) continue;
        int nb = nblock[v];
        if (nb >= 0 && nb < 12) by_nb[nb][n_by_nb[nb]++] = v;
    }

    int best_mis = 0, best_freed = 0, nA = 0, nB = 0, hit = 0;
    int freed[4096];

    /* Case A: each 5-blocker vertex determines R */
    for (int t = 0; t < n_by_nb[5]; t++) {
        int v = by_nb[5][t];
        uint8_t inR[SEEDN];
        memset(inR, 0, sizeof inR);
        for (int i = 0; i < nblock[v]; i++) inR[block_list[v][i]] = 1;
        int nf = 0;
        collect_freed(inR, freed, &nf);
        int a = exact_mis(freed, nf);
        if (a > best_mis) best_mis = a;
        if (nf > best_freed) best_freed = nf;
        nA++;
        if (a >= 6) {
            printf("CASE_A HIT v=%d freed=%d alpha=%d\n", v, nf, a);
            hit = 1;
            break;
        }
    }
    printf("caseA n=%d best_mis=%d max_freed=%d t=%.2fs\n", nA, best_mis,
           best_freed, (double)(clock() - t0) / CLOCKS_PER_SEC);
    fflush(stdout);

    int best_mis_B = 0, max_freed_B = 0;
    if (!hit) {
        int base_freed[4096];
        for (int t = 0; t < n_by_nb[4]; t++) {
            int v = by_nb[4][t];
            uint8_t baseR[SEEDN];
            memset(baseR, 0, sizeof baseR);
            for (int i = 0; i < nblock[v]; i++) baseR[block_list[v][i]] = 1;
            int nbase = 0;
            collect_freed(baseR, base_freed, &nbase);
            for (int e = 0; e < SEEDN; e++) {
                if (baseR[e]) continue;
                int nf = nbase;
                memcpy(freed, base_freed, (size_t)nbase * sizeof(int));
                /* vertices newly freed by also deleting seed e */
                for (int k = 0; k < 243; k++) {
                    int u = neigh[seed[e]][k];
                    if (in_seed[u]) continue;
                    if (nblock[u] > 5) continue;
                    int ok = 1, uses_e = 0;
                    for (int i = 0; i < nblock[u]; i++) {
                        int b = block_list[u][i];
                        if (b == e) uses_e = 1;
                        else if (!baseR[b]) {
                            ok = 0;
                            break;
                        }
                    }
                    if (ok && uses_e) {
                        if (nf < 4096) freed[nf++] = u;
                    }
                }
                int a = exact_mis(freed, nf);
                if (a > best_mis_B) best_mis_B = a;
                if (nf > max_freed_B) max_freed_B = nf;
                nB++;
                if (a >= 6) {
                    printf("CASE_B HIT v=%d extra=%d freed=%d alpha=%d\n", v, e, nf,
                           a);
                    hit = 1;
                    goto done;
                }
            }
            if ((t + 1) % 400 == 0) {
                printf("  caseB %d/%d best_mis=%d max_freed=%d t=%.1fs\n", t + 1,
                       n_by_nb[4], best_mis_B, max_freed_B,
                       (double)(clock() - t0) / CLOCKS_PER_SEC);
                fflush(stdout);
            }
        }
    }
done:
    printf("caseB n=%d best_mis=%d max_freed=%d\n", nB, best_mis_B, max_freed_B);
    printf("DONE hit=%d caseA_best=%d caseB_best=%d t=%.2fs\n", hit, best_mis,
           best_mis_B, (double)(clock() - t0) / CLOCKS_PER_SEC);
    if (!hit)
        printf("no 368 in Hamming-11 cases A+B (added vertex with 4 or 5 "
               "blockers)\n");
    return 0;
}
