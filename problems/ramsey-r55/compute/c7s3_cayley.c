/* Inverse-closed Cayley graphs on C7 x S3 (order 42).

   Elements: (z, s) with z in Z/7, s in S3 = {0,1,2,3,4,5}
   S3 as D3: 0,1,2 rotations, 3,4,5 reflections.
   gcc -O3 -std=c11 -o c7s3_cayley c7s3_cayley.c
*/

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N 42
#define DEG_LO 17
#define DEG_HI 24

/* pack (z,s) as 6*z + s */
static int s3mul[6][6];
static int s3inv[6];

static void init_s3(void) {
    /* D3: rot a=0,1,2; ref r=3,4,5 with r_i = rot_i * ref_0, ref_0=3 */
    /* use permutation representation: S3 on {0,1,2} as numbers 0..5
       0=id, 1=(012), 2=(021), 3=(12), 4=(02), 5=(01) */
    static const int p[6][3] = {
        {0, 1, 2}, {1, 2, 0}, {2, 0, 1}, {0, 2, 1}, {2, 1, 0}, {1, 0, 2},
    };
    for (int a = 0; a < 6; a++)
        for (int b = 0; b < 6; b++) {
            int q[3] = {p[a][p[b][0]], p[a][p[b][1]], p[a][p[b][2]]};
            int found = -1;
            for (int c = 0; c < 6; c++)
                if (q[0] == p[c][0] && q[1] == p[c][1] && q[2] == p[c][2])
                    found = c;
            s3mul[a][b] = found;
        }
    for (int a = 0; a < 6; a++)
        for (int b = 0; b < 6; b++)
            if (s3mul[a][b] == 0) s3inv[a] = b;
}

static int mul(int a, int b) {
    int az = a / 6, as = a % 6;
    int bz = b / 6, bs = b % 6;
    return 6 * ((az + bz) % 7) + s3mul[as][bs];
}
static int invi(int a) {
    int az = a / 6, as = a % 6;
    return 6 * ((7 - az) % 7) + s3inv[as];
}

static int inS[N], Slist[N], nS;
static unsigned long long scanned, hits, pruned;

static int connected(int g, int h) { return inS[mul(invi(g), h)]; }

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
    int old[N], oldS[N], oldn = nS;
    memcpy(old, inS, sizeof(old));
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

/* Inverse pairs among {1..41}. Involutions are free bits. */
static int pair_a[32], pair_b[32], npairs;
static int invol[32], ninv;
static int ch_pair[32], ch_inv[32];

static void classify(void) {
    int seen[N];
    memset(seen, 0, sizeof(seen));
    npairs = ninv = 0;
    for (int g = 1; g < N; g++) {
        if (seen[g]) continue;
        int h = invi(g);
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
            printf("HIT deg=%d pairs=", deg);
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

int main(void) {
    init_s3();
    classify();
    printf("c C7xS3 npairs=%d ninv=%d\n", npairs, ninv);
    fflush(stdout);
    clock_t t0 = clock();
    rec_pair(0, 0);
    double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("DONE scanned=%llu hits=%llu pruned=%llu sec=%.3f\n", scanned, hits,
           pruned, sec);
    return hits ? 1 : 0;
}
