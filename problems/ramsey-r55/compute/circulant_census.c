/* Exhaustive census of undirected circulant (5,5)-graphs on n in {42,43,44,45}.

   Connection set is a subset S of {1,...,floor(n/2)}, closed under n-x
   automatically. For even n the distance n/2 is an involution and contributes
   1 to the degree; every other chosen distance contributes 2.

   A graph is accepted iff it has no K5 and no independent set of size 5.
   Vertex-transitivity reduces both tests to a 4-clique search in the
   neighbourhood (resp. dual neighbourhood) of vertex 0.

   Compile: gcc -O3 -std=c11 -o circulant_census circulant_census.c
   Run:     ./circulant_census 43
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int N;
static int NDIST;          /* floor(n/2) */
static int HALF;           /* n/2 if n even, else -1 */
static int DEG_LO, DEG_HI; /* legal degrees using R(4,5)=25 */

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

static int is_ramsey55(const int *chosen) {
    int conn[64];
    int i;
    memset(conn, 0, sizeof(conn));
    int deg = 0;
    for (i = 1; i <= NDIST; i++) {
        if (!chosen[i]) continue;
        conn[i] = 1;
        if (i != N - i) {
            conn[N - i] = 1;
            deg += 2;
        } else {
            deg += 1;
        }
    }
    if (deg < DEG_LO || deg > DEG_HI) return 0;

    int neigh[64], nneigh = 0;
    int dual[64], ndual = 0;
    for (i = 1; i < N; i++) {
        if (conn[i])
            neigh[nneigh++] = i;
        else
            dual[ndual++] = i;
    }
    if (has_k4_in(conn, neigh, nneigh)) return 0;
    /* independent 4-set in dual neighbourhood = K4 in the complement */
    int cconn[64];
    for (i = 0; i < N; i++) cconn[i] = 0;
    for (i = 1; i < N; i++) cconn[i] = !conn[i];
    if (has_k4_in(cconn, dual, ndual)) return 0;
    return 1;
}

static unsigned long long scanned = 0;
static unsigned long long legal_deg = 0;
static unsigned long long hits = 0;
static int best_omega_block = 0; /* unused; kept for future logging */

static void rec(int dist, int *chosen, int deg_so_far) {
    if (deg_so_far > DEG_HI) return;
    if (dist > NDIST) {
        scanned++;
        if (deg_so_far < DEG_LO) return;
        legal_deg++;
        if (is_ramsey55(chosen)) {
            hits++;
            printf("HIT n=%d deg=%d S=", N, deg_so_far);
            for (int i = 1; i <= NDIST; i++)
                if (chosen[i]) printf("%d ", i);
            printf("\n");
            fflush(stdout);
        }
        return;
    }
    int add = (dist == HALF) ? 1 : 2;
    /* remaining distances after this one */
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
    if (argc < 2) {
        fprintf(stderr, "usage: %s n\n", argv[0]);
        return 2;
    }
    N = atoi(argv[1]);
    if (N < 5 || N > 62) {
        fprintf(stderr, "n out of range\n");
        return 2;
    }
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
    printf(
        "DONE n=%d ndist=%d deg=[%d,%d] scanned=%llu legal_deg=%llu hits=%llu "
        "sec=%.3f\n",
        N, NDIST, DEG_LO, DEG_HI, scanned, legal_deg, hits, sec);
    return hits ? 1 : 0;
}
