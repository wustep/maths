/* Exhaust the odd-zero family in N_13 and test p-salvage.

   Family: v_{1,3,5,7,9,11,13}=0, even speeds in {0,...,13}, not all-zero
   and not all-even-nonzero (those are not zeros-alone unsaved).
   Count = 14^6 - 13^6 - 1 = 2702726.

   gcc -O3 -std=c11 -o family_salvage family_salvage.c
   ./family_salvage --p 191
*/
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define K 13
#define M 14

static int Bvec[400][K], P;

static int p_saved(const int *v)
{
  for (int s = 0; s < M; s++)
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
  return 0;
}

int main(int argc, char **argv)
{
  P = 191;
  if (argc >= 3 && !strcmp(argv[1], "--p")) P = atoi(argv[2]);
  for (int j = 0; j < P; j++)
    for (int i = 0; i < K; i++) {
      long long rem = (long long)(i + 1) * j % P;
      Bvec[j][i] = (int)((long long)M * rem / P);
    }
  int ev[6] = {1, 3, 5, 7, 9, 11}; /* 0-based even speeds */
  unsigned long long n = 0, ok = 0, bad = 0;
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  for (int a0 = 0; a0 < M; a0++)
    for (int a1 = 0; a1 < M; a1++)
      for (int a2 = 0; a2 < M; a2++)
        for (int a3 = 0; a3 < M; a3++)
          for (int a4 = 0; a4 < M; a4++)
            for (int a5 = 0; a5 < M; a5++) {
              int a[6] = {a0, a1, a2, a3, a4, a5};
              int z = 0, nz = 0;
              for (int t = 0; t < 6; t++) {
                if (a[t]) nz++;
                else z++;
              }
              if (z == 6) continue;  /* all-zero */
              if (nz == 6) continue; /* not in zeros-alone family */
              int v[K] = {0};
              for (int t = 0; t < 6; t++) v[ev[t]] = a[t];
              n++;
              if (p_saved(v))
                ok++;
              else {
                bad++;
                if (bad <= 3) {
                  printf("UNSAVED");
                  for (int i = 0; i < K; i++) printf(" %d", v[i]);
                  printf("\n");
                }
              }
            }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("p=%d family=%llu saved=%llu unsaved=%llu expect=2702726 time=%.3fs\n", P, n, ok, bad,
         (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  return bad ? 1 : 0;
}
