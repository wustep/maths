/* Coloured branch-and-bound for a clique of given target.
 *
 * Usage: ./clique <graph.txt> <target> [node_limit]
 * Graph format: graphio.py (n, then n lines of little-endian hex words).
 * Exit 0; JSON on stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 2048
#define W ((MAXN + 63) / 64)

typedef uint64_t u64;

static int n, nwords, target;
static u64 adj[MAXN][W];
static int best, found;
static int found_idx[MAXN];
static long nodes, node_limit;

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

static int bit_test(const u64 *a, int v)
{
    return (a[v >> 6] >> (v & 63)) & 1U;
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
        band(P2, Q, adj[v]);
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
        if (n & 63)
            adj[i][nwords - 1] &= (1ULL << (n & 63)) - 1;
    }
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            int a = bit_test(adj[i], j);
            int b = bit_test(adj[j], i);
            if (!a || !b) {
                bit_clear(adj[i], j);
                bit_clear(adj[j], i);
            }
        }
    return 1;
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s <graph.txt> <target> [node_limit]\n", argv[0]);
        return 1;
    }
    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        fprintf(stderr, "cannot open %s\n", argv[1]);
        return 1;
    }
    if (!read_graph(fp)) {
        fprintf(stderr, "bad graph\n");
        return 1;
    }
    fclose(fp);
    target = atoi(argv[2]);
    node_limit = (argc >= 4) ? atol(argv[3]) : 20000000L;
    if (target < 1 || target > n) {
        fprintf(stderr, "bad target\n");
        return 1;
    }
    best = target - 1;
    found = 0;
    nodes = 0;
    u64 P[W];
    memset(P, 0, sizeof P);
    for (int i = 0; i < n; i++)
        P[i >> 6] |= 1ULL << (i & 63);
    int stack[MAXN];
    expand(P, 0, stack);

    printf("{\n");
    printf("  \"n\": %d,\n", n);
    printf("  \"target\": %d,\n", target);
    printf("  \"nodes\": %ld,\n", nodes);
    printf("  \"node_limit\": %ld,\n", node_limit);
    printf("  \"best\": %d,\n", best);
    printf("  \"found\": %s,\n", found ? "true" : "false");
    printf("  \"complete\": %s,\n", (found || nodes <= node_limit) ? "true" : "false");
    printf("  \"clique\": [");
    if (found) {
        for (int i = 0; i < target; i++) {
            if (i)
                printf(", ");
            printf("%d", found_idx[i]);
        }
    }
    printf("]\n}\n");
    return 0;
}
