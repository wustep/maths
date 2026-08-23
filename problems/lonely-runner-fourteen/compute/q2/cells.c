/* cells.c — decide T2(k,p) for ALL p at once, by replacing the grid (1/p)Z
   with the exact cell decomposition of the circle.

   Background.  q1/cover.c decides, for one prime p, whether some eligible
   v in Z_m^k (m = k+1) is UNSAVED, i.e. whether

        for every s in Z_m and every j in Z_p, some i has
              || i*j/p  +  s*v_i/m ||  <  1/m .                        (H)

   The inner predicate depends on j only through the real number t = j/p, and
   as a function of t it is piecewise constant: || i*t + s*v_i/m || < 1/m flips
   exactly at   t = (m*n +- 1 - s*v_i) / (m*i),  n in Z,  so all breakpoints
   lie in  (1/(m*i))Z  for some i <= k.  Let

        D = m * lcm(1,...,k),      S = union_i (1/(m*i))Z  intersect [0,1),

   a set of at most sum_i m*i points; the open intervals between consecutive
   points of S are the CELLS, and (H) is constant on each cell.

   Two facts make this a decision procedure for every p at once.

   Take the cells HALF-OPEN, C_r = [c_r, c_{r+1}), and read B_i off the left
   endpoint: B_i(t) = floor(m*frac(i*t)) is right-continuous and jumps only on
   (1/(m*i))Z, so B is genuinely constant on each half-open cell and every real
   t lies in exactly one.  No boundary cases anywhere.

   (1) WINDOW CONDITION.  Every half-open interval of length 1/p contains a
       point of (1/p)Z.  So for any x, the grid point of (1/p)Z inside
       [x, x + 1/p) lies in one of the cells meeting that interval; if v is
       unsaved at p it must hit (s, C) for at least ONE such cell C.  Writing
       W_r(q) for the cells meeting [c_r, c_r + 1/q), and using p >= q so that
       [x, x+1/p) is contained in [x, x+1/q),

            hit(s, W_r) := union over C in W_r of hit(s, C)

       is a constraint every v unsaved at any p >= q must satisfy.  Hence

           [ no eligible v covers every (s, W_r(q)) ]
              =>  T2(k,p) holds for every integer p >= q.

       W_r shrinks as q grows, so the constraints only get stronger with q and
       the property is monotone: one run at q certifies every p >= q at once.

   (2) When 1/q is below the length of cell r, W_r = {C_r} and the constraint
       is just "the cell is hit", which is the special case
       |C_r| >= 1/p => C_r meets the grid.  --q 0 forces every W_r = {C_r};
       that is the weakest useful setting and it certifies every
       p >= D/mingap.  Nothing is added by hand: c_0 = 0 is a cell left
       endpoint, so j = 0 is already covered.

   --strictcell drops the window union and keeps only cells of length > 1/q,
   which is the weaker first version of this reduction.

   --p P instead reproduces q1/cover.c's own constraint set (grid j/P), so the
   two programs can be compared directly on the same question.

   The DFS, the MRV rule, the counting bound and the ST26 Definition 2.1 gcd
   branch are the ones from q1/cover.c, unchanged; only the constraints differ.

   gcc -O3 -std=c11 -o cells cells.c
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK   16
#define MAXCON 32768
#define NW     ((MAXCON + 63) / 64)
#define SIGW   8                        /* >= (MAXK*(MAXK+1)+63)/64 */

static int K, M, P, Q, NCON, NWORD, Qeff;
static uint64_t hitmask[MAXK][MAXK + 1][NW];
static int      hcnt[MAXK][MAXK + 1];
static uint8_t  optcnt[MAXCON][MAXK];
static uint64_t FULL[NW];

static int val[MAXK];
static int optsum[MAXCON];
static int split_n = 1, split_i = 0, split_depth = 0;
static long long task_ctr;
static long long progress_every = 1LL << 24;
static int use_bound = 1, verbose_cells = 0, strictcell = 0;
static long long nodes, bound_cuts, dead_cuts;
static long long node_cap;
static int solution[MAXK], have_sol;

static inline void bset(uint64_t *b, int i) { b[i >> 6] |= 1ull << (i & 63); }
static inline int  btst(const uint64_t *b, int i) { return (b[i >> 6] >> (i & 63)) & 1ull; }

/* ------------------------------------------------------------ cell grid ---- */

static long long DEN;                   /* D = M * lcm(1..K)                   */
static long long cut[4096];             /* breakpoints, numerators over DEN    */
static int ncut;
static int Braw[MAXCON][MAXK];          /* B vector per retained time point    */
static long long cellnum[MAXCON], cellden[MAXCON];  /* cell length, for report */
static int winlo[MAXCON], winhi[MAXCON];            /* window = cells [lo,hi]  */
static int nB;

static int cmpll(const void *a, const void *b)
{
  long long x = *(const long long *)a, y = *(const long long *)b;
  return (x > y) - (x < y);
}

/* B_i at the exact rational time  num/den  (0 <= num < den) */
static void Bat(long long num, long long den, int *B)
{
  for (int i = 1; i <= K; i++) {
    long long r = ((long long)i * num) % den;
    B[i - 1] = (int)(M * r / den);
  }
}

static void build_times(void)
{
  if (P) {                              /* q1/cover.c's own constraint set */
    nB = 0;
    for (int j = 0; j < P; j++) {
      Bat(j, P, Braw[nB]); cellnum[nB] = 1; cellden[nB] = P;
      winlo[nB] = nB; winhi[nB] = nB; nB++;
    }
    printf("times: grid j/%d, %d points\n", P, nB);
    return;
  }
  long long L = 1;
  for (int i = 1; i <= K; i++) {        /* L = lcm(1..K) */
    long long a = L, b = i;
    while (b) { long long t = a % b; a = b; b = t; }
    L = L / a * i;
  }
  DEN = (long long)M * L;
  ncut = 0;
  for (int i = 1; i <= K; i++) {
    long long step = L / i;             /* DEN/(M*i) */
    for (long long x = 0; x < DEN; x += step) cut[ncut++] = x;
  }
  qsort(cut, ncut, sizeof(long long), cmpll);
  int w = 0;
  for (int r = 0; r < ncut; r++) if (r == 0 || cut[r] != cut[r - 1]) cut[w++] = cut[r];
  ncut = w;

  long long mingap = DEN;
  for (int r = 0; r < ncut; r++) {
    long long gap = ((r + 1 < ncut) ? cut[r + 1] : DEN) - cut[r];
    if (gap < mingap) mingap = gap;
  }
  /* p >= DEN/mingap makes every single cell meet the grid on its own */
  int qcell = (int)((DEN + mingap - 1) / mingap);

  if (strictcell) {                     /* first version: long cells only */
    nB = 0;
    for (int r = 0; r < ncut; r++) {
      long long lo = cut[r], hi = (r + 1 < ncut) ? cut[r + 1] : DEN;
      if (Q && (long long)Q * (hi - lo) <= DEN) continue;
      Bat(lo, DEN, Braw[nB]); cellnum[nB] = hi - lo; cellden[nB] = DEN;
      winlo[nB] = r; winhi[nB] = r; nB++;
    }
    Qeff = Q ? Q : qcell;
    printf("cells: D=%lld breakpoints=%d min cell=%lld/%lld (=1/%.1f)\n",
           DEN, ncut, mingap, DEN, (double)DEN / mingap);
    printf("--strictcell: kept %d cells of length > 1/%d\n", nB, Qeff);
    return;
  }

  /* window mode: all cells, constraint r spans the cells meeting
     [ c_r, c_r + 1/Q ).  Q = 0 means singleton windows.                     */
  nB = ncut;
  long long span = 0;
  for (int r = 0; r < ncut; r++) {
    Bat(cut[r], DEN, Braw[r]);
    long long gap = ((r + 1 < ncut) ? cut[r + 1] : DEN) - cut[r];
    cellnum[r] = gap; cellden[r] = DEN;
    winlo[r] = r; winhi[r] = r;
    if (Q)
      while ((long long)Q * (cut[(winhi[r] + 1) % ncut]
                             + ((winhi[r] + 1 >= ncut) ? DEN : 0) - cut[r]) < DEN) {
        winhi[r]++;
        if (winhi[r] - winlo[r] >= ncut) { fprintf(stderr, "FATAL: q too small\n"); exit(2); }
      }
    if (winhi[r] - winlo[r] + 1 > span) span = winhi[r] - winlo[r] + 1;
  }
  Qeff = Q ? Q : qcell;
  printf("cells: D=%lld breakpoints=%d min cell=%lld/%lld (=1/%.1f)\n",
         DEN, ncut, mingap, DEN, (double)DEN / mingap);
  printf("windows: q=%d, %d cells, widest window spans %lld cells%s\n",
         Qeff, ncut, span, Q ? "" : " (singleton, cell-length rule)");
  if (verbose_cells)
    for (int r = 0; r < ncut; r++)
      printf("  cell %3d lo=%lld/%lld len=%lld/%lld window=[%d,%d]\n",
             r, cut[r], DEN, cellnum[r], cellden[r], winlo[r], winhi[r]);
}

/* ---------------------------------------------------------------- build ---- */

static uint64_t sig[MAXCON][SIGW];
#define HB 18
static int htab[1 << HB];

static int build(void)
{
  build_times();

  for (int j = 0; j < nB; j++) {        /* the s=0 drop must be sound */
    int ok = 0;
    for (int i = 0; i < K; i++)
      if (Braw[j][i] == 0 || Braw[j][i] == M - 1) ok = 1;
    if (!ok) {
      fprintf(stderr, "FATAL: s=0 constraint at time index %d is unhittable\n", j);
      exit(2);
    }
  }

  int sw = (K * M + 63) / 64;
  memset(htab, -1, sizeof(htab));
  static uint8_t tmpcnt[MAXCON][MAXK];
  NCON = 0;
  for (int s = 1; s < M; s++)
    for (int j = 0; j < nB; j++) {
      uint64_t hs[SIGW]; uint8_t cn[MAXK];
      memset(hs, 0, sizeof(hs)); memset(cn, 0, sizeof(cn));
      int tot = 0;
      for (int i = 0; i < K; i++)
        for (int a = 0; a < M; a++) {
          int any = 0;
          for (int r = winlo[j]; r <= winhi[j] && !any; r++) {
            int x = (s * a + Braw[r % nB][i]) % M;
            if (x == 0 || x == M - 1) any = 1;
          }
          if (any) { bset(hs, i * M + a); cn[i]++; tot++; }
        }
      if (tot == 0) {
        printf("RESULT UNSAT (constraint s=%d time#%d is unhittable)\n", s, j);
        exit(0);
      }
      if (tot == K * M) continue;
      uint64_t h = 1469598103934665603ull;
      for (int w = 0; w < sw; w++) { h ^= hs[w]; h *= 1099511628211ull; }
      int slot = (int)(h >> (64 - HB)), dup = 0;
      while (htab[slot] >= 0) {
        if (!memcmp(sig[htab[slot]], hs, sw * 8)) { dup = 1; break; }
        slot = (slot + 1) & ((1 << HB) - 1);
      }
      if (dup) continue;
      if (NCON >= MAXCON) { fprintf(stderr, "FATAL: too many constraints\n"); exit(2); }
      memcpy(sig[NCON], hs, sw * 8);
      memcpy(tmpcnt[NCON], cn, sizeof(cn));
      htab[slot] = NCON;
      NCON++;
    }

  NWORD = (NCON + 63) / 64;
  memset(hitmask, 0, sizeof(hitmask));
  for (int c = 0; c < NCON; c++) {
    for (int i = 0; i < K; i++) optcnt[c][i] = tmpcnt[c][i];
    for (int i = 0; i < K; i++)
      for (int a = 0; a < M; a++)
        if (btst(sig[c], i * M + a)) bset(hitmask[i][a], c);
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
/* ST26 Definition 2.1 gcd branch: v never needs a witness when some prime
   q | m divides all but at most one coordinate.  Excluded from the search.   */

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
  int need = haszero ? 0 : 1, worst = 0;
  for (int t = 0; t < nmprimes; t++) {
    int d = 2 - coprime_cnt[t];
    if (d > worst) worst = d;
  }
  return free_ >= need + worst;
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
  K = 13; P = 0; Q = 0; node_cap = 200000000000LL;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k")) K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p")) P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--q")) Q = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--nodecap")) node_cap = atoll(argv[++i]);
    else if (!strcmp(argv[i], "--nobound")) use_bound = 0;
    else if (!strcmp(argv[i], "--cells")) verbose_cells = 1;
    else if (!strcmp(argv[i], "--strictcell")) strictcell = 1;
    else if (!strcmp(argv[i], "--split")) split_n = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--part")) split_i = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--splitdepth")) split_depth = atoi(argv[++i]);
  }
  M = K + 1;
  factor_m();
  build();

  printf("k=%d m=%d %s constraints=%d (s=0 dropped, duplicate hitting sets merged)\n",
         K, M, P ? "grid" : "cells", NCON);
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
    printf("RESULT SAT  (an eligible v covers every kept constraint)\n");
    printf("witness v =");
    for (int i = 0; i < K; i++) { if (solution[i] < 0) printf(" *"); else printf(" %d", solution[i]); }
    printf("   (* = free)\n");
  } else if (r == -1) {
    printf("RESULT UNKNOWN (node cap %lld reached)\n", node_cap);
  } else if (P) {
    printf("RESULT UNSAT (T2(%d,%d) HOLDS)\n", K, P);
  } else {
    printf("RESULT UNSAT (T2(%d,p) HOLDS for every integer p >= %d)\n", K, Qeff);
  }
  printf("nodes=%lld bound_cuts=%lld dead_cuts=%lld seconds=%.2f\n",
         nodes, bound_cuts, dead_cuts, el);
  return r == -1 ? 3 : 0;
}
