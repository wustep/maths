#!/usr/bin/env python3
"""Certified envelope of Carvalho Corso–Ried M_3 / L/Lcl via the Clausen form.

Carvalho Corso–Ried, arXiv:2403.04347v2, solve the FHJN/HKRV variational
problem. Theorem 1.3 + (1.4) at γ=3 give C_{1,1}=M_3 and
    M_3 = (16π/81) H^3,   H = ||h_{-2/3}||_∞ / ||h_{-1}||_2^{2/3}
with ||h_0||_∞=1. Carvalho Corso, arXiv:2407.10117v2, Remark 1.4 / (1.11)
evaluates that three-lines ratio in closed form:

    H_∞,2(α) = (4α sin(πα))^{-α/2} exp( CI_2(2π(1-α)) / (2π) ),

and Corollary 1.8 writes the same bound as

    L/Lcl ≤ (π (1-α)^{1/α}) / (α sin(πα)) · exp( CI_2(2π(1-α)) / (π α) )

with α = 2s/(d+2s). For d=s=1 one has α=2/3, sin(2π/3)=√3/2, and this
collapses to the elementary identity

    L/Lcl ≤ (π/3) exp( 3 CI_2(2π/3) / (2π) ),

which is algebraically the same as (9√3/4) M_3.

The Clausen value is the Fourier series
    CI_2(2π/3) = (√3/2) Σ_{m≥0} ( 1/(3m+1)^2 − 1/(3m+2)^2 ).
This file sums a finite prefix with a directed pad and an explicit
integral tail, then pushes the envelope through exp and the two
conversions. It does not claim priority over 2403.04347, and it does
not beat the paper's 1.44655.

A trapezoid replay of the original three-lines integral (not a bound)
lives in replay_m3.py.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

REL = 2.0e-14
ABS = 1.0e-15
FHJN_PUBLISHED = 1.456
Q1_CLAIM = 1.45576
CCR_CLAIM = 1.44655
PAPER_M3 = 0.371185695

# Directed constants: float64 π and √3 sit within 1 ulp of the true values.
# Push one extra ulp each way so every later product is an upper/lower.
PI_UP = math.nextafter(math.pi, math.inf)
PI_DN = math.nextafter(math.pi, 0.0)
SQRT3_UP = math.nextafter(math.sqrt(3.0), math.inf)
SQRT3_DN = math.nextafter(math.sqrt(3.0), 0.0)


def directed_up(x: float) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("non-finite")
    return math.nextafter(abs(x) * (1.0 + REL) + ABS, math.inf) * math.copysign(1.0, x)


def directed_down(x: float) -> float:
    x = float(x)
    if not math.isfinite(x) or x <= 0.0:
        return 0.0
    return math.nextafter(x * (1.0 - REL) - ABS, 0.0)


def exp_up(x: float) -> float:
    """Upper bound on e^x for x ≥ 0, Taylor with a positive remainder."""
    if x < 0.0:
        raise ValueError("exp_up expects x ≥ 0")
    # e^x = Σ_{k=0}^{n-1} x^k/k! + e^ξ x^n/n!  ≤ Σ_{k=0}^{n-1} x^k/k! + e^x x^n/n!
    # so e^x ≤ S / (1 − x^n/n!) once x^n/n! < 1.
    n = 24
    term = 1.0
    s = 1.0
    for k in range(1, n):
        term *= x / k
        s += term
    rem_ratio = term * (x / n)  # x^n / n!
    if rem_ratio >= 0.5:
        raise ValueError("exp_up remainder too large")
    return directed_up(s / (1.0 - rem_ratio))


def clausen_two_pi_over_three(n_terms: int) -> dict:
    """Upper and a raw partial sum for CI_2(2π/3).

    t_m = 1/(3m+1)^2 − 1/(3m+2)^2 > 0.
    For m ≥ 1, t_m < 1/(9 m^3), and
        Σ_{m≥N} t_m < (1/9) ∫_{N-1}^∞ x^{-3} dx = 1/(18 (N-1)^2),  N≥2.
    Then CI_2 = (√3/2) Σ t_m.
    """
    if n_terms < 8:
        raise ValueError("n_terms too small")
    partial = 0.0
    # Compensated sum; every term is positive.
    c = 0.0
    for m in range(n_terms):
        a = 3 * m + 1
        b = 3 * m + 2
        t = (1.0 / (a * a)) - (1.0 / (b * b))
        y = t - c
        u = partial + y
        c = (u - partial) - y
        partial = u
    # One relative pad per term, plus an absolute pad on the sum.
    partial_up = partial * (1.0 + REL * n_terms) + ABS * n_terms
    tail = 1.0 / (18.0 * (n_terms - 1) ** 2)
    tail_up = directed_up(tail)
    sum_up = directed_up(partial_up + tail_up)
    cl_up = directed_up((SQRT3_UP * 0.5) * sum_up)
    cl_raw = (math.sqrt(3.0) * 0.5) * partial
    return {
        "n_terms": n_terms,
        "partial": partial,
        "partial_up": partial_up,
        "tail_up": tail_up,
        "CI2_raw_partial": cl_raw,
        "CI2_upper": cl_up,
    }


def convert(ci2_up: float) -> dict:
    """Push CI_2_upper through both published conversions."""
    # L/Lcl ≤ (π/3) exp(3 CI_2 / (2π))
    arg_up = directed_up((3.0 * ci2_up) / (2.0 * PI_DN))
    exp_part = exp_up(arg_up)
    L_up = directed_up((PI_UP / 3.0) * exp_part)

    # H = (4√3/3)^{-1/3} exp(CI_2 / (2π)) = (3/(4√3))^{1/3} exp(...)
    # H^3 = 3/(4√3) exp(3 CI_2 / (2π))
    h3_pre_up = directed_up(3.0 / (4.0 * SQRT3_DN))
    H3_up = directed_up(h3_pre_up * exp_part)
    # H_upper = (H^3_upper)^{1/3}; only used for the table.
    H_up = directed_up(H3_up ** (1.0 / 3.0))
    M3_up = directed_up((16.0 * PI_UP / 81.0) * H3_up)
    # Dual kinetic ratio: K/Kcl ≥ 16/(243 M3^2)
    K_lo = directed_down(16.0 / (243.0 * M3_up * M3_up))
    return {
        "arg_up": arg_up,
        "exp_up": exp_part,
        "H_upper": H_up,
        "M3_upper": M3_up,
        "L_over_Lcl_upper": L_up,
        "K_over_Kcl_lower": K_lo,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-terms", type=int, default=20000)
    ap.add_argument(
        "--cert",
        type=Path,
        default=HERE / "certs" / "m3_ccr.json",
    )
    args = ap.parse_args()

    print("=== q2 verify_m3: Clausen envelope of CCR M_3 ===", flush=True)
    cl = clausen_two_pi_over_three(args.n_terms)
    print(
        f"CI_2(2π/3) partial={cl['CI2_raw_partial']:.15e}  "
        f"upper={cl['CI2_upper']:.15e}",
        flush=True,
    )
    conv = convert(cl["CI2_upper"])
    L_u = conv["L_over_Lcl_upper"]
    M3_u = conv["M3_upper"]
    print(f"H_upper            = {conv['H_upper']:.15e}", flush=True)
    print(f"M3_upper           = {M3_u:.15e}   paper {PAPER_M3}", flush=True)
    print(f"L/Lcl_upper        = {L_u:.15e}", flush=True)
    print(f"K/Kcl_lower        = {conv['K_over_Kcl_lower']:.15e}", flush=True)
    print(f"beats FHJN 1.456   = {L_u < FHJN_PUBLISHED}", flush=True)
    print(f"below q1 1.45576   = {L_u < Q1_CLAIM}", flush=True)
    print(f"below 1.45         = {L_u < 1.45}", flush=True)
    print(f"beats CCR 1.44655  = {L_u < CCR_CLAIM}", flush=True)

    cert = {
        "schema": "ccr-clausen-v1",
        "source": "problems/simon-lieb-thirring/compute/q2/verify_m3.py",
        "papers": ["arXiv:2403.04347v2", "arXiv:2407.10117v2"],
        "alpha": 2.0 / 3.0,
        "n_terms": args.n_terms,
        "CI2_upper": cl["CI2_upper"],
        "CI2_raw_partial": cl["CI2_raw_partial"],
        "tail_up": cl["tail_up"],
        "H_upper": conv["H_upper"],
        "M3_upper": M3_u,
        "L_over_Lcl_upper": L_u,
        "K_over_Kcl_lower": conv["K_over_Kcl_lower"],
        "formula_L": "(pi/3) exp(3 CI2(2pi/3) / (2pi))",
        "formula_M3": "(16 pi / 81) H^3,  H = (4*sqrt(3)/3)^(-1/3) exp(CI2/(2pi))",
        "beats_published_1456": bool(L_u < FHJN_PUBLISHED),
        "below_q1_145576": bool(L_u < Q1_CLAIM),
        "beats_ccr_144655": bool(L_u < CCR_CLAIM),
        "note": (
            "Independent envelope of the CCR / Carvalho Corso closed form. "
            "Not a new pair. Does not claim priority. Does not beat 1.44655."
        ),
    }
    args.cert.parent.mkdir(parents=True, exist_ok=True)
    args.cert.write_text(json.dumps(cert, indent=2) + "\n")
    print(f"wrote {args.cert}", flush=True)
    if not cert["beats_published_1456"]:
        raise SystemExit("envelope missed FHJN 1.456 — refuse that comparison")
    if not cert["below_q1_145576"]:
        raise SystemExit("envelope missed q1 1.45576 — refuse that comparison")
    if L_u >= 1.45:
        raise SystemExit("envelope is not below 1.45")


if __name__ == "__main__":
    main()
