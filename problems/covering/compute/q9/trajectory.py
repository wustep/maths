#!/usr/bin/env python3
"""The documented trajectory of upper bounds on l_2(10,2), re-derived.

Every number printed here is either recomputed from an explicit column set in
this repository or taken from a cited formula in the literature; nothing is
copied out of a table.  Sources:

  phi(2t) = 27*2^(t-4) - 1, t >= 4   Davydov-Drozhzhina-Labinskaya, ACCT-3 1992
                                     p.53, and IEEE-IT 40(4) 1270-1279 (1994),
                                     Example 3.1; Cohen-Honkala-Litsyn-Lobstein,
                                     "Covering Codes" (1997), Thm 5.4.27(i).
                                     Reprinted as (4.7) of arXiv:2511.02542.
  f(2t-1) = 5*2^(t-2) - 1, t >= 2    Gabidulin-Davydov-Tombak, IEEE-IT 37(1)
                                     219-224 (1991), Thm 1 eq. (5); (4.8) of
                                     arXiv:2511.02542.  Odd r only.
  n = 51                             Kaikkonen-Rosendahl, "New covering codes
                                     from an ADS-like construction", IEEE-IT
                                     49(7) 1809-1812 (2003), p.1812; reprinted
                                     as Thm 4.3 / display (4.9) of
                                     arXiv:2511.02542, whose Table 5.1 still
                                     carries it as the r=10 entry (Nov 2025).
  n = 50                             this repository, quest q1 (2026-08-16),
                                     compute/H_r10_n50.txt.
"""
import sys
from fractions import Fraction

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from profiles import load                                    # noqa: E402

R = 10


def density(n, r=R):
    return Fraction(1 + n + n * (n - 1) // 2, 1 << r)


def phi(r):
    return 27 * 2 ** (r // 2 - 4) - 1


def f_odd(r):
    return 5 * 2 ** ((r + 1) // 2 - 2) - 1


ROWS = [
    (1992, "phi(10), even-r family from the r=8 value 26", phi(10),
     "Davydov-Drozhzhina-Labinskaya; CHLL Thm 5.4.27(i)", None),
    (2003, "ADS-like direct construction at r=10", 51,
     "Kaikkonen-Rosendahl, IEEE-IT 49(7) 1809-1812", "compute/q9/H_r10_n51_KR.txt"),
    (2025, "Table 5.1 entry unchanged; used as their lift seed", 51,
     "Davydov-Marcugini-Pambianco, arXiv:2511.02542", "compute/q9/H_r10_n51_KR.txt"),
    (2026, "targeted annealing seeded from the 51-set", 50,
     "this repo, quest q1", "compute/H_r10_n50.txt"),
    (None, "open target", 49, "-", None),
]


def check(path):
    cols = load(path)
    hit = bytearray(1 << R)
    hit[0] = 1
    for c in cols:
        hit[c] = 1
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            hit[cols[i] ^ cols[j]] = 1
    basis, rk = [], 0
    for c in cols:
        for b in basis:
            c = min(c, c ^ b)
        if c:
            basis.append(c)
            basis.sort(reverse=True)
            rk += 1
    return len(cols), rk, sum(hit)


def main():
    print("trajectory of the documented upper bound on l_2(10,2)\n")
    print(f"{'year':>6} {'n':>4} {'density':>10} {'exact':>13} {'step':>5}  source")
    prev = None
    for year, how, n, src, path in ROWS:
        d = density(n)
        step = "" if prev is None else f"{n - prev:+d}"
        print(f"{(str(year) if year else 'open'):>6} {n:>4} {float(d):>10.5f} "
              f"{str(d):>13} {step:>5}  {src}")
        print(f"{'':>6} {'':>4} via {how}")
        if path:
            n2, rk, cov = check(path)
            assert n2 == n and rk == R, (path, n2, rk)
            print(f"{'':>6} {'':>4} re-verified from {path}: "
                  f"n={n2} rank={rk} covered={cov}/{1 << R}")
        prev = n
    print()
    print(f"f(9)={f_odd(9)}, f(11)={f_odd(11)}: the odd-r family does not reach r=10.")
    print(f"phi(8)={phi(8)}, phi(10)={phi(10)}, phi(12)={phi(12)}: the even-r family "
          "doubles n+1 every two units of r,")
    print("so the 1992 r=10 value is exactly the r=8 value 26 lifted: "
          f"2*(26+1)-1 = {2*(26+1)-1}.")
    vb = min(n for n in range(1, 60) if 1 + n + n * (n - 1) // 2 >= 1 << R)
    print(f"volume (sphere-covering) lower bound at r=10: n >= {vb}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
