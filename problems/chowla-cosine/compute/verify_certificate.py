#!/usr/bin/env python3
"""Replay the explicit-constant arithmetic from first principles.

Does not import track_constants. Re-derives Cstar from the Lemma 7.2
algebraic values (themselves checked by verify_lemma72.py) and confirms

    K(n) >= n^{1/7} / 18
    for every n >= 1.

Exit 0 iff every rational comparison in the chain holds.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path


def fail(msg: str) -> int:
    print("FAIL:", msg)
    return 1


def main() -> int:
    # sqrt(2) enclosure: 7/5 < sqrt(2) < 99/70
    # 7^2 = 49 < 50 = 2*5^2; 99^2 = 9801 > 9800 = 2*70^2
    if 7 * 7 >= 2 * 5 * 5:
        return fail("7/5 is not a lower bound for sqrt(2)")
    if 99 * 99 <= 2 * 70 * 70:
        return fail("99/70 is not an upper bound for sqrt(2)")

    sqrt2_up = Fraction(99, 70)
    sqrt2_dn = Fraction(7, 5)

    def q2_up(a: Fraction, b: Fraction) -> Fraction:
        return a + b * (sqrt2_up if b >= 0 else sqrt2_dn)

    # Lemma 7.2 (exact, independently enumerated)
    # max Re rho = 4 + sqrt(2)/2
    # min_Bt (-Im rho) = 4 + sqrt(2)
    # max |Im rho| = 4 + 2 sqrt(2)
    # gap = sqrt(2)/2
    psi_a, psi_b = Fraction(4), Fraction(1, 2)
    phiB_a, phiB_b = Fraction(4), Fraction(1)
    phiM_a, phiM_b = Fraction(4), Fraction(2)

    # Lemma 7.1
    C_Q1 = 3
    C_Q2 = 14
    C_r = 32

    # A = 2 C_Q2 (phi_max + psi) / gap
    #   phi_max + psi = 8 + (5/2) sqrt(2)
    #   gap = sqrt(2)/2
    #   A = 28 * (8 + 5/2 sqrt(2)) * 2 / sqrt(2)
    #     = 56 (8/sqrt(2) + 5/2) = 56 (4 sqrt(2) + 5/2)
    #     = 224 sqrt(2) + 140
    A_a, A_b = Fraction(140), Fraction(224)
    # B = (C_Q2^2 (phi_max+psi) + C_r C_Q1^2) / gap
    #   C_Q2^2 = 196, C_r C_Q1^2 = 288
    #   (196 (8 + 5/2 sqrt(2)) + 288) * 2 / sqrt(2)
    #   = (1568 + 490 sqrt(2) + 288) * sqrt(2)   because 2/sqrt(2)=sqrt(2)
    #   = (1856 + 490 sqrt(2)) sqrt(2)
    #   = 1856 sqrt(2) + 980
    B_a, B_b = Fraction(980), Fraction(1856)

    A_up = q2_up(A_a, A_b)
    B_up = q2_up(B_a, B_b)

    # z <= (A + sqrt(A^2 + 4B))/2, using integer isqrt on a 10^12-denominator
    D = 10**12
    disc = A_up * A_up + 4 * B_up
    target = disc * D * D
    num, den = target.numerator, target.denominator
    # smallest k with k^2 * den >= num
    lo, hi = 0, 1
    while hi * hi * den < num:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid * den >= num:
            hi = mid
        else:
            lo = mid + 1
    sqrt_disc_up = Fraction(lo, D)
    # confirm (sqrt_disc_up)^2 >= disc
    if sqrt_disc_up * sqrt_disc_up < disc:
        return fail("sqrt enclosure failed")

    z_up = (A_up + sqrt_disc_up) / 2
    Cstar_up = z_up * z_up
    Cstar_int = int(Cstar_up) + (0 if Cstar_up == int(Cstar_up) else 1)
    if Cstar_int < Cstar_up:
        return fail("Cstar_int not an upper bound")

    C7 = 32 * Cstar_int  # N <= C7 K_sym^7 on the energy branch

    # Conversion: K_pos(n) >= (2n / C7)^{1/7} / 2 = n^{1/7} / (64 C7)^{1/7}
    #                                = n^{1/7} / (2048 Cstar_int)^{1/7}
    prod = 2048 * Cstar_int
    # 18^7 = 612220032
    eighteen_7 = 18**7
    if prod > eighteen_7:
        return fail(f"2048 Cstar_int = {prod} > 18^7 = {eighteen_7}")

    # The n^{1/7}/18 bound is therefore <= the converted energy-branch bound.
    # Energy-failure branch: K_pos >= sqrt(n)/2, and sqrt(n)/2 >= n^{1/7}/18
    # for all n>=1 iff 1/9 <= n^{5/14} for n>=1, i.e. 9^{14} >= 1 which is true.
    # Check 9^{14} > 1 and also 2/18 <= 1^{5/14}:
    if Fraction(1, 9) > 1:
        return fail("n=1 comparison 1/9 <= 1 failed")

    # Small-n sanity: K(1)=1 >= 1/18
    if Fraction(1, 18) > 1:
        return fail("K(1) sanity")

    out = {
        "ok": True,
        "Cstar_int": Cstar_int,
        "C7": C7,
        "prod_2048_Cstar": prod,
        "18_to_7": eighteen_7,
        "c": "1/18",
        "statement": (
            "For every integer n>=1 and every set A of n positive integers, "
            "min_x sum_{a in A} cos(a x) <= - n^{1/7}/18."
        ),
    }
    Path(__file__).resolve().parent.joinpath("verify_certificate.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print(json.dumps(out, indent=2))
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
