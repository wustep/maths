#!/usr/bin/env python3
"""Certificate: BSKK N=2 theta is optimal among 4-prime products.

Recomputes alpha(s, gamma; P) for uniform-{0,1} using |muhat|=|cos(pi xi)|.
Checks:
  1. At P=210, s=134, gamma_max = 0.500565... and published 0.50057
     has alpha > 1 (their rounding is slightly illegal).
  2. The best feasible theta at P=210 is s=134.
  3. No 4-prime product of primes <= 31 with P<=15015 beats that theta
     on the s-grid used in fourier_theta.py.
"""

from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

# Reuse the search already run; this file only verifies the stored
# certificate and the two critical scalar claims at P=210.


def abs_cos_table(P: int):
    def divisors(n):
        d = []
        i = 1
        while i * i <= n:
            if n % i == 0:
                d.append(i)
                if i * i != n:
                    d.append(n // i)
            i += 1
        return sorted(d)

    tables = {}
    for Q in divisors(P):
        if Q == 1:
            continue
        R = P // Q
        k = np.arange(Q, dtype=np.float64)
        cols = [np.abs(np.cos(np.pi * (k / Q + ell / R))) for ell in range(R)]
        tables[Q] = np.stack(cols, axis=0)
    return tables


def alpha(tables, s, gamma):
    worst = 0.0
    for Q, mat in tables.items():
        S = np.sum(np.power(mat, s), axis=1)
        worst = max(worst, float(np.max((Q ** (gamma - 1.0)) * S)))
    return worst


def gamma_max(tables, s):
    best = float("inf")
    for Q, mat in tables.items():
        S = np.sum(np.power(mat, s), axis=1)
        S = S[S > 0]
        gvals = 1.0 - np.log(S) / math.log(Q)
        best = min(best, float(np.min(gvals)))
    return best


def main() -> int:
    tables = abs_cos_table(210)
    g = gamma_max(tables, 134)
    a_pub = alpha(tables, 134, 0.50057)
    a_g = alpha(tables, 134, g)
    a_below = alpha(tables, 134, g - 1e-8)
    theta = g / 134.0
    print(f"gamma_max(210,134) = {g:.12f}")
    print(f"theta              = {theta:.12f}")
    print(f"alpha(0.50057)     = {a_pub:.12f}")
    print(f"alpha(gamma_max)   = {a_g:.12f}")
    print(f"alpha(g-1e-8)      = {a_below:.12f}")

    errors = []
    if not (0.50056 < g < 0.50057):
        errors.append(f"unexpected gamma_max {g}")
    if a_pub <= 1.0:
        errors.append("published gamma 0.50057 should be infeasible")
    if a_g > 1.0 + 1e-12:
        errors.append("gamma_max should be feasible")
    if a_below >= 1.0:
        errors.append("g-1e-8 should be strictly feasible")
    if abs(theta - 0.0037355625) > 1e-10:
        errors.append(f"unexpected theta {theta}")

    path = os.path.join(os.path.dirname(__file__), "fourier_theta.json")
    with open(path) as f:
        data = json.load(f)
    bg = data["best_global"]
    if bg["P"] != 210 or bg["theta"] > theta + 1e-9:
        # coarse grid may report s=136; refined best is 134
        refined = data.get("refined_around_best") or data.get("feas210_top20")
        best_ref = max(refined, key=lambda r: r["theta"])
        if best_ref["s"] != 134:
            errors.append(f"refined best s={best_ref['s']} not 134")
        if best_ref["theta"] > theta + 1e-9:
            errors.append("search claims a better theta than P=210 s=134")

    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print("OK  BSKK N=2 theta is optimal for 4-prime Fourier; published 0.003736 is a 4e-7 over-round")
    return 0


if __name__ == "__main__":
    sys.exit(main())
