#!/usr/bin/env python3
"""Interval certificate for the q14 finite-range reweighting bound.

q13 proved the discrete mid-radius Rayleigh quotient phi is at least
0.9119 for R=10 and n=37.  Its final passage back to the continuous
radial quotient used the coarse range f_min <= lambda_i <= 1.  Here we
use the actual geometric-bin range

    f_min <= lambda_i <= max(f(q^2/R), f(1/q)) = f(q^2/R),

where q=R^(1/n).  The same total-variation estimate therefore costs
P times this smaller span, P=(q-1)/(q+1).

This implementation uses mpmath interval arithmetic and validates the
complete frozen q13 Gray-code face summary before writing the result.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q13_CERTS = HERE.parent / "q13" / "certs"
MATRIX = Q13_CERTS / "beta3_mid_R10_n37_t0p9119.txt"
FACES = Q13_CERTS / "beta3_mid_faces_R10_n37_t0p9119.txt"

mp.dps = 90
iv.dps = 90


def S(x, digits: int = 50) -> str:
    return nstr(x, digits, strip_zeros=False)


def bounds(x) -> list[str]:
    return [S(mpf(x.a)), S(mpf(x.b))]


def f_iv(t):
    return (1 + t**3) / (1 + t**2)


def parse_faces(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        key, _, value = line.partition(" ")
        out[key] = value.strip()
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    R_int = 10
    n = 37
    target_text = "0.9119"
    target = mpf(target_text)

    faces = parse_faces(FACES)
    total_faces = (1 << n) - 1
    face_checks = {
        "n_is_37": int(faces["n"]) == n,
        "target_is_0.9119": abs(mpf(faces["gamma_target"]) - target) < mpf("1e-15"),
        "all_faces_visited": int(faces["gray_i"]) == total_faces,
        "face_count_matches": int(faces["n_faces"]) == total_faces,
        "copositive": int(faces["copositive"]) == 1,
        "positive_safe_margin": mpf(faces["min_mMm_safe"]) > 0,
        "no_residual_skips": int(faces["singular_or_illconditioned"]) == 0,
    }
    if not all(face_checks.values()):
        raise SystemExit(f"frozen q13 face certificate failed: {face_checks}")

    matrix_tokens = MATRIX.read_text().split()
    if int(matrix_tokens[0]) != n or abs(mpf(matrix_tokens[1]) - target) >= mpf("1e-15"):
        raise SystemExit("frozen q13 matrix header mismatch")

    R = iv.mpf(R_int)
    q = iv.exp(iv.log(R) / n)
    P = (q - 1) / (q + 1)
    u = iv.exp(iv.log(1 + iv.sqrt(2)) / 3)
    t_star = u - 1 / u
    f_min = iv.mpf(3) * t_star / 2
    t_far = q**2 / R
    t_near = 1 / q
    f_far = f_iv(t_far)
    f_near = f_iv(t_near)

    # f decreases to t_star and increases after it.  For any bin pair,
    # the minimum is therefore at t_star, at a left endpoint <=1/q, or
    # at a right endpoint >=q^2/R.  These strict interval comparisons
    # certify that f(q^2/R) is the largest of those three possibilities.
    monotone_checks = {
        "q2_over_R_lt_t_star": mpf(t_far.b) < mpf(t_star.a),
        "t_star_lt_1_over_q": mpf(t_star.b) < mpf(t_near.a),
        "f_near_lt_f_far": mpf(f_near.b) < mpf(f_far.a),
    }
    if not all(monotone_checks.values()):
        raise SystemExit(f"bin-span monotonicity failed: {monotone_checks}")

    span_hi = mpf(f_far.b) - mpf(f_min.a)
    P_hi = mpf(P.b)
    # The frozen matrix is written in binary64 decimal form. q13's
    # independent rebuild differs by <6e-16 relatively; deducting 1e-12
    # here also covers that representation step by a wide margin.
    matrix_rounding_pad = mpf("1e-12")
    error_hi = P_hi * span_hi + matrix_rounding_pad
    gamma_lo = target - error_hi
    cut = mpf(R_int) / (R_int + 1)
    leading_hi = 1 / gamma_lo

    old_error_hi = mpf("0.003293890946025857")
    numeric_checks = {
        "span_positive": span_hi > 0,
        "new_error_lt_q13_error": error_hi < old_error_hi,
        "gamma_below_cut": gamma_lo < cut,
        "leading_lt_1.1002": leading_hi < mpf("1.1002"),
        "printed_beats_1.1006": mpf("1.1002") < mpf("1.1006"),
    }
    if not all(numeric_checks.values()):
        raise SystemExit(f"q14 numerical check failed: {numeric_checks}")

    blob = {
        "arxiv": "2504.18487v1",
        "source": "q13 R=10 n=37 target=0.9119 complete Gray faces",
        "proof": (
            "For each mass vector, I/D is a reweighting of the F-average "
            "by factors in [1/q,q]. Its total-variation distance from the "
            "mid-radius weights is at most P=(q-1)/(q+1). Each lambda_i is "
            "a convex combination of F_ij. Geometric-bin monotonicity gives "
            "f_min <= F_ij <= f(q^2/R), so the loss is at most "
            "P*(f(q^2/R)-f_min), rather than P*(1-f_min)."
        ),
        "R": R_int,
        "n": n,
        "target": target_text,
        "q_interval": bounds(q),
        "P_interval": bounds(P),
        "t_star_interval": bounds(t_star),
        "q2_over_R_interval": bounds(t_far),
        "one_over_q_interval": bounds(t_near),
        "f_min_interval": bounds(f_min),
        "f_q2_over_R_interval": bounds(f_far),
        "f_one_over_q_interval": bounds(f_near),
        "F_span_upper": S(span_hi),
        "reweight_error_upper": S(error_hi),
        "matrix_rounding_pad": S(matrix_rounding_pad),
        "q13_error_upper": S(old_error_hi),
        "beta3_lower": S(gamma_lo),
        "leading_upper": S(leading_hi),
        "printed_leading": "1.1002",
        "cut": S(cut),
        "monotone_checks": monotone_checks,
        "face_checks": face_checks,
        "numeric_checks": numeric_checks,
        "q13_faces": {
            "path": str(FACES.relative_to(HERE.parent.parent.parent.parent)),
            "sha256": sha256(FACES),
            "min_mMm_safe": faces["min_mMm_safe"],
            "min_phi_safe": faces["min_phi_safe"],
            "interior_critical": faces["interior_critical"],
        },
        "q13_matrix": {
            "path": str(MATRIX.relative_to(HERE.parent.parent.parent.parent)),
            "sha256": sha256(MATRIX),
        },
        "ok": True,
    }
    out = CERTS / "span_bound.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("F span <=", S(span_hi, 18))
    print("error <=", S(error_hi, 18), "(q13:", S(old_error_hi, 18) + ")")
    print("beta3 >=", S(gamma_lo, 18))
    print("1/beta3 <=", S(leading_hi, 18), "printed 1.1002")
    print("wrote", out)
    print("span_bound.py PASS")


if __name__ == "__main__":
    main()
