/* 2-out packing on the 108 private-pair 367-sets (shape 6).

   gcc -O3 -o q1/search_plateau q1/search_plateau.c
   ./q1/search_plateau R367.txt
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NV 16807
#define DIM 5
#define SEEDN 367

static int coord[NV][DIM];
static int neigh[NV][243];
static int seed0[SEEDN];

static const int PAIRS[8][2][5] = {
    {{1, 3, 4, 4, 6}, {2, 3, 5, 4, 6}},
    {{3, 4, 0, 3, 5}, {2, 4, 6, 3, 5}},
    {{5, 3, 1, 3, 4}, {5, 3, 2, 3, 5}},
    {{4, 4, 6, 1, 6}, {5, 4, 6, 0, 6}},
    {{6, 0, 6, 4, 5}, {6, 1, 6, 5, 5}},
    {{0, 3, 5, 6, 5}, {6, 3, 5, 0, 5}},
    {{6, 4, 3, 4, 0}, {6, 4, 2, 4, 6}},
    {{6, 4, 5, 3, 2}, {6, 5, 5, 3, 1}},
};

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
    if (!f) {
        perror(path);
        return -1;
    }
    int n = 0;
    char line[256];
    while (fgets(line, sizeof line, f)) {
        int c[5];
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\0' || *p == '\n') continue;
        int k = 0;
        if (p[0] >= '0' && p[0] <= '6' && p[1] >= '0' && p[1] <= '6') {
            for (int i = 0; i < 5; i++) c[i] = p[i] - '0';
            k = 5;
        } else {
            for (int i = 0; i < 5; i++) {
                int x, consumed = 0;
                if (sscanf(p, "%d%n", &x, &consumed) != 1) {
                    k = -1;
                    break;
                }
                c[i] = x;
                k++;
                p += consumed;
            }
        }
        if (k != 5) {
            fclose(f);
            return -1;
        }
        out[n++] = encode_coords(c);
    }
    fclose(f);
    return n;
}

static int circ_ok(int u, int v) {
    /* adjacent iff all coords circular dist <= 1, u!=v */
    if (u == v) return 0;
    for (int i = 0; i < 5; i++) {
        int d = coord[u][i] - coord[v][i];
        if (d < 0) d = -d;
        if (d > 3) d = 7 - d;
        if (d > 1) return 0;
    }
    return 1;
}

static int independent(const int *S, int n) {
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (circ_ok(S[i], S[j])) return 0;
    return 1;
}

static int pack_greedy(const int *freed, int nf, int *out) {
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

static int pack_freed(const int *freed, int nf, int *out) {
    /* greedy first; exact only if greedy < 3 and nf is tiny */
    if (nf == 0) return 0;
    int g = pack_greedy(freed, nf, out);
    if (g >= 3 || nf > 12) return g;
    int adj[20];
    memset(adj, 0, sizeof adj);
    for (int i = 0; i < nf; i++)
        for (int j = i + 1; j < nf; j++)
            if (circ_ok(freed[i], freed[j])) {
                adj[i] |= 1 << j;
                adj[j] |= 1 << i;
            }
    int best = 0, bestm = 0;
    int all = (1 << nf) - 1;
    /* recursive */
    int stack_cand[21], stack_cur[21], stack_side[21], top = 0;
    stack_cand[0] = all;
    stack_cur[0] = 0;
    stack_side[0] = 0;
    while (top >= 0) {
        int cand = stack_cand[top];
        int cur = stack_cur[top];
        int side = stack_side[top];
        if (side == 0) {
            int ub = cur;
            int tmp = cand;
            while (tmp) {
                ub++;
                tmp &= tmp - 1;
            }
            if (ub <= best) {
                top--;
                continue;
            }
            if (cand == 0) {
                int bc = 0, t = cur;
                while (t) {
                    bc++;
                    t &= t - 1;
                }
                if (bc > best) {
                    best = bc;
                    bestm = cur;
                }
                top--;
                continue;
            }
            int v = 0;
            int bit = cand & -cand;
            while ((1 << v) != bit) v++;
            /* first branch: take v */
            stack_side[top] = 1;
            top++;
            stack_cand[top] = cand & ~adj[v] & ~bit;
            stack_cur[top] = cur | bit;
            stack_side[top] = 0;
            continue;
        } else if (side == 1) {
            int v = 0;
            int bit = cand & -cand;
            while ((1 << v) != bit) v++;
            stack_side[top] = 2;
            top++;
            stack_cand[top] = cand & ~bit;
            stack_cur[top] = cur;
            stack_side[top] = 0;
            continue;
        } else {
            top--;
        }
    }
    int nout = 0;
    for (int i = 0; i < nf; i++)
        if (bestm & (1 << i)) out[nout++] = freed[i];
    return nout;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "R367.txt";
    fill_tables();
    int n = load_seed(path, seed0);
    if (n != SEEDN) {
        fprintf(stderr, "bad seed %d\n", n);
        return 1;
    }
    int renc[8], qenc[8];
    uint8_t in0[NV];
    memset(in0, 0, sizeof in0);
    for (int i = 0; i < SEEDN; i++) in0[seed0[i]] = 1;
    for (int j = 0; j < 8; j++) {
        renc[j] = encode_coords(PAIRS[j][0]);
        qenc[j] = encode_coords(PAIRS[j][1]);
        if (!in0[renc[j]] || in0[qenc[j]]) {
            fprintf(stderr, "pair %d not r-in q-out\n", j);
            return 1;
        }
    }

    int blocked[NV];
    int n_ok = 0, best_gain = -99, trials = 0, hit = 0;
    for (int mask = 0; mask < 256; mask++) {
        int S[SEEDN];
        memcpy(S, seed0, sizeof S);
        int ok = 1;
        for (int j = 0; j < 8; j++) {
            if (!((mask >> j) & 1)) continue;
            int found = 0;
            for (int i = 0; i < SEEDN; i++)
                if (S[i] == renc[j]) {
                    S[i] = qenc[j];
                    found = 1;
                    break;
                }
            if (!found) {
                ok = 0;
                break;
            }
        }
        if (!ok) continue;
        if (!independent(S, SEEDN)) continue;
        n_ok++;

        memset(blocked, 0, sizeof blocked);
        uint8_t sel[NV];
        memset(sel, 0, sizeof sel);
        for (int i = 0; i < SEEDN; i++) {
            sel[S[i]] = 1;
            for (int k = 0; k < 243; k++) blocked[neigh[S[i]][k]]++;
        }
        /* 2-out */
        for (int i = 0; i < SEEDN; i++) {
            for (int j = i + 1; j < SEEDN; j++) {
                int a = S[i], b = S[j];
                for (int k = 0; k < 243; k++) {
                    blocked[neigh[a][k]]--;
                    blocked[neigh[b][k]]--;
                }
                int freed[512], nf = 0;
                static int seen_stamp[NV], gen;
                gen++;
                if (gen == 0x7fffffff) {
                    memset(seen_stamp, 0, sizeof seen_stamp);
                    gen = 1;
                }
                for (int k = 0; k < 243; k++) {
                    int u = neigh[a][k];
                    if (blocked[u] == 0 && seen_stamp[u] != gen) {
                        seen_stamp[u] = gen;
                        freed[nf++] = u;
                    }
                    u = neigh[b][k];
                    if (blocked[u] == 0 && seen_stamp[u] != gen) {
                        seen_stamp[u] = gen;
                        freed[nf++] = u;
                    }
                }
                int packed[64];
                int np = pack_freed(freed, nf, packed);
                int gain = np - 2;
                if (gain > best_gain) {
                    best_gain = gain;
                    printf("best_gain=%d nf=%d mask=%d trial=%d\n", best_gain, nf, mask,
                           trials);
                    fflush(stdout);
                }
                if (gain >= 1) {
                    printf("HIT size=%d mask=%d i=%d j=%d\n", SEEDN + gain, mask, i, j);
                    hit = 1;
                    char outpath[128];
                    snprintf(outpath, sizeof outpath, "q1/R%d_plateau.txt", SEEDN + gain);
                    FILE *o = fopen(outpath, "w");
                    for (int t = 0; t < SEEDN; t++) {
                        if (t == i || t == j) continue;
                        int x = S[t];
                        fprintf(o, "%d %d %d %d %d\n", coord[x][0], coord[x][1], coord[x][2],
                                coord[x][3], coord[x][4]);
                    }
                    for (int t = 0; t < np; t++) {
                        int x = packed[t];
                        fprintf(o, "%d %d %d %d %d\n", coord[x][0], coord[x][1], coord[x][2],
                                coord[x][3], coord[x][4]);
                    }
                    fclose(o);
                    printf("wrote %s\n", outpath);
                    return 0;
                }
                for (int k = 0; k < 243; k++) {
                    blocked[neigh[a][k]]++;
                    blocked[neigh[b][k]]++;
                }
                trials++;
            }
        }
        if (n_ok % 10 == 0) {
            printf("sets %d/108 trials=%d best_gain=%d\n", n_ok, trials, best_gain);
            fflush(stdout);
        }
    }
    printf("DONE n_ok=%d trials=%d best_gain=%d hit=%d\n", n_ok, trials, best_gain, hit);
    return 0;
}
