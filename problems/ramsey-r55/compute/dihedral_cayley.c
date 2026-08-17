/* Inverse-closed Cayley graphs on D_21 (order 42).

   Elements: rot k = k (k=0..20), ref k = 21+k.
   gcc -O3 -std=c11 -o dihedral_cayley dihedral_cayley.c
*/

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 17
#define DEG_HI 24

static int mul(int a, int b) {
    int ak = a % 21, as = a / 21;
    int bk = b % 21, bs = b / 21;
    if (as == 0) return ((ak + bk) % 21) + 21 * bs;
    return ((ak - bk + 21) % 21) + 21 * (1 - bs);
}

static int inv(int a) {
    if (a < 21) return (21 - a) % 21;
    return a; /* reflections */
}

static int inS[N];
static int Slist[N], nS;
static unsigned long long scanned, hits, pruned;

static int connected(int g, int h) {
    /* edge iff g^{-1}h in S */
    return inS[mul(inv(g), h)];
}

static int has_k4_in_S(void) {
    /* K4 among identity-neighbourhood = S itself */
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
    /* complement connection set */
    int old[N];
    memcpy(old, inS, sizeof(old));
    int oldn = nS;
    int oldS[N];
    memcpy(oldS, Slist, sizeof(oldS));
    nS = 0;
    for (int i = 1; i < N; i++) {
        inS[i] = !old[i];
        if (inS[i]) Slist[nS++] = i;
    }
    int bad = has_k4_in_S();
    memcpy(inS, old, sizeof(old));
    memcpy(Slist, oldS, sizeof(oldS));
    nS = oldn;
    return !bad;
}

/* bits: rot pairs k=1..10 (rot k and rot -k), refs 0..20 */
static int chosen_rot[11]; /* 1..10 */
static int chosen_ref[21];

static void rebuild_S(void) {
    memset(inS, 0, sizeof(inS));
    nS = 0;
    for (int k = 1; k <= 10; k++)
        if (chosen_rot[k]) {
            inS[k] = inS[(21 - k) % 21] = 1;
            Slist[nS++] = k;
            Slist[nS++] = (21 - k) % 21;
        }
    for (int k = 0; k < 21; k++)
        if (chosen_ref[k]) {
            inS[21 + k] = 1;
            Slist[nS++] = 21 + k;
        }
}

static void rec_ref(int k, int deg) {
    if (deg > DEG_HI) return;
    if (k == 21) {
        if (deg < DEG_LO) return;
        scanned++;
        rebuild_S();
        if (nS != deg) {
            fprintf(stderr, "deg mismatch %d %d\n", nS, deg);
        }
        if (is_ramsey()) {
            hits++;
            printf("HIT deg=%d rot=", deg);
            for (int i = 1; i <= 10; i++)
                if (chosen_rot[i]) printf("%d ", i);
            printf("ref=");
            for (int i = 0; i < 21; i++)
                if (chosen_ref[i]) printf("%d ", i);
            printf("\n");
            fflush(stdout);
        }
        return;
    }
    int rem = 21 - k;
    if (deg + rem < DEG_LO) return;
    /* prune: if current S already has K4, both branches die */
    chosen_ref[k] = 0;
    rec_ref(k + 1, deg);
    chosen_ref[k] = 1;
    rebuild_S();
    if (has_k4_in_S()) {
        pruned++;
        chosen_ref[k] = 0;
        return;
    }
    rec_ref(k + 1, deg + 1);
    chosen_ref[k] = 0;
}

static void rec_rot(int k, int deg) {
    if (deg > DEG_HI) return;
    if (k == 11) {
        rec_ref(0, deg);
        return;
    }
    chosen_rot[k] = 0;
    rec_rot(k + 1, deg);
    chosen_rot[k] = 1;
    rebuild_S();
    if (has_k4_in_S()) {
        pruned++;
        chosen_rot[k] = 0;
        return;
    }
    rec_rot(k + 1, deg + 2);
    chosen_rot[k] = 0;
}

int main(void) {
    memset(chosen_rot, 0, sizeof(chosen_rot));
    memset(chosen_ref, 0, sizeof(chosen_ref));
    clock_t t0 = clock();
    rec_rot(1, 0);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE scanned=%llu hits=%llu pruned=%llu sec=%.3f\n", scanned, hits,
           pruned, sec);
    return hits ? 1 : 0;
}
