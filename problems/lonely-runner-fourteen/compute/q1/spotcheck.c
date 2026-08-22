/* spotcheck.c — corroborate a T2(k,p) HOLDS answer without trusting either search.

   v is saved iff  INTERSECT_i keep(i, v_i)  is non-empty, where
       keep(i,a) = { (s,j) : s*a + floor(m*((i*j) mod p)/p)  not in {0, m-1} }.
   That is a direct transcription of ST26 Lemma 4.3 over the full (k+1)*p pair
   set, with none of cover.c's reductions.  We stream candidate v through it:

     --mode random      uniform v with at least one zero coordinate
     --mode sparse      all v supported on <= 3 coordinates
     --mode ap          v_i = a*i + b (mod m) for every a,b, and one-coordinate
                        perturbations of those (the shapes that actually failed)
     --mode perturb     Hamming-ball of radius 2 around a given --v

   Reports any v that is unsaved AND not disposed of by the gcd branch.

   gcc -O3 -march=native -std=c11 -o spotcheck spotcheck.c
*/
#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXK 16
#define MAXW 512
static int K, M, P, NPAIR, NW;
static uint64_t keep[MAXK][MAXK + 1][MAXW];
static int mpr[4], nmpr;
static long long n_checked, n_needed, n_bad;

static void build(void)
{
  NPAIR = M * P; NW = (NPAIR + 63) / 64;
  memset(keep, 0, sizeof(keep));
  for (int s = 0; s < M; s++)
    for (int j = 0; j < P; j++) {
      int idx = s * P + j;
      for (int i = 1; i <= K; i++) {
        int B = (int)((long long)M * ((long long)i * j % P) / P);
        for (int a = 0; a < M; a++) {
          int x = (s * a + B) % M;
          if (x != 0 && x != M - 1) keep[i - 1][a][idx >> 6] |= 1ull << (idx & 63);
        }
      }
    }
  int x = M; nmpr = 0;
  for (int q = 2; q * q <= x; q++) if (x % q == 0) { mpr[nmpr++] = q; while (x % q == 0) x /= q; }
  if (x > 1) mpr[nmpr++] = x;
}

static int needs_witness(const int *v)             /* zero coord and not gcd-proper */
{
  int hz = 0;
  for (int i = 0; i < K; i++) if (v[i] == 0) hz = 1;
  if (!hz) return 0;
  for (int t = 0; t < nmpr; t++) {
    int c = 0;
    for (int i = 0; i < K; i++) if (v[i] % mpr[t]) c++;
    if (c <= 1) return 0;
  }
  return 1;
}

static int saved(const int *v)
{
  uint64_t A[MAXW];
  memcpy(A, keep[0][v[0]], NW * 8);
  for (int i = 1; i < K; i++) {
    uint64_t any = 0;
    for (int w = 0; w < NW; w++) { A[w] &= keep[i][v[i]][w]; any |= A[w]; }
    if (!any) return 0;
  }
  return 1;
}

static void report(const int *v)
{
  printf("UNSAVED AND NEEDED: v =");
  for (int i = 0; i < K; i++) printf(" %d", v[i]);
  printf("\n"); fflush(stdout);
}

static void test(const int *v)
{
  n_checked++;
  if (!needs_witness(v)) return;
  n_needed++;
  if (!saved(v)) { n_bad++; if (n_bad <= 8) report(v); }
}

static uint64_t rs = 88172645463325252ull;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

int main(int argc, char **argv)
{
  K = 13; P = 191; long long N = 10000000; const char *mode = "random"; const char *vs = NULL;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i],"--k")) K=atoi(argv[++i]);
    else if (!strcmp(argv[i],"--p")) P=atoi(argv[++i]);
    else if (!strcmp(argv[i],"--n")) N=atoll(argv[++i]);
    else if (!strcmp(argv[i],"--mode")) mode=argv[++i];
    else if (!strcmp(argv[i],"--seed")) rs=atoll(argv[++i])|1;
    else if (!strcmp(argv[i],"--v")) vs=argv[++i];
  }
  M = K + 1; build();
  int v[MAXK];

  if (!strcmp(mode,"random")) {
    for (long long t = 0; t < N; t++) {
      for (int i = 0; i < K; i++) v[i] = rnd() % M;
      v[rnd() % K] = 0;                       /* force a zero coordinate */
      test(v);
    }
  } else if (!strcmp(mode,"sparse")) {
    for (int i = 0; i < K; i++) v[i] = 0;
    test(v);
    for (int i = 0; i < K; i++) for (int a = 1; a < M; a++) {
      memset(v,0,sizeof(v)); v[i]=a; test(v); }
    for (int i = 0; i < K; i++) for (int a = 1; a < M; a++)
      for (int i2 = i+1; i2 < K; i2++) for (int b = 1; b < M; b++) {
        memset(v,0,sizeof(v)); v[i]=a; v[i2]=b; test(v); }
    for (int i = 0; i < K; i++) for (int a = 1; a < M; a++)
      for (int i2 = i+1; i2 < K; i2++) for (int b = 1; b < M; b++)
        for (int i3 = i2+1; i3 < K; i3++) for (int c = 1; c < M; c++) {
          memset(v,0,sizeof(v)); v[i]=a; v[i2]=b; v[i3]=c; test(v); }
  } else if (!strcmp(mode,"ap")) {
    for (int a = 0; a < M; a++) for (int b = 0; b < M; b++) {
      for (int i = 0; i < K; i++) v[i] = (a*(i+1)+b) % M;
      test(v);
      for (int i = 0; i < K; i++) { int o=v[i];
        for (int c = 0; c < M; c++) { v[i]=c; test(v);
          for (int i2 = 0; i2 < K; i2++) { int o2=v[i2];
            for (int c2 = 0; c2 < M; c2++) { v[i2]=c2; test(v); } v[i2]=o2; } }
        v[i]=o; }
    }
  } else if (!strcmp(mode,"perturb")) {
    int base[MAXK]; char *q=strdup(vs);
    for (int i=0;i<K;i++) base[i]=atoi(strsep(&q,","));
    for (int i = 0; i < K; i++) for (int a = 0; a < M; a++)
      for (int i2 = 0; i2 < K; i2++) for (int b = 0; b < M; b++) {
        memcpy(v,base,sizeof(v)); v[i]=a; v[i2]=b; test(v); }
  }
  printf("mode=%s k=%d p=%d checked=%lld needed-a-witness=%lld UNSAVED-AND-NEEDED=%lld\n",
         mode, K, P, n_checked, n_needed, n_bad);
  return n_bad ? 1 : 0;
}
