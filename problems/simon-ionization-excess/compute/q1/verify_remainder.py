#!/usr/bin/env python3
"""Second-path check of the tightened HPS remainders.

Does not import tighten_hps.py. Recomputes a1 and the Z=4 remainder
coefficient from the HPS closed forms and asserts the printed-record
improvements. Exit 0 is the dent replay.
"""

from __future__ import annotations

import math
import sys


def b2() -> float:
    return 0.5 * (math.sqrt(2.0) + 1.0)


def b3() -> float:
    u = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0)
    return (2.0 / 3.0) * u / (u * u - 1.0)


def constants() -> tuple[float, float, float]:
    """Return (C1^{-1}, κ, c) with LT factor 1.456."""
    pi = math.pi
    c1 = (
        (3.0 ** (5.0 / 3.0))
        * (5.0 ** (5.0 / 6.0))
        * ((7.0 / pi) ** (1.0 / 3.0))
        / (22.0 * math.sqrt(11.0))
    )
    kappa = math.sqrt(5.0) * (2.0 / (9.0 * pi * pi) * 1.456) ** (1.0 / 3.0)
    c2inv = 4.0 * (pi ** (2.0 / 3.0)) / math.sqrt(15.0)
    return 1.0 / c1, kappa, kappa * c2inv


def a_s2(x: float) -> float:
    inv_c1, kappa, _ = constants()
    beta2 = 2.0 * (math.sqrt(2.0) - 1.0)
    lam = (3.0 / 8.0) * inv_c1 * kappa
    return (1.0 / beta2) * lam * x ** (-2.0 / 3.0) + (1.0 / beta2) * (
        (9.0 / 2.0) * beta2
    ) ** (1.0 / 3.0) * x ** (1.0 / 3.0)


def a1(x: float) -> float:
    _, _, c = constants()
    beta3 = 1.0 / b3()
    return (
        3.0
        * (0.3) ** (1.0 / 3.0)
        * beta3 ** (-2.0 / 3.0)
        * x ** (1.0 / 3.0)
        + c * (1.0 / beta3) * x ** (-2.0 / 3.0)
    )


def extras() -> tuple[float, float, float]:
    _, _, c = constants()
    bb = b3()
    a2 = bb / 84.0
    a3 = (c / 5.0) * ((5.0 / 12.0) ** (2.0 / 3.0)) * (bb ** (1.0 / 3.0))
    a4 = c * (bb ** (1.0 / 3.0)) / 84.0
    return a2, a3, a4


def main() -> int:
    bb2, bb3 = b2(), b3()
    assert 1.2071 < bb2 < 1.2072
    assert 1.1184 < bb3 < 1.1185
    a52 = a_s2(2.5)
    left = a1(bb3)
    right = a1(2.25)
    far = a1(2.5)
    a2, a3, a4 = extras()
    z13 = 4.0 ** (1.0 / 3.0)
    coeff4 = left + a2 / z13 + a3 / (z13 * z13) + a4 / 4.0
    print(f"b(2)={bb2:.16f}")
    print(f"b(3)={bb3:.16f}")
    print(f"a_s2(5/2)={a52:.16f} < 2.953")
    print(f"a1(b3)={left:.16f} < 3.892")
    print(f"a1(9/4)={right:.16f} < a1(b3)")
    print(f"a1(5/2)={far:.16f} < 3.90 and not < 3.893")
    print(f"Z=4 remainder coeff={coeff4:.16f} < 3.9781")
    if not (a52 < 2.953):
        print("FAIL a < 2.953", file=sys.stderr)
        return 1
    if not (left < 3.892 and right < left):
        print("FAIL a1 < 3.892 on [b3, 9/4]", file=sys.stderr)
        return 1
    if not (far < 3.90 and far >= 3.893):
        print("FAIL HPS 5/2 replay", file=sys.stderr)
        return 1
    if not (coeff4 < 3.9781):
        print("FAIL 3.9781", file=sys.stderr)
        return 1
    if not (a2 < 0.0134 and a3 < 0.184 and a4 < 0.0196):
        print("FAIL extras", file=sys.stderr)
        return 1
    print("verify_remainder.py PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
