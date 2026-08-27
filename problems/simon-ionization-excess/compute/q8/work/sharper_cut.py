#!/usr/bin/env python3
"""Chebyshev / Hölder on the mass-stationary endpoint slab.

Not a certificate. q4 already found that linear moment inequalities
do not replace Q>R/(R+1) by a cut that beats a leading near 1.11.
Against printed 1.1021 the cut must exceed 1/1.1021 ≈ 0.90736.

Writes certs/sharper_cut.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE.parent / "certs"
NEED = 1.0 / 1.1021


def endpoint_interval(R: float, Q: float):
    if Q <= 0.0 or Q >= 1.0:
        return None
    lo = ((1.0 - Q) / Q) * (R * R)
    hi = Q / (1.0 - Q)
    lo = max(lo, 1.0)
    hi = min(hi, R * R)
    if lo >= hi:
        return None
    return lo, hi


def chebyshev_interval(Q: float):
    """D M_{-1} >= 1 with M_{-1}=Q+(Q-1)D, Q<1.

    Equivalent to (1-Q) D^2 - Q D + 1 <= 0 when the discriminant
    is nonnegative.
    """
    disc = Q * Q + 4.0 * Q - 4.0
    if disc < 0.0:
        return None
    s = math.sqrt(disc)
    den = 2.0 * (1.0 - Q)
    lo = (Q - s) / den
    hi = (Q + s) / den
    if lo > hi:
        lo, hi = hi, lo
    return lo, hi


def first_cut(R: float, layers: str) -> float | None:
    """Smallest Q on a 1e-6 grid where the named layer is nonempty."""
    q = R / (R + 1.0)
    step = 1e-6
    qn = q
    while qn < 0.999:
        ep = endpoint_interval(R, qn)
        if ep is None:
            qn += step
            continue
        if layers == "endpoint":
            return qn
        ch = chebyshev_interval(qn)
        if ch is None:
            qn += step
            continue
        lo = max(ep[0], ch[0])
        hi = min(ep[1], ch[1])
        if lo < hi:
            return qn
        qn += step
    return None


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = []
    reopen = False
    for R in (8.0, 9.0, 9.5, 9.8, 9.9, 10.0):
        pos = R / (R + 1.0)
        ch = first_cut(R, "endpoint+chebyshev")
        rec = {
            "R": R,
            "positivity_cut": pos,
            "chebyshev_cut": ch,
            "need_vs_1.1021": NEED,
            "chebyshev_beats_1.1021": bool(ch is not None and ch > NEED),
            "positivity_beats_1.1021": bool(pos > NEED),
        }
        rows.append(rec)
        if R <= 9.0 and rec["chebyshev_beats_1.1021"]:
            reopen = True
        print(
            f"R={R:4.1f}  pos={pos:.6f}  cheb={ch}  "
            f"need>{NEED:.6f}  reopen={rec['chebyshev_beats_1.1021'] and R<=9}"
        )
    blob = {
        "status": "residue" if not reopen else "probe",
        "reason": (
            "Chebyshev D·M_{-1}≥1 (since D·M_{-1}≥M_1≥1) on the endpoint "
            "identities shrinks the (Q,D) slab. At R<=9 the new cut is "
            "still below 0.90736, so R<=9 stays dead against printed "
            "1.1021. At R=9.5 the Chebyshev cut 0.91029 would sit above "
            "that floor; that is a probe, not a wired lift. The cheap "
            "live line stays the proven R=10 split."
        ),
        "need_gamma": NEED,
        "reopens_R_le_9": reopen,
        "rows": rows,
    }
    out = CERTS / "sharper_cut.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps({k: blob[k] for k in ("status", "reopens_R_le_9")}, indent=2))
    if reopen:
        raise SystemExit("sharper_cut.py: Chebyshev reopened R<=9 (unexpected)")
    print("sharper_cut.py PASS (R<=9 still dead after Chebyshev)")


if __name__ == "__main__":
    main()
