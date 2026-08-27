"""Analytic first-crossing of pure Example 4 on the {b,1} ray.

For β=1 and b in (1-1/√2, 1/2], Liu's a(t) saturates Π_{b,b}(0,0)=1/2,
so Hmix=1.  The equality 2-point then has mean

    f(b) = 1 - (1-b) h(b).

For b ≤ 1-1/√2, Example 4 coincides with iid and a_eq < 0 (since
that interval lies below φ), so those b do not cross.  Hence the
first-crossing of the ray is min f on (1-1/√2, 1/2], i.e. the unique
critical point of (1-b)h(b) in the interval:

    h(b) = (1-b) log2((1-b)/b).

Replay: python3 solve_crossing.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from mpmath import findroot, log, mp, mpf, nstr, sqrt

mp.dps = 80
LN2 = log(2)


def hm(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return -(p * log(p) + (1 - p) * log(1 - p)) / LN2


def critical_eq(b):
    b = mpf(b)
    return hm(b) - (1 - b) * log((1 - b) / b) / LN2


def second_deriv_g(b):
    """d²/db² of g(b)=(1-b)h(b).  Negative => local max of g => local min of f."""
    b = mpf(b)
    # g' = -h(b) + (1-b) log2((1-b)/b)
    # h' = log2((1-b)/b)
    # h'' = -1/(b(1-b) ln 2)
    # g'' = -h' + [ -log2((1-b)/b) + (1-b) * h'' ]
    #     = -2 log2((1-b)/b) - 1/(b ln 2)
    return -2 * log((1 - b) / b) / LN2 - 1 / (b * LN2)


def main():
    thresh = 1 - 1 / sqrt(2)
    phi = (3 - sqrt(5)) / 2
    b = findroot(critical_eq, mpf("0.2965"))
    hb = hm(b)
    c = 1 - (1 - b) * hb
    gpp = second_deriv_g(b)
    f_thresh = 1 - (1 / sqrt(2)) * hm(thresh)
    f_half = 1 - mpf("0.5") * hm(mpf("0.5"))

    # residual of the critical equation
    residual = float(critical_eq(b))

    report = {
        "b_star": nstr(b, 30),
        "b_star_float": float(b),
        "h_b": nstr(hb, 30),
        "crossing": nstr(c, 30),
        "crossing_float": float(c),
        "critical_eq_residual": residual,
        "g_second_deriv": nstr(gpp, 20),
        "g_second_deriv_negative": bool(gpp < 0),
        "f_at_thresh": nstr(f_thresh, 24),
        "f_at_half": nstr(f_half, 24),
        "thresh": nstr(thresh, 24),
        "phi": nstr(phi, 24),
        "claimed_c": 0.38304,
        "claimed_below_crossing": 0.38304 < float(c),
        "beats_repo_0_38285": float(c) > 0.38285,
        "beats_liu": float(c) > 0.382709087918741,
    }
    path = Path(__file__).resolve().parent / "certs" / "analytic_crossing.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if residual > 1e-20 or gpp >= 0 or 0.38304 >= float(c):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
