#!/usr/bin/env python3
"""Helium (Z=2, N=2) Hylleraas / Chandrasekhar variational replay.

Same two-electron families as hylleraas.py, now at Z=2. Zhislin already
gives binding for N < Z+1, so this energy is a unique-ish object (a
variational upper bound on E(2,2)), not a handle on N0(2). It is a
replay, not a bound.

The published non-relativistic infinite-mass helium energy
-2.9037243770341195... (Nakashima–Nakatsuji, J. Chem. Phys. 127, 224104
(2007), doi:10.1063/1.2801981) is a comparison, not a number we replay.

Replay:

    python3 he_hylleraas.py
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hylleraas import (
    chandrasekhar_TVN,
    chandrasekhar_energy,
    enclose_fraction,
    hylleraas_TVN,
    hylleraas_energy,
    script_sha256,
    uncorrelated_energy,
)

# Hylleraas (1 + c r12), near the classical α≈1.85, c≈0.36.
HE_HYLL_ALPHA = Fraction(37, 20)
HE_HYLL_C = Fraction(37, 100)

# Chandrasekhar, near Høgaasen–Richard–Sorba a≈2.18, b≈1.19.
HE_CHAND_A = Fraction(109, 50)
HE_CHAND_B = Fraction(119, 100)

# Simple equal-denominator Chandrasekhar point.
HE_CHAND_SIMPLE_A = Fraction(11, 5)
HE_CHAND_SIMPLE_B = Fraction(6, 5)

# Nakashima–Nakatsuji 2007, first 16 digits after the point (comparison only).
HE_PUBLISHED = "-2.9037243770341195"


def report() -> dict:
    Z = 2
    E_u = uncorrelated_energy(Fraction(27, 16), Z)
    if E_u != Fraction(-729, 256):
        raise RuntimeError("helium uncorrelated is not -729/256")
    if hylleraas_energy(Fraction(27, 16), 0, Z) != E_u:
        raise RuntimeError("Hylleraas c=0 disagrees at Z=2")
    if chandrasekhar_energy(Fraction(27, 16), Fraction(27, 16), Z) != E_u:
        raise RuntimeError("Chandrasekhar a=b disagrees at Z=2")

    E_h = hylleraas_energy(HE_HYLL_ALPHA, HE_HYLL_C, Z)
    E_c = chandrasekhar_energy(HE_CHAND_A, HE_CHAND_B, Z)
    E_s = chandrasekhar_energy(HE_CHAND_SIMPLE_A, HE_CHAND_SIMPLE_B, Z)
    if E_h != Fraction(-54353, 18800):
        raise RuntimeError(f"unexpected He Hylleraas energy {E_h}")

    T_h, V_h, N_h = hylleraas_TVN(HE_HYLL_ALPHA, HE_HYLL_C, Z)
    T_c, V_c, N_c = chandrasekhar_TVN(HE_CHAND_A, HE_CHAND_B, Z)

    print("Helium Z=2 N=2 variational replay (not a bound on N0)")
    print("  uncorrelated α = 27/16")
    print(f"    E = -729/256 = {float(E_u):.16f}")
    print("  Hylleraas ψ = exp(-α(r1+r2)) (1 + c r12)")
    print(f"    α = 37/20, c = 37/100")
    print(f"    E = -54353/18800 = {float(E_h):.16f}")
    print(f"    enclosure {list(enclose_fraction(E_h))}")
    print(f"    T/N = {float(T_h / N_h):.16f}, V/N = {float(V_h / N_h):.16f}")
    print("  Chandrasekhar Φ = exp(-a r1-b r2) + exp(-b r1-a r2)")
    print(f"    a = 109/50, b = 119/100")
    print(f"    E = {E_c} = {float(E_c):.16f}")
    print(f"    a = 11/5, b = 6/5 (simpler)")
    print(f"    E = {E_s} = {float(E_s):.16f}")
    print(f"  published NR benchmark {HE_PUBLISHED} (Nakashima–Nakatsuji 2007)")
    print(f"  Hylleraas sits {float(E_h) - float(HE_PUBLISHED):.6f} above the benchmark")
    print("  Zhislin already binds N=2 at Z=2. This is not a bound on N0(2).")
    print(f"  hylleraas.py SHA256 {script_sha256()}")
    return {
        "uncorrelated": E_u,
        "hylleraas": E_h,
        "chandrasekhar": E_c,
        "chandrasekhar_simple": E_s,
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0]).parse_args(argv)
    report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
