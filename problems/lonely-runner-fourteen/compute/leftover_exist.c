/* Existence-only leftover covering, with node cap and per-pattern logs.

   gcc -O3 -std=c11 -o leftover_exist leftover_exist.c
   ./leftover_exist --rem-min 5 --rem-max 5 --cap 2000000
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define K 13
#define M 14
#define MAXPAIRS 196

static int Rset[K + 1][M], Rlen[K + 1];
static uint64_t nodes, cap;
static int abort_cap;

static void pre(void)
{
  for (int i = 1; i <= K; i++) {
    Rlen[i] = 0;
    for (int r = 0; r < M; r++)
      if ((r * i) % M == 0 || (r * i) % M == M - 1) Rset[i][Rlen[i]++] = r;
  }
}

static int nP;
static int fail_list[K][M][MAXPAIRS], fail_len[K][M];
static uint32_t fail_bits[K][M][7];
static inline void setb(uint32_t *b, int i) { b[i >> 5] |= 1u << (i & 31); }
static inline int testb(const uint32_t *b, int i) { return (b[i >> 5] >> (i & 31)) & 1u; }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

static void build_fail(const int *rem_r, int nrem)
{
  nP = nrem * M;
  int pair_s[MAXPAIRS], pair_r[MAXPAIRS], t = 0;
  for (int c = 0; c < nrem; c++)
    for (int s = 0; s < M; s++, t++) {
      pair_s[t] = s;
      pair_r[t] = rem_r[c];
    }
  for (int i = 0; i < K; i++)
    for (int val = 0; val < M; val++) {
      fail_len[i][val] = 0;
      memset(fail_bits[i][val], 0, sizeof(fail_bits[i][val]));
      for (int b = 0; b < nP; b++) {
        int x = (pair_s[b] * val + pair_r[b] * (i + 1)) % M;
        if (x == 0 || x == M - 1) {
          fail_list[i][val][fail_len[i][val]++] = b;
          setb(fail_bits[i][val], b);
        }
      }
    }
}

typedef struct {
  uint32_t dom[K];
  int assigned[K];
  int count[MAXPAIRS];
  uint32_t uncovered[7];
  int nuncover;
} St;

static void mark_cov(St *st, int i, int val)
{
  for (int t = 0; t < fail_len[i][val]; t++) {
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
  for (int t = 0; t < fail_len[i][val]; t++) {
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
  mark_cov(st, i, val);
  return 1;
}

static int propagate(St *st)
{
  int nwords = (nP + 31) / 32, changed = 1;
  while (changed) {
    changed = 0;
    if (st->nuncover == 0) return 1;
    for (int w = 0; w < nwords; w++) {
      uint32_t u = st->uncovered[w];
      while (u) {
        int b = (w << 5) + lsb32(u);
        u &= u - 1;
        if (b >= nP) continue;
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

static int branch(St *st)
{
  if (nodes > cap) {
    abort_cap = 1;
    return 0;
  }
  int nwords = (nP + 31) / 32, bb = -1, bc = 100000;
  for (int w = 0; w < nwords; w++) {
    uint32_t u = st->uncovered[w];
    while (u) {
      int b = (w << 5) + lsb32(u);
      u &= u - 1;
      if (b >= nP) continue;
      if (st->count[b] < bc) {
        bc = st->count[b];
        bb = b;
        if (bc <= 2) goto chosen;
      }
    }
  }
chosen:
  if (bb < 0) return 1;
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
      if (pr > 0) return 1;
      if (dpll(&nxt)) return 1;
      if (abort_cap) return 0;
    }
  }
  return 0;
}

static int dpll(St *st)
{
  if (abort_cap || nodes > cap) {
    abort_cap = 1;
    return 0;
  }
  nodes++;
  int pr = propagate(st);
  if (pr < 0) return 0;
  if (pr > 0) return 1;
  return branch(st);
}

int main(int argc, char **argv)
{
  int rem_min = 5, rem_max = 5;
  cap = 2000000;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--rem-min") && i + 1 < argc) rem_min = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--rem-max") && i + 1 < argc) rem_max = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--cap") && i + 1 < argc) cap = strtoull(argv[++i], NULL, 10);
  }
  pre();
  printf("leftover_exist rem=%d..%d cap=%llu\n", rem_min, rem_max, (unsigned long long)cap);
  fflush(stdout);
  int npat = 0, nhit = 0, nno = 0, nunk = 0;
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  for (int mask = 1; mask < (1 << K) - 1; mask++) {
    int rem_r[M], nrem = 0, cov[M] = {0}, nZ = 0;
    for (int i = 0; i < K; i++)
      if (mask >> i & 1) {
        nZ++;
        for (int t = 0; t < Rlen[i + 1]; t++) cov[Rset[i + 1][t]] = 1;
      }
    for (int r = 0; r < M; r++)
      if (!cov[r]) rem_r[nrem++] = r;
    if (nrem < rem_min || nrem > rem_max) continue;
    npat++;
    build_fail(rem_r, nrem);
    St st;
    memset(&st, 0, sizeof(st));
    st.nuncover = nP;
    for (int b = 0; b < nP; b++) st.uncovered[b >> 5] |= 1u << (b & 31);
    for (int i = 0; i < K; i++) {
      if (mask >> i & 1) {
        st.dom[i] = 1u;
        st.assigned[i] = 0;
        mark_cov(&st, i, 0);
        for (int t = 0; t < fail_len[i][0]; t++) st.count[fail_list[i][0][t]]++;
      } else {
        st.dom[i] = (1u << M) - 2;
        st.assigned[i] = -1;
        for (int val = 1; val < M; val++)
          for (int t = 0; t < fail_len[i][val]; t++) st.count[fail_list[i][val][t]]++;
      }
    }
    nodes = 0;
    abort_cap = 0;
    int hit = dpll(&st);
    const char *stt = abort_cap ? "UNKNOWN" : (hit ? "HIT" : "NO");
    if (abort_cap)
      nunk++;
    else if (hit)
      nhit++;
    else
      nno++;
    if (npat <= 8 || abort_cap || hit || npat % 50 == 0) {
      printf("pat %d mask=%d nZ=%d nfree=%d nrem=%d nP=%d nodes=%llu %s\n", npat, mask, nZ, K - nZ,
             nrem, nP, (unsigned long long)nodes, stt);
      fflush(stdout);
    }
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("pats=%d HIT=%d NO=%d UNKNOWN=%d time=%.3fs\n", npat, nhit, nno, nunk,
         (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  return nunk ? 2 : (nhit ? 1 : 0);
}
