/* Inverse-closed Cayley graphs on C3 x D7 (order 42).
   D7: rot 0..6, ref 7..13. C3: 0,1,2. Pack as 14*c + d.
   gcc -O3 -std=c11 -o c3d7_cayley c3d7_cayley.c
*/

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 17
#define DEG_HI 24

static int d7mul(int a, int b) {
    int ak = a % 7, as = a / 7, bk = b % 7, bs = b / 7;
    if (as == 0) return ((ak + bk) % 7) + 7 * bs;
    return ((ak - bk + 7) % 7) + 7 * (1 - bs);
}
static int d7inv(int a) { return (a < 7) ? ((7 - a) % 7) : a; }

static int mul_el(int a, int b) {
    int ac = a / 14, ad = a % 14, bc = b / 14, bd = b % 14;
    return 14 * ((ac + bc) % 3) + d7mul(ad, bd);
}
static int inv_el(int a) {
    int ac = a / 14, ad = a % 14;
    return 14 * ((3 - ac) % 3) + d7inv(ad);
}

static int MUL[N][N], INV[N];
static int pair_a[32], pair_b[32], npairs, invol[32], ninv;
static int Slist[N], nS;
static uint64_t Smask;
static unsigned long long leaves, hits, pruned;

static int completes_k4(int x) {
    for (int a = 0; a < nS; a++) {
        int ga = Slist[a];
        if (!((Smask >> MUL[INV[ga]][x]) & 1ULL)) continue;
        for (int b = a + 1; b < nS; b++) {
            int gb = Slist[b];
            if (!((Smask >> MUL[INV[gb]][x]) & 1ULL)) continue;
            if (!((Smask >> MUL[INV[ga]][gb]) & 1ULL)) continue;
            for (int c = b + 1; c < nS; c++) {
                int gc = Slist[c];
                if (((Smask >> MUL[INV[gc]][x]) & 1ULL) &&
                    ((Smask >> MUL[INV[ga]][gc]) & 1ULL) &&
                    ((Smask >> MUL[INV[gb]][gc]) & 1ULL))
                    return 1;
            }
        }
    }
    return 0;
}

static int has_k4(void) {
    for (int a = 0; a < nS; a++) {
        int ga = Slist[a];
        for (int b = a + 1; b < nS; b++) {
            int gb = Slist[b];
            if (!((Smask >> MUL[INV[ga]][gb]) & 1ULL)) continue;
            for (int c = b + 1; c < nS; c++) {
                int gc = Slist[c];
                if (!((Smask >> MUL[INV[ga]][gc]) & 1ULL)) continue;
                if (!((Smask >> MUL[INV[gb]][gc]) & 1ULL)) continue;
                for (int d = c + 1; d < nS; d++) {
                    int gd = Slist[d];
                    if (((Smask >> MUL[INV[ga]][gd]) & 1ULL) &&
                        ((Smask >> MUL[INV[gb]][gd]) & 1ULL) &&
                        ((Smask >> MUL[INV[gc]][gd]) & 1ULL))
                        return 1;
                }
            }
        }
    }
    return 0;
}

static void rec_inv(int k) {
    if (nS > DEG_HI) return;
    if (k == ninv) {
        if (nS < DEG_LO) return;
        leaves++;
        uint64_t save = Smask;
        int oldn = nS, oldS[N];
        for (int i = 0; i < nS; i++) oldS[i] = Slist[i];
        Smask = ((1ULL << N) - 2ULL) ^ save;
        nS = 0;
        uint64_t m = Smask;
        while (m) {
            uint64_t b = m & -m;
            Slist[nS++] = __builtin_ctzll(b);
            m ^= b;
        }
        int bad = has_k4();
        Smask = save;
        nS = oldn;
        for (int i = 0; i < nS; i++) Slist[i] = oldS[i];
        if (!bad) {
            hits++;
            printf("HIT deg=%d mask=%llu\n", nS, (unsigned long long)save);
            fflush(stdout);
        }
        return;
    }
    if (nS + (ninv - k) < DEG_LO) return;
    rec_inv(k + 1);
    int x = invol[k];
    Smask |= 1ULL << x;
    if (completes_k4(x)) {
        pruned++;
        Smask ^= 1ULL << x;
        return;
    }
    Slist[nS++] = x;
    rec_inv(k + 1);
    nS--;
    Smask ^= 1ULL << x;
}

static void rec_pair(int k) {
    if (nS > DEG_HI) return;
    if (k == npairs) {
        rec_inv(0);
        return;
    }
    rec_pair(k + 1);
    int x = pair_a[k], y = pair_b[k];
    uint64_t bits = (1ULL << x) | (1ULL << y);
    Smask |= bits;
    if (completes_k4(x) || completes_k4(y)) {
        pruned++;
        Smask ^= bits;
        return;
    }
    Slist[nS++] = x;
    Slist[nS++] = y;
    rec_pair(k + 1);
    nS -= 2;
    Smask ^= bits;
}

int main(void) {
    for (int a = 0; a < N; a++) {
        INV[a] = inv_el(a);
        for (int b = 0; b < N; b++) MUL[a][b] = mul_el(a, b);
    }
    int seen[N];
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
    printf("c C3xD7 npairs=%d ninv=%d\n", npairs, ninv);
    fflush(stdout);
    Smask = 0;
    nS = 0;
    clock_t t0 = clock();
    rec_pair(0);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE leaves=%llu hits=%llu pruned=%llu sec=%.3f\n", leaves, hits,
           pruned, sec);
    return hits ? 1 : 0;
}
