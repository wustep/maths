#!/usr/bin/env python3
"""schema.py -- the exact family behind every T2(13,p) failure probe.c finds.

Every witness the alphabet probe returns has the same shape: two coordinates
equal to 1, the rest 0.  That shape has a closed form.

Let T = {a,b}, v = e_a + e_b, Z = {1,...,k} \\ T.  For s = 0 the pair (0,j) is
hit by any coordinate with B_i^(j) in {0, m-1}, which always exists.  For
s != 0, a coordinate i in Z (value 0) hits (s,j) iff B_i^(j) in {0, m-1}, i.e.
iff || i*j/p || < 1/m, independently of s; and a coordinate i in T (value 1)
hits only the two values s = -B_i, -B_i-1.  So if some j has no i in Z with
|| i*j/p || < 1/m, the two coordinates of T cover at most 4 of the m-1 = 13
nonzero s, and v is saved.  Hence, for |T| <= 6,

    v = e_T is UNSAVED at p  <=>  no j in Z_p has || i*j/p || >= 1/m for
                                  every i in Z,
    i.e. the speed set Z has no witness time on the grid (1/p)Z at gap 1/m.

So T2(k,p) FAILS whenever some pair {a,b} leaves the other k-2 speeds without
a grid witness.  G(Z) = { t : ||i t|| >= 1/m for all i in Z } is a finite union
of closed intervals with endpoints over D = m*lcm(1..k), computed here exactly,
and the question for each p is whether any of them contains a multiple of 1/p.

This decides the family for ALL p at once -- no per-p search.
"""
import argparse
from itertools import combinations
from math import gcd


def lcm_upto(k):
    L = 1
    for i in range(1, k + 1):
        L = L * i // gcd(L, i)
    return L


def good_set(k, Z):
    """G(Z) as a list of closed intervals [lo,hi] on the circle, over D.

    Intervals are kept on [0,D) and may wrap; a wrapping component is stored
    as (lo, hi) with hi > D, meaning [lo,D) followed by [0, hi-D].
    """
    m, L = k + 1, lcm_upto(k)
    D = m * L
    bad = []                       # open bad arcs, split at the wrap
    for i in Z:
        step, half = D // i, L // i          # centre spacing, half-width D/(m*i)
        for n in range(i):
            lo, hi = n * step - half, n * step + half
            if lo < 0:
                bad.append((0, hi)); bad.append((lo + D, D))
            elif hi > D:
                bad.append((lo, D)); bad.append((0, hi - D))
            else:
                bad.append((lo, hi))
    bad.sort()
    good, cur = [], 0
    for lo, hi in bad:
        if lo > cur:
            good.append((cur, lo))
        cur = max(cur, hi)
    if cur < D:
        good.append((cur, D))
    # join a component touching D to one touching 0
    if len(good) > 1 and good[0][0] == 0 and good[-1][1] == D:
        good = good[1:-1] + [(good[-1][0], good[0][1] + D)]
    elif len(good) == 1 and good[0] == (0, D):
        pass
    return D, good


def has_grid_point(D, good, p):
    """does some multiple of 1/p lie in G? (closed intervals)"""
    for lo, hi in good:
        # exists integer j with lo/D <= j/p <= hi/D  <=>  ceil(lo*p/D) <= floor(hi*p/D)
        if -(-lo * p // D) <= hi * p // D:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=13)
    ap.add_argument("--pmax", type=int, default=4000)
    ap.add_argument("--list", action="store_true", help="print every failing p")
    a = ap.parse_args()
    k = a.k

    fails = {}
    for T in combinations(range(1, k + 1), 2):
        Z = [i for i in range(1, k + 1) if i not in T]
        D, good = good_set(k, Z)
        if not good:
            print("pair", T, "-> G(Z) empty: v = e_T is unsaved at EVERY p")
            continue
        longest = max(hi - lo for lo, hi in good)
        bad_p = [p for p in range(2, a.pmax + 1) if not has_grid_point(D, good, p)]
        fails[T] = (bad_p, longest, D)

    allp = sorted(set(p for v in fails.values() for p in v[0]))
    print("k=%d  family v = e_a + e_b  (two coordinates 1, the rest 0)" % k)
    print("D = %d = %d*lcm(1..%d)" % (D, k + 1, k))
    worst = max(fails.items(), key=lambda kv: (max(kv[1][0]) if kv[1][0] else 0))
    print()
    print("longest interval of G(Z) over the %d pairs:" % len(fails))
    lo_pair = min(fails.items(), key=lambda kv: kv[1][1])
    print("  shortest longest-interval: pair %s, %d/%d = 1/%.2f"
          % (str(lo_pair[0]), lo_pair[1][1], D, D / lo_pair[1][1]))
    print("  so every p > %.2f has a grid witness for every pair"
          % (D / lo_pair[1][1]))
    print()
    print("p <= %d for which SOME pair has no grid witness (T2(%d,p) FAILS):"
          % (a.pmax, k))
    print(" ", allp)
    print("largest such p:", max(allp))
    print("pair achieving it:", worst[0], " (its failing p:", worst[1][0], ")")
    print()
    pr = [p for p in allp if p > 1 and all(p % d for d in range(2, int(p ** .5) + 1))]
    print("primes among them:", pr)
    print("largest failing PRIME from this family:", max(pr))
    if a.list:
        for T in sorted(fails):
            print("  pair %-8s longest=%d/%d  fails at %s"
                  % (str(T), fails[T][1], D, fails[T][0]))


if __name__ == "__main__":
    main()
