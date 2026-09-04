#!/usr/bin/env python3
"""Stdlib-only independent reconstruction of the q14 span bound.

Uses Decimal rather than mpmath intervals, parses the frozen q13 matrix
and face summary directly, and adds a 1e-40 outward safety pad.
"""

from __future__ import annotations

import json
from decimal import Decimal, getcontext
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q13 = HERE.parent / "q13" / "certs"
MATRIX = Q13 / "beta3_mid_R10_n37_t0p9119.txt"
FACES = Q13 / "beta3_mid_faces_R10_n37_t0p9119.txt"

getcontext().prec = 80
D = Decimal
PAD = D("1e-40")
MATRIX_PAD = D("1e-12")


def f(t: Decimal) -> Decimal:
    return (1 + t**3) / (1 + t**2)


def face_map() -> dict[str, str]:
    ans = {}
    for line in FACES.read_text().splitlines():
        key, _, value = line.partition(" ")
        ans[key] = value.strip()
    return ans


def main() -> None:
    R = D(10)
    n = 37
    target = D("0.9119")
    q = (R.ln() / D(n)).exp()
    P_hi = (q - 1) / (q + 1) + PAD
    u = ((1 + D(2).sqrt()).ln() / D(3)).exp()
    t_star = u - 1 / u
    f_min_lo = D(3) * t_star / D(2) - PAD
    t_far = q * q / R
    t_near = 1 / q
    f_far_hi = f(t_far) + PAD
    f_near_hi = f(t_near) + PAD
    span_hi = max(f_far_hi, f_near_hi) - f_min_lo
    error_hi = P_hi * span_hi + MATRIX_PAD
    gamma_lo = target - error_hi
    leading_hi = 1 / gamma_lo + PAD
    cut = R / (R + 1)

    faces = face_map()
    nfaces = (1 << n) - 1
    face_ok = (
        int(faces["n"]) == n
        and abs(D(faces["gamma_target"]) - target) < D("1e-15")
        and int(faces["n_faces"]) == nfaces
        and int(faces["gray_i"]) == nfaces
        and int(faces["copositive"]) == 1
        and int(faces["singular_or_illconditioned"]) == 0
        and D(faces["min_mMm_safe"]) > 0
    )

    toks = MATRIX.read_text().split()
    matrix_n = int(toks[0])
    matrix_target = D(toks[1])
    c = [D(x) for x in toks[2 : 2 + matrix_n]]
    flat_A = [D(x) for x in toks[2 + matrix_n :]]
    if len(flat_A) != matrix_n * matrix_n:
        raise SystemExit("bad matrix length")
    stored_F = []
    for i in range(matrix_n):
        for j in range(matrix_n):
            aij = flat_A[i * matrix_n + j]
            stored_F.append(2 * aij / (c[i] + c[j]))
    stored_min = min(stored_F)
    stored_max = max(stored_F)

    checks = {
        "face_certificate_ok": face_ok,
        "matrix_header_ok": matrix_n == n and abs(matrix_target - target) < D("1e-15"),
        "far_endpoint_below_t_star": t_far < t_star,
        "near_endpoint_above_t_star": t_near > t_star,
        "far_value_dominates_near": f_far_hi > f_near_hi,
        "stored_F_above_f_min": stored_min + D("1e-14") >= f_min_lo,
        "stored_F_below_analytic_max": stored_max <= f_far_hi + D("1e-14"),
        "gamma_below_cut": gamma_lo < cut,
        "leading_below_1.1002": leading_hi < D("1.1002"),
        "leading_below_q13_1.1006": leading_hi < D("1.1006"),
    }
    ok = all(checks.values())
    blob = {
        "implementation": "Python stdlib Decimal, 80 digits, 1e-40 transcendental pad",
        "matrix_rounding_pad": str(MATRIX_PAD),
        "q": str(q),
        "P_upper": str(P_hi),
        "t_star": str(t_star),
        "f_min_lower": str(f_min_lo),
        "f_far_upper": str(f_far_hi),
        "f_near_upper": str(f_near_hi),
        "stored_F_min": str(stored_min),
        "stored_F_max": str(stored_max),
        "span_upper": str(span_hi),
        "error_upper": str(error_hi),
        "beta3_lower": str(gamma_lo),
        "leading_upper": str(leading_hi),
        "cut": str(cut),
        "checks": checks,
        "ok": ok,
    }
    out = CERTS / "span_stdlib.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("stored F range", stored_min, stored_max)
    print("span <=", span_hi, "error <=", error_hi)
    print("beta3 >=", gamma_lo, "leading <=", leading_hi)
    print("wrote", out)
    if not ok:
        raise SystemExit("verify_span.py FAIL")
    print("verify_span.py PASS")


if __name__ == "__main__":
    main()
