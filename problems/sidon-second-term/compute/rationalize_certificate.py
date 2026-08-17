#!/usr/bin/env python3
"""Turn a floating Hou–Zhao-style candidate into an exact rational certificate.

Procedure (same shape as Hou–Zhao §3.2, implemented independently):
  1. Round mixing weights and kernels to a common denominator; restore
     exact simplex / symmetry.
  2. Re-solve the boundary QP in floats on the rounded kernels.
  3. Round the weights, then add a common rational η so every covering
     inequality holds exactly.
  4. Write a JSON certificate consumed by verify_certificate.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vector_smoothing import solve_boundary_qp  # noqa: E402


def to_frac_prob(values, den: int, symmetric: bool) -> list[Fraction]:
    ints = [max(0, int(round(float(x) * den))) for x in values]
    if symmetric:
        m = len(ints)
        for i in range(m // 2):
            s = ints[i] + ints[m - 1 - i]
            # split as evenly as possible, then force exact symmetry
            ints[i] = s // 2
            ints[m - 1 - i] = s - ints[i]
            # actually force equal
            ints[i] = ints[m - 1 - i] = s // 2
        # leftover 1 from odd sum goes to the two middle-most pair equally impossible;
        # drop it — we renormalize next.
    total = sum(ints)
    if total == 0:
        ints[len(ints) // 2] = 1
        total = 1
    # exact probability vector with denominator total
    return [Fraction(x, total) for x in ints]


def to_frac_mix(values, den: int) -> list[Fraction]:
    ints = [max(1, int(round(float(x) * den))) for x in values]
    total = sum(ints)
    return [Fraction(x, total) for x in ints]


def cover_slack(lams, kernels, weights, q: int, n: int) -> Fraction:
    total = Fraction(0)
    for lam, p, w in zip(lams, kernels, weights):
        for i, pi in enumerate(p):
            j = q + i
            total += lam * pi * (w[j] if j < n else Fraction(1))
    return total - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate_json")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--den-mix", type=int, default=10**8)
    ap.add_argument("--den-ker", type=int, default=10**12)
    ap.add_argument("--den-w", type=int, default=10**9)
    args = ap.parse_args()

    cand = json.loads(Path(args.candidate_json).read_text())
    m = int(cand["m"])
    L = int(cand["L"])
    n = m * L
    asymmetric = bool(cand.get("asymmetric", False))
    kernels_f = np.array(cand["kernels"], dtype=float)
    lams_f = np.array(cand["lambdas"], dtype=float)

    lams = to_frac_mix(lams_f, args.den_mix)
    kernels = [
        to_frac_prob(row, args.den_ker, symmetric=not asymmetric) for row in kernels_f
    ]
    # Re-solve QP on the rational kernels (as floats) so weights match the rounded p.
    ker_f = np.array([[float(x) for x in row] for row in kernels], dtype=float)
    lam_f = np.array([float(x) for x in lams], dtype=float)
    wL_f, wR_f, _, _, _ = solve_boundary_qp(ker_f, lam_f, L, asymmetric=asymmetric)

    def round_w(row):
        return [Fraction(int(round(float(x) * args.den_w)), args.den_w) for x in row]

    wL = [round_w(row) for row in wL_f]
    wR = [round_w(row) for row in wR_f] if asymmetric else [list(row) for row in wL]

    def eta_for(weights, reverse: bool) -> Fraction:
        ps = [list(reversed(p)) for p in kernels] if reverse else kernels
        eta = Fraction(0)
        for q in range(n):
            M = Fraction(0)
            rho = Fraction(0)
            for lam, p, w in zip(lams, ps, weights):
                for i, pi in enumerate(p):
                    j = q + i
                    if j < n:
                        M += lam * pi * w[j]
                        rho += lam * pi
                    else:
                        M += lam * pi
            if rho > 0 and M < 1:
                need = (1 - M) / rho
                if need > eta:
                    eta = need
        return eta

    etaL = eta_for(wL, reverse=False)
    etaR = eta_for(wR, reverse=True) if asymmetric else etaL
    eta = etaL if etaL >= etaR else etaR
    # tiny extra so rounding of display cannot hide a zero-slack miss
    if eta < 0:
        eta = Fraction(0)
    wL = [[x + eta for x in row] for row in wL]
    wR = [[x + eta for x in row] for row in wR]

    def ab(weights):
        a = Fraction(m) * sum(lam * sum(x * x for x in p) for lam, p in zip(lams, kernels))
        energy = sum(lam * sum(x * x for x in w) for lam, w in zip(lams, weights))
        if asymmetric:
            energy_r = sum(lam * sum(x * x for x in w) for lam, w in zip(lams, wR))
            b = 1 - 2 * L + (energy + energy_r) / m
        else:
            b = 1 + 2 * (energy / m - L)
        return a, b

    a, b = ab(wL)
    payload = {
        "m": m,
        "L": L,
        "asymmetric": asymmetric,
        "eta": str(eta),
        "lambdas": [str(x) for x in lams],
        "kernels": [[str(x) for x in row] for row in kernels],
        "weights_left": [[str(x) for x in row] for row in wL],
        "weights_right": [[str(x) for x in row] for row in wR],
        "a": str(a),
        "b": str(b),
        "source_gamma_float": cand.get("gamma_float"),
        "source_tag": cand.get("tag"),
    }
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", args.output)
    print("eta", eta)
    print("a", a)
    print("b", b)
    if a > 0 and b > 0:
        import math

        print("gamma_float_of_rationals", math.sqrt(float(a * b)))


if __name__ == "__main__":
    main()
