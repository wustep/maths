/* Incremental CSP: is there a v in N_k that is not p-saved?

   gcc -O3 -std=c11 -o ap_modp2 ap_modp2.c
   ./ap_modp2 --k 13 --p 191
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK 16
#define MAXM 17
#define MAXP 320
#define MAXPAIRS (MAXM * MAXP)
#define UW 120 /* 120*32=3840 > 14*320 */

static int K, M, P, NPAIRS, nB;
static int Bvec[MAXP][MAXK];
static uint32_t fail_bits[MAXK][MAXM][UW];
static int fail_list[MAXK][MAXM][MAXPAIRS];
static int fail_len[MAXK][MAXM];
static uint64_t nodes;
static int found;
static int obst[MAXK];

static inline void setb(uint32_t *b, int i) { b[i >> 5] |= 1u << (i & 31); }
static inline int testb(const uint32_t *b, int i) { return (b[i >> 5] >> (i & 31)) & 1u; }
static inline int pop32(uint32_t x) { return __builtin_popcount(x); }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

static void build(void)
{
  nB = P;
  NPAIRS = M * nB;
  for (int j = 0; j < P; j++)
    for (int i = 0; i < K; i++) {
      long long rem = (long long)(i + 1) * j % P;
      Bvec[j][i] = (int)((long long)M * rem / P);
    }
  for (int i = 0; i < K; i++)
    for (int val = 0; val < M; val++) {
      fail_len[i][val] = 0;
      memset(fail_bits[i][val], 0, sizeof(fail_bits[i][val]));
      for (int s = 0; s < M; s++)
        for (int j = 0; j < nB; j++) {
          int x = (s * val + Bvec[j][i]) % M;
          if (x == 0 || x == M - 1) {
            int b = s * nB + j;
            setb(fail_bits[i][val], b);
            fail_list[i][val][fail_len[i][val]++] = b;
          }
        }
    }
}

typedef struct {
  uint32_t dom[MAXK];
  int assigned[MAXK];
  int count[MAXPAIRS];
  uint32_t uncovered[UW];
  int nuncover;
} St;

static void uncover_fill(St *st)
{
  memset(st->uncovered, 0, sizeof(st->uncovered));
  st->nuncover = NPAIRS;
  for (int b = 0; b < NPAIRS; b++) st->uncovered[b >> 5] |= 1u << (b & 31);
}

static void mark_covered(St *st, int i, int val)
{
  int n = fail_len[i][val];
  for (int t = 0; t < n; t++) {
    int b = fail_list[i][val][t];
    uint32_t bit = 1u << (b & 31);
    if (st->uncovered[b >> 5] & bit) {
      st->uncovered[b >> 5] ^= bit;
      st->nuncover--;
    }
  }
}

static int del_val(St *st, int i, int val)
{
  if (!((st->dom[i] >> val) & 1u)) return 1;
  st->dom[i] &= ~(1u << val);
  int n = fail_len[i][val];
  for (int t = 0; t < n; t++) {
    int b = fail_list[i][val][t];
    st->count[b]--;
    if (st->count[b] == 0 && ((st->uncovered[b >> 5] >> (b & 31)) & 1u)) return 0;
  }
  return 1;
}

static int assign(St *st, int i, int val)
{
  uint32_t d = st->dom[i] & ~(1u << val);
  while (d) {
    int w = lsb32(d);
    d &= d - 1;
    if (!del_val(st, i, w)) return 0;
  }
  st->assigned[i] = val;
  mark_covered(st, i, val);
  return 1;
}

static int in_Nk_assigned(const St *st)
{
  int z = 0, nz = 0;
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] < 0) {
      if (st->dom[i] & 1u) z = 1;
      if (st->dom[i] & ~1u) nz = 1;
    } else if (st->assigned[i] == 0)
      z = 1;
    else
      nz = 1;
  }
  return z && nz;
}

static void extract(const St *st)
{
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0)
      obst[i] = st->assigned[i];
    else {
      uint32_t d = st->dom[i];
      /* prefer a value that keeps N_k */
      obst[i] = lsb32(d);
    }
  }
}

static int propagate(St *st)
{
  int changed = 1;
  int nwords = (NPAIRS + 31) / 32;
  while (changed) {
    changed = 0;
    if (st->nuncover == 0) return 1;
    for (int w = 0; w < nwords; w++) {
      uint32_t u = st->uncovered[w];
      while (u) {
        int b = (w << 5) + lsb32(u);
        u &= u - 1;
        if (b >= NPAIRS) continue;
        if (st->count[b] == 0) return -1;
        if (st->count[b] == 1) {
          int fi = -1, fv = -1;
          for (int i = 0; i < K; i++) {
            if (st->assigned[i] >= 0) continue;
            uint32_t d = st->dom[i];
            while (d) {
              int val = lsb32(d);
              d &= d - 1;
              if (testb(fail_bits[i][val], b)) {
                fi = i;
                fv = val;
                goto got;
              }
            }
          }
        got:
          if (fi < 0) return -1;
          if (!assign(st, fi, fv)) return -1;
          changed = 1;
          goto restart;
        }
      }
    }
  restart:;
  }
  return 0;
}

static int dpll(St *st);

static int accept_cover(const St *st)
{
  if (!in_Nk_assigned(st)) return 0;
  extract(st);
  found = 1;
  return 1;
}

static int branch(St *st)
{
  int nwords = (NPAIRS + 31) / 32;
  int bb = -1, bc = 100000;
  for (int w = 0; w < nwords; w++) {
    uint32_t u = st->uncovered[w];
    while (u) {
      int b = (w << 5) + lsb32(u);
      u &= u - 1;
      if (b >= NPAIRS) continue;
      if (st->count[b] < bc) {
        bc = st->count[b];
        bb = b;
        if (bc <= 2) goto chosen;
      }
    }
  }
chosen:
  if (bb < 0) return accept_cover(st);
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0) continue;
    uint32_t d = st->dom[i];
    while (d) {
      int val = lsb32(d);
      d &= d - 1;
      if (!testb(fail_bits[i][val], bb)) continue;
      St nxt = *st;
      nodes++;
      if (!assign(&nxt, i, val)) continue;
      int pr = propagate(&nxt);
      if (pr < 0) continue;
      if (pr > 0) {
        if (accept_cover(&nxt)) return 1;
        continue;
      }
      if (dpll(&nxt)) return 1;
    }
  }
  return 0;
}

static int dpll(St *st)
{
  if (found) return 1;
  nodes++;
  int pr = propagate(st);
  if (pr < 0) return 0;
  if (pr > 0) return accept_cover(st);
  return branch(st);
}

static void init_state(St *st)
{
  memset(st, 0, sizeof(*st));
  uncover_fill(st);
  uint32_t full = (M >= 32) ? 0xffffffffu : ((1u << M) - 1u);
  for (int i = 0; i < K; i++) {
    st->dom[i] = full;
    st->assigned[i] = -1;
    for (int val = 0; val < M; val++) {
      int n = fail_len[i][val];
      for (int t = 0; t < n; t++) st->count[fail_list[i][val][t]]++;
    }
  }
}

int main(int argc, char **argv)
{
  K = 13;
  P = 191;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k") && i + 1 < argc)
      K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p") && i + 1 < argc)
      P = atoi(argv[++i]);
  }
  M = K + 1;
  if (K < 2 || K > MAXK || P < 3 || P > MAXP) {
    fprintf(stderr, "range\n");
    return 2;
  }
  build();
  printf("ap_modp2 k=%d m=%d p=%d pairs=%d\n", K, M, P, NPAIRS);
  fflush(stdout);

  St st;
  init_state(&st);
  found = 0;
  nodes = 0;
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  int hit = dpll(&st);
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("hit=%d nodes=%llu time=%.3fs\n", hit, (unsigned long long)nodes,
         (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  if (hit) {
    printf("OBSTRUCTION ");
    for (int i = 0; i < K; i++) printf("%d%s", obst[i], i + 1 == K ? "" : ",");
    printf("\n");
    return 1;
  }
  printf("NO_OBSTRUCTION every N_k vector is p-saved\n");
  return 0;
}
