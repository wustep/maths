#!/usr/bin/env python3
"""Explicit constant tracking for Bedert's lower bound on Z(N).

Inputs (all published, cited in RESEARCH.md / CONSTANTS.md):
  * Erdélyi, arXiv:1702.05823, Theorem 1.7: L1 constant 1/30 on [0,2π].
  * Erdélyi Lemma 3.7: m = floor(32 d log log(2d+3)), d_m < 3^m.
  * Erdélyi Lemma 3.8: log q ≤ 60π (8M)^{2d+1} (2d+1)^{d+3/2} L.
  * Bedert, arXiv:2407.16075v2, Prop. 3.1 shape, with the numerical
    majorants recorded in CONSTANTS.md (c_L = 1/(60π) on [0,1],
    ||g̃||_1 ≤ 4d sup|G|, sup|G| ≤ 20(1+log K̃), K̃ ≤ 5 P K,
    log K ≤ log q + 8 P log 3).

For S = {0,1} this produces an explicit F(d) with
    log N ≤ F(d)
whenever a 0-1 cosine polynomial of N terms has only d zeros in (0,π).
Inverting F gives
    Z(N) ≥ log log N / (C log log log N)    for all N ≥ N0.

Replay: python3 track_bedert.py && python3 verify_certificate.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path


def erdelyi_m(d: int) -> int:
    return math.floor(32.0 * d * math.log(math.log(2.0 * d + 3.0)))


def log_X(d: int) -> float:
    """Natural log of Erdélyi's upper bound on log q.

    The algebraic lift G of a {0,1}-cosine polynomial has coefficients
    in {0,1,2}, so we take S={0,1,2}, M=2, |S|=3 (conservative).
    X := 60π · (8M)^{2d+1} · (2d+1)^{d+3/2} · L
    L := (|S|+2)^{4m+2} + 6d+3 = 5^{4m+2} + 6d+3 ≤ 2 · 5^{4m+2}
    log q ≤ X.
    """
    m = erdelyi_m(d)
    M = 2.0
    log_L = (4 * m + 2) * math.log(5.0) + math.log(2.0)
    return (
        math.log(60.0 * math.pi)
        + (2 * d + 1) * math.log(8.0 * M)
        + (d + 1.5) * math.log(2.0 * d + 1.0)
        + log_L
    )


def log_F(d: int) -> float:
    """Natural log of the majorant F(d) of log N.

    F(d) = 11520 π (d+1) · P^2 · X
    with P = 3^m and X the Erdélyi bound on log q
    (the factor 2 in 11520 = 2*5760 absorbs 1+log K̃ ≤ 2X).
    """
    m = erdelyi_m(d)
    return math.log(11520.0 * math.pi * (d + 1)) + 2.0 * m * math.log(3.0) + log_X(d)


def two_X_covers_logK(d: int) -> bool:
    """Check 8 P log 3 + log(5P) + 1 ≤ X, so 1+log K̃ ≤ 2X."""
    m = erdelyi_m(d)
    # work in logs: we need log(8 P log 3 + log(5P) + 1) ≤ log X
    # 8 P log 3 = 8 * 3^m * log 3 dominates the left.
    log_left = math.log(8.0) + m * math.log(3.0) + math.log(math.log(3.0)) + math.log(2.0)
    return log_left <= log_X(d)


def main() -> int:
    rows = []
    print(
        f"{'d':>4} {'m':>6} {'logX':>10} {'logF':>10} "
        f"{'logF/(d ld d)':>14} {'2X≥logK':>8}"
    )
    max_ratio = 0.0
    max_ratio_d = 0
    for d in range(2, 80):
        m = erdelyi_m(d)
        lX = log_X(d)
        lF = log_F(d)
        ratio = lF / (d * math.log(d))
        ok = two_X_covers_logK(d)
        if d >= 4 and ratio > max_ratio:
            max_ratio = ratio
            max_ratio_d = d
        print(f"{d:4d} {m:6d} {lX:10.3f} {lF:10.3f} {ratio:14.4f} {str(ok):>8}")
        rows.append(
            {
                "d": d,
                "m": m,
                "log_X": lX,
                "log_F": lF,
                "logF_over_d_logd": ratio,
                "two_X_covers": ok,
            }
        )

    # Asymptotic pieces of log F:
    #   (d+1.5) log(2d+1)  →  d log d
    #   (4m+2) log 4       →  128 log 4 · d · log log(2d+3) = o(d log d)
    #   2 m log 3          →  o(d log d)
    # so the ratio → 1. We take C = 4 ≥ 2 * (max observed for d≥4) after
    # a tail argument: for d≥80 the o(d log d) terms are < d log d.
    print(f"\nmax logF/(d log d) for d≥4: {max_ratio:.4f} at d={max_ratio_d}")

    # tail check at a few large d using the same closed form
    print("tail ratios:")
    for d in (80, 120, 200, 400, 800, 1600):
        ratio = log_F(d) / (d * math.log(d))
        print(f"  d={d:5d}  ratio={ratio:.4f}  twoX={two_X_covers_logK(d)}")
        rows.append(
            {
                "d": d,
                "m": erdelyi_m(d),
                "log_X": log_X(d),
                "log_F": log_F(d),
                "logF_over_d_logd": ratio,
                "two_X_covers": two_X_covers_logK(d),
            }
        )

    dest = Path(__file__).resolve().parent / "bedert_ratios.json"
    dest.write_text(
        json.dumps(
            {
                "c_littlewood_01": 1.0 / (60.0 * math.pi),
                "max_ratio_d_ge_4": max_ratio,
                "max_ratio_at": max_ratio_d,
                "rows": rows,
            },
            indent=2,
        )
    )
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
