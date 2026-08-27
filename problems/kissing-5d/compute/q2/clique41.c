/* Exact search for a clique of size TARGET in a dumped bitset graph.
 *
 * Input (stdin or argv[1]): the graphio.py text format.
 * Exit 0 always; writes JSON to stdout.
 *
 * Tomita-style coloured branch-and-bound.  Starts from a known lower
 * bound of 40 if the file header does not say otherwise, and hunts 41.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

#define MAXN 2048
#define W ((MAXN + 63) / 64)
#define TARGET 41

typedef uint64_t u64;

static int n, nwords;
static u64 adj[MAXN][W];
static int best;
static int found41;
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
    for (int i = 0; i < nwords; i++) {
        if (a[i])
            return i * 64 + __builtin_ctzll(a[i]);
    }
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

/* Greedy colouring of P: colour[v] is a 1-based colour, colours assigned
 * in decreasing order so the last remaining vertices have large colours.
 * Returns the number of colours used. */
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
            /* forbid neighbours of v from this colour class */
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
        /* no loops */
        bit_clear(adj[i], i);
        /* mask unused high bits */
        if (n & 63)
            adj[i][nwords - 1] &= (1ULL << (n & 63)) - 1;
    }
    /* symmetrise / drop one-way edges */
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
    FILE *fp = stdin;
    if (argc >= 2) {
        fp = fopen(argv[1], "r");
        if (!fp) {
            fprintf(stderr, "cannot open %s\n", argv[1]);
            return 1;
        }
    }
    if (!read_graph(fp)) {
        fprintf(stderr, "bad graph\n");
        return 1;
    }
    if (fp != stdin)
        fclose(fp);

    best = 40; /* known published codes */
    found41 = 0;
    nodes = 0;
    u64 P[W];
    memset(P, 0, sizeof P);
    for (int i = 0; i < n; i++)
        P[i >> 6] |= 1ULL << (i & 63);
    int stack[MAXN];
    expand(P, 0, stack);

    printf("{\n");
    printf("  \"n\": %d,\n", n);
    printf("  \"nodes\": %ld,\n", nodes);
    printf("  \"best\": %d,\n", best);
    printf("  \"found_41\": %s,\n", found41 ? "true" : "false");
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
