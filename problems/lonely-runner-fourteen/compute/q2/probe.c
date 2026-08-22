/* probe.c — cheap SAT-side probe: is there an unsaved v with every coordinate
   in a small alphabet A?

   Deciding T2(13,p) outright gets expensive exactly where it is interesting:
   p = 41 and p = 43 neither answer quickly.  But a FAILURE only needs one
   witness, and the witnesses that q1 found at p = 17..37 use very few distinct
   values -- (0,0,0,1,1,1,0,0,1,0,0,0,0) at p = 31, and only {0,1,7} at p = 37.
   So restrict the alphabet and enumerate exhaustively.

   The answer is one-sided and says so:
     FOUND    an explicit v, replayable in q1/check_unsaved.py -> T2(k,p) FAILS.
     NONE     no unsaved v with all coordinates in A.  Says nothing about
              other alphabets, so it is NOT a proof that T2(k,p) holds.

   Same constraint set as q1/cover.c: pairs (s,j), s != 0, j in Z_p, and
   (i,a) hits (s,j) when s*a + floor(m*((i*j) mod p)/p) = 0 or m-1 (mod m).
   v is unsaved iff the hit sets of its coordinates cover every pair.

   gcc -O3 -std=c11 -o probe probe.c
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK 16
#define MAXW 512

static int K, M, P, NCON, NW;
static int alpha[MAXK + 1], na;
static uint64_t hit[MAXK][MAXK + 1][MAXW];   /* per (i, value) */
static uint64_t reach[MAXK + 1][MAXW];       /* suffix union over i >= d      */
static uint64_t FULL[MAXW];
static int val[MAXK];
static long long leaves, cuts;
static int found;

static inline void bset(uint64_t *b, int i) { b[i >> 6] |= 1ull << (i & 63); }

static int mprimes[MAXK], nmprimes;

static void factor_m(void)
{
  nmprimes = 0;
  int x = M;
  for (int q = 2; q * q <= x; q++)
    if (x % q == 0) { mprimes[nmprimes++] = q; while (x % q == 0) x /= q; }
  if (x > 1) mprimes[nmprimes++] = x;
}

/* ST26 Def 2.1: a witness is needed only when some v_i = 0 and no prime
   q | m divides all but at most one coordinate. */
static int needs_witness(void)
{
  int haszero = 0;
  for (int i = 0; i < K; i++) if (val[i] == 0) haszero = 1;
  if (!haszero) return 0;
  for (int t = 0; t < nmprimes; t++) {
    int c = 0;
    for (int i = 0; i < K; i++) if (val[i] % mprimes[t]) c++;
    if (c <= 1) return 0;
  }
  return 1;
}

static void build(void)
{
  NCON = (M - 1) * P;
  NW = (NCON + 63) / 64;
  if (NW > MAXW) { fprintf(stderr, "FATAL: p too large\n"); exit(2); }
  memset(hit, 0, sizeof(hit));
  for (int j = 0; j < P; j++) {
    int B[MAXK];
    for (int i = 1; i <= K; i++) B[i - 1] = (int)((long long)M * ((long long)i * j % P) / P);
    int ok = 0;
    for (int i = 0; i < K; i++) if (B[i] == 0 || B[i] == M - 1) ok = 1;
    if (!ok) { fprintf(stderr, "FATAL: s=0 pair j=%d unhittable\n", j); exit(2); }
    for (int s = 1; s < M; s++) {
      int c = (s - 1) * P + j;
      for (int i = 0; i < K; i++)
        for (int a = 0; a < M; a++)
          if ((s * a + B[i]) % M == 0 || (s * a + B[i]) % M == M - 1) bset(hit[i][a], c);
    }
  }
  memset(FULL, 0, sizeof(FULL));
  for (int c = 0; c < NCON; c++) bset(FULL, c);
  /* reach[d] = what coordinates d..K-1 could still cover, over A */
  memset(reach, 0, sizeof(reach));
  for (int d = K - 1; d >= 0; d--)
    for (int w = 0; w < NW; w++) {
      uint64_t u = reach[d + 1][w];
      for (int t = 0; t < na; t++) u |= hit[d][alpha[t]][w];
      reach[d][w] = u;
    }
}

static void rec(int d, uint64_t *cov)
{
  if (found) return;
  for (int w = 0; w < NW; w++)
    if (FULL[w] & ~cov[w] & ~reach[d][w]) { cuts++; return; }   /* unreachable */
  if (d == K) {
    leaves++;
    if (needs_witness()) {
      for (int w = 0; w < NW; w++) if (FULL[w] & ~cov[w]) return;
      found = 1;
    }
    return;
  }
  for (int t = 0; t < na && !found; t++) {
    uint64_t nc[MAXW];
    for (int w = 0; w < NW; w++) nc[w] = cov[w] | hit[d][alpha[t]][w];
    val[d] = alpha[t];
    rec(d + 1, nc);
  }
}

int main(int argc, char **argv)
{
  K = 13; P = 0;
  const char *as = "0,1";
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k")) K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p")) P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--alpha")) as = argv[++i];
  }
  M = K + 1;
  if (!P) P = M;
  na = 0;
  for (const char *s = as; *s; ) {
    alpha[na++] = (int)strtol(s, (char **)&s, 10);
    if (*s == ',') s++;
  }
  factor_m();
  build();

  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  uint64_t cov[MAXW]; memset(cov, 0, sizeof(cov));
  rec(0, cov);
  clock_gettime(CLOCK_MONOTONIC, &t1);
  double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);

  printf("k=%d p=%d alphabet {%s} pairs=%d  ", K, P, as, NCON);
  if (found) {
    printf("FOUND unsaved v =");
    for (int i = 0; i < K; i++) printf(" %d", val[i]);
    printf("  -> T2(%d,%d) FAILS\n", K, P);
  } else {
    printf("NONE in this alphabet (says nothing about other v)\n");
  }
  printf("leaves=%lld cuts=%lld seconds=%.2f\n", leaves, cuts, el);
  return found ? 0 : 1;
}
