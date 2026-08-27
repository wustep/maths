/* Incremental D_22 Cayley census. Same group law as cayley_census d22.

   gcc -O3 -std=c11 -o d22_fast d22_fast.c
   ./d22_fast
*/

#include <stdint.h>
#include <stdio.h>
#include <time.h>

#define N 44
#define DEG_LO 19
#define DEG_HI 24

static int MUL[N][N], INV[N];
static int Slist[N], nS;
static uint64_t Smask;
static unsigned long long leaves, hits, pruned;

static int mul_el(int a, int b) {
    int ak = a % 22, as = a / 22, bk = b % 22, bs = b / 22;
    if (as == 0) return ((ak + bk) % 22) + 22 * bs;
    return ((ak - bk + 22) % 22) + 22 * (1 - bs);
}

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

/* rotations: pairs (k, 22-k) for k=1..10; involution r^11; reflections 22..43 */
static void rec_ref(int k) {
    if (nS > DEG_HI) return;
    if (k == 22) {
        if (nS < DEG_LO) return;
        leaves++;
        uint64_t save = Smask;
        int oldn = nS, oldS[N];
        for (int i = 0; i < nS; i++) oldS[i] = Slist[i];
        Smask = (((1ULL << N) - 2ULL) ^ save);
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
            printf("HIT deg=%d mask=%llu\n", (int)__builtin_popcountll(save),
                   (unsigned long long)save);
            fflush(stdout);
        }
        return;
    }
    int rem = 22 - k;
    if (nS + rem < DEG_LO) return;
    rec_ref(k + 1);
    int x = 22 + k;
    uint64_t bit = 1ULL << x;
    Smask |= bit;
    if (completes_k4(x)) {
        pruned++;
        Smask ^= bit;
        return;
    }
    Slist[nS++] = x;
    rec_ref(k + 1);
    nS--;
    Smask ^= bit;
}

static void rec_r11(void) {
    /* optional involution r^11 = 11 */
    rec_ref(0);
    uint64_t bit = 1ULL << 11;
    Smask |= bit;
    if (completes_k4(11)) {
        pruned++;
        Smask ^= bit;
        return;
    }
    Slist[nS++] = 11;
    rec_ref(0);
    nS--;
    Smask ^= bit;
}

static void rec_rot(int k) {
    if (nS > DEG_HI) return;
    if (k == 11) {
        rec_r11();
        return;
    }
    rec_rot(k + 1);
    int x = k, y = 22 - k;
    uint64_t bits = (1ULL << x) | (1ULL << y);
    Smask |= bits;
    int bad = completes_k4(x) || completes_k4(y);
    if (bad) {
        pruned++;
        Smask ^= bits;
        return;
    }
    Slist[nS++] = x;
    Slist[nS++] = y;
    rec_rot(k + 1);
    nS -= 2;
    Smask ^= bits;
}

int main(void) {
    for (int a = 0; a < N; a++) {
        INV[a] = (a < 22) ? ((22 - a) % 22) : a;
        for (int b = 0; b < N; b++) MUL[a][b] = mul_el(a, b);
    }
    /* r^11 is an involution already handled separately; INV[11]=11 */
    if (INV[11] != 11) {
        fprintf(stderr, "inv 11\n");
        return 2;
    }
    Smask = 0;
    nS = 0;
    clock_t t0 = clock();
    rec_rot(1);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE group=d22 n=44 scanned=%llu hits=%llu pruned=%llu sec=%.3f\n",
           leaves, hits, pruned, sec);
    return 0;
}
