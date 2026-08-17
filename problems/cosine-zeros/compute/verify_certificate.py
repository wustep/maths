#!/usr/bin/env python3
"""Independent replay of the explicit Bedert constant.

Rebuilds F(d) from the formulas in CONSTANTS.md (no stored magic numbers
except the published 1/30, 32, 3^m, 60π) and checks:

  (i)  1 + log K̃ ≤ 2X  for 2 ≤ d ≤ 400
  (ii) log F(d) ≤ 200 d log d  for 4 ≤ d ≤ 2000
  (iii) inversion: if log log N > 200 d log d then F(d) < log N
        is impossible, so a 0-1 cosine N-sum has more than d zeros in (0,π)

Claim (see WALKTHROUGH / RESEARCH): we do **not** beat Bedert's exponent
(log log N)^{1-o(1)}. We name the constant in his Theorem 1.3:
    Z(N) ≥ log log N / (200 log log log N)
whenever the right-hand side is ≥ 4.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def erdelyi_m(d: int) -> int:
    return math.floor(32.0 * d * math.log(math.log(2.0 * d + 3.0)))


def log_X(d: int) -> float:
    """log of Erdélyi Lemma 3.8 majorant of log q.

    Algebraic lift has coefficients in {0,1,2}: M=2, |S|=3.
    """
    m = erdelyi_m(d)
    M = 2.0
    log_L = (4 * m + 2) * math.log(5.0) + math.log(2.0)  # L ≤ 2 · 5^{4m+2}
    return (
        math.log(60.0 * math.pi)
        + (2 * d + 1) * math.log(8.0 * M)
        + (d + 1.5) * math.log(2.0 * d + 1.0)
        + log_L
    )


def log_F(d: int) -> float:
    """log of F(d) = 11520 π (d+1) 3^{2m} X."""
    m = erdelyi_m(d)
    return math.log(11520.0 * math.pi * (d + 1)) + 2.0 * m * math.log(3.0) + log_X(d)


def two_X_covers(d: int) -> bool:
    """8 P log 3 + log(5P) + 1 ≤ X."""
    m = erdelyi_m(d)
    # left ≤ 16 P log 3  (P≥1, log(5P)+1 ≤ 8 P log 3)
    log_left = math.log(16.0) + m * math.log(3.0) + math.log(math.log(3.0))
    return log_left <= log_X(d)


def main() -> int:
    failures = []

    for d in range(2, 401):
        if not two_X_covers(d):
            failures.append(f"two_X_covers failed at d={d}")

    max_ratio = 0.0
    max_at = 0
    for d in range(4, 2001):
        ratio = log_F(d) / (d * math.log(d))
        if ratio > max_ratio:
            max_ratio = ratio
            max_at = d
        if ratio > 200.0:
            failures.append(f"logF/(d log d)={ratio:.4f} > 200 at d={d}")

    # spot-check inversion arithmetic: log F ≤ 200 d log d
    # ⇒ log log N ≤ 200 d log d whenever log N ≤ F(d)
    for d in (4, 10, 20, 50, 100, 400, 2000):
        if log_F(d) > 200.0 * d * math.log(d) + 1e-9:
            failures.append(f"inversion seed failed at d={d}")

    cert = {
        "c_littlewood_01_with_cosine_half": 1.0 / (120.0 * math.pi),
        "F_prefactor": "11520 π (d+1) 3^{2m} X",
        "C": 200,
        "max_logF_over_d_logd_d_4_to_2000": max_ratio,
        "max_at_d": max_at,
        "two_X_checked": "d=2..400",
        "ratio_checked": "d=4..2000",
        "claim": (
            "Z(N) >= loglog N / (200 logloglog N) whenever the RHS is >= 4. "
            "Does not beat Bedert's exponent (log log N)^{1-o(1)}."
        ),
        "failures": failures,
    }
    dest = Path(__file__).resolve().parent / "certificate.json"
    dest.write_text(json.dumps(cert, indent=2))
    print(json.dumps({k: cert[k] for k in cert if k != "failures"}, indent=2))
    if failures:
        print("FAILURES:")
        for f in failures:
            print(" ", f)
        return 1
    print(f"max ratio d=4..2000: {max_ratio:.4f} at d={max_at}")
    print("certificate: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
