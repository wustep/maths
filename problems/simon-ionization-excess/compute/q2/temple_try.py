#!/usr/bin/env python3
"""Temple / intermediate-Hamiltonian attempts at N=3, Z=2.

Variational UPPER bounds on E(3,2) cannot prove non-binding. A proof that
Nc(2)<3 needs a LOWER bound on E(3,2) sitting at or above a variational
UPPER bound on E(2,2).

Temple. If μ = ⟨ψ, H ψ⟩ < E_1 and σ² = ⟨H²⟩−μ², then
    E_0 ≥ μ − σ² / (E_1 − μ).
On H(3,2) the essential spectrum starts at E(2,2) by HVZ. Every Slater
trial we evaluate has μ > E(2,2)_var (and above the published helium
energy). Then μ > E_1 whenever E_1 is taken as that threshold, so Temple
does not apply. Circular if one assumes a second bound state above μ.

Intermediate Hamiltonian, crude minorants of the repulsion:
  1/|x-y| ≥ 0                 =>  E(3,2) ≥ 3 E(1,2) = −6
  1/|x-y| ≥ 1 / (|x|+|y|)     =>  still a 3-body form; a product trial
                                 for that minorant sits well below E(2,2)
Neither minorant reaches the helium Hylleraas upper bound −54353/18800.

Helium Hylleraas is imported from q1 as a comparison object only
(read, not edited).

Replay: python3 temple_try.py
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q1 = HERE.parent / "q1"
sys.path.insert(0, str(Q1))

from hylleraas import hylleraas_energy  # noqa: E402
from three_electron_try import (  # noqa: E402
    energy_1s2s_doublet,
    energy_4P,
    optimize_zeta,
)


HE_HYLL = Fraction(-54353, 18800)  # q1 he_hylleraas.py, upper on E(2,2)
HE_PUBLISHED = -2.9037243770341195  # Nakashima–Nakatsuji, comparison only
E_HYDROGENIC_Z2 = -2.0  # E(1,2) = -Z^2/2


def product_minorant_energy(zeta: float) -> float:
    """⟨∑_i (−1/2 Δ_i − 2/r_i) + ∑_{i<j} 1/(r_i+r_j)⟩ on a 1s^3 product.

    Not antisymmetrised — a lower-bound *attempt* on the minorant, not a
    legal fermionic trial for H itself. Closed hydrogenic 1s integrals
    plus a one-dimensional radial quadrature for 1/(r+s).
    """
    # 1s(ζ): ⟨−½Δ − 2/r⟩ = ζ²/2 − 2ζ each.
    one = 0.5 * zeta**2 - 2.0 * zeta
    # Radial density of r for 1s: 4 ζ³ r² e^{-2ζ r}
    # E[1/(r+s)] for two independent 1s.
    # Use a Gauss–Laguerre style grid on [0, ∞).
    xs = np.linspace(1e-6, 40.0 / max(zeta, 0.05), 800)
    w = 4.0 * zeta**3 * xs**2 * np.exp(-2.0 * zeta * xs)
    trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    w /= trap(w, xs)
    # double integral ∫∫ w(r) w(s) / (r+s)
    # Exploit 1/(r+s) = ∫_0^∞ e^{-t(r+s)} dt
    ts = np.linspace(0.0, 80.0 * zeta, 600)
    lap = trap(np.exp(-np.outer(ts, xs)) * w, xs, axis=1)
    pair = float(trap(lap**2, ts))
    return 3.0 * one + 3.0 * pair


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    Z = Fraction(2)
    E_h = hylleraas_energy(Fraction(37, 20), Fraction(37, 100), 2)
    if E_h != HE_HYLL:
        raise RuntimeError("q1 helium Hylleraas drifted")

    E_d, z_d = optimize_zeta(energy_1s2s_doublet, Z, Fraction(1, 5), Fraction(4))
    E_q, z_q = optimize_zeta(energy_4P, Z, Fraction(1, 5), Fraction(4))

    print("Helium variational upper (q1 Hylleraas):", float(E_h), "=", HE_HYLL)
    print("Published He (comparison only):", HE_PUBLISHED)
    print("3e hydrogenic 1s2 2s:", float(E_d), "zeta", z_d)
    print("3e hydrogenic 4P:    ", float(E_q), "zeta", z_q)
    print(
        "Both 3e trials sit above the helium upper bound by",
        float(E_d - E_h),
        "and",
        float(E_q - E_h),
    )

    temple_applies_doublet = float(E_d) < HE_PUBLISHED
    temple_applies_vs_hyll = float(E_d) < float(E_h)
    print(
        "Temple vs E_1 ≥ E(2,2): applies on doublet?",
        temple_applies_doublet,
        "(need μ < E_1)",
    )
    print("Temple vs Hylleraas upper used as if it were E_1?", temple_applies_vs_hyll)

    # Crude IH minorants.
    hyd = 3 * E_HYDROGENIC_Z2
    print("IH 1/|x-y|≥0: E(3,2) ≥", hyd, "  vs He upper", float(E_h), "  gap", hyd - float(E_h))

    # Scan the product minorant.
    best_m = None
    for z in np.linspace(0.3, 2.5, 45):
        e = product_minorant_energy(float(z))
        if best_m is None or e < best_m[0]:
            best_m = (e, float(z))
    print(
        f"IH 1/(|x|+|y|) product scan min ≈ {best_m[0]:.6f} at ζ={best_m[1]:.3f}  "
        f"vs He upper {float(E_h):.6f}  gap {best_m[0] - float(E_h):+.6f}"
    )

    blob = {
        "not_a_certificate": True,
        "is_new_bound": False,
        "E22_hylleraas_upper": {
            "exact": f"{HE_HYLL.numerator}/{HE_HYLL.denominator}",
            "float": float(HE_HYLL),
            "note": "variational upper on E(2,2); legal threshold only as an upper",
        },
        "E22_published_comparison": HE_PUBLISHED,
        "three_electron_variational_uppers": {
            "hydrogenic_doublet": {
                "energy": f"{E_d.numerator}/{E_d.denominator}",
                "float": float(E_d),
                "above_hylleraas": float(E_d - E_h),
            },
            "hydrogenic_4P": {
                "energy": f"{E_q.numerator}/{E_q.denominator}",
                "float": float(E_q),
                "above_hylleraas": float(E_q - E_h),
            },
        },
        "temple": {
            "applies_if_E1_is_published_He": temple_applies_doublet,
            "applies_if_E1_is_hylleraas_upper": temple_applies_vs_hyll,
            "reason": (
                "μ > E(2,2) for every trial here. Temple needs μ < E_1. "
                "Taking E_1 as the HVZ threshold E(2,2) makes the hypothesis "
                "false. No Temple number is claimed."
            ),
        },
        "intermediate_hamiltonian": {
            "repulsion_dropped": {
                "lower": hyd,
                "below_he_upper_by": hyd - float(E_h),
            },
            "triangle_minorant_product_scan": {
                "approx_float": best_m[0],
                "zeta": best_m[1],
                "below_he_upper_by": best_m[0] - float(E_h),
                "note": (
                    "Product (not fermionic) expectation of the minorant. "
                    "A number this low cannot prove E(3,2) ≥ E(2,2)."
                ),
            },
        },
        "note": (
            "No Temple or intermediate-Hamiltonian inequality certified "
            "Nc(2)<3 or Nc(2)<4. Variational uppers on E(3,2) are not used "
            "as non-binding evidence."
        ),
    }
    path = CERTS / "temple.json"
    path.write_text(json.dumps(blob, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
