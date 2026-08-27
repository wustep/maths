"""Analytic margin for the five-decimal q3 claim on the {b,1} ray.

For pure Liu Example 4, the first-crossing is the unique critical point
of f(b) = 1 - (1-b)h(b) on the saturation interval.  It solves

    h(b) = (1-b) log2((1-b)/b).

Replay: python3 solve_margin.py
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import findroot, log, mp, mpf, nstr

mp.dps = 80
LN2 = log(2)

CLAIMED = mpf("0.38305")
Q1 = mpf("0.38304")
LIU = mpf("0.382709087918741")
HERE = Path(__file__).resolve().parent


def h(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return -(p * log(p) + (1 - p) * log(1 - p)) / LN2


def critical_eq(b):
    b = mpf(b)
    return h(b) - (1 - b) * log((1 - b) / b) / LN2


def main():
    b = findroot(critical_eq, mpf("0.2965"))
    crossing = 1 - (1 - b) * h(b)
    residual = critical_eq(b)
    g_second = -2 * log((1 - b) / b) / LN2 - 1 / (b * LN2)
    margin = crossing - CLAIMED
    saturation_ratio_at_bstar = (1 - CLAIMED) / (1 - crossing)

    checks = {
        "critical_residual_below_1e_60": bool(abs(residual) < mpf("1e-60")),
        "g_second_derivative_negative": bool(g_second < 0),
        "crossing_above_claimed": bool(crossing > CLAIMED),
        "claimed_above_q1": bool(CLAIMED > Q1),
        "claimed_above_liu": bool(CLAIMED > LIU),
        "saturation_ratio_strictly_above_1": bool(saturation_ratio_at_bstar > 1),
    }
    report = {
        "claimed_c": float(CLAIMED),
        "q1_c": float(Q1),
        "liu_quote": float(LIU),
        "record_inequality": "0.38305 > 0.38304 > 0.382709087918741",
        "b_star": nstr(b, 40),
        "crossing": nstr(crossing, 40),
        "crossing_float": float(crossing),
        "crossing_minus_claimed": nstr(margin, 30),
        "critical_eq_residual": nstr(residual, 12),
        "g_second_derivative": nstr(g_second, 30),
        "saturation_ratio_at_bstar_for_claimed_c": nstr(
            saturation_ratio_at_bstar, 30
        ),
        "checks": checks,
        "all_ok": all(checks.values()),
    }
    path = HERE / "certs" / "analytic_margin.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
