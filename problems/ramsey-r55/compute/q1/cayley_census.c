/* Inverse-closed undirected Cayley (5,5)-census on groups of order 44 and 45.

   gcc -O3 -std=c11 -o cayley_census cayley_census.c
   ./cayley_census c2c22
   ./cayley_census d22
   ./cayley_census c11c4
   ./cayley_census c3c15

   Degree window from R(4,5)=25: [n-25, 24].
   Incremental K4 prune on the connection set (vertex-transitive).
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 64

static int N, DEG_LO, DEG_HI;
static int MUL[MAXN][MAXN], INV[MAXN];
static const char *GNAME;

static int inS[MAXN], Slist[MAXN], nS;
static unsigned long long scanned, hits, pruned;

static int pair_a[64], pair_b[64], npairs;
static int invol[64], ninv;
static int ch_pair[64], ch_inv[64];

static int mul_c2c22(int a, int b) {
    return 22 * (((a / 22) + (b / 22)) & 1) + ((a % 22 + b % 22) % 22);
}
static int mul_d22(int a, int b) {
    int ak = a % 22, as = a / 22, bk = b % 22, bs = b / 22;
    if (as == 0) return ((ak + bk) % 22) + 22 * bs;
    return ((ak - bk + 22) % 22) + 22 * (1 - bs);
}
static int mul_c11c4(int x, int y) {
    int a1 = x % 11, b1 = x / 11, a2 = y % 11, b2 = y / 11;
    int a = (b1 % 2 == 0) ? (a1 + a2) % 11 : (a1 - a2 + 11) % 11;
    return 11 * ((b1 + b2) % 4) + a;
}
static int mul_c3c15(int a, int b) {
    return 15 * (((a / 15) + (b / 15)) % 3) + ((a % 15 + b % 15) % 15);
}

static void fill_from(int (*mul)(int, int), int n) {
    N = n;
    DEG_LO = n - 25;
    if (DEG_LO < 0) DEG_LO = 0;
    DEG_HI = 24;
    if (DEG_HI > n - 1) DEG_HI = n - 1;
    for (int a = 0; a < n; a++)
        for (int b = 0; b < n; b++) MUL[a][b] = mul(a, b);
    for (int a = 0; a < n; a++) {
        int found = -1;
        for (int b = 0; b < n; b++)
            if (MUL[a][b] == 0 && MUL[b][a] == 0) found = b;
        if (found < 0) {
            fprintf(stderr, "no inverse %d\n", a);
            exit(2);
        }
        INV[a] = found;
    }
    /* identity / a sample of associativity */
    for (int a = 0; a < n; a++)
        if (MUL[a][0] != a || MUL[0][a] != a) {
            fprintf(stderr, "id fail\n");
            exit(2);
        }
    for (int a = 0; a < n; a++)
        for (int b = 0; b < n; b++)
            for (int c = 0; c < n; c++)
                if (MUL[MUL[a][b]][c] != MUL[a][MUL[b][c]]) {
                    fprintf(stderr, "assoc fail %d %d %d\n", a, b, c);
                    exit(2);
                }
}

static int connected(int g, int h) { return inS[MUL[INV[g]][h]]; }

static int has_k4_in_S(void) {
    for (int a = 0; a < nS; a++) {
        int ga = Slist[a];
        for (int b = a + 1; b < nS; b++) {
            int gb = Slist[b];
            if (!connected(ga, gb)) continue;
            for (int c = b + 1; c < nS; c++) {
                int gc = Slist[c];
                if (!connected(ga, gc) || !connected(gb, gc)) continue;
                for (int d = c + 1; d < nS; d++) {
                    int gd = Slist[d];
                    if (connected(ga, gd) && connected(gb, gd) && connected(gc, gd))
                        return 1;
                }
            }
        }
    }
    return 0;
}

static int is_ramsey(void) {
    if (has_k4_in_S()) return 0;
    int old[MAXN], oldS[MAXN], oldn = nS;
    memcpy(old, inS, sizeof(int) * N);
    memcpy(oldS, Slist, sizeof(int) * N);
    nS = 0;
    for (int i = 1; i < N; i++) {
        inS[i] = !old[i];
        if (inS[i]) Slist[nS++] = i;
    }
    int bad = has_k4_in_S();
    memcpy(inS, old, sizeof(int) * N);
    memcpy(Slist, oldS, sizeof(int) * N);
    nS = oldn;
    return !bad;
}

static void classify(void) {
    int seen[MAXN];
    memset(seen, 0, sizeof(seen));
    npairs = ninv = 0;
    for (int g = 1; g < N; g++) {
        if (seen[g]) continue;
        int h = INV[g];
        if (h == g) {
            invol[ninv++] = g;
            seen[g] = 1;
        } else {
            pair_a[npairs] = g;
            pair_b[npairs] = h;
            seen[g] = seen[h] = 1;
            npairs++;
        }
    }
}

static void rebuild(void) {
    memset(inS, 0, sizeof(inS));
    nS = 0;
    for (int i = 0; i < npairs; i++)
        if (ch_pair[i]) {
            inS[pair_a[i]] = inS[pair_b[i]] = 1;
            Slist[nS++] = pair_a[i];
            Slist[nS++] = pair_b[i];
        }
    for (int i = 0; i < ninv; i++)
        if (ch_inv[i]) {
            inS[invol[i]] = 1;
            Slist[nS++] = invol[i];
        }
}

static void rec_inv(int k, int deg) {
    if (deg > DEG_HI) return;
    if (k == ninv) {
        if (deg < DEG_LO) return;
        scanned++;
        rebuild();
        if (is_ramsey()) {
            hits++;
            printf("HIT group=%s n=%d deg=%d pairs=", GNAME, N, deg);
            for (int i = 0; i < npairs; i++)
                if (ch_pair[i]) printf("%d ", pair_a[i]);
            printf("inv=");
            for (int i = 0; i < ninv; i++)
                if (ch_inv[i]) printf("%d ", invol[i]);
            printf("\n");
            fflush(stdout);
        }
        return;
    }
    int rem = ninv - k;
    if (deg + rem < DEG_LO) return;
    ch_inv[k] = 0;
    rec_inv(k + 1, deg);
    ch_inv[k] = 1;
    rebuild();
    if (has_k4_in_S()) {
        pruned++;
        ch_inv[k] = 0;
        return;
    }
    rec_inv(k + 1, deg + 1);
    ch_inv[k] = 0;
}

static void rec_pair(int k, int deg) {
    if (deg > DEG_HI) return;
    if (k == npairs) {
        rec_inv(0, deg);
        return;
    }
    int rem_pairs = npairs - k;
    if (deg + 2 * rem_pairs + ninv < DEG_LO) return;
    ch_pair[k] = 0;
    rec_pair(k + 1, deg);
    ch_pair[k] = 1;
    rebuild();
    if (has_k4_in_S()) {
        pruned++;
        ch_pair[k] = 0;
        return;
    }
    rec_pair(k + 1, deg + 2);
    ch_pair[k] = 0;
}

static void run(void) {
    classify();
    printf("c group=%s n=%d npairs=%d ninv=%d deg=[%d,%d]\n", GNAME, N, npairs,
           ninv, DEG_LO, DEG_HI);
    fflush(stdout);
    scanned = hits = pruned = 0;
    memset(ch_pair, 0, sizeof(ch_pair));
    memset(ch_inv, 0, sizeof(ch_inv));
    clock_t t0 = clock();
    rec_pair(0, 0);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE group=%s n=%d scanned=%llu hits=%llu pruned=%llu sec=%.3f\n",
           GNAME, N, scanned, hits, pruned, sec);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s c2c22|d22|c11c4|c3c15\n", argv[0]);
        return 2;
    }
    GNAME = argv[1];
    if (strcmp(GNAME, "c2c22") == 0)
        fill_from(mul_c2c22, 44);
    else if (strcmp(GNAME, "d22") == 0)
        fill_from(mul_d22, 44);
    else if (strcmp(GNAME, "c11c4") == 0)
        fill_from(mul_c11c4, 44);
    else if (strcmp(GNAME, "c3c15") == 0)
        fill_from(mul_c3c15, 45);
    else {
        fprintf(stderr, "unknown group %s\n", GNAME);
        return 2;
    }
    run();
    return 0; /* completed; hits are in the log */
}
