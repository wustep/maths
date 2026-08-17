/* I(k,p,1) covering DFS, matching ST26/Rosenfeld: speeds in 1..(p-1)/2,
   combinations with repetition, times 1..p/2, canonicalize by units and ±.

   gcc -O3 -std=c11 -o find_cover find_cover.c
   ./find_cover --k 6 --p 47
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXP 80
#define MAXK 16

static int K, P, H; /* H = P/2 */
static uint64_t cover[MAXP]; /* bit i = time slot 0..H-1 for speed i+1 */
static uint64_t ALLT;
static int speeds[MAXK];
static uint64_t n_raw, n_canon;

static int mod_pow(int a, int e, int p)
{
  long long r = 1, x = a % p;
  while (e) {
    if (e & 1) r = r * x % p;
    x = x * x % p;
    e >>= 1;
  }
  return (int)r;
}

static void canon(const int *in, int *out)
{
  int best[MAXK];
  int have = 0;
  for (int take = 0; take < K; take++) {
    int inv = mod_pow(in[take], P - 2, P);
    int tmp[MAXK];
    for (int j = 0; j < K; j++) {
      int v = (int)((long long)in[j] * inv % P);
      int f = P - v;
      tmp[j] = v < f ? v : f;
    }
    /* sort */
    for (int a = 0; a < K; a++)
      for (int b = a + 1; b < K; b++)
        if (tmp[b] < tmp[a]) {
          int t = tmp[a];
          tmp[a] = tmp[b];
          tmp[b] = t;
        }
    if (!have) {
      memcpy(best, tmp, K * sizeof(int));
      have = 1;
    } else {
      int less = 0;
      for (int j = 0; j < K; j++)
        if (tmp[j] != best[j]) {
          less = tmp[j] < best[j];
          break;
        }
      if (less) memcpy(best, tmp, K * sizeof(int));
    }
  }
  memcpy(out, best, K * sizeof(int));
}

static void rec(int pos, int start, uint64_t cov, int *elim)
{
  if (pos == K) {
    if (cov != ALLT) return;
    n_raw++;
    int c[MAXK];
    canon(speeds, c);
    /* count unique later if needed; here just raw covers of this search tree
       which already is combinations with repetition in increasing index */
    n_canon++; /* not actually unique; caller can unique */
    return;
  }
  /* next time to cover */
  int next = -1;
  if (cov != ALLT) {
    uint64_t miss = ALLT & ~cov;
    next = 0;
    while (next < H && !((miss >> next) & 1ull)) next++;
  }
  for (int i = start; i < H; i++) {
    if (elim[i]) continue;
    if (next >= 0 && !((cover[i] >> next) & 1ull)) continue;
    speeds[pos] = i + 1;
    rec(pos + 1, i, cov | cover[i], elim); /* allow repeats: start=i */
  }
}

int main(int argc, char **argv)
{
  K = 6;
  P = 47;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k") && i + 1 < argc) K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p") && i + 1 < argc) P = atoi(argv[++i]);
  }
  if (P > MAXP || K > MAXK || P < 3) {
    fprintf(stderr, "range\n");
    return 2;
  }
  H = P / 2;
  ALLT = (H >= 64) ? ~0ull : ((1ull << H) - 1ull);
  for (int i = 0; i < H; i++) {
    cover[i] = 0;
    int spd = i + 1;
    for (int t = 1; t <= H; t++) {
      int rem = (int)((long long)t * spd % P);
      int bad = (rem * (K + 1) < P) || ((P - rem) * (K + 1) < P);
      if (bad) cover[i] |= 1ull << (H - t);
    }
  }
  int elim[MAXP] = {0};
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  rec(0, 0, 0, elim);
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("find_cover k=%d p=%d raw_combos=%llu time=%.3fs\n", K, P,
         (unsigned long long)n_raw, (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  return 0;
}
