/*
 * poly_enum.c -- prototype: enumerate straight-line programs over Z[x] from
 * {1, x} with +, -, * in the canonical pending-queue order, counting nodes
 * per depth and distinct polynomials reached.  Coefficients are exact
 * __int128 with overflow detection (abort on overflow, to measure).
 * Build: gcc -O3 -march=native -o poly_enum poly_enum.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef __int128 i128;
#define MAXDEG 128
typedef struct { int deg; i128 c[MAXDEG + 1]; } poly_t;   /* deg = -1 for zero */

static uint64_t mix64(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
static uint64_t phash(const poly_t *p) { uint64_t h = 0x1234 + (uint64_t)(p->deg + 1); for (int i = 0; i <= p->deg; i++) { h = mix64(h ^ (uint64_t)p->c[i]); h = mix64(h ^ (uint64_t)((unsigned __int128)p->c[i] >> 64)); } return h; }
static bool peq(const poly_t *a, const poly_t *b) { if (a->deg != b->deg) return false; for (int i = 0; i <= a->deg; i++) if (a->c[i] != b->c[i]) return false; return true; }
static void pnorm(poly_t *p) { while (p->deg >= 0 && p->c[p->deg] == 0) p->deg--; }
static uint64_t overflow_count = 0;
static const i128 LIM = ((i128)1 << 126);
static inline i128 chk(i128 v) { if (v >= LIM || v <= -LIM) { overflow_count++; } return v; }
static void padd(const poly_t *a, const poly_t *b, poly_t *r, int sign) {
    int d = a->deg > b->deg ? a->deg : b->deg; r->deg = d;
    for (int i = 0; i <= d; i++) { i128 x = i <= a->deg ? a->c[i] : 0, y = i <= b->deg ? b->c[i] : 0; r->c[i] = chk(sign > 0 ? x + y : x - y); }
    pnorm(r);
}
static void pmul(const poly_t *a, const poly_t *b, poly_t *r) {
    if (a->deg < 0 || b->deg < 0) { r->deg = -1; return; }
    int d = a->deg + b->deg; if (d > MAXDEG) { fprintf(stderr, "degree overflow\n"); exit(2); }
    r->deg = d; for (int i = 0; i <= d; i++) r->c[i] = 0;
    for (int i = 0; i <= a->deg; i++) if (a->c[i]) for (int j = 0; j <= b->deg; j++) r->c[i + j] = chk(r->c[i + j] + a->c[i] * b->c[j]);
    pnorm(r);
}

#define HBITS 15
#define HSIZE (1u << HBITS)
#define MAXQ 8192
#define MAXD 12
static poly_t *queue; static int qlen;
static poly_t set[MAXD + 2]; static int nset;
static uint32_t hidx[HSIZE]; static uint8_t hstate[HSIZE];   /* 0 empty, 1 in queue, 2 in set; hidx -> queue index or set index */
static poly_t *hval; /* parallel to hstate: pointer to value */
static uint32_t hslot_stack[MAXQ + 64]; static int hslot_top;
static int qblock[MAXD + 2], hmark[MAXD + 2];
static uint64_t nodes[MAXD + 2];
static int g_depth;
/* reached set (distinct polynomials) : simple open addressing on hash + full compare via stored copies */
static uint64_t *reach_a, *reach_b; static uint64_t reach_cap, reach_n; static uint8_t *reach_depth;
static uint64_t depth_new[MAXD + 2];
static void reach_insert(const poly_t *p, int depth) {
    uint64_t h1 = phash(p), h2 = mix64(h1 ^ 0x5bd1e9955bd1e995ULL) ^ (uint64_t)(p->deg + 7);
    for (int i = 0; i <= p->deg; i++) h2 = mix64(h2 + (uint64_t)p->c[i] * 0x9E3779B97F4A7C15ULL);
    uint64_t h = h1 & (reach_cap - 1);
    while (reach_a[h] || reach_b[h]) { if (reach_a[h] == h1 && reach_b[h] == h2) { if (depth < reach_depth[h]) { depth_new[reach_depth[h]]--; reach_depth[h] = depth; depth_new[depth]++; } return; } h = (h + 1) & (reach_cap - 1); }
    reach_a[h] = h1; reach_b[h] = h2; reach_depth[h] = depth; reach_n++; depth_new[depth]++;
    if (reach_n * 2 > reach_cap) { fprintf(stderr, "reach table full\n"); exit(2); }
}
static poly_t hvals[HSIZE];
static uint32_t hfind(const poly_t *p) { uint32_t s = (uint32_t)(phash(p) & (HSIZE - 1)); while (hstate[s]) { if (peq(&hvals[s], p)) return s; s = (s + 1) & (HSIZE - 1); } return s; }
static void enqueue(const poly_t *p) { uint32_t s = hfind(p); if (!hstate[s]) { if (qlen >= MAXQ) { fprintf(stderr, "queue overflow\n"); exit(2); } queue[qlen++] = *p; hvals[s] = *p; hstate[s] = 1; hslot_stack[hslot_top++] = s; } }
static void push(int pos) {
    int d = nset; qblock[d] = qlen; hmark[d] = hslot_top;
    set[d] = queue[pos]; nset = d + 1;
    hstate[hfind(&set[d])] = 2;
    poly_t r;
    for (int i = 0; i <= d; i++) {
        padd(&set[d], &set[i], &r, +1); enqueue(&r);
        pmul(&set[d], &set[i], &r); enqueue(&r);
        if (i != d) { padd(&set[d], &set[i], &r, -1); enqueue(&r); padd(&set[i], &set[d], &r, -1); enqueue(&r); }
        else { /* v - v = 0 */ r.deg = -1; enqueue(&r); }
    }
}
static void pop(void) {
    int d = nset - 1;
    while (hslot_top > hmark[d]) { uint32_t s = hslot_stack[--hslot_top]; hstate[s] = 0; }
    qlen = qblock[d];
    hstate[hfind(&set[d])] = 1;
    nset = d;
}
static void dfs(int qstart) {
    int end = qlen;
    for (int pos = qstart; pos < end; pos++) {
        push(pos);
        int steps = nset - 2;   /* set holds 1, x, then steps values */
        nodes[steps]++;
        reach_insert(&set[nset - 1], steps);
        if (steps < g_depth) dfs(pos + 1);
        pop();
    }
}
int main(int argc, char **argv) {
    g_depth = argc > 1 ? atoi(argv[1]) : 5;
    queue = malloc(sizeof(poly_t) * MAXQ);
    reach_cap = 1ull << (g_depth >= 7 ? 27 : 24); reach_a = calloc(reach_cap, 8); reach_b = calloc(reach_cap, 8); reach_depth = calloc(reach_cap, 1);
    if (!queue || !reach_a || !reach_b) { fprintf(stderr, "malloc\n"); return 2; }
    /* set = {1, x} */
    set[0].deg = 0; set[0].c[0] = 1; set[1].deg = 1; set[1].c[0] = 0; set[1].c[1] = 1; nset = 2;
    hstate[hfind(&set[0])] = 2; hvals[hfind(&set[0])] = set[0]; { uint32_t s = hfind(&set[0]); hvals[s] = set[0]; hstate[s] = 2; }
    { uint32_t s = hfind(&set[1]); hvals[s] = set[1]; hstate[s] = 2; }
    reach_insert(&set[0], 0); reach_insert(&set[1], 0);
    /* initial queue: block from {1, x}: all pairs */
    poly_t r;
    for (int i = 0; i < 2; i++) for (int j = i; j < 2; j++) {
        padd(&set[i], &set[j], &r, +1); enqueue(&r);
        pmul(&set[i], &set[j], &r); enqueue(&r);
        if (i != j) { padd(&set[i], &set[j], &r, -1); enqueue(&r); padd(&set[j], &set[i], &r, -1); enqueue(&r); }
        else { r.deg = -1; enqueue(&r); }
    }
    hmark[1] = hslot_top;   /* the initial block is permanent */
    dfs(0);
    printf("{\"depth\": %d, \"nodes_per_depth\": [", g_depth);
    for (int d = 1; d <= g_depth; d++) printf("%s%llu", d > 1 ? "," : "", (unsigned long long)nodes[d]);
    printf("], \"reached_cumulative\": [");
    uint64_t cum = 0; for (int d = 0; d <= g_depth; d++) { cum += depth_new[d]; printf("%s%llu", d ? "," : "", (unsigned long long)cum); }
    printf("], \"overflow_events\": %llu}\n", (unsigned long long)overflow_count);
    return 0;
}
