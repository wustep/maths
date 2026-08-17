/* Same census as circulant_census.c but writes every HIT as a compact line.
   gcc -O3 -std=c11 -o dump_circulants dump_circulants.c
   ./dump_circulants n
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int N;
static int NDIST;
static int HALF;
static int DEG_LO, DEG_HI;
static unsigned long long scanned, legal_deg, hits;

static int has_k4_in(const int *conn, const int *verts, int d) {
    int a, b, c, e;
    for (a = 0; a < d; a++) {
        for (b = a + 1; b < d; b++) {
            int ab = verts[b] - verts[a];
            if (ab < 0) ab += N;
            if (!conn[ab]) continue;
            for (c = b + 1; c < d; c++) {
                int ac = verts[c] - verts[a];
                int bc = verts[c] - verts[b];
                if (ac < 0) ac += N;
                if (bc < 0) bc += N;
                if (!conn[ac] || !conn[bc]) continue;
                for (e = c + 1; e < d; e++) {
                    int ae = verts[e] - verts[a];
                    int be = verts[e] - verts[b];
                    int ce = verts[e] - verts[c];
                    if (ae < 0) ae += N;
                    if (be < 0) be += N;
                    if (ce < 0) ce += N;
                    if (conn[ae] && conn[be] && conn[ce]) return 1;
                }
            }
        }
    }
    return 0;
}

static int is_ramsey55(const int *chosen, int *deg_out) {
    int conn[64];
    memset(conn, 0, sizeof(conn));
    int deg = 0;
    for (int i = 1; i <= NDIST; i++) {
        if (!chosen[i]) continue;
        conn[i] = 1;
        if (i != N - i) {
            conn[N - i] = 1;
            deg += 2;
        } else {
            deg += 1;
        }
    }
    *deg_out = deg;
    if (deg < DEG_LO || deg > DEG_HI) return 0;
    int neigh[64], nneigh = 0, dual[64], ndual = 0;
    for (int i = 1; i < N; i++) {
        if (conn[i])
            neigh[nneigh++] = i;
        else
            dual[ndual++] = i;
    }
    if (has_k4_in(conn, neigh, nneigh)) return 0;
    int cconn[64];
    for (int i = 0; i < N; i++) cconn[i] = 0;
    for (int i = 1; i < N; i++) cconn[i] = !conn[i];
    if (has_k4_in(cconn, dual, ndual)) return 0;
    return 1;
}

static void rec(int dist, int *chosen, int deg_so_far) {
    if (deg_so_far > DEG_HI) return;
    if (dist > NDIST) {
        scanned++;
        if (deg_so_far < DEG_LO) return;
        legal_deg++;
        int deg;
        if (is_ramsey55(chosen, &deg)) {
            hits++;
            unsigned long long mask = 0;
            printf("HIT n=%d deg=%d S=", N, deg);
            for (int i = 1; i <= NDIST; i++)
                if (chosen[i]) {
                    printf("%d ", i);
                    mask |= 1ULL << i;
                }
            printf("mask=%llu\n", mask);
        }
        return;
    }
    int add = (dist == HALF) ? 1 : 2;
    int rem = 0;
    for (int i = dist + 1; i <= NDIST; i++) rem += (i == HALF) ? 1 : 2;
    if (deg_so_far + rem < DEG_LO) return;
    chosen[dist] = 0;
    rec(dist + 1, chosen, deg_so_far);
    chosen[dist] = 1;
    rec(dist + 1, chosen, deg_so_far + add);
    chosen[dist] = 0;
}

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    N = atoi(argv[1]);
    NDIST = N / 2;
    HALF = (N % 2 == 0) ? N / 2 : -1;
    DEG_LO = N - 25;
    if (DEG_LO < 0) DEG_LO = 0;
    DEG_HI = 24;
    if (DEG_HI > N - 1) DEG_HI = N - 1;
    int chosen[64];
    memset(chosen, 0, sizeof(chosen));
    clock_t t0 = clock();
    rec(1, chosen, 0);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE n=%d scanned=%llu legal=%llu hits=%llu sec=%.3f\n", N, scanned,
           legal_deg, hits, sec);
    return 0;
}
