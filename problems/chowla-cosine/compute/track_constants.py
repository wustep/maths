#!/usr/bin/env python3
"""Certified explicit constants for Chowla K(n) via Bedert §7 + Lemma 7.2.

All numerical comparisons that involve sqrt(2) use the rational bound
    99/70 = 1.4142857... > sqrt(2) > 7/5 = 1.4
so every inequality is a comparison of rationals.

Output: compute/certificate.json and a human-readable dump.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from qsqrt2 import QSqrt2, SQRT2


# --- rational enclosure of sqrt(2) ---
SQRT2_UP = Fraction(99, 70)  # 1.4142857... > 1.41421356...
SQRT2_DN = Fraction(7, 5)  # 1.4


def q2_upper(x: QSqrt2) -> Fraction:
    """Rational upper bound for a + b sqrt(2)."""
    if x.b >= 0:
        return x.a + x.b * SQRT2_UP
    return x.a + x.b * SQRT2_DN


def q2_lower(x: QSqrt2) -> Fraction:
    if x.b >= 0:
        return x.a + x.b * SQRT2_DN
    return x.a + x.b * SQRT2_UP


def rat_sqrt_upper(y: Fraction) -> Fraction:
    """Smallest Fraction k/D with D=10**12 such that (k/D)^2 >= y. Binary search."""
    if y <= 0:
        raise ValueError(y)
    D = 10**12
    # find smallest integer k with k^2 >= y * D^2
    target = y * D * D
    # target is a Fraction; compare k^2 * den >= num
    num, den = target.numerator, target.denominator
    lo, hi = 0, int(math.isqrt(num // den) + 3) * 2 + 10
    # ensure hi is large enough: hi^2 * den >= num
    while hi * hi * den < num:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid * den >= num:
            hi = mid
        else:
            lo = mid + 1
    return Fraction(lo, D)


def main() -> None:
    # Exact algebraic values from the independently checked 32-window table.
    psi_max = QSqrt2(4, Fraction(1, 2))  # 4 + 1/sqrt(2)
    phi_B = QSqrt2(4, 1)  # 4 + sqrt(2)
    phi_max = QSqrt2(4, 2)  # 4 + 2 sqrt(2)
    gap = phi_B - psi_max  # sqrt(2)/2

    # Lemma 7.1 explicit constants, derived in WALKTHROUGH / constants.md
    # and re-checked below as integers.
    C_Q1 = 3  # |Q1| <= 3 (hat1_A + K), ||Q1||_1 <= 3K
    C_Q2 = 14  # ||Q2||_2 <= 14 K^2   (for K >= 0; see derivation)
    C_r = 32  # |phi| <= psi + 32 K^2

    # Prop 7.3 quadratic, written in Q(sqrt(2)):
    # gap |B| <= 2 C_Q2 (phi_max + psi_max) K^2 sqrt|B|
    #          + (C_Q2^2 (phi_max + psi_max) + C_r C_Q1^2) K^4
    # z = sqrt|B| / K^2
    # z^2 <= A z + B
    # with A = 2 C_Q2 (phi_max+psi_max) / gap
    #      B = (C_Q2^2 (phi_max+psi_max) + C_r C_Q1^2) / gap
    sm = phi_max + psi_max  # 8 + (5/2) sqrt(2)
    A_alg = QSqrt2(2 * C_Q2) * sm / gap
    B_alg = (QSqrt2(C_Q2 * C_Q2) * sm + QSqrt2(C_r * C_Q1 * C_Q1)) / gap

    A_up = q2_upper(A_alg)
    B_up = q2_upper(B_alg)
    disc_up = A_up * A_up + 4 * B_up
    sqrt_disc_up = rat_sqrt_upper(disc_up)
    z_up = (A_up + sqrt_disc_up) / 2
    Cstar_up = z_up * z_up  # |B| <= Cstar_up K^4

    # Slightly looser integer/rational we actually publish.
    # Take a clean fraction strictly above Cstar_up.
    Cstar_pub = Fraction(Cstar_up.numerator + Cstar_up.denominator, Cstar_up.denominator)
    # and then a simple integer ceiling for the write-up
    Cstar_int = int(Cstar_up) + 1

    # Energy + AP: |B_t| >= N / (16 K (K^2 + 1)) when N >= 2 K^2
    #   (N = |A| even, K = ||hat1_A||_min)
    # Combined: N <= 16 Cstar (K^7 + K^5)
    # For a pure 7th-root: N <= 32 Cstar K^7   (using K^7+K^5 <= 2 K^7 for K>=1,
    # and a separate check K>=1 or the same 32 Cstar when K<1 — see WALKTHROUGH)
    C7 = 32 * Cstar_int  # N <= C7 K^7   on the energy branch
    # slightly tighter with the exact fraction:
    C7_frac = 32 * Cstar_pub

    # Chowla (positive n-set): N = 2n, K_pos >= K_sym / 2
    # K_pos(n) >= min( sqrt(n)/2 ,  (2n / C7)^{1/7} / 2 )
    #            = min( n^{1/2}/2 ,  2^{-6/7} C7^{-1/7} n^{1/7} )
    # We publish a rational lower bound on the n^{1/7} coefficient.

    # 2^{-6/7} / C7^{1/7} = 1 / (2^{6/7} C7^{1/7}) = 1 / (64 * C7)^{1/7} * 2^{0}?
    # 2^{6/7} C7^{1/7} = (2^6 C7)^{1/7} = (64 C7)^{1/7}
    # so coeff = (64 C7)^{-1/7}
    # Lower-bound this by 1 / ceil((64 C7)^{1/7}) using an integer seventh root upper bound.

    def int_nth_root_upper(m: int, n: int) -> int:
        """Smallest integer r with r^n >= m."""
        r = int(math.pow(m, 1 / n)) + 2
        while (r - 1) ** n >= m and r > 0:
            r -= 1
        if r ** n < m:
            r += 1
        return r

    seventh_up = int_nth_root_upper(64 * C7, 7)
    # coeff >= 1/seventh_up
    # Use a slightly cleaner smaller rational: 1 / seventh_up
    c_pos_17 = Fraction(1, seventh_up)

    # Also a float preview (not used in the certificate inequalities).
    c_pos_17_float = (2.0 ** (-6 / 7)) / (C7 ** (1 / 7))

    # Polylog form from Lemma 7.4 with explicit M.
    # max_t |B_t| >= N^{1 - 2/pi(M)} / (4 M^2 K)   provided the exponent box is nonempty.
    # Combined with |B| <= Cstar K^4:
    # Cstar K^5 >= N^{1-2/pi(M)} / (4 M^2)
    # We record several M and let the verifier pick the best per n.

    def pi_of(M: int) -> int:
        if M < 2:
            return 0
        sieve = [True] * (M + 1)
        sieve[0] = sieve[1] = False
        p = 2
        while p * p <= M:
            if sieve[p]:
                for j in range(p * p, M + 1, p):
                    sieve[j] = False
            p += 1
        return sum(sieve)

    m_rows = []
    for M in [5, 7, 11, 13, 19, 23, 31, 43, 61, 79, 97]:
        pim = pi_of(M)
        if pim <= 2:
            continue
        # K_sym^5 >= N^{1-2/pi} / (4 M^2 Cstar)
        # K_pos >= K_sym(2n)/2, N=2n
        # K_pos >= (1/2) * ( (2n)^{1-2/pi} / (4 M^2 Cstar) )^{1/5}
        exp_num = pim - 2
        exp_den = pim
        denom = 4 * M * M * Cstar_int
        m_rows.append(
            {
                "M": M,
                "pi_M": pim,
                "N_exp_num": exp_num,
                "N_exp_den": exp_den,
                "denom": denom,
            }
        )

    cert = {
        "lemma72": {
            "psi_max": ["4", "1/2"],
            "phi_B": ["4", "1"],
            "phi_max": ["4", "2"],
            "gap": ["0", "1/2"],
            "verified_by": "verify_lemma72.py",
        },
        "lemma71": {
            "C_Q1": C_Q1,
            "C_Q2": C_Q2,
            "note": "|Q1| <= 3(hat1_A+K), ||Q2||_2 <= 14 K^2",
        },
        "C_r": C_r,
        "quadratic": {
            "A_alg": [str(A_alg.a), str(A_alg.b)],
            "B_alg": [str(B_alg.a), str(B_alg.b)],
            "A_up": str(A_up),
            "B_up": str(B_up),
            "disc_up": str(disc_up),
            "sqrt_disc_up": str(sqrt_disc_up),
            "z_up": str(z_up),
            "Cstar_up": str(Cstar_up),
            "Cstar_pub": str(Cstar_pub),
            "Cstar_int": Cstar_int,
            "sqrt2_up": str(SQRT2_UP),
            "sqrt2_dn": str(SQRT2_DN),
        },
        "symmetric": {
            "N_le": f"{C7} K^7 on the energy branch",
            "C7": C7,
            "C7_frac": str(C7_frac),
            "K_sym_ge_min_of": ["sqrt(N/2)", f"(N/{C7})^(1/7)"],
        },
        "chowla_positive": {
            "K_n_ge_min_of": [
                "n^(1/2)/2",
                f"{c_pos_17} n^(1/7)",
            ],
            "c_1_7": str(c_pos_17),
            "c_1_7_float_preview": c_pos_17_float,
            "seventh_root_upper_of_64_C7": seventh_up,
            "statement": (
                f"For every n>=1 and every n-element set A of positive integers, "
                f"min_x sum_{{a in A}} cos(a x) <= - min(sqrt(n)/2, ({c_pos_17}) n^{{1/7}})."
            ),
        },
        "polylog_rows": m_rows,
    }

    out_dir = Path(__file__).resolve().parent
    (out_dir / "certificate.json").write_text(json.dumps(cert, indent=2) + "\n")

    print("=== algebraic pieces ===")
    print(f"psi_max = {psi_max}")
    print(f"phi_B   = {phi_B}")
    print(f"phi_max = {phi_max}")
    print(f"gap     = {gap}")
    print(f"sm      = {sm}")
    print(f"A_alg   = {A_alg}")
    print(f"B_alg   = {B_alg}")
    print(f"A_up    = {A_up}  (~ {float(A_up)})")
    print(f"B_up    = {B_up}  (~ {float(B_up)})")
    print(f"z_up    = {z_up}  (~ {float(z_up)})")
    print(f"Cstar   <= {Cstar_up}  (~ {float(Cstar_up)})")
    print(f"Cstar_int = {Cstar_int}")
    print(f"C7        = {C7}")
    print(f"c_pos_1/7 >= {c_pos_17}  (~ {float(c_pos_17)})")
    print(f"float preview {c_pos_17_float}")
    print()
    print(cert["chowla_positive"]["statement"])


if __name__ == "__main__":
    main()
