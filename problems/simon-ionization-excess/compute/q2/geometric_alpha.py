#!/usr/bin/env python3
"""Elementary lower bounds on alpha_{N,s} that do not use a search.

s=1: triangle, alpha_{N,1} >= 1/2 (Lieb). Equality along opposite rays.
s=2, N=2: alpha_2,2 = 1/2 (HPS/Nam).
s=2, N=3: the underestimate (a^2+b^2)/(a+b) recovers only 1/2.
Nam's √5/4 is cited as a published lower bound for N>=3, s=2; we replay
the arithmetic  √5/4 ≈ 0.559, and check it against structured configs.
We do not re-prove √5/4.

For N=4, Z=2, even √5/4 is too small: (√5/4)*3 ≈ 1.677 < 2.
A lemma that alpha_4,2 > 2/3 would be the geometric half of a dent if
the kinetic remainder were also controlled. This file records that the
published elementary lowers do not reach 2/3.

Replay: python3 geometric_alpha.py
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    sqrt5_4 = math.sqrt(5.0) / 4.0
    two_thirds = 2.0 / 3.0
    blob = {
        "not_a_certificate": True,
        "is_new_bound": False,
        "lieb_s1": {
            "alpha_N_1_ge": 0.5,
            "gives": "N < 2Z+1",
            "at_Z2": "N < 5, so Nc(2) <= 4",
        },
        "nam_s2_N2": {"alpha_2_2": 0.5},
        "nam_sqrt5_over_4": {
            "value": sqrt5_4,
            "exact": "sqrt(5)/4",
            "applies": "Nam text: alpha_N >= sqrt(5)/4 when N>=3 (s=2)",
            "invoked_not_reproved": True,
            "N4_times_3": 3.0 * sqrt5_4,
            "below_Z2": 3.0 * sqrt5_4 < 2.0,
        },
        "threshold_N4_Z2_kinetic_dropped": {
            "need_alpha_4": two_thirds,
            "sqrt5_over_4_minus_need": sqrt5_4 - two_thirds,
        },
        "equilateral_centred_s2": {
            "alpha": math.sqrt(3.0) / 3.0,
            "exact": "sqrt(3)/3",
            "N3_times_2": 2.0 * math.sqrt(3.0) / 3.0,
            "below_Z2": True,
            "note": "configuration, hence an upper bound on inf alpha_3",
        },
        "tetrahedron_centred_s2": {
            "alpha": math.sqrt(6.0) / 4.0,
            "exact": "sqrt(6)/4",
            "N4_times_3": 3.0 * math.sqrt(6.0) / 4.0,
            "below_Z2": True,
            "integer_form": "3*sqrt(6) < 8  <=>  54 < 64",
            "note": (
                "Regular tetrahedron centred at the origin. Evaluates "
                "alpha_4,2 exactly. So alpha_4,2 <= sqrt(6)/4 < 2/3, and "
                "alpha_4,2 * 3 <= 3*sqrt(6)/4 < 2. The s=2 pair geometry "
                "cannot exclude N=4 at Z=2 even if the kinetic remainder "
                "is dropped. Independent integer check: 9*6 = 54 < 64."
            ),
        },
        "one_at_origin_opposite_s2": {
            "alpha": 0.75,
            "exact": "3/4",
            "note": "configuration; not the infimum",
        },
        "note": (
            "Published elementary lowers on alpha_4 stop at 1/2 or at "
            "sqrt(5)/4. The tetrahedron gives a certified *upper* on "
            "alpha_4,2 below the 2/3 threshold. No geometric dent for "
            "Nc(2)<4 from the |x|^s pair ratio."
        ),
    }
    # Integer check: 3 sqrt(5) < 8  <=>  (sqrt(5)/4)*3 < 2.
    if not (3.0 * sqrt5_4 < 2.0):
        raise RuntimeError("arithmetic of sqrt(5)/4 * 3 vs 2 drifted")
    if Fraction(3, 4) <= Fraction(2, 3):
        raise RuntimeError("3/4 should exceed 2/3")
    # 3 sqrt(6) < 8  <=>  9*6 < 64.
    if 54 >= 64:
        raise RuntimeError("54 < 64 failed")
    if 3 * 3 * 6 >= 8 * 8:
        raise RuntimeError("tetrahedron 3*sqrt(6) < 8 failed")
    # Cross-check the closed form on the tetrahedron vertices.
    tet = (
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    )
    r = math.sqrt(3.0)
    d = math.sqrt(8.0)
    num = 6.0 * (r**2 + r**2) / d
    den = 3.0 * 4.0 * r
    a_tet = num / den
    if abs(a_tet - math.sqrt(6.0) / 4.0) > 1e-12:
        raise RuntimeError(f"tetrahedron alpha drifted: {a_tet}")
    path = CERTS / "geometric_alpha.json"
    path.write_text(json.dumps(blob, indent=2) + "\n")
    print("Lieb s=1: alpha >= 1/2, N < 2Z+1, Nc(2)<=4")
    print(f"Nam √5/4 = {sqrt5_4:.12f};  3*(√5/4) = {3*sqrt5_4:.12f} < 2")
    print(f"need alpha_4 > 2/3 = {two_thirds:.12f} if kinetic dropped")
    print(f"√5/4 - 2/3 = {sqrt5_4 - two_thirds:.12f}  (short)")
    print("equilateral centred s=2:", math.sqrt(3) / 3)
    print("wrote", path)


if __name__ == "__main__":
    main()
