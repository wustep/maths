/* Enumerate p-independent unsaved v in N_13 by leftover r-columns,
   then test p-salvage for a given prime.

   gcc -O3 -std=c11 -o enum_and_salvage enum_and_salvage.c
   ./enum_and_salvage --p 191
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define K 13
#define M 14

static uint16_t col[K + 1][M]; /* col[i][val] bit s set if (s,r0) fails; built per r0 */
static int Rset[K + 1][M];
static int Rlen[K + 1];

static int Bvec[400][K];
static int P;

static void pre_R(void)
{
  for (int i = 1; i <= K; i++) {
    Rlen[i] = 0;
    for (int r = 0; r < M; r++)
      if ((r * i) % M == 0 || (r * i) % M == M - 1) Rset[i][Rlen[i]++] = r;
  }
}

static void build_col(int r0)
{
  for (int i = 1; i <= K; i++)
    for (int val = 0; val < M; val++) {
      uint16_t m = 0;
      for (int s = 0; s < M; s++) {
        int x = (s * val + r0 * i) % M;
        if (x == 0 || x == M - 1) m |= (uint16_t)1 << s;
      }
      col[i][val] = m;
    }
}

static int zeros_cover_r(const int *isZ, int r)
{
  for (int i = 1; i <= K; i++)
    if (isZ[i]) {
      for (int t = 0; t < Rlen[i]; t++)
        if (Rset[i][t] == r) return 1;
    }
  return 0;
}

/* exist assignment of free (nonzero) covering all leftover columns */
static int free_list[K], nfree;
static int vals[K];
static int rem_r[M], nrem;
static uint64_t n_mixed_pat, n_mixed_vec, n_family_vec;
static uint64_t n_saved, n_unsaved;
static void check_vec(const int *v);
static int unsaved_ex[8][K], n_unex;
static int mixed_ex[4][K], n_mex;

static int rec_cover(int pos, uint16_t *left /* nrem entries */)
{
  int done = 1;
  for (int c = 0; c < nrem; c++)
    if (left[c]) {
      done = 0;
      break;
    }
  if (done) return 1;
  if (pos == nfree) return 0;
  /* pool prune */
  uint16_t pool[M];
  memset(pool, 0, sizeof(pool));
  for (int p2 = pos; p2 < nfree; p2++) {
    int i = free_list[p2];
    for (int val = 1; val < M; val++)
      for (int c = 0; c < nrem; c++) pool[c] |= col[i][val]; /* wait col is for one r — rebuild per column */
  }
  /* col[] is for a single r0; we need per-column fail. Fix: store col_r[r][i][val] */
  return -99; /* placeholder, real rec below */
}

static uint16_t COL[M][K + 1][M]; /* COL[r][i][val] */

static void build_all_col(void)
{
  for (int r = 0; r < M; r++)
    for (int i = 1; i <= K; i++)
      for (int val = 0; val < M; val++) {
        uint16_t m = 0;
        for (int s = 0; s < M; s++) {
          int x = (s * val + r * i) % M;
          if (x == 0 || x == M - 1) m |= (uint16_t)1 << s;
        }
        COL[r][i][val] = m;
      }
}

static int rec(int pos, uint16_t *left)
{
  int done = 1;
  for (int c = 0; c < nrem; c++)
    if (left[c]) {
      done = 0;
      break;
    }
  if (done) {
    /* leftover columns covered: every completion of remaining free
       coords is unsaved. Check a representative, then all if nfree-pos small. */
    int v[K];
    for (int i = 0; i < K; i++) v[i] = 0;
    for (int j = 0; j < pos; j++) v[free_list[j] - 1] = vals[j];
    int rest = nfree - pos;
    if (rest == 0) {
      n_mixed_vec++;
      check_vec(v);
      if (n_mex < 4) memcpy(mixed_ex[n_mex++], v, sizeof(v));
    } else if (rest <= 7) {
      uint64_t lim = 1;
      for (int t = 0; t < rest; t++) lim *= 13ull;
      for (uint64_t idx = 0; idx < lim; idx++) {
        uint64_t x = idx;
        for (int t = 0; t < rest; t++) {
          v[free_list[pos + t] - 1] = (int)(x % 13) + 1;
          x /= 13;
        }
        n_mixed_vec++;
        check_vec(v);
      }
      if (n_mex < 4) memcpy(mixed_ex[n_mex++], v, sizeof(v));
    } else {
      /* too many completions: check 1 + hash samples, count exactly */
      for (int t = pos; t < nfree; t++) v[free_list[t] - 1] = 1;
      n_mixed_vec += 1;
      for (int t = 0; t < rest; t++) n_mixed_vec = n_mixed_vec * 13ull; /* wait no */
      /* recount properly */
      n_mixed_vec -= 1;
      uint64_t ways = 1;
      for (int t = 0; t < rest; t++) ways *= 13ull;
      n_mixed_vec += ways;
      check_vec(v);
      if (n_mex < 4) memcpy(mixed_ex[n_mex++], v, sizeof(v));
    }
    return 0; /* keep enumerating sibling covers */
  }
  if (pos == nfree) return 0;
  uint16_t pool[14];
  for (int c = 0; c < nrem; c++) pool[c] = 0;
  for (int p2 = pos; p2 < nfree; p2++) {
    int i = free_list[p2];
    for (int val = 1; val < M; val++)
      for (int c = 0; c < nrem; c++) pool[c] |= COL[rem_r[c]][i][val];
  }
  for (int c = 0; c < nrem; c++)
    if (left[c] & ~pool[c]) return 0;
  int i = free_list[pos];
  int any = 0;
  for (int val = 1; val < M; val++) {
    vals[pos] = val;
    uint16_t nxt[14];
    for (int c = 0; c < nrem; c++) nxt[c] = left[c] & ~COL[rem_r[c]][i][val];
    if (rec(pos + 1, nxt)) any = 1;
  }
  return any;
}

/* count all covering assignments (not just existence) for small nfree */
static uint64_t rec_count(int pos, uint16_t *left)
{
  int done = 1;
  for (int c = 0; c < nrem; c++)
    if (left[c]) {
      done = 0;
      break;
    }
  if (done) {
    uint64_t ways = 1;
    for (int p2 = pos; p2 < nfree; p2++) ways *= 13ull; /* remaining free anything nonzero */
    return ways;
  }
  if (pos == nfree) return 0;
  uint16_t pool[14];
  for (int c = 0; c < nrem; c++) pool[c] = 0;
  for (int p2 = pos; p2 < nfree; p2++) {
    int i = free_list[p2];
    for (int val = 1; val < M; val++)
      for (int c = 0; c < nrem; c++) pool[c] |= COL[rem_r[c]][i][val];
  }
  for (int c = 0; c < nrem; c++)
    if (left[c] & ~pool[c]) return 0;
  uint64_t tot = 0;
  int i = free_list[pos];
  for (int val = 1; val < M; val++) {
    vals[pos] = val;
    uint16_t nxt[14];
    for (int c = 0; c < nrem; c++) nxt[c] = left[c] & ~COL[rem_r[c]][i][val];
    tot += rec_count(pos + 1, nxt);
  }
  return tot;
}

static int p_saved_vec(const int *v)
{
  for (int s = 0; s < M; s++) {
    for (int j = 0; j < P; j++) {
      int ok = 1;
      for (int i = 0; i < K; i++) {
        int x = (s * v[i] + Bvec[j][i]) % M;
        if (x == 0 || x == M - 1) {
          ok = 0;
          break;
        }
      }
      if (ok) return 1;
    }
  }
  return 0;
}

static void build_B(void)
{
  for (int j = 0; j < P; j++)
    for (int i = 0; i < K; i++) {
      long long rem = (long long)(i + 1) * j % P;
      Bvec[j][i] = (int)((long long)M * rem / P);
    }
}

static void check_vec(const int *v)
{
  if (p_saved_vec(v))
    n_saved++;
  else {
    n_unsaved++;
    if (n_unex < 8) memcpy(unsaved_ex[n_unex++], v, K * sizeof(int));
  }
}

/* enumerate family: odd speeds 0, evens in 0..13, not all zero */
static void enum_family(void)
{
  int ev[6] = {2, 4, 6, 8, 10, 12}; /* 1-based even speeds */
  int a[6];
  /* 14^6 loop */
  uint64_t lim = 1;
  for (int t = 0; t < 6; t++) lim *= 14ull;
  for (uint64_t idx = 0; idx < lim; idx++) {
    uint64_t x = idx;
    int allz = 1, allnz = 1;
    for (int t = 0; t < 6; t++) {
      a[t] = (int)(x % 14);
      x /= 14;
      if (a[t]) allz = 0;
      else allnz = 0;
    }
    if (allz) continue; /* v=0 */
    if (allnz) continue; /* not unsaved by zeros-alone; mixed handled later */
    int v[K];
    for (int i = 0; i < K; i++) v[i] = 0; /* odds zero, evens overwritten */
    for (int t = 0; t < 6; t++) v[ev[t] - 1] = a[t];
    n_family_vec++;
    check_vec(v);
  }
}

int main(int argc, char **argv)
{
  P = 191;
  int do_family = 1, rem_max = 6;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--p") && i + 1 < argc) P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--no-family")) do_family = 0;
    else if (!strcmp(argv[i], "--rem-max") && i + 1 < argc) rem_max = atoi(argv[++i]);
  }
  pre_R();
  build_all_col();
  build_B();
  printf("enum_and_salvage p=%d rem_max=%d\n", P, rem_max);
  fflush(stdout);
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);

  if (do_family) {
    enum_family();
    printf("family_nonzero_even_zero %llu p_saved %llu p_unsaved %llu\n",
           (unsigned long long)n_family_vec, (unsigned long long)n_saved,
           (unsigned long long)n_unsaved);
    fflush(stdout);
  }

  uint64_t n_full = 0, n_mixed_pats = 0, n_mixed_exist = 0;
  n_saved = n_unsaved = 0; /* reset for mixed */
  for (int mask = 1; mask < (1 << K) - 1; mask++) {
    int isZ[K + 1] = {0};
    nfree = 0;
    int cov[M] = {0};
    for (int i = 1; i <= K; i++) {
      if (mask >> (i - 1) & 1) {
        isZ[i] = 1;
        for (int t = 0; t < Rlen[i]; t++) cov[Rset[i][t]] = 1;
      } else {
        free_list[nfree++] = i;
      }
    }
    nrem = 0;
    for (int r = 0; r < M; r++)
      if (!cov[r]) rem_r[nrem++] = r;
    if (nrem == 0) {
      n_full++;
      continue;
    }
    if (nrem > rem_max) continue;
    uint16_t left[14];
    for (int c = 0; c < nrem; c++) left[c] = (uint16_t)((1 << M) - 1);
    uint64_t before = n_mixed_vec;
    rec(0, left);
    if (n_mixed_vec > before) {
      n_mixed_exist++;
      n_mixed_pats++;
    }
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("full_zero_cover_pats %llu mixed_pats_with_hit %llu mixed_vectors %llu\n",
         (unsigned long long)n_full, (unsigned long long)n_mixed_pats,
         (unsigned long long)n_mixed_vec);
  printf("mixed_examples_p_saved %llu unsaved %llu time=%.3fs\n", (unsigned long long)n_saved,
         (unsigned long long)n_unsaved, (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  for (int t = 0; t < n_mex; t++) {
    printf("mixed_ex ");
    for (int i = 0; i < K; i++) printf("%d%s", mixed_ex[t][i], i + 1 == K ? "" : ",");
    printf("\n");
  }
  for (int t = 0; t < n_unex; t++) {
    printf("UNSAVED ");
    for (int i = 0; i < K; i++) printf("%d%s", unsaved_ex[t][i], i + 1 == K ? "" : ",");
    printf("\n");
  }
  return n_unsaved ? 1 : 0;
}
