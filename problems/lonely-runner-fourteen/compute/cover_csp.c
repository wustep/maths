/* Incremental covering CSP: exists v in N_13, outside the odd-zero family,
   that fails every (s,r).

   Family excluded by forcing at least one odd-indexed speed (1,3,...,13)
   to be nonzero.

   Compile: gcc -O3 -std=c11 -o cover_csp cover_csp.c
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define K 13
#define M 14
#define NPAIRS (M * M)

static uint32_t fail_bits[K][M][4]; /* 196 bits */
static int fail_list[K][M][NPAIRS];
static int fail_len[K][M];
static uint64_t nodes;
static int found;
static int obst[K];

static inline void setb(uint32_t b[4], int i) { b[i >> 5] |= 1u << (i & 31); }
static inline int testb(const uint32_t b[4], int i) { return (b[i >> 5] >> (i & 31)) & 1u; }

static void pre(void)
{
  for (int i = 0; i < K; i++)
    for (int val = 0; val < M; val++) {
      fail_len[i][val] = 0;
      memset(fail_bits[i][val], 0, sizeof(fail_bits[i][val]));
      for (int s = 0; s < M; s++)
        for (int r = 0; r < M; r++) {
          int x = (s * val + r * (i + 1)) % M;
          if (x == 0 || x == M - 1) {
            int b = s * M + r;
            setb(fail_bits[i][val], b);
            fail_list[i][val][fail_len[i][val]++] = b;
          }
        }
    }
}

typedef struct {
  uint32_t dom[K];
  int assigned[K]; /* -1 free */
  int count[NPAIRS];
  uint32_t uncovered[7]; /* 196 bits, 7*32 */
  int nuncover;
} St;

static inline int pop32(uint32_t x) { return __builtin_popcount(x); }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

static void uncover_clear(St *st)
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

/* Remove val from i's domain; decrement counts. Return 0 if some uncovered
   pair now has count 0. */
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
  /* delete every other value */
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

static int propagate_force(St *st)
{
  int changed = 1;
  while (changed) {
    changed = 0;
    if (st->nuncover == 0) return 1;
    for (int w = 0; w < 7; w++) {
      uint32_t u = st->uncovered[w];
      while (u) {
        int b = (w << 5) + lsb32(u);
        u &= u - 1;
        if (st->count[b] == 0) return -1;
        if (st->count[b] == 1) {
          /* find the unique remaining killer */
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

static int branch(St *st)
{
  /* pick uncovered pair with smallest count */
  int bb = -1, bc = 100;
  for (int w = 0; w < 7; w++) {
    uint32_t u = st->uncovered[w];
    while (u) {
      int b = (w << 5) + lsb32(u);
      u &= u - 1;
      if (st->count[b] < bc) {
        bc = st->count[b];
        bb = b;
        if (bc <= 2) goto chosen;
      }
    }
  }
chosen:
  if (bb < 0) return 1;
  /* try killer assignments */
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0) continue;
    uint32_t d = st->dom[i];
    while (d) {
      int val = lsb32(d);
      d &= d - 1;
      if (!testb(fail_bits[i][val], bb)) continue;
      St nxt = *st;
      nodes++;
      if (assign(&nxt, i, val)) {
        int pr = propagate_force(&nxt);
        if (pr < 0) continue;
        if (pr > 0) {
          memcpy(obst, nxt.assigned, sizeof(obst));
          /* fill free with any remaining domain value */
          for (int j = 0; j < K; j++)
            if (obst[j] < 0) obst[j] = lsb32(nxt.dom[j]);
          found = 1;
          return 1;
        }
        if (dpll(&nxt)) return 1;
      }
    }
  }
  return 0;
}

static int dpll(St *st)
{
  if (found) return 1;
  nodes++;
  int pr = propagate_force(st);
  if (pr < 0) return 0;
  if (pr > 0) {
    memcpy(obst, st->assigned, sizeof(obst));
    for (int j = 0; j < K; j++)
      if (obst[j] < 0) obst[j] = lsb32(st->dom[j]);
    found = 1;
    return 1;
  }
  return branch(st);
}

static void init_state(St *st, uint32_t *doms)
{
  memset(st, 0, sizeof(*st));
  uncover_clear(st);
  memset(st->count, 0, sizeof(st->count));
  for (int i = 0; i < K; i++) {
    st->dom[i] = doms[i];
    st->assigned[i] = -1;
    uint32_t d = doms[i];
    while (d) {
      int val = lsb32(d);
      d &= d - 1;
      int n = fail_len[i][val];
      for (int t = 0; t < n; t++) st->count[fail_list[i][val][t]]++;
    }
  }
}

int main(void)
{
  pre();
  uint32_t full = (1u << M) - 1u;
  uint32_t nonzero = full & ~1u;
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);

  /* Search 7 slices: odd speed 2a+1 forced nonzero. */
  for (int odd = 0; odd < K; odd += 2) {
    St st;
    uint32_t doms[K];
    for (int i = 0; i < K; i++) doms[i] = full;
    doms[odd] = nonzero;
    init_state(&st, doms);
    found = 0;
    nodes = 0;
    int hit = dpll(&st);
    printf("force_odd_speed_%d_nonzero hit=%d nodes=%llu obst=", odd + 1, hit,
           (unsigned long long)nodes);
    if (hit) {
      for (int i = 0; i < K; i++) printf("%d%s", obst[i], i + 1 == K ? "" : ",");
    } else {
      printf("none");
    }
    printf("\n");
    fflush(stdout);
    if (hit) return 1;
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("NO_MIXED_OBSTRUCTION time=%.3fs\n",
         (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  return 0;
}
