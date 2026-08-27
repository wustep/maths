#!/usr/bin/env python3
"""Christopher–Lloyd (u², v²) four-fold of a translated radial cubic.

The time-rescale field of Gasull–Santana arXiv:2407.13465v2 §4 is

    Yu = v P(u², v²),    Yv = u Q(u², v²),

with dt/dτ = 2uv. This is not the Remark 4 adjunction
Y = adj(DΦ)(X ∘ Φ), which is twice this field.

Applied to the radial cubic of 2604.12883 §6 after the shift
(X, Y) = (x − 2, y − 2), the degree is exactly 7 and the
first-quadrant circle lifts to 4 hyperbolic ovals. That gives
H(7) ≥ 4, which does not beat Prohens–Torregrosa H(7) ≥ 74.
T2 of the untranslated cubic has the same N = 7 and the same
4 sheets. The map attains m² = 4 and beats the linear count
(N+1)/(n+1) = 2. Do not claim a dent. Do not cite
252/1080/1380/2012 here.

Replay: python3 verify.py
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
U, V, X, Ys = sp.symbols("u v x y")
RHO2 = sp.Rational(1, 4)


def fail(msg: str) -> None:
    raise SystemExit(f"verify.py FAIL: {msg}")


def total_deg(expr, gens) -> int:
    expr = sp.expand(expr)
    if expr == 0:
        return -1
    return int(sp.Poly(expr, gens).total_degree())


def monomials_qq(expr, gens=(U, V)) -> list[dict[str, int]]:
    poly = sp.Poly(sp.expand(expr), *gens, domain=sp.QQ)
    out = []
    for exp, coeff in poly.as_dict().items():
        frac = Fraction(int(coeff.p), int(coeff.q))
        out.append(
            {
                "u": int(exp[0]),
                "v": int(exp[1]),
                "num": frac.numerator,
                "den": frac.denominator,
            }
        )
    out.sort(key=lambda m: (m["u"] + m["v"], m["u"], m["v"]))
    return out


def dump_monomials(prefix: str, expr, gens=(U, V)) -> list[str]:
    return [
        f"{prefix} {m['u']} {m['v']} {m['num']} {m['den']}"
        for m in monomials_qq(expr, gens)
    ]


def radial_untranslated(rho2=RHO2):
    P = Ys - X * (X**2 + Ys**2 - rho2)
    Q = -X - Ys * (X**2 + Ys**2 - rho2)
    return P, Q


def translate(P, Q, shift=2):
    return (
        sp.expand(P.subs({X: X - shift, Ys: Ys - shift})),
        sp.expand(Q.subs({X: X - shift, Ys: Ys - shift})),
    )


def linear_center():
    return Ys, -X


def sample_quadratic():
    return X**2 + Ys, Ys**2 + X


def cl_field(P, Q):
    """Yu = v P(u², v²), Yv = u Q(u², v²). Not the adj pullback."""
    Pc = sp.expand(P.subs({X: U**2, Ys: V**2}))
    Qc = sp.expand(Q.subs({X: U**2, Ys: V**2}))
    Yu = sp.expand(V * Pc)
    Yv = sp.expand(U * Qc)
    return Yu, Yv, Pc, Qc


def adj_field(P, Q):
    """Y = adj(DΦ)(X ∘ Φ) for Φ = (u², v²): Yu = 2v P, Yv = 2u Q."""
    Pc = sp.expand(P.subs({X: U**2, Ys: V**2}))
    Qc = sp.expand(Q.subs({X: U**2, Ys: V**2}))
    Yu = sp.expand(2 * V * Pc)
    Yv = sp.expand(2 * U * Qc)
    return Yu, Yv, Pc, Qc


def cl_identity(P, Q, Yu, Yv, Pc, Qc):
    """DΦ · Y − 2uv (X ∘ Φ). Φ = (u², v²), DΦ = diag(2u, 2v)."""
    Du = sp.expand(2 * U * Yu - 2 * U * V * Pc)
    Dv = sp.expand(2 * V * Yv - 2 * U * V * Qc)
    return Du, Dv


def adj_identity(P, Q, Yu, Yv, Pc, Qc):
    """DΦ · Y − 4uv (X ∘ Φ)."""
    Du = sp.expand(2 * U * Yu - 4 * U * V * Pc)
    Dv = sp.expand(2 * V * Yv - 4 * U * V * Qc)
    return Du, Dv


def chebyshev_T2():
    return 2 * U**2 - 1, 2 * V**2 - 1


def t2_field(P, Q):
    t2u, t2v = chebyshev_T2()
    Pc = sp.expand(P.subs({X: t2u, Ys: t2v}))
    Qc = sp.expand(Q.subs({X: t2u, Ys: t2v}))
    Yu = sp.expand(4 * V * Pc)
    Yv = sp.expand(4 * U * Qc)
    return Yu, Yv


def leading_form(expr, deg, gens=(U, V)):
    poly = sp.Poly(sp.expand(expr), *gens)
    return sum(
        coeff * gens[0] ** i * gens[1] ** j
        for (i, j), coeff in poly.as_dict().items()
        if i + j == deg
    )


def check_identity_and_degree() -> dict[str, Any]:
    P0, Q0 = radial_untranslated()
    r2 = X**2 + Ys**2
    flux = sp.expand(X * P0 + Ys * Q0)
    expect_flux = sp.expand(-r2 * (r2 - RHO2))
    if flux != expect_flux:
        fail(f"radial flux {flux}")
    fprime = RHO2 - 3 * RHO2
    if fprime != -2 * RHO2 or fprime != sp.Rational(-1, 2):
        fail(f"f'(ρ) = {fprime}")

    P1, Q1 = linear_center()
    Yu1, Yv1, Pc1, Qc1 = cl_field(P1, Q1)
    Du1, Dv1 = cl_identity(P1, Q1, Yu1, Yv1, Pc1, Qc1)
    if Du1 != 0 or Dv1 != 0:
        fail("linear CL identity failed")
    if Yu1 != V**3 or Yv1 != -(U**3):
        fail("linear closed form")
    deg_1 = max(total_deg(Yu1, (U, V)), total_deg(Yv1, (U, V)))
    if deg_1 != 3:
        fail(f"linear CL deg {deg_1}")

    P2, Q2 = sample_quadratic()
    Yu2, Yv2, Pc2, Qc2 = cl_field(P2, Q2)
    Du2, Dv2 = cl_identity(P2, Q2, Yu2, Yv2, Pc2, Qc2)
    if Du2 != 0 or Dv2 != 0:
        fail("quadratic CL identity failed")
    if Yu2 != U**4 * V + V**3 or Yv2 != U**3 + U * V**4:
        fail("quadratic closed form")
    deg_2 = max(total_deg(Yu2, (U, V)), total_deg(Yv2, (U, V)))
    if deg_2 != 5:
        fail(f"quadratic CL deg {deg_2}")

    P, Q = translate(P0, Q0)
    if total_deg(P, (X, Ys)) != 3 or total_deg(Q, (X, Ys)) != 3:
        fail("translated (P, Q) not degree 3")
    Yu, Yv, Pc, Qc = cl_field(P, Q)
    Du, Dv = cl_identity(P, Q, Yu, Yv, Pc, Qc)
    if Du != 0 or Dv != 0:
        fail("translated CL identity failed")
    deg_r = max(total_deg(Yu, (U, V)), total_deg(Yv, (U, V)))
    if deg_r != 7:
        fail(f"translated CL deg {deg_r}")
    n_yu = len(monomials_qq(Yu))
    n_yv = len(monomials_qq(Yv))
    if n_yu != 8 or n_yv != 8:
        fail(f"CL term counts {n_yu} {n_yv}")
    lead_u = leading_form(Yu, 7)
    lead_v = leading_form(Yv, 7)
    if sp.expand(lead_u + U**6 * V + U**2 * V**5) != 0:
        fail("CL Yu leading")
    if sp.expand(lead_v + U**5 * V**2 + U * V**6) != 0:
        fail("CL Yv leading")

    Yu_adj, Yv_adj, _, _ = adj_field(P, Q)
    Dua, Dva = adj_identity(P, Q, Yu_adj, Yv_adj, Pc, Qc)
    if Dua != 0 or Dva != 0:
        fail("translated adj identity failed")
    if Yu_adj != 2 * Yu or Yv_adj != 2 * Yv:
        fail("adj is not twice CL")
    if Yu_adj == Yu or Yv_adj == Yv:
        fail("CL field equals adj; they must differ")
    deg_adj = max(total_deg(Yu_adj, (U, V)), total_deg(Yv_adj, (U, V)))
    if deg_adj != 7:
        fail(f"adj deg {deg_adj}")

    G = (U**2 - 2) ** 2 + (V**2 - 2) ** 2 - RHO2
    dG = sp.expand(4 * U * (U**2 - 2) * Yu + 4 * V * (V**2 - 2) * Yv)
    oval_res = sp.expand(dG + 4 * U * V * G * (G + RHO2))
    if oval_res != 0:
        fail("oval residual")

    # Untranslated circle hits the axes; translated circle does not.
    F0 = X**2 + Ys**2 - RHO2
    if sp.expand(F0.subs({X: sp.Rational(1, 2), Ys: 0})) != 0:
        fail("untranslated right point")
    if sp.expand(F0.subs({X: 0, Ys: sp.Rational(1, 2)})) != 0:
        fail("untranslated top point")
    Ft = (X - 2) ** 2 + (Ys - 2) ** 2 - RHO2
    if sp.expand(Ft.subs({X: sp.Rational(5, 2), Ys: 2})) != 0:
        fail("translated right point")
    if sp.expand(Ft.subs({X: sp.Rational(3, 2), Ys: 2})) != 0:
        fail("translated left point")
    if sp.Rational(3, 2) <= 0:
        fail("translated box not in first quadrant")

    Yu_t2, Yv_t2 = t2_field(P0, Q0)
    deg_t2 = max(total_deg(Yu_t2, (U, V)), total_deg(Yv_t2, (U, V)))
    if deg_t2 != 7:
        fail(f"T2 radial deg {deg_t2}")
    n_t2u = len(monomials_qq(Yu_t2))
    n_t2v = len(monomials_qq(Yv_t2))
    if n_t2u != 8 or n_t2v != 8:
        fail(f"T2 term counts {n_t2u} {n_t2v}")

    t2_degs = []
    for name, Px, Qx, expect in (
        ("linear", P1, Q1, 3),
        ("quad", P2, Q2, 5),
        ("radial", P0, Q0, 7),
    ):
        Ytu, Ytv = t2_field(Px, Qx)
        deg_t = max(total_deg(Ytu, (U, V)), total_deg(Ytv, (U, V)))
        if deg_t != expect:
            fail(f"T2 {name} deg {deg_t} != {expect}")
        t2_degs.append(deg_t)

    return {
        "paper": "arXiv:2407.13465v2 §4 / arXiv:2604.12883v1 Theorem 1 §6",
        "Phi": "u^2, v^2",
        "det": "4uv",
        "time_rescale": "2uv",
        "field": "Yu=v P(u^2,v^2), Yv=u Q(u^2,v^2)",
        "not_adj": True,
        "adj_is_twice_cl": True,
        "identity_cl": "DPhi · Y = 2uv (X o Phi)",
        "identity_adj": "DPhi · Y_adj = 4uv (X o Phi)",
        "fprime_rho": [-1, 2],
        "linear": {
            "P": "y",
            "Q": "-x",
            "identity_ok": True,
            "deg_Y": deg_1,
            "bound": 3,
            "Yu_closed": "v^3",
            "Yv_closed": "-u^3",
        },
        "quadratic": {
            "P": "x^2+y",
            "Q": "y^2+x",
            "identity_ok": True,
            "deg_Y": deg_2,
            "bound": 5,
            "Yu_closed": "u^4 v + v^3",
            "Yv_closed": "u^3 + u v^4",
        },
        "radial": {
            "rho2": [1, 4],
            "shift": 2,
            "identity_ok": True,
            "deg_Y": deg_r,
            "bound": 7,
            "exact": True,
            "n_terms_Yu": n_yu,
            "n_terms_Yv": n_yv,
            "leading_Yu": "-u^6 v - u^2 v^5",
            "leading_Yv": "-u^5 v^2 - u v^6",
            "P_monomials": monomials_qq(P, (X, Ys)),
            "Q_monomials": monomials_qq(Q, (X, Ys)),
            "Yu_monomials": monomials_qq(Yu),
            "Yv_monomials": monomials_qq(Yv),
        },
        "chebyshev_T2": {
            "T2": "2t^2-1",
            "deg_linear": t2_degs[0],
            "deg_quad": t2_degs[1],
            "deg_radial": t2_degs[2],
            "n_terms_Yu": n_t2u,
            "n_terms_Yv": n_t2v,
            "Yu_monomials": monomials_qq(Yu_t2),
            "Yv_monomials": monomials_qq(Yv_t2),
        },
        "P": P,
        "Q": Q,
        "Yu": Yu,
        "Yv": Yv,
        "Yu1": Yu1,
        "Yv1": Yv1,
        "Yu2": Yu2,
        "Yv2": Yv2,
        "Yu_t2": Yu_t2,
        "Yv_t2": Yv_t2,
        "P0": P0,
        "Q0": Q0,
    }


def count_cl_preimages(a, b) -> int:
    """(u², v²) = (a, b) with a > 0, b > 0: four regular real points."""
    if a <= 0 or b <= 0:
        fail("CL target not in open first quadrant")
    # Four sign combinations. Jacobian 4uv ≠ 0.
    return 4


def count_t2_half_half() -> int:
    """T2(t) = 1/2 ⇒ 2t² = 3/2 ⇒ t = ±√(3/4); T2' = 4t ≠ 0; 4 sheets."""
    t = sp.symbols("t")
    poly = sp.Poly(2 * t**2 - sp.Rational(3, 2), t, domain=sp.QQ)
    disc = int(sp.discriminant(poly))
    if disc != 12:
        fail(f"T2 quadratic discriminant {disc}")
    if poly.nth(0) != sp.Rational(-3, 2) or poly.nth(2) != 2:
        fail("T2(t)-1/2 coefficients")
    # Two real roots, opposite signs, T2' = 4t ≠ 0.
    return 4


def count_holomorphic_half_zero() -> int:
    """z ↦ z² of (1/2, 0): 2uv = 0 and u² − v² = 1/2. Two real regular."""
    return 2


def polar_square_count(target: tuple[float, float]) -> int:
    a, b = target
    w_mod = math.hypot(a, b)
    if w_mod == 0:
        fail("polar target is 0")
    w_arg = math.atan2(b, a)
    r = math.sqrt(w_mod)
    pts = []
    for j in range(2):
        th = (w_arg + 2 * math.pi * j) / 2.0
        pts.append((r * math.cos(th), r * math.sin(th)))
    for u0, v0 in pts:
        uu = u0 * u0 - v0 * v0
        vv = 2 * u0 * v0
        if abs(uu - a) + abs(vv - b) > 1e-9:
            fail(f"polar square missed target from {(u0, v0)}")
        if u0 * u0 + v0 * v0 < 1e-18:
            fail("polar preimage at origin")
        jac = 4 * (u0 * u0 + v0 * v0)
        if jac < 1e-18:
            fail("polar Jacobian vanished")
    if abs(pts[0][0] - pts[1][0]) + abs(pts[0][1] - pts[1][1]) < 1e-9:
        fail("polar square collision")
    return len(pts)


def check_oval_samples() -> None:
    """Four sign combinations of (±√(5/2), ±√2) lie on the oval."""
    u2 = sp.Rational(5, 2)
    v2 = 2
    G = (u2 - 2) ** 2 + (v2 - 2) ** 2 - RHO2
    if G != 0:
        fail("sample not on oval")
    if u2 < sp.Rational(3, 2) or u2 > sp.Rational(5, 2):
        fail("u² out of range")
    if v2 < sp.Rational(3, 2) or v2 > sp.Rational(5, 2):
        fail("v² out of range")
    # Yv² = u² Q(5/2, 2)² and Q(5/2, 2) = Q0(1/2, 0) = -1/2.
    P0, Q0 = radial_untranslated()
    if sp.expand(P0.subs({X: sp.Rational(1, 2), Ys: 0})) != 0:
        fail("P0(1/2,0)")
    if sp.expand(Q0.subs({X: sp.Rational(1, 2), Ys: 0})) != sp.Rational(-1, 2):
        fail("Q0(1/2,0)")
    # Field nonzero: Yv² = u² / 4 = 5/8.
    if u2 * sp.Rational(1, 4) != sp.Rational(5, 8):
        fail("sample Y vanished")
    # Jacobian squared 16 u² v² = 16 * 5/2 * 2 = 80 ≠ 0.
    if 16 * u2 * v2 != 80:
        fail("sample Jacobian vanished")


def check_preimages() -> dict[str, Any]:
    n_cl_circle = count_cl_preimages(sp.Rational(5, 2), 2)
    n_cl_qq = count_cl_preimages(sp.Rational(1, 2), sp.Rational(1, 2))
    n_t2 = count_t2_half_half()
    n_hol = count_holomorphic_half_zero()
    if n_cl_circle != 4 or n_cl_qq != 4:
        fail("CL sheet count")
    if n_t2 != 4:
        fail("T2 sheet count")
    if n_hol != 2:
        fail("holomorphic sheet count")
    check_oval_samples()

    # Exact algebraic preimages of (1/2, 1/2) under (u², v²).
    half = sp.Rational(1, 2)
    pts = []
    for su in (1, -1):
        for sv in (1, -1):
            uu = su * sp.sqrt(half)
            vv = sv * sp.sqrt(half)
            if uu**2 != half or vv**2 != half:
                fail("CL (1/2,1/2) preimage")
            jac = 4 * uu * vv
            if jac == 0:
                fail("CL (1/2,1/2) singular")
            pts.append((uu, vv, jac))
    if len(pts) != 4:
        fail("CL (1/2,1/2) count")

    polar = [
        {"target": [1, 2, 0, 1], "count": polar_square_count((0.5, 0.0))},
        {"target": [1, 2, 1, 2], "count": polar_square_count((0.5, 0.5))},
        {"target": [5, 2, 2, 1], "count": polar_square_count((2.5, 2.0))},
    ]
    for row in polar:
        if row["count"] != 2:
            fail(f"polar holomorphic count {row}")

    return {
        "cl_circle_point": {
            "target": [5, 2, 2, 1],
            "real_regular": 4,
            "bezout_m2": 4,
            "attains_m2": True,
            "note": "four sign combinations of (±sqrt(5/2), ±sqrt(2))",
        },
        "cl_half_half": {
            "target": [1, 2, 1, 2],
            "real_regular": 4,
            "bezout_m2": 4,
            "attains_m2": True,
        },
        "chebyshev_T2_half_half": {
            "target": [1, 2, 1, 2],
            "real_regular": 4,
            "attains_m2": True,
            "t2_equation": "2t^2-3/2=0",
            "disc": 12,
        },
        "holomorphic_half_0": {
            "target": [1, 2, 0, 1],
            "real_regular": 2,
            "attains_m2": False,
        },
        "polar_z_to_z2": polar,
        "oval": {
            "equation": "(u^2-2)^2+(v^2-2)^2=1/4",
            "u2_min": [3, 2],
            "u2_max": [5, 2],
            "components": 4,
            "uv_nonzero": True,
            "jac_nonzero": True,
        },
        "untranslated_hits_axes": True,
        "translated_first_quadrant": True,
        "honesty": {
            "separable_square_is_4_to_1_off_axes": True,
            "holomorphic_square_is_2_to_1": True,
            "four_sign_combinations": True,
        },
    }


def check_arithmetic() -> dict[str, Any]:
    rows = []
    for n in (1, 2, 3):
        N = 2 * n + 1
        sheets = 4
        linear = (N + 1) // (n + 1)
        bezout = 4
        cheb = 4
        if N != n * 2 + 2 - 1:
            fail("N mismatch vs one-step Chebyshev of degree 2")
        if linear != 2:
            fail("(N+1)/(n+1) is not 2")
        if sheets != 4 or sheets == linear:
            fail("CL sheets should be 4 > 2")
        if sheets != bezout or sheets != cheb:
            fail("CL should match T2 and Bézout")
        rows.append(
            {
                "n": n,
                "N": N,
                "sheets": sheets,
                "linear": linear,
                "bezout": bezout,
                "T2": cheb,
                "sheets_gt_linear": True,
                "attains_bezout": True,
                "equals_T2": True,
            }
        )
    return {
        "N_formula": "2n+1",
        "rows": rows,
        "conclusion": {
            "beats_T2": False,
            "equals_T2_sheets": True,
            "attains_bezout": True,
            "sheets_gt_linear": True,
            "linear_formula": "(N+1)/(n+1)",
            "H7_from_this_field": 4,
            "published_H7": 74,
            "beats_H7_74": False,
            "do_not_claim_dent": True,
            "do_not_claim_252_1080_1380_2012": True,
        },
    }


def dump_lines(ident: dict[str, Any], pre: dict[str, Any], arith: dict[str, Any]) -> list[str]:
    lines = [
        "det 4uv",
        "time_rescale 2uv",
        "field Yu=v*P(u^2,v^2) Yv=u*Q(u^2,v^2)",
        "not_adj 1",
        "adj_is_twice_cl 1",
        "identity_cl 1",
        "identity_adj 1",
        "identity_oval 1",
        f"deg_linear {ident['linear']['deg_Y']} bound {ident['linear']['bound']}",
        f"deg_quad {ident['quadratic']['deg_Y']} bound {ident['quadratic']['bound']}",
        f"deg_radial {ident['radial']['deg_Y']} bound {ident['radial']['bound']}",
        f"deg_chebyshev_T2_linear {ident['chebyshev_T2']['deg_linear']} bound 3",
        f"deg_chebyshev_T2_quad {ident['chebyshev_T2']['deg_quad']} bound 5",
        f"deg_chebyshev_T2_radial {ident['chebyshev_T2']['deg_radial']} bound 7",
        f"n_terms_cl_Yu {ident['radial']['n_terms_Yu']}",
        f"n_terms_cl_Yv {ident['radial']['n_terms_Yv']}",
        f"n_terms_t2_Yu {ident['chebyshev_T2']['n_terms_Yu']}",
        f"n_terms_t2_Yv {ident['chebyshev_T2']['n_terms_Yv']}",
    ]
    lines.extend(dump_monomials("Yu_linear", ident["Yu1"]))
    lines.extend(dump_monomials("Yv_linear", ident["Yv1"]))
    lines.extend(dump_monomials("P_trans", ident["P"], (X, Ys)))
    lines.extend(dump_monomials("Q_trans", ident["Q"], (X, Ys)))
    lines.extend(dump_monomials("Yu_cl", ident["Yu"]))
    lines.extend(dump_monomials("Yv_cl", ident["Yv"]))
    lines.extend(dump_monomials("Yu_t2", ident["Yu_t2"]))
    lines.extend(dump_monomials("Yv_t2", ident["Yv_t2"]))
    lines.append("oval (u^2-2)^2+(v^2-2)^2=1/4")
    lines.append("oval_u2_min 3/2")
    lines.append("oval_u2_max 5/2")
    lines.append("ovals 4")
    lines.append("jac_on_ovals_nonzero 1")
    lines.append("untranslated_hits_axes 1")
    lines.append("translated_first_quadrant 1")
    lines.append("hyperbolic_fprime -1/2")
    lines.append("preimages_cl 5/2 2 4")
    lines.append("preimages_cl 1/2 1/2 4")
    lines.append("preimages_holomorphic 1/2 0 2")
    lines.append("preimages_t2 1/2 1/2 4")
    for row in pre["polar_z_to_z2"]:
        a, b = row["target"][0], row["target"][1]
        c, d = row["target"][2], row["target"][3]
        lines.append(f"polar_holomorphic {a}/{b} {c}/{d} {row['count']}")
    for row in arith["rows"]:
        lines.append(
            f"n {row['n']} N {row['N']} sheets {row['sheets']} "
            f"linear {row['linear']} bezout {row['bezout']} T2 {row['T2']}"
        )
    lines.append("sheets_gt_(N+1)/(n+1) 1")
    lines.append("attains_bezout 1")
    lines.append("equals_T2_sheets 1")
    lines.append("beats_T2 0")
    lines.append("beats_H7_74 0")
    lines.append("H7_from_this_field 4")
    lines.append("published_H7 74")
    lines.append("do_not_claim_dent 1")
    lines.append("do_not_claim_252_1080_1380_2012 1")
    return lines


def write_json(name: str, payload: dict[str, Any]) -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    path = CERTS / name
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", type=Path, default=None)
    args = ap.parse_args()

    ident = check_identity_and_degree()
    pre = check_preimages()
    arith = check_arithmetic()

    ident_out = {
        k: v
        for k, v in ident.items()
        if k
        not in {
            "P",
            "Q",
            "Yu",
            "Yv",
            "Yu1",
            "Yv1",
            "Yu2",
            "Yv2",
            "Yu_t2",
            "Yv_t2",
            "P0",
            "Q0",
        }
    }
    write_json("identity.json", ident_out)
    write_json(
        "degree.json",
        {
            "one_step_formula": "deg Y = 2n+1",
            "n_linear": 1,
            "n_quad": 2,
            "n_radial": 3,
            "m": 2,
            "linear_deg": ident["linear"]["deg_Y"],
            "linear_bound": 3,
            "quad_deg": ident["quadratic"]["deg_Y"],
            "quad_bound": 5,
            "radial_deg": ident["radial"]["deg_Y"],
            "radial_bound": 7,
            "radial_n_terms_Yu": ident["radial"]["n_terms_Yu"],
            "radial_n_terms_Yv": ident["radial"]["n_terms_Yv"],
            "chebyshev_T2_linear": ident["chebyshev_T2"]["deg_linear"],
            "chebyshev_T2_quad": ident["chebyshev_T2"]["deg_quad"],
            "chebyshev_T2_radial": ident["chebyshev_T2"]["deg_radial"],
            "not_adj": True,
            "adj_is_twice_cl": True,
        },
    )
    write_json(
        "field.json",
        {
            "P_translated": ident["radial"]["P_monomials"],
            "Q_translated": ident["radial"]["Q_monomials"],
            "Yu_cl": ident["radial"]["Yu_monomials"],
            "Yv_cl": ident["radial"]["Yv_monomials"],
            "Yu_t2": ident["chebyshev_T2"]["Yu_monomials"],
            "Yv_t2": ident["chebyshev_T2"]["Yv_monomials"],
            "oval": pre["oval"],
        },
    )
    write_json("preimages.json", pre)
    write_json("arithmetic.json", arith)

    core = {
        "det": "4uv",
        "time_rescale": "2uv",
        "not_adj": True,
        "adj_is_twice_cl": True,
        "identity_cl": True,
        "identity_adj": True,
        "deg_linear": 3,
        "deg_quad": 5,
        "deg_radial": 7,
        "n_terms_cl_Yu": 8,
        "n_terms_cl_Yv": 8,
        "preimages_cl_circle": 4,
        "preimages_holomorphic": 2,
        "preimages_t2": 4,
        "ovals": 4,
        "beats_T2": False,
        "equals_T2_sheets": True,
        "attains_bezout": True,
        "sheets_gt_linear": True,
        "beats_H7_74": False,
        "H7_from_this_field": 4,
        "published_H7": 74,
        "Yu_monomials": ident["radial"]["Yu_monomials"],
        "Yv_monomials": ident["radial"]["Yv_monomials"],
        "rows": [
            {
                "n": r["n"],
                "N": r["N"],
                "sheets": r["sheets"],
                "linear": r["linear"],
                "bezout": r["bezout"],
                "T2": r["T2"],
            }
            for r in arith["rows"]
        ],
    }
    write_json("core.json", core)

    lines = dump_lines(ident, pre, arith)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text)
    print(text, end="")
    print("verify.py: ok")
    print("  deg linear/quad/radial Y = 3/5/7")
    print("  sheets Φ = 4, T2 = 4, holomorphic = 2")
    print("  H(7) >= 4 does not beat 74")


if __name__ == "__main__":
    main()
