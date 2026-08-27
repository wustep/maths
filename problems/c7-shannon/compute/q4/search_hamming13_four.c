/* Hamming-13 case C: add a 4-blocker, remove its 4 blockers plus two extras.

   q3 finished 6-blocker and 5-blocker+1 extra (freed α≤4). This is the
   next split. Leftover after this file is add-only ≤3-blocker vertices.

   gcc -O3 -o q4/search_hamming13_four q4/search_hamming13_four.c
   ./q4/search_hamming13_four ../R367.txt
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807
#define DIM 5
#define SEEDN 367

static int coord[NV][DIM];
static int neigh[NV][243];
static int seed[SEEDN];
static int in_seed[NV];
static int nblock[NV];
static int block_list[NV][16];
static int n_by_nb[16];
static int *by_nb[16];

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
        int n = 0, o0, o1, o2, o3, o4;
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

static int alpha_atleast(const int *verts, int n, int target) {
    if (n < target) return 0;
    int take = 0;
    uint8_t used[64];
    if (n > 40) {
        uint8_t *big = calloc((size_t)n, 1);
        for (int i = 0; i < n; i++) {
            if (big[i]) continue;
            take++;
            for (int j = i + 1; j < n; j++)
                if (!big[j] && adj_uv(verts[i], verts[j])) big[j] = 1;
            big[i] = 1;
        }
        free(big);
        return take >= target;
    }
    memset(used, 0, (size_t)n);
    for (int i = 0; i < n; i++) {
        if (used[i]) continue;
        take++;
        for (int j = i + 1; j < n; j++)
            if (!used[j] && adj_uv(verts[i], verts[j])) used[j] = 1;
        used[i] = 1;
    }
    if (take >= target) return 1;

    uint64_t neighm[40];
    memset(neighm, 0, sizeof neighm);
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (adj_uv(verts[i], verts[j])) {
                neighm[i] |= 1ull << j;
                neighm[j] |= 1ull << i;
            }
    int best = take, nodes = 0, hit = 0;
    uint64_t full = (1ull << n) - 1;
    void rec(uint64_t cand, int sofar) {
        if (hit || ++nodes > 150000) return;
        if (sofar >= target) {
            hit = 1;
            return;
        }
        if (sofar + __builtin_popcountll(cand) < target) return;
        if (!cand) {
            if (sofar > best) best = sofar;
            return;
        }
        int v = __builtin_ctzll(cand);
        rec(cand & ~neighm[v] & ~(1ull << v), sofar + 1);
        rec(cand & ~(1ull << v), sofar);
    }
    rec(full, 0);
    return hit || best >= target;
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
    for (int i = 0; i < SEEDN; i++) in_seed[seed[i]] = 1;
    memset(nblock, 0, sizeof nblock);
    for (int i = 0; i < SEEDN; i++) {
        for (int k = 0; k < 243; k++) {
            int u = neigh[seed[i]][k];
            if (in_seed[u]) continue;
            if (nblock[u] < 16) block_list[u][nblock[u]++] = i;
        }
    }
    memset(n_by_nb, 0, sizeof n_by_nb);
    for (int v = 0; v < NV; v++) {
        if (in_seed[v]) continue;
        if (nblock[v] < 16) n_by_nb[nblock[v]]++;
    }
    printf("blocker_hist");
    for (int nb = 0; nb < 16; nb++) printf(" %d:%d", nb, n_by_nb[nb]);
    printf("\n");
    for (int nb = 0; nb < 16; nb++) {
        by_nb[nb] = malloc(sizeof(int) * (n_by_nb[nb] + 1));
        n_by_nb[nb] = 0;
    }
    for (int v = 0; v < NV; v++) {
        if (in_seed[v]) continue;
        int nb = nblock[v];
        if (nb < 16) by_nb[nb][n_by_nb[nb]++] = v;
    }

    int max_freed = 0, nC = 0, hit = 0, best_alpha = 0;
    int n4 = n_by_nb[4];
    printf("caseC 4-blockers=%d\n", n4);
    fflush(stdout);

    int L[SEEDN][8], nL[SEEDN];
    static int nP[SEEDN][SEEDN];
    static int P[SEEDN][SEEDN][4];

    for (int t = 0; t < n4; t++) {
        int v = by_nb[4][t];
        uint8_t inB[SEEDN];
        memset(inB, 0, sizeof inB);
        for (int i = 0; i < nblock[v]; i++) inB[block_list[v][i]] = 1;

        int base[64], nbase = 0;
        memset(nL, 0, sizeof nL);
        memset(nP, 0, sizeof nP);
        for (int nb = 1; nb <= 4; nb++) {
            for (int s = 0; s < n_by_nb[nb]; s++) {
                int u = by_nb[nb][s];
                int extras[4], ne = 0, ok = 1;
                for (int i = 0; i < nblock[u]; i++) {
                    int b = block_list[u][i];
                    if (inB[b]) continue;
                    if (ne < 4) extras[ne++] = b;
                    else {
                        ok = 0;
                        break;
                    }
                }
                if (!ok) continue;
                if (ne == 0) {
                    if (nbase < 64) base[nbase++] = u;
                } else if (ne == 1) {
                    int e = extras[0];
                    if (nL[e] < 8) L[e][nL[e]++] = u;
                } else if (ne == 2) {
                    int a = extras[0], b = extras[1];
                    if (a > b) {
                        int tmp = a;
                        a = b;
                        b = tmp;
                    }
                    if (nP[a][b] < 4) P[a][b][nP[a][b]++] = u;
                }
            }
        }

        for (int e1 = 0; e1 < SEEDN; e1++) {
            if (inB[e1]) continue;
            for (int e2 = e1 + 1; e2 < SEEDN; e2++) {
                if (inB[e2]) continue;
                int nf = nbase + nL[e1] + nL[e2] + nP[e1][e2];
                nC++;
                if (nf > max_freed) max_freed = nf;
                if (nf < 7) continue;
                int freed[64], m = 0;
                memcpy(freed, base, (size_t)nbase * sizeof(int));
                m = nbase;
                for (int i = 0; i < nL[e1]; i++) freed[m++] = L[e1][i];
                for (int i = 0; i < nL[e2]; i++) freed[m++] = L[e2][i];
                for (int i = 0; i < nP[e1][e2]; i++) freed[m++] = P[e1][e2][i];
                if (alpha_atleast(freed, m, 7)) {
                    printf("CASE_C HIT v=%d e1=%d e2=%d freed=%d\n", v, e1, e2,
                           m);
                    hit = 1;
                    int kept[SEEDN], nk = 0;
                    for (int i = 0; i < SEEDN; i++)
                        if (!inB[i] && i != e1 && i != e2) kept[nk++] = seed[i];
                    write_set("q4/R_hamming13_four.txt", kept, nk, freed, m);
                    goto done;
                }
                if (m > best_alpha) best_alpha = m;
            }
        }
        if ((t + 1) % 20 == 0) {
            printf("  caseC %d/%d pairs=%d max_freed=%d t=%.1fs\n", t + 1, n4, nC,
                   max_freed, (double)(clock() - t0) / CLOCKS_PER_SEC);
            fflush(stdout);
        }
    }
done:
    printf("caseC n=%d max_freed=%d hit=%d t=%.2fs\n", nC, max_freed, hit,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    if (!hit)
        printf("no 368 in Hamming-13 case C (added vertex with 4 blockers)\n");
    (void)best_alpha;
    return 0;
}
