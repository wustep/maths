/* cover_bdd.c — second, independent decision procedure for the same question.

   cover.c backtracks over CONSTRAINTS with an MRV heuristic and a counting
   bound.  This one instead sweeps COORDINATES i = 1..k forward, carrying the
   set of pairs (s,j) that still save the prefix, and deduplicates states.  No
   heuristic, no bound, no constraint reductions: it keeps the full (k+1)*p pair
   set, so it does not inherit cover.c's "drop s=0" or "merge (s,j)~(-s,p-j)"
   steps either.  Agreement between the two is meaningful.

       A_0 = all pairs
       A_d = A_{d-1} INTERSECT { (s,j) : s*v_d + B^{(j)}_d  not in {0, k} }

   v is saved iff A_k is non-empty.  So an obstruction is a path reaching the
   empty set whose flags can still be completed to "some coordinate zero, not
   gcd-proper".  Once A is empty it stays empty, so we may stop early.

   Flags carried alongside A: whether a zero coordinate has been used, and how
   many coordinates so far are coprime to each prime factor of k+1 (capped at 2).

   gcc -O3 -march=native -std=c11 -o cover_bdd cover_bdd.c
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK 16
#define MAXP 1024
static int K, M, P, NPAIR, NW;

static uint64_t keepmask[MAXK][MAXK + 1][(MAXK + 1) * MAXP / 64 + 2];
static int mpr[4], nmpr;

/* ---- state: bitset A + flags packed as (haszero, c0, c1) ---- */
#define FLAGS 18
static int flag_id(int hz, int c0, int c1) { return (hz * 3 + c0) * 3 + c1; }

typedef struct { uint64_t *bits; int flag; } State;

/* open-addressed hash set over (bits, flag) */
static State *tab; static int64_t tabn, tabmask, tabcnt;
static uint64_t *arena; static int64_t arena_used, arena_cap;

static uint64_t hashbits(const uint64_t *b, int flag)
{
  uint64_t h = 1469598103934665603ull ^ (uint64_t)flag;
  for (int w = 0; w < NW; w++) { h ^= b[w]; h *= 1099511628211ull; }
  return h;
}
static void tab_init(int64_t n)
{
  tabn = 1; while (tabn < n) tabn <<= 1; tabmask = tabn - 1; tabcnt = 0;
  tab = calloc(tabn, sizeof(State));
  if (!tab) { fprintf(stderr, "OOM tab\n"); exit(1); }
}
static int tab_insert(const uint64_t *b, int flag)   /* 1 if new */
{
  uint64_t h = hashbits(b, flag) & tabmask;
  while (tab[h].bits) {
    if (tab[h].flag == flag && !memcmp(tab[h].bits, b, NW * 8)) return 0;
    h = (h + 1) & tabmask;
  }
  if (arena_used + NW > arena_cap) { fprintf(stderr, "OOM arena\n"); exit(1); }
  uint64_t *slot = arena + arena_used; arena_used += NW;
  memcpy(slot, b, NW * 8);
  tab[h].bits = slot; tab[h].flag = flag; tabcnt++;
  return 1;
}

int main(int argc, char **argv)
{
  K = 13; P = 0;
  int64_t statecap = 40000000;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k")) K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p")) P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--statecap")) statecap = atoll(argv[++i]);
  }
  M = K + 1; if (!P) P = M;
  { int x = M; nmpr = 0;
    for (int q = 2; q * q <= x; q++) if (x % q == 0) { mpr[nmpr++] = q; while (x % q == 0) x /= q; }
    if (x > 1) mpr[nmpr++] = x; }

  int nj = (P == M) ? M : P;
  NPAIR = M * nj; NW = (NPAIR + 63) / 64;

  for (int i = 0; i < K; i++)
    for (int a = 0; a < M; a++) memset(keepmask[i][a], 0, NW * 8);
  for (int s = 0; s < M; s++)
    for (int j = 0; j < nj; j++) {
      int idx = s * nj + j;
      for (int i = 1; i <= K; i++) {
        int B = (P == M) ? (j * i) % M : (int)((long long)M * ((long long)i * j % P) / P);
        for (int a = 0; a < M; a++) {
          int x = (s * a + B) % M;
          if (x != 0 && x != M - 1) keepmask[i - 1][a][idx >> 6] |= 1ull << (idx & 63);
        }
      }
    }

  printf("k=%d m=%d p=%d pairs=%d (full set, no reductions) words=%d\n", K, M, P, NPAIR, NW);
  printf("m factors:"); for (int t = 0; t < nmpr; t++) printf(" %d", mpr[t]); printf("\n");
  fflush(stdout);

  arena_cap = statecap * NW; arena = malloc(arena_cap * 8);
  if (!arena) { fprintf(stderr, "OOM arena alloc\n"); exit(1); }

  /* frontier as plain arrays */
  uint64_t *cur = malloc((size_t)statecap * NW * 8);
  int      *curf = malloc((size_t)statecap * sizeof(int));
  int64_t ncur = 1;
  for (int w = 0; w < NW; w++) cur[w] = 0;
  for (int idx = 0; idx < NPAIR; idx++) cur[idx >> 6] |= 1ull << (idx & 63);
  curf[0] = flag_id(0, 0, 0);

  int sat = 0, sat_depth = -1;
  struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);

  for (int d = 0; d < K && !sat; d++) {
    tab_init(ncur * (int64_t)M * 2 + 1024);
    arena_used = 0;
    uint64_t *nxt = malloc((size_t)statecap * NW * 8);
    int *nxtf = malloc((size_t)statecap * sizeof(int));
    int64_t nn = 0;
    uint64_t tmp[(MAXK + 1) * MAXP / 64 + 2];

    for (int64_t st = 0; st < ncur; st++) {
      const uint64_t *A = cur + st * NW;
      int f = curf[st], hz = f / 9, c0 = (f / 3) % 3, c1 = f % 3;
      for (int a = 0; a < M; a++) {
        int empty = 1;
        for (int w = 0; w < NW; w++) { tmp[w] = A[w] & keepmask[d][a][w]; if (tmp[w]) empty = 0; }
        int nhz = hz || (a == 0);
        int nc0 = c0, nc1 = c1;
        if (a % mpr[0] && nc0 < 2) nc0++;
        if (nmpr > 1) { if (a % mpr[1] && nc1 < 2) nc1++; } else nc1 = 2;
        if (empty) {
          /* remaining K-1-d coordinates are free; cheapest completion needs
             (need a zero) + max over primes of (2 - coprime count) of them */
          int need = nhz ? 0 : 1;
          int w0 = 2 - nc0, w1 = 2 - nc1;
          int worst = w0 > w1 ? w0 : w1; if (worst < 0) worst = 0;
          if (K - 1 - d >= need + worst) { sat = 1; sat_depth = d + 1; break; }
          continue;      /* empty but not completable to a needed tuple */
        }
        int nf = flag_id(nhz, nc0, nc1);
        if (tab_insert(tmp, nf)) {
          if (nn >= statecap) { fprintf(stderr, "state cap %lld hit at depth %d\n", (long long)statecap, d); exit(3); }
          memcpy(nxt + nn * NW, tmp, NW * 8); nxtf[nn] = nf; nn++;
        }
      }
      if (sat) break;
    }
    free(tab); free(cur); free(curf);
    cur = nxt; curf = nxtf; ncur = nn;
    printf("  depth %2d: states=%lld\n", d + 1, (long long)ncur); fflush(stdout);
    if (sat) break;
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
  if (sat) printf("RESULT SAT  (obstruction exists; T2(%d,%d) FAILS) first empty at coordinate %d\n", K, P, sat_depth);
  else     printf("RESULT UNSAT (every non-gcd-proper v with a zero coord is saved; T2(%d,%d) HOLDS)\n", K, P);
  printf("seconds=%.2f\n", el);
  return 0;
}
