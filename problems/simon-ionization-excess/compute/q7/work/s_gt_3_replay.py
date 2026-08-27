#!/usr/bin/env python3
"""Replay the q2 s=4 two-shell dipole: I_s is exactly -1025/2048.

HPS Lemma 4.3 needs I_s(ν)≥0 for every ν ⊥ radial. The closed
two-shell form (q2, ℓ=1)

    Q_s = α² t^{s-1} + β² + αβ (t^{s+ℓ} + t^ℓ)

at s=4, t=1/8, α=16, β=-1 is the rational -1025/2048. b(4) cannot
enter Theorem 2.2.

Writes certs/s_gt_3.json.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE.parent / "certs"


def Q_two_shell(s: int, ell: int, t: Fraction, alpha: Fraction, beta: Fraction) -> Fraction:
    return (
        alpha**2 * t ** (s - 1)
        + beta**2
        + alpha * beta * (t ** (s + ell) + t**ell)
    )


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    Q = Q_two_shell(4, 1, Fraction(1, 8), Fraction(16), Fraction(-1))
    expected = Fraction(-1025, 2048)
    if Q != expected:
        raise SystemExit(f"s_gt_3_replay.py FAIL: got {Q}, expected {expected}")
    Q3 = Q_two_shell(3, 1, Fraction(1, 8), Fraction(16), Fraction(-1))
    if Q3 < 0:
        raise SystemExit("s_gt_3_replay.py FAIL: s=3 same weights should stay nonnegative")
    blob = {
        "status": "residue",
        "arxiv": "2504.18487v1",
        "Q_s4_t_1_8_alpha_16_beta_-1": str(Q),
        "Q_value": float(Q),
        "Q_s3_same_weights": str(Q3),
        "sign_s4": "negative",
        "sign_s3": "nonnegative",
        "reason": (
            "Lemma 4.3 needs I_s(ν)≥0. Two-shell opposite dipoles give "
            "Q=-1025/2048 at s=4. b(4) cannot be used in Theorem 2.2."
        ),
    }
    out = CERTS / "s_gt_3.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps(blob, indent=2))
    print("s_gt_3_replay.py PASS (s>3 still residue)")


if __name__ == "__main__":
    main()
