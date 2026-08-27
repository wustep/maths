#!/usr/bin/env python3
"""Independent exact check of a q2 rational certificate.

Does not import the searcher, the rationalizer, verify_certificate.py,
or q1/verify_q1.py. Covering is a sparse exact matrix-vector product:
one Fraction matrix A of shape (n+1, R*n) times the stacked weights,
plus the kernel-tail contribution when q+i >= n.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


def F(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate")
    ap.add_argument("--beat", default="0.94325")
    args = ap.parse_args()

    data = json.loads(Path(args.certificate).read_text())
    m, L = int(data["m"]), int(data["L"])
    n = m * L
    if data.get("asymmetric"):
        raise SystemExit("FAIL this verifier is for the symmetric lemma")
    lams = [F(x) for x in data["lambdas"]]
    kernels = [[F(x) for x in row] for row in data["kernels"]]
    weights = [[F(x) for x in row] for row in data["weights_left"]]
    R = len(lams)

    if any(x < 0 for x in lams) or sum(lams) != 1:
        raise SystemExit(f"FAIL mix sum={sum(lams)}")
    for r, p in enumerate(kernels):
        if len(p) != m or any(x < 0 for x in p) or sum(p) != 1:
            raise SystemExit(f"FAIL kernel {r} simplex")
        if p != list(reversed(p)):
            raise SystemExit(f"FAIL kernel {r} not symmetric")
    for r, w in enumerate(weights):
        if len(w) != n:
            raise SystemExit(f"FAIL weight {r} length {len(w)}")

    # A[q, r*n + j] = λ_r * p_i whenever j = q+i < n.
    # tail[q] = sum_{r,i : q+i >= n} λ_r p_i.
    dim = R * n
    A = [[Fraction(0) for _ in range(dim)] for _ in range(n + 1)]
    tail = [Fraction(0) for _ in range(n + 1)]
    for r, (lam, p) in enumerate(zip(lams, kernels)):
        for i, pi in enumerate(p):
            coeff = lam * pi
            for q in range(n + 1):
                j = q + i
                if j < n:
                    A[q][r * n + j] += coeff
                else:
                    tail[q] += coeff

    wflat = [x for row in weights for x in row]
    slacks = []
    for q in range(n + 1):
        s = tail[q]
        row = A[q]
        for j, wj in enumerate(wflat):
            if row[j]:
                s += row[j] * wj
        slacks.append(s - 1)
    if any(s < 0 for s in slacks):
        q = min(range(len(slacks)), key=lambda i: slacks[i])
        raise SystemExit(f"FAIL covering q={q} slack={slacks[q]}")

    a = Fraction(m) * sum(lam * sum(x * x for x in p) for lam, p in zip(lams, kernels))
    energy = sum(lam * sum(x * x for x in w) for lam, w in zip(lams, weights))
    b = 1 + 2 * (energy / m - L)
    if b <= 0:
        raise SystemExit(f"FAIL b={b}")
    target = F(args.beat)
    if a * b >= target * target:
        raise SystemExit(f"FAIL ab={a * b} not < ({target})^2")

    print("certificate", args.certificate)
    print("R", R, "m", m, "L", L)
    print("min_slack", min(slacks))
    print("a", a)
    print("b", b)
    print("ab", a * b)
    print("gamma_float", math.sqrt(float(a * b)))
    print("beats", str(target), "YES")
    print("PASS")


if __name__ == "__main__":
    main()
