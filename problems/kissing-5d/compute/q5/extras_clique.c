/* Coloured B&B for extras in the 1480-point (1/4)Z^5 graph.

 * Same-missed extras are independent.  A clique E of extras with
 * missed-union U is a 41-set together with D5 \ U iff |E| >= |U|+1.
 * q4 emptied |U| <= 18.  This search hunts |E| >= 20 with |U| <= |E|-1.
 *
 * Usage: ./extras_clique [target] [node_limit]
 * Default target=20, node_limit=200000000.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <sys/stat.h>

#define MAXN 2048
#define MAXE 1600
#define MAXG 512
#define W ((MAXN + 63) / 64)

typedef uint64_t u64;

static int d = 4, thresh, target_norm;
static int n, nD, nE, nG, nwords, target;
static int pts[MAXN][5];
static int isD[MAXN];
static int Dlist[64];
static int eidx[MAXE];
static u64 miss[MAXE];
static int g_of[MAXE];
static int gsize[MAXG];
static int gmem[MAXG][16];
static u64 adj[MAXE][W];

static long nodes, node_limit = 200000000L;
static int found, best;
static int found_idx[64];
static u64 found_U;
static int slice_complete = 1;

static int ip_pts(int i, int j)
{
    int s = 0;
    for (int k = 0; k < 5; k++)
        s += pts[i][k] * pts[j][k];
    return s;
}

static int isqrt(int x)
{
    int r = (int)(sqrt((double)x) + 0.5);
    while (r * r > x)
        r--;
    while ((r + 1) * (r + 1) <= x)
        r++;
    return r;
}

static void enumerate(void)
{
    int lim = isqrt(target_norm);
    n = 0;
    for (int a = -lim; a <= lim; a++) {
        int r2 = target_norm - a * a;
        for (int b = -lim; b <= lim; b++) {
            int r3 = r2 - b * b;
            if (r3 < 0)
                continue;
            for (int c = -lim; c <= lim; c++) {
                int r4 = r3 - c * c;
                if (r4 < 0)
                    continue;
                for (int e = -lim; e <= lim; e++) {
                    int rem = r4 - e * e;
                    if (rem < 0)
                        continue;
                    int f = isqrt(rem);
                    if (f * f != rem)
                        continue;
                    int nf = (f == 0) ? 1 : 2;
                    int fs[2] = {f, -f};
                    for (int k = 0; k < nf; k++) {
                        pts[n][0] = a;
                        pts[n][1] = b;
                        pts[n][2] = c;
                        pts[n][3] = e;
                        pts[n][4] = fs[k];
                        n++;
                    }
                }
            }
        }
    }
}

static int popc(const u64 *a)
{
    int s = 0;
    for (int i = 0; i < nwords; i++)
        s += __builtin_popcountll(a[i]);
    return s;
}

static int first_bit(const u64 *a)
{
    for (int i = 0; i < nwords; i++)
        if (a[i])
            return i * 64 + __builtin_ctzll(a[i]);
    return -1;
}

static void bit_clear(u64 *a, int v)
{
    a[v >> 6] &= ~(1ULL << (v & 63));
}

static int colour_order(const u64 *P, int *ord, int *col)
{
    u64 rem[W];
    memcpy(rem, P, nwords * sizeof(u64));
    int m = 0, c = 0;
    while (popc(rem)) {
        c++;
        u64 avail[W];
        memcpy(avail, rem, nwords * sizeof(u64));
        int v;
        while ((v = first_bit(avail)) >= 0) {
            ord[m] = v;
            col[m] = c;
            m++;
            bit_clear(avail, v);
            for (int w = 0; w < nwords; w++)
                avail[w] &= ~adj[v][w];
            bit_clear(rem, v);
        }
    }
    return m;
}

static void write_code41(int rsz, const int *stack, u64 U)
{
    FILE *f = fopen("certs/code41.json", "w");
    if (!f)
        return;
    fprintf(f, "{\n  \"n\": %d,\n", rsz + (40 - __builtin_popcountll(U)));
    fprintf(f, "  \"source\": \"q5 extras_clique.c\",\n");
    fprintf(f, "  \"n_extras\": %d,\n  \"n1\": %d,\n  \"points\": [\n",
            rsz, 40 - __builtin_popcountll(U));
    int first = 1;
    for (int t = 0; t < rsz; t++) {
        int i = eidx[stack[t]];
        if (!first)
            fprintf(f, ",\n");
        first = 0;
        fprintf(f, "    [\"%d/4\", \"%d/4\", \"%d/4\", \"%d/4\", \"%d/4\"]",
                pts[i][0], pts[i][1], pts[i][2], pts[i][3], pts[i][4]);
    }
    for (int j = 0; j < nD; j++) {
        if ((U >> j) & 1ULL)
            continue;
        int i = Dlist[j];
        if (!first)
            fprintf(f, ",\n");
        first = 0;
        fprintf(f, "    [\"%d/4\", \"%d/4\", \"%d/4\", \"%d/4\", \"%d/4\"]",
                pts[i][0], pts[i][1], pts[i][2], pts[i][3], pts[i][4]);
    }
    fprintf(f, "\n  ]\n}\n");
    fclose(f);
}

static void expand(u64 *P, int rsz, int *stack, u64 U)
{
    nodes++;
    if (found || nodes > node_limit)
        return;
    int psz = popc(P);
    int uk = __builtin_popcountll(U);
    /* even taking every remaining extra, |E| = rsz+psz, need |E| >= |U|+1
     * and |U| can only grow.  q4 emptied |U|<=18, so a leftover 41-set
     * also needs |U| >= 19. */
    if (rsz + psz <= uk)
        return;
    if (rsz + psz < target)
        return;
    if (rsz + psz < 20)
        return;
    if (uk < 19 && psz <= 96) {
        u64 grow = U;
        for (int w = 0; w < nwords; w++) {
            u64 bits = P[w];
            while (bits) {
                int b = __builtin_ctzll(bits);
                bits &= bits - 1;
                grow |= miss[w * 64 + b];
            }
        }
        if (__builtin_popcountll(grow) < 19)
            return;
    }
    if (psz == 0) {
        if (rsz > best)
            best = rsz;
        if (rsz >= uk + 1 && rsz >= target) {
            found = 1;
            found_U = U;
            memcpy(found_idx, stack, (size_t)rsz * sizeof(int));
            write_code41(rsz, stack, U);
        }
        return;
    }
    int ord[MAXN], col[MAXN];
    int m = colour_order(P, ord, col);
    u64 Q[W];
    memcpy(Q, P, nwords * sizeof(u64));
    for (int i = m - 1; i >= 0; i--) {
        if (found || nodes > node_limit)
            return;
        if (rsz + col[i] < target)
            return;
        int v = ord[i];
        u64 U2 = U | miss[v];
        int uk2 = __builtin_popcountll(U2);
        if (rsz + 1 + (psz - 1) <= uk2) {
            bit_clear(Q, v);
            continue;
        }
        u64 P2[W];
        for (int w = 0; w < nwords; w++)
            P2[w] = Q[w] & adj[v][w];
        int g = g_of[v];
        for (int t = 0; t < gsize[g]; t++)
            bit_clear(P2, gmem[g][t]);
        stack[rsz] = v;
        if (rsz + 1 >= target && rsz + 1 >= uk2 + 1) {
            found = 1;
            best = rsz + 1;
            found_U = U2;
            memcpy(found_idx, stack, (size_t)(rsz + 1) * sizeof(int));
            write_code41(rsz + 1, stack, U2);
            return;
        }
        expand(P2, rsz + 1, stack, U2);
        bit_clear(Q, v);
    }
}

int main(int argc, char **argv)
{
    target = 20;
    if (argc >= 2)
        target = atoi(argv[1]);
    if (argc >= 3)
        node_limit = atol(argv[2]);
    if (target < 19 || target > 40) {
        fprintf(stderr, "target out of range\n");
        return 1;
    }
    target_norm = 2 * d * d;
    thresh = d * d;
    enumerate();

    nD = 0;
    memset(isD, 0, sizeof isD);
    for (int i = 0; i < n; i++) {
        int nz = 0, ok = 1;
        for (int k = 0; k < 5; k++) {
            int a = pts[i][k] < 0 ? -pts[i][k] : pts[i][k];
            if (a == 0)
                continue;
            nz++;
            if (a != d)
                ok = 0;
        }
        if (ok && nz == 2) {
            isD[i] = 1;
            Dlist[nD++] = i;
        }
    }

    nE = 0;
    nG = 0;
    u64 seeds[MAXG];
    for (int i = 0; i < n; i++) {
        if (isD[i])
            continue;
        u64 msk = 0;
        for (int j = 0; j < nD; j++)
            if (ip_pts(i, Dlist[j]) > thresh)
                msk |= 1ULL << j;
        int gi = -1;
        for (int g = 0; g < nG; g++)
            if (seeds[g] == msk) {
                gi = g;
                break;
            }
        if (gi < 0) {
            gi = nG++;
            seeds[gi] = msk;
            gsize[gi] = 0;
        }
        eidx[nE] = i;
        miss[nE] = msk;
        g_of[nE] = gi;
        gmem[gi][gsize[gi]++] = nE;
        nE++;
    }

    nwords = (nE + 63) / 64;
    memset(adj, 0, sizeof adj);
    long edges = 0;
    for (int i = 0; i < nE; i++) {
        for (int j = i + 1; j < nE; j++) {
            if (ip_pts(eidx[i], eidx[j]) <= thresh) {
                adj[i][j >> 6] |= 1ULL << (j & 63);
                adj[j][i >> 6] |= 1ULL << (i & 63);
                edges++;
            }
        }
    }

    mkdir("certs", 0755);
    found = 0;
    best = target - 1;
    nodes = 0;
    u64 P[W];
    memset(P, 0, sizeof P);
    for (int v = 0; v < nE; v++)
        P[v >> 6] |= 1ULL << (v & 63);
    int stack[64];
    expand(P, 0, stack, 0);
    if (nodes > node_limit && !found)
        slice_complete = 0;

    printf("{\n");
    printf("  \"d\": %d,\n", d);
    printf("  \"n\": %d,\n", n);
    printf("  \"n_d5\": %d,\n", nD);
    printf("  \"n_extras\": %d,\n", nE);
    printf("  \"n_groups\": %d,\n", nG);
    printf("  \"n_extra_edges\": %ld,\n", edges);
    printf("  \"target\": %d,\n", target);
    printf("  \"nodes\": %ld,\n", nodes);
    printf("  \"node_limit\": %ld,\n", node_limit);
    printf("  \"best_extras\": %d,\n", best);
    printf("  \"found_41\": %s,\n", found ? "true" : "false");
    if (found)
        printf("  \"found_n1\": %d,\n", 40 - __builtin_popcountll(found_U));
    printf("  \"complete\": %s,\n", slice_complete && !found ? "true" : "false");
    printf("  \"comment\": \"extras B&B for |E|>=target and |E|>=|U|+1\"\n");
    printf("}\n");
    return 0;
}
