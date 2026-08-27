"""Python boundary scan for the q3 {b,1} mesh.

For fixed b, the pure-Example-4 ratio at the independent C3 endpoint is

    (1-a) h_or_ex4(b,b) / h(b),

which decreases with a.  The mean b+(1-b)a increases with a.  It is
therefore enough to inspect the last retained a-grid point in each
b-row.  The independent C verifier visits every retained point.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

CLAIMED_C = 0.38305
Q1_C = 0.38304
LIU_QUOTE = 0.382709087918741
NB = 9000
NA = 7000
B_LO = 0.02
B_HI = 0.499
A_LO = 0.0
A_HI = 0.499
MEAN_TOL = 1e-15
HERE = Path(__file__).resolve().parent


def h(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p)) / math.log(2.0)


def a_example4(t: float) -> float:
    if t >= 0.5:
        return 1.0
    threshold = 1.0 - 1.0 / math.sqrt(2.0)
    if t <= threshold:
        return 0.0
    tb = 1.0 - t
    return math.sqrt((1.0 - 2.0 * tb * tb) / (2.0 * t * tb))


def h_or_example4(b: float) -> float:
    bb = 1.0 - b
    aa = a_example4(b)
    pi0 = bb * bb + aa * aa * (bb - bb * bb)
    return h(1.0 - pi0)


def grid_value(lo: float, hi: float, n: int, i: int) -> float:
    return lo + (hi - lo) * i / (n - 1)


def last_retained_index(b: float) -> int:
    if b > CLAIMED_C + MEAN_TOL:
        return -1
    da = (A_HI - A_LO) / (NA - 1)
    a_limit = (CLAIMED_C + MEAN_TOL - b) / (1.0 - b)
    j = min(NA - 1, math.floor((a_limit - A_LO) / da))
    while j >= 0:
        a = grid_value(A_LO, A_HI, NA, j)
        if b + (1.0 - b) * a <= CLAIMED_C + MEAN_TOL:
            break
        j -= 1
    while j + 1 < NA:
        a = grid_value(A_LO, A_HI, NA, j + 1)
        if b + (1.0 - b) * a > CLAIMED_C + MEAN_TOL:
            break
        j += 1
    return j


def main():
    min_ratio = math.inf
    at = None
    n_kept = 0
    rows_retained = 0
    bad_boundary_rows = 0

    for i in range(NB):
        b = grid_value(B_LO, B_HI, NB, i)
        j = last_retained_index(b)
        if j < 0:
            continue
        rows_retained += 1
        n_kept += j + 1
        a = grid_value(A_LO, A_HI, NA, j)
        mean = b + (1.0 - b) * a
        hb = h(b)
        hp = h_or_example4(b)
        ratio = (1.0 - a) * hp / hb
        if ratio <= 1.0:
            bad_boundary_rows += 1
        if ratio < min_ratio:
            min_ratio = ratio
            at = {"i_b": i, "i_a": j, "b": b, "a": a, "mean": mean}

    checks = {
        "claimed_above_q1": CLAIMED_C > Q1_C,
        "claimed_above_liu": CLAIMED_C > LIU_QUOTE,
        "retained_cells_nonzero": n_kept > 0,
        "all_boundary_ratios_strictly_above_1": bad_boundary_rows == 0,
        "minimum_ratio_strictly_above_1": min_ratio > 1.0,
    }
    report = {
        "implementation": "Python row-boundary scan using ratio monotonicity in a",
        "claimed_c": CLAIMED_C,
        "grid": {
            "n_b": NB,
            "n_a": NA,
            "b_lo": B_LO,
            "b_hi": B_HI,
            "a_lo": A_LO,
            "a_hi": A_HI,
            "total_cells": NB * NA,
            "retained_cells": n_kept,
            "retained_rows": rows_retained,
            "mean_tolerance": MEAN_TOL,
        },
        "monotonicity": (
            "mean increases and ratio=(1-a)h_or_ex4(b,b)/h(b) decreases "
            "with a, so each retained row is minimized at its last point"
        ),
        "min_ratio": min_ratio,
        "n_bad_boundary_rows": bad_boundary_rows,
        "n_bad_cells": 0 if bad_boundary_rows == 0 else None,
        "at": at,
        "checks": checks,
        "all_ok": all(checks.values()),
    }
    path = HERE / "certs" / "python_mesh.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
