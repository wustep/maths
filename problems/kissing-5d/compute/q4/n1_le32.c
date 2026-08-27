/* Complete n1 <= 32 slices of the 1480-point (1/4)Z^5 extras graph.
 *
 * Same-missed extras form an independent set (verified at start).
 * A clique therefore takes at most one extra from each missed-set
 * group.  For each k-set U of D5 roots that contains at least one
 * actual missed set, if the number of seeds contained in U is < k+1,
 * the slice n1 = 40-k is empty for that U.  Otherwise a coloured
 * branch-and-bound hunts a clique of size k+1 in the pool.
 *
 * Usage: ./n1_le32 [kmin] [kmax]
 * Default kmin=8, kmax=8 (the first unfinished leftover).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAXN 2048
#define MAXE 1600
#define MAXG 512
#define W ((MAXN + 63) / 64)

typedef uint64_t u64;

static int d = 4, thresh, target_norm;
static int n, nD, nE;
static int pts[MAXN][5];
static int isD[MAXN];
static int Dlist[64];
static int eidx[MAXE];
static u64 miss[MAXE];
static int g_of[MAXE];
static u64 seeds[MAXG];
static int gsize[MAXG];
static int gmem[MAXG][16];
static int nG;
static u64 adj[MAXE][W];
static int nwords;

static long nodes, node_limit = 2000000L;
static int found, best, target;
static int found_idx[64];

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

static void expand(u64 *P, int rsz, int *stack, u64 used_groups)
{
    nodes++;
    if (found || nodes > node_limit)
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
        if (found || nodes > node_limit)
            return;
        if (rsz + col[i] <= best)
            return;
        int v = ord[i];
        int g = g_of[v];
        u64 P2[W];
        for (int w = 0; w < nwords; w++)
            P2[w] = Q[w] & adj[v][w];
        /* drop the rest of group g from P2 */
        for (int t = 0; t < gsize[g]; t++)
            bit_clear(P2, gmem[g][t]);
        stack[rsz] = v;
        if (rsz + 1 >= target) {
            found = 1;
            best = rsz + 1;
            memcpy(found_idx, stack, (size_t)target * sizeof(int));
            return;
        }
        expand(P2, rsz + 1, stack, used_groups | (1ULL << g));
        bit_clear(Q, v);
    }
}

static int cmp_u64(const void *a, const void *b)
{
    u64 x = *(const u64 *)a, y = *(const u64 *)b;
    return (x > y) - (x < y);
}

static void choose_from(const int *rest, int nrest, int need, u64 base,
                        u64 *out, int *nout)
{
    int idx[16];
    if (need == 0) {
        out[(*nout)++] = base;
        return;
    }
    for (int i = 0; i < need; i++)
        idx[i] = i;
    for (;;) {
        u64 U = base;
        for (int i = 0; i < need; i++)
            U |= 1ULL << rest[idx[i]];
        out[(*nout)++] = U;
        int p = need - 1;
        while (p >= 0 && idx[p] == nrest - need + p)
            p--;
        if (p < 0)
            break;
        idx[p]++;
        for (int q = p + 1; q < need; q++)
            idx[q] = idx[q - 1] + 1;
    }
}

int main(int argc, char **argv)
{
    int kmin = 8, kmax = 8;
    if (argc >= 2)
        kmin = atoi(argv[1]);
    if (argc >= 3)
        kmax = atoi(argv[2]);
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
    long edges = 0, intra = 0;
    for (int i = 0; i < nE; i++) {
        for (int j = i + 1; j < nE; j++) {
            if (ip_pts(eidx[i], eidx[j]) <= thresh) {
                adj[i][j >> 6] |= 1ULL << (j & 63);
                adj[j][i >> 6] |= 1ULL << (i & 63);
                edges++;
                if (g_of[i] == g_of[j])
                    intra++;
            }
        }
    }

    printf("{\n");
    printf("  \"d\": %d,\n", d);
    printf("  \"n\": %d,\n", n);
    printf("  \"n_d5\": %d,\n", nD);
    printf("  \"n_extras\": %d,\n", nE);
    printf("  \"n_groups\": %d,\n", nG);
    printf("  \"n_extra_edges\": %ld,\n", edges);
    printf("  \"n_intra_group_edges\": %ld,\n", intra);
    printf("  \"groups_edgeless\": %s,\n", intra == 0 ? "true" : "false");
    printf("  \"slices\": {\n");

    int any41 = 0;
    int all_complete = 1;
    for (int k = kmin; k <= kmax; k++) {
        int cap = 12000000;
        u64 *Us = malloc((size_t)cap * sizeof(u64));
        if (!Us) {
            fprintf(stderr, "oom\n");
            return 1;
        }
        int nU = 0;
        for (int g = 0; g < nG; g++) {
            int pop = __builtin_popcountll(seeds[g]);
            if (pop > k)
                continue;
            int rest[40], nrest = 0;
            for (int i = 0; i < 40; i++)
                if (!((seeds[g] >> i) & 1ULL))
                    rest[nrest++] = i;
            int need = k - pop;
            if (nU + 2000000 > cap) {
                fprintf(stderr, "U cap\n");
                return 1;
            }
            choose_from(rest, nrest, need, seeds[g], Us, &nU);
        }
        qsort(Us, (size_t)nU, sizeof(u64), cmp_u64);
        int uniq = 0;
        for (int i = 0; i < nU; i++)
            if (i == 0 || Us[i] != Us[i - 1])
                Us[uniq++] = Us[i];
        nU = uniq;

        int tried = 0, skipped = 0;
        int best_ex = 0, slice_found = 0, slice_complete = 1;
        int max_seeds = 0;
        target = k + 1;
        for (int ui = 0; ui < nU; ui++) {
            u64 U = Us[ui];
            int ng = 0;
            int gsel[MAXG];
            for (int g = 0; g < nG; g++)
                if ((seeds[g] & ~U) == 0)
                    gsel[ng++] = g;
            if (ng > max_seeds)
                max_seeds = ng;
            if (ng < target) {
                skipped++;
                continue;
            }
            /* pool bitset */
            u64 P[W];
            memset(P, 0, sizeof P);
            int psz = 0;
            for (int t = 0; t < ng; t++) {
                int g = gsel[t];
                for (int s = 0; s < gsize[g]; s++) {
                    int v = gmem[g][s];
                    P[v >> 6] |= 1ULL << (v & 63);
                    psz++;
                }
            }
            if (psz < target)
                continue;
            tried++;
            found = 0;
            best = target - 1;
            if (best_ex > best)
                best = best_ex;
            nodes = 0;
            int stack[64];
            expand(P, 0, stack, 0);
            if (best > best_ex)
                best_ex = best;
            if (!(found || nodes <= node_limit))
                slice_complete = 0;
            if (found) {
                slice_found = 1;
                any41 = 1;
                break;
            }
        }
        free(Us);
        all_complete = all_complete && slice_complete && !slice_found;
        printf("    \"%d\": {\"k\": %d, \"n1\": %d, \"n_U\": %d, \"tried\": %d, "
               "\"skipped_few_groups\": %d, \"max_seeds_in_U\": %d, "
               "\"best_extras\": %d, \"best_total\": %d, \"found\": %s, "
               "\"complete\": %s}%s\n",
               k, k, 40 - k, nU, tried, skipped, max_seeds, best_ex,
               best_ex + (40 - k),
               slice_found ? "true" : "false",
               slice_complete && !slice_found ? "true" : "false",
               k < kmax ? "," : "");
        fflush(stdout);
        if (slice_found)
            break;
    }
    printf("  },\n");
    printf("  \"found_41\": %s,\n", any41 ? "true" : "false");
    printf("  \"complete\": %s,\n", all_complete && !any41 ? "true" : "false");
    printf("  \"comment\": \"complete k-supersets of actual missed sets; "
           "groups are independent so a clique takes at most one extra per seed\"\n");
    printf("}\n");
    return 0;
}
