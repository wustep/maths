#!/usr/bin/env python3
"""Replay Steinerberger's cosine test on an independently generated prefix.

This is a documented spectral fact with a verifier, not a proof that the
hidden signal persists.  Density is not claimed.

Uses the published McCranie bracket
    2.57144749846 < alpha < 2.57144749850
and Steinerberger's working value 2.5714474995.  For each Ulam number we
record the sign of cos(alpha a_n).  Float64 is enough: we only assert a
strict inequality when |cos| exceeds 1e-8.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from ulam import ulam_first

HERE = Path(__file__).resolve().parent

STEINER = 2.5714474995
ALPHA_LO = 2.57144749846
ALPHA_HI = 2.57144749850
KNOWN_EXCEPTIONS = {2, 3, 47, 69}


def classify(seq: list[int], alpha: float) -> dict:
    pos, neg, tiny, pos_vals = 0, 0, 0, []
    for a in seq:
        c = math.cos(alpha * a)
        if abs(c) < 1e-8:
            tiny += 1
            pos_vals.append((a, c))
        elif c > 0:
            pos += 1
            pos_vals.append((a, c))
        else:
            neg += 1
    return {
        "alpha": alpha,
        "N": len(seq),
        "a_N": seq[-1],
        "cos_negative": neg,
        "cos_positive": pos,
        "cos_tiny": tiny,
        "positive_or_tiny": [{"a": a, "cos": c} for a, c in pos_vals],
        "exceptions_match_published": {a for a, _ in pos_vals} <= KNOWN_EXCEPTIONS
        and all(
            any(a == e for a, _ in pos_vals) for e in KNOWN_EXCEPTIONS if e in seq
        ),
        "mean_cos": sum(math.cos(alpha * a) for a in seq) / len(seq),
    }


def packet(seq: list[int], alpha: float, ell_max: int = 8) -> list[dict]:
    N = len(seq)
    rows = []
    for ell in range(0, ell_max + 1):
        s = sum(math.cos(ell * alpha * a) for a in seq) / N
        rows.append({"ell": ell, "mean_cos": s})
    return rows


def main() -> None:
    N = 20000
    seq = ulam_first(N)
    stein = classify(seq, STEINER)
    lo = classify(seq, ALPHA_LO)
    hi = classify(seq, ALPHA_HI)
    mid = classify(seq, 0.5 * (ALPHA_LO + ALPHA_HI))
    report = {
        "N": N,
        "a_N": seq[-1],
        "known_exceptions": sorted(KNOWN_EXCEPTIONS),
        "steinerberger_2015": stein,
        "mccranie_lo": lo,
        "mccranie_hi": hi,
        "mccranie_mid": mid,
        "packet_steinerberger": packet(seq, STEINER),
        "packet_mccranie_mid": packet(seq, 0.5 * (ALPHA_LO + ALPHA_HI)),
        "note": (
            "Finite cosine sign pattern on an independently generated prefix. "
            "Does not prove a limiting measure, nor that the density exists."
        ),
    }
    out = HERE / "spectral_verify.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
