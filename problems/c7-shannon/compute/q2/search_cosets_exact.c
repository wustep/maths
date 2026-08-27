/* Exact 8-coset census for good 2-dimensional F7-subspaces.

   Enumerate unique RREF generators. A code is good when
   V ∩ {-1,0,1}^5 = {0}. The 343-vertex quotient is the Cayley graph
   on F7^3 whose connection set is (V + cube) / V. Eight independent
   cosets would be 392 vertices.

   Also pack a maximum (or greedy-7) set of cosets and measure the
   residual in the original graph: a maximal 7-pack in the quotient
   can still leave original-graph vertices free.

   gcc -O3 -o q2/search_cosets_exact q2/search_cosets_exact.c
   ./q2/search_cosets_exact
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define NV 16807
#define QN 343
#define BW 6

typedef uint64_t BS[BW];

static int coord[NV][5];
static int cube[243][5];
static int encode_c(const int c[5]) {
    return ((((c[0] * 7 + c[1]) * 7 + c[2]) * 7 + c[3]) * 7 + c[4]);
}

static void fill_tables(void) {
    for (int v = 0; v < NV; v++) {
        int x = v;
        for (int i = 4; i >= 0; i--) {
            coord[v][i] = x % 7;
            x /= 7;
        }
    }
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

static inline int bs_get(const BS a, int i) { return (int)((a[i >> 6] >> (i & 63)) & 1ull); }

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

static int rec8(const BS *adj, BS cand, int sofar) {
    if (sofar >= 8) return 1;
    int rem = bs_count(cand);
    if (sofar + rem < 8) return 0;
    if (rem == 0) return 0;
    /* branch on a vertex of maximum degree in the candidate */
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
    if (rec8(adj, next, sofar + 1)) return 1;
    cand[v >> 6] &= ~(1ull << (v & 63));
    return rec8(adj, cand, sofar);
}

static int exists8(const BS *adj) {
    BS cand;
    bs_fill343(cand);
    return rec8(adj, cand, 0);
}

static int greedy_pack(const BS *adj, unsigned *rng, int *taken) {
    int order[QN];
    for (int i = 0; i < QN; i++) order[i] = i;
    for (int i = QN - 1; i > 0; i--) {
        *rng = *rng * 1664525u + 1013904223u;
        int j = (int)(*rng % (unsigned)(i + 1));
        int tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }
    uint8_t banned[QN];
    memset(banned, 0, sizeof banned);
    int nt = 0;
    for (int t = 0; t < QN; t++) {
        int v = order[t];
        if (banned[v]) continue;
        taken[nt++] = v;
        for (int u = 0; u < QN; u++)
            if (bs_get(adj[v], u)) banned[u] = 1;
        banned[v] = 1;
    }
    return nt;
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

static int mis64(const int *verts, int n, const uint8_t *blocked_mark) {
    /* exact MIS among verts[0..n) using closed-neighbourhood via cube, n<=64 */
    if (n == 0) return 0;
    if (n > 64) {
        /* greedy fallback */
        uint8_t used[64 + 256];
        memset(used, 0, (size_t)n);
        int take = 0;
        for (int i = 0; i < n; i++) {
            if (used[i]) continue;
            take++;
            int v = verts[i];
            for (int k = 0; k < 243; k++) {
                int c[5];
                for (int d = 0; d < 5; d++)
                    c[d] = (coord[v][d] + cube[k][d] + 7) % 7;
                int u = encode_c(c);
                for (int j = 0; j < n; j++)
                    if (verts[j] == u) used[j] = 1;
            }
        }
        return take;
    }
    uint64_t neigh[64];
    memset(neigh, 0, sizeof neigh);
    uint8_t idx[NV];
    /* idx too big to zero fully each call — build from verts only */
    /* use a stamp */
    static uint16_t stamp[NV];
    static uint16_t gen;
    static uint8_t pos[NV];
    gen++;
    if (gen == 0) {
        memset(stamp, 0, sizeof stamp);
        gen = 1;
    }
    for (int i = 0; i < n; i++) {
        stamp[verts[i]] = gen;
        pos[verts[i]] = (uint8_t)i;
    }
    for (int i = 0; i < n; i++) {
        int v = verts[i];
        for (int k = 0; k < 243; k++) {
            int c[5];
            for (int d = 0; d < 5; d++)
                c[d] = (coord[v][d] + cube[k][d] + 7) % 7;
            int u = encode_c(c);
            if (u == v) continue;
            if (stamp[u] == gen) neigh[i] |= 1ull << pos[u];
        }
    }
    (void)blocked_mark;
    int best = 0;
    int nodes = 0;
    const int NODE_CAP = 200000;

    void rec(uint64_t cand, int sofar) {
        if (nodes++ > NODE_CAP) return;
        if (sofar + __builtin_popcountll(cand) <= best) return;
        if (cand == 0) {
            if (sofar > best) best = sofar;
            return;
        }
        int v = __builtin_ctzll(cand);
        rec(cand & ~neigh[v] & ~(1ull << v), sofar + 1);
        rec(cand & ~(1ull << v), sofar);
    }
    /* C doesn't allow nested functions in -pedantic; use a simple greedy+retry
       if we cannot nest. gcc allows nested functions. */
    rec((n == 64) ? ~0ull : ((1ull << n) - 1), 0);
    return best;
}

/* gcc nested-function version above; provide a non-nested fallback via macros */

static int pack_residual(const uint8_t *in_pack, int *best_extra) {
    uint8_t blocked[NV];
    memset(blocked, 0, sizeof blocked);
    for (int v = 0; v < NV; v++) {
        if (!in_pack[v]) continue;
        for (int k = 0; k < 243; k++) {
            int c[5];
            for (int d = 0; d < 5; d++)
                c[d] = (coord[v][d] + cube[k][d] + 7) % 7;
            blocked[encode_c(c)] = 1;
        }
    }
    int res[512];
    int nr = 0;
    for (int v = 0; v < NV; v++)
        if (!blocked[v]) {
            if (nr < 512) res[nr] = v;
            nr++;
        }
    if (nr == 0) {
        *best_extra = 0;
        return 0;
    }
    /* greedy extra */
    uint8_t extra_block[NV];
    memset(extra_block, 0, sizeof extra_block);
    int extra = 0;
    for (int i = 0; i < (nr < 512 ? nr : 512); i++) {
        int v = res[i];
        if (extra_block[v] || blocked[v]) continue;
        extra++;
        for (int k = 0; k < 243; k++) {
            int c[5];
            for (int d = 0; d < 5; d++)
                c[d] = (coord[v][d] + cube[k][d] + 7) % 7;
            extra_block[encode_c(c)] = 1;
        }
    }
    if (nr <= 64 && nr > 0) {
        int exact = mis64(res, nr, blocked);
        if (exact > extra) extra = exact;
    }
    *best_extra = extra;
    return nr;
}

static void write_hit(const char *path, const uint8_t *keep_cid, const int *cid,
                      int extra_n, const int *extra) {
    FILE *f = fopen(path, "w");
    if (!f) return;
    int wrote = 0;
    for (int v = 0; v < NV; v++)
        if (keep_cid[cid[v]]) {
            fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                    coord[v][3], coord[v][4]);
            wrote++;
        }
    for (int i = 0; i < extra_n; i++) {
        int v = extra[i];
        fprintf(f, "%d %d %d %d %d\n", coord[v][0], coord[v][1], coord[v][2],
                coord[v][3], coord[v][4]);
        wrote++;
    }
    fclose(f);
    printf("wrote %s size=%d\n", path, wrote);
}

int main(void) {
    clock_t t0 = clock();
    fill_tables();
    int pivots[10][2];
    int npiv = 0;
    for (int i = 0; i < 5; i++)
        for (int j = i + 1; j < 5; j++) {
            pivots[npiv][0] = i;
            pivots[npiv][1] = j;
            npiv++;
        }

    int n_sub = 0, n_good = 0, n8 = 0, n_res_pos = 0;
    int best_cosets = 0, best_total = 0, best_res = 0, max_res_n = 0;
    unsigned rng = 1;
    int cid[NV];
    uint8_t conn[QN];
    BS adj[QN];
    int hit = 0;

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

            for (int i = 0; i < QN; i++) bs_zero(adj[i]);
            for (int i = 0; i < QN; i++) {
                int i0 = i / 49, i1 = (i / 7) % 7, i2 = i % 7;
                for (int j = 0; j < QN; j++) {
                    if (i == j) continue;
                    int j0 = j / 49, j1 = (j / 7) % 7, j2 = j % 7;
                    int d = ((j0 - i0 + 7) % 7) * 49 + ((j1 - i1 + 7) % 7) * 7 +
                            (j2 - i2 + 7) % 7;
                    if (conn[d]) bs_set(adj[i], j);
                }
            }

            int has8 = exists8(adj);
            if (has8) n8++;
            if (has8 > best_cosets) best_cosets = 8;

            int local_best = 0, taken[QN];
            for (int trial = 0; trial < 8; trial++) {
                int pack[QN];
                int npk = greedy_pack(adj, &rng, pack);
                if (npk > local_best) {
                    local_best = npk;
                    memcpy(taken, pack, npk * sizeof(int));
                }
            }
            if (local_best > best_cosets && !has8) best_cosets = local_best;

            /* materialise best greedy pack and measure residual */
            if (local_best >= 6) {
                for (int v = 0; v < NV; v++)
                    cid[v] = cid_of(coord[v], a, b, p0, p1);
                uint8_t keep[QN];
                memset(keep, 0, sizeof keep);
                for (int i = 0; i < local_best; i++) keep[taken[i]] = 1;
                uint8_t in_pack[NV];
                memset(in_pack, 0, sizeof in_pack);
                int npack_v = 0;
                for (int v = 0; v < NV; v++)
                    if (keep[cid[v]]) {
                        in_pack[v] = 1;
                        npack_v++;
                    }
                int extra = 0;
                int nres = pack_residual(in_pack, &extra);
                if (nres > max_res_n) max_res_n = nres;
                if (extra > best_res) best_res = extra;
                int total = npack_v + extra;
                if (nres > 0) n_res_pos++;
                if (total > best_total) {
                    best_total = total;
                    printf("good #%d pack=%d verts=%d residual=%d extra=%d total=%d\n",
                           n_good, local_best, npack_v, nres, extra, total);
                    fflush(stdout);
                }
                if (has8 || total >= 368) {
                    uint8_t keep8[QN];
                    memset(keep8, 0, sizeof keep8);
                    if (has8) {
                        /* reconstruct an 8-set by a second search that records */
                        BS cand;
                        bs_fill343(cand);
                        int stack[8], ns = 0;
                        /* greedy-plus leftover */
                        unsigned r2 = rng;
                        int pk[QN];
                        int npk = greedy_pack(adj, &r2, pk);
                        for (int i = 0; i < npk && i < 8; i++) keep8[pk[i]] = 1;
                        if (npk < 8) {
                            uint8_t banned[QN];
                            memset(banned, 0, sizeof banned);
                            for (int i = 0; i < npk; i++) {
                                banned[pk[i]] = 1;
                                for (int u = 0; u < QN; u++)
                                    if (bs_get(adj[pk[i]], u)) banned[u] = 1;
                            }
                            for (int u = 0; u < QN && npk < 8; u++)
                                if (!banned[u]) {
                                    keep8[u] = 1;
                                    npk++;
                                }
                        }
                    } else {
                        memcpy(keep8, keep, sizeof keep);
                    }
                    write_hit("q2/R_cosets.txt", has8 ? keep8 : keep, cid, 0, NULL);
                    hit = 1;
                    printf("HIT has8=%d total=%d\n", has8, total);
                    goto done;
                }
            }

            if (n_good <= 3 || n_good % 200 == 0) {
                double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
                printf("  good=%d sub=%d best_cosets=%d best_total=%d best_res=%d "
                       "n8=%d nres>0=%d t=%.1fs\n",
                       n_good, n_sub, best_cosets, best_total, best_res, n8,
                       n_res_pos, sec);
                fflush(stdout);
            }
        }
    }
done:
    printf("DONE subspaces=%d good=%d has8=%d best_cosets=%d best_total=%d "
           "best_res=%d max_res_n=%d n_res_pos=%d t=%.1fs\n",
           n_sub, n_good, n8, best_cosets, best_total, best_res, max_res_n,
           n_res_pos, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return hit ? 0 : 0;
}
