/* q9: exact quotient-block replacement for binary radius-2 covering codes at r=10.
 *
 * Every column set S of F_2^r splits, along a 2-dimensional quotient
 * q : F_2^r -> F_2^2, into four blocks (A;B,C,D): A = S cap V with V = ker q,
 * and B,C,D the fibres over the three nonzero labels.  Choosing coset
 * representatives with t01 + t10 = t11 makes radius-2 covering equivalent to
 * four conditions inside V (all sums are inside V):
 *
 *   (00)  {0} u A u D(A) u D(B) u D(C) u D(D) = V        D(X) = {x+x' : x != x'}
 *   (01)  (A u {0}) + B  u  C + D             = V
 *   (10)  (A u {0}) + C  u  B + D             = V
 *   (11)  (A u {0}) + D  u  B + C             = V
 *
 * Fix A, B, C.  Then every condition involving D is either a hitting-set
 * constraint on D or a pair constraint on D(D):
 *
 *   for u not in (A+ + B): D cap (u + C)  != empty
 *   for u not in (A+ + C): D cap (u + B)  != empty
 *   for u not in (B  + C): D cap (u + A+) != empty
 *   for h not in {0} u A u D(A) u D(B) u D(C): h in D(D)
 *
 * so "is there ANY block of size <= k that completes A,B,C to a covering" is a
 * finite exact question.  This file decides it by constraint-directed DFS with
 * exclusion (complete, no duplicate subtrees) and counting prunes.  Replacing a
 * whole block is a swap of up to |D| columns at once, which is exactly the move
 * a k-swap prover cannot reach.
 *
 * Modes:
 *   --shrink   ask for a block of size |D|-1  (n -> n-1)
 *   --resolve  ask for a block of size |D|    (same n, different block)
 *
 * Usage: block_solve --input <cols|matrix> [--shrink|--resolve] [--maxblock M]
 *                    [--nodes N] [--shard i/N] [--out FILE]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define R      10
#define FULL   (1 << R)
#define VDIM   (R - 2)
#define VSZ    (1 << VDIM)

static int  cols[256], ncols;

/* ---------- instance ---------- */
static int  Ap[VSZ], nAp;          /* A u {0} */
static int  Bv[VSZ], nB;
static int  Cv[VSZ], nC;
static int  U1[VSZ], nU1;          /* need D cap (u+C)  */
static int  U2[VSZ], nU2;          /* need D cap (u+B)  */
static int  U3[VSZ], nU3;          /* need D cap (u+Ap) */
static int  U0[VSZ], nU0;          /* need in D(D)      */
static int  in1[VSZ], in2[VSZ], in3[VSZ], in0[VSZ];   /* membership flags */
static int  c1[VSZ], c2[VSZ], c3[VSZ], c0[VSZ];       /* satisfaction counts */
static int  rem1, rem2, rem3, rem0;
static int  excl[VSZ], inD[VSZ];
static int  Dcur[64], nD, Kbudget;
static long nodes, node_cap;
static int  Dout[64], nDout;

static int parity(int x) { return __builtin_parity(x); }

static void add_elem(int d)
{
    int i;
    for (i = 0; i < nC; i++) { int u = d ^ Cv[i]; if (in1[u] && c1[u]++ == 0) rem1--; }
    for (i = 0; i < nB; i++) { int u = d ^ Bv[i]; if (in2[u] && c2[u]++ == 0) rem2--; }
    for (i = 0; i < nAp; i++){ int u = d ^ Ap[i]; if (in3[u] && c3[u]++ == 0) rem3--; }
    for (i = 0; i < nD; i++) { int h = d ^ Dcur[i]; if (in0[h] && c0[h]++ == 0) rem0--; }
    inD[d] = 1;
    Dcur[nD++] = d;
}

static void del_elem(void)
{
    int i, d = Dcur[--nD];
    inD[d] = 0;
    for (i = 0; i < nD; i++) { int h = d ^ Dcur[i]; if (in0[h] && --c0[h] == 0) rem0++; }
    for (i = 0; i < nAp; i++){ int u = d ^ Ap[i]; if (in3[u] && --c3[u] == 0) rem3++; }
    for (i = 0; i < nB; i++) { int u = d ^ Bv[i]; if (in2[u] && --c2[u] == 0) rem2++; }
    for (i = 0; i < nC; i++) { int u = d ^ Cv[i]; if (in1[u] && --c1[u] == 0) rem1++; }
}

static int pairs(int m) { return m * (m - 1) / 2; }

/* returns 1 = solved, 0 = exhausted, -1 = node cap hit */
static int dfs(void)
{
    int budget = Kbudget - nD, i, j, hit;
    if (++nodes > node_cap) return -1;
    if (rem1 == 0 && rem2 == 0 && rem3 == 0 && rem0 == 0) {
        memcpy(Dout, Dcur, nD * sizeof(int)); nDout = nD; return 1;
    }
    if (budget <= 0) return 0;
    if (rem1 > (long)budget * nC)  return 0;
    if (rem2 > (long)budget * nB)  return 0;
    if (rem3 > (long)budget * nAp) return 0;
    if (rem0 > pairs(Kbudget) - pairs(nD)) return 0;

    /* branch on the unsatisfied constraint with the fewest live candidates */
    int best = -1, bestcnt = 1 << 30, bestfam = 0;
    for (i = 0; i < nU1; i++) {
        int u = U1[i]; if (c1[u]) continue;
        int cnt = 0; for (j = 0; j < nC; j++) if (!excl[u ^ Cv[j]]) cnt++;
        if (cnt < bestcnt) { bestcnt = cnt; best = u; bestfam = 1; if (!cnt) break; }
    }
    if (bestcnt) for (i = 0; i < nU2; i++) {
        int u = U2[i]; if (c2[u]) continue;
        int cnt = 0; for (j = 0; j < nB; j++) if (!excl[u ^ Bv[j]]) cnt++;
        if (cnt < bestcnt) { bestcnt = cnt; best = u; bestfam = 2; if (!cnt) break; }
    }
    if (bestcnt && best < 0) for (i = 0; i < nU3; i++) {
        int u = U3[i]; if (c3[u]) continue;
        int cnt = 0; for (j = 0; j < nAp; j++) if (!excl[u ^ Ap[j]]) cnt++;
        if (cnt < bestcnt) { bestcnt = cnt; best = u; bestfam = 3; if (!cnt) break; }
    }
    if (best >= 0) {
        if (bestcnt == 0) return 0;
        int cand[64], nc2 = 0;
        int *src = bestfam == 1 ? Cv : bestfam == 2 ? Bv : Ap;
        int ns   = bestfam == 1 ? nC : bestfam == 2 ? nB : nAp;
        for (j = 0; j < ns; j++) { int d = best ^ src[j]; if (!excl[d]) cand[nc2++] = d; }
        for (j = 0; j < nc2; j++) {
            int d = cand[j];
            excl[d] = 1; add_elem(d);
            int r = dfs();
            del_elem();
            if (r) { if (r == 1) return 1; /* node cap */ excl[d] = 0; return -1; }
            /* keep d excluded for the remaining siblings: standard exact branching */
        }
        for (j = 0; j < nc2; j++) excl[cand[j]] = 0;
        return 0;
    }
    /* only pair constraints left.  The branches "h is covered by the pair
     * {d, d+h}" are exhaustive but NOT disjoint, so no sibling exclusion is
     * sound here; we branch without excluding. */
    for (i = 0; i < nU0; i++) {
        int h = U0[i]; if (c0[h]) continue;
        for (int d = 0; d < VSZ; d++) {
            int e = d ^ h;
            if (d > e) continue;
            if (excl[d] && !inD[d]) continue;
            if (excl[e] && !inD[e]) continue;
            int need = (!inD[d]) + (!inD[e]);
            if (need > budget) continue;
            int added = 0;
            if (!inD[d]) { excl[d] = 1; add_elem(d); added++; }
            if (!inD[e]) { excl[e] = 1; add_elem(e); added++; }
            int r = dfs();
            while (added--) { int z = Dcur[nD-1]; del_elem(); excl[z] = 0; }
            if (r == 1) return 1;
            if (r < 0) return -1;
        }
        return 0;
    }
    return 0;
}

/* ---------- driver ---------- */
static int load(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(2); }
    char line[4096], rows[R][4096];
    int nr = 0, i;
    ncols = 0;
    while (fgets(line, sizeof line, f)) {
        char *h = strchr(line, '#'); if (h) *h = 0;
        int only01 = 1, any = 0;
        for (char *p = line; *p; p++) {
            if (*p == '0' || *p == '1') any = 1;
            else if (*p != ' ' && *p != '\t' && *p != '\n' && *p != '\r') only01 = 0;
        }
        if (!any) continue;
        if (only01 && nr < R) { int k = 0;
            for (char *p = line; *p; p++) if (*p=='0'||*p=='1') rows[nr][k++] = *p;
            rows[nr][k] = 0; nr++; continue; }
        char *tok = strtok(line, " \t\n\r");
        while (tok) { cols[ncols++] = (int)strtol(tok, NULL, 0); tok = strtok(NULL, " \t\n\r"); }
    }
    fclose(f);
    if (nr == R) {
        int n = (int)strlen(rows[0]);
        ncols = n;
        for (i = 0; i < n; i++) { int v = 0;
            for (int b = 0; b < R; b++) if (rows[b][i] == '1') v |= 1 << b;
            cols[i] = v; }
    }
    return ncols;
}

static int covered_count(const int *s, int n)
{
    static unsigned char hit[FULL];
    memset(hit, 0, sizeof hit); hit[0] = 1;
    for (int i = 0; i < n; i++) hit[s[i]] = 1;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) hit[s[i] ^ s[j]] = 1;
    int c = 0; for (int i = 0; i < FULL; i++) c += hit[i];
    return c;
}

/* Independent oracle for the small cases: enumerate every candidate block of
 * size <= kmax directly, rebuild the whole column set, and test the covering
 * property with covered_count().  This shares no code with the constraint
 * encoding or the DFS, so a mismatch is a real bug in one of them. */
static int brute(const int *keep, int nkeep, const int *basis, int trep_tgt, int kmax)
{
    int cand[256], s[256];
    for (int i = 0; i < VSZ; i++) {
        int v = 0;
        for (int b = 0; b < VDIM; b++) if ((i >> b) & 1) v ^= basis[b];
        cand[i] = v ^ trep_tgt;
    }
    memcpy(s, keep, nkeep * sizeof(int));
    if (kmax >= 0 && covered_count(s, nkeep) == FULL) return 1;
    for (int a = 0; a < VSZ && kmax >= 1; a++) {
        s[nkeep] = cand[a];
        if (covered_count(s, nkeep + 1) == FULL) return 1;
        for (int b = a + 1; b < VSZ && kmax >= 2; b++) {
            s[nkeep + 1] = cand[b];
            if (covered_count(s, nkeep + 2) == FULL) return 1;
        }
    }
    return 0;
}

int main(int argc, char **argv)
{
    const char *in = NULL, *out = "q9_hit.cols";
    int shrink = 1, maxblock = 20, shard = 0, nshard = 1, selftest = 0, keepgoing = 0;
    long agree = 0, mismatch = 0, nofit = 0;
    int onlyf = -1, onlyg = -1, onlyt = -1;
    node_cap = 4000000;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--input")) in = argv[++i];
        else if (!strcmp(argv[i], "--shrink")) shrink = 1;
        else if (!strcmp(argv[i], "--resolve")) shrink = 0;
        else if (!strcmp(argv[i], "--maxblock")) maxblock = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--nodes")) node_cap = atol(argv[++i]);
        else if (!strcmp(argv[i], "--out")) out = argv[++i];
        else if (!strcmp(argv[i], "--shard")) sscanf(argv[++i], "%d/%d", &shard, &nshard);
        else if (!strcmp(argv[i], "--selftest")) selftest = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--all")) keepgoing = 1;
        else if (!strcmp(argv[i], "--only")) sscanf(argv[++i], "%d,%d,%d", &onlyf, &onlyg, &onlyt);
    }
    if (!in) { fprintf(stderr, "need --input\n"); return 2; }
    load(in);
    fprintf(stderr, "loaded n=%d covered=%d/%d\n", ncols, covered_count(cols, ncols), FULL);

    long qtot = 0, inst = 0, skipped = 0, capped = 0;
    for (int f = 1; f < FULL; f++) {
        for (int g = f + 1; g < FULL; g++) {
            int h = f ^ g;
            if (h < g) continue;                 /* canonical f < g < f^g */
            qtot++;
            if ((qtot - 1) % nshard != shard) continue;
            if (onlyf >= 0 && (f != onlyf || g != onlyg)) continue;

            /* coset representatives with t01 + t10 = t11 */
            int t01 = -1, t10 = -1;
            for (int x = 1; x < FULL && (t01 < 0 || t10 < 0); x++) {
                int a = parity(f & x), b = parity(g & x);
                if (!a && b && t01 < 0) t01 = x;
                if (a && !b && t10 < 0) t10 = x;
            }
            int t11 = t01 ^ t10;
            int trep[4] = {0, t01, t10, t11};

            int blk[4][64], nblk[4] = {0, 0, 0, 0};
            for (int i = 0; i < ncols; i++) {
                int lab = parity(f & cols[i]) * 2 + parity(g & cols[i]);
                int idx = lab == 0 ? 0 : lab == 1 ? 1 : lab == 2 ? 2 : 3;
                /* lab bits: (f,g); label 0=kernel, 1=(0,1), 2=(1,0), 3=(1,1) */
                blk[idx][nblk[idx]++] = cols[i] ^ trep[idx];
            }
            /* map V onto F_2^8 coordinates */
            int basis[VDIM], nb2 = 0;
            for (int x = 1; x < FULL && nb2 < VDIM; x++) {
                if (parity(f & x) || parity(g & x)) continue;
                int y = x;
                for (int b = 0; b < nb2; b++) { int t = y ^ basis[b]; if (t < y) y = t; }
                if (y) { basis[nb2++] = y;
                    for (int b = nb2 - 1; b > 0 && basis[b] > basis[b-1]; b--)
                        { int t = basis[b]; basis[b] = basis[b-1]; basis[b-1] = t; } }
            }
            static int coord[FULL];
            for (int x = 0; x < FULL; x++) coord[x] = -1;
            for (int m = 0; m < VSZ; m++) { int v = 0;
                for (int b = 0; b < VDIM; b++) if ((m >> b) & 1) v ^= basis[b];
                coord[v] = m; }

            for (int tgt = 1; tgt <= 3; tgt++) {
                if (onlyt > 0 && tgt != onlyt) continue;
                int m = nblk[tgt];
                int k = shrink ? m - 1 : m;
                if (k < 1) { skipped++; continue; }
                if (m > maxblock) { skipped++; continue; }
                int o1 = tgt == 1 ? 2 : 1, o2 = tgt == 3 ? 2 : 3;
                nAp = 0; Ap[nAp++] = 0;
                for (int i = 0; i < nblk[0]; i++) Ap[nAp++] = coord[blk[0][i]];
                nB = 0; for (int i = 0; i < nblk[o1]; i++) Bv[nB++] = coord[blk[o1][i]];
                nC = 0; for (int i = 0; i < nblk[o2]; i++) Cv[nC++] = coord[blk[o2][i]];

                static unsigned char P1[VSZ], P2[VSZ], P3[VSZ], P0[VSZ];
                memset(P1,0,VSZ); memset(P2,0,VSZ); memset(P3,0,VSZ); memset(P0,0,VSZ);
                for (int i = 0; i < nAp; i++) {
                    for (int j = 0; j < nB; j++) P1[Ap[i] ^ Bv[j]] = 1;
                    for (int j = 0; j < nC; j++) P2[Ap[i] ^ Cv[j]] = 1;
                }
                for (int i = 0; i < nB; i++) for (int j = 0; j < nC; j++) P3[Bv[i] ^ Cv[j]] = 1;
                P0[0] = 1;
                for (int i = 1; i < nAp; i++) P0[Ap[i]] = 1;
                for (int i = 1; i < nAp; i++) for (int j = i+1; j < nAp; j++) P0[Ap[i]^Ap[j]] = 1;
                for (int i = 0; i < nB; i++) for (int j = i+1; j < nB; j++) P0[Bv[i]^Bv[j]] = 1;
                for (int i = 0; i < nC; i++) for (int j = i+1; j < nC; j++) P0[Cv[i]^Cv[j]] = 1;

                nU1 = nU2 = nU3 = nU0 = 0;
                memset(in1,0,sizeof in1); memset(in2,0,sizeof in2);
                memset(in3,0,sizeof in3); memset(in0,0,sizeof in0);
                memset(c1,0,sizeof c1); memset(c2,0,sizeof c2);
                memset(c3,0,sizeof c3); memset(c0,0,sizeof c0);
                for (int u = 0; u < VSZ; u++) {
                    if (!P1[u]) { U1[nU1++] = u; in1[u] = 1; }
                    if (!P2[u]) { U2[nU2++] = u; in2[u] = 1; }
                    if (!P3[u]) { U3[nU3++] = u; in3[u] = 1; }
                    if (!P0[u]) { U0[nU0++] = u; in0[u] = 1; }
                }
                rem1 = nU1; rem2 = nU2; rem3 = nU3; rem0 = nU0;
                memset(excl, 0, sizeof excl);
                nD = 0; Kbudget = k; nodes = 0; nDout = 0;
                inst++;
                int r = dfs();
                if (selftest && k <= selftest && r >= 0) {
                    int keep[256], nk = 0;
                    for (int i = 0; i < ncols; i++) {
                        int lab = parity(f & cols[i]) * 2 + parity(g & cols[i]);
                        int idx = lab == 0 ? 0 : lab == 1 ? 1 : lab == 2 ? 2 : 3;
                        if (idx != tgt) keep[nk++] = cols[i];
                    }
                    int b2 = brute(keep, nk, basis, trep[tgt], k);
                    if (b2 != (r == 1)) {
                        printf("MISMATCH f=%d g=%d block=%d k=%d dfs=%d brute=%d\n",
                               f, g, tgt, k, r, b2);
                        mismatch++;
                    } else agree++;
                }
                if (r < 0) { capped++; continue; }
                if (r == 1) {
                    int news[256], nn = 0;
                    for (int i = 0; i < ncols; i++) {
                        int lab = parity(f & cols[i]) * 2 + parity(g & cols[i]);
                        int idx = lab == 0 ? 0 : lab == 1 ? 1 : lab == 2 ? 2 : 3;
                        if (idx != tgt) news[nn++] = cols[i];
                    }
                    for (int i = 0; i < nDout; i++) {
                        int v = 0;
                        for (int b = 0; b < VDIM; b++) if ((Dout[i] >> b) & 1) v ^= basis[b];
                        news[nn++] = v ^ trep[tgt];
                    }
                    int cov = covered_count(news, nn);
                    printf("HIT quotient f=%d g=%d block=%d old=%d new=%d n=%d covered=%d/%d\n",
                           f, g, tgt, m, nDout, nn, cov, FULL);
                    FILE *o = fopen(out, "w");
                    fprintf(o, "# q9 block replacement: f=%d g=%d block=%d %d->%d n=%d covered=%d\n",
                            f, g, tgt, m, nDout, nn, cov);
                    for (int i = 0; i < nn; i++) fprintf(o, "%d%c", news[i], i+1==nn?'\n':' ');
                    fclose(o);
                    fflush(stdout);
                    if (cov == FULL) { if (!keepgoing) return 0; nofit++; }
                }
            }
        }
        if ((f & 63) == 0)
            fprintf(stderr, "f=%d instances=%d skipped=%ld capped=%ld\n",
                    f, (int)inst, skipped, capped);
    }
    printf("DONE shard %d/%d quotients=%ld instances=%ld skipped=%ld capped=%ld"
           " selftest_agree=%ld selftest_mismatch=%ld hits=%ld\n",
           shard, nshard, qtot, inst, skipped, capped, agree, mismatch, nofit);
    return 1;
}
