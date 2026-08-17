/* Exact search for ST26-style (s,r) witnesses on the (1,...,k) fiber.

   Work in Z/mZ with m = k+1. A vector v in (Z/mZ)^k is *saved* if some
   s,r in Z/mZ satisfy

       (s * v_i + r * i) mod m  ∈ {1, 2, ..., m-2}    for every i=1..k.

   N_k is the set of v that are not identically 0 and have at least one
   zero coordinate. ST26 Proposition 4.1 proves every v in N_k is saved
   when m is an odd prime, by a polynomial identity in F_m. The lonely-
   runner application (their Lemma 4.2 and Proposition 4.4) only needs
   the finite statement, not the field proof.

   This program exhausts N_k and either emits a saved-witness table
   checksum or an unsaved obstruction. Two search modes:

     brute   — enumerate every v in {0,...,m-1}^k (small k)
     dpll    — covering-CSP on the (s,r)-torus (k=13)

   Compile: gcc -O3 -std=c11 -pthread -o ap_fiber ap_fiber.c
*/

#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <inttypes.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXK 16
#define MAXM 17
#define MAXPAIRS (MAXM * MAXM) /* 289 */
#define NWORDS 5               /* 5 * 64 = 320 > 289 */

typedef struct {
  uint64_t w[NWORDS];
} Mask;

static inline void mask_clear(Mask *m) { memset(m->w, 0, sizeof(m->w)); }
static inline void mask_fill(Mask *m, int nbits)
{
  mask_clear(m);
  int full = nbits / 64;
  int rem = nbits % 64;
  for (int i = 0; i < full; i++) m->w[i] = ~UINT64_C(0);
  if (rem) m->w[full] = (UINT64_C(1) << rem) - 1;
}
static inline void mask_or(Mask *a, const Mask *b)
{
  for (int i = 0; i < NWORDS; i++) a->w[i] |= b->w[i];
}
static inline void mask_and(Mask *a, const Mask *b)
{
  for (int i = 0; i < NWORDS; i++) a->w[i] &= b->w[i];
}
static inline bool mask_eq(const Mask *a, const Mask *b)
{
  for (int i = 0; i < NWORDS; i++)
    if (a->w[i] != b->w[i]) return false;
  return true;
}
static inline bool mask_is_zero(const Mask *a)
{
  for (int i = 0; i < NWORDS; i++)
    if (a->w[i]) return false;
  return true;
}
static inline void mask_set(Mask *m, int b) { m->w[b >> 6] |= UINT64_C(1) << (b & 63); }
static inline bool mask_test(const Mask *m, int b)
{
  return (m->w[b >> 6] >> (b & 63)) & 1u;
}
static inline int mask_pop(const Mask *m)
{
  int c = 0;
  for (int i = 0; i < NWORDS; i++) c += __builtin_popcountll(m->w[i]);
  return c;
}
static inline void mask_not_and(Mask *out, const Mask *a, const Mask *full)
{
  for (int i = 0; i < NWORDS; i++) out->w[i] = (~a->w[i]) & full->w[i];
}

/* fail_mask[i][val] = pairs (s,r) with (s*val + r*(i+1)) mod m in {0,m-1}.
   Index i is 0-based, corresponding to runner speed i+1. */
static int K, M, NPAIRS;
static Mask fail_mask[MAXK][MAXM];
static Mask ALL;
static int units_only;
static int unit[MAXM];

static void precompute(void)
{
  NPAIRS = M * M;
  mask_fill(&ALL, NPAIRS);
  for (int a = 0; a < M; a++) {
    int g = a;
    int b = M;
    while (b) {
      int t = a % b;
      /* gcd via locals */
      (void)t;
      break;
    }
  }
  for (int a = 0; a < M; a++) {
    int x = a, y = M, t;
    while (y) {
      t = x % y;
      x = y;
      y = t;
    }
    unit[a] = (x == 1);
  }
  for (int i = 0; i < K; i++) {
    int idx = i + 1; /* the coordinate multiplier */
    for (int val = 0; val < M; val++) {
      mask_clear(&fail_mask[i][val]);
      for (int s = 0; s < M; s++) {
        if (units_only && !unit[s]) continue;
        for (int r = 0; r < M; r++) {
          if (units_only && !unit[r]) continue;
          int x = (s * val + r * idx) % M;
          if (x == 0 || x == M - 1) mask_set(&fail_mask[i][val], s * M + r);
        }
      }
    }
  }
  if (units_only) {
    /* ALL is only the unit-unit pairs */
    mask_clear(&ALL);
    for (int s = 0; s < M; s++)
      if (unit[s])
        for (int r = 0; r < M; r++)
          if (unit[r]) mask_set(&ALL, s * M + r);
  }
}

static bool saved_by(const int *v, int *outs, int *outr)
{
  Mask cov;
  mask_clear(&cov);
  for (int i = 0; i < K; i++) mask_or(&cov, &fail_mask[i][v[i]]);
  /* saved iff some pair is *not* failed */
  Mask unfailed;
  mask_not_and(&unfailed, &cov, &ALL);
  if (mask_is_zero(&unfailed)) return false;
  for (int b = 0; b < NPAIRS; b++)
    if (mask_test(&unfailed, b)) {
      if (outs) *outs = b / M;
      if (outr) *outr = b % M;
      return true;
    }
  return false;
}

/* ---------------- brute force ---------------- */

static uint64_t brute_checked, brute_saved, brute_in_Nk;
static int brute_obstruction[MAXK];
static int brute_found;

static void brute_rec(int pos, int *v, int nzero, int nzero_slots_left)
{
  if (brute_found) return;
  if (pos == K) {
    brute_checked++;
    if (nzero == 0 || nzero == K) return;
    brute_in_Nk++;
    if (saved_by(v, NULL, NULL)) {
      brute_saved++;
    } else {
      memcpy(brute_obstruction, v, K * sizeof(int));
      brute_found = 1;
    }
    return;
  }
  /* remaining coordinates after this one: K-pos-1 */
  for (int val = 0; val < M; val++) {
    int nz = nzero + (val == 0);
    /* prune: if we already have all-nonzero and no zeros left to place, we
       still must enumerate (those are not in N_k and will be skipped) */
    v[pos] = val;
    brute_rec(pos + 1, v, nz, nzero_slots_left - 1);
    if (brute_found) return;
  }
}

/* ---------------- DPLL covering search for an unsaved v in N_k ----------------
   A counterexample is a v in N_k whose fail-masks cover ALL pairs.
   Variables v[0..K-1]; domains are bitmasks of width M. */

static atomic_int dpll_found;
static int dpll_obstruction[MAXK];
static atomic_uint_fast64_t dpll_nodes;

typedef struct {
  uint32_t dom[MAXK];
  int assigned[MAXK]; /* -1 free, else value */
  int nzero_forced;   /* number of assigned zeros */
  int nfree;
  Mask covered;
} CP;

static inline int pop32(uint32_t x) { return __builtin_popcount(x); }
static inline int lsb32(uint32_t x) { return __builtin_ctz(x); }

static int propagate(CP *st)
{
  /* Unit-propagate covering of still-unfailed pairs. */
  for (;;) {
    Mask unfailed;
    mask_not_and(&unfailed, &st->covered, &ALL);
    if (mask_is_zero(&unfailed)) {
      /* fully covered: this is a counterexample if we can complete to N_k */
      return 1; /* SAT-as-obstruction, pending N_k */
    }
    int progress = 0;
    /* For each unfailed pair, collect possible (i,val) killers. */
    for (int b = 0; b < NPAIRS; b++) {
      if (!mask_test(&unfailed, b)) continue;
      int nopt = 0;
      int only_i = -1, only_val = -1;
      for (int i = 0; i < K; i++) {
        uint32_t d = st->dom[i];
        while (d) {
          int val = lsb32(d);
          d &= d - 1;
          if (mask_test(&fail_mask[i][val], b)) {
            nopt++;
            only_i = i;
            only_val = val;
            if (nopt > 1) break;
          }
        }
        if (nopt > 1) break;
      }
      if (nopt == 0) return -1; /* this pair can never fail: no obstruction down this branch */
      if (nopt == 1 && st->assigned[only_i] < 0) {
        /* force v[only_i] = only_val */
        st->assigned[only_i] = only_val;
        st->dom[only_i] = (uint32_t)1u << only_val;
        st->nfree--;
        if (only_val == 0) st->nzero_forced++;
        mask_or(&st->covered, &fail_mask[only_i][only_val]);
        progress = 1;
      }
    }
    if (!progress) return 0;
  }
}

static int dpll_rec(CP *st, int depth);

static int assign_and_rec(CP *st, int i, int val)
{
  CP nxt = *st;
  nxt.assigned[i] = val;
  nxt.dom[i] = (uint32_t)1u << val;
  nxt.nfree--;
  if (val == 0) nxt.nzero_forced++;
  mask_or(&nxt.covered, &fail_mask[i][val]);
  return dpll_rec(&nxt, 0);
}

static int dpll_rec(CP *st, int depth)
{
  (void)depth;
  if (dpll_found) return 1;
  atomic_fetch_add_explicit(&dpll_nodes, 1, memory_order_relaxed);

  int pr = propagate(st);
  if (pr < 0) return 0;
  if (pr > 0) {
    /* covered. Complete free vars arbitrarily, requiring N_k. */
    int v[MAXK];
    int nzero = st->nzero_forced;
    for (int i = 0; i < K; i++) {
      if (st->assigned[i] >= 0) {
        v[i] = st->assigned[i];
      } else {
        /* pick a remaining domain value; prefer nonzero unless we still need a zero */
        uint32_t d = st->dom[i];
        int val = -1;
        if (nzero == 0) {
          if (d & 1u) {
            val = 0;
          } else {
            /* no zero available here; pick any */
            val = lsb32(d);
          }
        } else {
          uint32_t nz = d & ~1u;
          val = nz ? lsb32(nz) : 0;
        }
        v[i] = val;
        if (val == 0) nzero++;
      }
    }
    if (nzero == 0) {
      /* try to force a zero on a free coordinate if any domain allows it */
      int ok = 0;
      for (int i = 0; i < K; i++) {
        if (st->assigned[i] < 0 && (st->dom[i] & 1u)) {
          v[i] = 0;
          nzero = 1;
          ok = 1;
          break;
        }
      }
      if (!ok) return 0; /* cannot enter N_k */
    }
    if (nzero == K) return 0; /* identically zero */
    /* verify it really is unsaved */
    if (!saved_by(v, NULL, NULL)) {
      if (!dpll_found) {
        memcpy(dpll_obstruction, v, K * sizeof(int));
        dpll_found = 1;
      }
      return 1;
    }
    return 0;
  }

  /* branch on the free variable with smallest domain */
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
  if (bi < 0) {
    /* all assigned */
    int nzero = 0;
    int v[MAXK];
    for (int i = 0; i < K; i++) {
      v[i] = st->assigned[i];
      if (v[i] == 0) nzero++;
    }
    if (nzero == 0 || nzero == K) return 0;
    if (!saved_by(v, NULL, NULL)) {
      if (!dpll_found) {
        memcpy(dpll_obstruction, v, K * sizeof(int));
        dpll_found = 1;
      }
      return 1;
    }
    return 0;
  }

  uint32_t d = st->dom[bi];
  while (d) {
    int val = lsb32(d);
    d &= d - 1;
    if (assign_and_rec(st, bi, val)) return 1;
    if (dpll_found) return 1;
  }
  return 0;
}

static void run_dpll(void)
{
  CP st;
  memset(&st, 0, sizeof(st));
  uint32_t full = (M >= 31) ? 0xffffffffu : ((1u << M) - 1u);
  for (int i = 0; i < K; i++) {
    st.dom[i] = full;
    st.assigned[i] = -1;
  }
  st.nfree = K;
  st.nzero_forced = 0;
  mask_clear(&st.covered);
  dpll_found = 0;
  dpll_nodes = 0;
  dpll_rec(&st, 0);
}

/* ---------------- witness census for independent replay ---------------- */

static uint64_t fnv1a(const int *v, int n)
{
  uint64_t h = 14695981039346656037ull;
  for (int i = 0; i < n; i++) {
    h ^= (unsigned)v[i];
    h *= 1099511628211ull;
  }
  return h;
}

static void print_vec(const int *v)
{
  fputc('[', stdout);
  for (int i = 0; i < K; i++) {
    if (i) fputc(',', stdout);
    printf("%d", v[i]);
  }
  fputc(']', stdout);
}

static void usage(const char *argv0)
{
  fprintf(stderr,
          "usage: %s --k K [--units] [--brute] [--dpll] [--witnesses N]\n"
          "  --units     restrict (s,r) to (Z/mZ)*  (ST26 Prop 4.1)\n"
          "  --brute     full enumeration of (Z/mZ)^k\n"
          "  --dpll      covering-CSP search for an unsaved v in N_k\n"
          "  --witnesses print (s,r) for N random N_k vectors\n",
          argv0);
}

int main(int argc, char **argv)
{
  K = 13;
  int do_brute = 0, do_dpll = 1, nwit = 0;
  units_only = 0;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--k") && i + 1 < argc) {
      K = atoi(argv[++i]);
    } else if (!strcmp(argv[i], "--units")) {
      units_only = 1;
    } else if (!strcmp(argv[i], "--brute")) {
      do_brute = 1;
      do_dpll = 0;
    } else if (!strcmp(argv[i], "--dpll")) {
      do_dpll = 1;
    } else if (!strcmp(argv[i], "--witnesses") && i + 1 < argc) {
      nwit = atoi(argv[++i]);
    } else if (!strcmp(argv[i], "--help")) {
      usage(argv[0]);
      return 0;
    } else {
      usage(argv[0]);
      return 2;
    }
  }
  if (K < 2 || K > MAXK) {
    fprintf(stderr, "k out of range\n");
    return 2;
  }
  M = K + 1;
  precompute();

  printf("ap_fiber k=%d m=%d pairs=%d units_only=%d\n", K, M, mask_pop(&ALL), units_only);
  fflush(stdout);

  if (nwit) {
    /* deterministic LCG sample of N_k */
    uint64_t seed = 0xC0FFEE1234ull + (uint64_t)K * 17 + (unsigned)units_only;
    int ok = 0;
    for (int t = 0; t < nwit; t++) {
      int v[MAXK];
      int nzero;
      do {
        nzero = 0;
        for (int i = 0; i < K; i++) {
          seed = seed * 6364136223846793005ull + 1;
          v[i] = (int)((seed >> 33) % (unsigned)M);
          if (v[i] == 0) nzero++;
        }
      } while (nzero == 0 || nzero == K);
      int s, r;
      if (saved_by(v, &s, &r)) {
        ok++;
        if (t < 8) {
          printf("sample ");
          print_vec(v);
          printf(" -> s=%d r=%d\n", s, r);
        }
      } else {
        printf("UNSAVED sample ");
        print_vec(v);
        printf("\n");
        return 1;
      }
    }
    printf("witness_samples %d/%d ok\n", ok, nwit);
  }

  if (do_brute) {
    double lim = 1;
    for (int i = 0; i < K; i++) lim *= M;
    if (lim > 3e8) {
      fprintf(stderr, "brute refused: m^k = %.3g\n", lim);
      return 2;
    }
    int v[MAXK];
    brute_checked = brute_saved = brute_in_Nk = 0;
    brute_found = 0;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    brute_rec(0, v, 0, K);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("brute checked=%" PRIu64 " N_k=%" PRIu64 " saved=%" PRIu64 " time=%.3fs\n", brute_checked,
           brute_in_Nk, brute_saved, sec);
    if (brute_found) {
      printf("OBSTRUCTION ");
      print_vec(brute_obstruction);
      printf(" hash=%016" PRIx64 "\n", fnv1a(brute_obstruction, K));
      return 1;
    }
    printf("NO_OBSTRUCTION brute N_k=%" PRIu64 "\n", brute_in_Nk);
  }

  if (do_dpll) {
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    run_dpll();
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("dpll nodes=%" PRIu64 " time=%.3fs\n", (uint64_t)dpll_nodes, sec);
    if (dpll_found) {
      printf("OBSTRUCTION ");
      print_vec(dpll_obstruction);
      printf(" hash=%016" PRIx64 "\n", fnv1a(dpll_obstruction, K));
      int s, r;
      printf("verify_unsaved=%d\n", saved_by(dpll_obstruction, &s, &r) ? 0 : 1);
      return 1;
    }
    printf("NO_OBSTRUCTION dpll\n");
  }
  return 0;
}
