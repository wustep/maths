/* From-scratch GRASP on C7^{box5}, not seeded by the 367-set.

   Random-order greedy, then 1-out / k-out ejection. Writes a set iff
   size >= 368.

   gcc -O3 -o q4/search_scratch q4/search_scratch.c
   ./q4/search_scratch
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807

static int coord[NV][5];
static int neigh[NV][243];

static int encode_coords(const int c[5]) {
    int v = 0;
    for (int i = 0; i < 5; i++) v = v * 7 + c[i];
    return v;
}

static void fill_tables(void) {
    for (int v = 0; v < NV; v++) {
        int x = v;
        for (int i = 4; i >= 0; i--) {
            coord[v][i] = x % 7;
            x /= 7;
        }
        int n = 0, o0, o1, o2, o3, o4;
        for (o0 = -1; o0 <= 1; o0++)
            for (o1 = -1; o1 <= 1; o1++)
                for (o2 = -1; o2 <= 1; o2++)
                    for (o3 = -1; o3 <= 1; o3++)
                        for (o4 = -1; o4 <= 1; o4++) {
                            int c[5];
                            c[0] = (coord[v][0] + o0 + 7) % 7;
                            c[1] = (coord[v][1] + o1 + 7) % 7;
                            c[2] = (coord[v][2] + o2 + 7) % 7;
                            c[3] = (coord[v][3] + o3 + 7) % 7;
                            c[4] = (coord[v][4] + o4 + 7) % 7;
                            neigh[v][n++] = encode_coords(c);
                        }
    }
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

int main(int argc, char **argv) {
    int restarts = argc > 1 ? atoi(argv[1]) : 40;
    int steps = argc > 2 ? atoi(argv[2]) : 20000;
    clock_t t0 = clock();
    fill_tables();
    unsigned rng = 1234567u;
    int global_best = 0;

    int order[NV];
    for (int v = 0; v < NV; v++) order[v] = v;

    for (int r = 0; r < restarts; r++) {
        for (int i = NV - 1; i > 0; i--) {
            rng = rng * 1664525u + 1013904223u;
            int j = (int)(rng % (unsigned)(i + 1));
            int tmp = order[i];
            order[i] = order[j];
            order[j] = tmp;
        }
        uint8_t sel[NV];
        int blocked[NV];
        int S[NV], nS = 0;
        memset(sel, 0, sizeof sel);
        memset(blocked, 0, sizeof blocked);
        for (int i = 0; i < NV; i++) {
            int v = order[i];
            if (blocked[v] == 0) addv(v, sel, blocked, S, &nS);
        }
        int best = nS;
        if (nS > global_best) {
            global_best = nS;
            printf("restart %d greedy=%d\n", r, nS);
            fflush(stdout);
        }
        for (int t = 0; t < steps; t++) {
            int dropn = (t % 11 == 0) ? 8 : 1;
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
            int packed[1024], np = 0;
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
                    packed[np++] = u;
                    take[u] = 1;
                }
            }
            if (nS + np >= best - 3) {
                for (int i = 0; i < np; i++) addv(packed[i], sel, blocked, S, &nS);
            } else {
                for (int i = 0; i < dropn; i++)
                    addv(dropped[i], sel, blocked, S, &nS);
            }
            if (nS > best) {
                best = nS;
                if (nS > global_best) {
                    global_best = nS;
                    printf("restart %d size=%d step=%d\n", r, nS, t);
                    fflush(stdout);
                    if (nS >= 368) {
                        write_set("q4/R_scratch.txt", S, nS);
                        return 0;
                    }
                }
            }
        }
        if ((r + 1) % 5 == 0) {
            printf("  restarts=%d best=%d last=%d t=%.1fs\n", r + 1, global_best,
                   best, (double)(clock() - t0) / CLOCKS_PER_SEC);
            fflush(stdout);
        }
    }
    printf("DONE restarts=%d best=%d t=%.2fs\n", restarts, global_best,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
