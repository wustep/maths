/* Faster D_21 Cayley census: S is a 42-bit mask, incremental K4 test.
   gcc -O3 -std=c11 -o dihedral_fast dihedral_fast.c
*/

#include <stdint.h>
#include <stdio.h>
#include <time.h>

#define N 42
#define DEG_LO 17
#define DEG_HI 24

static int MUL[N][N], INV[N];

static int mul_el(int a, int b) {
    int ak = a % 21, as = a / 21, bk = b % 21, bs = b / 21;
    if (as == 0) return ((ak + bk) % 21) + 21 * bs;
    return ((ak - bk + 21) % 21) + 21 * (1 - bs);
}

static int Slist[N], nS;
static uint64_t Smask;
static unsigned long long leaves, hits, pruned;

static int completes_k4(int x) {
    /* does x + some 3-set of S form a K4 in the Cayley graph? */
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

/* rot pairs 1..10 add two elements; refs 0..20 add one */
static void rec_ref(int k) {
    if (nS > DEG_HI) return;
    if (k == 21) {
        if (nS < DEG_LO) return;
        leaves++;
        /* complement K4 = K4 in V\S\{e} with edges = non-S differences */
        /* reuse has_k4 on complement mask */
        uint64_t save = Smask;
        int oldn = nS, oldS[N];
        for (int i = 0; i < nS; i++) oldS[i] = Slist[i];
        Smask = ((1ULL << N) - 2ULL) ^ save; /* all non-id not in S */
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
    int rem = 21 - k;
    if (nS + rem < DEG_LO) return;
    /* skip ref k */
    rec_ref(k + 1);
    /* take ref k */
    int x = 21 + k;
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

static void rec_rot(int k) {
    if (nS > DEG_HI) return;
    if (k == 11) {
        rec_ref(0);
        return;
    }
    rec_rot(k + 1);
    int x = k, y = (21 - k) % 21;
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
        INV[a] = (a < 21) ? ((21 - a) % 21) : a;
        for (int b = 0; b < N; b++) MUL[a][b] = mul_el(a, b);
    }
    Smask = 0;
    nS = 0;
    clock_t t0 = clock();
    rec_rot(1);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE leaves=%llu hits=%llu pruned=%llu sec=%.3f\n", leaves, hits,
           pruned, sec);
    return hits ? 1 : 0;
}
