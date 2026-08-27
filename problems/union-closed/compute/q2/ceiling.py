"""Analytic ceiling for any 2-sample bit protocol on {b,1}.

On support {b,1} with P(S=1)=a, a product coupling of (S,T) puts all
OR-entropy on the (b,b) cell.  Any protocol satisfies
h(Π_{b,b}(0,0)) ≤ 1, so

    ratio ≤ (1-a) / h(b),
    first-crossing ≤ f(b) := 1 − (1-b) h(b).

Example 4 saturates h=1 on (1−1/√2, 1/2], so the best crossing in
this class is min f on that interval.  That minimum is the unique
critical point of (1-b)h(b):

    h(b) = (1-b) log2((1-b)/b)

and equals 0.3830513565868….  No mix of iid, Example 4, Example 5,
max-entropy, or any other 2-sample bit protocol can certify a {b,1}
frequency above this number.  It is not 1/2.

Replay: python3 ceiling.py
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import findroot, log, mp, mpf, nstr, sqrt

mp.dps = 80
LN2 = log(2)

CLAIMED_C = 0.38304
LIU_QUOTE = 0.382709087918741
REPO_C = 0.38285


def hm(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return -(p * log(p) + (1 - p) * log(1 - p)) / LN2


def critical_eq(b):
    b = mpf(b)
    return hm(b) - (1 - b) * log((1 - b) / b) / LN2


def second_deriv_g(b):
    """d²/db² of g(b)=(1-b)h(b). Negative => local min of f=1-g."""
    b = mpf(b)
    return -2 * log((1 - b) / b) / LN2 - 1 / (b * LN2)


def f_of(b):
    b = mpf(b)
    return 1 - (1 - b) * hm(b)


def main():
    thresh = 1 - 1 / sqrt(2)
    phi = (3 - sqrt(5)) / 2
    b = findroot(critical_eq, mpf("0.2965"))
    c = f_of(b)
    gpp = second_deriv_g(b)
    residual = float(critical_eq(b))

    # Any protocol with h(Π_{b,b}) = η ≤ 1 has equality mean
    # 1-(1-b)h(b)/η ≥ f(b), with equality iff η=1.
    # So the first-crossing is ≤ min f, with equality only if some
    # protocol saturates h=1 at the minimizer (Example 4 does).
    report = {
        "statement": (
            "any 2-sample bit protocol, product coupling of (S,T), "
            "family {b,1}: first-crossing ≤ min f, f(b)=1-(1-b)h(b)"
        ),
        "b_star": nstr(b, 30),
        "b_star_float": float(b),
        "h_b": nstr(hm(b), 30),
        "ceiling": nstr(c, 30),
        "ceiling_float": float(c),
        "critical_eq_residual": residual,
        "g_second_deriv": nstr(gpp, 20),
        "g_second_deriv_negative": bool(gpp < 0),
        "f_at_thresh": nstr(f_of(thresh), 24),
        "f_at_half": nstr(f_of(mpf("0.5")), 24),
        "f_at_phi": nstr(f_of(phi), 24),
        "thresh": nstr(thresh, 24),
        "phi": nstr(phi, 24),
        "why_half_is_not_this_class": (
            "f(1/2)=1/2, but the minimizer on the saturation "
            "interval is at b*≈0.2965, where f=0.383051…"
        ),
        "claimed_c": CLAIMED_C,
        "claimed_below_ceiling": CLAIMED_C < float(c),
        "beats_repo_0_38285": float(c) > REPO_C,
        "beats_liu": float(c) > LIU_QUOTE,
        "half_above_ceiling": 0.5 > float(c),
        "note": (
            "this is a ceiling for the hypothesis class, not a new "
            "frequency constant.  0.38304 is already below it."
        ),
    }
    path = Path(__file__).resolve().parent / "certs" / "ceiling.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if residual > 1e-20 or gpp >= 0 or CLAIMED_C >= float(c) or float(c) >= 0.5:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
