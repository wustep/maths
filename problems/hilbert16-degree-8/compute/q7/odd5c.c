/* Exhaust compatible collections of five odd Harnack splits.
 *
 * The Python exporter supplies the q5 split graph, split edges and twist
 * vectors.  For each 5-clique this program constructs the same deterministic
 * greedy unimodular refinement as deepnest.fast_refine, builds its rhombus
 * complex, and evaluates the scheme with tcore.h.  It emits one collection
 * per scheme fingerprint; Python independently decodes every emitted witness.
 */
#define TCORE_MAX_CHILDREN 64
#include "../tcore.h"
#include <time.h>

#define MAX_PTS 45
#define MAX_PAIRS 640
#define MAX_SPLITS 1260
#define MAX_ODDS 192
#define MAX_PAIR_WORDS 10
#define MAX_ODD_WORDS 3
#define MAX_BASE_TRIS 64
#define MAX_UNIT_TRIS 4096
#define MAX_NV 145
#define MAX_EDGES 512

static int npair, nsplit, nodd, npw, now;
static int px[MAX_PTS], py[MAX_PTS];
static int pair_u[MAX_PAIRS], pair_v[MAX_PAIRS];
static uint64_t pair_cross[MAX_PAIRS][MAX_PAIR_WORDS];
static int split_ne[MAX_SPLITS], split_edge[MAX_SPLITS][2];
static uint64_t split_twist[MAX_SPLITS];
static int odd_id[MAX_ODDS];
static uint64_t odd_adj[MAX_ODDS][MAX_ODD_WORDS];
static uint64_t expected_first[MAX_ODDS];

static int pair_index[MAX_PTS][MAX_PTS];
static int unit_tri[MAX_UNIT_TRIS][3];
static int unit_edge[MAX_UNIT_TRIS][3];
static int nunit;
static int base_tri[MAX_BASE_TRIS][3];
static int nbase;

static int vid_map[17][17], vx[MAX_NV], vy[MAX_NV];
static int inc1[MAX_NV][MAX_NV], inc2[MAX_NV][MAX_NV];
static unsigned char boundary_done[MAX_NV][MAX_NV];

static inline int bit_get(const uint64_t *a, int k)
{
    return (int)((a[k >> 6] >> (k & 63)) & 1ULL);
}
static inline void bit_set(uint64_t *a, int k)
{
    a[k >> 6] |= 1ULL << (k & 63);
}
static inline void bit_clear(uint64_t *a, int k)
{
    a[k >> 6] &= ~(1ULL << (k & 63));
}

static void read_int(FILE *f, int *x)
{
    if (fscanf(f, "%d", x) != 1) { fprintf(stderr, "bad task integer\n"); exit(2); }
}
static void read_hex(FILE *f, uint64_t *x)
{
    if (fscanf(f, "%" SCNx64, x) != 1) { fprintf(stderr, "bad task word\n"); exit(2); }
}

static void load_odd_task(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(2); }
    if (fscanf(f, "%d %d %d %d %d %d", &npts, &npair, &nsplit,
               &nodd, &npw, &now) != 6) exit(2);
    if (npts != 45 || npair > MAX_PAIRS || nsplit > MAX_SPLITS ||
        nodd > MAX_ODDS || npw > MAX_PAIR_WORDS || now > MAX_ODD_WORDS) {
        fprintf(stderr, "task dimensions out of range\n"); exit(2);
    }
    eta_s = malloc(npts);
    for (int i = 0; i < npts; i++) { int x; read_int(f, &x); eta_s[i] = (signed char)x; }
    for (int i = 0; i < npts; i++) { read_int(f, &px[i]); read_int(f, &py[i]); }
    memset(pair_index, -1, sizeof(pair_index));
    for (int i = 0; i < npair; i++) {
        read_int(f, &pair_u[i]); read_int(f, &pair_v[i]);
        pair_index[pair_u[i]][pair_v[i]] = pair_index[pair_v[i]][pair_u[i]] = i;
        for (int w = 0; w < npw; w++) read_hex(f, &pair_cross[i][w]);
    }
    for (int i = 0; i < nsplit; i++) {
        int even;
        read_int(f, &split_ne[i]); read_int(f, &split_edge[i][0]);
        read_int(f, &split_edge[i][1]); read_hex(f, &split_twist[i]);
        read_int(f, &even);
    }
    for (int i = 0; i < nodd; i++) read_int(f, &odd_id[i]);
    for (int i = 0; i < nodd; i++)
        for (int w = 0; w < now; w++) read_hex(f, &odd_adj[i][w]);
    for (int i = 0; i < nodd; i++)
        if (fscanf(f, "%" SCNu64, &expected_first[i]) != 1) exit(2);
    fclose(f);
}

static int area2(int a, int b, int c)
{
    return (px[b] - px[a]) * (py[c] - py[a])
         - (py[b] - py[a]) * (px[c] - px[a]);
}

static void prepare_unit_triangles(void)
{
    nunit = 0;
    for (int a = 0; a < npts; a++) for (int b = a + 1; b < npts; b++) {
        int ab = pair_index[a][b];
        if (ab < 0) continue;
        for (int c = b + 1; c < npts; c++) {
            int ac = pair_index[a][c], bc = pair_index[b][c];
            if (ac < 0 || bc < 0 || abs(area2(a, b, c)) != 1) continue;
            if (nunit >= MAX_UNIT_TRIS) { fprintf(stderr, "too many unit triangles\n"); exit(2); }
            unit_tri[nunit][0] = a; unit_tri[nunit][1] = b; unit_tri[nunit][2] = c;
            unit_edge[nunit][0] = ab; unit_edge[nunit][1] = ac; unit_edge[nunit][2] = bc;
            nunit++;
        }
    }
}

static void choose_edge(int e, uint64_t *allowed, uint64_t *chosen)
{
    bit_set(chosen, e);
    for (int w = 0; w < npw; w++) allowed[w] &= ~pair_cross[e][w];
    bit_clear(allowed, e);
}

static int build_base(const int ids[5])
{
    uint64_t allowed[MAX_PAIR_WORDS], chosen[MAX_PAIR_WORDS];
    for (int w = 0; w < npw; w++) { allowed[w] = UINT64_MAX; chosen[w] = 0; }
    if (npair & 63) allowed[npw - 1] &= (1ULL << (npair & 63)) - 1;
    for (int q = 0; q < 5; q++) {
        int sid = ids[q];
        for (int z = 0; z < split_ne[sid]; z++) {
            int e = split_edge[sid][z];
            if (bit_get(chosen, e)) continue;
            if (!bit_get(allowed, e)) return 0;
            choose_edge(e, allowed, chosen);
        }
    }
    for (int e = 0; e < npair; e++)
        if (bit_get(allowed, e)) choose_edge(e, allowed, chosen);

    nbase = 0;
    for (int k = 0; k < nunit; k++) {
        if (!bit_get(chosen, unit_edge[k][0]) ||
            !bit_get(chosen, unit_edge[k][1]) ||
            !bit_get(chosen, unit_edge[k][2])) continue;
        if (nbase >= MAX_BASE_TRIS) return 0;
        memcpy(base_tri[nbase++], unit_tri[k], 3 * sizeof(int));
    }
    return nbase == 64;
}

static void prepare_vertices(void)
{
    memset(vid_map, -1, sizeof(vid_map));
    nv = 0;
    for (int x = -8; x <= 8; x++) for (int y = -8; y <= 8; y++) {
        if (abs(x) + abs(y) > 8) continue;
        int v = nv++;
        vid_map[x + 8][y + 8] = v; vx[v] = x; vy[v] = y;
    }
    if (nv != 145) exit(2);
    vbase = malloc(nv * sizeof(int)); vflip = malloc(nv * sizeof(int));
    for (int v = 0; v < nv; v++) {
        int ax = abs(vx[v]), ay = abs(vy[v]), b = -1;
        for (int i = 0; i < npts; i++) if (px[i] == ax && py[i] == ay) { b = i; break; }
        if (b < 0) exit(2);
        vbase[v] = b;
        int flip = 1;
        if (vx[v] < 0 && (ax & 1)) flip = -flip;
        if (vy[v] < 0 && (ay & 1)) flip = -flip;
        vflip[v] = flip;
    }
}

static int vertex_id(int x, int y)
{
    if (x < -8 || x > 8 || y < -8 || y > 8) return -1;
    return vid_map[x + 8][y + 8];
}
static int tri_slot(int t, int v)
{
    for (int s = 0; s < 3; s++) if (rtris[t][s] == v) return s;
    return -1;
}
static void add_complex_edge(int t1, int t2, int cross, int u1, int u2, int w1, int w2)
{
    if (nedges >= MAX_EDGES) exit(2);
    int su1 = tri_slot(t1, u1), su2 = tri_slot(t2, u2);
    int sw1 = tri_slot(t1, w1), sw2 = tri_slot(t2, w2);
    if (su1 < 0 || su2 < 0 || sw1 < 0 || sw2 < 0) exit(2);
    edg[nedges][0] = t1; edg[nedges][1] = t2; edg[nedges][2] = cross;
    edg[nedges][3] = 3 * t1 + su1; edg[nedges][4] = 3 * t2 + su2;
    edg[nedges][5] = 3 * t1 + sw1; edg[nedges][6] = 3 * t2 + sw2;
    edg[nedges][7] = u1; edg[nedges][8] = w1;
    nedges++;
}

static int build_complex(void)
{
    F = 4 * nbase;
    int ti = 0;
    const int sg[2] = {1, -1};
    for (int k = 0; k < nbase; k++) for (int ia = 0; ia < 2; ia++)
        for (int ib = 0; ib < 2; ib++) {
            for (int s = 0; s < 3; s++) {
                int p = base_tri[k][s];
                rtris[ti][s] = vertex_id(sg[ia] * px[p], sg[ib] * py[p]);
            }
            ti++;
        }
    memset(inc1, -1, sizeof(inc1)); memset(inc2, -1, sizeof(inc2));
    memset(boundary_done, 0, sizeof(boundary_done));
    for (int t = 0; t < F; t++) for (int s = 0; s < 3; s++) {
        int u = rtris[t][s], v = rtris[t][(s + 1) % 3];
        if (u > v) { int z = u; u = v; v = z; }
        if (inc1[u][v] < 0) inc1[u][v] = t;
        else if (inc2[u][v] < 0) inc2[u][v] = t;
        else return 0;
    }
    nedges = 0;
    for (int u = 0; u < nv; u++) for (int v = u + 1; v < nv; v++) {
        if (inc1[u][v] < 0) continue;
        if (inc2[u][v] >= 0) {
            add_complex_edge(inc1[u][v], inc2[u][v], 0, u, u, v, v);
            continue;
        }
        if (boundary_done[u][v]) continue;
        int au = vertex_id(-vx[u], -vy[u]), av = vertex_id(-vx[v], -vy[v]);
        int x = au, y = av;
        if (x > y) { int z = x; x = y; y = z; }
        if (inc1[x][y] < 0 || inc2[x][y] >= 0) return 0;
        boundary_done[u][v] = boundary_done[x][y] = 1;
        add_complex_edge(inc1[u][v], inc1[x][y], 1, u, au, v, av);
    }
    return F == 256;
}

static void alloc_tcore(void)
{
    rtris = malloc(256 * sizeof(*rtris)); edg = malloc(MAX_EDGES * sizeof(*edg));
    basis = malloc(sizeof(uint64_t)); rnk = 0;
    sigma = malloc(nv); cursign = malloc(npts); oddv = malloc(256);
    cutl = malloc(256 * sizeof(int));
    ufc = malloc(512 * sizeof(int)); ufc2 = malloc(512 * sizeof(int));
    ufr = malloc(1536 * sizeof(int)); ufr2 = malloc(1536 * sizeof(int));
    cmap = malloc(512 * sizeof(int)); rmap = malloc(1536 * sizeof(int));
    region_of = malloc(768 * sizeof(int));
    comp_lift = malloc(512 * sizeof(int)); reg_lift = malloc(1536 * sizeof(int));
    adjr = malloc(1024 * sizeof(int)); adjn = malloc(512 * sizeof(int));
    ovals = malloc(512 * sizeof(int)); pseudos = malloc(512 * sizeof(int));
    rc_head = malloc(1536 * sizeof(int)); rc_next = malloc(1024 * sizeof(int));
    parent_reg = malloc(512 * sizeof(int)); frontier = malloc(1536 * sizeof(int));
    nxt = malloc(1536 * sizeof(int)); seen_c = malloc(512 * sizeof(int));
    seen_r = malloc(1536 * sizeof(int)); tree_head = malloc(512 * sizeof(int));
    tree_next = malloc(512 * sizeof(int)); nodeh = malloc(512 * sizeof(H128));
    htk = calloc(1u << HTBITS, sizeof(H128)); htu = calloc(1u << HTBITS, sizeof(int));
}

static int eval_ids(const int ids[5], int *ok, H128 *fp)
{
    if (!build_base(ids) || !build_complex()) { *ok = 0; return 0; }
    uint64_t twist = 0;
    for (int q = 0; q < 5; q++) twist ^= split_twist[ids[q]];
    for (int i = 0; i < npts; i++)
        cursign[i] = ((twist >> i) & 1ULL) ? -eta_s[i] : eta_s[i];
    return evaluate(cursign, ok, fp);
}

static double now_seconds(void)
{
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char **argv)
{
    if (argc < 5 || argc > 7) {
        fprintf(stderr, "usage: odd5c task lo hi out [cap] [trace]\n"); return 1;
    }
    int lo = atoi(argv[2]), hi = atoi(argv[3]);
    uint64_t cap = argc >= 6 ? strtoull(argv[5], NULL, 10) : 0;
    int trace = argc >= 7 ? atoi(argv[6]) : 0;
    load_odd_task(argv[1]);
    if (lo < 0 || hi > nodd || lo > hi) return 1;
    prepare_unit_triangles(); prepare_vertices(); alloc_tcore();
    FILE *out = fopen(argv[4], "w");
    if (!out) { perror(argv[4]); return 2; }
    uint64_t evals = 0, bad = 0, logged = 0, expected = 0;
    for (int a = lo; a < hi; a++) expected += expected_first[a];
    double t0 = now_seconds();
    int stopped = 0;
    for (int a = lo; a < hi && !stopped; a++) {
        uint64_t before = evals;
        for (int b = a + 1; b < nodd && !stopped; b++) {
            if (!bit_get(odd_adj[a], b)) continue;
            for (int c = b + 1; c < nodd && !stopped; c++) {
                if (!bit_get(odd_adj[a], c) || !bit_get(odd_adj[b], c)) continue;
                for (int d = c + 1; d < nodd && !stopped; d++) {
                    if (!bit_get(odd_adj[a], d) || !bit_get(odd_adj[b], d) ||
                        !bit_get(odd_adj[c], d)) continue;
                    for (int e = d + 1; e < nodd; e++) {
                        if (!bit_get(odd_adj[a], e) || !bit_get(odd_adj[b], e) ||
                            !bit_get(odd_adj[c], e) || !bit_get(odd_adj[d], e)) continue;
                        int ids[5] = {odd_id[a], odd_id[b], odd_id[c], odd_id[d], odd_id[e]};
                        int ok; H128 fp = {0, 0};
                        int nc = eval_ids(ids, &ok, &fp);
                        evals++;
                        if (!ok || nc != 22) bad++;
                        int fresh = ok && !seen_fp(fp, nc);
                        if (fresh) logged++;
                        if (trace || fresh || !ok || nc != 22) {
                            fprintf(out, "{\"kind\":\"%s\",\"ncomp\":%d,\"ok\":%s,"
                                "\"fp\":\"%016llx%016llx\",\"collection\":[%d,%d,%d,%d,%d]}\n",
                                trace ? "TRACE" : (fresh ? "WITNESS" : "BAD"), nc,
                                ok ? "true" : "false", (unsigned long long)fp.a,
                                (unsigned long long)fp.b, ids[0], ids[1], ids[2], ids[3], ids[4]);
                        }
                        if (cap && evals >= cap) { stopped = 1; break; }
                        if (evals % 200000 == 0) {
                            fprintf(stderr, "  progress a=%d evals=%llu/%llu distinct=%llu %.1fs\n",
                                    a, (unsigned long long)evals,
                                    (unsigned long long)expected,
                                    (unsigned long long)logged, now_seconds() - t0);
                            fflush(stderr);
                        }
                    }
                }
            }
        }
        if (!stopped && evals - before != expected_first[a]) {
            fprintf(stderr, "first-index %d count %llu != %llu\n", a,
                    (unsigned long long)(evals - before),
                    (unsigned long long)expected_first[a]); return 3;
        }
        fprintf(stderr, "a=%d evals=%llu/%llu distinct=%llu bad=%llu %.1fs\n",
                a, (unsigned long long)evals, (unsigned long long)expected,
                (unsigned long long)logged, (unsigned long long)bad,
                now_seconds() - t0);
        fflush(out);
        fflush(stderr);
    }
    int complete = !stopped && evals == expected && bad == 0;
    fprintf(out, "{\"kind\":\"summary\",\"lo\":%d,\"hi\":%d,"
        "\"evals\":%llu,\"expected\":%llu,\"distinct\":%llu,"
        "\"bad\":%llu,\"complete\":%s,\"seconds\":%.3f}\n",
        lo, hi, (unsigned long long)evals, (unsigned long long)expected,
        (unsigned long long)logged, (unsigned long long)bad,
        complete ? "true" : "false", now_seconds() - t0);
    fclose(out);
    return complete || cap ? 0 : 4;
}
