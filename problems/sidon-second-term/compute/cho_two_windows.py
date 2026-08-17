#!/usr/bin/env python3
"""Independent check of Carter–Hunter–O’Bryant Theorem 2.1 (two windows).

Recomputes the affine bounds (1),(2) from their published parameters and
confirms the hand-checkable claim b_∞ ≤ 1.99058, i.e.
F(N) ≤ sqrt(N) + 0.99529 N^{1/4} + O(1). This is strictly weaker than
Hou–Zhao 0.9435; it is only a replay of the published two-window proof.
"""

from __future__ import annotations

import math


def bound1(tau, a1, a2, w1, w2):
    # b <= tau + 1/tau - tau*(w1 (a1-1)^2 + (2-w2)(a2-1)^2)
    return tau + 1.0 / tau - tau * (w1 * (a1 - 1.0) ** 2 + (2.0 - w2) * (a2 - 1.0) ** 2)


def bound2(tau, a1, a2, c, w1, w2):
    # b <= c tau + 1/(c tau) - (tau/c^2) * ((w2-w1-2c)_+ (c-(a2-a1))_+^2 + w1 (c-a1)_+^2)
    def pos(x):
        return x if x > 0 else 0.0

    return (
        c * tau
        + 1.0 / (c * tau)
        - (tau / c**2)
        * (pos(w2 - w1 - 2 * c) * pos(c - (a2 - a1)) ** 2 + w1 * pos(c - a1) ** 2)
    )


def main():
    tau, a1, a2, c = 1.07950, 0.72720, 1.31609, 0.86838
    # Paper's truncated affine forms (rounded weaker):
    # (1) b <= 1.7901428 - 0.0803363 w1 + 0.1078559 w2
    # (2) b <= 3.3009719 + 0.7181409 w1 - 0.7466741 w2
    worst = 0.0
    # sample the triangle 0 <= w1 <= w2 <= 2
    n = 400
    for i in range(n + 1):
        for j in range(i, n + 1):
            w1 = 2.0 * i / n
            w2 = 2.0 * j / n
            b = min(bound1(tau, a1, a2, w1, w2), bound2(tau, a1, a2, c, w1, w2))
            if b > worst:
                worst = b
    # also the paper's 7-digit weaker comparison
    paper_claim = 1.99058
    C = worst / 2.0
    print("worst_b_sampled", worst)
    print("equiv_C", C)
    print("paper_claim_b", paper_claim)
    print("below_paper_claim", worst <= paper_claim + 1e-5)
    print("weaker_than_houzhao_0.9435", C > 0.9435)
    # recover the paper's affine coefficients at the same rounding direction
    # Evaluate (1) at (w1,w2)=(0,0) and basis vectors numerically
    b1_00 = bound1(tau, a1, a2, 0, 0)
    b1_10 = bound1(tau, a1, a2, 1, 0)
    b1_01 = bound1(tau, a1, a2, 0, 1)
    print("bound1_const", b1_00)
    print("bound1_coeff_w1", b1_10 - b1_00)
    print("bound1_coeff_w2", b1_01 - b1_00)


if __name__ == "__main__":
    main()
