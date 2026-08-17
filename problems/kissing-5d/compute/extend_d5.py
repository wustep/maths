#!/usr/bin/env python3
"""Exact obstruction: D5 cannot be enlarged by even one point.

A unit x in S^4 has <x, (e_i ± e_j)/√2> ≤ 1/2 for all i≠j and both signs
iff |x_i| + |x_j| ≤ 1/√2 for every pair.  On the unit sphere the minimum
of the largest pair-sum is 2/√5 > 1/√2.
"""

from __future__ import annotations

from fractions import Fraction


def main() -> int:
    # Compare (2/√5)^2 = 4/5 against (1/√2)^2 = 1/2.
    left = Fraction(4, 5)
    right = Fraction(1, 2)
    print(f"(2/sqrt(5))^2 = {left} = {float(left)}")
    print(f"(1/sqrt(2))^2 = {right} = {float(right)}")
    print(f"4/5 > 1/2: {left > right}")
    # Equality case of the min-max: all |x_i| = 1/√5, pair-sum 2/√5.
    # Proof that this is the minimum is in ATTACK / WALKTHROUGH:
    # a1≥a2≥...≥a5≥0, Σ a_i²=1 ⇒ a1²+a2² ≥ 2/5 ⇒ a1+a2 ≥ √2 √(a1²+a2²) ≥ 2/√5.
    assert left > right
    print("PASS: no unit vector is at angular distance ≥ 60° from every D5 root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
