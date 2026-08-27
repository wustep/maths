#!/usr/bin/env python3
"""T2 Chebyshev pullback of the §6 radial cubic (arXiv:2604.12883v1).

q1 line C wrote the T3 field (degree 11, nine ovals). This program
writes the m=2 field the same way:

    T2(t) = 2t^2 - 1,    T2'(t) = 4t,
    Φ(u,v) = (T2(u), T2(v)),
    Y = (T2'(v) P(Φ), T2'(u) Q(Φ)).

For the radial cubic with ρ² = 1/4 one has deg Y = 3*2 + 2 - 1 = 7,
eight monomials in each component, and four compact ovals, one per
open branch rectangle of T2 on (−1,1).

H(7) ≥ 4 from this field does not beat Prohens–Torregrosa H(7) ≥ 74.
It is the same four sheets at N=7 as the Christopher–Lloyd four-fold
(Corollary 1 of the paper). Do not claim 252/1080/1380/2012 here.

Replay: python3 verify.py
"""

from __future__ import annotations

import argparse
import json
import os
from fractions import Fraction
from typing import Any

from sympy import (
    Integer,
    Poly,
    QQ,
    ZZ,
    cancel,
    factor,
    gcd,
    symbols,
)

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, "certs")

u, v, t, x, y = symbols("u v t x y")


def fail(msg: str) -> None:
    raise SystemExit(f"verify.py FAIL: {msg}")


def chebyshev_T(m: int) -> Poly:
    """T_m in Z[t] by T_0=1, T_1=t, T_k=2t T_{k-1}-T_{k-2}."""
    if m < 0:
        fail("Chebyshev index must be nonnegative")
    t_poly = Poly(t, t, domain=ZZ)
    prev = Poly(1, t, domain=ZZ)
    curr = t_poly
    if m == 0:
        return prev
    if m == 1:
        return curr
    for _ in range(2, m + 1):
        prev, curr = curr, (2 * t_poly * curr - prev).as_poly(t, domain=ZZ)
    return curr


def poly_coeffs_asc(p: Poly) -> list[int]:
    deg = p.degree()
    return [int(p.nth(i)) for i in range(deg + 1)]


def sturm_chain(p: Poly) -> list[Poly]:
    chain = [p.as_poly(t, domain=QQ), p.diff(t).as_poly(t, domain=QQ)]
    while chain[-1].degree() >= 0 and not chain[-1].is_zero:
        rem = -(chain[-2].rem(chain[-1]))
        rem = rem.as_poly(t, domain=QQ)
        if rem.is_zero:
            break
        chain.append(rem)
    if chain[-1].is_zero:
        chain.pop()
    return chain


def sturm_sign_variations(chain: list[Poly], a: Fraction) -> int:
    signs: list[int] = []
    for q in chain:
        val = q.subs(t, QQ(a.numerator, a.denominator))
        if val == 0:
            continue
        signs.append(1 if val > 0 else -1)
    return sum(1 for i in range(len(signs) - 1) if signs[i] * signs[i + 1] < 0)


def count_real_roots_open(p: Poly, left: Fraction, right: Fraction) -> int:
    """Number of distinct real roots of p in (left, right). p square-free."""
    if p.as_poly(t, domain=QQ).degree() <= 0:
        return 0
    chain = sturm_chain(p.as_poly(t, domain=QQ))
    lo = left
    hi = right
    step = (right - left) / 10**6
    for _ in range(8):
        if all(q.subs(t, QQ(lo.numerator, lo.denominator)) != 0 for q in chain):
            break
        lo = lo + step
    for _ in range(8):
        if all(q.subs(t, QQ(hi.numerator, hi.denominator)) != 0 for q in chain):
            break
        hi = hi - step
    if lo >= hi:
        fail("Sturm interval collapsed")
    return sturm_sign_variations(chain, lo) - sturm_sign_variations(chain, hi)


def evaluate_univariate(p: Poly, arg: Fraction) -> Fraction:
    val = p.subs(t, QQ(arg.numerator, arg.denominator))
    return Fraction(int(val.p), int(val.q)) if hasattr(val, "p") else Fraction(val)


def pullback(P_expr, Q_expr, tm: Poly):
    """Y = (T'(v) P∘Φ, T'(u) Q∘Φ) with Φ=(T(u),T(v))."""
    T_u = tm.as_expr().subs(t, u)
    T_v = tm.as_expr().subs(t, v)
    Tp_u = tm.diff(t).as_expr().subs(t, u)
    Tp_v = tm.diff(t).as_expr().subs(t, v)
    P_phi = P_expr.subs({x: T_u, y: T_v})
    Q_phi = Q_expr.subs({x: T_u, y: T_v})
    Yu = cancel(Tp_v * P_phi)
    Yv = cancel(Tp_u * Q_phi)
    return Yu, Yv, T_u, T_v, Tp_u, Tp_v


def total_degree_bivariate(expr) -> int:
    poly = Poly(cancel(expr), u, v, domain=QQ)
    if poly.is_zero:
        return -1
    return int(poly.total_degree())


def monomials_qq(expr) -> list[dict[str, int]]:
    poly = Poly(cancel(expr), u, v, domain=QQ)
    out = []
    for exp, coeff in poly.as_dict().items():
        frac = Fraction(int(coeff.p), int(coeff.q)) if hasattr(coeff, "p") else Fraction(coeff)
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


def dump_monomials(prefix: str, mons: list[dict[str, int]]) -> list[str]:
    return [f"{prefix} {m['u']} {m['v']} {m['num']} {m['den']}" for m in mons]


def section6_field(rho2: Fraction):
    P = y - x * (x**2 + y**2 - rho2)
    Q = -x - y * (x**2 + y**2 - rho2)
    return P, Q


def check_chebyshev() -> dict[str, Any]:
    named = {
        0: [1],
        1: [0, 1],
        2: [-1, 0, 2],
        3: [0, -3, 0, 4],
    }
    for m, coeffs in named.items():
        got = poly_coeffs_asc(chebyshev_T(m))
        if got != coeffs:
            fail(f"T_{m} coeffs {got} != {coeffs}")

    t2 = chebyshev_T(2)
    if t2.as_expr() != 2 * t**2 - 1:
        fail("T2(t) != 2t^2-1")
    t2p = t2.diff(t)
    if t2p.as_expr() != 4 * t:
        fail("T2' != 4t")

    ident = cancel((4 * t2**2 + (1 - t**2) * t2p**2 - 4).as_expr())
    if ident != 0:
        fail("Pell identity failed for m=2")

    if int(t2.subs(t, 1)) != 1 or int(t2.subs(t, -1)) != 1:
        fail("T2(±1) != 1")
    if int(t2.subs(t, 0)) != -1:
        fail("T2(0) != -1")

    g = gcd(t2p, t2p.diff(t))
    if g.degree() != 0:
        fail("T2' is not square-free")

    n_open = count_real_roots_open(t2p, Fraction(-1), Fraction(1))
    if n_open != 1:
        fail(f"T2' has {n_open} roots in (-1,1), expected 1")
    n_plus = count_real_roots_open(t2p, Fraction(0), Fraction(1))
    n_minus = count_real_roots_open(t2p, Fraction(-1), Fraction(0))
    if n_plus != 0 or n_minus != 0:
        fail(f"T2' has a critical point in an open branch: +{n_plus} -{n_minus}")

    samples = {
        "T2(1)": evaluate_univariate(t2, Fraction(1)),
        "T2(-1)": evaluate_univariate(t2, Fraction(-1)),
        "T2(0)": evaluate_univariate(t2, Fraction(0)),
        "T2(1/2)": evaluate_univariate(t2, Fraction(1, 2)),
        "T2(-1/2)": evaluate_univariate(t2, Fraction(-1, 2)),
        "T2'(0)": evaluate_univariate(t2p, Fraction(0)),
        "T2'(1/2)": evaluate_univariate(t2p, Fraction(1, 2)),
        "T2'(-1/2)": evaluate_univariate(t2p, Fraction(-1, 2)),
        "T2'(1)": evaluate_univariate(t2p, Fraction(1)),
        "T2'(-1)": evaluate_univariate(t2p, Fraction(-1)),
    }
    expected = {
        "T2(1)": Fraction(1),
        "T2(-1)": Fraction(1),
        "T2(0)": Fraction(-1),
        "T2(1/2)": Fraction(-1, 2),
        "T2(-1/2)": Fraction(-1, 2),
        "T2'(0)": Fraction(0),
        "T2'(1/2)": Fraction(2),
        "T2'(-1/2)": Fraction(-2),
        "T2'(1)": Fraction(4),
        "T2'(-1)": Fraction(-4),
    }
    for key, val in expected.items():
        if samples[key] != val:
            fail(f"{key} = {samples[key]} != {val}")

    return {
        "T2": "2*t**2 - 1",
        "T2_prime": "4*t",
        "T2_coeffs": named[2],
        "T2_prime_coeffs": [0, 4],
        "pell_m2": True,
        "square_free": True,
        "Sturm_(-1,1)": n_open,
        "Sturm_I1": n_plus,
        "Sturm_I2": n_minus,
        "evaluations": {k: [v.numerator, v.denominator] for k, v in samples.items()},
        "critical_point_is_branch_wall": True,
    }


def check_degree_formula() -> dict[str, Any]:
    rows = []
    for n in (1, 2, 3):
        tm = chebyshev_T(2)
        Yu, Yv, _, _, _, _ = pullback(x**n, Integer(0), tm)
        deg = max(total_degree_bivariate(Yu), total_degree_bivariate(Yv))
        expected = n * 2 + (2 - 1)
        if deg != expected:
            fail(f"deg Y for (x^{n},0), m=2: {deg} != {expected}")
        rows.append(
            {
                "n": n,
                "m": 2,
                "X": f"(x^{n}, 0)",
                "deg_Y": deg,
                "nm_plus_m_minus_1": expected,
            }
        )
    return {"lemma5_samples": rows}


def check_polar(rho2: Fraction) -> dict[str, Any]:
    P, Q = section6_field(rho2)
    radial = cancel(x * P + y * Q + (x**2 + y**2) * (x**2 + y**2 - rho2))
    angular = cancel(x * Q - y * P + (x**2 + y**2))
    if radial != 0 or angular != 0:
        fail("polar identities failed")
    fprime_at_rho = -2 * rho2
    if fprime_at_rho == 0:
        fail("hyperbolicity f'(rho)=0")
    return {
        "rho2": [rho2.numerator, rho2.denominator],
        "xP_plus_yQ": "-(x^2+y^2)((x^2+y^2)-rho2)",
        "xQ_minus_yP": "-(x^2+y^2)",
        "rdot": "r(rho2-r^2)",
        "thetadot": -1,
        "fprime_at_rho": [fprime_at_rho.numerator, fprime_at_rho.denominator],
        "hyperbolic": True,
    }


def check_field() -> dict[str, Any]:
    rho2 = Fraction(1, 4)
    P, Q = section6_field(rho2)
    tm = chebyshev_T(2)
    Yu, Yv, T_u, T_v, Tp_u, Tp_v = pullback(P, Q, tm)
    lam = Tp_u * Tp_v
    dphi_y_u = cancel(Tp_u * Yu - lam * P.subs({x: T_u, y: T_v}))
    dphi_y_v = cancel(Tp_v * Yv - lam * Q.subs({x: T_u, y: T_v}))
    if dphi_y_u != 0 or dphi_y_v != 0:
        fail("conjugacy DΦ·Y = λ X∘Φ failed")

    deg_P = int(Poly(P, x, y, domain=QQ).total_degree())
    deg_Q = int(Poly(Q, x, y, domain=QQ).total_degree())
    deg_X = max(deg_P, deg_Q)
    deg_Yu = total_degree_bivariate(Yu)
    deg_Yv = total_degree_bivariate(Yv)
    deg_Y = max(deg_Yu, deg_Yv)
    if deg_X != 3:
        fail(f"deg X = {deg_X}, expected 3")
    if deg_Y != 7 or deg_Yu != 7 or deg_Yv != 7:
        fail(f"deg Y = {deg_Y} ({deg_Yu},{deg_Yv}), expected 7")

    mons_u = monomials_qq(Yu)
    mons_v = monomials_qq(Yv)
    if len(mons_u) != 8 or len(mons_v) != 8:
        fail(f"term counts Yu={len(mons_u)} Yv={len(mons_v)}")

    expect_u = [
        (0, 1, 3, 1),
        (0, 3, -8, 1),
        (2, 1, -30, 1),
        (0, 5, 16, 1),
        (2, 3, 32, 1),
        (4, 1, 48, 1),
        (2, 5, -32, 1),
        (6, 1, -32, 1),
    ]
    expect_v = [
        (1, 0, 11, 1),
        (1, 2, -30, 1),
        (3, 0, -24, 1),
        (1, 4, 48, 1),
        (3, 2, 32, 1),
        (5, 0, 16, 1),
        (1, 6, -32, 1),
        (5, 2, -32, 1),
    ]
    got_u = [(m["u"], m["v"], m["num"], m["den"]) for m in mons_u]
    got_v = [(m["u"], m["v"], m["num"], m["den"]) for m in mons_v]
    if got_u != expect_u:
        fail(f"Yu monomials {got_u}")
    if got_v != expect_v:
        fail(f"Yv monomials {got_v}")

    lead_u = sum(
        coeff * u**i * v**j
        for (i, j), coeff in Poly(Yu, u, v, domain=QQ).as_dict().items()
        if i + j == 7
    )
    lead_v = sum(
        coeff * u**i * v**j
        for (i, j), coeff in Poly(Yv, u, v, domain=QQ).as_dict().items()
        if i + j == 7
    )
    if cancel(lead_u + 32 * u**2 * v * (u**4 + v**4)) != 0:
        fail("Yu leading form")
    if cancel(lead_v + 32 * u * v**2 * (u**4 + v**4)) != 0:
        fail("Yv leading form")

    P4 = cancel(4 * P)
    Q4 = cancel(4 * Q)
    Poly(P4, x, y, domain=ZZ)
    Poly(Q4, x, y, domain=ZZ)
    Yu4, Yv4, _, _, _, _ = pullback(P4, Q4, tm)
    deg_Y4 = max(total_degree_bivariate(Yu4), total_degree_bivariate(Yv4))
    if deg_Y4 != 7:
        fail(f"integer 4X pullback degree {deg_Y4} != 7")

    return {
        "paper": "arXiv:2604.12883v1 §6, m=2",
        "rho2": [1, 4],
        "T2": "2*t**2 - 1",
        "T2_prime": "4*t",
        "X": {"P": str(P), "Q": str(Q), "deg": deg_X},
        "Y": {
            "u_dot": "T2'(v) * P(T2(u), T2(v))",
            "v_dot": "T2'(u) * Q(T2(u), T2(v))",
            "deg_u": deg_Yu,
            "deg_v": deg_Yv,
            "deg": deg_Y,
            "n_terms_u": len(mons_u),
            "n_terms_v": len(mons_v),
            "monomials_u": mons_u,
            "monomials_v": mons_v,
            "leading_u": "-32 u^2 v (u^4 + v^4)",
            "leading_v": "-32 u v^2 (u^4 + v^4)",
        },
        "integer_time_rescale_4X": {
            "P": str(P4),
            "Q": str(Q4),
            "deg_Y": deg_Y4,
        },
        "conjugacy": True,
        "expected_deg": 3 * 2 + (2 - 1),
        "H7_from_this_field": 4,
        "beats_PT_74": False,
        "same_4_sheets_as_CL_at_N7": True,
        "beats_CL": False,
        "CL_beats_this": False,
    }


def check_four_rectangles() -> dict[str, Any]:
    """Exact algebra for ρ²=1/4: four compact ovals, one per branch rectangle.

    T2' = 4t vanishes only at t=0. On each I_k the restriction
    T2 → (−1,1) is a diffeomorphism, so Φ is a diffeomorphism of
    I_i × I_j onto (−1,1)². The circle x²+y²=1/4 sits in
    [−1/2,1/2]² ⋐ (−1,1)². Its preimage in each open rectangle is
    one compact simple closed curve, strictly inside the rectangle
    because |T2|=1 on the closed endpoints and 1 > 1/2.
    """
    rho2 = Fraction(1, 4)
    tm = chebyshev_T(2)
    tmp = tm.diff(t)
    if cancel(tmp.as_expr() - 4 * t) != 0:
        fail("T2' formula")

    intervals = [
        {"name": "I1", "left": Fraction(0), "right": Fraction(1), "Tprime_sign": 1},
        {"name": "I2", "left": Fraction(-1), "right": Fraction(0), "Tprime_sign": -1},
    ]

    interval_certs = []
    for spec in intervals:
        left, right = spec["left"], spec["right"]
        mid = (left + right) / 2
        tp_mid = evaluate_univariate(tmp, mid)
        if tp_mid == 0:
            fail(f"T2' vanishes in {spec['name']}")
        sign = 1 if tp_mid > 0 else -1
        if sign != spec["Tprime_sign"]:
            fail(f"T2' sign on {spec['name']}")
        n_crit = count_real_roots_open(tmp, left, right)
        if n_crit != 0:
            fail(f"T2' has {n_crit} roots in {spec['name']}")
        T_left = evaluate_univariate(tm, left)
        T_right = evaluate_univariate(tm, right)
        if abs(T_left) != 1 or abs(T_right) != 1:
            fail(f"|T2| != 1 at endpoints of {spec['name']}")
        if T_left == T_right:
            fail(f"T2 not opposite at endpoints of {spec['name']}")
        t_minus = T_left + Fraction(1, 2), T_right + Fraction(1, 2)
        t_plus = T_left - Fraction(1, 2), T_right - Fraction(1, 2)
        if t_minus[0] * t_minus[1] >= 0 or t_plus[0] * t_plus[1] >= 0:
            fail(f"T2±1/2 do not change sign on {spec['name']}")
        strictly_inside = abs(T_left) > Fraction(1, 2) and abs(T_right) > Fraction(1, 2)
        if not strictly_inside:
            fail(f"[-1/2,1/2] not compactly inside T2({spec['name']})")
        interval_certs.append(
            {
                "name": spec["name"],
                "left": [left.numerator, left.denominator],
                "right": [right.numerator, right.denominator],
                "T2_left": [T_left.numerator, T_left.denominator],
                "T2_right": [T_right.numerator, T_right.denominator],
                "T2_prime_sign": sign,
                "T2_prime_roots_in_open": 0,
                "T2_pm_half_sign_changes": True,
                "preimage_of_[-1/2,1/2]_strictly_inside": True,
                "diffeo_onto_(-1,1)": True,
            }
        )

    F = tm.as_expr().subs(t, u) ** 2 + tm.as_expr().subs(t, v) ** 2 - rho2
    F4 = cancel(4 * F)
    F4_poly = Poly(F4, u, v, domain=ZZ)
    expect_F4 = 16 * u**4 - 16 * u**2 + 16 * v**4 - 16 * v**2 + 7
    if cancel(F4 - expect_F4) != 0:
        fail(f"cleared level curve {F4}")
    if int(F4_poly.total_degree()) != 4:
        fail(f"level curve degree {F4_poly.total_degree()} != 4")
    n_factors = len(F4_poly.factor_list()[1])
    if n_factors != 1:
        fail(f"level curve Q-factors {n_factors}")

    rectangles = []
    for i, Iu in enumerate(interval_certs, start=1):
        for j, Iv in enumerate(interval_certs, start=1):
            rectangles.append(
                {
                    "i": i,
                    "j": j,
                    "Iu": Iu["name"],
                    "Iv": Iv["name"],
                    "Phi_diffeo_onto_(-1,1)^2": True,
                    "jacobian_det": "T2'(u) T2'(v) = 16 u v",
                    "jacobian_nonzero": True,
                    "circle_in_[-1/2,1/2]^2": True,
                    "circle_compactly_in_(-1,1)^2": True,
                    "one_compact_oval": True,
                    "oval_strictly_inside_open_rectangle": True,
                }
            )

    if len(rectangles) != 4:
        fail("expected 4 rectangles")

    return {
        "rho2": [1, 4],
        "T2_prime_factorization": str(factor(tmp.as_expr())),
        "intervals": interval_certs,
        "level_curve": {
            "equation": "T2(u)^2 + T2(v)^2 - 1/4 = 0",
            "cleared": "16u^4 - 16u^2 + 16v^4 - 16v^2 + 7",
            "total_degree": 4,
            "factor_over_Q": str(factor(F4)),
            "n_Q_factors": n_factors,
            "four_oval_factors_over_Q": False,
        },
        "rectangles": rectangles,
        "four_ovals": True,
        "proof": (
            "T2'=4t has no zero in either open I_k; T2(I_k)=(-1,1) by "
            "endpoint values ±1 and strict monotonicity; Φ is a product "
            "diffeomorphism on each I_i×I_j; the circle of radius 1/2 is "
            "compactly in (-1,1)^2; each preimage is therefore one compact "
            "oval strictly inside its rectangle. The degree-4 curve does not "
            "split into four factors over Q; the ovals are real components."
        ),
    }


def write_json(name: str, payload: dict[str, Any]) -> None:
    os.makedirs(CERTS, exist_ok=True)
    path = os.path.join(CERTS, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")


def canonical_core(
    cheb: dict[str, Any],
    degree: dict[str, Any],
    four: dict[str, Any],
) -> dict[str, Any]:
    return {
        "deg_Y": degree["Y"]["deg"],
        "deg_Yu": degree["Y"]["deg_u"],
        "deg_Yv": degree["Y"]["deg_v"],
        "deg_X": degree["X"]["deg"],
        "conjugacy": degree["conjugacy"],
        "H7_from_this_field": degree["H7_from_this_field"],
        "beats_PT_74": degree["beats_PT_74"],
        "four_ovals": four["four_ovals"],
        "n_terms_Yu": degree["Y"]["n_terms_u"],
        "n_terms_Yv": degree["Y"]["n_terms_v"],
        "T2_at_1": cheb["evaluations"]["T2(1)"],
        "T2_at_-1": cheb["evaluations"]["T2(-1)"],
        "T2_at_0": cheb["evaluations"]["T2(0)"],
        "Y_u_monomials": degree["Y"]["monomials_u"],
        "Y_v_monomials": degree["Y"]["monomials_v"],
        "same_4_sheets_as_CL_at_N7": True,
        "beats_CL": False,
        "CL_beats_this": False,
        "do_not_claim_252_1080_1380_2012": True,
        "T2_coeffs": cheb["T2_coeffs"],
    }


def dump_lines(
    cheb: dict[str, Any],
    deg_formula: dict[str, Any],
    polar: dict[str, Any],
    degree: dict[str, Any],
    four: dict[str, Any],
) -> list[str]:
    ev = cheb["evaluations"]
    tp0 = ev["T2'(0)"]
    tp_half = ev["T2'(1/2)"]
    tp_mhalf = ev["T2'(-1/2)"]
    lines = [
        "paper arXiv:2604.12883v1",
        "T2 2*t^2-1",
        "T2_prime 4*t",
        "T2_coeffs -1 0 2",
        "T2_prime_coeffs 0 4",
        "pell 1",
        "square_free_T2_prime 1",
        f"T2_at_1 {ev['T2(1)'][0]} {ev['T2(1)'][1]}",
        f"T2_at_-1 {ev['T2(-1)'][0]} {ev['T2(-1)'][1]}",
        f"T2_at_0 {ev['T2(0)'][0]} {ev['T2(0)'][1]}",
        f"T2_prime_at_0 {tp0[0]} {tp0[1]}",
        f"T2_prime_at_1/2 {tp_half[0]} {tp_half[1]}",
        f"T2_prime_at_-1/2 {tp_mhalf[0]} {tp_mhalf[1]}",
        f"Sturm_(-1,1) {cheb['Sturm_(-1,1)']}",
        f"Sturm_I1 {cheb['Sturm_I1']}",
        f"Sturm_I2 {cheb['Sturm_I2']}",
        "I1 (0,1) sign 1",
        "I2 (-1,0) sign -1",
        "T2_pm_half_sign_changes 1",
        "preimage_half_strictly_inside 1",
        "polar_radial 1",
        "polar_angular 1",
        f"fprime_rho {polar['fprime_at_rho'][0]} {polar['fprime_at_rho'][1]}",
        "hyperbolic 1",
        "conjugacy 1",
        f"deg_X {degree['X']['deg']}",
        f"deg_Y {degree['Y']['deg']}",
        f"deg_Yu {degree['Y']['deg_u']}",
        f"deg_Yv {degree['Y']['deg_v']}",
        f"expected_deg {degree['expected_deg']}",
        f"n_terms_Yu {degree['Y']['n_terms_u']}",
        f"n_terms_Yv {degree['Y']['n_terms_v']}",
    ]
    lines.extend(dump_monomials("Yu", degree["Y"]["monomials_u"]))
    lines.extend(dump_monomials("Yv", degree["Y"]["monomials_v"]))
    lines.append("leading_Yu -32 u^2 v (u^4+v^4)")
    lines.append("leading_Yv -32 u v^2 (u^4+v^4)")
    lines.append(f"integer_4X_deg {degree['integer_time_rescale_4X']['deg_Y']}")
    for row in deg_formula["lemma5_samples"]:
        lines.append(f"lemma5 n={row['n']} m=2 deg {row['deg_Y']}")
    lines.append(f"level_curve {four['level_curve']['cleared']}")
    lines.append(f"level_curve_deg {four['level_curve']['total_degree']}")
    lines.append("four_oval_factors_over_Q 0")
    for rec in four["rectangles"]:
        lines.append(f"rectangle {rec['i']} {rec['j']} {rec['Iu']} {rec['Iv']}")
    lines.append("four_ovals 1")
    lines.append(f"H7_from_this_field {degree['H7_from_this_field']}")
    lines.append("beats_PT_74 0")
    lines.append("same_4_sheets_as_CL_at_N7 1")
    lines.append("beats_CL 0")
    lines.append("CL_beats_this 0")
    lines.append("do_not_claim_252_1080_1380_2012 1")
    lines.append("hn_moved 0")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", type=str, default=None)
    args = ap.parse_args()

    cheb = check_chebyshev()
    deg_formula = check_degree_formula()
    polar = check_polar(Fraction(1, 4))
    degree = check_field()
    four = check_four_rectangles()
    core = canonical_core(cheb, degree, four)

    write_json("chebyshev.json", cheb)
    write_json("degree_formula.json", deg_formula)
    write_json("polar.json", polar)
    write_json("section6_degree.json", degree)
    write_json("four_rectangles.json", four)
    write_json("core.json", core)

    lines = dump_lines(cheb, deg_formula, polar, degree, four)
    text = "\n".join(lines) + "\n"
    if args.dump:
        with open(args.dump, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text, end="")
    print("verify.py: ok")
    print(f"  deg Y = {degree['Y']['deg']} (expected 7)")
    print(f"  Yu terms = {degree['Y']['n_terms_u']}, Yv terms = {degree['Y']['n_terms_v']}")
    print(f"  four ovals = {four['four_ovals']}")
    print(f"  beats PT 74 = {degree['beats_PT_74']}")


if __name__ == "__main__":
    main()
