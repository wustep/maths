#!/usr/bin/env python3
"""More exact interpolating Delsarte duals on motivated finite T.

The 17 August duals cover T_D5 (bound 42) and T_L5 (bound 239925/5456).
This file tries other short Gegenbauer supports on:

  - T_Q5 and one-angle deletions of T_Q5
  - T_R5 = all known 40-point angles
  - T_L5 with alternate supports (looking for a bound < 43)
  - the even (antipodal) cone, which applies to even N only

A dual is recorded only when every c_k ≥ 0 and f ≤ 0 on T.  Bounds ≥ 44
do not exclude any k in {41,42,43,44}.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delsarte import eval_poly, gegenbauer_dim5
from exact_duals import certify_dual, ge_q

F = Fraction

T_D5 = [F(-1), F(-1, 2), F(0), F(1, 2)]
T_L5 = [F(-1), F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 2)]
T_Q5 = [F(-1), F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]
T_R5 = [F(-1), F(-4, 5), F(-3, 4), F(-1, 2), F(-3, 10), F(-1, 4),
        F(0), F(1, 5), F(1, 2)]


def interpolate(T_zero, free, T_all, name):
    deg = max(free)
    polys = gegenbauer_dim5(deg)
    A, b = [], []
    for t in T_zero:
        A.append([eval_poly(polys[k], t) for k in free])
        b.append(-F(1))
    try:
        x = ge_q(A, b)
    except ValueError as e:
        return {"name": name, "certified": False, "error": str(e)}
    c = [F(0)] * (deg + 1)
    c[0] = F(1)
    for k, val in zip(free, x):
        c[k] = val
    rec = certify_dual(c, T_all, name)
    rec["free"] = free
    rec["T_zero"] = [str(t) for t in T_zero]
    return rec


def even_antipodal(T_sym, free_even, name):
    """Even polynomial (antipodal codes): vanish on the nonnegative part of T."""
    zeros = [t for t in T_sym if t != F(-1) and t >= 0]
    return interpolate(zeros, free_even, T_sym, name)


def main() -> int:
    jobs = []
    # Q5, vanish on T except -1, several supports.
    Tq = [t for t in T_Q5 if t != F(-1)]
    for free in (
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 8],
        [1, 2, 3, 4, 5, 10],
        [2, 3, 4, 5, 6, 9],
        [1, 2, 4, 5, 6, 9],
    ):
        jobs.append(interpolate(Tq, free, T_Q5, f"Q5_free_{'_'.join(map(str, free))}"))

    # Drop 1/5 (LP already sets A_{1/5}=0).
    Tq2 = [F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 2)]
    jobs.append(interpolate(Tq2, [1, 2, 3, 4, 9],
                            [F(-1)] + Tq2, "Q5_minus_1_5"))

    # Drop -4/5.
    Tq3 = [F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]
    jobs.append(interpolate(Tq3, [1, 2, 3, 4, 9],
                            [F(-1)] + Tq3, "Q5_minus_m4_5"))

    # L5 alternate supports, hoping for < 43.
    Tl = [t for t in T_L5 if t != F(-1)]
    for free in (
        [1, 2, 3, 4, 6],
        [1, 2, 3, 4, 8],
        [1, 2, 3, 4, 10],
        [1, 2, 3, 5, 9],
        [2, 3, 4, 5, 9],
    ):
        jobs.append(interpolate(Tl, free, T_L5, f"L5_free_{'_'.join(map(str, free))}"))

    # R5 / all known angles.
    Tr = [t for t in T_R5 if t != F(-1)]
    jobs.append(interpolate(Tr, [1, 2, 3, 4, 5, 6, 7, 9], T_R5, "R5_c1_to_c7_c9"))
    jobs.append(interpolate(Tr, [1, 2, 3, 4, 5, 6, 8, 10], T_R5, "R5_c1_to_c6_c8_c10"))

    # Antipodal even duals (apply only to even N, A_{-1}=1).
    jobs.append(even_antipodal(
        [F(-1), F(-1, 2), F(0), F(1, 2)],
        [2, 4, 6],
        "antipodal_D5_even",
    ))
    jobs.append(even_antipodal(
        [F(-1), F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 4), F(1, 2), F(3, 4)],
        [2, 4, 6, 8],
        "antipodal_L5_symmetrized",
    ))

    report = {j["name"]: j for j in jobs}
    out = Path(__file__).resolve().parent / "restricted_duals.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    best = []
    for j in jobs:
        print(f"{j['name']}: certified={j.get('certified')} "
              f"bound={j.get('float_bound')} excludes={j.get('excludes')} "
              f"err={j.get('error')}")
        if j.get("certified") and j.get("excludes"):
            best.append(j)
    print("new exclusions:", [b["name"] for b in best])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
