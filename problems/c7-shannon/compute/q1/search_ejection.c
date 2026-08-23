/* Ejection-chain local search from the 367-set (shape 6, not 3-out SAT).

   Drop one vertex, pack newly free, accept size-improving or small downhill
   moves. Sampled 4-out packing. Restarts. Writes a set iff size >= 368.

   gcc -O3 -o q1/search_ejection q1/search_ejection.c
   ./q1/search_ejection R367.txt
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
static int seed0[SEEDN];

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

static int load_seed(const char *path, int *out) {
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
                int x, consumed = 0;
                if (sscanf(p, "%d%n", &x, &consumed) != 1) {
                    fclose(f);
                    return -1;
                }
                c[i] = x;
                p += consumed;
            }
        }
        out[n++] = encode_coords(c);
    }
    fclose(f);
    return n;
}

static int circ_ok(int u, int v) {
    if (u == v) return 0;
    for (int i = 0; i < 5; i++) {
        int d = coord[u][i] - coord[v][i];
        if (d < 0) d = -d;
        if (d > 3) d = 7 - d;
        if (d > 1) return 0;
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

static int pack_free(const int *freed, int nf, int *out) {
    int nout = 0;
    for (int i = 0; i < nf; i++) {
        int ok = 1;
        for (int j = 0; j < nout; j++)
            if (circ_ok(freed[i], out[j])) {
                ok = 0;
                break;
            }
        if (ok) out[nout++] = freed[i];
    }
    return nout;
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
    const char *path = argc > 1 ? argv[1] : "R367.txt";
    int steps = argc > 2 ? atoi(argv[2]) : 400000;
    int restarts = argc > 3 ? atoi(argv[3]) : 12;
    fill_tables();
    int n0 = load_seed(path, seed0);
    if (n0 != SEEDN) {
        fprintf(stderr, "bad seed\n");
        return 1;
    }
    unsigned rng = 1;
    int global_best = SEEDN;
    int four_out_gain = -99;
    int four_trials = 0;

    for (int r = 0; r < restarts; r++) {
        uint8_t sel[NV];
        int blocked[NV];
        int S[NV], nS = 0;
        memset(sel, 0, sizeof sel);
        memset(blocked, 0, sizeof blocked);
        for (int i = 0; i < SEEDN; i++) addv(seed0[i], sel, blocked, S, &nS);
        int best = nS;
        int stuck = 0;
        for (int t = 0; t < steps; t++) {
            rng = rng * 1664525u + 1013904223u;
            int idx = (int)(rng % (unsigned)nS);
            int v = S[idx];
            remv(v, sel, blocked, S, &nS);
            int freed[512], nf = 0;
            static int stamp[NV], gen;
            gen++;
            if (gen <= 0) {
                memset(stamp, 0, sizeof stamp);
                gen = 1;
            }
            for (int k = 0; k < 243; k++) {
                int u = neigh[v][k];
                if (blocked[u] == 0 && stamp[u] != gen) {
                    stamp[u] = gen;
                    freed[nf++] = u;
                }
            }
            /* shuffle freed */
            for (int i = nf - 1; i > 0; i--) {
                rng = rng * 1664525u + 1013904223u;
                int j = (int)(rng % (unsigned)(i + 1));
                int tmp = freed[i];
                freed[i] = freed[j];
                freed[j] = tmp;
            }
            int packed[243];
            int np = pack_free(freed, nf, packed);
            for (int i = 0; i < np; i++) addv(packed[i], sel, blocked, S, &nS);
            if (nS > best) {
                best = nS;
                printf("restart %d step %d size %d\n", r, t, nS);
                fflush(stdout);
                stuck = 0;
                if (nS > global_best) {
                    global_best = nS;
                    if (nS >= 368) {
                        write_set("q1/R_ejection.txt", S, nS);
                        return 0;
                    }
                }
            } else {
                stuck++;
            }
            /* sampled 4-out every 200 steps */
            if (t % 200 == 0 && nS >= 4) {
                int drop[4];
                for (int i = 0; i < 4; i++) {
                    rng = rng * 1664525u + 1013904223u;
                    drop[i] = S[rng % (unsigned)nS];
                    remv(drop[i], sel, blocked, S, &nS);
                }
                nf = 0;
                gen++;
                for (int i = 0; i < 4; i++)
                    for (int k = 0; k < 243; k++) {
                        int u = neigh[drop[i]][k];
                        if (blocked[u] == 0 && stamp[u] != gen) {
                            stamp[u] = gen;
                            freed[nf++] = u;
                        }
                    }
                np = pack_free(freed, nf, packed);
                int gain = np - 4;
                if (gain > four_out_gain) four_out_gain = gain;
                four_trials++;
                if (gain >= 1) {
                    for (int i = 0; i < np; i++) addv(packed[i], sel, blocked, S, &nS);
                    printf("4-out hit size=%d gain=%d\n", nS, gain);
                    if (nS >= 368) {
                        write_set("q1/R_ejection.txt", S, nS);
                        return 0;
                    }
                } else {
                    for (int i = 0; i < 4; i++) addv(drop[i], sel, blocked, S, &nS);
                }
            }
            if (stuck > 8000) {
                /* jump: drop 8 random, pack */
                for (int i = 0; i < 8 && nS > 0; i++) {
                    rng = rng * 1664525u + 1013904223u;
                    remv(S[rng % (unsigned)nS], sel, blocked, S, &nS);
                }
                nf = 0;
                gen++;
                for (int u = 0; u < NV; u++)
                    if (blocked[u] == 0) {
                        if (nf < 512) freed[nf++] = u;
                    }
                for (int i = nf - 1; i > 0; i--) {
                    rng = rng * 1664525u + 1013904223u;
                    int j = (int)(rng % (unsigned)(i + 1));
                    int tmp = freed[i];
                    freed[i] = freed[j];
                    freed[j] = tmp;
                }
                np = pack_free(freed, nf, packed);
                for (int i = 0; i < np; i++) addv(packed[i], sel, blocked, S, &nS);
                stuck = 0;
            }
        }
        printf("restart %d done size=%d best=%d\n", r, nS, best);
        fflush(stdout);
    }
    printf("DONE global_best=%d four_out_best_gain=%d four_trials=%d\n", global_best,
           four_out_gain, four_trials);
    return 0;
}
