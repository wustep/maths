#!/usr/bin/env python3
"""Replay Seiringer–Solovej remainder absorption at d=1.

Seiringer–Solovej, arXiv:2303.04504v2, Corollary 2 and the Airy evaluation
after (8): R_1 = (-3/a)^3 / 16, where a is the largest real zero of Ai.
After Hoffmann–Ostenhof absorption this is a pure kinetic bound
K/K^{cl} ≥ R_1 ≈ 0.132, hence L/Lcl ≤ 1/sqrt(R_1) ≈ 2.75, weaker than
CCR 1.44655 and weaker than Rumin d/(d+4)=1/5.

This file encloses the Airy zero by a series for Ai on the negative axis
and pushes a directed R_1 through the conversion. It does not beat 1.44655.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from constants import CCR_L, FHJN_L, Q1_L, ratio_from_k_over_kcl

HERE = Path(__file__).resolve().parent

# Ai(z) = 3^{-2/3}/Γ(2/3) * f(z) - 3^{-1/3}/Γ(1/3) * g(z)
# f(z) = Σ_{k≥0} 3^k (1/3)_k z^{3k} / (3k)!
# g(z) = Σ_{k≥0} 3^k (2/3)_k z^{3k+1} / (3k+1)!


def ai_series(z: float, nterms: int = 40) -> float:
    """Ai(z) via the standard power series. Fine for |z| ≲ 4."""
    c1 = (3.0 ** (-2.0 / 3.0)) / math.gamma(2.0 / 3.0)
    c2 = (3.0 ** (-1.0 / 3.0)) / math.gamma(1.0 / 3.0)
    z3 = z * z * z
    # f_{k+1} = f_k * z^3 / ((3k+2)(3k+3)),  f_0 = 1
    # g_{k+1} = g_k * z^3 / ((3k+3)(3k+4)),  g_0 = z
    fk = 1.0
    gk = z
    f = fk
    g = gk
    for k in range(nterms - 1):
        fk *= z3 / ((3 * k + 2) * (3 * k + 3))
        gk *= z3 / ((3 * k + 3) * (3 * k + 4))
        f += fk
        g += gk
    return c1 * f - c2 * g


def airy_zero_bracket() -> dict:
    """Largest real zero of Ai lies in (-2.3381074105, -2.3381074104).

    Sign check: Ai is positive just right of the largest real zero and
    negative just left of it (standard Airy oscillation on the negative axis,
    Ai(x)>0 for x>a_1).
    """
    lo = -2.3381074105
    hi = -2.3381074104
    ai_lo = ai_series(lo)
    ai_hi = ai_series(hi)
    # Ai(hi) should be >0, Ai(lo)<0.
    if not (ai_lo < 0.0 < ai_hi):
        raise RuntimeError(f"Airy sign bracket failed: Ai({lo})={ai_lo}, Ai({hi})={ai_hi}")
    # Conservative: a in (lo, hi), so |a| in (-hi, -lo) = (2.3381074104, 2.3381074105)
    a_abs_lo = -hi
    a_abs_hi = -lo
    return {
        "a_lo": lo,
        "a_hi": hi,
        "Ai_lo": ai_lo,
        "Ai_hi": ai_hi,
        "a_abs_lo": a_abs_lo,
        "a_abs_hi": a_abs_hi,
    }


def r1_from_a_abs(a_abs: float) -> float:
    # R_1 = (-3/a)^3 / 16 = (3/|a|)^3 / 16
    return (3.0 / a_abs) ** 3 / 16.0


def main() -> int:
    br = airy_zero_bracket()
    # Directed: larger |a| makes R_1 smaller (worse kinetic lower bound).
    # For an upper bound on L/Lcl we need a lower bound on R_1, hence the
    # smaller |a|. For "does not beat CCR" we need L/Lcl_upper still > 1.44655,
    # so we take the *best* (largest) R_1 in the bracket — even that is ~0.132.
    r1_best = r1_from_a_abs(br["a_abs_lo"])  # smaller |a|, larger R_1
    r1_worst = r1_from_a_abs(br["a_abs_hi"])
    # Pad a relative 1e-9 for series truncation / gamma rounding.
    r1_upper = r1_best * (1.0 + 1e-8)
    l_ratio_from_best = ratio_from_k_over_kcl(r1_upper)
    out = {
        "paper": "arXiv:2303.04504v2",
        "formula": "R_1 = (3/|a|)^3 / 16, a = largest real zero of Ai",
        "bracket": br,
        "R1_upper": r1_upper,
        "R1_lower": r1_worst * (1.0 - 1e-8),
        "K_over_Kcl_upper": r1_upper,
        "L_over_Lcl_from_best_R1": l_ratio_from_best,
        "beats_CCR": bool(l_ratio_from_best < CCR_L),
        "beats_FHJN": bool(l_ratio_from_best < FHJN_L),
        "beats_q1": bool(l_ratio_from_best < Q1_L),
        "note": (
            "Hoffmann–Ostenhof absorption of the Seiringer–Solovej remainder. "
            "R_1 ≈ 0.132 is weaker than CCR 0.47789 and weaker than Rumin 1/5. "
            "Not a dent of 1.44655."
        ),
    }
    dest = HERE / "certs" / "ss_airy.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print("=== q3 Seiringer–Solovej Airy R_1 ===")
    print(f"a in ({br['a_lo']}, {br['a_hi']})")
    print(f"Ai(lo)={br['Ai_lo']:.3e}  Ai(hi)={br['Ai_hi']:.3e}")
    print(f"R1_upper         = {r1_upper:.8f}")
    print(f"L/Lcl from that  = {l_ratio_from_best:.6f}")
    print(f"beats CCR        = {out['beats_CCR']}")
    print(f"wrote {dest}")
    if out["beats_CCR"]:
        raise SystemExit("unexpected: SS R_1 beat CCR — inspect")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
