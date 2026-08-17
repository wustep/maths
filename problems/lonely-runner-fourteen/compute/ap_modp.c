/* p-dependent salvage of the (1,...,k) fiber.

   For a prime p, a vector v in (Z/mZ)^k, m=k+1, is *p-saved* if some
   s in Z/mZ and some residue j mod p satisfy

       (s * v_i + B_i(j)) mod m  ∈ {1,...,m-2}   for all i=1..k

   where B_i(j) = floor( m * ((i*j) mod p) / p ) = r_k(j/p)_i.

   This is exactly the discrete condition in ST26 Proposition 4.4, without
   passing through the inclusion r_k(1/m Z) ⊆ r_k(1/p Z). If every v in
   N_k is p-saved, and the all-zero / all-nonzero cases are handled as in
   that proposition, then every lift in π_{m p → p}^{-1}(1,...,k) is
   (k,p,m)-proper, so (1,...,k) is eventually (k,p)-proper.

   Compile: gcc -O3 -std=c11 -o ap_modp ap_modp.c
*/

#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK 16
#define MAXM 17
#define MAXP 400
#define MAXPAIRS (MAXM * MAXP) /* 17*400=6800 */
#define NWORDS 110             /* 110*64=7040 */

typedef struct {
  uint64_t w[NWORDS];
} Mask;

static int K, M, P, NPAIRS, nB;
static int Bvec[MAXP][MAXK];
static Mask fail_mask[MAXK][MAXM];
static Mask ALL;
static uint32_t full_dom;

static inline void mask_clear(Mask *m) { memset(m->w, 0, sizeof(m->w)); }
static inline void mask_or(Mask *a, const Mask *b)
{
  for (int i = 0; i < NWORDS; i++) a->w[i] |= b->w[i];
}
static inline int mask_pop(const Mask *m)
{
  int c = 0;
  for (int i = 0; i < NWORDS; i++) c += __builtin_popcountll(m->w[i]);
  return c;
}
static inline void mask_set(Mask *m, int b) { m->w[b >> 6] |= UINT64_C(1) << (b & 63); }
static inline int mask_test(const Mask *m, int b)
{
  return (int)((m->w[b >> 6] >> (b & 63)) & 1u);
}
static inline void mask_not_and(Mask *out, const Mask *a)
{
  for (int i = 0; i < NWORDS; i++) out->w[i] = (~a->w[i]) & ALL.w[i];
}
static inline int mask_is_zero(const Mask *a)
{
  for (int i = 0; i < NWORDS; i++)
    if (a->w[i]) return 0;
  return 1;
}

static void build_B(void)
{
  nB = P;
  for (int j = 0; j < P; j++)
    for (int i = 0; i < K; i++) {
      long long rem = (long long)(i + 1) * j % P;
      Bvec[j][i] = (int)((long long)M * rem / P);
    }
  NPAIRS = M * nB;
  mask_clear(&ALL);
  for (int b = 0; b < NPAIRS; b++) mask_set(&ALL, b);

  for (int i = 0; i < K; i++)
    for (int val = 0; val < M; val++) {
      mask_clear(&fail_mask[i][val]);
      for (int s = 0; s < M; s++)
        for (int j = 0; j < nB; j++) {
          int x = (s * val + Bvec[j][i]) % M;
          if (x == 0 || x == M - 1) mask_set(&fail_mask[i][val], s * nB + j);
        }
    }
  full_dom = (M >= 32) ? 0xffffffffu : ((1u << M) - 1u);
}

static int saved_by(const int *v, int *outs, int *outj)
{
  Mask cov;
  mask_clear(&cov);
  for (int i = 0; i < K; i++) mask_or(&cov, &fail_mask[i][v[i]]);
  Mask unf;
  mask_not_and(&unf, &cov);
  if (mask_is_zero(&unf)) return 0;
  if (outs) {
    for (int b = 0; b < NPAIRS; b++)
      if (mask_test(&unf, b)) {
        *outs = b / nB;
        *outj = b % nB;
        return 1;
      }
  }
  return 1;
}

/* Incremental DPLL. */
static uint64_t nodes;
static int found;
static int obst[MAXK];

typedef struct {
  uint32_t dom[MAXK];
  int assigned[MAXK];
  int nfree;
  int nzero;
  Mask covered;
} CP;

static inline int pop32(uint32_t x) { return __builtin_popcount(x); }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

/* For each unfailed pair, count remaining killers. Force uniques.
   Return -1 contradiction (some pair uncoverable), 1 fully covered, 0 otherwise. */
static int propagate(CP *st)
{
  for (int iter = 0; iter < K + 2; iter++) {
    Mask unf;
    mask_not_and(&unf, &st->covered);
    if (mask_is_zero(&unf)) return 1;
    int progress = 0;
    int forced_i = -1, forced_val = -1;
    int saw_uncoverable = 0;
    for (int b = 0; b < NPAIRS; b++) {
      if (!mask_test(&unf, b)) continue;
      int nopt = 0, oi = -1, ov = -1;
      for (int i = 0; i < K; i++) {
        uint32_t d = st->dom[i];
        while (d) {
          int val = lsb32(d);
          d &= d - 1;
          if (mask_test(&fail_mask[i][val], b)) {
            nopt++;
            oi = i;
            ov = val;
            if (nopt > 1) break;
          }
        }
        if (nopt > 1) break;
      }
      if (nopt == 0) {
        saw_uncoverable = 1;
        break;
      }
      if (nopt == 1 && st->assigned[oi] < 0) {
        forced_i = oi;
        forced_val = ov;
        break;
      }
    }
    if (saw_uncoverable) return -1;
    if (forced_i < 0) return 0;
    st->assigned[forced_i] = forced_val;
    st->dom[forced_i] = 1u << forced_val;
    st->nfree--;
    if (forced_val == 0) st->nzero++;
    mask_or(&st->covered, &fail_mask[forced_i][forced_val]);
    progress = 1;
    (void)progress;
  }
  return 0;
}

static int dpll(CP *st);

static int assign_val(const CP *st, int i, int val)
{
  CP nxt = *st;
  nxt.assigned[i] = val;
  nxt.dom[i] = 1u << val;
  nxt.nfree--;
  if (val == 0) nxt.nzero++;
  mask_or(&nxt.covered, &fail_mask[i][val]);
  return dpll(&nxt);
}

static int complete_Nk(const CP *st)
{
  int v[MAXK];
  int nzero = st->nzero;
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0) {
      v[i] = st->assigned[i];
    } else {
      uint32_t d = st->dom[i];
      int val;
      if (nzero == 0 && (d & 1u))
        val = 0;
      else {
        uint32_t nz = d & ~1u;
        val = nz ? lsb32(nz) : 0;
      }
      v[i] = val;
      if (val == 0) nzero++;
    }
  }
  if (nzero == 0) {
    int ok = 0;
    for (int i = 0; i < K; i++)
      if (st->assigned[i] < 0 && (st->dom[i] & 1u)) {
        v[i] = 0;
        nzero = 1;
        ok = 1;
        break;
      }
    if (!ok) return 0;
  }
  if (nzero == K) return 0;
  if (!saved_by(v, NULL, NULL)) {
    memcpy(obst, v, K * sizeof(int));
    found = 1;
    return 1;
  }
  return 0;
}

static int dpll(CP *st)
{
  if (found) return 1;
  nodes++;
  int pr = propagate(st);
  if (pr < 0) return 0;
  if (pr > 0) return complete_Nk(st);

  int bi = -1, bsz = 100;
  for (int i = 0; i < K; i++) {
    if (st->assigned[i] >= 0) continue;
    int sz = pop32(st->dom[i]);
    if (sz == 0) return 0;
    if (sz < bsz) {
      bsz = sz;
      bi = i;
    }
  }
  if (bi < 0) return complete_Nk(st);

  uint32_t d = st->dom[bi];
  /* try 0 first so N_k is entered early if it helps? For obstruction search,
     zeros fail more pairs, so try 0 first. */
  if (d & 1u) {
    if (assign_val(st, bi, 0)) return 1;
    d &= ~1u;
  }
  while (d) {
    int val = lsb32(d);
    d &= d - 1;
    if (assign_val(st, bi, val)) return 1;
  }
  return 0;
}

static void print_vec(const int *v)
{
  putchar('[');
  for (int i = 0; i < K; i++) {
    if (i) putchar(',');
    printf("%d", v[i]);
  }
  putchar(']');
}

int main(int argc, char **argv)
{
  K = 13;
  P = 191;
  int samples = 0;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k") && i + 1 < argc)
      K = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--p") && i + 1 < argc)
      P = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--samples") && i + 1 < argc)
      samples = atoi(argv[++i]);
    else {
      fprintf(stderr, "usage: %s --k K --p P [--samples N]\n", argv[0]);
      return 2;
    }
  }
  M = K + 1;
  if (K < 2 || K > MAXK || P < 3 || P > MAXP) {
    fprintf(stderr, "range error\n");
    return 2;
  }
  build_B();
  printf("ap_modp k=%d m=%d p=%d nB=%d pairs=%d\n", K, M, P, nB, NPAIRS);
  fflush(stdout);

  if (samples) {
    uint64_t seed = 0x9E3779B97F4A7C15ull ^ ((uint64_t)P << 8) ^ (unsigned)K;
    int ok = 0;
    for (int t = 0; t < samples; t++) {
      int v[MAXK], nzero;
      do {
        nzero = 0;
        for (int i = 0; i < K; i++) {
          seed = seed * 6364136223846793005ull + 1;
          v[i] = (int)((seed >> 33) % (unsigned)M);
          if (v[i] == 0) nzero++;
        }
      } while (nzero == 0 || nzero == K);
      int s, j;
      if (!saved_by(v, &s, &j)) {
        printf("UNSAVED sample ");
        print_vec(v);
        printf("\n");
        return 1;
      }
      ok++;
      if (t < 5) {
        printf("sample ");
        print_vec(v);
        printf(" -> s=%d j=%d\n", s, j);
      }
    }
    printf("samples %d/%d p-saved\n", ok, samples);
  }

  CP st;
  memset(&st, 0, sizeof(st));
  for (int i = 0; i < K; i++) {
    st.dom[i] = full_dom;
    st.assigned[i] = -1;
  }
  st.nfree = K;
  mask_clear(&st.covered);
  found = 0;
  nodes = 0;
  struct timespec t0, t1;
  clock_gettime(CLOCK_MONOTONIC, &t0);
  dpll(&st);
  clock_gettime(CLOCK_MONOTONIC, &t1);
  double sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
  printf("dpll nodes=%llu time=%.3fs\n", (unsigned long long)nodes, sec);
  if (found) {
    printf("OBSTRUCTION ");
    print_vec(obst);
    printf("\n");
    int s, j;
    printf("verify_unsaved=%d\n", saved_by(obst, &s, &j) ? 0 : 1);
    return 1;
  }
  printf("NO_OBSTRUCTION p-saved every N_k\n");
  return 0;
}
