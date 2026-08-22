/* cover.c — decide ST26 Lemma-4.3-style saving as a covering problem.

   Question T1(k,p):  for every v in N_k = { v in Z_{k+1}^k : v != 0, some v_i = 0 }
   are there s in Z_{k+1} and j in Z with   s v + r_k(j/p)  in {1,...,k-1}^k  (mod k+1) ?

   Write B^{(j)}_i = floor( (k+1) * ((i*j) mod p) / p ),  the i-th entry of r_k(j/p).
   Call (s,j) a CONSTRAINT and say coordinate i taking value a HITS it when
        s*a + B^{(j)}_i  ==  0  or  k  (mod k+1).
   Then v fails to be saved  <=>  the sets hit(i, v_i) together cover every constraint.
   So T1(k,p) holds  <=>  no v in N_k covers all constraints.  That is a set-cover
   feasibility question in k variables of k+1 values -- no vector enumeration.

   Two exact reductions, both applied:
     * s = 0 constraints do not mention a, and each is hit by every v (some
       coordinate of r_k(j/p) is always 0 or k, because (1,...,k) is tight).
       They are auto-satisfied and dropped.  Asserted, not assumed.
     * (s,j) and (-s, p-j) induce the same hitting set; duplicates are merged.

   p == k+1 selects the p-independent statement (ST26 Proposition 4.1), where
   r_k(r/(k+1)) = r*(1,...,k).  Those are the self-test cases.

   gcc -O3 -march=native -std=c11 -o cover cover.c
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK   16
#define MAXCON 8192
#define NW     ((MAXCON + 63) / 64)

static int K, M, P, NCON, NWORD;
static uint64_t hitmask[MAXK][MAXK + 1][NW];   /* constraints hit by v_i = a   */
static int      hcnt[MAXK][MAXK + 1];          /* popcount of the above        */
static uint8_t  optcnt[MAXCON][MAXK];          /* #values of coord i hitting c */
static uint64_t FULL[NW];

static int val[MAXK];                          /* -1 = unassigned              */
static int optsum[MAXCON];                     /* live (i,a) options per c     */
static int split_n = 1, split_i = 0, split_depth = 0;
static long long task_ctr;
static long long progress_every = 1LL << 24;
static int use_bound = 1;
static long long nodes, bound_cuts, dead_cuts;
static long long node_cap;
static int solution[MAXK], have_sol;

static inline void bset(uint64_t *b, int i) { b[i >> 6] |= 1ull << (i & 63); }
static inline int  btst(const uint64_t *b, int i) { return (b[i >> 6] >> (i & 63)) & 1ull; }

/* ---------------------------------------------------------------- build ---- */

static int Braw[MAXCON][MAXK];   /* B^{(j)} for j = 0..P-1 (or r=0..M-1)        */

static int build(void)
{
  int nj = (P == M) ? M : P;
  for (int j = 0; j < nj; j++)
    for (int i = 1; i <= K; i++)
      Braw[j][i - 1] = (P == M) ? (j * i) % M
                                : (int)((long long)M * ((long long)i * j % P) / P);

  /* assert the s=0 drop is sound: every j has a coordinate equal to 0 or K */
  for (int j = 0; j < nj; j++) {
    int ok = 0;
    for (int i = 0; i < K; i++)
      if (Braw[j][i] == 0 || Braw[j][i] == M - 1) ok = 1;
    if (!ok) {
      /* (1,...,K) would have a witness time j/p -- impossible, it is tight */
      fprintf(stderr, "FATAL: s=0 constraint j=%d is unhittable; (1..K) has witness j/p\n", j);
      exit(2);
    }
  }

  /* enumerate (s,j) with s != 0, dedupe by hitting set */
  static uint64_t tmp[MAXCON][NW];
  static uint8_t  tmpcnt[MAXCON][MAXK];
  NCON = 0;
  for (int s = 1; s < M; s++)
    for (int j = 0; j < nj; j++) {
      uint64_t hs[NW];
      uint8_t  cn[MAXK];
      memset(hs, 0, sizeof(hs));
      memset(cn, 0, sizeof(cn));
      int idx = 0, tot = 0;
      for (int i = 0; i < K; i++)
        for (int a = 0; a < M; a++) {
          int x = (s * a + Braw[j][i]) % M;
          if (x == 0 || x == M - 1) { bset(hs, i * M + a); cn[i]++; tot++; }
        }
      (void)idx;
      if (tot == 0) {                      /* unhittable -> nothing is unsaved */
        printf("RESULT UNSAT (constraint s=%d j=%d is unhittable)\n", s, j);
        exit(0);
      }
      if (tot == K * M) continue;          /* auto-satisfied, drop             */
      int dup = 0;
      for (int c = 0; c < NCON && !dup; c++)
        if (!memcmp(tmp[c], hs, ((K * M + 63) / 64) * 8)) dup = 1;
      if (dup) continue;
      memcpy(tmp[NCON], hs, sizeof(hs));
      memcpy(tmpcnt[NCON], cn, sizeof(cn));
      NCON++;
    }

  NWORD = (NCON + 63) / 64;
  memset(hitmask, 0, sizeof(hitmask));
  for (int c = 0; c < NCON; c++) {
    for (int i = 0; i < K; i++) optcnt[c][i] = tmpcnt[c][i];
    for (int i = 0; i < K; i++)
      for (int a = 0; a < M; a++)
        if (btst(tmp[c], i * M + a)) bset(hitmask[i][a], c);
  }
  for (int i = 0; i < K; i++)
    for (int a = 0; a < M; a++) {
      int t = 0;
      for (int w = 0; w < NWORD; w++) t += __builtin_popcountll(hitmask[i][a][w]);
      hcnt[i][a] = t;
    }
  memset(FULL, 0, sizeof(FULL));
  for (int c = 0; c < NCON; c++) bset(FULL, c);
  return NCON;
}

/* ------------------------------------------------------------- feasible ---- */
/* ST26 Definition 2.1 (with footnote 1: gcd taken against l, here l = m = k+1).
   u is (k,p,m)-proper by the GCD BRANCH when some i has
        gcd(m, u_1, ..., u_i^, ..., u_k) > 1,
   i.e. some prime q | m divides every u_j with j != i.  Writing v = u mod m,
   that is:  exists prime q | m with  #{ j : q does not divide v_j } <= 1.
   Such v never needs a Lemma 4.3 witness, so it is EXCLUDED from the search.

   When m is prime this collapses to "at most one nonzero coordinate", which is
   ST26's own u' = 0 case (plus one slack coordinate).  When m = 14 it is a
   genuinely wider branch, and that is the term this folder had been dropping.

   Prop 4.4 also disposes of any v with no zero coordinate via s=1, r=0, so the
   search space is  { v : some v_i = 0 } minus the gcd-proper tuples.

   Given a covering PARTIAL assignment, we may still choose the free
   coordinates.  A coordinate of value 1 is coprime to every q, so the cheapest
   completion needs   needZero + max_q need_q   free coordinates.               */

static int mprimes[MAXK], nmprimes;

static void factor_m(void)
{
  nmprimes = 0;
  int x = M;
  for (int q = 2; (long long)q * q <= x; q++)
    if (x % q == 0) { mprimes[nmprimes++] = q; while (x % q == 0) x /= q; }
  if (x > 1) mprimes[nmprimes++] = x;
}

static int feasible_Nk(void)
{
  int free_ = 0, haszero = 0;
  int coprime_cnt[MAXK];
  for (int t = 0; t < nmprimes; t++) coprime_cnt[t] = 0;
  for (int i = 0; i < K; i++) {
    if (val[i] < 0) { free_++; continue; }
    if (val[i] == 0) haszero = 1;
    for (int t = 0; t < nmprimes; t++)
      if (val[i] % mprimes[t] != 0) coprime_cnt[t]++;
  }
  int need = haszero ? 0 : 1;
  int worst = 0;
  for (int t = 0; t < nmprimes; t++) {
    int d = 2 - coprime_cnt[t];
    if (d > worst) worst = d;
  }
  need += worst;
  return free_ >= need;
}

/* ------------------------------------------------------------------ DFS ---- */

static int rec(uint64_t *cov, int depth)
{
  if (++nodes > node_cap) return -1;
  if ((nodes & (progress_every - 1)) == 0)
    fprintf(stderr, "  [part %d/%d] nodes=%lld bound_cuts=%lld\n",
            split_i, split_n, nodes, bound_cuts), fflush(stderr);

  uint64_t unc[NW];
  int rem = 0;
  for (int w = 0; w < NWORD; w++) { unc[w] = FULL[w] & ~cov[w]; rem += __builtin_popcountll(unc[w]); }

  if (rem == 0) {
    if (feasible_Nk()) { memcpy(solution, val, sizeof(solution)); have_sol = 1; return 1; }
    return 0;
  }

  /* MRV over uncovered constraints, using the incrementally kept optsum */
  int bestc = -1, bestn = 1 << 30;
  for (int w = 0; w < NWORD && bestn > 1; w++) {
    uint64_t x = unc[w];
    while (x) {
      int c = (w << 6) + __builtin_ctzll(x);
      x &= x - 1;
      if (optsum[c] < bestn) { bestn = optsum[c]; bestc = c; if (bestn <= 1) break; }
    }
  }
  if (bestn == 0) { dead_cuts++; return 0; }

  /* counting bound: the free coordinates cannot cover what is left */
  int cap = 0;
  if (use_bound)
  for (int i = 0; i < K && cap < rem; i++) {
    if (val[i] >= 0) continue;
    int mx = 0;
    for (int a = 0; a < M; a++) {
      int t = 0;
      for (int w = 0; w < NWORD; w++) t += __builtin_popcountll(hitmask[i][a][w] & unc[w]);
      if (t > mx) mx = t;
    }
    cap += mx;
  }
  if (use_bound && cap < rem) { bound_cuts++; return 0; }

  /* work split: partition the subtrees rooted at split_depth across parts */
  if (depth == split_depth && split_n > 1)
    if ((task_ctr++ % split_n) != split_i) return 0;

  for (int i = 0; i < K; i++) {
    if (val[i] >= 0) continue;
    for (int a = 0; a < M; a++) {
      if (!btst(hitmask[i][a], bestc)) continue;
      uint64_t ncov[NW];
      for (int w = 0; w < NWORD; w++) ncov[w] = cov[w] | hitmask[i][a][w];
      val[i] = a;
      for (int c = 0; c < NCON; c++) optsum[c] -= optcnt[c][i];
      int r = rec(ncov, depth + 1);
      for (int c = 0; c < NCON; c++) optsum[c] += optcnt[c][i];
      val[i] = -1;
      if (r != 0) return r;
    }
  }
  return 0;
}

int main(int argc, char **argv)
{
  K = 13; P = 0; node_cap = 200000000000LL;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k")) K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p")) P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--nodecap")) node_cap = atoll(argv[++i]);
    else if (!strcmp(argv[i], "--nobound")) use_bound = 0;
    else if (!strcmp(argv[i], "--split")) split_n = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--part")) split_i = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--splitdepth")) split_depth = atoi(argv[++i]);
  }
  M = K + 1;
  if (!P) P = M;
  factor_m();
  build();

  printf("k=%d m=%d p=%d constraints=%d (after dropping s=0 and merging (s,j)~(-s,p-j))\n",
         K, M, P, NCON);
  printf("m factors:");
  for (int t = 0; t < nmprimes; t++) printf(" %d", mprimes[t]);
  printf("   search space = { some v_i = 0 } minus gcd-proper (ST26 Def 2.1)\n");
  fflush(stdout);

  for (int i = 0; i < K; i++) val[i] = -1;
  for (int c = 0; c < NCON; c++) {
    optsum[c] = 0;
    for (int i = 0; i < K; i++) optsum[c] += optcnt[c][i];
  }
  uint64_t cov[NW]; memset(cov, 0, sizeof(cov));
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  int r = rec(cov, 0);
  clock_gettime(CLOCK_MONOTONIC, &t1);
  double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);

  if (r == 1) {
    printf("RESULT SAT  (an unsaved v exists; T2(%d,%d) FAILS)\n", K, P);
    printf("witness v =");
    for (int i = 0; i < K; i++) { if (solution[i] < 0) printf(" *"); else printf(" %d", solution[i]); }
    printf("   (* = free, any value in Z_%d)\n", M);
  } else if (r == -1) {
    printf("RESULT UNKNOWN (node cap %lld reached)\n", node_cap);
  } else {
    printf("RESULT UNSAT (every non-gcd-proper v with a zero coord is saved; T2(%d,%d) HOLDS)\n", K, P);
  }
  printf("nodes=%lld bound_cuts=%lld dead_cuts=%lld seconds=%.2f\n",
         nodes, bound_cuts, dead_cuts, el);
  return r == -1 ? 3 : 0;
}
