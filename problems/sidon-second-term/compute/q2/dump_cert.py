#!/usr/bin/env python3
"""Dump a rational certificate as num/den lines for the C verifier."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path


def F(x) -> Fraction:
    return Fraction(x)


def main() -> None:
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    data = json.loads(src.read_text())
    m, L = int(data["m"]), int(data["L"])
    if data.get("asymmetric"):
        raise SystemExit("symmetric certificates only")
    lams = [F(x) for x in data["lambdas"]]
    kernels = [[F(x) for x in row] for row in data["kernels"]]
    weights = [[F(x) for x in row] for row in data["weights_left"]]
    lines = [f"{len(lams)} {m} {L}"]
    for x in lams:
        lines.append(f"{x.numerator} {x.denominator}")
    for p in kernels:
        for x in p:
            lines.append(f"{x.numerator} {x.denominator}")
    for w in weights:
        for x in w:
            lines.append(f"{x.numerator} {x.denominator}")
    dst.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
