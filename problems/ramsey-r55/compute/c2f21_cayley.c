/* Inverse-closed Cayley graphs on C2 x F21, F21 = C7 rtimes C3.
   F21 elements: (x,a) x in F7, a in {1,2,4}=<2> <= F7^*.
   Pack F21 as 3*x + log2(a) with log2: 1->0, 2->1, 4->2.
   C2 coordinate is 0/1, total pack 21*c + f.
   gcc -O3 -std=c11 -o c2f21_cayley c2f21_cayley.c
*/

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 17
#define DEG_HI 24

static const int A[3] = {1, 2, 4};

static int f21mul(int p, int q) {
    int px = p / 3, pa = A[p % 3];
    int qx = q / 3, qa = A[q % 3];
    int x = (px + pa * qx) % 7;
    int a = (pa * qa) % 7;
    int ai = (a == 1) ? 0 : (a == 2) ? 1 : 2;
    return 3 * x + ai;
}
static int f21inv(int p) {
    int px = p / 3, pa = A[p % 3];
    int ainv = 1;
    while ((ainv * pa) % 7 != 1) ainv++;
    int x = (7 - (ainv * px) % 7) % 7;
    int ai = (ainv == 1) ? 0 : (ainv == 2) ? 1 : 2;
    return 3 * x + ai;
}

static int mul_el(int a, int b) {
    int ac = a / 21, af = a % 21, bc = b / 21, bf = b % 21;
    return 21 * ((ac + bc) & 1) + f21mul(af, bf);
}
static int inv_el(int a) {
    int ac = a / 21, af = a % 21;
    return 21 * ac + f21inv(af); /* C2 is its own inverse */
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
    for (int a = 0; a < N; a++) {
        if (mul_el(a, 0) != a || mul_el(0, a) != a) {
            fprintf(stderr, "id fail %d\n", a);
            return 2;
        }
        if (mul_el(a, INV[a]) != 0 || mul_el(INV[a], a) != 0) {
            fprintf(stderr, "inv fail %d\n", a);
            return 2;
        }
        for (int b = 0; b < N; b++)
            for (int c = 0; c < N; c++)
                if (mul_el(mul_el(a, b), c) != mul_el(a, mul_el(b, c))) {
                    fprintf(stderr, "assoc fail %d %d %d\n", a, b, c);
                    return 2;
                }
    }
    printf("c C2xF21 npairs=%d ninv=%d group_ok=1\n", npairs, ninv);
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
