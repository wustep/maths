/* Pack cosets of a good 2-dimensional F7-subspace (shape 4).

   Assign each of the 16807 vertices a coset id in 0..342. Two cosets
   are adjacent if any strong-product edge crosses them. Greedy MIS of
   that 343-vertex graph; 8 cosets would be 392 vertices.

   gcc -O3 -o q1/search_cosets q1/search_cosets.c
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define N 7
#define DIM 5
#define NV 16807
#define QN 343

static int coord[NV][DIM];
static int neigh[NV][243];

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

static int is_good(const int a[DIM], const int b[DIM]) {
    for (int s = 0; s < 7; s++)
        for (int t = 0; t < 7; t++) {
            if (s == 0 && t == 0) continue;
            int ok_small = 1;
            for (int i = 0; i < DIM; i++) {
                int x = (s * a[i] + t * b[i]) % 7;
                if (x > 1 && x < 6) {
                    ok_small = 0;
                    break;
                }
            }
            if (ok_small) return 0;
        }
    return 1;
}

static int greedy_mis(int n, const uint32_t *adj, unsigned rng, int *taken) {
    int order[QN];
    for (int i = 0; i < n; i++) order[i] = i;
    for (int i = n - 1; i > 0; i--) {
        rng = rng * 1664525u + 1013904223u;
        int j = (int)(rng % (unsigned)(i + 1));
        int tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }
    uint8_t banned[QN];
    memset(banned, 0, n);
    int nt = 0;
    for (int t = 0; t < n; t++) {
        int v = order[t];
        if (banned[v]) continue;
        taken[nt++] = v;
        const uint32_t *row = adj + v * ((n + 31) / 32);
        for (int u = 0; u < n; u++)
            if (row[u >> 5] & (1u << (u & 31))) banned[u] = 1;
        banned[v] = 1;
    }
    return nt;
}

int main(void) {
    fill_tables();
    int best = 0, n_good = 0, checked = 0;
    int cid[NV];
    uint32_t adj[QN * ((QN + 31) / 32)];
    int words[8 * 49];
    FILE *hitf = NULL;

    for (int p0 = 0; p0 < 5; p0++)
    for (int p1 = p0 + 1; p1 < 5; p1++) {
        int free_idx[3], nf = 0;
        for (int j = 0; j < 5; j++)
            if (j != p0 && j != p1) free_idx[nf++] = j;
        int nfill = 7 * 7 * 7 * 7 * 7 * 7;
        for (int code = 0; code < nfill; code++) {
            int x = code;
            int fill[6];
            for (int k = 0; k < 6; k++) {
                fill[k] = x % 7;
                x /= 7;
            }
            int a[DIM] = {0}, b[DIM] = {0};
            a[p0] = 1;
            b[p1] = 1;
            a[free_idx[0]] = fill[0];
            a[free_idx[1]] = fill[1];
            a[free_idx[2]] = fill[2];
            b[free_idx[0]] = fill[3];
            b[free_idx[1]] = fill[4];
            b[free_idx[2]] = fill[5];
            checked++;
            if (!is_good(a, b)) {
                if (checked % 200000 == 0)
                    printf("checked=%d good=%d best=%d\n", checked, n_good, best), fflush(stdout);
                continue;
            }
            n_good++;
            /* coset id: solve x = s a + t b + w, use the two pivot coords as (s,t)
               and pack the three free coords. For RREF with pivots p0<p1 this is
               exactly the remaining three coordinates, but only after subtracting
               the V-component. cid = 49*x[f0]+7*x[f1]+x[f2] after clearing pivots. */
            for (int v = 0; v < NV; v++) {
                int c[DIM];
                for (int i = 0; i < DIM; i++) c[i] = coord[v][i];
                int s = c[p0];
                for (int i = 0; i < DIM; i++) c[i] = (c[i] - s * a[i] % 7 + 14) % 7;
                int t = c[p1];
                for (int i = 0; i < DIM; i++) c[i] = (c[i] - t * b[i] % 7 + 14) % 7;
                cid[v] = c[free_idx[0]] * 49 + c[free_idx[1]] * 7 + c[free_idx[2]];
            }
            memset(adj, 0, sizeof adj);
            int roww = (QN + 31) / 32;
            for (int v = 0; v < NV; v++) {
                int i = cid[v];
                for (int k = 0; k < 243; k++) {
                    int u = neigh[v][k];
                    if (u == v) continue;
                    int j = cid[u];
                    if (i == j) continue;
                    adj[i * roww + (j >> 5)] |= 1u << (j & 31);
                    adj[j * roww + (i >> 5)] |= 1u << (i & 31);
                }
            }
            int local = 0, best_taken[QN];
            for (int trial = 0; trial < 16; trial++) {
                int taken[QN];
                int pack = greedy_mis(QN, adj, 1u + (unsigned)n_good * 31u + (unsigned)trial * 7u,
                                      taken);
                if (pack > local) {
                    local = pack;
                    memcpy(best_taken, taken, pack * sizeof(int));
                }
            }
            if (local > best) {
                best = local;
                printf("good #%d pivots %d%d V=(%d%d%d%d%d/%d%d%d%d%d) cosets=%d total=%d\n",
                       n_good, p0, p1, a[0], a[1], a[2], a[3], a[4], b[0], b[1], b[2], b[3],
                       b[4], local, 49 * local);
                fflush(stdout);
            }
            if (local >= 8 && !hitf) {
                /* materialise union of the packed cosets */
                uint8_t keep[QN];
                memset(keep, 0, sizeof keep);
                for (int i = 0; i < local; i++) keep[best_taken[i]] = 1;
                int nw = 0;
                for (int v = 0; v < NV; v++)
                    if (keep[cid[v]]) {
                        if (nw < 8 * 49) words[nw] = v;
                        nw++;
                    }
                printf("materialised %d verts (expect %d)\n", nw, 49 * local);
                if (nw >= 368) {
                    hitf = fopen("q1/R_cosets.txt", "w");
                    if (hitf) {
                        for (int i = 0; i < nw; i++) {
                            int v = words[i];
                            /* words buffer may be too small if local>8 */
                        }
                        fclose(hitf);
                        hitf = NULL;
                    }
                    /* write all kept vertices */
                    hitf = fopen("q1/R_cosets.txt", "w");
                    int wrote = 0;
                    for (int v = 0; v < NV; v++)
                        if (keep[cid[v]]) {
                            fprintf(hitf, "%d %d %d %d %d\n", coord[v][0], coord[v][1],
                                    coord[v][2], coord[v][3], coord[v][4]);
                            wrote++;
                        }
                    fclose(hitf);
                    printf("wrote q1/R_cosets.txt size=%d\n", wrote);
                    hitf = (FILE *)1; /* don't rewrite */
                }
            }
            if (n_good <= 5 || n_good % 50 == 0) {
                printf("  good=%d checked=%d best_cosets=%d\n", n_good, checked, best);
                fflush(stdout);
            }
        }
    }
    printf("DONE checked=%d good=%d best_cosets=%d best_total=%d\n", checked, n_good, best,
           49 * best);
    return 0;
}
