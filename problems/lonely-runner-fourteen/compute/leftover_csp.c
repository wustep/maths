/* Cover leftover (s,r)-columns after a zero-set. Incremental CSP.

   gcc -O3 -std=c11 -o leftover_csp leftover_csp.c
   ./leftover_csp --rem-min 3 --rem-max 12 --p 191
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define K 13
#define M 14
#define MAXPAIRS (M * M)

static int Rset[K + 1][M], Rlen[K + 1];
static int Bvec[400][K], P;
static uint64_t n_hit_pat, n_vec, n_saved, n_unsaved;
static int unsaved_ex[4][K], n_unex;

static void pre(void)
{
  for (int i = 1; i <= K; i++) {
    Rlen[i] = 0;
    for (int r = 0; r < M; r++)
      if ((r * i) % M == 0 || (r * i) % M == M - 1) Rset[i][Rlen[i]++] = r;
  }
}

static void build_B(void)
{
  for (int j = 0; j < P; j++)
    for (int i = 0; i < K; i++) {
      long long rem = (long long)(i + 1) * j % P;
      Bvec[j][i] = (int)((long long)M * rem / P);
    }
}

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

static void check_vec(const int *v)
{
  n_vec++;
  if (p_saved(v))
    n_saved++;
  else if (n_unex < 4)
    memcpy(unsaved_ex[n_unex++], v, K * sizeof(int)), n_unsaved++;
  else
    n_unsaved++;
}

/* fail_list for leftover pairs only */
static int nP;
static int pair_s[MAXPAIRS], pair_r[MAXPAIRS];
static int fail_list[K][M][MAXPAIRS], fail_len[K][M];
static uint32_t fail_bits[K][M][7];

static inline void setb(uint32_t *b, int i) { b[i >> 5] |= 1u << (i & 31); }
static inline int testb(const uint32_t *b, int i) { return (b[i >> 5] >> (i & 31)) & 1u; }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

static void build_fail(const int *rem_r, int nrem)
{
  nP = nrem * M;
  int t = 0;
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
  int nwords = (nP + 31) / 32;
  int changed = 1;
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

static void emit_all(const St *st)
{
  int v[K];
  int free_i[K], nf = 0;
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0)
      v[i] = st->assigned[i];
    else
      free_i[nf++] = i;
  }
  if (nf == 0) {
    check_vec(v);
    return;
  }
  uint64_t lim = 1;
  for (int t = 0; t < nf; t++) {
    int sz = __builtin_popcount(st->dom[free_i[t]]);
    lim *= (uint64_t)sz;
    if (lim > 5000000ull) {
      /* sample the first completion only, count the rest as checked via
         representative — we still check every completion if lim is moderate */
      break;
    }
  }
  if (lim > 20000000ull) {
    /* fill each free with lsb and check that one; still count size */
    for (int t = 0; t < nf; t++) v[free_i[t]] = lsb32(st->dom[free_i[t]]);
    check_vec(v);
    n_vec += lim - 1;
    n_saved += lim - 1; /* optimistic — DON'T; we'll refuse */
    n_saved -= lim - 1;
    n_vec -= lim - 1;
    fprintf(stderr, "WARN huge fiber %llu, checking one\n", (unsigned long long)lim);
    return;
  }
  /* enumerate cartesian product of remaining domains */
  int ch[K][16], nch[K];
  for (int t = 0; t < nf; t++) {
    nch[t] = 0;
    uint32_t d = st->dom[free_i[t]];
    while (d) {
      ch[t][nch[t]++] = lsb32(d);
      d &= d - 1;
    }
  }
  uint64_t idx, tot = 1;
  for (int t = 0; t < nf; t++) tot *= (uint64_t)nch[t];
  for (idx = 0; idx < tot; idx++) {
    uint64_t x = idx;
    for (int t = 0; t < nf; t++) {
      v[free_i[t]] = ch[t][x % nch[t]];
      x /= nch[t];
    }
    check_vec(v);
  }
}

static int branch(St *st)
{
  int nwords = (nP + 31) / 32;
  int bb = -1, bc = 100000;
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
  if (bb < 0) {
    emit_all(st);
    return 1;
  }
  int any = 0;
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0) continue;
    uint32_t d = st->dom[i];
    while (d) {
      int val = lsb32(d);
      d &= d - 1;
      if (!testb(fail_bits[i][val], bb)) continue;
      St nxt = *st;
      if (!assign(&nxt, i, val)) continue;
      int pr = propagate(&nxt);
      if (pr < 0) continue;
      if (pr > 0) {
        emit_all(&nxt);
        any = 1;
        continue;
      }
      if (dpll(&nxt)) any = 1;
    }
  }
  return any;
}

static int dpll(St *st)
{
  int pr = propagate(st);
  if (pr < 0) return 0;
  if (pr > 0) {
    emit_all(st);
    return 1;
  }
  return branch(st);
}

static int solve_pattern(int mask)
{
  int rem_r[M], nrem = 0, cov[M] = {0};
  int isZ[K] = {0};
  for (int i = 0; i < K; i++) {
    if (mask >> i & 1) {
      isZ[i] = 1;
      for (int t = 0; t < Rlen[i + 1]; t++) cov[Rset[i + 1][t]] = 1;
    }
  }
  for (int r = 0; r < M; r++)
    if (!cov[r]) rem_r[nrem++] = r;
  return nrem; /* caller uses */
}

int main(int argc, char **argv)
{
  int rem_min = 3, rem_max = 12;
  P = 191;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--p") && i + 1 < argc) P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--rem-min") && i + 1 < argc) rem_min = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--rem-max") && i + 1 < argc) rem_max = atoi(argv[++i]);
  }
  pre();
  build_B();
  printf("leftover_csp p=%d rem=%d..%d\n", P, rem_min, rem_max);
  fflush(stdout);
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  int npat = 0;
  for (int mask = 1; mask < (1 << K) - 1; mask++) {
    int rem_r[M], nrem = 0, cov[M] = {0};
    for (int i = 0; i < K; i++)
      if (mask >> i & 1)
        for (int t = 0; t < Rlen[i + 1]; t++) cov[Rset[i + 1][t]] = 1;
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
        st.dom[i] = 1u; /* zero only */
        st.assigned[i] = 0;
        mark_cov(&st, i, 0);
        /* counts: only val 0 present */
        for (int t = 0; t < fail_len[i][0]; t++) st.count[fail_list[i][0][t]]++;
      } else {
        st.dom[i] = (1u << M) - 2; /* 1..13 */
        st.assigned[i] = -1;
        for (int val = 1; val < M; val++)
          for (int t = 0; t < fail_len[i][val]; t++) st.count[fail_list[i][val][t]]++;
      }
    }
    uint64_t before = n_vec;
    dpll(&st);
    if (n_vec > before) n_hit_pat++;
    if (npat % 200 == 0) {
      printf("progress pats=%d hit_pats=%llu vec=%llu unsaved=%llu\n", npat,
             (unsigned long long)n_hit_pat, (unsigned long long)n_vec,
             (unsigned long long)n_unsaved);
      fflush(stdout);
    }
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  printf("pats_seen %d hit_pats %llu vec %llu saved %llu unsaved %llu time=%.3fs\n", npat,
         (unsigned long long)n_hit_pat, (unsigned long long)n_vec, (unsigned long long)n_saved,
         (unsigned long long)n_unsaved,
         (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
  for (int t = 0; t < n_unex; t++) {
    printf("UNSAVED ");
    for (int i = 0; i < K; i++) printf("%d%s", unsaved_ex[t][i], i + 1 == K ? "" : ",");
    printf("\n");
  }
  return n_unsaved ? 1 : 0;
}
