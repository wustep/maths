/* Backtrack for 3 involution-MOLS of order 12.
 * Free half only; L[k][r+6][c] = L[k][r][c]+6 is implicit.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N 12
#define H 6
#define T 3

static int L[T][H][N];
static uint16_t rowmask[T][H];
static uint8_t colpair[T][N];
/* 72 orbits per pair of squares, bitsets of length 72 */
static uint64_t orb[3][2];
static unsigned long nodes, sols;
static clock_t t0;

static inline int oid(int s, int sp) {
    if (s >= H) return (s - H) * N + ((sp + N - H) % N);
    return s * N + sp;
}

static inline int orb_get(int p, int id) {
    return (int)((orb[p][id >> 6] >> (id & 63)) & 1ULL);
}
static inline void orb_flip(int p, int id) {
    orb[p][id >> 6] ^= 1ULL << (id & 63);
}

static inline int place(int k, int r, int c, int s) {
    if (rowmask[k][r] & (1u << s)) return 0;
    int u = s % H;
    if (colpair[k][c] & (1u << u)) return 0;
    rowmask[k][r] |= (uint16_t)(1u << s);
    colpair[k][c] |= (uint8_t)(1u << u);
    L[k][r][c] = s;
    return 1;
}
static inline void unplace(int k, int r, int c, int s) {
    rowmask[k][r] ^= (uint16_t)(1u << s);
    colpair[k][c] ^= (uint8_t)(1u << (s % H));
    L[k][r][c] = -1;
}

static void rec(int cell);

static void choose(int r, int c, int k) {
    int smin = 0, smax = 11;
    if (r == 0 && k == 0) {
        choose(r, c, 1);
        return;
    }
    if (r == 0 && c == 0 && k == 1) {
        if (place(1, 0, 0, 0)) {
            choose(r, c, 2);
            unplace(1, 0, 0, 0);
        }
        return;
    }
    if (r == 0 && c == 0 && k == 2) {
        if (place(2, 0, 0, 0)) {
            choose(r, c, 3);
            unplace(2, 0, 0, 0);
        }
        return;
    }
    if (r == 0 && c == 1 && k == 2) smin = L[1][0][1];
    if (c == 0 && k == 0 && r >= 1) {
        int opts[2] = {r, r + H};
        for (int i = 0; i < 2; i++) {
            if (!place(0, r, 0, opts[i])) continue;
            choose(r, c, 1);
            unplace(0, r, 0, opts[i]);
        }
        return;
    }
    if (k == 3) {
        int a = L[0][r][c], b = L[1][r][c], e = L[2][r][c];
        int i01 = oid(a, b), i02 = oid(a, e), i12 = oid(b, e);
        if (orb_get(0, i01) || orb_get(1, i02) || orb_get(2, i12)) return;
        orb_flip(0, i01);
        orb_flip(1, i02);
        orb_flip(2, i12);
        /* column-major: next is (r+1,c) then (0,c+1) */
        int next = (r + 1 < H) ? (c * H + (r + 1)) : ((c + 1) * H);
        rec(next);
        orb_flip(0, i01);
        orb_flip(1, i02);
        orb_flip(2, i12);
        return;
    }
    for (int s = smin; s <= smax; s++) {
        if (!place(k, r, c, s)) continue;
        choose(r, c, k + 1);
        unplace(k, r, c, s);
    }
}

static void rec(int cell) {
    nodes++;
    if ((nodes & ((1ul << 22) - 1)) == 0) {
        double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
        fprintf(stderr, "c nodes=%lu sols=%lu cell=%d time=%.1f\n",
                nodes, sols, cell, sec);
    }
    if (cell == H * N) {
        sols++;
        printf("SAT\n");
        for (int k = 0; k < T; k++) {
            printf("# square %d\n", k);
            for (int r = 0; r < H; r++) {
                for (int c = 0; c < N; c++) printf("%2d ", L[k][r][c]);
                putchar('\n');
            }
            for (int r = 0; r < H; r++) {
                for (int c = 0; c < N; c++)
                    printf("%2d ", (L[k][r][c] + H) % N);
                putchar('\n');
            }
        }
        fflush(stdout);
        return;
    }
    choose(cell % H, cell / H, 0);
}

int main(void) {
    memset(L, -1, sizeof L);
    for (int c = 0; c < N; c++) {
        if (!place(0, 0, c, c)) return 2;
    }
    t0 = clock();
    rec(0);
    fprintf(stderr, "c done nodes=%lu sols=%lu time=%.2f\n",
            nodes, sols, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return sols ? 0 : 1;
}
