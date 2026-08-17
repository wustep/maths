/* Inverse-closed Cayley graphs on AGL(1,7) = F7 rtimes F7^* (order 42).
   gcc -O3 -std=c11 -o agl17_cayley agl17_cayley.c
*/

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 17
#define DEG_HI 24

/* pack (x,s) as 6*x + (s-1), s=1..6 */
static int mul_el(int a, int b) {
    int ax = a / 6, as = a % 6 + 1;
    int bx = b / 6, bs = b % 6 + 1;
    int x = (ax + as * bx) % 7;
    int s = (as * bs) % 7;
    return 6 * x + (s - 1);
}
static int inv_el(int a) {
    int ax = a / 6, as = a % 6 + 1;
    /* s^{-1}, then x' = -s^{-1} x */
    int sinv = 1;
    while ((sinv * as) % 7 != 1) sinv++;
    int x = (7 - (sinv * ax) % 7) % 7;
    return 6 * x + (sinv - 1);
}

static int MUL[N][N], INV[N];
static int pair_a[32], pair_b[32], npairs, invol[32], ninv;
static int ch_pair[32], ch_inv[32];
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
    printf("c AGL(1,7) npairs=%d ninv=%d\n", npairs, ninv);
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
