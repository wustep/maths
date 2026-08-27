/* Kissing graph on (1/d) Z^5 intersect the sphere |x|^2 = 2.
 *
 * Integer model: a in Z^5, a·a = 2 d^2, edge iff a·b <= d^2 (and a != b).
 * Exact 41-clique search, same coloured B&B as clique41.c.
 *
 * Usage: ./sphere_clique <d>
 * d = 2 is the half-integer sphere (200 points; contains D5 and L5).
 * d = 4 is 1480 points.  Larger d is accepted but may not finish.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAXN 2048
#define W ((MAXN + 63) / 64)
#define TARGET 41

typedef uint64_t u64;

static int n, nwords, d, thresh, target_norm;
static int pts[MAXN][5];
static u64 adj[MAXN][W];
static int best, found41;
static int found_idx[TARGET];
static long nodes;

static int popc(const u64 *a)
{
    int s = 0;
    for (int i = 0; i < nwords; i++)
        s += __builtin_popcountll(a[i]);
    return s;
}

static void band(u64 *dst, const u64 *a, const u64 *b)
{
    for (int i = 0; i < nwords; i++)
        dst[i] = a[i] & b[i];
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
    int m = 0;
    int c = 0;
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

static void expand(u64 *P, int rsz, int *stack)
{
    nodes++;
    if (found41)
        return;
    int psz = popc(P);
    if (rsz + psz <= best)
        return;
    if (psz == 0) {
        if (rsz > best)
            best = rsz;
        return;
    }
    int ord[MAXN], col[MAXN];
    int m = colour_order(P, ord, col);
    u64 Q[W];
    memcpy(Q, P, nwords * sizeof(u64));
    for (int i = m - 1; i >= 0; i--) {
        if (found41)
            return;
        if (rsz + col[i] <= best)
            return;
        int v = ord[i];
        u64 P2[W];
        band(P2, Q, adj[v]);
        stack[rsz] = v;
        if (rsz + 1 >= TARGET) {
            found41 = 1;
            best = rsz + 1;
            memcpy(found_idx, stack, TARGET * sizeof(int));
            return;
        }
        expand(P2, rsz + 1, stack);
        bit_clear(Q, v);
    }
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
                        if (n >= MAXN) {
                            fprintf(stderr, "MAXN %d too small for d=%d\n", MAXN, d);
                            exit(1);
                        }
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

static int ip(int i, int j)
{
    int s = 0;
    for (int k = 0; k < 5; k++)
        s += pts[i][k] * pts[j][k];
    return s;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s <d>\n", argv[0]);
        return 1;
    }
    d = atoi(argv[1]);
    if (d < 1 || d > 20) {
        fprintf(stderr, "d out of range\n");
        return 1;
    }
    target_norm = 2 * d * d;
    thresh = d * d;
    enumerate();
    nwords = (n + 63) / 64;
    memset(adj, 0, sizeof adj);
    long edges = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (ip(i, j) <= thresh) {
                adj[i][j >> 6] |= 1ULL << (j & 63);
                adj[j][i >> 6] |= 1ULL << (i & 63);
                edges++;
            }
        }
    }

    best = 40;
    found41 = 0;
    nodes = 0;
    u64 P[W];
    memset(P, 0, sizeof P);
    for (int i = 0; i < n; i++)
        P[i >> 6] |= 1ULL << (i & 63);
    int stack[MAXN];
    expand(P, 0, stack);

    printf("{\n");
    printf("  \"d\": %d,\n", d);
    printf("  \"n\": %d,\n", n);
    printf("  \"n_edges\": %ld,\n", edges);
    printf("  \"nodes\": %ld,\n", nodes);
    printf("  \"best\": %d,\n", best);
    printf("  \"found_41\": %s,\n", found41 ? "true" : "false");
    printf("  \"comment\": \"(1/%d)Z^5 on |x|^2=2; kissing iff <a,b> <= %d\",\n",
           d, thresh);
    printf("  \"clique41\": [");
    if (found41) {
        for (int i = 0; i < TARGET; i++) {
            if (i)
                printf(", ");
            printf("%d", found_idx[i]);
        }
    }
    printf("]\n}\n");
    return 0;
}
