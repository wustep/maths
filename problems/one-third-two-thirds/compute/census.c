/* Naturally labelled width-<=3 posets, exact delta.
 *
 * Recursively add a maximal element. Evaluate at TARGET.
 * Width stays <=3 iff the complement of the new down-set has width <=2.
 *
 * Build: gcc -O3 -march=native -o census census.c
 * Run:   ./census 9
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 12
#define MAXIDEALS 8192

static int TARGET;
static uint16_t down[MAXN];
static uint16_t succ[MAXN];
static int N;

static uint64_t n_natural[MAXN + 1];
static uint64_t n_w3[MAXN + 1];
static uint64_t n_below1439[MAXN + 1];
static uint64_t n_below13[MAXN + 1];
static uint64_t min_num[MAXN + 1];
static uint64_t min_den[MAXN + 1];
static uint64_t min_e[MAXN + 1];
static int min_x[MAXN + 1], min_y[MAXN + 1];
static uint64_t min_cxy[MAXN + 1], min_cyx[MAXN + 1];
static uint16_t min_down[MAXN + 1][MAXN];

static int popcnt(uint32_t x) { return __builtin_popcount(x); }
static int lsb_i(uint32_t x) { return __builtin_ctz(x); }

static uint16_t minima_of(uint16_t mask, int n) {
    uint16_t out = 0;
    uint16_t m = mask;
    while (m) {
        uint16_t b = m & -m;
        int i = lsb_i(b);
        if ((down[i] & mask) == 0) out |= b;
        m ^= b;
    }
    return out;
}

static uint16_t maxima_of(uint16_t mask, int n) {
    uint16_t out = 0;
    uint16_t m = mask;
    while (m) {
        uint16_t b = m & -m;
        int i = lsb_i(b);
        if ((succ[i] & mask) == 0) out |= b;
        m ^= b;
    }
    return out;
}

static int width_le2(uint16_t mask, int n) {
    /* return 1 if width(mask) <= 2 */
    if (mask == 0) return 1;
    int els[MAXN], k = 0;
    uint16_t m = mask;
    while (m) {
        uint16_t b = m & -m;
        els[k++] = lsb_i(b);
        m ^= b;
    }
    if (k <= 2) return 1;
    char inc[MAXN][MAXN];
    memset(inc, 0, sizeof inc);
    for (int a = 0; a < k; a++) {
        int ia = els[a];
        for (int b = a + 1; b < k; b++) {
            int ib = els[b];
            if (((down[ia] >> ib) & 1) == 0 && ((down[ib] >> ia) & 1) == 0)
                inc[a][b] = inc[b][a] = 1;
        }
    }
    for (int a = 0; a < k; a++)
        for (int b = a + 1; b < k; b++) if (inc[a][b])
            for (int c = b + 1; c < k; c++)
                if (inc[a][c] && inc[b][c]) return 0;
    return 1;
}

static int collect_ideals(uint16_t *out, int n) {
    uint16_t full = (uint16_t)((1u << n) - 1);
    int cnt = 0;
    uint16_t q[MAXIDEALS];
    unsigned char seen[1 << MAXN];
    /* n<=12, 1<<12=4096 */
    memset(seen, 0, 1 << n);
    q[cnt++] = 0;
    seen[0] = 1;
    for (int qi = 0; qi < cnt; qi++) {
        uint16_t I = q[qi];
        uint16_t mins = minima_of((uint16_t)(full ^ I), n);
        uint16_t m = mins;
        while (m) {
            uint16_t b = m & -m;
            uint16_t nxt = (uint16_t)(I | b);
            if (!seen[nxt]) {
                if (cnt >= MAXIDEALS) {
                    fprintf(stderr, "too many ideals\n");
                    exit(2);
                }
                seen[nxt] = 1;
                q[cnt++] = nxt;
            }
            m ^= b;
        }
    }
    memcpy(out, q, cnt * sizeof(uint16_t));
    return cnt;
}

static uint64_t Fbuf[1 << MAXN];
static uint64_t Bbuf[1 << MAXN];
static uint64_t Cbuf[MAXN][MAXN];

static void evaluate(int n) {
    n_natural[n]++;
    /* width of the whole poset: we only generate width<=3, check ==3 */
    uint16_t full = (uint16_t)((1u << n) - 1);
    if (width_le2(full, n)) return; /* width <=2 */
    n_w3[n]++;

    uint16_t ideals[MAXIDEALS];
    int ni = collect_ideals(ideals, n);

    memset(Fbuf, 0, sizeof(uint64_t) << n);
    Fbuf[0] = 1;
    /* sort ideals by popcount via counting */
    int start[MAXN + 2] = {0};
    uint16_t sorted[MAXIDEALS];
    int cntp[MAXN + 1] = {0};
    for (int i = 0; i < ni; i++) cntp[popcnt(ideals[i])]++;
    start[0] = 0;
    for (int p = 0; p <= n; p++) start[p + 1] = start[p] + cntp[p];
    int cur[MAXN + 1];
    memcpy(cur, start, sizeof cur);
    for (int i = 0; i < ni; i++) {
        int p = popcnt(ideals[i]);
        sorted[cur[p]++] = ideals[i];
    }
    for (int i = 0; i < ni; i++) {
        uint16_t mask = sorted[i];
        if (mask == 0) continue;
        uint64_t tot = 0;
        uint16_t mx = maxima_of(mask, n);
        uint16_t m = mx;
        while (m) {
            uint16_t b = m & -m;
            tot += Fbuf[mask ^ b];
            m ^= b;
        }
        Fbuf[mask] = tot;
    }
    uint64_t e = Fbuf[full];
    memset(Bbuf, 0, sizeof(uint64_t) << n);
    Bbuf[full] = 1;
    for (int i = ni - 1; i >= 0; i--) {
        uint16_t mask = sorted[i];
        if (mask == full) continue;
        uint16_t rem = (uint16_t)(full ^ mask);
        uint16_t mins = minima_of(rem, n);
        uint16_t m = mins;
        uint64_t tot = 0;
        while (m) {
            uint16_t b = m & -m;
            tot += Bbuf[mask | b];
            m ^= b;
        }
        Bbuf[mask] = tot;
    }

    memset(Cbuf, 0, sizeof Cbuf);
    uint16_t incomp[MAXN];
    for (int i = 0; i < n; i++) {
        incomp[i] = (uint16_t)(full ^ down[i] ^ succ[i] ^ (1u << i));
    }
    for (int ii = 0; ii < ni; ii++) {
        uint16_t I = ideals[ii];
        uint64_t fI = Fbuf[I];
        if (!fI && I) continue;
        for (int x = 0; x < n; x++) {
            if (((I >> x) & 1) == 0) continue;
            uint16_t ys = (uint16_t)(incomp[x] & ~I);
            while (ys) {
                uint16_t b = ys & -ys;
                int y = lsb_i(b);
                if ((down[y] & ~I) == 0) {
                    Cbuf[x][y] += fI * Bbuf[I | b];
                }
                ys ^= b;
            }
        }
    }

    uint64_t best_n = 0, best_d = 1;
    int bx = -1, by = -1;
    uint64_t bxy = 0, byx = 0;
    for (int x = 0; x < n; x++) {
        uint16_t ys = incomp[x];
        while (ys) {
            uint16_t b = ys & -ys;
            int y = lsb_i(b);
            if (x < y) {
                uint64_t a = Cbuf[x][y];
                uint64_t c = Cbuf[y][x];
                if (a + c != e) {
                    fprintf(stderr, "pair sum mismatch n=%d e=%llu a+c=%llu\n",
                            n, (unsigned long long)e,
                            (unsigned long long)(a + c));
                    exit(3);
                }
                uint64_t mn = a < c ? a : c;
                if (mn * best_d > best_n * e) {
                    best_n = mn;
                    best_d = e;
                    bx = x; by = y; bxy = a; byx = c;
                }
            }
            ys ^= b;
        }
    }
    if (best_n * 3 < best_d) n_below13[n]++;
    if (best_n * 39 < best_d * 14) n_below1439[n]++;
    if (best_n * min_den[n] < min_num[n] * best_d) {
        min_num[n] = best_n;
        min_den[n] = best_d;
        min_e[n] = e;
        min_x[n] = bx;
        min_y[n] = by;
        min_cxy[n] = bxy;
        min_cyx[n] = byx;
        memcpy(min_down[n], down, n * sizeof(uint16_t));
    }
}

static void rec(int n) {
    if (n >= 3) evaluate(n);
    if (n == TARGET) return;
    /* generate all ideals of current n-element poset */
    uint16_t ideals[MAXIDEALS];
    int ni;
    if (n == 0) {
        ideals[0] = 0;
        ni = 1;
    } else {
        ni = collect_ideals(ideals, n);
    }
    uint16_t full = n ? (uint16_t)((1u << n) - 1) : 0;
    for (int i = 0; i < ni; i++) {
        uint16_t I = ideals[i];
        uint16_t comp = (uint16_t)(full ^ I);
        if (!width_le2(comp, n)) continue;
        down[n] = I;
        succ[n] = 0;
        /* update succ of predecessors */
        uint16_t m = I;
        uint16_t old[MAXN];
        int preds[MAXN], np = 0;
        while (m) {
            uint16_t b = m & -m;
            int j = lsb_i(b);
            old[np] = succ[j];
            preds[np] = j;
            succ[j] |= (uint16_t)(1u << n);
            np++;
            m ^= b;
        }
        rec(n + 1);
        for (int k = 0; k < np; k++) succ[preds[k]] = old[k];
        succ[n] = 0;
        down[n] = 0;
    }
}

int main(int argc, char **argv) {
    TARGET = argc > 1 ? atoi(argv[1]) : 8;
    if (TARGET < 1 || TARGET > 12) {
        fprintf(stderr, "target 1..12\n");
        return 1;
    }
    for (int i = 0; i <= TARGET; i++) {
        min_num[i] = 1;
        min_den[i] = 2;
    }
    rec(0);
    printf("n\tnat\tw3\tmin_d\t<14/39\t<1/3\te\tpair\n");
    for (int n = 1; n <= TARGET; n++) {
        if (!n_natural[n]) continue;
        printf("%d\t%llu\t%llu\t%llu/%llu\t%llu\t%llu\t%llu\t(%d,%d):%llu/%llu\n",
               n,
               (unsigned long long)n_natural[n],
               (unsigned long long)n_w3[n],
               (unsigned long long)min_num[n],
               (unsigned long long)min_den[n],
               (unsigned long long)n_below1439[n],
               (unsigned long long)n_below13[n],
               (unsigned long long)min_e[n],
               min_x[n], min_y[n],
               (unsigned long long)min_cxy[n],
               (unsigned long long)min_cyx[n]);
    }
    /* dump best down-sets for n>=5 */
    for (int n = 5; n <= TARGET; n++) {
        if (!n_w3[n]) continue;
        printf("BEST n=%d down:", n);
        for (int i = 0; i < n; i++) printf(" %u", (unsigned)min_down[n][i]);
        printf("\n");
    }
    return 0;
}
