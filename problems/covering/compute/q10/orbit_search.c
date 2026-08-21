/* orbit_search.c -- prescribed-automorphism search for l_2(10,2).
 *
 * sigma in GL(10,2) has order 7 and a 1-dimensional fixed space, so it has
 * 146 orbits of size 7 on F_2^10 plus the two fixed vectors 0 and f.  A
 * sigma-invariant 49-set is therefore exactly a union of 7 orbits (49 = 7*7,
 * and f cannot be used since 48 is not a multiple of 7).
 *
 * Covering radius <= 2 for S becomes, orbit-wise:
 *   orbit i in S            covers orbit i
 *   sums inside orbit i     cover  orb(rep_i ^ sigma^d rep_i), d = 1..6
 *   sums across i != j      cover  orb(rep_i ^ sigma^d rep_j), d = 0..6
 * and one of those cross sums may be f itself, which happens exactly when
 * orbits i and j are partners (rep_j in orbit of rep_i ^ f).  f can be covered
 * no other way, so every solution contains a partner pair; the centraliser of
 * sigma acts on the 73 partner pairs, and setup.py reduces them to class
 * representatives.  Forcing one such pair and enumerating the rest is
 * exhaustive up to conjugacy in GL(10,2).
 *
 * Build:  gcc -O2 -o orbit_search orbit_search.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define R 10
#define NV (1 << R)
#define MAXORB 160
#define MW 3
#define MAXK 12

typedef struct { uint64_t w[MW]; } Mask;

static inline void m_or(Mask *a, const Mask *b) {
    a->w[0] |= b->w[0]; a->w[1] |= b->w[1]; a->w[2] |= b->w[2];
}
static inline void m_set(Mask *a, int b) { a->w[b >> 6] |= 1ULL << (b & 63); }
static inline int m_pop(const Mask *a) {
    return __builtin_popcountll(a->w[0]) + __builtin_popcountll(a->w[1])
         + __builtin_popcountll(a->w[2]);
}

static int sigma[NV], oid[NV], reps[MAXORB], n_orb, fvec;
static Mask self_m[MAXORB];
static Mask cross_m[MAXORB][MAXORB];
static Mask full_m;
static int nbits;                       /* n_orb orbits + 1 bit for f */

static int mul_M1(int a) {
    int a0 = a & 1, a1 = (a >> 1) & 1, a2 = (a >> 2) & 1;
    return a2 | ((a0 ^ a2) << 1) | (a1 << 2);
}
static int mul_M2(int a) {
    int a0 = a & 1, a1 = (a >> 1) & 1, a2 = (a >> 2) & 1;
    return a2 | (a0 << 1) | ((a1 ^ a2) << 2);
}

static void build_sigma(const char *kind) {
    int third_is_M2 = (strcmp(kind, "21") == 0);
    for (int v = 0; v < NV; v++) {
        int out = mul_M1(v & 7) | (mul_M1((v >> 3) & 7) << 3);
        out |= (third_is_M2 ? mul_M2((v >> 6) & 7) : mul_M1((v >> 6) & 7)) << 6;
        out |= v & (1 << 9);
        sigma[v] = out;
    }
}

static void build_orbits(void) {
    int nfix = 0;
    fvec = -1;
    for (int v = 1; v < NV; v++)
        if (sigma[v] == v) { nfix++; fvec = v; }
    if (nfix != 1) { fprintf(stderr, "fixed space is not 1-dimensional\n"); exit(1); }
    for (int v = 0; v < NV; v++) oid[v] = -1;
    n_orb = 0;
    for (int v = 1; v < NV; v++) {
        if (v == fvec || oid[v] >= 0) continue;
        int u = v;
        for (int t = 0; t < 7; t++) { oid[u] = n_orb; u = sigma[u]; }
        if (u != v) { fprintf(stderr, "sigma has order != 7\n"); exit(1); }
        reps[n_orb++] = v;
    }
    nbits = n_orb + 1;                  /* last bit is the fixed vector f */
    memset(&full_m, 0, sizeof full_m);
    for (int b = 0; b < nbits; b++) m_set(&full_m, b);
}

/* bit for the syndrome s (nonzero); f gets the extra bit */
static inline int bit_of(int s) { return (s == fvec) ? n_orb : oid[s]; }

static void build_tables(void) {
    for (int i = 0; i < n_orb; i++) {
        Mask m; memset(&m, 0, sizeof m);
        m_set(&m, i);
        int v = reps[i], u = sigma[v];
        for (int d = 1; d < 7; d++) { m_set(&m, bit_of(v ^ u)); u = sigma[u]; }
        self_m[i] = m;
    }
    for (int i = 0; i < n_orb; i++)
        for (int j = 0; j < n_orb; j++) {
            Mask m; memset(&m, 0, sizeof m);
            if (i != j) {
                int v = reps[i], u = reps[j];
                for (int d = 0; d < 7; d++) { m_set(&m, bit_of(v ^ u)); u = sigma[u]; }
            }
            cross_m[i][j] = m;
        }
}

/* ---- search ---------------------------------------------------------- */

static int K;                            /* number of orbits to pick */
static int cand[MAXORB], ncand;
static int chosen[MAXK];
static Mask covA[MAXK + 1][MAXORB];      /* self | cross to everything chosen */
static Mask cov[MAXK + 1];
static long long nodes, leaves;
static long long node_cap;
static int use_prune = 1;
static int found;
static int solution[MAXK];

/* an upper bound on the bits still reachable with k more orbits on top of
 * `depth` already chosen: each new orbit gives <= 1 membership + 3 internal
 * sums, and each new pair of orbits gives <= 7 */
static inline int capacity(int k, int depth) {
    return 4 * k + 7 * (k * depth + k * (k - 1) / 2);
}

static void dfs(int depth, int start) {
    if (found) return;
    nodes++;
    if (node_cap && nodes > node_cap) return;
    int k = K - depth;
    if (use_prune && nbits - m_pop(&cov[depth]) > capacity(k, depth)) return;

    if (k == 1) {
        Mask c = cov[depth];
        for (int p = start; p < ncand; p++) {
            leaves++;
            Mask t = c; m_or(&t, &covA[depth][cand[p]]);
            if (t.w[0] == full_m.w[0] && t.w[1] == full_m.w[1]
                                      && t.w[2] == full_m.w[2]) {
                memcpy(solution, chosen, sizeof(int) * depth);
                solution[depth] = cand[p];
                found = 1;
                return;
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

/* ---- independent flat check ------------------------------------------ */

static int flat_holes(const int *orbs, int k, int *cols_out) {
    int cols[MAXK * 7], n = 0;
    for (int a = 0; a < k; a++) {
        int u = reps[orbs[a]];
        for (int d = 0; d < 7; d++) { cols[n++] = u; u = sigma[u]; }
    }
    if (cols_out) memcpy(cols_out, cols, sizeof(int) * n);
    static char seen[NV];
    memset(seen, 0, sizeof seen);
    seen[0] = 1;
    for (int a = 0; a < n; a++) seen[cols[a]] = 1;
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++) seen[cols[a] ^ cols[b]] = 1;
    int holes = 0;
    for (int s = 0; s < NV; s++) if (!seen[s]) holes++;
    return holes;
}

/* control: the orbit-level mask must agree with the flat sweep, bit for bit */
static int selftest(int trials, unsigned seed) {
    unsigned st = seed ? seed : 1u;
    int bad = 0;
    for (int t = 0; t < trials; t++) {
        int k = 3 + (int)(st = st * 1103515245u + 12345u) % 6;
        int orbs[MAXK];
        for (int a = 0; a < k; a++) {
            int pick, dup;
            do {
                st = st * 1103515245u + 12345u;
                pick = (int)((st >> 8) % (unsigned)n_orb);
                dup = 0;
                for (int b = 0; b < a; b++) if (orbs[b] == pick) dup = 1;
            } while (dup);
            orbs[a] = pick;
        }
        Mask m; memset(&m, 0, sizeof m);
        for (int a = 0; a < k; a++) {
            m_or(&m, &self_m[orbs[a]]);
            for (int b = a + 1; b < k; b++) m_or(&m, &cross_m[orbs[a]][orbs[b]]);
        }
        /* orbit-level holes, translated back to a syndrome count */
        int hole_syn = 0;
        for (int b = 0; b < n_orb; b++)
            if (!((m.w[b >> 6] >> (b & 63)) & 1)) hole_syn += 7;
        if (!((m.w[n_orb >> 6] >> (n_orb & 63)) & 1)) hole_syn += 1;
        int flat = flat_holes(orbs, k, NULL);
        if (flat != hole_syn) {
            printf("  selftest MISMATCH k=%d flat=%d orbit=%d\n", k, flat, hole_syn);
            bad++;
        }
    }
    return bad;
}

int main(int argc, char **argv) {
    const char *kind = "21";
    int p0v = -1, p1v = -1, do_selftest = 0, st_trials = 0;
    K = 7;
    node_cap = 0;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--kind")) kind = argv[++a];
        else if (!strcmp(argv[a], "--pair")) { p0v = atoi(argv[++a]); p1v = atoi(argv[++a]); }
        else if (!strcmp(argv[a], "--orbits")) K = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--nodes")) node_cap = atoll(argv[++a]);
        else if (!strcmp(argv[a], "--noprune")) use_prune = 0;
        else if (!strcmp(argv[a], "--selftest")) { do_selftest = 1; st_trials = atoi(argv[++a]); }
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    build_sigma(kind);
    build_orbits();
    build_tables();
    printf("kind=%s orbits=%d f=%d target-bits=%d K=%d (n=%d)\n",
           kind, n_orb, fvec, nbits, K, 7 * K);

    if (do_selftest) {
        int bad = selftest(st_trials, 12345u);
        printf("selftest: %d trials, %d mismatches\n", st_trials, bad);
        if (bad) return 1;
        if (p0v < 0) return 0;
    }
    if (p0v < 0) { fprintf(stderr, "need --pair v0 v1\n"); return 2; }

    int p0 = oid[p0v], p1 = oid[p1v];
    if (p0 < 0 || p1 < 0 || p0 == p1) { fprintf(stderr, "bad forced pair\n"); return 2; }
    if (bit_of(reps[p0] ^ reps[p1]) != n_orb) {
        int ok = 0, u = reps[p1];
        for (int d = 0; d < 7; d++) { if ((reps[p0] ^ u) == fvec) ok = 1; u = sigma[u]; }
        if (!ok) { fprintf(stderr, "forced pair is not a partner pair\n"); return 2; }
    }

    ncand = 0;
    for (int i = 0; i < n_orb; i++) if (i != p0 && i != p1) cand[ncand++] = i;

    chosen[0] = p0; chosen[1] = p1;
    memset(&cov[2], 0, sizeof cov[2]);
    m_or(&cov[2], &self_m[p0]);
    m_or(&cov[2], &self_m[p1]);
    m_or(&cov[2], &cross_m[p0][p1]);
    for (int q = 0; q < ncand; q++) {
        int j = cand[q];
        covA[2][j] = self_m[j];
        m_or(&covA[2][j], &cross_m[j][p0]);
        m_or(&covA[2][j], &cross_m[j][p1]);
    }

    clock_t t0 = clock();
    dfs(2, 0);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;

    if (found) {
        int cols[MAXK * 7];
        int holes = flat_holes(solution, K, cols);
        printf("SOLUTION orbits:");
        for (int a = 0; a < K; a++) printf(" %d", reps[solution[a]]);
        printf("\ncolumns:");
        for (int a = 0; a < 7 * K; a++) printf(" %d", cols[a]);
        printf("\nflat-sweep holes: %d  (%d/%d syndromes covered)\n",
               holes, NV - holes, NV);
    } else if (node_cap && nodes > node_cap) {
        printf("CAPPED after %lld nodes -- UNKNOWN, not a negative\n", nodes);
    } else {
        printf("EXHAUSTED: no sigma-invariant %d-set with this forced pair\n", 7 * K);
    }
    printf("nodes=%lld leaves=%lld secs=%.1f\n", nodes, leaves, secs);
    return found ? 0 : 3;
}
