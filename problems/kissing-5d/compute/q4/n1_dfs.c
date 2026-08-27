/* Hash-free complete leftover 1480-graph scan.

 * Every missed-union extras can realise is a union of the 240 seeds.
 * Generate each seed-union exactly once: start from the least-index
 * contained seed, then add later seeds that are not already contained.
 * If a smaller-index seed becomes contained, the branch is non-canonical
 * and is pruned.  No hash table, so |U| is not capped by RAM.
 *
 * Usage: ./n1_dfs [maxk]
 * Default maxk=15.
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
static int n, nD, nE, nG, nwords, maxk;
static int pts[MAXN][5];
static int isD[MAXN];
static int Dlist[64];
static int eidx[MAXE];
static u64 miss[MAXE];
static int g_of[MAXE];
static u64 seeds[MAXG];
static int gsize[MAXG];
static int gmem[MAXG][16];
static u64 all_seeds_mask[4];
static u64 through4[40][4];
static u64 adj[MAXE][W];
static u64 stars[10];
static int n_stars;

static long nodes, node_limit = 50000000L;
static int found, best, target;
static int found_idx[64];
static int found_k, found_n1;
static int any41;

static long n_seen;
static long n_unions[41], n_prom[41], n_tried[41];
static int max_seeds[41], best_ex[41], slice_found[41], slice_complete[41];

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

static void expand(u64 *P, int rsz, int *stack)
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
        for (int t = 0; t < gsize[g]; t++)
            bit_clear(P2, gmem[g][t]);
        stack[rsz] = v;
        if (rsz + 1 >= target) {
            found = 1;
            best = rsz + 1;
            memcpy(found_idx, stack, (size_t)target * sizeof(int));
            return;
        }
        expand(P2, rsz + 1, stack);
        bit_clear(Q, v);
    }
}

static int contained_bits(u64 U, u64 out[4])
{
    u64 dead[4] = {0, 0, 0, 0};
    for (int r = 0; r < 40; r++) {
        if (!((U >> r) & 1ULL)) {
            dead[0] |= through4[r][0];
            dead[1] |= through4[r][1];
            dead[2] |= through4[r][2];
            dead[3] |= through4[r][3];
        }
    }
    out[0] = all_seeds_mask[0] & ~dead[0];
    out[1] = all_seeds_mask[1] & ~dead[1];
    out[2] = all_seeds_mask[2] & ~dead[2];
    out[3] = all_seeds_mask[3] & ~dead[3];
    return __builtin_popcountll(out[0]) + __builtin_popcountll(out[1])
         + __builtin_popcountll(out[2]) + __builtin_popcountll(out[3]);
}

/* Last irredundant seed of X, and the union of the earlier ones. */
static int canon_last_parent(u64 X, u64 *parent)
{
    u64 run = 0;
    int last = -1;
    u64 prev = 0;
    for (int h = 0; h < nG; h++) {
        if ((seeds[h] & ~X) == 0 && (seeds[h] & ~run) != 0) {
            prev = run;
            last = h;
            run |= seeds[h];
        }
    }
    *parent = prev;
    return last;
}

static void write_code41(void)
{
    FILE *f = fopen("certs/code41.json", "w");
    if (!f)
        return;
    fprintf(f, "{\n  \"n\": 41,\n  \"model\": \"integer a in Z^5, a.a=32, edge iff a.b<=16\",\n");
    fprintf(f, "  \"n_extras\": %d,\n  \"n1\": %d,\n  \"points\": [\n",
            target, found_n1);
    int first = 1;
    for (int t = 0; t < target; t++) {
        int ei = found_idx[t];
        int i = eidx[ei];
        if (!first)
            fprintf(f, ",\n");
        first = 0;
        fprintf(f, "    [%d, %d, %d, %d, %d]",
                pts[i][0], pts[i][1], pts[i][2], pts[i][3], pts[i][4]);
    }
    u64 U = 0;
    for (int t = 0; t < target; t++)
        U |= miss[found_idx[t]];
    for (int j = 0; j < nD; j++) {
        if ((U >> j) & 1ULL)
            continue;
        int i = Dlist[j];
        if (!first)
            fprintf(f, ",\n");
        first = 0;
        fprintf(f, "    [%d, %d, %d, %d, %d]",
                pts[i][0], pts[i][1], pts[i][2], pts[i][3], pts[i][4]);
    }
    fprintf(f, "\n  ]\n}\n");
    fclose(f);
}

static void process(u64 U, int ns, const u64 bits[4])
{
    int k = __builtin_popcountll(U);
    n_seen++;
    if ((n_seen & ((1L << 20) - 1)) == 0)
        fprintf(stderr, "dfs seen=%ld k=%d ns=%d\n", n_seen, k, ns);
    if (k <= 40) {
        n_unions[k]++;
        if (ns > max_seeds[k])
            max_seeds[k] = ns;
    }
    if (k < 4 || k > 40 || ns < k + 1 || any41)
        return;
    n_prom[k]++;
    u64 P[W];
    memset(P, 0, sizeof P);
    int psz = 0;
    for (int limb = 0; limb < 4; limb++) {
        u64 b = bits[limb];
        while (b) {
            int g = limb * 64 + __builtin_ctzll(b);
            b &= b - 1;
            for (int s = 0; s < gsize[g]; s++) {
                int v = gmem[g][s];
                P[v >> 6] |= 1ULL << (v & 63);
                psz++;
            }
        }
    }
    target = k + 1;
    if (psz < target)
        return;
    n_tried[k]++;
    found = 0;
    best = target - 1;
    if (best_ex[k] > best)
        best = best_ex[k];
    nodes = 0;
    int stack[64];
    expand(P, 0, stack);
    if (best > best_ex[k])
        best_ex[k] = best;
    if (!(found || nodes <= node_limit))
        slice_complete[k] = 0;
    if (found) {
        slice_found[k] = 1;
        any41 = 1;
        found_k = k;
        found_n1 = 40 - k;
        write_code41();
    }
}

static void rec(u64 U, int last)
{
    u64 bits[4];
    int ns = contained_bits(U, bits);
    process(U, ns, bits);
    int k = __builtin_popcountll(U);
    if (k >= maxk || any41)
        return;
    for (int g = last + 1; g < nG; g++) {
        if ((seeds[g] & ~U) == 0)
            continue;
        u64 U2 = U | seeds[g];
        if ((int)__builtin_popcountll(U2) > maxk)
            continue;
        u64 par;
        if (canon_last_parent(U2, &par) != g || par != U)
            continue;
        rec(U2, g);
    }
}

int main(int argc, char **argv)
{
    maxk = 15;
    if (argc >= 2)
        maxk = atoi(argv[1]);
    if (maxk < 4 || maxk > 40) {
        fprintf(stderr, "maxk out of range\n");
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

    n_stars = 0;
    for (int axis = 0; axis < 5; axis++) {
        for (int s = -1; s <= 1; s += 2) {
            u64 m = 0;
            int cnt = 0;
            for (int j = 0; j < nD; j++) {
                if (pts[Dlist[j]][axis] == s * d) {
                    m |= 1ULL << j;
                    cnt++;
                }
            }
            if (cnt != 8) {
                fprintf(stderr, "star axis %d s %d size %d\n", axis, s, cnt);
                return 1;
            }
            stars[n_stars++] = m;
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

    memset(through4, 0, sizeof through4);
    memset(all_seeds_mask, 0, sizeof all_seeds_mask);
    for (int g = 0; g < nG; g++) {
        all_seeds_mask[g >> 6] |= 1ULL << (g & 63);
        u64 m = seeds[g];
        while (m) {
            int r = __builtin_ctzll(m);
            through4[r][g >> 6] |= 1ULL << (g & 63);
            m &= m - 1;
        }
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

    memset(n_unions, 0, sizeof n_unions);
    memset(n_prom, 0, sizeof n_prom);
    memset(n_tried, 0, sizeof n_tried);
    memset(max_seeds, 0, sizeof max_seeds);
    memset(best_ex, 0, sizeof best_ex);
    memset(slice_found, 0, sizeof slice_found);
    for (int i = 0; i < 41; i++)
        slice_complete[i] = 1;

    mkdir("certs", 0755);
    any41 = 0;
    n_seen = 0;
    for (int g0 = 0; g0 < nG && !any41; g0++) {
        u64 par;
        if (canon_last_parent(seeds[g0], &par) != g0)
            continue;
        rec(seeds[g0], g0);
    }

    int all_complete = 1;
    for (int k = 4; k <= maxk; k++)
        all_complete = all_complete && slice_complete[k] && !slice_found[k];

    printf("{\n");
    printf("  \"d\": %d,\n", d);
    printf("  \"n\": %d,\n", n);
    printf("  \"n_d5\": %d,\n", nD);
    printf("  \"n_extras\": %d,\n", nE);
    printf("  \"n_groups\": %d,\n", nG);
    printf("  \"n_stars\": %d,\n", n_stars);
    printf("  \"n_extra_edges\": %ld,\n", edges);
    printf("  \"n_intra_group_edges\": %ld,\n", intra);
    printf("  \"groups_edgeless\": %s,\n", intra == 0 ? "true" : "false");
    printf("  \"maxk\": %d,\n", maxk);
    printf("  \"n_unions_visited\": %ld,\n", n_seen);
    printf("  \"algorithm\": \"canonical-dfs\",\n");
    printf("  \"slices\": {\n");
    int first = 1;
    for (int k = 4; k <= maxk; k++) {
        if (!first)
            printf(",\n");
        first = 0;
        printf("    \"%d\": {\"k\": %d, \"n1\": %d, \"n_unions\": %ld, "
               "\"n_promising\": %ld, \"tried\": %ld, \"max_seeds\": %d, "
               "\"best_extras\": %d, \"best_total\": %d, \"found\": %s, "
               "\"complete\": %s, \"empty_by_part_count\": %s}",
               k, k, 40 - k, n_unions[k], n_prom[k], n_tried[k],
               max_seeds[k], best_ex[k], best_ex[k] + (40 - k),
               slice_found[k] ? "true" : "false",
               slice_complete[k] && !slice_found[k] ? "true" : "false",
               max_seeds[k] < k + 1 ? "true" : "false");
    }
    printf("\n  },\n");
    printf("  \"found_41\": %s,\n", any41 ? "true" : "false");
    printf("  \"complete\": %s,\n", all_complete && !any41 ? "true" : "false");
    printf("  \"comment\": \"every seed-union with |U|<=maxk by canonical "
           "DFS; a 41-set needs |E|>=|U|+1 extras whose missed sets sit "
           "in U\"\n");
    printf("}\n");
    return 0;
}
