/* Union of two translates of the published 367-set.

   Induced edges in A ∪ (A+v) run only between L = A \ I and R = (A+v) \ I
   with I = A ∩ (A+v). Intersection points are isolated. Then
   α = |union| - ν = 734 - |I| - ν, so a 368-set exists iff the bipartite
   matching on (L,R) is imperfect.

   gcc -O3 -o q1/search_translates q1/search_translates.c
   ./q1/search_translates R367.txt
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NV 16807
#define DIM 5
#define SEEDN 367
#define MAXDEG 242

static int coord[NV][DIM];
static int neigh[NV][243];
static int seed[SEEDN];
static uint8_t inA[NV], inT[NV];
static int idxR[NV], idxRstamp, idxRgen[NV];

static int pairU[SEEDN], pairV[SEEDN], seen[SEEDN], stamp;
static int adj[SEEDN][MAXDEG], deg[SEEDN];
static int Lverts[SEEDN], Rverts[SEEDN];

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

static int addv(int a, int b) {
    int c[DIM];
    for (int i = 0; i < DIM; i++) c[i] = (coord[a][i] + coord[b][i]) % 7;
    return encode_coords(c);
}

static int load_seed(const char *path) {
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
        if (p[0] >= '0' && p[0] <= '6' && p[1] >= '0' && p[1] <= '6' &&
            p[2] >= '0' && p[2] <= '6' && p[3] >= '0' && p[3] <= '6' &&
            p[4] >= '0' && p[4] <= '6' &&
            (p[5] == '\0' || p[5] == '\n' || p[5] == '\r' || p[5] == ' ')) {
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
            fprintf(stderr, "bad line: %s", line);
            fclose(f);
            return -1;
        }
        if (n >= SEEDN) {
            fprintf(stderr, "too many words\n");
            fclose(f);
            return -1;
        }
        seed[n++] = encode_coords(c);
    }
    fclose(f);
    return n;
}

static int dfs(int u) {
    for (int i = 0; i < deg[u]; i++) {
        int v = adj[u][i];
        if (seen[v] == stamp) continue;
        seen[v] = stamp;
        if (pairV[v] < 0 || dfs(pairV[v])) {
            pairU[u] = v;
            pairV[v] = u;
            return 1;
        }
    }
    return 0;
}

static int max_matching(int nL, int nR) {
    for (int i = 0; i < nL; i++) pairU[i] = -1;
    for (int i = 0; i < nR; i++) pairV[i] = -1;
    int m = 0;
    for (int u = 0; u < nL; u++) {
        for (int i = 0; i < deg[u]; i++) {
            int v = adj[u][i];
            if (pairV[v] < 0) {
                pairV[v] = u;
                pairU[u] = v;
                m++;
                break;
            }
        }
    }
    stamp = 1;
    memset(seen, 0, nR * sizeof seen[0]);
    for (int u = 0; u < nL; u++) {
        if (pairU[u] >= 0) continue;
        stamp++;
        if (dfs(u)) m++;
    }
    return m;
}

static void write_konig(const char *path, int nL, int nR) {
    uint8_t reachL[SEEDN], reachR[SEEDN];
    memset(reachL, 0, sizeof reachL);
    memset(reachR, 0, sizeof reachR);
    int q[SEEDN], qt = 0;
    for (int u = 0; u < nL; u++) {
        if (pairU[u] < 0) {
            reachL[u] = 1;
            q[qt++] = u;
        }
    }
    int qh = 0;
    while (qh < qt) {
        int u = q[qh++];
        for (int i = 0; i < deg[u]; i++) {
            int r = adj[u][i];
            if (reachR[r]) continue;
            reachR[r] = 1;
            int u2 = pairV[r];
            if (u2 >= 0 && !reachL[u2]) {
                reachL[u2] = 1;
                q[qt++] = u2;
            }
        }
    }
    FILE *hit = fopen(path, "w");
    if (!hit) {
        perror(path);
        return;
    }
    int wrote = 0;
    for (int i = 0; i < SEEDN; i++) {
        if (inT[seed[i]]) {
            fprintf(hit, "%d %d %d %d %d\n", coord[seed[i]][0], coord[seed[i]][1],
                    coord[seed[i]][2], coord[seed[i]][3], coord[seed[i]][4]);
            wrote++;
        }
    }
    for (int u = 0; u < nL; u++) {
        if (reachL[u]) {
            int x = Lverts[u];
            fprintf(hit, "%d %d %d %d %d\n", coord[x][0], coord[x][1], coord[x][2],
                    coord[x][3], coord[x][4]);
            wrote++;
        }
    }
    for (int r = 0; r < nR; r++) {
        if (!reachR[r]) {
            int x = Rverts[r];
            fprintf(hit, "%d %d %d %d %d\n", coord[x][0], coord[x][1], coord[x][2],
                    coord[x][3], coord[x][4]);
            wrote++;
        }
    }
    fclose(hit);
    printf("wrote %s size=%d\n", path, wrote);
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "R367.txt";
    fill_tables();
    int n = load_seed(path);
    if (n != SEEDN) {
        fprintf(stderr, "expected %d words, got %d\n", SEEDN, n);
        return 1;
    }
    memset(inA, 0, sizeof inA);
    for (int i = 0; i < SEEDN; i++) inA[seed[i]] = 1;
    memset(idxRgen, 0, sizeof idxRgen);
    idxRstamp = 1;

    int disjoint = 0, intersecting = 0, imperfect = 0;
    int best_alpha = 0, best_v = -1, best_nu = 0, best_I = 0;
    int found368 = 0;

    for (int v = 1; v < NV; v++) {
        memset(inT, 0, sizeof inT);
        int Tv[SEEDN];
        for (int i = 0; i < SEEDN; i++) {
            Tv[i] = addv(seed[i], v);
            inT[Tv[i]] = 1;
        }
        int Icnt = 0;
        for (int i = 0; i < SEEDN; i++)
            if (inT[seed[i]]) Icnt++;
        if (Icnt)
            intersecting++;
        else
            disjoint++;

        int nL = 0, nR = 0;
        idxRstamp++;
        if (idxRstamp == 0x7fffffff) {
            memset(idxRgen, 0, sizeof idxRgen);
            idxRstamp = 1;
        }
        for (int i = 0; i < SEEDN; i++) {
            if (!inT[seed[i]]) Lverts[nL++] = seed[i];
        }
        for (int i = 0; i < SEEDN; i++) {
            int y = Tv[i];
            if (!inA[y]) {
                idxR[y] = nR;
                idxRgen[y] = idxRstamp;
                Rverts[nR++] = y;
            }
        }
        if (nL != SEEDN - Icnt || nR != SEEDN - Icnt) {
            fprintf(stderr, "size mismatch v=%d I=%d nL=%d nR=%d\n", v, Icnt, nL, nR);
            return 1;
        }
        for (int u = 0; u < nL; u++) {
            deg[u] = 0;
            int x = Lverts[u];
            for (int k = 0; k < 243; k++) {
                int y = neigh[x][k];
                if (y == x) continue;
                if (idxRgen[y] != idxRstamp) continue;
                adj[u][deg[u]++] = idxR[y];
            }
        }
        int nu = max_matching(nL, nR);
        int alpha = 734 - Icnt - nu;
        if (alpha > best_alpha) {
            best_alpha = alpha;
            best_v = v;
            best_nu = nu;
            best_I = Icnt;
            printf("best alpha=%d v=%d I=%d nu=%d/%d\n", alpha, v, Icnt, nu, nL);
            fflush(stdout);
        }
        if (nu < nL) {
            imperfect++;
            printf("IMPERFECT v=%d I=%d nu=%d/%d alpha=%d\n", v, Icnt, nu, nL, alpha);
            fflush(stdout);
            if (alpha >= 368 && !found368) {
                char outpath[128];
                snprintf(outpath, sizeof outpath, "q1/R%d_translate.txt", alpha);
                write_konig(outpath, nL, nR);
                found368 = 1;
            }
        }
        if (v % 2000 == 0) {
            printf("progress v=%d disjoint=%d inter=%d best_alpha=%d imperfect=%d\n",
                   v, disjoint, intersecting, best_alpha, imperfect);
            fflush(stdout);
        }
    }

    printf("DONE disjoint=%d intersecting=%d best_alpha=%d best_v=%d I=%d nu=%d imperfect=%d found368=%d\n",
           disjoint, intersecting, best_alpha, best_v, best_I, best_nu, imperfect, found368);
    return 0;
}
