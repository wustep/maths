/* orbit_search_f.c -- prescribed-automorphism search with a general fixed space.
 *
 * sigma has odd prime order p in GL(r,2) and fixes a subspace of dimension c.
 * A sigma-invariant n-set is k full orbits of size p together with m of the
 * 2^c - 1 nonzero fixed vectors, so n = p*k + m.  Coverage, orbit-wise:
 *
 *   orbit i in S            covers orbit i
 *   sums inside orbit i     cover orb(rep_i ^ sigma^d rep_i), d = 1..p-1
 *   sums across i != j      cover orb(rep_i ^ sigma^d rep_j), d = 0..p-1
 *   orbit i with fixed g    covers orb(rep_i ^ g)          (a single orbit)
 *   fixed g in S            covers g
 *   fixed g with fixed h    covers g ^ h
 *
 * Any of the sums above may land on a fixed vector, which gets its own bit.
 * The outer loop runs over m-subsets of the fixed vectors; the inner DFS runs
 * over k-subsets of the orbits.  --force pins the first chosen orbit to a
 * centraliser class representative (sound because conjugating a solution by a
 * centraliser element gives another solution).
 *
 * Build: gcc -O2 -o orbit_search_f orbit_search_f.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXR 12
#define MAXNV (1 << MAXR)
#define MAXORB 200
#define MAXFIX 256
#define MW 4
#define MAXK 16

typedef struct { uint64_t w[MW]; } Mask;

static inline void m_or(Mask *a, const Mask *b) {
    for (int i = 0; i < MW; i++) a->w[i] |= b->w[i];
}
static inline void m_set(Mask *a, int b) { a->w[b >> 6] |= 1ULL << (b & 63); }
static inline int m_pop(const Mask *a) {
    int s = 0;
    for (int i = 0; i < MW; i++) s += __builtin_popcountll(a->w[i]);
    return s;
}
static inline int m_eq(const Mask *a, const Mask *b) {
    for (int i = 0; i < MW; i++) if (a->w[i] != b->w[i]) return 0;
    return 1;
}

static int R, NV, P, n_orb, NF, nbits;
static int sigma[MAXNV], oid[MAXNV], reps[MAXORB];
static int fixv[MAXFIX], fidx[MAXNV];
static Mask self_m[MAXORB], cross_m[MAXORB][MAXORB], full_m;
static Mask ofix[MAXORB][MAXFIX];        /* orbit i summed with fixed vector j */

static void load_sigma(const char *path) {
    FILE *fh = fopen(path, "r");
    if (!fh) { perror(path); exit(2); }
    int cols[MAXR];
    if (fscanf(fh, "%d", &R) != 1 || R < 2 || R > MAXR) { fprintf(stderr, "bad r\n"); exit(2); }
    for (int i = 0; i < R; i++)
        if (fscanf(fh, "%d", &cols[i]) != 1) { fprintf(stderr, "bad sigma\n"); exit(2); }
    fclose(fh);
    NV = 1 << R;
    for (int v = 0; v < NV; v++) {
        int out = 0;
        for (int i = 0; i < R; i++) if ((v >> i) & 1) out ^= cols[i];
        sigma[v] = out;
    }
}

static void build_orbits(void) {
    NF = 0;
    for (int v = 0; v < NV; v++) fidx[v] = -1;
    for (int v = 1; v < NV; v++) if (sigma[v] == v) { fidx[v] = NF; fixv[NF++] = v; }
    if (NF >= MAXFIX) { fprintf(stderr, "fixed space too big\n"); exit(2); }
    for (int v = 0; v < NV; v++) oid[v] = -1;
    P = 0;
    n_orb = 0;
    for (int v = 1; v < NV; v++) {
        if (fidx[v] >= 0 || oid[v] >= 0) continue;
        int u = sigma[v], len = 1;
        while (u != v) { u = sigma[u]; len++; }
        if (!P) P = len;
        if (len != P) { fprintf(stderr, "orbit sizes differ (%d vs %d)\n", len, P); exit(2); }
        u = v;
        for (int t = 0; t < P; t++) { oid[u] = n_orb; u = sigma[u]; }
        reps[n_orb++] = v;
    }
    if (n_orb > MAXORB) { fprintf(stderr, "too many orbits\n"); exit(2); }
    nbits = n_orb + NF;
    if (nbits > 64 * MW) { fprintf(stderr, "raise MW\n"); exit(2); }
    memset(&full_m, 0, sizeof full_m);
    for (int b = 0; b < nbits; b++) m_set(&full_m, b);
}

static inline int bit_of(int s) { return (fidx[s] >= 0) ? n_orb + fidx[s] : oid[s]; }

static void build_tables(void) {
    for (int i = 0; i < n_orb; i++) {
        Mask m; memset(&m, 0, sizeof m);
        m_set(&m, i);
        int v = reps[i], u = sigma[v];
        for (int d = 1; d < P; d++) { m_set(&m, bit_of(v ^ u)); u = sigma[u]; }
        self_m[i] = m;
        for (int j = 0; j < NF; j++) {
            Mask g; memset(&g, 0, sizeof g);
            m_set(&g, bit_of(reps[i] ^ fixv[j]));
            ofix[i][j] = g;
        }
    }
    for (int i = 0; i < n_orb; i++)
        for (int j = 0; j < n_orb; j++) {
            Mask m; memset(&m, 0, sizeof m);
            if (i != j) {
                int v = reps[i], u = reps[j];
                for (int d = 0; d < P; d++) { m_set(&m, bit_of(v ^ u)); u = sigma[u]; }
            }
            cross_m[i][j] = m;
        }
}

static int K, M, forced = -1;
static int cand[MAXORB], ncand, chosen[MAXK], fsel[MAXFIX];
static Mask eff[MAXORB];                 /* self_m | contribution of the fixed part */
static Mask covA[MAXK + 1][MAXORB], cov[MAXK + 1];
static long long nodes, leaves, node_cap, progress;
static int found, use_prune = 1, solution[MAXK];

static inline int capacity(int k, int depth) {
    return (1 + (P - 1) / 2 + M) * k + P * (k * depth + k * (k - 1) / 2);
}

static void dfs(int depth, int start) {
    if (found) return;
    nodes++;
    if (node_cap && nodes > node_cap) return;
    int k = K - depth;
    if (use_prune && nbits - m_pop(&cov[depth]) > capacity(k, depth)) return;
    if (k == 0) { if (m_eq(&cov[depth], &full_m)) { memcpy(solution, chosen, sizeof(int) * K); found = 1; } return; }
    if (k == 1) {
        Mask c = cov[depth];
        for (int p = start; p < ncand; p++) {
            leaves++;
            Mask t = c; m_or(&t, &covA[depth][cand[p]]);
            if (m_eq(&t, &full_m)) {
                memcpy(solution, chosen, sizeof(int) * depth);
                solution[depth] = cand[p]; found = 1; return;
            }
        }
        return;
    }
    if (k == 2) {
        Mask c0 = cov[depth];
        for (int p = start; p + 1 < ncand; p++) {
            int i = cand[p];
            Mask c1 = c0; m_or(&c1, &covA[depth][i]);
            for (int q = p + 1; q < ncand; q++) {
                int j = cand[q];
                leaves++;
                Mask t = c1; m_or(&t, &covA[depth][j]); m_or(&t, &cross_m[i][j]);
                if (m_eq(&t, &full_m)) {
                    memcpy(solution, chosen, sizeof(int) * depth);
                    solution[depth] = i; solution[depth + 1] = j; found = 1; return;
                }
            }
        }
        return;
    }
    for (int p = start; p + k <= ncand; p++) {
        int i = cand[p];
        chosen[depth] = i;
        cov[depth + 1] = cov[depth];
        m_or(&cov[depth + 1], &covA[depth][i]);
        for (int q = p + 1; q < ncand; q++) {
            int j = cand[q];
            covA[depth + 1][j] = covA[depth][j];
            m_or(&covA[depth + 1][j], &cross_m[j][i]);
        }
        dfs(depth + 1, p + 1);
        if (found) return;
    }
}

static int flat_holes(const int *orbs, int k, const int *fs, int m, int *cols_out, int *n_out) {
    static int cols[MAXK * 32 + MAXFIX];
    int n = 0;
    for (int a = 0; a < k; a++) {
        int u = reps[orbs[a]];
        for (int d = 0; d < P; d++) { cols[n++] = u; u = sigma[u]; }
    }
    for (int a = 0; a < m; a++) cols[n++] = fixv[fs[a]];
    if (cols_out) memcpy(cols_out, cols, sizeof(int) * n);
    if (n_out) *n_out = n;
    static char seen[MAXNV];
    memset(seen, 0, sizeof seen);
    seen[0] = 1;
    for (int a = 0; a < n; a++) seen[cols[a]] = 1;
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++) seen[cols[a] ^ cols[b]] = 1;
    int holes = 0;
    for (int s = 0; s < NV; s++) if (!seen[s]) holes++;
    return holes;
}

/* control: the orbit-level mask must reproduce the flat syndrome sweep */
static int selftest(int trials) {
    unsigned st = 24681357u;
    int bad = 0;
    for (int t = 0; t < trials; t++) {
        st = st * 1103515245u + 12345u;
        int k = 2 + (int)((st >> 9) % 5);
        int m = NF ? (int)((st >> 17) % (unsigned)(NF < 5 ? NF + 1 : 5)) : 0;
        int orbs[MAXK], fs[MAXFIX];
        for (int a = 0; a < k; a++) {
            int pick, dup;
            do { st = st * 1103515245u + 12345u; pick = (int)((st >> 8) % (unsigned)n_orb);
                 dup = 0; for (int b = 0; b < a; b++) if (orbs[b] == pick) dup = 1; } while (dup);
            orbs[a] = pick;
        }
        for (int a = 0; a < m; a++) {
            int pick, dup;
            do { st = st * 1103515245u + 12345u; pick = (int)((st >> 8) % (unsigned)NF);
                 dup = 0; for (int b = 0; b < a; b++) if (fs[b] == pick) dup = 1; } while (dup);
            fs[a] = pick;
        }
        Mask mm; memset(&mm, 0, sizeof mm);
        for (int a = 0; a < m; a++) {
            m_set(&mm, n_orb + fs[a]);
            for (int b = a + 1; b < m; b++) m_set(&mm, bit_of(fixv[fs[a]] ^ fixv[fs[b]]));
        }
        for (int a = 0; a < k; a++) {
            m_or(&mm, &self_m[orbs[a]]);
            for (int b = 0; b < m; b++) m_or(&mm, &ofix[orbs[a]][fs[b]]);
            for (int b = a + 1; b < k; b++) m_or(&mm, &cross_m[orbs[a]][orbs[b]]);
        }
        int hole_syn = 0;
        for (int b = 0; b < n_orb; b++)
            if (!((mm.w[b >> 6] >> (b & 63)) & 1)) hole_syn += P;
        for (int b = 0; b < NF; b++)
            if (!((mm.w[(n_orb + b) >> 6] >> ((n_orb + b) & 63)) & 1)) hole_syn += 1;
        int flat = flat_holes(orbs, k, fs, m, NULL, NULL);
        if (flat != hole_syn) { printf("  MISMATCH k=%d m=%d flat=%d orbit=%d\n", k, m, flat, hole_syn); bad++; }
    }
    return bad;
}

int main(int argc, char **argv) {
    const char *sig_path = NULL;
    int st_trials = 0, forcev = -1;
    const char *fixedset = NULL;
    K = 7; M = 0; node_cap = 0;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--sigma")) sig_path = argv[++a];
        else if (!strcmp(argv[a], "--orbits")) K = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--fixed")) M = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--force")) forcev = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--nodes")) node_cap = atoll(argv[++a]);
        else if (!strcmp(argv[a], "--noprune")) use_prune = 0;
        else if (!strcmp(argv[a], "--selftest")) st_trials = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--progress")) progress = atoll(argv[++a]);
        else if (!strcmp(argv[a], "--fixedset")) fixedset = argv[++a];
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    if (!sig_path) { fprintf(stderr, "need --sigma FILE\n"); return 2; }
    load_sigma(sig_path);
    build_orbits();
    build_tables();
    printf("r=%d p=%d orbits=%d fixed=%d bits=%d K=%d M=%d -> n=%d\n",
           R, P, n_orb, NF, nbits, K, M, P * K + M);
    if (st_trials) {
        int bad = selftest(st_trials);
        printf("selftest: %d trials, %d mismatches\n", st_trials, bad);
        if (bad) return 1;
        return 0;
    }
    if (M > NF || K > MAXK) { fprintf(stderr, "M > available fixed vectors\n"); return 2; }
    if (forcev >= 0) { forced = oid[forcev]; if (forced < 0) { fprintf(stderr, "bad --force\n"); return 2; } }

    ncand = 0;
    for (int i = 0; i < n_orb; i++) if (i != forced) cand[ncand++] = i;

    /* outer loop over m-subsets of the fixed vectors; --fixedset pins one
     * centraliser class representative instead (see fixed_classes.py) */
    int single = 0;
    if (fixedset) {
        const char *q = fixedset;
        int cnt = 0;
        while (*q) {
            while (*q == ' ') q++;
            if (!*q) break;
            int v = (int)strtol(q, (char **)&q, 10);
            if (v <= 0 || v >= NV || fidx[v] < 0) { fprintf(stderr, "bad --fixedset entry %d\n", v); return 2; }
            fsel[cnt++] = fidx[v];
        }
        if (cnt != M) { fprintf(stderr, "--fixedset has %d entries, --fixed says %d\n", cnt, M); return 2; }
        single = 1;
    } else {
        for (int a = 0; a < M; a++) fsel[a] = a;
    }
    long long subsets = 0;
    clock_t t0 = clock();
    for (;;) {
        subsets++;
        if (progress && subsets % progress == 0) {
            fprintf(stderr, "  ... %lld fixed-subsets decided (%.0fs)\n", subsets - 1,
                    (double)(clock() - t0) / CLOCKS_PER_SEC);
            fflush(stderr);
        }
        Mask base; memset(&base, 0, sizeof base);
        for (int a = 0; a < M; a++) {
            m_set(&base, n_orb + fsel[a]);
            for (int b = a + 1; b < M; b++) m_set(&base, bit_of(fixv[fsel[a]] ^ fixv[fsel[b]]));
        }
        for (int i = 0; i < n_orb; i++) {
            eff[i] = self_m[i];
            for (int a = 0; a < M; a++) m_or(&eff[i], &ofix[i][fsel[a]]);
        }
        int depth = 0;
        cov[0] = base;
        if (forced >= 0) {
            chosen[0] = forced;
            cov[1] = base; m_or(&cov[1], &eff[forced]);
            for (int q = 0; q < ncand; q++) {
                covA[1][cand[q]] = eff[cand[q]];
                m_or(&covA[1][cand[q]], &cross_m[cand[q]][forced]);
            }
            depth = 1;
        } else {
            for (int q = 0; q < ncand; q++) covA[0][cand[q]] = eff[cand[q]];
        }
        dfs(depth, 0);
        if (found) {
            int cols[MAXK * 32 + MAXFIX], ncols = 0;
            int holes = flat_holes(solution, K, fsel, M, cols, &ncols);
            printf("SOLUTION orbit reps:");
            for (int a = 0; a < K; a++) printf(" %d", reps[solution[a]]);
            printf("\nfixed vectors:");
            for (int a = 0; a < M; a++) printf(" %d", fixv[fsel[a]]);
            printf("\ncolumns (%d):", ncols);
            for (int a = 0; a < ncols; a++) printf(" %d", cols[a]);
            printf("\nflat-sweep holes: %d  (%d/%d syndromes covered)\n", holes, NV - holes, NV);
            printf("subsets=%lld nodes=%lld leaves=%lld secs=%.1f\n",
                   subsets, nodes, leaves, (double)(clock() - t0) / CLOCKS_PER_SEC);
            return 0;
        }
        if (node_cap && nodes > node_cap) {
            printf("CAPPED after %lld nodes -- UNKNOWN, not a negative\n", nodes);
            return 4;
        }
        if (!M || single) break;
        int a = M - 1;
        while (a >= 0 && fsel[a] == NF - M + a) a--;
        if (a < 0) break;
        fsel[a]++;
        for (int b = a + 1; b < M; b++) fsel[b] = fsel[b - 1] + 1;
    }
    printf("EXHAUSTED: no sigma-invariant %d-set (%lld fixed-subset%s%s)\n",
           P * K + M, subsets, subsets == 1 ? "" : "s", single ? ", one centraliser class" : "");
    printf("subsets=%lld nodes=%lld leaves=%lld secs=%.1f\n",
           subsets, nodes, leaves, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 3;
}
