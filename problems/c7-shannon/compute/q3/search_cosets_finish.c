/* Finish the q2 8-coset residue.

   Enumerate every 2-dimensional F7-subspace in RREF (Gaussian binomial
   [5 choose 2]_7 = 140050). Keep the good codes
   V ∩ {-1,0,1}^5 = {0}. The 343-vertex quotient is the Cayley graph
   on F7^3 with connection set (V + cube) / V. Eight independent
   cosets would be 392 vertices.

   q2 left 1280 graphs after a node-capped search. This pass:
     1. deduplicates connection sets,
     2. kills α<8 by a Hoffman bound (Cayley eigenvalues over F7^3),
     3. kills α<8 by a multi-start clique cover,
     4. exact bitset search for an 8-set containing 0, with
        clique-cover pruning and a high node cap,
     5. dumps any leftover unique connection set for SAT.

   gcc -O3 -o q3/search_cosets_finish q3/search_cosets_finish.c -lm
   ./q3/search_cosets_finish
*/
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807
#define QN 343
#define BW 6
#define HS 262144
#define RECCAP 2000000

typedef uint64_t BS[BW];

static int cube[243][5];

static void fill_tables(void) {
    int n = 0;
    for (int o0 = -1; o0 <= 1; o0++)
        for (int o1 = -1; o1 <= 1; o1++)
            for (int o2 = -1; o2 <= 1; o2++)
                for (int o3 = -1; o3 <= 1; o3++)
                    for (int o4 = -1; o4 <= 1; o4++) {
                        cube[n][0] = o0;
                        cube[n][1] = o1;
                        cube[n][2] = o2;
                        cube[n][3] = o3;
                        cube[n][4] = o4;
                        n++;
                    }
}

static int is_good(const int a[5], const int b[5]) {
    for (int s = 0; s < 7; s++)
        for (int t = 0; t < 7; t++) {
            if (s == 0 && t == 0) continue;
            int small = 1;
            for (int i = 0; i < 5; i++) {
                int x = (s * a[i] + t * b[i]) % 7;
                if (x > 1 && x < 6) {
                    small = 0;
                    break;
                }
            }
            if (small) return 0;
        }
    return 1;
}

static void bs_zero(BS a) { memset(a, 0, sizeof(BS)); }

static void bs_fill343(BS a) {
    a[0] = a[1] = a[2] = a[3] = a[4] = ~0ull;
    a[5] = (1ull << 23) - 1;
}

static inline void bs_set(BS a, int i) { a[i >> 6] |= 1ull << (i & 63); }

static inline int bs_get(const BS a, int i) {
    return (int)((a[i >> 6] >> (i & 63)) & 1ull);
}

static inline void bs_andnot(BS a, const BS b) {
    for (int i = 0; i < BW; i++) a[i] &= ~b[i];
}

static inline int bs_count(const BS a) {
    int s = 0;
    for (int i = 0; i < BW; i++) s += __builtin_popcountll(a[i]);
    return s;
}

static inline int bs_first(const BS a) {
    for (int i = 0; i < BW; i++)
        if (a[i]) return i * 64 + __builtin_ctzll(a[i]);
    return -1;
}

static int add_cid(int i, int d) {
    int i0 = i / 49, i1 = (i / 7) % 7, i2 = i % 7;
    int d0 = d / 49, d1 = (d / 7) % 7, d2 = d % 7;
    return ((i0 + d0) % 7) * 49 + ((i1 + d1) % 7) * 7 + (i2 + d2) % 7;
}

static int cid_of(const int c[5], const int a[5], const int b[5], int p0, int p1) {
    int x[5];
    for (int i = 0; i < 5; i++) x[i] = c[i];
    int s = x[p0];
    for (int i = 0; i < 5; i++) x[i] = (x[i] - (s * a[i]) % 7 + 14) % 7;
    int t = x[p1];
    for (int i = 0; i < 5; i++) x[i] = (x[i] - (t * b[i]) % 7 + 14) % 7;
    int rest[3], nr = 0;
    for (int i = 0; i < 5; i++)
        if (i != p0 && i != p1) rest[nr++] = x[i];
    return rest[0] * 49 + rest[1] * 7 + rest[2];
}

/* Unique connection-set table. */
typedef struct {
    uint64_t k[BW];
    uint8_t used;
} Slot;

static Slot ht[HS];

static void key_from_conn(const uint8_t *conn, uint64_t k[BW]) {
    memset(k, 0, BW * sizeof(uint64_t));
    for (int i = 0; i < QN; i++)
        if (conn[i]) k[i >> 6] |= 1ull << (i & 63);
}

static uint32_t hash_key(const uint64_t k[BW]) {
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < BW; i++) {
        h ^= k[i];
        h *= 1099511628211ull;
    }
    return (uint32_t)(h & (HS - 1));
}

static int key_eq(const uint64_t a[BW], const uint64_t b[BW]) {
    for (int i = 0; i < BW; i++)
        if (a[i] != b[i]) return 0;
    return 1;
}

/* 1 = newly inserted, 0 = already present. */
static int ht_insert(const uint8_t *conn) {
    uint64_t k[BW];
    key_from_conn(conn, k);
    uint32_t h = hash_key(k);
    for (int probe = 0; probe < HS; probe++) {
        Slot *s = &ht[(h + (uint32_t)probe) & (HS - 1)];
        if (!s->used) {
            s->used = 1;
            memcpy(s->k, k, sizeof k);
            return 1;
        }
        if (key_eq(s->k, k)) return 0;
    }
    fprintf(stderr, "hash table full\n");
    exit(1);
}

static void build_adj(const uint8_t *conn, BS *adj) {
    for (int i = 0; i < QN; i++) {
        bs_zero(adj[i]);
        for (int d = 1; d < QN; d++) {
            if (!conn[d]) continue;
            bs_set(adj[i], add_cid(i, d));
        }
    }
}

/* Greedy clique cover of G[cand]: an upper bound on α. */
static int clique_cover(const BS *adj, const BS cand0, unsigned *rng) {
    BS left;
    memcpy(left, cand0, sizeof(BS));
    int ncl = 0;
    int verts[QN], nv = 0;
    for (int i = 0; i < QN; i++)
        if (bs_get(left, i)) verts[nv++] = i;
    if (*rng) {
        for (int i = nv - 1; i > 0; i--) {
            *rng = *rng * 1664525u + 1013904223u;
            int j = (int)(*rng % (unsigned)(i + 1));
            int t = verts[i];
            verts[i] = verts[j];
            verts[j] = t;
        }
    }
    uint8_t alive[QN];
    memset(alive, 0, sizeof alive);
    for (int i = 0; i < nv; i++) alive[verts[i]] = 1;
    for (int s = 0; s < nv; s++) {
        int v = verts[s];
        if (!alive[v]) continue;
        ncl++;
        alive[v] = 0;
        int members[QN], nm = 1;
        members[0] = v;
        for (int t = s + 1; t < nv; t++) {
            int u = verts[t];
            if (!alive[u]) continue;
            int ok = 1;
            for (int m = 0; m < nm; m++) {
                if (!bs_get(adj[u], members[m])) {
                    ok = 0;
                    break;
                }
            }
            if (ok) {
                members[nm++] = u;
                alive[u] = 0;
            }
        }
    }
    return ncl;
}

static int color_ub(const BS *adj, const BS cand) {
    int color[QN];
    for (int i = 0; i < QN; i++) color[i] = -1;
    int ncolors = 0;
    BS left;
    memcpy(left, cand, sizeof(BS));
    while (1) {
        int v = bs_first(left);
        if (v < 0) break;
        uint8_t used[64];
        memset(used, 0, sizeof used);
        for (int u = 0; u < QN; u++) {
            if (u == v || !bs_get(cand, u) || color[u] < 0) continue;
            if (!bs_get(adj[v], u) && color[u] < 64) used[color[u]] = 1;
        }
        int c = 0;
        while (c < 64 && used[c]) c++;
        color[v] = c;
        if (c + 1 > ncolors) ncolors = c + 1;
        left[v >> 6] &= ~(1ull << (v & 63));
    }
    return ncolors;
}

static int rec_nodes, rec_cap;

static int rec8(const BS *adj, BS cand, int sofar) {
    if (sofar >= 8) return 1;
    if (++rec_nodes > rec_cap) return -1;
    int rem = bs_count(cand);
    if (sofar + rem < 8) return 0;
    if (rem == 0) return 0;
    if (rem >= 10 && sofar + 4 < 8) {
        unsigned rng = (unsigned)(rec_nodes * 10007u + 1u);
        int ub = clique_cover(adj, cand, &rng);
        if (sofar + ub < 8) return 0;
    }
    int best_v = -1, best_d = -1;
    BS tmp;
    memcpy(tmp, cand, sizeof(BS));
    while (1) {
        int v = bs_first(tmp);
        if (v < 0) break;
        tmp[v >> 6] &= ~(1ull << (v & 63));
        int d = 0;
        for (int i = 0; i < BW; i++) d += __builtin_popcountll(cand[i] & adj[v][i]);
        if (d > best_d) {
            best_d = d;
            best_v = v;
        }
    }
    int v = best_v;
    BS next;
    memcpy(next, cand, sizeof(BS));
    next[v >> 6] &= ~(1ull << (v & 63));
    bs_andnot(next, adj[v]);
    int a = rec8(adj, next, sofar + 1);
    if (a != 0) return a;
    cand[v >> 6] &= ~(1ull << (v & 63));
    return rec8(adj, cand, sofar);
}

/* Hoffman bound for a Cayley graph on F7^3.
   λ_a = Σ_{c in Conn\{0}} 2cos(2π <a,c>/7)/2, real because Conn=-Conn.
   α ≤ n (−μ)/(d−μ). Conservative: require the float bound < 7.9. */
static int hoffman_lt8(const uint8_t *conn, int *deg_out, long double *hoff_out) {
    static int init = 0;
    static long double re[7];
    if (!init) {
        for (int k = 0; k < 7; k++)
            re[k] = cosl(2.0L * 3.14159265358979323846L * (long double)k / 7.0L);
        init = 1;
    }
    int clist[QN], deg = 0;
    for (int d = 1; d < QN; d++)
        if (conn[d]) clist[deg++] = d;
    *deg_out = deg;
    if (deg == 0) {
        *hoff_out = (long double)QN;
        return 0;
    }
    long double mu = (long double)deg;
    for (int a0 = 0; a0 < 7; a0++)
        for (int a1 = 0; a1 < 7; a1++)
            for (int a2 = 0; a2 < 7; a2++) {
                if (a0 == 0 && a1 == 0 && a2 == 0) continue;
                long double sr = 0;
                for (int i = 0; i < deg; i++) {
                    int c = clist[i];
                    int c0 = c / 49, c1 = (c / 7) % 7, c2 = c % 7;
                    int ip = (a0 * c0 + a1 * c1 + a2 * c2) % 7;
                    sr += re[ip];
                }
                if (sr < mu) mu = sr;
            }
    if (mu >= -1e-12L) {
        *hoff_out = (long double)QN;
        return 0;
    }
    long double hoff = 343.0L * (-mu) / ((long double)deg - mu);
    *hoff_out = hoff;
    /* 0.1 slack covers long-double summation of ≤342 cosines. */
    return hoff < 7.9L;
}

static void write_conn(FILE *f, const uint8_t *conn) {
    for (int i = 0; i < QN; i++) fputc(conn[i] ? '1' : '0', f);
    fputc('\n', f);
}

int main(void) {
    clock_t t0 = clock();
    fill_tables();
    remove("q3/coset_leftover.conn");
    remove("q3/coset_unique.conn");
    FILE *leftover = fopen("q3/coset_leftover.conn", "w");
    FILE *unique_f = fopen("q3/coset_unique.conn", "w");
    if (!leftover || !unique_f) {
        fprintf(stderr, "cannot write q3 connection dumps\n");
        return 1;
    }

    int pivots[10][2], npiv = 0;
    for (int i = 0; i < 5; i++)
        for (int j = i + 1; j < 5; j++) {
            pivots[npiv][0] = i;
            pivots[npiv][1] = j;
            npiv++;
        }

    int n_sub = 0, n_good = 0, n_unique = 0;
    int n_hoff = 0, n_cover = 0, n_search_no = 0, n_yes = 0, n_unk = 0;
    int min_deg = QN, max_deg = 0, n_deg_sum = 0;
    long double best_hoff = 1e9L;
    BS adj[QN];
    unsigned rng = 1;

    for (int p = 0; p < npiv; p++) {
        int p0 = pivots[p][0], p1 = pivots[p][1];
        int fa[5], nfa = 0, fb[5], nfb = 0;
        for (int k = 0; k < 5; k++) {
            if (k == p0 || k == p1) continue;
            if (k > p0) fa[nfa++] = k;
            if (k > p1) fb[nfb++] = k;
        }
        int nfill = nfa + nfb;
        int ncomb = 1;
        for (int t = 0; t < nfill; t++) ncomb *= 7;
        for (int code = 0; code < ncomb; code++) {
            int a[5] = {0}, b[5] = {0};
            a[p0] = 1;
            b[p1] = 1;
            int x = code;
            for (int t = 0; t < nfa; t++) {
                a[fa[t]] = x % 7;
                x /= 7;
            }
            for (int t = 0; t < nfb; t++) {
                b[fb[t]] = x % 7;
                x /= 7;
            }
            n_sub++;
            if (!is_good(a, b)) continue;
            n_good++;

            uint8_t conn[QN];
            memset(conn, 0, sizeof conn);
            int V[49][5];
            int nv = 0;
            for (int s = 0; s < 7; s++)
                for (int t = 0; t < 7; t++) {
                    for (int i = 0; i < 5; i++)
                        V[nv][i] = (s * a[i] + t * b[i]) % 7;
                    nv++;
                }
            for (int i = 0; i < 49; i++)
                for (int k = 0; k < 243; k++) {
                    int c[5];
                    for (int d = 0; d < 5; d++)
                        c[d] = (V[i][d] + cube[k][d] + 7) % 7;
                    conn[cid_of(c, a, b, p0, p1)] = 1;
                }

            if (!ht_insert(conn)) continue;
            n_unique++;
            write_conn(unique_f, conn);

            int deg = 0;
            long double hoff = 0;
            if (hoffman_lt8(conn, &deg, &hoff)) {
                n_hoff++;
                if (deg < min_deg) min_deg = deg;
                if (deg > max_deg) max_deg = deg;
                n_deg_sum += deg;
                if (hoff < best_hoff) best_hoff = hoff;
                goto progress;
            }
            if (deg < min_deg) min_deg = deg;
            if (deg > max_deg) max_deg = deg;
            n_deg_sum += deg;
            if (hoff < best_hoff) best_hoff = hoff;

            build_adj(conn, adj);
            BS cand;
            bs_fill343(cand);
            int ub = color_ub(adj, cand);
            unsigned r2 = rng;
            int cc = clique_cover(adj, cand, &r2);
            rng = r2;
            for (int t = 0; t < 7; t++) {
                unsigned r3 = rng + (unsigned)t * 9973u + 1u;
                int c2 = clique_cover(adj, cand, &r3);
                if (c2 < cc) cc = c2;
            }
            if (cc < ub) ub = cc;
            if (ub < 8) {
                n_cover++;
                goto progress;
            }

            /* Cayley: an 8-set may be translated to contain 0. */
            cand[0] &= ~1ull;
            bs_andnot(cand, adj[0]);
            rec_nodes = 0;
            rec_cap = RECCAP;
            int r = rec8(adj, cand, 1);
            if (r == 1) {
                n_yes++;
                printf("YES unique #%d deg=%d hoff=%.4Lf\n", n_unique, deg, hoff);
                write_conn(leftover, conn);
                fflush(stdout);
            } else if (r == 0) {
                n_search_no++;
            } else {
                n_unk++;
                write_conn(leftover, conn);
            }

        progress:
            if (n_unique <= 3 || n_unique % 50 == 0) {
                double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
                printf("  unique=%d good=%d hoff=%d cover=%d search_no=%d "
                       "yes=%d unk=%d deg[%d,%d] t=%.1fs\n",
                       n_unique, n_good, n_hoff, n_cover, n_search_no, n_yes,
                       n_unk, min_deg, max_deg, sec);
                fflush(stdout);
            }
        }
    }

    fclose(leftover);
    fclose(unique_f);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE subspaces=%d good=%d unique=%d hoffman_lt8=%d cover_lt8=%d "
           "search_no=%d yes=%d leftover=%d deg[%d,%d] avg_deg=%.1f "
           "best_hoff=%.4Lf t=%.1fs\n",
           n_sub, n_good, n_unique, n_hoff, n_cover, n_search_no, n_yes, n_unk,
           min_deg, max_deg, n_unique ? (double)n_deg_sum / n_unique : 0.0,
           best_hoff, sec);
    return n_yes ? 0 : 0;
}
