/* aut_group.c -- automorphism group of a column set S in F_2^r.
 *
 * Aut(S) = { g in GL(r,2) : g(S) = S }.  q10 prescribes exactly this kind of
 * symmetry, so it is worth knowing how much of it the coverings people already
 * have actually carry.
 *
 * Colour the columns by refinable invariants -- the pair count
 * w(x) = #{ {a,b} subset S : a+b = x }, refined through the multiset of
 * (colour(t), w(s+t)) -- then backtrack over the images of a basis drawn from
 * S, rejecting a partial image as soon as some element of S already inside the
 * span maps outside S.  The count returned is the full group order: the
 * backtrack enumerates every g with g(S) = S.
 *
 * Build: gcc -O2 -o aut_group aut_group.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXR 12
#define MAXNV (1 << MAXR)
#define MAXN 512

static int R, NV, n;
static int S[MAXN];
static int w[MAXNV];
static unsigned char inS[MAXNV];
static int col[MAXN];
static int basis[MAXR], posmask[MAXNV];
static int fresh[MAXR][MAXN], nfresh[MAXR];
static int spanv[MAXNV];
static unsigned char inspan[MAXNV];
static long long found, nodes;
static int do_list, images[MAXR];

static int cmp_int(const void *a, const void *b) { return *(const int *)a - *(const int *)b; }

static int read_set(const char *path) {
    FILE *fh = fopen(path, "r");
    if (!fh) { perror(path); exit(2); }
    char line[1 << 16];
    int rows[MAXR][MAXN], nrows = 0, ncols = 0, flat[MAXN], nflat = 0;
    while (fgets(line, sizeof line, fh)) {
        char *h = strchr(line, '#');
        if (h) *h = 0;
        int vals[MAXN], nv = 0, only01 = 1;
        char *tok = strtok(line, " \t\r\n");
        while (tok) {
            size_t len = strlen(tok);
            int bits = 1;
            for (size_t q = 0; q < len; q++) if (tok[q] != '0' && tok[q] != '1') bits = 0;
            if (bits && len > 12) {                 /* a contiguous row of bits */
                for (size_t q = 0; q < len && nv < MAXN; q++) vals[nv++] = tok[q] - '0';
            } else {
                long v = strtol(tok, NULL, 10);
                if (v != 0 && v != 1) only01 = 0;
                if (nv < MAXN) vals[nv++] = (int)v;
            }
            tok = strtok(NULL, " \t\r\n");
        }
        if (!nv) continue;
        if (only01 && nv > 12) {
            if (nrows < MAXR) { memcpy(rows[nrows], vals, sizeof(int) * nv); ncols = nv; nrows++; }
        } else {
            for (int i = 0; i < nv; i++) if (nflat < MAXN) flat[nflat++] = vals[i];
        }
    }
    fclose(fh);
    if (nrows) {
        R = nrows; n = 0;
        for (int j = 0; j < ncols; j++) {
            int v = 0;
            for (int i = 0; i < nrows; i++) if (rows[i][j] & 1) v |= 1 << i;
            S[n++] = v;
        }
    } else {
        n = nflat;
        memcpy(S, flat, sizeof(int) * n);
        int mx = 0;
        for (int i = 0; i < n; i++) if (S[i] > mx) mx = S[i];
        R = 0; while ((1 << R) <= mx) R++;
    }
    qsort(S, n, sizeof(int), cmp_int);
    int m = 0;
    for (int i = 0; i < n; i++) if (!i || S[i] != S[i - 1]) S[m++] = S[i];
    n = m;
    NV = 1 << R;
    return n;
}

static void build_colours(void) {
    memset(w, 0, sizeof(int) * NV);
    memset(inS, 0, NV);
    for (int i = 0; i < n; i++) inS[S[i]] = 1;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) w[S[i] ^ S[j]]++;
    for (int i = 0; i < n; i++) col[i] = w[S[i]];
    /* compress to ranks, then refine */
    for (int round = 0; round < 8; round++) {
        static long long sig[MAXN][MAXN];
        static long long key[MAXN];
        for (int i = 0; i < n; i++) {
            int c = 0;
            for (int j = 0; j < n; j++)
                if (j != i) sig[i][c++] = (long long)col[j] * 4096 + w[S[i] ^ S[j]];
            for (int a = 0; a < c; a++)
                for (int b = a + 1; b < c; b++)
                    if (sig[i][b] < sig[i][a]) { long long t = sig[i][a]; sig[i][a] = sig[i][b]; sig[i][b] = t; }
            long long h = 1469598103934665603LL ^ col[i];
            for (int a = 0; a < c; a++) { h ^= sig[i][a]; h *= 1099511628211LL; }
            key[i] = h;
        }
        int newcol[MAXN], nc = 0;
        long long seen[MAXN];
        for (int i = 0; i < n; i++) {
            int f = -1;
            for (int a = 0; a < nc; a++) if (seen[a] == key[i]) { f = a; break; }
            if (f < 0) { seen[nc] = key[i]; f = nc++; }
            newcol[i] = f;
        }
        int oldnc = 0;
        for (int i = 0; i < n; i++) if (col[i] + 1 > oldnc) oldnc = col[i] + 1;
        memcpy(col, newcol, sizeof(int) * n);
        if (nc == oldnc) break;
    }
}

static void rec(int i, int size) {
    nodes++;
    if (i == R) {
        found++;
        if (do_list) {
            printf("g");
            for (int j = 0; j < R; j++) printf(" %d", images[j]);
            printf("\n");
        }
        return;
    }
    int bi = -1;
    for (int a = 0; a < n; a++) if (S[a] == basis[i]) { bi = a; break; }
    for (int a = 0; a < n; a++) {
        if (col[a] != col[bi]) continue;
        int c = S[a];
        if (inspan[c]) continue;                     /* image must stay independent */
        int ok = 1;
        for (int m = 0; m < size; m++) spanv[size + m] = spanv[m] ^ c;
        for (int t = 0; t < nfresh[i]; t++)
            if (!inS[spanv[fresh[i][t]]]) { ok = 0; break; }
        if (ok) {
            images[i] = c;
            for (int m = 0; m < size; m++) inspan[spanv[size + m]] = 1;
            rec(i + 1, size << 1);
            for (int m = 0; m < size; m++) inspan[spanv[size + m]] = 0;
        }
    }
}

int main(int argc, char **argv) {
    for (int f = 1; f < argc; f++) {
        if (!strcmp(argv[f], "--list")) { do_list = 1; continue; }
        read_set(argv[f]);
        build_colours();

        int nb = 0;
        memset(inspan, 0, NV);
        inspan[0] = 1;
        int sv[MAXNV]; sv[0] = 0; int sz = 1;
        for (int i = 0; i < n && nb < R; i++) {
            if (inspan[S[i]]) continue;
            basis[nb++] = S[i];
            for (int m = 0; m < sz; m++) { sv[sz + m] = sv[m] ^ S[i]; inspan[sv[sz + m]] = 1; }
            sz <<= 1;
        }
        if (nb != R) { fprintf(stderr, "%s: S does not span\n", argv[f]); continue; }
        for (int v = 0; v < NV; v++) posmask[v] = -1;
        for (int m = 0; m < (1 << R); m++) {
            int val = 0;
            for (int j = 0; j < R; j++) if ((m >> j) & 1) val ^= basis[j];
            posmask[val] = m;
        }
        for (int i = 0; i < R; i++) nfresh[i] = 0;
        for (int i = 0; i < n; i++) {
            int m = posmask[S[i]], top = 31 - __builtin_clz(m);
            fresh[top][nfresh[top]++] = m;
        }
        int ncol = 0;
        for (int i = 0; i < n; i++) if (col[i] + 1 > ncol) ncol = col[i] + 1;

        memset(inspan, 0, NV);
        inspan[0] = 1;
        spanv[0] = 0;
        found = nodes = 0;
        rec(0, 1);
        if (do_list) {
            printf("basis");
            for (int j = 0; j < R; j++) printf(" %d", basis[j]);
            printf("\nset");
            for (int j = 0; j < n; j++) printf(" %d", S[j]);
            printf("\n");
        }
        printf("%s: r=%d |S|=%d colour classes=%d |Aut(S)|=%lld (nodes %lld)\n",
               argv[f], R, n, ncol, found, nodes);
    }
    return 0;
}
