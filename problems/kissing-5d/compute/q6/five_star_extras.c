/* Leftover 41-set hosted by a 5-star union of D5 coordinate-stars.

 * q6 emptied every 4-star host (extras ω <= 19).  A remaining leftover
 * 41-set has star-cover at least 5.  This file searches each of the
 * 252 five-star pools for |E| >= 20 and |E| >= |U| + 1, |U| >= 19.
 *
 * Usage: ./five_star_extras [target] [node_limit] [shard] [nshards]
 * Default target=20, node_limit=20000000, shard=0, nshards=1.
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
static u64 stars[10];

static long nodes, node_limit = 20000000L;
static int found, best;
static int found_idx[64];
static u64 found_U;
static int slice_complete;

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
    fprintf(f, "  \"source\": \"q6 five_star_extras.c\",\n");
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
        if (rsz >= uk + 1 && rsz >= target && uk >= 19) {
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
        if (rsz + 1 >= target && rsz + 1 >= uk2 + 1 && uk2 >= 19) {
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
    int shard = 0, nshards = 1;
    if (argc >= 2)
        target = atoi(argv[1]);
    if (argc >= 3)
        node_limit = atol(argv[2]);
    if (argc >= 4)
        shard = atoi(argv[3]);
    if (argc >= 5)
        nshards = atoi(argv[4]);
    if (target < 19 || target > 40 || nshards < 1 || shard < 0 || shard >= nshards) {
        fprintf(stderr, "bad args\n");
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

    memset(stars, 0, sizeof stars);
    int ns = 0;
    for (int ax = 0; ax < 5; ax++) {
        for (int sg = -1; sg <= 1; sg += 2) {
            u64 bits = 0;
            for (int j = 0; j < nD; j++) {
                int i = Dlist[j];
                if (pts[i][ax] == sg * d)
                    bits |= 1ULL << j;
            }
            stars[ns++] = bits;
        }
    }

    mkdir("certs", 0755);
    int n_pools = 0, n_complete = 0, n_hit = 0, n_incomplete = 0;
    int any41 = 0;
    int max_best = 0;
    long tot_nodes = 0;

    printf("{\n");
    printf("  \"d\": 4,\n");
    printf("  \"n_extras\": %d,\n", nE);
    printf("  \"n_groups\": %d,\n", nG);
    printf("  \"target\": %d,\n", target);
    printf("  \"node_limit\": %ld,\n", node_limit);
    printf("  \"shard\": %d,\n  \"nshards\": %d,\n", shard, nshards);
    printf("  \"pools\": [\n");

    int pidx = 0;
    int first_pool = 1;
    for (int a = 0; a < 10; a++) {
        for (int b = a + 1; b < 10; b++) {
            for (int c = b + 1; c < 10; c++) {
                for (int e = c + 1; e < 10; e++) {
                for (int f = e + 1; f < 10; f++) {
                    if ((pidx++ % nshards) != shard)
                        continue;
                    u64 U4 = stars[a] | stars[b] | stars[c] | stars[e] | stars[f];
                    int k = __builtin_popcountll(U4);
                    u64 P[W];
                    memset(P, 0, sizeof P);
                    int nL = 0;
                    for (int v = 0; v < nE; v++) {
                        if ((miss[v] & ~U4) == 0) {
                            P[v >> 6] |= 1ULL << (v & 63);
                            nL++;
                        }
                    }
                    found = 0;
                    best = target - 1;
                    nodes = 0;
                    slice_complete = 1;
                    int stack[64];
                    expand(P, 0, stack, 0);
                    if (nodes > node_limit && !found)
                        slice_complete = 0;
                    if (best > max_best)
                        max_best = best;
                    tot_nodes += nodes;
                    n_pools++;
                    if (found) {
                        n_hit++;
                        any41 = 1;
                    } else if (slice_complete) {
                        n_complete++;
                    } else {
                        n_incomplete++;
                    }
                    if (!first_pool)
                        printf(",\n");
                    first_pool = 0;
                    printf("    {\"stars\": [%d, %d, %d, %d, %d], \"k\": %d, "
                           "\"n_extras\": %d, \"best\": %d, \"nodes\": %ld, "
                           "\"complete\": %s, \"found_41\": %s}",
                           a, b, c, e, f, k, nL, best, nodes,
                           slice_complete ? "true" : "false",
                           found ? "true" : "false");
                    fflush(stdout);
                    if (found)
                        goto done_pools;
                }
                }
            }
        }
    }
done_pools:
    printf("\n  ],\n");
    printf("  \"n_pools\": %d,\n", n_pools);
    printf("  \"n_bb_complete_empty\": %d,\n", n_complete);
    printf("  \"n_incomplete\": %d,\n", n_incomplete);
    printf("  \"n_hit\": %d,\n", n_hit);
    printf("  \"max_best\": %d,\n", max_best);
    printf("  \"tot_nodes\": %ld,\n", tot_nodes);
    printf("  \"found_41\": %s,\n", any41 ? "true" : "false");
    printf("  \"comment\": \"5-star leftover extras B&B; |E|>=20 and |E|>=|U|+1\"\n");
    printf("}\n");
    return 0;
}
