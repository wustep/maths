#!/usr/bin/env python3
"""Hylleraas / Chandrasekhar variational certificate that H^- binds.

The two-electron Hamiltonian (infinite nuclear mass, Hartree atomic units)

    H = -1/2 Δ_1 - 1/2 Δ_2 - Z/r_1 - Z/r_2 + 1/r_12

is evaluated exactly on two classical trial families. The hydrogen
threshold is E(1, 1) = -1/2. A normalized trial with energy strictly
below -1/2 proves E(2, 1) < E(1, 1), hence N0(1) >= 2.

Closed-form integrals: Hylleraas coordinates for
ψ = exp(-α (r1+r2)) (1 + c r12), and hydrogenic factorisation plus the
Coulomb integral for Chandrasekhar
Φ = exp(-a r1 - b r2) + exp(-b r1 - a r2).
Both energies are rational functions of the parameters. Rational
parameter points therefore give an exact rational energy, compared to
-1/2 by integer arithmetic.

This is a replay of Hylleraas / Bethe / Chandrasekhar. Combined with
Lieb's Nc < 2Z+1 (invoked, not re-proved) it recovers N0(1) = 2, which
Lieb, Phys. Rev. A 29, 3018 (1984) already recorded. It is not a new
bound.

Replay:

    python3 hylleraas.py
    python3 hylleraas.py --write-certs
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_DIR = HERE / "certs"

# Primary Hylleraas (1 + c r12) point: tiny integers, strict gap 7/801.
HYLL_ALPHA = Fraction(5, 6)
HYLL_C = Fraction(1, 2)

# Stronger Chandrasekhar point (near the classical a≈1.039, b≈0.283).
CHAND_A = Fraction(26, 25)
CHAND_B = Fraction(7, 25)

# Frozen-inner-electron point from Høgaasen–Richard–Sorba (arXiv:0907.2614).
CHAND_FROZEN_A = Fraction(1)
CHAND_FROZEN_B = Fraction(2, 7)


# ---------------------------------------------------------------------------
# Hylleraas coordinates
# ---------------------------------------------------------------------------
# For an S-state function F even in t = r2 - r1,
#
#   ∫ F d³r1 d³r2 = 2π² ∫_0^∞ ds ∫_0^s du ∫_0^u dt (s² - t²) u F
#
# with s = r1+r2, u = r12. Overall 2π² cancels in every Rayleigh quotient.


def _J(p: int, q: int, r: int, k: Fraction) -> Fraction:
    """∫ e^{-k s} s^p t^q u^r  on the Hylleraas 1/8-octant (no measure)."""
    return (
        Fraction(1, q + 1)
        * Fraction(1, r + q + 2)
        * factorial(p + q + r + 2)
        / k ** (p + q + r + 3)
    )


def _I_measure(p: int, q: int, r: int, k: Fraction) -> Fraction:
    """∫ e^{-k s} s^p t^q u^r (s² - t²) u  on the Hylleraas 1/8-octant."""
    return factorial(p + q + r + 5) / k ** (p + q + r + 6) * (
        Fraction(1, (q + 1) * (r + q + 3)) - Fraction(1, (q + 3) * (r + q + 5))
    )


def hylleraas_TVN(alpha: Fraction, c: Fraction, Z: Fraction | int):
    """Kinetic, potential, overlap for ψ = exp(-α(r1+r2)) (1 + c r12).

    Returns (T, V, N) in units of 2π². Energy is (T+V)/N.
    """
    Z = Fraction(Z)
    k = 2 * alpha
    I000 = _I_measure(0, 0, 0, k)
    I001 = _I_measure(0, 0, 1, k)
    I002 = _I_measure(0, 0, 2, k)
    N = I000 + 2 * c * I001 + c**2 * I002

    # ⟨1/r1 + 1/r2⟩: 4s/(s²-t²) times the measure leaves 4 s u.
    Vne = -Z * 4 * (
        _J(1, 0, 1, k) + 2 * c * _J(1, 0, 2, k) + c**2 * _J(1, 0, 3, k)
    )

    def st2(rpow: int) -> Fraction:
        return _J(2, 0, rpow, k) - _J(0, 2, rpow, k)

    Vee = st2(0) + 2 * c * st2(1) + c**2 * st2(2)
    V = Vne + Vee

    # |∇₁ψ|² + |∇₂ψ|² reduced in (s,t,u). The cross piece is
    # 4s (u²-t²) / (u (s²-t²)) and cancels the measure.
    T = (
        alpha**2 * N
        + c**2 * I000
        - 2
        * alpha
        * c
        * (
            _J(1, 0, 2, k)
            - _J(1, 2, 0, k)
            + c * _J(1, 0, 3, k)
            - c * _J(1, 2, 1, k)
        )
    )
    return T, V, N


def hylleraas_energy(alpha: Fraction, c: Fraction, Z: Fraction | int) -> Fraction:
    T, V, N = hylleraas_TVN(alpha, c, Z)
    if N <= 0:
        raise ValueError("non-positive overlap")
    return (T + V) / N


# ---------------------------------------------------------------------------
# Chandrasekhar open shell
# ---------------------------------------------------------------------------
# Φ = φ_ab + φ_ba, φ_ab = exp(-a r1 - b r2).
# One-body integrals factor. The Coulomb integral is
#   ∫∫ exp(-λ r1 - μ r2)/r12 d³r1 d³r2
#     = 32 π² (λ² + 3λμ + μ²) / (λ² μ² (λ+μ)³).
# Overall π² cancels in the Rayleigh quotient.


def chandrasekhar_TVN(a: Fraction, b: Fraction, Z: Fraction | int, eps: int = 1):
    """T, V, N for Φ = exp(-a r1-b r2) + ε exp(-b r1-a r2), units of π²."""
    if eps not in (1, -1):
        raise ValueError("eps must be ±1")
    Z = Fraction(Z)
    s = a + b
    N = 2 / (a**3 * b**3) + eps * 128 / s**6
    T = (a**2 + b**2) / (a**3 * b**3) + eps * 128 * a * b / s**6
    Vne = -Z * (2 / (a**2 * b**3) + 2 / (a**3 * b**2) + eps * 128 / s**5)
    Vee = 2 * (a**2 + 3 * a * b + b**2) / (a**2 * b**2 * s**3) + eps * 40 / s**5
    return T, Vne + Vee, N


def chandrasekhar_energy(
    a: Fraction, b: Fraction, Z: Fraction | int, eps: int = 1
) -> Fraction:
    T, V, N = chandrasekhar_TVN(a, b, Z, eps)
    if N <= 0:
        raise ValueError("non-positive overlap")
    return (T + V) / N


def uncorrelated_energy(alpha: Fraction, Z: Fraction | int) -> Fraction:
    """ψ = exp(-α(r1+r2)). Equals α² - 2(Z - 5/16)α."""
    Z = Fraction(Z)
    return alpha**2 - 2 * (Z - Fraction(5, 16)) * alpha


# ---------------------------------------------------------------------------
# Enclosure and certificate
# ---------------------------------------------------------------------------


def enclose_fraction(x: Fraction, places: int = 40) -> tuple[str, str]:
    """Decimal enclosure of a rational by integer floor/ceil (no floats)."""
    p, q = x.numerator, x.denominator
    if q < 0:
        p, q = -p, -q
    scale = 10**places
    num = p * scale
    lo_n = num // q
    hi_n = -((-num) // q)

    def fmt(n: int) -> str:
        sign = "-" if n < 0 else ""
        n = abs(n)
        whole, frac = divmod(n, scale)
        return f"{sign}{whole}.{frac:0{places}d}"

    return fmt(lo_n), fmt(hi_n)


def script_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _frac_json(x: Fraction) -> dict:
    lo, hi = enclose_fraction(x)
    return {
        "exact": f"{x.numerator}/{x.denominator}",
        "float": float(x),
        "enclosure": [lo, hi],
    }


def build_hminus_cert() -> dict:
    Z = 1
    E_h = hylleraas_energy(HYLL_ALPHA, HYLL_C, Z)
    E_c = chandrasekhar_energy(CHAND_A, CHAND_B, Z)
    E_f = chandrasekhar_energy(CHAND_FROZEN_A, CHAND_FROZEN_B, Z)
    half = Fraction(1, 2)
    gap_h = -half - E_h
    gap_c = -half - E_c
    gap_f = -half - E_f
    if not (E_h < -half and E_c < -half and E_f < -half):
        raise RuntimeError("a listed trial is not below the hydrogen threshold")
    # Integer form of the primary gap (reduces 7/801).
    if gap_h != Fraction(7, 801):
        raise RuntimeError("primary Hylleraas gap drifted; expected 7/801")

    T_h, V_h, N_h = hylleraas_TVN(HYLL_ALPHA, HYLL_C, Z)
    T_c, V_c, N_c = chandrasekhar_TVN(CHAND_A, CHAND_B, Z)

    # Sanity: uncorrelated hydrogenic product does *not* bind (Zhislin-scale).
    E_u = uncorrelated_energy(Fraction(11, 16), 1)
    if E_u >= -half:
        pass
    else:
        raise RuntimeError("uncorrelated H- unexpectedly bound")
    if hylleraas_energy(Fraction(11, 16), 0, 1) != E_u:
        raise RuntimeError("Hylleraas c=0 disagrees with the uncorrelated formula")
    if chandrasekhar_energy(Fraction(11, 16), Fraction(11, 16), 1) != E_u:
        raise RuntimeError("Chandrasekhar a=b disagrees with the uncorrelated formula")

    return {
        "system": "H-",
        "Z": 1,
        "N": 2,
        "threshold": "-1/2",
        "strict": True,
        "is_new_bound": False,
        "note": (
            "Variational replay that H- binds. Combined with Lieb Nc < 2Z+1 "
            "this recovers N0(1)=2, already in Lieb 1984. Not a new bound."
        ),
        "primary": {
            "family": "Hylleraas",
            "psi": "exp(-alpha (r1+r2)) (1 + c r12)",
            "alpha": _frac_json(HYLL_ALPHA),
            "c": _frac_json(HYLL_C),
            "energy": _frac_json(E_h),
            "gap_below_threshold": _frac_json(gap_h),
            "T_over_N": _frac_json(T_h / N_h),
            "V_over_N": _frac_json(V_h / N_h),
        },
        "chandrasekhar": {
            "family": "Chandrasekhar",
            "psi": "exp(-a r1 - b r2) + exp(-b r1 - a r2)",
            "a": _frac_json(CHAND_A),
            "b": _frac_json(CHAND_B),
            "energy": _frac_json(E_c),
            "gap_below_threshold": _frac_json(gap_c),
            "T_over_N": _frac_json(T_c / N_c),
            "V_over_N": _frac_json(V_c / N_c),
        },
        "chandrasekhar_frozen_inner": {
            "comment": "a=1 frozen, b=2/7; already binds (Høgaasen–Richard–Sorba)",
            "a": _frac_json(CHAND_FROZEN_A),
            "b": _frac_json(CHAND_FROZEN_B),
            "energy": _frac_json(E_f),
            "gap_below_threshold": _frac_json(gap_f),
        },
        "uncorrelated_does_not_bind": {
            "alpha": _frac_json(Fraction(11, 16)),
            "energy": _frac_json(E_u),
            "comment": "E = -(11/16)^2 = -121/256 > -1/2",
        },
        "published_comparison": {
            "best_NR_Hminus": "-0.527751016544377...",
            "source": "Nakashima–Nakatsuji, J. Chem. Phys. 127, 224104 (2007), doi:10.1063/1.2801981",
            "comment": "Published benchmark, not replayed here. Our trials sit above it.",
        },
        "script_sha256": script_sha256(),
        "replay": "python3 hylleraas.py",
    }


def build_n0_z1_cert(hminus: dict) -> dict:
    return {
        "statement": "N0(1) = 2",
        "is_new_bound": False,
        "note": (
            "Replay of Lieb 1984 plus the classical H- variational bound. "
            "Not a new bound."
        ),
        "legs": {
            "variational_binding": {
                "proves": "N0(1) >= 2",
                "reason": (
                    "A normalized trial on H(2,1) has energy strictly below "
                    "E(1,1) = -1/2, so E(2,1) < E(1,1)."
                ),
                "certificate": "hminus.json",
                "threshold": "-1/2",
                "energy": hminus["primary"]["energy"]["exact"],
                "gap_below_threshold": hminus["primary"]["gap_below_threshold"]["exact"],
                "strict": True,
                "script_sha256": hminus["script_sha256"],
            },
            "lieb_triangle": {
                "proves": "Nc(1) <= 2",
                "theorem": "Lieb, Phys. Rev. A 29, 3018 (1984): Nc < 2Z+1",
                "invoked_not_reproved": True,
                "for_Z_1": "Nc < 3, hence Nc <= 2 (N integer)",
                "comment": (
                    "The triangle |x|+|y| >= |x-y| is used in Lieb's proof. "
                    "We invoke the published theorem; we do not re-prove the "
                    "functional analysis."
                ),
            },
        },
        "combined": "N0(1) = 2",
        "published_precedence": (
            "Lieb 1984 already concludes Nc = 2 for hydrogen "
            "(H-- is not stable). Nam, arXiv:2206.15393, restates that "
            "Lieb settles the ionization conjecture for the hydrogen atom."
        ),
    }


def self_check() -> None:
    """Algebraic identities that must hold before any certificate is written."""
    half = Fraction(1, 2)
    # Uncorrelated closed form, both families.
    for Z, a in ((1, Fraction(11, 16)), (2, Fraction(27, 16))):
        pred = uncorrelated_energy(a, Z)
        got_h = hylleraas_energy(a, 0, Z)
        got_c = chandrasekhar_energy(a, a, Z)
        if got_h != pred or got_c != pred:
            raise RuntimeError(f"uncorrelated mismatch at Z={Z}")
    # Primary H- points sit strictly below -1/2.
    E_h = hylleraas_energy(HYLL_ALPHA, HYLL_C, 1)
    E_c = chandrasekhar_energy(CHAND_A, CHAND_B, 1)
    if E_h >= -half or E_c >= -half:
        raise RuntimeError("H- certificate is not strict")
    if E_h != Fraction(-815, 1602):
        raise RuntimeError(f"unexpected Hylleraas energy {E_h}")
    if E_c != Fraction(-1076189452297, 2096620401250):
        raise RuntimeError(f"unexpected Chandrasekhar energy {E_c}")
    # Helium uncorrelated textbook value.
    if uncorrelated_energy(Fraction(27, 16), 2) != Fraction(-729, 256):
        raise RuntimeError("helium uncorrelated drifted")


def write_certs() -> None:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    hminus = build_hminus_cert()
    n0 = build_n0_z1_cert(hminus)
    (CERT_DIR / "hminus.json").write_text(json.dumps(hminus, indent=2) + "\n")
    (CERT_DIR / "n0_z1.json").write_text(json.dumps(n0, indent=2) + "\n")
    print(f"wrote {CERT_DIR / 'hminus.json'}")
    print(f"wrote {CERT_DIR / 'n0_z1.json'}")


def report() -> None:
    self_check()
    hminus = build_hminus_cert()
    E_h = Fraction(hminus["primary"]["energy"]["exact"])
    E_c = Fraction(hminus["chandrasekhar"]["energy"]["exact"])
    gap_h = Fraction(hminus["primary"]["gap_below_threshold"]["exact"])
    gap_c = Fraction(hminus["chandrasekhar"]["gap_below_threshold"]["exact"])
    lo_h, hi_h = hminus["primary"]["energy"]["enclosure"]
    print("H- Hylleraas certificate (replay, not a new bound)")
    print("  psi = exp(-alpha (r1+r2)) (1 + c r12)")
    print("  alpha = 5/6, c = 1/2")
    print(f"  E = -815/1602 = {float(E_h):.16f}")
    print(f"  enclosure [{lo_h}, {hi_h}]")
    print("  E + 1/2 = -7/801 < 0")
    print(f"  gap below -1/2: 7/801 = {float(gap_h):.16f}")
    print(f"  strict: {E_h < -Fraction(1, 2)} (integer comparison of E + 1/2 = -7/801)")
    print("Chandrasekhar (stronger trial, still a replay)")
    print(f"  a = 26/25, b = 7/25")
    print(f"  E = {E_c} = {float(E_c):.16f}")
    print(f"  gap below -1/2: {gap_c} = {float(gap_c):.16f}")
    print(f"script SHA256 {hminus['script_sha256']}")
    print("N0(1) = 2 via Hylleraas binding + Lieb Nc < 3. Not a new bound.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument(
        "--write-certs",
        action="store_true",
        help="write certs/hminus.json and certs/n0_z1.json",
    )
    args = p.parse_args(argv)
    report()
    if args.write_certs:
        write_certs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
