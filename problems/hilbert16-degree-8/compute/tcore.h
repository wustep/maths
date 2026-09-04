/* tcore.h -- shared T-curve evaluator for the C searches.
 *
 * Port of fastcx.Complex.eval + fastcx._scheme: same rhombus complex, same
 * union-find, same nesting logic.  The bracket rendering is replaced by a
 * 128-bit canonical hash of the nesting forest, so a search can dedupe
 * schemes without building strings; the scheme string of record is always
 * recomputed in Python from the emitted witness.
 *
 * Cross-checked against the Python sweep by validate_zonec.py.
 */
#ifndef TCORE_H
#define TCORE_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

static int npts, nv, F, nedges, rnk;
static int *vbase, *vflip;
static int (*rtris)[3];
static int (*edg)[9];          /* t1 t2 cross s1t1 s1t2 s2t1 s2t2 u1 w1 */
static signed char *eta_s;
static uint64_t *basis;

static signed char *sigma, *cursign;
static signed char *oddv;
static int *cutl, ncut;
static int *ufc, *ufr, *ufc2, *ufr2;
static int *cmap, *rmap, *region_of;
static int *comp_lift, *reg_lift;
static int *adjr, *adjn;       /* adjr[2*c+k] */
static int *ovals, *pseudos;
static int *rc_head, *rc_next; /* region -> list of ovals */
static int *parent_reg, *frontier, *nxt, *seen_c, *seen_r;
static int *stack_c;

static inline int find(int *p, int x)
{
    while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
    return x;
}
static inline void uni(int *p, int a, int b)
{
    int ra = find(p, a), rb = find(p, b);
    if (ra != rb) p[ra] = rb;
}

typedef struct { uint64_t a, b; } H128;

static inline uint64_t mix64(uint64_t x)
{
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33; return x;
}
static int hcmp(const void *x, const void *y)
{
    const H128 *p = x, *q = y;
    if (p->a != q->a) return p->a < q->a ? -1 : 1;
    if (p->b != q->b) return p->b < q->b ? -1 : 1;
    return 0;
}
/* canonical hash of an unordered multiset of child hashes */
static H128 fold(H128 *ch, int n)
{
    qsort(ch, n, sizeof(H128), hcmp);
    H128 h = { 0x243f6a8885a308d3ULL, 0x13198a2e03707344ULL };
    for (int i = 0; i < n; i++) {
        h.a = mix64(h.a ^ mix64(ch[i].a + 0x9e3779b97f4a7c15ULL));
        h.b = mix64(h.b * 0x100000001b3ULL ^ ch[i].b);
    }
    h.a = mix64(h.a + (uint64_t)n);
    h.b = mix64(h.b + (uint64_t)n * 0x9e3779b97f4a7c15ULL);
    return h;
}

/* nesting forest, filled by the scheme pass */
static int *tree_head, *tree_next;
static H128 *nodeh;

static H128 enc(int c)
{
    int n = 0;
    for (int k = tree_head[c]; k >= 0; k = tree_next[k]) n++;
#ifdef TCORE_MAX_CHILDREN
    if (n > TCORE_MAX_CHILDREN) abort();
    H128 ch[TCORE_MAX_CHILDREN];
#else
    H128 *ch = malloc((n ? n : 1) * sizeof(H128));
#endif
    int i = 0;
    for (int k = tree_head[c]; k >= 0; k = tree_next[k]) ch[i++] = enc(k);
    H128 h = fold(ch, n);
#ifndef TCORE_MAX_CHILDREN
    free(ch);
#endif
    nodeh[c] = h;
    return h;
}

/* returns ncomp; *ok set when the scheme is well formed, *fp its fingerprint */
static int evaluate(const signed char *signs, int *ok, H128 *fp)
{
    const int H = 3 * F;
    for (int v = 0; v < nv; v++) sigma[v] = signs[vbase[v]] * vflip[v];
    for (int i = 0; i < 2 * F; i++) { ufc[i] = i; ufc2[i] = i; }
    for (int i = 0; i < 6 * F; i++) { ufr[i] = i; ufr2[i] = i; }
    ncut = 0;
    for (int ti = 0; ti < F; ti++) {
        int a = rtris[ti][0], b = rtris[ti][1], c = rtris[ti][2];
        signed char sa = sigma[a], sb = sigma[b], sc = sigma[c];
        int o = -1;
        if (sa == sb) { if (sa != sc) o = 2; }
        else if (sa == sc) o = 1;
        else o = 0;
        oddv[ti] = (signed char)o;
        int base = 3 * ti;
        if (o < 0) {
            uni(ufr, base, base + 1); uni(ufr, base, base + 2);
            uni(ufr, H + base, H + base + 1); uni(ufr, H + base, H + base + 2);
        } else {
            cutl[ncut++] = ti;
            int s1 = (o + 1) % 3, s2 = (o + 2) % 3;
            uni(ufr, base + s1, base + s2);
            uni(ufr, H + base + s1, H + base + s2);
        }
    }
    for (int e = 0; e < nedges; e++) {
        int t1 = edg[e][0], t2 = edg[e][1], cross = edg[e][2];
        int a1 = edg[e][3], a2 = edg[e][4], b1 = edg[e][5], b2 = edg[e][6];
        int cutedge = sigma[edg[e][7]] != sigma[edg[e][8]];
        if (cross) {
            uni(ufr, a1, H + a2); uni(ufr, H + a1, a2);
            uni(ufr, b1, H + b2); uni(ufr, H + b1, b2);
            if (cutedge) { uni(ufc, t1, F + t2); uni(ufc, F + t1, t2); }
        } else {
            uni(ufr, a1, a2); uni(ufr, H + a1, H + a2);
            uni(ufr, b1, b2); uni(ufr, H + b1, H + b2);
            if (cutedge) { uni(ufc, t1, t2); uni(ufc, F + t1, F + t2); }
        }
    }
    for (int i = 0; i < ncut; i++) {
        int ti = cutl[i];
        uni(ufc2, find(ufc, ti), find(ufc, F + ti));
    }
    memset(cmap, -1, 2 * F * sizeof(int));
    int nc = 0;
    for (int i = 0; i < ncut; i++) {
        int ti = cutl[i];
        int r = find(ufc2, find(ufc, ti));
        if (cmap[r] < 0) {
            cmap[r] = nc;
            comp_lift[nc] = (find(ufc, ti) != find(ufc, F + ti)) ? 2 : 1;
            adjn[nc] = 0;
            nc++;
        }
    }
    *ok = 0;
    if (nc == 0) return 0;

    for (int cid = 0; cid < H; cid++)
        uni(ufr2, find(ufr, cid), find(ufr, H + cid));
    memset(rmap, -1, 6 * F * sizeof(int));
    int nr = 0;
    for (int cid = 0; cid < H; cid++) {
        int r = find(ufr2, find(ufr, cid));
        if (rmap[r] < 0) {
            rmap[r] = nr;
            reg_lift[nr] = (find(ufr, cid) != find(ufr, H + cid)) ? 2 : 1;
            nr++;
        }
        region_of[cid] = rmap[r];
    }
    int bad = 0;
    for (int i = 0; i < ncut; i++) {
        int ti = cutl[i];
        int c = cmap[find(ufc2, find(ufc, ti))];
        int o = oddv[ti];
        int rr[2] = { region_of[3 * ti + o], region_of[3 * ti + (o + 1) % 3] };
        for (int k = 0; k < 2; k++) {
            int seen = 0;
            for (int j = 0; j < adjn[c]; j++) if (adjr[2 * c + j] == rr[k]) seen = 1;
            if (!seen) {
                if (adjn[c] >= 2) { bad = 1; }
                else adjr[2 * c + adjn[c]++] = rr[k];
            }
        }
    }
    if (bad) return nc;

    int nov = 0, nps = 0;
    for (int c = 0; c < nc; c++) {
        if (comp_lift[c] == 2) {
            if (adjn[c] != 2) return nc;
            ovals[nov++] = c;
        } else {
            if (adjn[c] != 1) return nc;
            pseudos[nps++] = c;
        }
    }
    if (nr != nov + 1) return nc;
    if (nps) return nc;                 /* degree 8 is even */
    int root = -1, nnon = 0;
    for (int r = 0; r < nr; r++) if (reg_lift[r] == 1) { root = r; nnon++; }
    if (nnon != 1) return nc;

    for (int r = 0; r < nr; r++) rc_head[r] = -1;
    for (int i = 0; i < nov; i++) {
        int c = ovals[i];
        for (int k = 0; k < 2; k++) {
            int r = adjr[2 * c + k];
            rc_next[c * 2 + k] = rc_head[r];
            rc_head[r] = c * 2 + k;     /* encode (oval,slot) */
        }
    }
    for (int c = 0; c < nc; c++) { parent_reg[c] = -1; seen_c[c] = 0; }
    for (int r = 0; r < nr; r++) seen_r[r] = 0;
    seen_r[root] = 1;
    int nf = 1, nsc = 0, nsr = 1;
    frontier[0] = root;
    while (nf) {
        int nn = 0;
        for (int i = 0; i < nf; i++) {
            int r = frontier[i];
            for (int k = rc_head[r]; k >= 0; k = rc_next[k]) {
                int c = k / 2;
                if (seen_c[c]) continue;
                seen_c[c] = 1; nsc++;
                int r2 = adjr[2 * c + 0] == r ? adjr[2 * c + 1] : adjr[2 * c + 0];
                if (seen_r[r2]) return nc;
                seen_r[r2] = 1; nsr++;
                parent_reg[c] = r;
                nxt[nn++] = r2;
            }
        }
        for (int i = 0; i < nn; i++) frontier[i] = nxt[i];
        nf = nn;
    }
    if (nsc != nov || nsr != nr) return nc;

    for (int c = 0; c < nc; c++) tree_head[c] = -1;
    for (int i = 0; i < nov; i++) {
        int c = ovals[i];
        int pr = parent_reg[c];
        int other = adjr[2 * c + 0] == pr ? adjr[2 * c + 1] : adjr[2 * c + 0];
        for (int k = rc_head[other]; k >= 0; k = rc_next[k]) {
            int x = k / 2;
            if (parent_reg[x] == other) { tree_next[x] = tree_head[c]; tree_head[c] = x; }
        }
    }
#ifdef TCORE_MAX_CHILDREN
    if (nov > TCORE_MAX_CHILDREN) abort();
    H128 rootch[TCORE_MAX_CHILDREN];
#else
    H128 *rootch = malloc((nov ? nov : 1) * sizeof(H128));
#endif
    int nrt = 0;
    for (int i = 0; i < nov; i++) {
        int c = ovals[i];
        if (parent_reg[c] == root) rootch[nrt++] = enc(c);
    }
    *fp = fold(rootch, nrt);
#ifndef TCORE_MAX_CHILDREN
    free(rootch);
#endif
    *ok = 1;
    return nc;
}

/* ------------------------------------------------------------------ */
#define HTBITS 20
static H128 *htk;
static int *htu;

static int seen_fp(H128 h, int ncomp)
{
    uint64_t x = mix64(h.a ^ (h.b * 0x9e3779b97f4a7c15ULL) ^ (uint64_t)ncomp);
    uint64_t i = x & ((1u << HTBITS) - 1);
    while (htu[i]) {
        if (htk[i].a == h.a && htk[i].b == h.b) return 1;
        i = (i + 1) & ((1u << HTBITS) - 1);
    }
    htu[i] = 1; htk[i] = h;
    return 0;
}

static void need(FILE *f, int n, int *dst)
{
    for (int i = 0; i < n; i++)
        if (fscanf(f, "%d", &dst[i]) != 1) { fprintf(stderr, "bad task\n"); exit(1); }
}

/* reads the prepared complex written by export_span.py; leaves f positioned
 * after the point list so a caller can read extra records (e.g. seeds) */
static FILE *load_task(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { perror("task"); exit(1); }
    if (fscanf(f, "%d %d %d %d %d", &npts, &nv, &F, &nedges, &rnk) != 5) exit(1);
    vbase = malloc(nv * sizeof(int)); vflip = malloc(nv * sizeof(int));
    need(f, nv, vbase); need(f, nv, vflip);
    rtris = malloc(F * sizeof(*rtris));
    need(f, 3 * F, (int *)rtris);
    edg = malloc(nedges * sizeof(*edg));
    need(f, 9 * nedges, (int *)edg);
    eta_s = malloc(npts);
    for (int i = 0; i < npts; i++) { int v; need(f, 1, &v); eta_s[i] = (signed char)v; }
    basis = malloc((rnk ? rnk : 1) * sizeof(uint64_t));
    for (int i = 0; i < rnk; i++)
        if (fscanf(f, "%" SCNu64, &basis[i]) != 1) { fprintf(stderr, "bad basis\n"); exit(1); }
    for (int i = 0; i < npts; i++) { int a, b; need(f, 1, &a); need(f, 1, &b); }

    sigma = malloc(nv); cursign = malloc(npts); oddv = malloc(F);
    cutl = malloc(F * sizeof(int));
    ufc = malloc(2 * F * sizeof(int)); ufc2 = malloc(2 * F * sizeof(int));
    ufr = malloc(6 * F * sizeof(int)); ufr2 = malloc(6 * F * sizeof(int));
    cmap = malloc(2 * F * sizeof(int)); rmap = malloc(6 * F * sizeof(int));
    region_of = malloc(3 * F * sizeof(int));
    comp_lift = malloc(2 * F * sizeof(int)); reg_lift = malloc(6 * F * sizeof(int));
    adjr = malloc(4 * F * sizeof(int)); adjn = malloc(2 * F * sizeof(int));
    ovals = malloc(2 * F * sizeof(int)); pseudos = malloc(2 * F * sizeof(int));
    rc_head = malloc(6 * F * sizeof(int)); rc_next = malloc(4 * F * sizeof(int));
    parent_reg = malloc(2 * F * sizeof(int));
    frontier = malloc(6 * F * sizeof(int)); nxt = malloc(6 * F * sizeof(int));
    seen_c = malloc(2 * F * sizeof(int)); seen_r = malloc(6 * F * sizeof(int));
    tree_head = malloc(2 * F * sizeof(int)); tree_next = malloc(2 * F * sizeof(int));
    nodeh = malloc(2 * F * sizeof(H128));
    htk = calloc(1u << HTBITS, sizeof(H128)); htu = calloc(1u << HTBITS, sizeof(int));
    return f;
}
#endif
