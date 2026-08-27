#!/usr/bin/env python3
"""Independent exact check of a q1 rational certificate.

Does not import the searcher, the rationalizer, or verify_certificate.py.
Covering is computed by a Fraction convolution (correlate padded w with p),
not by the nested (q,i) loop used in the parent verifier.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


def F(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def correlate(W: list[Fraction], p: list[Fraction]) -> list[Fraction]:
    """valid-mode correlation: out[q] = sum_i p[i] * W[q+i]."""
    m = len(p)
    out = []
    for q in range(len(W) - m + 1):
        s = Fraction(0)
        for i, pi in enumerate(p):
            s += pi * W[q + i]
        out.append(s)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate")
    ap.add_argument("--beat", default="0.9435")
    args = ap.parse_args()

    data = json.loads(Path(args.certificate).read_text())
    m, L = int(data["m"]), int(data["L"])
    n = m * L
    if data.get("asymmetric"):
        raise SystemExit("FAIL this verifier is for the symmetric lemma")
    lams = [F(x) for x in data["lambdas"]]
    kernels = [[F(x) for x in row] for row in data["kernels"]]
    weights = [[F(x) for x in row] for row in data["weights_left"]]

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

    ones = [Fraction(1)] * m
    M = [Fraction(0)] * (n + 1)
    for lam, p, w in zip(lams, kernels, weights):
        vals = correlate(w + ones, p)
        if len(vals) != n + 1:
            raise SystemExit(f"FAIL correlate length {len(vals)}")
        for q, v in enumerate(vals):
            M[q] += lam * v
    slacks = [mq - 1 for mq in M]
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
        raise SystemExit(f"FAIL ab={a*b} not < ({target})^2")

    print("certificate", args.certificate)
    print("R", len(lams), "m", m, "L", L)
    print("min_slack", min(slacks))
    print("a", a)
    print("b", b)
    print("ab", a * b)
    print("gamma_float", math.sqrt(float(a * b)))
    print("beats", str(target), "YES")
    print("PASS")


if __name__ == "__main__":
    main()
