#!/usr/bin/env python3
"""Which prime-order automorphisms can a radius-2 n-set in F_2^r even have?

sigma of odd prime order p acts on F_2^r with a fixed space of dimension c and
(2^r - 2^c)/p orbits of size p.  An invariant set is k full orbits plus m
nonzero fixed vectors, so n = p*k + m with 0 <= m <= 2^c - 1.  If no (k,m)
solves that, the symmetry is impossible for arithmetic reasons alone; if one
does, the exhaustive cost is C(n_orbits,k) * C(2^c-1,m).

sigma has odd order, so V = M (+) T canonically with T the fixed space; write
the "layer" of a vector for its T-component.  sigma does not move the layer, so
the layer of every sum is forced:

  membership -> t_i      inside orbit i -> 0     orbits i,j -> t_i + t_j
  orbit i with fixed g -> t_i + g       fixed with fixed -> stays in the fixed part

Every one of the 2^c layers contains orbits that must be covered, and the
layers a solution can touch at all are contained in
{0} u {t_i} u {t_i+t_j} u {t_i+g}, so

  1 + k + C(k,2) + k*m >= 2^c

is necessary.  That kills several families at a glance, with no search at all.
layer_lemma.py carries a second, per-layer version of the same idea.

p = 2 (unipotent sigma) is not covered here.

Usage: prime_orders.py <r> <n> [n ...]
"""
import sys
from math import comb


def ord2(p):
    k, x = 1, 2 % p
    while x != 1:
        x, k = x * 2 % p, k + 1
    return k


def main():
    r = int(sys.argv[1])
    targets = [int(a) for a in sys.argv[2:]]
    primes = [p for p in range(3, 1 << r) if all(p % q for q in range(2, int(p ** .5) + 1))]
    rows = []
    for p in primes:
        d = ord2(p)
        if d > r:
            continue                              # no element of order p in GL(r,2)
        for s in range(1, r // d + 1):
            c = r - d * s
            if c == r:
                continue
            n_orb = ((1 << r) - (1 << c)) // p
            fixedn = (1 << c) - 1
            for n in targets:
                sols = [(k, n - p * k) for k in range(n // p + 1)
                        if 0 <= n - p * k <= fixedn]
                if not sols:
                    rows.append((p, d, c, n_orb, fixedn, n, None, None))
                else:
                    sols = [(k, m) for k, m in sols
                            if 1 + k + k * (k - 1) // 2 + k * m >= (1 << c)]
                    if not sols:
                        rows.append((p, d, c, n_orb, fixedn, n, "layer", None))
                        continue
                    cost = min(comb(n_orb, k) * comb(fixedn, m) for k, m in sols)
                    rows.append((p, d, c, n_orb, fixedn, n, sols, cost))
    print(f"r = {r}, targets {targets}")
    print(f"{'p':>4} {'dim':>4} {'c':>3} {'orbits':>7} {'fixed':>6} {'n':>4}  "
          f"{'(k,m)':>18}  cost")
    for p, d, c, n_orb, fixedn, n, sols, cost in rows:
        if sols is None or sols == "layer":
            why = "arithmetic" if sols is None else "layer bound"
            print(f"{p:>4} {d:>4} {c:>3} {n_orb:>7} {fixedn:>6} {n:>4}  "
                  f"{'-- impossible --':>18}  {why}")
        else:
            ss = ",".join(f"({k},{m})" for k, m in sols[:3])
            if len(sols) > 3:
                ss += ",..."
            print(f"{p:>4} {d:>4} {c:>3} {n_orb:>7} {fixedn:>6} {n:>4}  {ss:>18}  {cost:.3g}")


if __name__ == "__main__":
    main()
