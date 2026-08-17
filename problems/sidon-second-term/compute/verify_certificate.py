#!/usr/bin/env python3
"""Independent exact verifier for a rational vector-smoothing certificate.

Uses only fractions.Fraction. Re-derives covering, a, b from the definitions
in Hou–Zhao Lemma 2.1 (and the left/right split written in vector_smoothing.py).
Does not import the searcher or the rationalizer.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


def F(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def cover(lams, kernels, weights, q: int, n: int) -> Fraction:
    total = Fraction(0)
    for lam, p, w in zip(lams, kernels, weights):
        for i, pi in enumerate(p):
            j = q + i
            total += lam * pi * (w[j] if j < n else Fraction(1))
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate")
    ap.add_argument("--beat", type=str, default=None, help="rational or decimal upper target")
    args = ap.parse_args()

    data = json.loads(Path(args.certificate).read_text())
    m = int(data["m"])
    L = int(data["L"])
    n = m * L
    asymmetric = bool(data.get("asymmetric", False))
    lams = [F(x) for x in data["lambdas"]]
    kernels = [[F(x) for x in row] for row in data["kernels"]]
    wL = [[F(x) for x in row] for row in data["weights_left"]]
    wR = [[F(x) for x in row] for row in data["weights_right"]]

    if any(x < 0 for x in lams) or sum(lams) != 1:
        raise SystemExit(f"FAIL mix {lams} sum={sum(lams)}")
    for r, p in enumerate(kernels):
        if len(p) != m or any(x < 0 for x in p) or sum(p) != 1:
            raise SystemExit(f"FAIL kernel {r}")
        if not asymmetric and p != list(reversed(p)):
            raise SystemExit(f"FAIL kernel {r} symmetry")
    for r, w in enumerate(wL):
        if len(w) != n:
            raise SystemExit(f"FAIL wL {r} length")
    for r, w in enumerate(wR):
        if len(w) != n:
            raise SystemExit(f"FAIL wR {r} length")

    slacks_L = [cover(lams, kernels, wL, q, n) - 1 for q in range(n + 1)]
    ker_rev = [list(reversed(p)) for p in kernels]
    slacks_R = [cover(lams, ker_rev, wR, q, n) - 1 for q in range(n + 1)]
    if any(s < 0 for s in slacks_L):
        q = min(range(len(slacks_L)), key=lambda i: slacks_L[i])
        raise SystemExit(f"FAIL left covering q={q} slack={slacks_L[q]}")
    if any(s < 0 for s in slacks_R):
        q = min(range(len(slacks_R)), key=lambda i: slacks_R[i])
        raise SystemExit(f"FAIL right covering q={q} slack={slacks_R[q]}")

    a = Fraction(m) * sum(lam * sum(x * x for x in p) for lam, p in zip(lams, kernels))
    eL = sum(lam * sum(x * x for x in w) for lam, w in zip(lams, wL))
    eR = sum(lam * sum(x * x for x in w) for lam, w in zip(lams, wR))
    if asymmetric:
        b = 1 - 2 * L + (eL + eR) / m
    else:
        b = 1 + 2 * (eL / m - L)
    if b <= 0:
        raise SystemExit(f"FAIL b={b}")

    gamma2 = a * b
    print("certificate", args.certificate)
    print("R", len(lams), "m", m, "L", L, "asymmetric", asymmetric)
    print("min_slack_left", min(slacks_L))
    print("min_slack_right", min(slacks_R))
    print("a", a)
    print("b", b)
    print("ab", gamma2)
    print("gamma_float", math.sqrt(float(gamma2)))

    if args.beat is not None:
        target = F(args.beat)
        # allow a decimal like 0.9435
        if gamma2 < target * target:
            print("beats_target", str(target), "YES")
        else:
            print("beats_target", str(target), "NO")
            raise SystemExit("FAIL did not beat target")
    print("PASS")


if __name__ == "__main__":
    main()
