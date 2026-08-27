/* Ejection from good 3-dimensional F7-codes (size 343, empty residual).

   Sample RREF generators, keep good codes, then delete-and-repack toward
   368. A 343-set is maximal, so every improvement deletes first.

   gcc -O3 -o q4/search_eject_linear q4/search_eject_linear.c
   ./q4/search_eject_linear
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807
#define DIM 5

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

static int is_good(const int a[5], const int b[5], const int c[5]) {
    for (int s = 0; s < 7; s++)
        for (int t = 0; t < 7; t++)
            for (int u = 0; u < 7; u++) {
                if (!(s | t | u)) continue;
                int small = 1;
                for (int i = 0; i < 5; i++) {
                    int x = (s * a[i] + t * b[i] + u * c[i]) % 7;
                    if (x > 1 && x < 6) {
                        small = 0;
                        break;
                    }
                }
                if (small) return 0;
            }
    return 1;
}

static void addv(int v, uint8_t *sel, int *blocked, int *S, int *nS) {
    sel[v] = 1;
    S[(*nS)++] = v;
    for (int k = 0; k < 243; k++) blocked[neigh[v][k]]++;
}

static void remv(int v, uint8_t *sel, int *blocked, int *S, int *nS) {
    sel[v] = 0;
    for (int i = 0; i < *nS; i++)
        if (S[i] == v) {
            S[i] = S[--(*nS)];
            break;
        }
    for (int k = 0; k < 243; k++) blocked[neigh[v][k]]--;
}

static void write_set(const char *path, const int *S, int n) {
    FILE *f = fopen(path, "w");
    if (!f) return;
    for (int i = 0; i < n; i++) {
        int v = S[i];
        fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                coord[v][3], coord[v][4]);
    }
    fclose(f);
    printf("wrote %s size=%d\n", path, n);
}

int main(void) {
    clock_t t0 = clock();
    fill_tables();
    unsigned rng = 7;
    int global_best = 343, n_good = 0, n_codes = 0;

    int pivots[10][3], np = 0;
    for (int i = 0; i < 5; i++)
        for (int j = i + 1; j < 5; j++)
            for (int k = j + 1; k < 5; k++) {
                pivots[np][0] = i;
                pivots[np][1] = j;
                pivots[np][2] = k;
                np++;
            }

    /* Sample 80 good codes: walk random RREF fills. */
    while (n_good < 80) {
        rng = rng * 1664525u + 1013904223u;
        int *pv = pivots[rng % 10];
        int a[5] = {0}, b[5] = {0}, c[5] = {0};
        a[pv[0]] = 1;
        b[pv[1]] = 1;
        c[pv[2]] = 1;
        for (int i = 0; i < 5; i++) {
            if (i > pv[0]) {
                rng = rng * 1664525u + 1013904223u;
                a[i] = (int)(rng % 7);
            }
            if (i > pv[1]) {
                rng = rng * 1664525u + 1013904223u;
                b[i] = (int)(rng % 7);
            }
            if (i > pv[2]) {
                rng = rng * 1664525u + 1013904223u;
                c[i] = (int)(rng % 7);
            }
        }
        n_codes++;
        if (!is_good(a, b, c)) continue;
        n_good++;

        int pts[343], npts = 0;
        for (int s = 0; s < 7; s++)
            for (int t = 0; t < 7; t++)
                for (int u = 0; u < 7; u++) {
                    int x[5];
                    for (int i = 0; i < 5; i++)
                        x[i] = (s * a[i] + t * b[i] + u * c[i]) % 7;
                    pts[npts++] = encode_coords(x);
                }

        uint8_t sel[NV];
        int blocked[NV];
        int S[NV], nS = 0;
        memset(sel, 0, sizeof sel);
        memset(blocked, 0, sizeof blocked);
        for (int i = 0; i < 343; i++) addv(pts[i], sel, blocked, S, &nS);

        int best = nS;
        for (int step = 0; step < 25000; step++) {
            int dropn = (step % 17 == 0) ? 12 : (step % 5 == 0) ? 6 : 1;
            if (dropn > nS) dropn = nS;
            int dropped[16];
            for (int i = 0; i < dropn; i++) {
                rng = rng * 1664525u + 1013904223u;
                dropped[i] = S[rng % (unsigned)nS];
                remv(dropped[i], sel, blocked, S, &nS);
            }
            int freed[1024], nf = 0;
            for (int u = 0; u < NV && nf < 1024; u++)
                if (blocked[u] == 0) freed[nf++] = u;
            for (int i = nf - 1; i > 0; i--) {
                rng = rng * 1664525u + 1013904223u;
                int j = (int)(rng % (unsigned)(i + 1));
                int tmp = freed[i];
                freed[i] = freed[j];
                freed[j] = tmp;
            }
            int packed[1024], npk = 0;
            uint8_t take[NV];
            memset(take, 0, sizeof take);
            for (int i = 0; i < nf; i++) {
                int u = freed[i];
                int ok = 1;
                for (int k = 0; k < 243; k++)
                    if (take[neigh[u][k]]) {
                        ok = 0;
                        break;
                    }
                if (ok) {
                    packed[npk++] = u;
                    take[u] = 1;
                }
            }
            if (npk >= dropn || npk + (nS) >= best - 2) {
                for (int i = 0; i < npk; i++) addv(packed[i], sel, blocked, S, &nS);
            } else {
                for (int i = 0; i < dropn; i++)
                    addv(dropped[i], sel, blocked, S, &nS);
            }
            if (nS > best) {
                best = nS;
                printf("code %d size=%d step=%d\n", n_good, nS, step);
                fflush(stdout);
                if (nS > global_best) {
                    global_best = nS;
                    if (nS >= 368) {
                        write_set("q4/R_eject_linear.txt", S, nS);
                        return 0;
                    }
                }
            }
        }
        if (n_good <= 3 || n_good % 10 == 0) {
            printf("  codes=%d tried=%d best=%d t=%.1fs\n", n_good, n_codes,
                   global_best, (double)(clock() - t0) / CLOCKS_PER_SEC);
            fflush(stdout);
        }
    }
    printf("DONE good=%d tried=%d best=%d t=%.2fs\n", n_good, n_codes, global_best,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
