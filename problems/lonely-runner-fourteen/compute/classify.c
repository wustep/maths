/* Classify p-independent obstructions in N_k for m=k+1=14.

   For every nonempty proper zero-set Z, decide whether some assignment
   of the complementary coordinates (nonzero, or anything if Z already
   covers) makes v unsaved. Incremental covering DPLL.
*/
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define K 13
#define M 14
#define NPAIRS (M * M)
#define NWORDS 4

typedef struct {
  uint64_t w[NWORDS];
} Mask;

static Mask FAIL[K][M], ALL;

static inline void mc(Mask *m) { memset(m->w, 0, sizeof(m->w)); }
static inline void mor(Mask *a, const Mask *b)
{
  for (int i = 0; i < NWORDS; i++) a->w[i] |= b->w[i];
}
static inline void mset(Mask *m, int b) { m->w[b >> 6] |= UINT64_C(1) << (b & 63); }
static inline int mtest(const Mask *m, int b) { return (int)((m->w[b >> 6] >> (b & 63)) & 1u); }
static inline int mzero(const Mask *a)
{
  return !(a->w[0] | a->w[1] | a->w[2] | a->w[3]);
}
static inline int meq(const Mask *a, const Mask *b)
{
  return a->w[0] == b->w[0] && a->w[1] == b->w[1] && a->w[2] == b->w[2] && a->w[3] == b->w[3];
}
static inline void mnotand(Mask *out, const Mask *a)
{
  for (int i = 0; i < NWORDS; i++) out->w[i] = (~a->w[i]) & ALL.w[i];
}

static void pre(void)
{
  mc(&ALL);
  for (int b = 0; b < NPAIRS; b++) mset(&ALL, b);
  for (int i = 0; i < K; i++)
    for (int val = 0; val < M; val++) {
      mc(&FAIL[i][val]);
      for (int s = 0; s < M; s++)
        for (int r = 0; r < M; r++) {
          int x = (s * val + r * (i + 1)) % M;
          if (x == 0 || x == M - 1) mset(&FAIL[i][val], s * M + r);
        }
    }
}

static inline int pop32(uint32_t x) { return __builtin_popcount(x); }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

typedef struct {
  uint32_t dom[K];
  int assigned[K];
  Mask covered;
} CP;

static int prop(CP *st)
{
  for (int it = 0; it < K + 3; it++) {
    Mask unf;
    mnotand(&unf, &st->covered);
    if (mzero(&unf)) return 1;
    int fi = -1, fv = -1, bad = 0;
    for (int b = 0; b < NPAIRS; b++) {
      if (!mtest(&unf, b)) continue;
      int nopt = 0, oi = -1, ov = -1;
      for (int i = 0; i < K; i++) {
        uint32_t d = st->dom[i];
        while (d) {
          int val = lsb32(d);
          d &= d - 1;
          if (mtest(&FAIL[i][val], b)) {
            nopt++;
            oi = i;
            ov = val;
            if (nopt > 1) break;
          }
        }
        if (nopt > 1) break;
      }
      if (nopt == 0) {
        bad = 1;
        break;
      }
      if (nopt == 1 && st->assigned[oi] < 0) {
        fi = oi;
        fv = ov;
        break;
      }
    }
    if (bad) return -1;
    if (fi < 0) return 0;
    st->assigned[fi] = fv;
    st->dom[fi] = 1u << fv;
    mor(&st->covered, &FAIL[fi][fv]);
  }
  return 0;
}

static int dpll(CP *st)
{
  int pr = prop(st);
  if (pr < 0) return 0;
  if (pr > 0) return 1;
  int bi = -1, bsz = 99;
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0) continue;
    int sz = pop32(st->dom[i]);
    if (sz == 0) return 0;
    if (sz < bsz) {
      bsz = sz;
      bi = i;
    }
  }
  if (bi < 0) return 1;
  uint32_t d = st->dom[bi];
  while (d) {
    int val = lsb32(d);
    d &= d - 1;
    CP nxt = *st;
    nxt.assigned[bi] = val;
    nxt.dom[bi] = 1u << val;
    mor(&nxt.covered, &FAIL[bi][val]);
    if (dpll(&nxt)) return 1;
  }
  return 0;
}

int main(void)
{
  pre();
  int n_full = 0, n_mixed = 0, n_empty = 0;
  unsigned long long n_vec = 0;
  int mixed_ex[8][K];
  int n_mex = 0;
  int contain_odds = 0;
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);

  for (int mask = 1; mask < (1 << K) - 1; mask++) {
    Mask zcov;
    mc(&zcov);
    int nfree = 0;
    int has_all_odds = 1;
    for (int i = 0; i < K; i++) {
      if (mask >> i & 1)
        mor(&zcov, &FAIL[i][0]);
      else
        nfree++;
      if (((i + 1) & 1) && !(mask >> i & 1)) has_all_odds = 0;
    }
    if (meq(&zcov, &ALL)) {
      n_full++;
      unsigned long long add = 1;
      for (int t = 0; t < nfree; t++) add *= 13ull;
      n_vec += add;
      if (has_all_odds) contain_odds++;
      continue;
    }
    CP st;
    memset(&st, 0, sizeof(st));
    for (int i = 0; i < K; i++) {
      if (mask >> i & 1) {
        st.assigned[i] = 0;
        st.dom[i] = 1u;
        mor(&st.covered, &FAIL[i][0]);
      } else {
        st.assigned[i] = -1;
        st.dom[i] = (1u << M) - 2; /* 1..13 */
      }
    }
    if (dpll(&st)) {
      n_mixed++;
      if (n_mex < 8) {
        for (int i = 0; i < K; i++) mixed_ex[n_mex][i] = st.assigned[i];
        n_mex++;
      }
    } else {
      n_empty++;
    }
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  double sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
  printf("Nk_zero_patterns %d\n", (1 << K) - 2);
  printf("zeros_alone_cover %d\n", n_full);
  printf("those_containing_all_odd_speed_zeros %d\n", contain_odds);
  printf("mixed_obstruction_patterns %d\n", n_mixed);
  printf("no_obstruction_patterns %d\n", n_empty);
  printf("zeros_cover_vectors %llu\n", n_vec);
  printf("time %.3fs\n", sec);
  for (int t = 0; t < n_mex; t++) {
    printf("mixed ");
    for (int i = 0; i < K; i++) printf("%d%s", mixed_ex[t][i], i + 1 == K ? "" : ",");
    printf("\n");
  }
  return n_mixed ? 1 : 0;
}
