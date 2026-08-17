/* Non-extension of each (5,5,42)-graph in r55_42some.g6 and its complement.

   gcc -O3 -std=c11 -o extend_check extend_check.c
   ./extend_check refs/r55_42some.g6
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 18
#define DEG_HI 24
#define MAXK 8000

static uint64_t nbr[N];
static uint64_t k4[MAXK];
static uint64_t i4[MAXK];
static int nk4, ni4;
static int assign[N]; /* -1,0,1 */
static unsigned long long nodes, conflicts, decisions;
static int sat_found;

static int pop64(uint64_t x) { return __builtin_popcountll(x); }

static void list_k4(uint64_t *adj, uint64_t *out, int *nout) {
    int a, b, c, d;
    *nout = 0;
    for (a = 0; a < N; a++) {
        for (b = a + 1; b < N; b++) {
            if (!((adj[a] >> b) & 1ULL)) continue;
            uint64_t cab = adj[a] & adj[b];
            for (c = b + 1; c < N; c++) {
                if (!((cab >> c) & 1ULL)) continue;
                uint64_t cabc = cab & adj[c];
                for (d = c + 1; d < N; d++) {
                    if ((cabc >> d) & 1ULL) {
                        if (*nout >= MAXK) {
                            fprintf(stderr, "MAXK overflow\n");
                            exit(2);
                        }
                        out[(*nout)++] =
                            (1ULL << a) | (1ULL << b) | (1ULL << c) | (1ULL << d);
                    }
                }
            }
        }
    }
}

static int propagate(void) {
    int changed = 1;
    while (changed) {
        changed = 0;
        int ones = 0, zeros = 0;
        for (int i = 0; i < N; i++) {
            if (assign[i] == 1) ones++;
            else if (assign[i] == 0) zeros++;
        }
        if (ones > DEG_HI) return 0;
        if (zeros > N - DEG_LO) return 0;
        if (ones == DEG_HI) {
            for (int i = 0; i < N; i++)
                if (assign[i] == -1) {
                    assign[i] = 0;
                    changed = 1;
                }
            if (changed) continue;
        }
        if (zeros == N - DEG_LO) {
            for (int i = 0; i < N; i++)
                if (assign[i] == -1) {
                    assign[i] = 1;
                    changed = 1;
                }
            if (changed) continue;
        }
        for (int t = 0; t < nk4; t++) {
            uint64_t m = k4[t];
            int in_s = 0, nundef = 0, last = -1;
            while (m) {
                uint64_t b = m & -m;
                int v = __builtin_ctzll(b);
                if (assign[v] == 1) in_s++;
                else if (assign[v] == -1) {
                    nundef++;
                    last = v;
                }
                m ^= b;
            }
            if (in_s == 4) return 0;
            if (in_s == 3 && nundef == 1) {
                if (assign[last] == 1) return 0;
                if (assign[last] == -1) {
                    assign[last] = 0;
                    changed = 1;
                }
            }
        }
        for (int t = 0; t < ni4; t++) {
            uint64_t m = i4[t];
            int out_s = 0, nundef = 0, last = -1;
            while (m) {
                uint64_t b = m & -m;
                int v = __builtin_ctzll(b);
                if (assign[v] == 0) out_s++;
                else if (assign[v] == -1) {
                    nundef++;
                    last = v;
                }
                m ^= b;
            }
            if (out_s == 4) return 0;
            if (out_s == 3 && nundef == 1) {
                if (assign[last] == 0) return 0;
                if (assign[last] == -1) {
                    assign[last] = 1;
                    changed = 1;
                }
            }
        }
    }
    return 1;
}

static int score(int v) {
    uint64_t bit = 1ULL << v;
    int s = 0;
    for (int t = 0; t < nk4; t++)
        if (k4[t] & bit) s++;
    for (int t = 0; t < ni4; t++)
        if (i4[t] & bit) s++;
    return s;
}

static int rec(void) {
    nodes++;
    int snap[N];
    memcpy(snap, assign, sizeof(snap));
    if (!propagate()) {
        conflicts++;
        memcpy(assign, snap, sizeof(snap));
        return 0;
    }
    int undefs[N], nu = 0;
    for (int i = 0; i < N; i++)
        if (assign[i] == -1) undefs[nu++] = i;
    if (nu == 0) {
        int ones = 0;
        for (int i = 0; i < N; i++)
            if (assign[i] == 1) ones++;
        if (ones >= DEG_LO && ones <= DEG_HI) {
            sat_found = 1;
            return 1;
        }
        conflicts++;
        memcpy(assign, snap, sizeof(snap));
        return 0;
    }
    int best = undefs[0], bests = -1;
    for (int i = 0; i < nu; i++) {
        int sc = score(undefs[i]);
        if (sc > bests) {
            bests = sc;
            best = undefs[i];
        }
    }
    int after_prop[N];
    memcpy(after_prop, assign, sizeof(after_prop));
    for (int val = 1; val >= 0; val--) {
        memcpy(assign, after_prop, sizeof(after_prop));
        decisions++;
        assign[best] = val;
        if (rec()) return 1;
    }
    memcpy(assign, snap, sizeof(snap));
    return 0;
}

static int parse_graph6(const char *s, uint64_t *out) {
    if (!s || !s[0]) return -1;
    int n = (unsigned char)s[0] - 63;
    if (n != N) return -1;
    memset(out, 0, N * sizeof(uint64_t));
    int need = (N * (N - 1) / 2 + 5) / 6;
    int bitpos = 0;
    for (int j = 1; j < N; j++) {
        for (int i = 0; i < j; i++) {
            int byte = bitpos / 6;
            int off = 5 - (bitpos % 6);
            int bit = (((unsigned char)s[1 + byte] - 63) >> off) & 1;
            if (bit) {
                out[i] |= 1ULL << j;
                out[j] |= 1ULL << i;
            }
            bitpos++;
        }
    }
    (void)need;
    return 0;
}

static void complement_of(const uint64_t *in, uint64_t *out) {
    uint64_t full = (1ULL << N) - 1ULL;
    for (int i = 0; i < N; i++) out[i] = (full ^ (1ULL << i)) ^ in[i];
}

static int check_graph(uint64_t *adj, int *out_k4, int *out_i4) {
    uint64_t cadj[N];
    complement_of(adj, cadj);
    memcpy(nbr, adj, sizeof(nbr));
    list_k4(adj, k4, &nk4);
    list_k4(cadj, i4, &ni4);
    *out_k4 = nk4;
    *out_i4 = ni4;
    for (int i = 0; i < N; i++) assign[i] = -1;
    nodes = conflicts = decisions = 0;
    sat_found = 0;
    rec();
    return sat_found;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "refs/r55_42some.g6";
    FILE *f = fopen(path, "r");
    if (!f) {
        perror(path);
        return 2;
    }
    char line[512];
    int idx = 0;
    int any = 0;
    unsigned long long tot_nodes = 0;
    clock_t t0 = clock();
    printf("idx side k4 i4 sat decisions conflicts nodes sec\n");
    while (fgets(line, sizeof(line), f)) {
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n' || line[L - 1] == '\r')) line[--L] = 0;
        if (!L) continue;
        uint64_t adj[N], cadj[N];
        if (parse_graph6(line, adj) != 0) {
            fprintf(stderr, "bad graph6 line %d\n", idx);
            return 2;
        }
        complement_of(adj, cadj);
        for (int side = 0; side < 2; side++) {
            uint64_t *g = side ? cadj : adj;
            clock_t t1 = clock();
            int k4c, i4c;
            int sat = check_graph(g, &k4c, &i4c);
            double sec = (double)(clock() - t1) / CLOCKS_PER_SEC;
            tot_nodes += nodes;
            if (sat) any = 1;
            printf("%d %s %d %d %d %llu %llu %llu %.4f\n", idx,
                   side ? "comp" : "stored", k4c, i4c, sat, decisions, conflicts,
                   nodes, sec);
            fflush(stdout);
        }
        idx++;
    }
    fclose(f);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE graphs_pairs=%d any_extension=%d tot_nodes=%llu sec=%.3f\n",
           idx, any, tot_nodes, sec);
    return any ? 1 : 0;
}
