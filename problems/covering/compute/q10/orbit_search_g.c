/* orbit_search_g.c -- prescribed-automorphism search, general r.
 *
 * Reads sigma (prime order, 1-dimensional fixed space) as a column table, and
 * decides whether some union of k sigma-orbits, optionally together with the
 * fixed vector f, has covering radius <= 2 in F_2^r.
 *
 * A sigma-invariant n-set is k orbits of size p plus m copies of f, with
 * p*k + m = n and m in {0,1}.  Coverage is tracked orbit-wise:
 *   orbit i in S         covers orbit i
 *   sums inside orbit i  cover orb(rep_i ^ sigma^d rep_i), d = 1..p-1
 *   sums across i != j   cover orb(rep_i ^ sigma^d rep_j), d = 0..p-1
 *   f in S               covers f, and orb(rep_i ^ f) for every chosen i
 * When f is not in S it can only be covered by a cross sum, and rep_i ^ f
 * lies in orbit j exactly when i and j are partners -- so S must contain a
 * partner pair, which is what --force pins to a centraliser class rep.
 *
 * Build: gcc -O2 -o orbit_search_g orbit_search_g.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXR 12
#define MAXNV (1 << MAXR)
#define MAXORB 200
#define MW 3
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

static int R, NV, P;
static int sigma[MAXNV], oid[MAXNV], reps[MAXORB], n_orb, fvec;
static Mask self_m[MAXORB], cross_m[MAXORB][MAXORB], full_m;
static int partner[MAXORB];
static int nbits, withf, hasf;

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
    int nfix = 0;
    fvec = -1;
    for (int v = 1; v < NV; v++) if (sigma[v] == v) { nfix++; fvec = v; }
    if (nfix > 1) { fprintf(stderr, "fixed space must be at most 1-dimensional (got %d)\n", nfix); exit(2); }
    hasf = (nfix == 1);
    P = 1;
    for (int v = 1; v < NV; v++) if (v != fvec) {
        int u = sigma[v], k = 1;
        while (u != v) { u = sigma[u]; k++; }
        P = k;
        break;
    }
    for (int v = 0; v < NV; v++) oid[v] = -1;
    n_orb = 0;
    for (int v = 1; v < NV; v++) {
        if (v == fvec || oid[v] >= 0) continue;
        int u = v;
        for (int t = 0; t < P; t++) { if (oid[u] >= 0) { fprintf(stderr, "orbit sizes differ\n"); exit(2); } oid[u] = n_orb; u = sigma[u]; }
        if (u != v) { fprintf(stderr, "orbit sizes differ\n"); exit(2); }
        reps[n_orb++] = v;
    }
    if (n_orb > MAXORB) { fprintf(stderr, "too many orbits\n"); exit(2); }
    nbits = n_orb + (hasf ? 1 : 0);
    if (nbits > 64 * MW) { fprintf(stderr, "raise MW\n"); exit(2); }
    memset(&full_m, 0, sizeof full_m);
    for (int b = 0; b < nbits; b++) m_set(&full_m, b);
}

static inline int bit_of(int s) { return (hasf && s == fvec) ? n_orb : oid[s]; }

static void build_tables(void) {
    for (int i = 0; i < n_orb; i++) {
        partner[i] = hasf ? oid[reps[i] ^ fvec] : -1;
        Mask m; memset(&m, 0, sizeof m);
        m_set(&m, i);
        int v = reps[i], u = sigma[v];
        for (int d = 1; d < P; d++) { m_set(&m, bit_of(v ^ u)); u = sigma[u]; }
        if (withf) m_set(&m, partner[i]);   /* f in S also covers rep_i ^ f */
        self_m[i] = m;
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

static int K, cand[MAXORB], ncand, chosen[MAXK];
static Mask covA[MAXK + 1][MAXORB], cov[MAXK + 1];
static long long nodes, leaves, node_cap;
static int found, use_prune = 1, solution[MAXK];

/* k more orbits on top of `depth` already chosen contribute at most
 * 1 membership + (P-1)/2 internal sums (+1 partner if f is in S) each, and at
 * most P bits per new pair */
static inline int capacity(int k, int depth) {
    int per = 1 + (P - 1) / 2 + (withf ? 1 : 0);
    return per * k + P * (k * depth + k * (k - 1) / 2);
}

static void dfs(int depth, int start) {
    if (found) return;
    nodes++;
    if (node_cap && nodes > node_cap) return;
    int k = K - depth;
    if (use_prune && nbits - m_pop(&cov[depth]) > capacity(k, depth)) return;

    if (k == 2) {
        Mask c0 = cov[depth];
        for (int p = start; p + 1 < ncand; p++) {
            int i = cand[p];
            Mask c1 = c0; m_or(&c1, &covA[depth][i]);
            for (int q = p + 1; q < ncand; q++) {
                int j = cand[q];
                leaves++;
                Mask t = c1;
                m_or(&t, &covA[depth][j]);
                m_or(&t, &cross_m[i][j]);
                if (m_eq(&t, &full_m)) {
                    memcpy(solution, chosen, sizeof(int) * depth);
                    solution[depth] = i; solution[depth + 1] = j;
                    found = 1;
                    return;
                }
            }
        }
        return;
    }
    if (k == 1) {
        Mask c = cov[depth];
        for (int p = start; p < ncand; p++) {
            leaves++;
            Mask t = c; m_or(&t, &covA[depth][cand[p]]);
            if (m_eq(&t, &full_m)) {
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

static int flat_holes(const int *orbs, int k, int *cols_out, int *n_out) {
    static int cols[MAXK * 32];
    int n = 0;
    for (int a = 0; a < k; a++) {
        int u = reps[orbs[a]];
        for (int d = 0; d < P; d++) { cols[n++] = u; u = sigma[u]; }
    }
    if (withf) cols[n++] = fvec;
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

static int selftest(int trials) {
    unsigned st = 987654321u;
    int bad = 0;
    for (int t = 0; t < trials; t++) {
        st = st * 1103515245u + 12345u;
        int k = 3 + (int)((st >> 9) % 6), orbs[MAXK];
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
        if (withf) m_set(&m, n_orb);
        for (int a = 0; a < k; a++) {
            m_or(&m, &self_m[orbs[a]]);
            for (int b = a + 1; b < k; b++) m_or(&m, &cross_m[orbs[a]][orbs[b]]);
        }
        int hole_syn = 0;
        for (int b = 0; b < n_orb; b++)
            if (!((m.w[b >> 6] >> (b & 63)) & 1)) hole_syn += P;
        if (hasf && !((m.w[n_orb >> 6] >> (n_orb & 63)) & 1)) hole_syn += 1;
        int flat = flat_holes(orbs, k, NULL, NULL);
        if (flat != hole_syn) { printf("  MISMATCH k=%d flat=%d orbit=%d\n", k, flat, hole_syn); bad++; }
    }
    return bad;
}

static uint64_t rs;
static inline uint64_t rnd(void) {
    rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs;
}

/* uncovered syndromes for a set of K orbits (+ f when withf) */
static int score_of(const int *o, Mask *out) {
    Mask m; memset(&m, 0, sizeof m);
    if (withf) m_set(&m, n_orb);
    for (int a = 0; a < K; a++) {
        m_or(&m, &self_m[o[a]]);
        for (int b = a + 1; b < K; b++) m_or(&m, &cross_m[o[a]][o[b]]);
    }
    if (out) *out = m;
    int fbit = hasf ? (int)((m.w[n_orb >> 6] >> (n_orb & 63)) & 1) : 0;
    return P * (n_orb - (m_pop(&m) - fbit)) + (hasf ? 1 - fbit : 0);
}

/* steepest descent on single-orbit swaps, with random restarts */
static int anneal(long long restarts, unsigned seed, int *best_out) {
    rs = seed ? seed : 0x9e3779b97f4a7c15ULL;
    int cur[MAXK], best = 1 << 30;
    for (long long t = 0; t < restarts && !found; t++) {
        char used[MAXORB]; memset(used, 0, sizeof used);
        for (int a = 0; a < K; a++) {
            int pick;
            do { pick = (int)(rnd() % (uint64_t)n_orb); } while (used[pick]);
            used[pick] = 1; cur[a] = pick;
        }
        int sc = score_of(cur, NULL);
        for (int step = 0; step < 4000 && sc; step++) {
            int bs = sc, ba = -1, bj = -1, ties = 0;
            for (int a = 0; a < K; a++) {
                int keep = cur[a];
                for (int j = 0; j < n_orb; j++) {
                    if (used[j]) continue;
                    cur[a] = j;
                    int s2 = score_of(cur, NULL);
                    if (s2 < bs) { bs = s2; ba = a; bj = j; ties = 1; }
                    else if (s2 == bs && ba >= 0 && (rnd() % (uint64_t)(++ties)) == 0) { ba = a; bj = j; }
                }
                cur[a] = keep;
            }
            if (ba < 0) {                          /* local minimum: kick */
                int a = (int)(rnd() % (uint64_t)K), j;
                do { j = (int)(rnd() % (uint64_t)n_orb); } while (used[j]);
                used[cur[a]] = 0; used[j] = 1; cur[a] = j;
                sc = score_of(cur, NULL);
                continue;
            }
            used[cur[ba]] = 0; used[bj] = 1; cur[ba] = bj; sc = bs;
        }
        if (sc < best) {
            best = sc;
            memcpy(best_out, cur, sizeof(int) * K);
            printf("  restart %lld: %d uncovered syndromes\n", t, sc);
            fflush(stdout);
        }
        if (sc == 0) { memcpy(solution, cur, sizeof(int) * K); found = 1; }
    }
    return best;
}

int main(int argc, char **argv) {
    const char *sig_path = NULL;
    int fv[2] = {-1, -1}, nforce = 0, st_trials = 0;
    long long do_anneal = 0; unsigned seed = 1;
    K = 7; node_cap = 0;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--sigma")) sig_path = argv[++a];
        else if (!strcmp(argv[a], "--orbits")) K = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--withf")) withf = 1;
        else if (!strcmp(argv[a], "--force")) { fv[nforce++] = atoi(argv[++a]); }
        else if (!strcmp(argv[a], "--nodes")) node_cap = atoll(argv[++a]);
        else if (!strcmp(argv[a], "--noprune")) use_prune = 0;
        else if (!strcmp(argv[a], "--selftest")) st_trials = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--anneal")) do_anneal = atoll(argv[++a]);
        else if (!strcmp(argv[a], "--seed")) seed = (unsigned)atoi(argv[++a]);
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    if (!sig_path) { fprintf(stderr, "need --sigma FILE\n"); return 2; }
    load_sigma(sig_path);
    build_orbits();
    build_tables();
    int n = P * K + (withf ? 1 : 0);
    printf("r=%d p=%d orbits=%d f=%d K=%d withf=%d -> n=%d\n",
           R, P, n_orb, fvec, K, withf, n);

    if (st_trials) {
        int bad = selftest(st_trials);
        printf("selftest: %d trials, %d mismatches\n", st_trials, bad);
        if (bad) return 1;
        if (!nforce) return 0;
    }
    if (do_anneal) {
        int best_o[MAXK];
        clock_t ta = clock();
        int best = anneal(do_anneal, seed, best_o);
        double asec = (double)(clock() - ta) / CLOCKS_PER_SEC;
        if (found) {
            int cols[MAXK * 32], ncols = 0;
            int holes = flat_holes(solution, K, cols, &ncols);
            printf("SOLUTION orbit reps:");
            for (int a = 0; a < K; a++) printf(" %d", reps[solution[a]]);
            printf("\ncolumns (%d):", ncols);
            for (int a = 0; a < ncols; a++) printf(" %d", cols[a]);
            printf("\nflat-sweep holes: %d  (%d/%d syndromes covered)\n",
                   holes, NV - holes, NV);
            printf("anneal secs=%.1f\n", asec);
            return 0;
        }
        printf("anneal residue: %d uncovered syndromes (best), secs=%.1f\n", best, asec);
        printf("  best orbit reps:");
        for (int a = 0; a < K; a++) printf(" %d", reps[best_o[a]]);
        printf("\n");
        return 3;
    }
    int need = (hasf && !withf) ? 2 : 1;
    if (nforce != need) {
        fprintf(stderr, "need %d --force argument(s)\n", need);
        return 2;
    }

    int f0 = oid[fv[0]], f1 = (need == 2) ? oid[fv[1]] : -1;
    if (f0 < 0 || (need == 2 && (f1 < 0 || partner[f0] != f1))) {
        fprintf(stderr, "bad forced orbit(s)\n"); return 2;
    }
    int base = need;
    ncand = 0;
    for (int i = 0; i < n_orb; i++) if (i != f0 && i != f1) cand[ncand++] = i;

    chosen[0] = f0;
    memset(&cov[base], 0, sizeof cov[base]);
    if (withf) m_set(&cov[base], n_orb);
    m_or(&cov[base], &self_m[f0]);
    if (need == 2) {
        chosen[1] = f1;
        m_or(&cov[base], &self_m[f1]);
        m_or(&cov[base], &cross_m[f0][f1]);
    }
    for (int q = 0; q < ncand; q++) {
        int j = cand[q];
        covA[base][j] = self_m[j];
        m_or(&covA[base][j], &cross_m[j][f0]);
        if (need == 2) m_or(&covA[base][j], &cross_m[j][f1]);
    }

    clock_t t0 = clock();
    dfs(base, 0);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;

    if (found) {
        int cols[MAXK * 32], ncols = 0;
        int holes = flat_holes(solution, K, cols, &ncols);
        printf("SOLUTION orbit reps:");
        for (int a = 0; a < K; a++) printf(" %d", reps[solution[a]]);
        printf("\ncolumns (%d):", ncols);
        for (int a = 0; a < ncols; a++) printf(" %d", cols[a]);
        printf("\nflat-sweep holes: %d  (%d/%d syndromes covered)\n", holes, NV - holes, NV);
    } else if (node_cap && nodes > node_cap) {
        printf("CAPPED after %lld nodes -- UNKNOWN, not a negative\n", nodes);
    } else {
        printf("EXHAUSTED: no sigma-invariant %d-set with this forced start\n", n);
    }
    printf("nodes=%lld leaves=%lld secs=%.1f\n", nodes, leaves, secs);
    return found ? 0 : 3;
}
