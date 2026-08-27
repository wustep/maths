/* Clique search on the extras of (1/d)Z^5, |x|^2=2.
 *
 * A 41-set has n1 <= 36 D5-type points.  An extras-clique E contributes
 *     total = |E| + (40 - |union missed D5 roots|).
 * We hunt total >= 41, i.e. |E| >= |U| + 1.
 *
 * Usage: ./extras_bb <d> [node_limit]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAXN 2048
#define W ((MAXN + 63) / 64)

typedef uint64_t u64;

static int d, n, nwords, nD, nE, thresh, target_norm;
static int pts[MAXN][5];
static int isD[MAXN];
static int eidx[MAXN];          /* extra -> original */
static u64 miss[MAXN];          /* 40-bit missed-D5 mask of extra i */
static u64 adj[MAXN][W];
static int best_total, found;
static int found_E[MAXN];
static int found_nE, found_n1;
static long nodes, node_limit;

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

static int ip(int i, int j)
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
                    int fs[2] = {f, -f};
                    int nf = (f == 0) ? 1 : 2;
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

static void expand(u64 *P, int rsz, int *stack, u64 U)
{
    nodes++;
    if (found || nodes > node_limit)
        return;
    int psz = popc(P);
    int u = __builtin_popcountll(U);
    /* total <= rsz + psz + (40 - u) */
    if (rsz + psz + 40 - u < 41)
        return;
    if (rsz + (40 - u) >= 41 && rsz > 0) {
        found = 1;
        found_nE = rsz;
        found_n1 = 40 - u;
        memcpy(found_E, stack, (size_t)rsz * sizeof(int));
        best_total = rsz + found_n1;
        return;
    }
    if (psz == 0)
        return;
    int ord[MAXN], col[MAXN];
    int m = colour_order(P, ord, col);
    u64 Q[W];
    memcpy(Q, P, nwords * sizeof(u64));
    for (int i = m - 1; i >= 0; i--) {
        if (found || nodes > node_limit)
            return;
        /* colour bound on extras only; still need |E| >= |U|+1 */
        if (rsz + col[i] + 40 - u < 41)
            return;
        int v = ord[i];
        u64 P2[W];
        for (int w = 0; w < nwords; w++)
            P2[w] = Q[w] & adj[v][w];
        stack[rsz] = v;
        expand(P2, rsz + 1, stack, U | miss[v]);
        bit_clear(Q, v);
    }
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s <d> [node_limit]\n", argv[0]);
        return 1;
    }
    d = atoi(argv[1]);
    node_limit = (argc >= 3) ? atol(argv[2]) : 20000000L;
    target_norm = 2 * d * d;
    thresh = d * d;
    enumerate();

    /* Mark D5: two coords ±d, rest 0. */
    nD = 0;
    int Dlist[64];
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
    for (int i = 0; i < n; i++) {
        if (isD[i])
            continue;
        eidx[nE] = i;
        u64 msk = 0;
        for (int j = 0; j < nD; j++) {
            if (ip(i, Dlist[j]) > thresh)
                msk |= 1ULL << j;
        }
        miss[nE] = msk;
        nE++;
    }
    nwords = (nE + 63) / 64;
    memset(adj, 0, sizeof adj);
    long edges = 0;
    for (int i = 0; i < nE; i++) {
        for (int j = i + 1; j < nE; j++) {
            if (ip(eidx[i], eidx[j]) <= thresh) {
                adj[i][j >> 6] |= 1ULL << (j & 63);
                adj[j][i >> 6] |= 1ULL << (i & 63);
                edges++;
            }
        }
    }

    best_total = 40;
    found = 0;
    nodes = 0;
    u64 P[W];
    memset(P, 0, sizeof P);
    for (int i = 0; i < nE; i++)
        P[i >> 6] |= 1ULL << (i & 63);
    int stack[MAXN];
    expand(P, 0, stack, 0);

    printf("{\n");
    printf("  \"d\": %d,\n", d);
    printf("  \"n\": %d,\n", n);
    printf("  \"n_d5\": %d,\n", nD);
    printf("  \"n_extras\": %d,\n", nE);
    printf("  \"n_edges_extras\": %ld,\n", edges);
    printf("  \"nodes\": %ld,\n", nodes);
    printf("  \"node_limit\": %ld,\n", node_limit);
    printf("  \"best_total\": %d,\n", best_total);
    printf("  \"found_41\": %s,\n", found ? "true" : "false");
    printf("  \"complete\": %s,\n", (found || nodes <= node_limit) ? "true" : "false");
    printf("  \"found_nE\": %d,\n", found_nE);
    printf("  \"found_n1\": %d,\n", found_n1);
    printf("  \"comment\": \"extras-clique search: total = |E| + (40-|union miss|); hunt >= 41\"\n");
    printf("}\n");
    return 0;
}
