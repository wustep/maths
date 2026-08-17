#!/usr/bin/env python3
"""Third check: our L=6 certificate vs Hou–Zhao Claim 4.1, fractions only.

Does not import the searcher, the rationalizer, or verify_certificate.py.
Recomputes covering / a / b from the JSON, then compares ab to the
fractions printed in arXiv:2607.01169v2 Claim 4.1.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

CERT = Path(__file__).resolve().parent / "certs" / "hz_kernels_L6.json"
HZ_A = Fraction(497329054138522113993707809619, 390625000000000000000000000000)
HZ_B = Fraction(69918675237166718360455326217, 100000000000000000000000000000)
TARGET = Fraction(94349251, 100000000) ** 2


def F(x):
    return Fraction(x)


def main():
    data = json.loads(CERT.read_text())
    m, L = int(data["m"]), int(data["L"])
    n = m * L
    lams = [F(x) for x in data["lambdas"]]
    kernels = [[F(x) for x in row] for row in data["kernels"]]
    weights = [[F(x) for x in row] for row in data["weights_left"]]
    if sum(lams) != 1 or any(x <= 0 for x in lams):
        raise SystemExit("FAIL mix")
    for p in kernels:
        if sum(p) != 1 or any(x < 0 for x in p) or p != list(reversed(p)):
            raise SystemExit("FAIL kernel")
    slacks = []
    for q in range(n + 1):
        tot = Fraction(0)
        for lam, p, w in zip(lams, kernels, weights):
            for i, pi in enumerate(p):
                j = q + i
                tot += lam * pi * (w[j] if j < n else Fraction(1))
        slacks.append(tot - 1)
    if any(s < 0 for s in slacks):
        raise SystemExit(f"FAIL cover {min(slacks)}")
    a = Fraction(m) * sum(lam * sum(x * x for x in p) for lam, p in zip(lams, kernels))
    b = 1 + 2 * (
        Fraction(1, m) * sum(lam * sum(x * x for x in w) for lam, w in zip(lams, weights))
        - L
    )
    if a != HZ_A:
        raise SystemExit(f"FAIL a changed {a}")
    if not (b > 0 and a * b < HZ_A * HZ_B):
        raise SystemExit("FAIL ab not below Hou–Zhao Claim 4.1")
    if not (a * b < TARGET):
        raise SystemExit("FAIL not below 0.94349251")
    print("cert", CERT)
    print("L", L, "R", len(lams), "m", m)
    print("min_slack", min(slacks))
    print("a_matches_HZ_claim_4_1", True)
    print("ab_HZ", HZ_A * HZ_B)
    print("ab_L6", a * b)
    print("gamma_HZ", math.sqrt(float(HZ_A * HZ_B)))
    print("gamma_L6", math.sqrt(float(a * b)))
    print("delta_gamma", math.sqrt(float(HZ_A * HZ_B)) - math.sqrt(float(a * b)))
    print("certified_C_lt", "0.94349251")
    print("PASS")


if __name__ == "__main__":
    main()
