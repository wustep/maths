/* Exact 36-cliques that share s vertices with a published 35.
 *
 * Usage: ./t5_share <adj.txt> <published.json> <share> [node_limit]
 *
 * For each published 35-clique P and each (35-share)-subset L of P,
 * S = P \ L has size share.  A 36-clique meeting P in S is S plus a
 * (36-share)-clique in the common neighbourhood of S minus S.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 512
#define W ((MAXN + 63) / 64)

typedef uint64_t u64;

static int n, nwords, target;
static u64 adj[MAXN][W];
static int best, found;
static long nodes, node_limit;
static int found_idx[64];

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

static int bit_test(const u64 *a, int v)
{
    return (int)((a[v >> 6] >> (v & 63)) & 1U);
}

static void bit_set(u64 *a, int v)
{
    a[v >> 6] |= 1ULL << (v & 63);
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
        u64 P2[W];
        for (int w = 0; w < nwords; w++)
            P2[w] = Q[w] & adj[v][w];
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

static int read_graph(FILE *fp)
{
    if (fscanf(fp, "%d", &n) != 1)
        return 0;
    if (n <= 0 || n > MAXN)
        return 0;
    nwords = (n + 63) / 64;
    memset(adj, 0, sizeof adj);
    for (int i = 0; i < n; i++) {
        for (int w = 0; w < nwords; w++) {
            unsigned long long x;
            if (fscanf(fp, "%llx", &x) != 1)
                return 0;
            adj[i][w] = (u64)x;
        }
        bit_clear(adj[i], i);
    }
    return 1;
}

static int parse_published(const char *path, int cl[4][40], int *ncl)
{
    FILE *f = fopen(path, "r");
    if (!f)
        return 0;
    char buf[1 << 16];
    size_t m = fread(buf, 1, sizeof buf - 1, f);
    buf[m] = 0;
    fclose(f);
    *ncl = 0;
    const char *p = buf;
    while (*p && *ncl < 4) {
        const char *r = strstr(p, "remainder_clique");
        if (!r)
            break;
        r = strchr(r, '[');
        if (!r)
            break;
        r++;
        int k = 0;
        while (*r && *r != ']') {
            if (*r >= '0' && *r <= '9') {
                int v = 0;
                while (*r >= '0' && *r <= '9') {
                    v = v * 10 + (*r - '0');
                    r++;
                }
                if (k < 40)
                    cl[*ncl][k++] = v;
            } else {
                r++;
            }
        }
        if (k == 35)
            (*ncl)++;
        p = r;
    }
    return *ncl == 4;
}

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr, "usage: %s adj.txt published.json share [node_limit]\n",
                argv[0]);
        return 1;
    }
    FILE *fp = fopen(argv[1], "r");
    if (!fp || !read_graph(fp)) {
        fprintf(stderr, "bad graph\n");
        return 1;
    }
    fclose(fp);
    int cl[4][40], ncl;
    if (!parse_published(argv[2], cl, &ncl)) {
        fprintf(stderr, "bad published json (need 4 remainder 35-cliques)\n");
        return 1;
    }
    int share = atoi(argv[3]);
    node_limit = (argc >= 5) ? atol(argv[4]) : 200000L;
    if (share < 20 || share > 34) {
        fprintf(stderr, "share out of range\n");
        return 1;
    }
    int leave = 35 - share;
    int need = 36 - share;
    long tried = 0, empty = 0, incomplete = 0, hits = 0;
    int best_out = 0;
    int comb[16];

    printf("{\n  \"n\": %d,\n  \"share\": %d,\n  \"leave\": %d, \"need\": %d,\n",
           n, share, leave, need);
    printf("  \"by_code\": {\n");

    for (int c = 0; c < ncl; c++) {
        long c_tried = 0, c_empty = 0, c_inc = 0, c_hit = 0;
        int c_best = 0;
        /* enumerate leave-subsets of the 35 */
        for (int i = 0; i < leave; i++)
            comb[i] = i;
        for (;;) {
            u64 S[W];
            memset(S, 0, sizeof S);
            int inL[MAXN];
            memset(inL, 0, sizeof inL);
            for (int i = 0; i < leave; i++)
                inL[cl[c][comb[i]]] = 1;
            for (int i = 0; i < 35; i++)
                if (!inL[cl[c][i]])
                    bit_set(S, cl[c][i]);
            u64 N[W];
            memset(N, 0xFF, sizeof N);
            if (n & 63)
                N[nwords - 1] = (1ULL << (n & 63)) - 1;
            else
                N[nwords - 1] = ~0ULL;
            for (int i = 0; i < 35; i++) {
                int v = cl[c][i];
                if (inL[v])
                    continue;
                for (int w = 0; w < nwords; w++)
                    N[w] &= adj[v][w];
            }
            for (int w = 0; w < nwords; w++)
                N[w] &= ~S[w];
            target = need;
            found = 0;
            best = need - 1;
            if (c_best > best)
                best = c_best;
            nodes = 0;
            int stack[64];
            expand(N, 0, stack);
            c_tried++;
            tried++;
            if (best > c_best)
                c_best = best;
            if (best > best_out)
                best_out = best;
            if (found) {
                c_hit++;
                hits++;
            } else if (nodes > node_limit) {
                c_inc++;
                incomplete++;
            } else {
                c_empty++;
                empty++;
            }
            /* next combination */
            int i = leave - 1;
            while (i >= 0 && comb[i] == 35 - leave + i)
                i--;
            if (i < 0)
                break;
            comb[i]++;
            for (int j = i + 1; j < leave; j++)
                comb[j] = comb[j - 1] + 1;
        }
        if (c)
            printf(",\n");
        printf("    \"%d\": {\"tried\": %ld, \"empty\": %ld, \"incomplete\": %ld, "
               "\"found\": %ld, \"best_extra\": %d, \"complete\": %s}",
               c, c_tried, c_empty, c_inc, c_hit, c_best,
               c_inc == 0 && c_hit == 0 ? "true" : "false");
        fprintf(stderr, "code %d tried=%ld empty=%ld inc=%ld hit=%ld best=%d\n",
                c, c_tried, c_empty, c_inc, c_hit, c_best);
    }
    printf("\n  },\n");
    printf("  \"tried\": %ld,\n  \"empty\": %ld,\n  \"incomplete\": %ld,\n",
           tried, empty, incomplete);
    printf("  \"found_36\": %s,\n", hits ? "true" : "false");
    printf("  \"best_extra\": %d,\n", best_out);
    printf("  \"complete\": %s\n}\n",
           incomplete == 0 && hits == 0 ? "true" : "false");
    return 0;
}
