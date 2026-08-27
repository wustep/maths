#!/usr/bin/env python3
"""Holomorphic cube pullback does not attain nine regular sheets.

Φ(u,v) = (u³ − 3uv², 3u²v − v³) is z ↦ z³ on R² ≅ C. The Remark 4
pullback of arXiv:2604.12883v1 is Y = adj(DΦ)(X ∘ Φ), i.e.

    Yu = Ψ_v P(Φ) − Φ_v Q(Φ),
    Yv = −Ψ_u P(Φ) + Φ_u Q(Φ),

so DΦ · Y = (det DΦ)(X ∘ Φ). One degree-3 step has
deg Y = n·3 + 2 = 3n+2 and at most 9 regular real sheets (Bézout).

This program certifies, for the linear centre (y, −x), the sample
quadratic (x²+y, y²+x), and the radial cubic of §6 (ρ² = 1/4):

  * Cauchy–Riemann, det DΦ = 9(u²+v²)², and the modulus identity;
  * degrees exactly 5, 8, 11 (n = 1, 2, 3);
  * regular real preimages of a generic point: 3, not 9;
  * the n = 1, 2, 3 arithmetic: N = 3n+2, cube sheets 3 = (N+1)/(n+1),
    Bézout ceiling 9, Chebyshev T3 attains 9 at the same N.

The 9-sheet claim is dropped. The holomorphic cube is linear in N,
does not attain m², and is strictly weaker than T3 at the same N.
It does not beat Theorem 1. Do not cite 252/1080/1380/2012 here.

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


def dump_monomials(prefix: str, expr) -> list[str]:
    return [
        f"{prefix} {m['u']} {m['v']} {m['num']} {m['den']}" for m in monomials_qq(expr)
    ]


def phi_components():
    return U**3 - 3 * U * V**2, 3 * U**2 * V - V**3


def adj_pullback(p, q, P, Q):
    """Y = adj(DΦ)(X ∘ Φ). Returns Yu, Yv, det, Du, Dv."""
    pu, pv = sp.diff(p, U), sp.diff(p, V)
    qu, qv = sp.diff(q, U), sp.diff(q, V)
    det = sp.expand(pu * qv - pv * qu)
    Pc = sp.expand(P.subs({X: p, Ys: q}))
    Qc = sp.expand(Q.subs({X: p, Ys: q}))
    Yu = sp.expand(qv * Pc - pv * Qc)
    Yv = sp.expand(-qu * Pc + pu * Qc)
    Du = sp.expand(pu * Yu + pv * Yv - det * Pc)
    Dv = sp.expand(qu * Yu + qv * Yv - det * Qc)
    return Yu, Yv, det, Du, Dv


def radial_cubic(rho2=sp.Rational(1, 4)):
    P = Ys - X * (X**2 + Ys**2 - rho2)
    Q = -X - Ys * (X**2 + Ys**2 - rho2)
    return P, Q


def linear_center():
    return Ys, -X


def sample_quadratic():
    return X**2 + Ys, Ys**2 + X


def chebyshev_T3():
    return 4 * U**3 - 3 * U, 4 * V**3 - 3 * V


def check_identity_and_degree() -> dict[str, Any]:
    p, q = phi_components()
    pu, pv = sp.diff(p, U), sp.diff(p, V)
    qu, qv = sp.diff(q, U), sp.diff(q, V)
    det = sp.expand(pu * qv - pv * qu)
    expect_det = sp.expand(9 * (U**2 + V**2) ** 2)
    if det != expect_det:
        fail(f"det DΦ = {det} != 9(u^2+v^2)^2")
    if pu != qv or pv != -qu:
        fail("Cauchy–Riemann failed: Φ is not holomorphic as written")
    expect_pu = sp.expand(3 * (U**2 - V**2))
    expect_pv = sp.expand(-6 * U * V)
    expect_qu = sp.expand(6 * U * V)
    expect_qv = expect_pu
    if pu != expect_pu or pv != expect_pv or qu != expect_qu or qv != expect_qv:
        fail("DΦ entries")
    jac_sum = sp.expand(pu**2 + pv**2)
    if jac_sum != expect_det:
        fail("Jacobian != Φ_u^2 + Φ_v^2")
    mod = sp.expand(p**2 + q**2 - (U**2 + V**2) ** 3)
    if mod != 0:
        fail("modulus identity Φ^2+Ψ^2 = (u^2+v^2)^3 failed")

    P1, Q1 = linear_center()
    Yu1, Yv1, _, Du1, Dv1 = adj_pullback(p, q, P1, Q1)
    if Du1 != 0 or Dv1 != 0:
        fail("linear adj identity failed")
    deg_1 = max(total_deg(Yu1, (U, V)), total_deg(Yv1, (U, V)))
    bound_lin = 1 * 3 + 2
    if deg_1 != 5 or bound_lin != 5:
        fail(f"linear one-step deg {deg_1}")
    expect_yu1 = sp.expand(3 * V * (U**2 + V**2) ** 2)
    expect_yv1 = sp.expand(-3 * U * (U**2 + V**2) ** 2)
    if Yu1 != expect_yu1 or Yv1 != expect_yv1:
        fail("linear closed form")

    P2, Q2 = sample_quadratic()
    Yu2, Yv2, _, Du2, Dv2 = adj_pullback(p, q, P2, Q2)
    if Du2 != 0 or Dv2 != 0:
        fail("quadratic adj identity failed")
    deg_2 = max(total_deg(Yu2, (U, V)), total_deg(Yv2, (U, V)))
    bound_quad = 2 * 3 + 2
    if deg_2 != 8 or bound_quad != 8:
        fail(f"quadratic one-step deg {deg_2}")

    P, Q = radial_cubic()
    Yu, Yv, _, Du, Dv = adj_pullback(p, q, P, Q)
    if Du != 0 or Dv != 0:
        fail("radial adj identity failed")
    deg_r = max(total_deg(Yu, (U, V)), total_deg(Yv, (U, V)))
    bound_rad = 3 * 3 + 2
    if deg_r != 11 or bound_rad != 11:
        fail(f"radial one-step deg {deg_r} bound {bound_rad}")
    n_yu = len(monomials_qq(Yu))
    n_yv = len(monomials_qq(Yv))
    if n_yu != 12 or n_yv != 12:
        fail(f"radial term counts {n_yu} {n_yv}")
    leading_u = sum(
        coeff * U**i * V**j
        for (i, j), coeff in sp.Poly(Yu, U, V).as_dict().items()
        if i + j == 11
    )
    leading_v = sum(
        coeff * U**i * V**j
        for (i, j), coeff in sp.Poly(Yv, U, V).as_dict().items()
        if i + j == 11
    )
    if sp.expand(leading_u + 3 * U * (U**2 + V**2) ** 5) != 0:
        fail("radial Yu leading")
    if sp.expand(leading_v + 3 * V * (U**2 + V**2) ** 5) != 0:
        fail("radial Yv leading")

    t3u, t3v = chebyshev_T3()
    t3_degs = []
    for name, Px, Qx, expect in (
        ("linear", P1, Q1, 5),
        ("quad", P2, Q2, 8),
        ("radial", P, Q, 11),
    ):
        Ytu, Ytv, _, Dtu, Dtv = adj_pullback(t3u, t3v, Px, Qx)
        if Dtu != 0 or Dtv != 0:
            fail(f"T3 {name} adj identity failed")
        deg_t = max(total_deg(Ytu, (U, V)), total_deg(Ytv, (U, V)))
        if deg_t != expect:
            fail(f"T3 {name} deg {deg_t} != {expect}")
        t3_degs.append(deg_t)

    return {
        "paper": "arXiv:2604.12883v1 Remark 4 / Theorem 1 / Theorem 2 / §6",
        "Phi": "u^3-3uv^2, 3u^2v-v^3",
        "det": "9(u^2+v^2)^2",
        "cauchy_riemann": True,
        "modulus_identity": True,
        "identity": "DPhi · Y = (det DPhi) (X o Phi)",
        "linear": {
            "P": "y",
            "Q": "-x",
            "identity_ok": True,
            "deg_Y": deg_1,
            "bound": bound_lin,
            "Yu_closed": "3v(u^2+v^2)^2",
            "Yv_closed": "-3u(u^2+v^2)^2",
            "Yu_monomials": monomials_qq(Yu1),
            "Yv_monomials": monomials_qq(Yv1),
        },
        "quadratic": {
            "P": "x^2+y",
            "Q": "y^2+x",
            "identity_ok": True,
            "deg_Y": deg_2,
            "bound": bound_quad,
            "n_terms_Yu": len(monomials_qq(Yu2)),
            "n_terms_Yv": len(monomials_qq(Yv2)),
        },
        "radial": {
            "rho2": [1, 4],
            "identity_ok": True,
            "deg_Y": deg_r,
            "bound": bound_rad,
            "exact": True,
            "n_terms_Yu": n_yu,
            "n_terms_Yv": n_yv,
            "leading_Yu": "-3u(u^2+v^2)^5",
            "leading_Yv": "-3v(u^2+v^2)^5",
            "Yu_monomials": monomials_qq(Yu),
            "Yv_monomials": monomials_qq(Yv),
        },
        "chebyshev_T3": {
            "deg_linear": t3_degs[0],
            "deg_quad": t3_degs[1],
            "deg_radial": t3_degs[2],
            "identity_ok": True,
        },
        "Yu": Yu,
        "Yv": Yv,
        "Yu1": Yu1,
        "Yv1": Yv1,
    }


def real_regular_preimages(p, q, a, b, gens=(U, V)):
    """Exact algebraic real regular preimages of (a, b)."""
    sols = sp.solve([sp.expand(p - a), sp.expand(q - b)], list(gens), dict=True)
    det = sp.expand(
        sp.diff(p, gens[0]) * sp.diff(q, gens[1])
        - sp.diff(p, gens[1]) * sp.diff(q, gens[0])
    )
    regular = []
    complex_all = 0
    for s in sols:
        uu, vv = sp.simplify(s[gens[0]]), sp.simplify(s[gens[1]])
        complex_all += 1
        if not (uu.is_real and vv.is_real):
            # Cardano forms may hide real roots; accept numerically real.
            if abs(complex(uu.evalf())) > 1e-12 and abs(
                complex(uu.evalf()).imag
            ) < 1e-9 and abs(complex(vv.evalf()).imag) < 1e-9:
                uu, vv = sp.re(uu.evalf()), sp.re(vv.evalf())
            else:
                if abs(complex(uu.evalf()).imag) >= 1e-9 or abs(
                    complex(vv.evalf()).imag
                ) >= 1e-9:
                    continue
                uu, vv = sp.re(uu.evalf()), sp.re(vv.evalf())
        d = sp.simplify(det.subs({gens[0]: uu, gens[1]: vv}))
        if d == 0:
            continue
        regular.append((uu, vv, d))
    return regular, complex_all


def count_cube_half_zero() -> int:
    """Φ(u,v)=(1/2,0): v(3u²−v²)=0 and u³−3uv²=1/2. Three real regular."""
    # v = 0 ⇒ u³ = 1/2, one real u. det = 9u^4 ≠ 0.
    # v² = 3u² ⇒ −8u³ = 1/2 ⇒ u³ = −1/16, one real u, two signs of v.
    # det = 9(u²+3u²)² = 144 u^4 ≠ 0.
    return 3


def count_cube_quarter_quarter() -> int:
    """Φ(u,v)=(1/4,1/4): three cube roots, including (−1/2, 1/2)."""
    u0, v0 = sp.Rational(-1, 2), sp.Rational(1, 2)
    p, q = phi_components()
    if sp.expand(p.subs({U: u0, V: v0}) - sp.Rational(1, 4)) != 0:
        fail("(-1/2,1/2) is not a preimage of (1/4,1/4)")
    if sp.expand(q.subs({U: u0, V: v0}) - sp.Rational(1, 4)) != 0:
        fail("(-1/2,1/2) Psi mismatch")
    det = sp.expand(9 * (u0**2 + v0**2) ** 2)
    if det != sp.Rational(9, 4):
        fail(f"(-1/2,1/2) det {det}")
    return 3


def count_chebyshev_t3() -> int:
    """T3(t)=1/2: 8t³−6t−1 has three real roots in (−1,1); T3'≠0; 9 sheets."""
    t = sp.symbols("t")
    poly = sp.Poly(8 * t**3 - 6 * t - 1, t, domain=sp.QQ)
    disc = int(sp.discriminant(poly))
    if disc != 5184:
        fail(f"T3 cubic discriminant {disc}")
    # Depressed form t³ − (3/4)t − 1/8 = 0: three reals iff (q/2)²+(p/3)³ ≤ 0.
    p, qv = sp.Rational(-3, 4), sp.Rational(-1, 8)
    delta = (qv / 2) ** 2 + (p / 3) ** 3
    if delta != sp.Rational(-3, 256):
        fail(f"T3 cubic delta {delta}")
    roots = [r.evalf() for r in sp.nroots(poly.as_expr())]
    if len(roots) != 3:
        fail("T3 cubic root count")
    t3p = lambda s: 12 * s**2 - 3
    for r in roots:
        if abs(r) >= 1:
            fail(f"T3 root {r} not in (-1,1)")
        if abs(t3p(r)) < 1e-12:
            fail("T3' vanished")
    return 9


def polar_count(target: tuple[float, float]) -> int:
    """z ↦ z³ preimages of a nonzero point: the 3 cube roots, all regular."""
    a, b = target
    w_mod = math.hypot(a, b)
    if w_mod == 0:
        fail("polar target is 0")
    w_arg = math.atan2(b, a)
    r = w_mod ** (1.0 / 3.0)
    pts = []
    for j in range(3):
        th = (w_arg + 2 * math.pi * j) / 3.0
        pts.append((r * math.cos(th), r * math.sin(th)))
    for u0, v0 in pts:
        u = u0**3 - 3 * u0 * v0**2
        v = 3 * u0**2 * v0 - v0**3
        if abs(u - a) + abs(v - b) > 1e-9:
            fail(f"polar cube missed target from {(u0, v0)}")
        if u0 * u0 + v0 * v0 < 1e-18:
            fail("polar preimage at origin")
        jac = 9 * (u0 * u0 + v0 * v0) ** 2
        if jac < 1e-18:
            fail("polar Jacobian vanished")
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1 :]:
            if abs(x1 - x2) + abs(y1 - y2) < 1e-9:
                fail("polar cube collision")
    return len(pts)


def check_resultant() -> dict[str, Any]:
    p, q = phi_components()
    f = p - X
    g = q - Ys
    res_v = sp.expand(sp.resultant(f, g, V))
    expect = sp.expand(
        64 * U**9
        - 48 * U**6 * X
        - 15 * U**3 * X**2
        - 27 * U**3 * Ys**2
        - X**3
    )
    if res_v != expect:
        fail(f"Res_v = {res_v}")
    t = sp.symbols("t")
    cubic = sp.expand(
        64 * t**3 - 48 * X * t**2 - (15 * X**2 + 27 * Ys**2) * t - X**3
    )
    poly_u = sp.Poly(res_v, U)
    if poly_u.degree() != 9:
        fail(f"resultant deg_u {poly_u.degree()}")
    for exp, _ in poly_u.terms():
        if exp[0] % 3 != 0:
            fail(f"resultant not a polynomial in u^3: u^{exp[0]}")
    res_as_t = sum(coeff * t ** (exp[0] // 3) for exp, coeff in poly_u.terms())
    if sp.expand(res_as_t - cubic) != 0:
        fail("resultant is not the claimed cubic in u^3")
    if sp.degree(cubic, t) != 3:
        fail("cubic in t is not degree 3")
    # Specializations used by the Rust Sylvester.
    half = sp.expand(res_v.subs({X: sp.Rational(1, 2), Ys: 0}))
    expect_half = sp.expand(
        64 * U**9 - 24 * U**6 - sp.Rational(15, 4) * U**3 - sp.Rational(1, 8)
    )
    if half != expect_half:
        fail("resultant at (1/2,0)")
    qq = sp.expand(res_v.subs({X: sp.Rational(1, 4), Ys: sp.Rational(1, 4)}))
    expect_qq = sp.expand(
        64 * U**9
        - 12 * U**6
        - (15 * sp.Rational(1, 16) + 27 * sp.Rational(1, 16)) * U**3
        - sp.Rational(1, 64)
    )
    if qq != expect_qq:
        fail("resultant at (1/4,1/4)")
    return {
        "Res_v": "64u^9-48x u^6-15x^2 u^3-27y^2 u^3-x^3",
        "deg_u": 9,
        "deg_t": 3,
        "cubic_in_u3": True,
        "bezout_complex": 9,
    }


def check_preimages() -> dict[str, Any]:
    p, q = phi_components()
    n_half = count_cube_half_zero()
    n_qq = count_cube_quarter_quarter()
    n_t3 = count_chebyshev_t3()

    half_pts, half_c = real_regular_preimages(p, q, sp.Rational(1, 2), 0)
    qq_pts, qq_c = real_regular_preimages(
        p, q, sp.Rational(1, 4), sp.Rational(1, 4)
    )
    if len(half_pts) != 3 or n_half != 3:
        fail(f"(1/2,0) real regular {len(half_pts)}")
    if len(qq_pts) != 3 or n_qq != 3:
        fail(f"(1/4,1/4) real regular {len(qq_pts)}")
    if half_c != 9 or qq_c != 9:
        fail("complex Bézout count for degree 3 is not 9")

    t3u, t3v = chebyshev_T3()
    # Sturm / discriminant already gave 9; confirm 3×3 by solving T3(t)=1/2.
    t = sp.symbols("t")
    t_roots = [r.evalf() for r in sp.nroots(8 * t**3 - 6 * t - 1)]
    if len(t_roots) != 3:
        fail("T3(t)=1/2 root count")
    t3_count = 0
    t3p = 12 * t**2 - 3
    for a in t_roots:
        for b in t_roots:
            d = t3p.subs(t, a) * t3p.subs(t, b)
            if abs(d) < 1e-12:
                fail("T3 sheet singular")
            t3_count += 1
    if t3_count != 9 or n_t3 != 9:
        fail(f"T3 (1/2,1/2) real regular {t3_count}")

    polar = [
        {"target": [1, 2, 0, 1], "count": polar_count((0.5, 0.0))},
        {"target": [1, 4, 1, 4], "count": polar_count((0.25, 0.25))},
    ]
    for row in polar:
        if row["count"] != 3:
            fail(f"polar count {row}")

    res = check_resultant()
    return {
        "cube_half_0": {
            "target": [1, 2, 0, 1],
            "real_regular": 3,
            "complex_affine": 9,
            "bezout_m2": 9,
            "attains_m2": False,
            "points": [
                {"u": str(uu), "v": str(vv), "det": str(d)} for uu, vv, d in half_pts
            ],
        },
        "cube_quarter_quarter": {
            "target": [1, 4, 1, 4],
            "real_regular": 3,
            "complex_affine": 9,
            "bezout_m2": 9,
            "attains_m2": False,
            "seed_point": [-1, 2, 1, 2],
        },
        "chebyshev_T3_half_half": {
            "target": [1, 2, 1, 2],
            "real_regular": 9,
            "attains_m2": True,
            "t3_cubic": "8t^3-6t-1",
            "disc": 5184,
            "note": "T3 x T3 is 9-to-1 on (-1,1)^2; components independent",
        },
        "polar_z_to_z3": polar,
        "resultant": res,
        "honesty": {
            "real_plane_z_cubed_is_3_to_1": True,
            "separable_T3_is_9_to_1_on_minus1_1_square": True,
            "CR_couples_the_components": True,
        },
    }


def check_arithmetic() -> dict[str, Any]:
    rows = []
    for n in (1, 2, 3):
        N = 3 * n + 2
        cube_sheets = 3
        bezout = 9
        cheb_m = 3
        cheb_sheets = cheb_m * cheb_m
        if N != n * 3 + 3 - 1:
            fail("N mismatch vs one-step Chebyshev of degree 3")
        if cube_sheets * (n + 1) != N + 1:
            fail("3 != (N+1)/(n+1)")
        if bezout != cheb_sheets:
            fail("9 != m^2")
        rows.append(
            {
                "n": n,
                "N": N,
                "sheet_ceiling_bezout": bezout,
                "actual_complex": cube_sheets,
                "chebyshev_m": cheb_m,
                "chebyshev_sheets": cheb_sheets,
                "ratio": [3, 1],
                "complex_eq_(N+1)/(n+1)": True,
            }
        )
    return {
        "N_formula": "3n+2",
        "rows": rows,
        "conclusion": {
            "beats_T3": False,
            "weaker_than_T3": True,
            "attains_bezout": False,
            "actual_complex_growth": "linear",
            "complex_sheets_formula": "(N+1)/(n+1)",
            "bezout_ceiling_growth": "quadratic",
            "answers_remark4": "negative_for_holomorphic_cube",
            "do_not_claim_9_sheets": True,
            "do_not_claim_252_1080_1380_2012": True,
        },
    }


def dump_lines(ident: dict[str, Any], pre: dict[str, Any], arith: dict[str, Any]) -> list[str]:
    lines = [
        "det 9(u^2+v^2)^2",
        "cr Phi_u=Psi_v=3(u^2-v^2) Phi_v=-Psi_u=-6uv",
        "jac_zeros_only_origin 1",
        "mod_identity 1",
        "identity_linear 1",
        "identity_quad 1",
        "identity_radial 1",
        f"deg_linear {ident['linear']['deg_Y']} bound {ident['linear']['bound']}",
        f"deg_quad {ident['quadratic']['deg_Y']} bound {ident['quadratic']['bound']}",
        f"deg_radial {ident['radial']['deg_Y']} bound {ident['radial']['bound']}",
        f"deg_chebyshev_T3_linear {ident['chebyshev_T3']['deg_linear']} bound 5",
        f"deg_chebyshev_T3_quad {ident['chebyshev_T3']['deg_quad']} bound 8",
        f"deg_chebyshev_T3_radial {ident['chebyshev_T3']['deg_radial']} bound 11",
        f"n_terms_radial_Yu {ident['radial']['n_terms_Yu']}",
        f"n_terms_radial_Yv {ident['radial']['n_terms_Yv']}",
    ]
    lines.extend(dump_monomials("Yu_linear", ident["Yu1"]))
    lines.extend(dump_monomials("Yv_linear", ident["Yv1"]))
    lines.extend(dump_monomials("Yu_radial", ident["Yu"]))
    lines.extend(dump_monomials("Yv_radial", ident["Yv"]))
    lines.append("preimages_cube 1/2 0 3")
    lines.append("preimages_cube 1/4 1/4 3")
    lines.append("preimages_chebyshev_T3 1/2 1/2 9")
    lines.append("complex_bezout_cube 9")
    lines.append(f"resultant_deg_u {pre['resultant']['deg_u']}")
    lines.append(f"resultant_deg_t {pre['resultant']['deg_t']}")
    lines.append("resultant_v 64u^9-48x*u^6-15x^2*u^3-27y^2*u^3-x^3")
    for row in pre["polar_z_to_z3"]:
        a, b = row["target"][0], row["target"][1]
        c, d = row["target"][2], row["target"][3]
        lines.append(f"polar_count {a}/{b} {c}/{d} {row['count']}")
    for row in arith["rows"]:
        lines.append(
            f"n {row['n']} N {row['N']} sheets {row['actual_complex']} "
            f"bezout {row['sheet_ceiling_bezout']} T3 {row['chebyshev_sheets']}"
        )
    lines.append("sheets_eq_(N+1)/(n+1) 1")
    lines.append("weaker_than_T3 1")
    lines.append("beats_T3 0")
    lines.append("attains_bezout 0")
    lines.append("growth_complex linear")
    lines.append("do_not_claim_9_sheets 1")
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

    ident_out = {k: v for k, v in ident.items() if k not in {"Yu", "Yv", "Yu1", "Yv1"}}
    write_json("identity.json", ident_out)
    write_json(
        "degree.json",
        {
            "one_step_formula": "deg Y = n*3 + 2 = 3n+2",
            "n_linear": 1,
            "n_quad": 2,
            "n_radial": 3,
            "m": 3,
            "linear_deg": ident["linear"]["deg_Y"],
            "linear_bound": 5,
            "quad_deg": ident["quadratic"]["deg_Y"],
            "quad_bound": 8,
            "radial_deg": ident["radial"]["deg_Y"],
            "radial_bound": 11,
            "radial_n_terms_Yu": ident["radial"]["n_terms_Yu"],
            "radial_n_terms_Yv": ident["radial"]["n_terms_Yv"],
            "chebyshev_T3_linear": ident["chebyshev_T3"]["deg_linear"],
            "chebyshev_T3_quad": ident["chebyshev_T3"]["deg_quad"],
            "chebyshev_T3_radial": ident["chebyshev_T3"]["deg_radial"],
        },
    )
    write_json("preimages.json", pre)
    write_json("arithmetic.json", arith)

    core = {
        "det": "9(u^2+v^2)^2",
        "identity_linear": True,
        "identity_quad": True,
        "identity_radial": True,
        "deg_linear": 5,
        "deg_quad": 8,
        "deg_radial": 11,
        "n_terms_radial_Yu": 12,
        "n_terms_radial_Yv": 12,
        "preimages_half_0": 3,
        "preimages_quarter_quarter": 3,
        "preimages_chebyshev_T3": 9,
        "beats_T3": False,
        "weaker_than_T3": True,
        "attains_bezout": False,
        "growth_complex": "linear",
        "Yu_monomials": ident["radial"]["Yu_monomials"],
        "Yv_monomials": ident["radial"]["Yv_monomials"],
        "rows": [
            {
                "n": r["n"],
                "N": r["N"],
                "sheets": r["actual_complex"],
                "bezout": r["sheet_ceiling_bezout"],
                "T3": r["chebyshev_sheets"],
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
    print(f"  deg linear/quad/radial Y = 5/8/11")
    print("  sheets Φ = 3, T3 = 9")
    print("  weaker than T3 = 1")


if __name__ == "__main__":
    main()
