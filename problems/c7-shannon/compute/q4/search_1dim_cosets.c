/* 1-dimensional good F7-codes: pack independent 7-point cosets.

   A generator g in RREF is good when <g> meets {-1,0,1}^5 only at 0.
   The quotient is the Cayley graph on F7^4 with 2401 vertices. Fifty-three
   independent cosets would be 371 vertices. Fifty-two are 364; leftover
   original-graph vertices can still make 368.

   gcc -O3 -o q4/search_1dim_cosets q4/search_1dim_cosets.c -lm
   ./q4/search_1dim_cosets
*/
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NV 16807
#define QN 2401
#define BW 38
#define HS 65536
#define GREEDY_TRIALS 24
#define LOCAL_STEPS 80

typedef uint64_t BS[BW];

static int cube[243][5];
static int coord[NV][5];
static int neigh[NV][243];

static int encode_c(const int c[5]) {
    return ((((c[0] * 7 + c[1]) * 7 + c[2]) * 7 + c[3]) * 7 + c[4]);
}

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
    for (int v = 0; v < NV; v++) {
        int x = v;
        for (int i = 4; i >= 0; i--) {
            coord[v][i] = x % 7;
            x /= 7;
        }
        int k = 0;
        for (int t = 0; t < 243; t++) {
            int c[5];
            for (int i = 0; i < 5; i++)
                c[i] = (coord[v][i] + cube[t][i] + 7) % 7;
            neigh[v][k++] = encode_c(c);
        }
    }
}

static int is_good(const int g[5]) {
    for (int s = 1; s < 7; s++) {
        int small = 1;
        for (int i = 0; i < 5; i++) {
            int x = (s * g[i]) % 7;
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

static void bs_fill2401(BS a) {
    for (int i = 0; i < 37; i++) a[i] = ~0ull;
    a[37] = (1ull << 33) - 1; /* 37*64+33 = 2401 */
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

static int pack4(const int x[4]) {
    return ((x[0] * 7 + x[1]) * 7 + x[2]) * 7 + x[3];
}

static void unpack4(int id, int x[4]) {
    for (int i = 3; i >= 0; i--) {
        x[i] = id % 7;
        id /= 7;
    }
}

static int cid_of(const int c[5], const int g[5], int pivot) {
    int x[5];
    for (int i = 0; i < 5; i++) x[i] = c[i];
    int s = x[pivot];
    for (int i = 0; i < 5; i++) x[i] = (x[i] - (s * g[i]) % 7 + 14) % 7;
    int rest[4], nr = 0;
    for (int i = 0; i < 5; i++)
        if (i != pivot) rest[nr++] = x[i];
    return pack4(rest);
}

static void rep_of(int cid, const int g[5], int pivot, int out[5]) {
    int rest[4];
    unpack4(cid, rest);
    int t = 0;
    for (int i = 0; i < 5; i++) {
        if (i == pivot)
            out[i] = 0;
        else
            out[i] = rest[t++];
    }
    (void)g;
}

static uint64_t hash_conn(const uint8_t *conn) {
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < QN; i++) {
        h ^= (uint64_t)conn[i] + 1u;
        h *= 1099511628211ull;
    }
    return h;
}

static uint8_t *ht_key[HS];
static int ht_used;

static int ht_insert(const uint8_t *conn) {
    uint64_t h = hash_conn(conn);
    int i = (int)(h & (HS - 1));
    for (int t = 0; t < HS; t++) {
        int j = (i + t) & (HS - 1);
        if (!ht_key[j]) {
            uint8_t *p = (uint8_t *)malloc(QN);
            memcpy(p, conn, QN);
            ht_key[j] = p;
            ht_used++;
            return 1;
        }
        if (memcmp(ht_key[j], conn, QN) == 0) return 0;
    }
    return 0;
}

static void build_adj(const uint8_t *conn, BS *adj) {
    int clist[QN], deg = 0;
    for (int d = 1; d < QN; d++)
        if (conn[d]) clist[deg++] = d;
    for (int i = 0; i < QN; i++) {
        bs_zero(adj[i]);
        int i0 = i / 343, i1 = (i / 49) % 7, i2 = (i / 7) % 7, i3 = i % 7;
        for (int t = 0; t < deg; t++) {
            int d = clist[t];
            int d0 = d / 343, d1 = (d / 49) % 7, d2 = (d / 7) % 7, d3 = d % 7;
            int j = ((i0 + d0) % 7) * 343 + ((i1 + d1) % 7) * 49 +
                    ((i2 + d2) % 7) * 7 + (i3 + d3) % 7;
            bs_set(adj[i], j);
        }
    }
}

static int greedy_mis(const BS *adj, unsigned *rng, int *out) {
    int order[QN];
    for (int i = 0; i < QN; i++) order[i] = i;
    for (int i = QN - 1; i > 0; i--) {
        *rng = *rng * 1664525u + 1013904223u;
        int j = (int)(*rng % (unsigned)(i + 1));
        int tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }
    BS left;
    bs_fill2401(left);
    int n = 0;
    for (int t = 0; t < QN; t++) {
        int v = order[t];
        if (!bs_get(left, v)) continue;
        out[n++] = v;
        left[v >> 6] &= ~(1ull << (v & 63));
        bs_andnot(left, adj[v]);
    }
    return n;
}

static int collect_free(const BS *adj, const int *S, int n, int skip, int *cand) {
    BS left;
    bs_fill2401(left);
    for (int i = 0; i < n; i++) {
        if (i == skip) continue;
        left[S[i] >> 6] &= ~(1ull << (S[i] & 63));
        bs_andnot(left, adj[S[i]]);
    }
    if (skip >= 0) left[S[skip] >> 6] &= ~(1ull << (S[skip] & 63));
    int nc = 0;
    while (nc < 64) {
        int u = bs_first(left);
        if (u < 0) break;
        cand[nc++] = u;
        left[u >> 6] &= ~(1ull << (u & 63));
    }
    return nc;
}

static int local_improve(const BS *adj, int *S, int n, unsigned *rng, int steps) {
    for (int t = 0; t < steps; t++) {
        *rng = *rng * 1664525u + 1013904223u;
        int idx = (int)(*rng % (unsigned)n);
        int cand[64];
        int nc = collect_free(adj, S, n, idx, cand);
        if (nc >= 2) {
            *rng = *rng * 1664525u + 1013904223u;
            int a = cand[*rng % (unsigned)nc];
            *rng = *rng * 1664525u + 1013904223u;
            int b = cand[*rng % (unsigned)nc];
            if (a != b && !bs_get(adj[a], b)) {
                S[idx] = a;
                S[n++] = b;
                continue;
            }
        }
        if (nc >= 1) {
            *rng = *rng * 1664525u + 1013904223u;
            S[idx] = cand[*rng % (unsigned)nc];
        }
    }
    return n;
}

static int hoffman_bound(const uint8_t *conn, int *deg_out, long double *hoff_out) {
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
            for (int a2 = 0; a2 < 7; a2++)
                for (int a3 = 0; a3 < 7; a3++) {
                    if (!(a0 | a1 | a2 | a3)) continue;
                    long double sr = 0;
                    for (int i = 0; i < deg; i++) {
                        int c = clist[i];
                        int c0 = c / 343, c1 = (c / 49) % 7, c2 = (c / 7) % 7,
                            c3 = c % 7;
                        int ip = (a0 * c0 + a1 * c1 + a2 * c2 + a3 * c3) % 7;
                        sr += re[ip];
                    }
                    if (sr < mu) mu = sr;
                }
    if (mu >= -1e-12L) {
        *hoff_out = (long double)QN;
        return 0;
    }
    *hoff_out = 2401.0L * (-mu) / ((long double)deg - mu);
    return *hoff_out < 52.9L;
}

static void write_words(const char *path, const int *verts, int n) {
    FILE *f = fopen(path, "w");
    if (!f) return;
    for (int i = 0; i < n; i++) {
        int v = verts[i];
        fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                coord[v][3], coord[v][4]);
    }
    fclose(f);
    printf("wrote %s size=%d\n", path, n);
}

static int expand_cosets(const int *cids, int nc, const int g[5], int pivot,
                         int *out) {
    int n = 0;
    for (int t = 0; t < nc; t++) {
        int rep[5];
        rep_of(cids[t], g, pivot, rep);
        for (int s = 0; s < 7; s++) {
            int c[5];
            for (int i = 0; i < 5; i++) c[i] = (rep[i] + s * g[i]) % 7;
            out[n++] = encode_c(c);
        }
    }
    return n;
}

static int residual_mis(const int *base, int nb, int *extra) {
    uint8_t blocked[NV];
    memset(blocked, 0, sizeof blocked);
    for (int i = 0; i < nb; i++)
        for (int k = 0; k < 243; k++) blocked[neigh[base[i]][k]] = 1;
    int n = 0;
    for (int v = 0; v < NV; v++) {
        if (blocked[v]) continue;
        extra[n++] = v;
        for (int k = 0; k < 243; k++) blocked[neigh[v][k]] = 1;
    }
    return n;
}

static void write_conn(FILE *f, const uint8_t *conn) {
    for (int i = 0; i < QN; i++) fputc(conn[i] ? '1' : '0', f);
    fputc('\n', f);
}

int main(void) {
    clock_t t0 = clock();
    fill_tables();
    FILE *unique_f = fopen("q4/onedim_unique.conn", "w");
    if (!unique_f) {
        fprintf(stderr, "cannot write q4/onedim_unique.conn\n");
        return 1;
    }

    int n_sub = 0, n_good = 0, n_unique = 0;
    int n_hoff = 0, best_pack = 0, best_total = 0, n_hit = 0;
    int min_deg = QN, max_deg = 0;
    long double best_hoff = 1e9L, worst_hoff = 0;
    unsigned rng = 1;
    BS *adj = (BS *)malloc(sizeof(BS) * QN);
    if (!adj) return 1;

    int best_g[5] = {0}, best_pivot = 0, best_cids[80], best_nc = 0;

    for (int pivot = 0; pivot < 5; pivot++) {
        /* RREF: leading 1 at pivot, zeros before it, free columns after. */
        int nfill = 5 - pivot - 1;
        int ncomb = 1;
        for (int t = 0; t < nfill; t++) ncomb *= 7;
        for (int code = 0; code < ncomb; code++) {
            int g[5] = {0};
            g[pivot] = 1;
            int x = code;
            for (int i = pivot + 1; i < 5; i++) {
                g[i] = x % 7;
                x /= 7;
            }
            n_sub++;
            if (!is_good(g)) continue;
            n_good++;

            uint8_t conn[QN];
            memset(conn, 0, sizeof conn);
            for (int s = 0; s < 7; s++)
                for (int k = 0; k < 243; k++) {
                    int c[5];
                    for (int i = 0; i < 5; i++)
                        c[i] = (s * g[i] + cube[k][i] + 7) % 7;
                    conn[cid_of(c, g, pivot)] = 1;
                }

            if (!ht_insert(conn)) continue;
            n_unique++;
            write_conn(unique_f, conn);

            int deg = 0;
            long double hoff = 0;
            int hoff_kill = hoffman_bound(conn, &deg, &hoff);
            if (deg < min_deg) min_deg = deg;
            if (deg > max_deg) max_deg = deg;
            if (hoff < best_hoff) best_hoff = hoff;
            if (hoff > worst_hoff) worst_hoff = hoff;
            if (hoff_kill) n_hoff++;

            build_adj(conn, adj);
            int pack[QN];
            int local_best = 0, local_cids[80], local_nc = 0;
            for (int trial = 0; trial < GREEDY_TRIALS; trial++) {
                unsigned r = rng + (unsigned)trial * 10007u + (unsigned)n_unique;
                int n = greedy_mis(adj, &r, pack);
                if (n > local_best) {
                    local_best = n;
                    local_nc = n < 80 ? n : 80;
                    memcpy(local_cids, pack, (size_t)local_nc * sizeof(int));
                }
            }
            {
                unsigned r = rng + 17u * (unsigned)n_unique;
                memcpy(pack, local_cids, (size_t)local_nc * sizeof(int));
                int n = local_improve(adj, pack, local_nc, &r, LOCAL_STEPS);
                if (n > local_best) {
                    local_best = n;
                    local_nc = n < 80 ? n : 80;
                    memcpy(local_cids, pack, (size_t)local_nc * sizeof(int));
                }
            }
            if (local_best > best_pack) {
                best_pack = local_best;
                memcpy(best_g, g, sizeof best_g);
                best_pivot = pivot;
                best_nc = local_nc;
                memcpy(best_cids, local_cids, (size_t)local_nc * sizeof(int));
                printf("pack=%d unique=%d deg=%d hoff=%.3Lf g=(%d %d %d %d %d)\n",
                       local_best, n_unique, deg, hoff, g[0], g[1], g[2], g[3],
                       g[4]);
                fflush(stdout);
            }

            int verts[QN * 7];
            int take = local_nc;
            int nv = expand_cosets(local_cids, take, g, pivot, verts);
            int extra[NV];
            int ne = residual_mis(verts, nv, extra);
            int total = nv + ne;
            if (total > best_total) {
                best_total = total;
                printf("total=%d pack=%d residual=%d unique=%d\n", total,
                       local_best, ne, n_unique);
                fflush(stdout);
            }
            if (total >= 368) {
                int all[NV];
                memcpy(all, verts, (size_t)nv * sizeof(int));
                memcpy(all + nv, extra, (size_t)ne * sizeof(int));
                write_words("q4/R_1dim.txt", all, nv + ne);
                n_hit++;
            }

            if (n_unique <= 3 || n_unique % 20 == 0) {
                double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
                printf("  unique=%d good=%d hoff_lt53=%d best_pack=%d "
                       "best_total=%d deg[%d,%d] t=%.1fs\n",
                       n_unique, n_good, n_hoff, best_pack, best_total, min_deg,
                       max_deg, sec);
                fflush(stdout);
            }
        }
    }

    fclose(unique_f);
    if (best_nc > 0) {
        int verts[QN * 7];
        int nv = expand_cosets(best_cids, best_nc, best_g, best_pivot, verts);
        char path[64];
        snprintf(path, sizeof path, "q4/R%d_1dim_bestpack.txt", nv);
        write_words(path, verts, nv);
    }
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE subspaces=%d good=%d unique=%d hoffman_lt53=%d best_pack=%d "
           "best_total=%d hit=%d deg[%d,%d] best_hoff=%.3Lf worst_hoff=%.3Lf "
           "t=%.1fs\n",
           n_sub, n_good, n_unique, n_hoff, best_pack, best_total, n_hit, min_deg,
           max_deg, best_hoff, worst_hoff, sec);
    free(adj);
    return 0;
}
