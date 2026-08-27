#!/usr/bin/env python3
"""Replay Eshkobilov–Kadyrov–Mamayusupov arXiv:2604.12883v1.

Independent check of the Chebyshev pullback
    H(n m + m - 1) >= m^2 H(n)   (m >= 2),
of Table 1 / Appendix A arithmetic on the published seeds those
authors quote, and of the Section 6 degree-11 field.

This is a replay, not a new H(n) bound. The four numbers
H(14)>=252, H(29)>=1080, H(31)>=1380, H(39)>=2012 are already
on that arXiv. The Section 6 field gives H(11)>=9, which does
not beat Han–Li H(11)>=153.
"""

from __future__ import annotations

import json
import os
from fractions import Fraction
from typing import Any

from sympy import (
    Poly,
    QQ,
    ZZ,
    cancel,
    factor,
    gcd,
    symbols,
    together,
)

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, "certs")

# ---------------------------------------------------------------------------
# Published seeds. Cited, not reconstructed. Appendix A of 2604.12883v1
# quotes these as L_pub; we do not replay the Prohens–Torregrosa or
# Han–Li centres.
# ---------------------------------------------------------------------------

# Prohens–Torregrosa, Nonlinearity 32 (2019), Theorem 1.
PT_THM1: dict[int, int] = {
    4: 28,
    5: 37,
    6: 53,
    7: 74,
    8: 96,
    9: 120,
    10: 142,
}

# Han–Li, J. Differ. Equations 252 (2012), Theorem 1.2(i),
# as quoted by 2604.12883v1 Appendix A (not extracted from the paywall).
HAN_LI_APP_A: dict[int, int] = {
    11: 153,
    12: 157,
    14: 194,
    15: 345,
    16: 351,
    18: 372,
    19: 503,
    20: 509,
}

# Prohens–Torregrosa 2019, Corollary 2(a), the m=2 lifts they record.
PT_COR2: dict[int, int] = {
    13: 212,
    17: 384,
    21: 568,
    31: 1184,
    35: 1536,
    39: 1920,
    43: 2272,
}

# Appendix A seed list used to compute L_Ch.
SEEDS_APP_A: dict[int, int] = {}
SEEDS_APP_A.update(PT_THM1)
SEEDS_APP_A.update(HAN_LI_APP_A)
SEEDS_APP_A.update(PT_COR2)

# Table 1 L_pub column, including Han–Li rows that Appendix A does not
# list as seeds (used only to replay Δ, and as an optional extra-seed
# sensitivity check).
HAN_LI_TABLE1_ONLY: dict[int, int] = {
    23: 833,
    24: 843,
    25: 870,
    26: 880,
    27: 1023,
    29: 1060,
}

# Published small-n bounds, not used as Appendix A seeds.
SMALL_PUB: dict[int, int] = {1: 0, 2: 4, 3: 13}

# 2604.12883v1 Table 1 / Table 2, as printed.
PAPER_L_CH: dict[int, int] = {
    11: 148,
    13: 212,
    14: 252,
    15: 296,
    17: 384,
    19: 480,
    20: 477,
    21: 568,
    23: 666,
    24: 700,
    25: 628,
    26: 864,
    27: 848,
    29: 1080,
    31: 1380,
    35: 1536,
    39: 2012,
    43: 2272,
}

PAPER_TABLE1_L_PUB: dict[int, int] = {
    11: 153,
    13: 212,
    14: 194,
    15: 345,
    17: 384,
    19: 503,
    20: 509,
    21: 568,
    23: 833,
    24: 843,
    25: 870,
    26: 880,
    27: 1023,
    29: 1060,
    31: 1184,
    35: 1536,
    39: 1920,
    43: 2272,
}

PAPER_TABLE2_SEED: dict[int, tuple[int, int]] = {
    11: (5, 2),
    13: (6, 2),
    14: (4, 3),
    15: (7, 2),
    17: (8, 2),
    19: (9, 2),
    20: (6, 3),
    21: (10, 2),
    23: (7, 3),
    24: (4, 5),
    25: (12, 2),
    26: (8, 3),
    27: (13, 2),
    29: (9, 3),
    31: (15, 2),
    35: (17, 2),
    39: (19, 2),
    43: (21, 2),
}

PAPER_FOUR_NEW: dict[int, int] = {14: 252, 29: 1080, 31: 1380, 39: 2012}

u, v, t, x, y = symbols("u v t x y")


def fail(msg: str) -> None:
    raise SystemExit(f"verify.py FAIL: {msg}")


def chebyshev_T(m: int) -> Poly:
    """T_m in Z[t] by the integer recurrence T_0=1, T_1=t, T_{k}=2t T_{k-1}-T_{k-2}."""
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


def check_chebyshev_table() -> dict[str, Any]:
    """Named low-degree T_m and the Pell identity of Lemma 3."""
    named = {
        0: [1],
        1: [0, 1],
        2: [-1, 0, 2],
        3: [0, -3, 0, 4],
        4: [1, 0, -8, 0, 8],
        5: [0, 5, 0, -20, 0, 16],
    }
    for m, coeffs in named.items():
        got = poly_coeffs_asc(chebyshev_T(m))
        if got != coeffs:
            fail(f"T_{m} coeffs {got} != {coeffs}")

    t3 = chebyshev_T(3)
    if t3.as_expr() != 4 * t**3 - 3 * t:
        fail("T_3(t) != 4t^3-3t")
    t3p = t3.diff(t)
    if t3p.as_expr() != 12 * t**2 - 3:
        fail("T_3' != 12t^2-3")

    pell_ok: list[int] = []
    for m in range(1, 17):
        tm = chebyshev_T(m)
        tm_p = tm.diff(t)
        # m^2 T_m^2 + (1-t^2) (T_m')^2 - m^2 = 0
        ident = (m**2 * tm**2 + (1 - t**2) * tm_p**2 - m**2).as_expr()
        if cancel(ident) != 0:
            fail(f"Pell identity failed for m={m}")
        pell_ok.append(m)

    # Endpoint values used by the branch argument.
    endpoints = {}
    for m in range(1, 17):
        tm = chebyshev_T(m)
        endpoints[str(m)] = {
            "T_at_1": int(tm.subs(t, 1)),
            "T_at_-1": int(tm.subs(t, -1)),
            "expected_T_1": 1,
            "expected_T_-1": (-1) ** m,
        }
        if int(tm.subs(t, 1)) != 1 or int(tm.subs(t, -1)) != (-1) ** m:
            fail(f"T_{m}(±1) mismatch")

    # T_m' has exactly m-1 distinct real roots in (-1,1), by Sturm,
    # and they are simple (gcd(T_m', T_m'')=1). Combined with Pell,
    # T_m = ±1 at those roots, and consecutive critical values cannot
    # share a sign (else T_m ∓ 1 would force an extra critical point).
    sturm_counts: dict[str, int] = {}
    for m in range(2, 17):
        tm_p = chebyshev_T(m).diff(t)
        g = gcd(tm_p, tm_p.diff(t))
        if g.degree() != 0:
            fail(f"T_{m}' is not square-free")
        # Sturm on (-1,1): evaluate the Sturm chain just inside the
        # endpoints so we do not sit on T_m'(±1) when that vanishes.
        n_roots = count_real_roots_open(tm_p, Fraction(-1), Fraction(1))
        if n_roots != m - 1:
            fail(f"T_{m}' has {n_roots} roots in (-1,1), expected {m - 1}")
        sturm_counts[str(m)] = n_roots

    return {
        "named_T_m": {str(k): v for k, v in named.items()},
        "pell_identity_m": pell_ok,
        "T_pm_1": endpoints,
        "Tprime_roots_in_(-1,1)": sturm_counts,
        "lemma3_checked_m": list(range(2, 17)),
    }


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
    # Nudge off the endpoints if a Sturm polynomial vanishes there.
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
    Yu = together(Tp_v * P_phi)
    Yv = together(Tp_u * Q_phi)
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


def check_degree_formula() -> dict[str, Any]:
    """Lemma 5: deg Y = n m + (m-1) for X = (x^n, 0) and for a few mixed fields."""
    rows = []
    for n, m in (
        (1, 2),
        (2, 2),
        (3, 2),
        (3, 3),
        (4, 3),
        (5, 2),
        (1, 5),
        (6, 2),
        (2, 4),
    ):
        tm = chebyshev_T(m)
        Yu, Yv, _, _, _, _ = pullback(x**n, 0, tm)
        deg = max(total_degree_bivariate(Yu), total_degree_bivariate(Yv))
        expected = n * m + (m - 1)
        if deg != expected:
            fail(f"deg Y for (x^{n},0), m={m}: {deg} != {expected}")
        rows.append({"n": n, "m": m, "X": f"(x^{n}, 0)", "deg_Y": deg, "nm_plus_m_minus_1": expected})

    # Mixed top-degree: P = x^{n-1} y, Q = x^n. Still exact.
    for n, m in ((3, 3), (4, 2)):
        tm = chebyshev_T(m)
        Yu, Yv, _, _, _, _ = pullback(x ** (n - 1) * y, x**n, tm)
        deg = max(total_degree_bivariate(Yu), total_degree_bivariate(Yv))
        expected = n * m + (m - 1)
        if deg != expected:
            fail(f"mixed deg Y n={n} m={m}: {deg} != {expected}")
        rows.append(
            {
                "n": n,
                "m": m,
                "X": f"(x^{n-1} y, x^{n})",
                "deg_Y": deg,
                "nm_plus_m_minus_1": expected,
            }
        )
    return {"lemma5_samples": rows}


def section6_field(rho2: Fraction):
    P = y - x * (x**2 + y**2 - rho2)
    Q = -x - y * (x**2 + y**2 - rho2)
    return P, Q


def check_polar_identities(rho2: Fraction) -> dict[str, Any]:
    P, Q = section6_field(rho2)
    # x P + y Q = -(x^2+y^2) ((x^2+y^2) - rho2)
    radial = cancel(x * P + y * Q + (x**2 + y**2) * (x**2 + y**2 - rho2))
    # x Q - y P = -(x^2+y^2)
    angular = cancel(x * Q - y * P + (x**2 + y**2))
    if radial != 0 or angular != 0:
        fail("polar identities failed")
    # f(r) = r (rho2 - r^2), f'(rho) = -2 rho^2
    rho2_f = rho2
    fprime_at_rho = -2 * rho2_f
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


def check_conjugacy_and_section6() -> dict[str, Any]:
    rho2 = Fraction(1, 4)
    P, Q = section6_field(rho2)
    tm = chebyshev_T(3)
    Yu, Yv, T_u, T_v, Tp_u, Tp_v = pullback(P, Q, tm)
    lam = Tp_u * Tp_v
    # DΦ · Y = (T'(u) Yu, T'(v) Yv) should equal λ X(Φ)
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
    if deg_Y != 11:
        fail(f"deg Y = {deg_Y}, expected 11")

    # Also the integer-coefficient time-rescaled field 4X (same orbits).
    P4 = cancel(4 * P)
    Q4 = cancel(4 * Q)
    Poly(P4, x, y, domain=ZZ)
    Poly(Q4, x, y, domain=ZZ)
    Yu4, Yv4, _, _, _, _ = pullback(P4, Q4, tm)
    deg_Y4 = max(total_degree_bivariate(Yu4), total_degree_bivariate(Yv4))
    if deg_Y4 != 11:
        fail(f"integer 4X pullback degree {deg_Y4} != 11")

    return {
        "paper": "arXiv:2604.12883v1 §6",
        "rho2": [1, 4],
        "T3": "4*t**3 - 3*t",
        "T3_prime": "12*t**2 - 3",
        "X": {
            "P": str(P),
            "Q": str(Q),
            "deg": deg_X,
        },
        "Y": {
            "u_dot": "T3'(v) * P(T3(u), T3(v))",
            "v_dot": "T3'(u) * Q(T3(u), T3(v))",
            "deg_u": deg_Yu,
            "deg_v": deg_Yv,
            "deg": deg_Y,
            "monomials_u": monomials_qq(Yu),
            "monomials_v": monomials_qq(Yv),
        },
        "integer_time_rescale_4X": {
            "P": str(P4),
            "Q": str(Q4),
            "deg_Y": deg_Y4,
        },
        "conjugacy": True,
        "expected_deg": 3 * 3 + (3 - 1),
        "H11_from_this_field": 9,
        "beats_HanLi_153": False,
    }


def check_nine_rectangles() -> dict[str, Any]:
    """Exact algebra for ρ²=1/4: nine compact ovals, one per branch rectangle.

    Not a plot. T_3' = 3(2t-1)(2t+1) vanishes only at ±1/2. On each
    I_k the restriction T_3 → (-1,1) is a diffeomorphism, so
    Φ(u,v)=(T_3(u),T_3(v)) is a diffeomorphism of I_i×I_j onto (-1,1)².
    The circle x²+y²=1/4 sits in [-1/2,1/2]² ⋐ (-1,1)². Its preimage
    in each open rectangle is therefore a single compact simple closed
    curve, strictly inside the rectangle because |T_3|=1 on the closed
    endpoints and 1 > 1/2.
    """
    rho2 = Fraction(1, 4)
    tm = chebyshev_T(3)
    tmp = tm.diff(t)
    fact = factor(tmp.as_expr())
    if cancel(tmp.as_expr() - (12 * t**2 - 3)) != 0:
        fail("T3' formula")
    # 12t^2-3 = 3(2t-1)(2t+1)
    if cancel(tmp.as_expr() - 3 * (2 * t - 1) * (2 * t + 1)) != 0:
        fail("T3' factorization")

    samples = {
        "T3(1)": evaluate_univariate(tm, Fraction(1)),
        "T3(-1)": evaluate_univariate(tm, Fraction(-1)),
        "T3(1/2)": evaluate_univariate(tm, Fraction(1, 2)),
        "T3(-1/2)": evaluate_univariate(tm, Fraction(-1, 2)),
        "T3(0)": evaluate_univariate(tm, Fraction(0)),
        "T3'(1/2)": evaluate_univariate(tmp, Fraction(1, 2)),
        "T3'(-1/2)": evaluate_univariate(tmp, Fraction(-1, 2)),
        "T3'(0)": evaluate_univariate(tmp, Fraction(0)),
        "T3'(3/4)": evaluate_univariate(tmp, Fraction(3, 4)),
        "T3'(1/4)": evaluate_univariate(tmp, Fraction(1, 4)),
        "T3'(-3/4)": evaluate_univariate(tmp, Fraction(-3, 4)),
    }
    expected = {
        "T3(1)": Fraction(1),
        "T3(-1)": Fraction(-1),
        "T3(1/2)": Fraction(-1),
        "T3(-1/2)": Fraction(1),
        "T3(0)": Fraction(0),
        "T3'(1/2)": Fraction(0),
        "T3'(-1/2)": Fraction(0),
        "T3'(0)": Fraction(-3),
        "T3'(3/4)": Fraction(12 * (9 / 16) - 3).limit_denominator(),
        "T3'(1/4)": Fraction(12 * (1 / 16) - 3).limit_denominator(),
        "T3'(-3/4)": Fraction(12 * (9 / 16) - 3).limit_denominator(),
    }
    # Recompute the last three exactly.
    expected["T3'(3/4)"] = Fraction(12 * 9, 16) - 3
    expected["T3'(1/4)"] = Fraction(12, 16) - 3
    expected["T3'(-3/4)"] = Fraction(12 * 9, 16) - 3
    for key, val in expected.items():
        if samples[key] != val:
            fail(f"{key} = {samples[key]} != {val}")

    intervals = [
        {"name": "I1", "left": Fraction(1, 2), "right": Fraction(1), "Tprime_sign": 1},
        {"name": "I2", "left": Fraction(-1, 2), "right": Fraction(1, 2), "Tprime_sign": -1},
        {"name": "I3", "left": Fraction(-1), "right": Fraction(-1, 2), "Tprime_sign": 1},
    ]

    interval_certs = []
    for spec in intervals:
        left, right = spec["left"], spec["right"]
        mid = (left + right) / 2
        tp_mid = evaluate_univariate(tmp, mid)
        if tp_mid == 0:
            fail(f"T3' vanishes in {spec['name']}")
        sign = 1 if tp_mid > 0 else -1
        if sign != spec["Tprime_sign"]:
            fail(f"T3' sign on {spec['name']}")
        # No root of T3' in the open interval: the only real roots are ±1/2.
        n_crit = count_real_roots_open(tmp, left, right)
        if n_crit != 0:
            fail(f"T3' has {n_crit} roots in {spec['name']}")
        T_left = evaluate_univariate(tm, left)
        T_right = evaluate_univariate(tm, right)
        if abs(T_left) != 1 or abs(T_right) != 1:
            fail(f"|T3| != 1 at endpoints of {spec['name']}")
        if T_left == T_right:
            fail(f"T3 not opposite at endpoints of {spec['name']}")
        # T3 ± 1/2 each have exactly one root in the open interval:
        # T3 is strictly monotone from one of {±1} to the other, so it
        # crosses ±1/2 once each. Record endpoint signs.
        t_minus = T_left + Fraction(1, 2), T_right + Fraction(1, 2)  # T3+1/2
        t_plus = T_left - Fraction(1, 2), T_right - Fraction(1, 2)  # T3-1/2
        if t_minus[0] * t_minus[1] >= 0 or t_plus[0] * t_plus[1] >= 0:
            fail(f"T3±1/2 do not change sign on {spec['name']}")
        # Compact preimage of [-1/2,1/2] sits strictly inside I_k
        # because |T3(endpoint)|=1 > 1/2.
        strictly_inside = abs(T_left) > Fraction(1, 2) and abs(T_right) > Fraction(1, 2)
        if not strictly_inside:
            fail(f"[-1/2,1/2] not compactly inside T3({spec['name']})")
        interval_certs.append(
            {
                "name": spec["name"],
                "left": [left.numerator, left.denominator],
                "right": [right.numerator, right.denominator],
                "T3_left": [T_left.numerator, T_left.denominator],
                "T3_right": [T_right.numerator, T_right.denominator],
                "T3_prime_sign": sign,
                "T3_prime_roots_in_open": 0,
                "T3_pm_half_sign_changes": True,
                "preimage_of_[-1/2,1/2]_strictly_inside": True,
                "diffeo_onto_(-1,1)": True,
            }
        )

    # The algebraic curve T3(u)^2 + T3(v)^2 - 1/4. Over Q it is not a
    # product of nine oval factors (each oval is a real connected
    # component, not a Q-factor). Record the factorization.
    F = tm.as_expr().subs(t, u) ** 2 + tm.as_expr().subs(t, v) ** 2 - rho2
    F4 = cancel(4 * F)  # 4 T3(u)^2 + 4 T3(v)^2 - 1 ∈ Z[u,v]
    F4_poly = Poly(F4, u, v, domain=ZZ)
    F_factored = factor(F4)
    # Irreducible over Q, or a small factorisation that is not 9 ovals.
    n_factors = len(Poly(F4, u, v, domain=ZZ).factor_list()[1])
    # Resultant in v of F4 and F4_v: used only as a sanity that the
    # curve is genuinely degree 6, not a union of lower-degree lines.
    if int(F4_poly.total_degree()) != 6:
        fail(f"level curve degree {F4_poly.total_degree()} != 6")

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
                    "jacobian_det": "T3'(u) T3'(v)",
                    "jacobian_nonzero": True,
                    "circle_in_[-1/2,1/2]^2": True,
                    "circle_compactly_in_(-1,1)^2": True,
                    "one_compact_oval": True,
                    "oval_strictly_inside_open_rectangle": True,
                }
            )

    if len(rectangles) != 9:
        fail("expected 9 rectangles")

    return {
        "rho2": [1, 4],
        "T3_prime_factorization": str(fact),
        "T3_prime_equals_3_(2t-1)(2t+1)": True,
        "evaluations": {k: [v.numerator, v.denominator] for k, v in samples.items()},
        "intervals": interval_certs,
        "level_curve": {
            "equation": "T3(u)^2 + T3(v)^2 - 1/4 = 0",
            "cleared": "4 T3(u)^2 + 4 T3(v)^2 - 1",
            "total_degree": 6,
            "factor_over_Q": str(F_factored),
            "n_Q_factors": n_factors,
            "nine_oval_factors_over_Q": False,
        },
        "rectangles": rectangles,
        "nine_ovals": True,
        "proof": (
            "T3'=3(2t-1)(2t+1) has no zero in any open I_k; T3(I_k)=(-1,1) "
            "by endpoint values ±1 and strict monotonicity; Φ is a product "
            "diffeomorphism on each I_i×I_j; the circle of radius 1/2 is "
            "compactly in (-1,1)^2; each preimage is therefore one compact "
            "oval strictly inside its rectangle. The degree-6 curve does not "
            "split into nine factors over Q; the ovals are real components."
        ),
    }


def enumerate_lifts(seeds: dict[int, int], n_max: int = 50) -> dict[int, dict[str, Any]]:
    """All factorisations N+1 = m(n+1), m>=2, n>=1, N<=n_max, with L_pub(n)."""
    out: dict[int, dict[str, Any]] = {}
    for N in range(1, n_max + 1):
        Np = N + 1
        lifts = []
        for m in range(2, Np + 1):
            if Np % m != 0:
                continue
            nplus = Np // m
            n = nplus - 1
            if n < 1:
                continue
            if n not in seeds:
                lifts.append(
                    {
                        "n": n,
                        "m": m,
                        "seed_known": False,
                        "lift": None,
                    }
                )
                continue
            lift = m * m * seeds[n]
            lifts.append(
                {
                    "n": n,
                    "m": m,
                    "seed_known": True,
                    "L_pub_n": seeds[n],
                    "lift": lift,
                }
            )
        known = [row for row in lifts if row["seed_known"]]
        if not known:
            out[N] = {"N": N, "factorizations": lifts, "L_Ch": None, "argmax": None}
            continue
        best = max(known, key=lambda r: (r["lift"], r["m"], r["n"]))
        # Deterministic argmax: largest lift, then paper-style (n,m).
        # If several achieve the max, list them all.
        max_lift = max(r["lift"] for r in known)
        argmax = [r for r in known if r["lift"] == max_lift]
        out[N] = {
            "N": N,
            "factorizations": lifts,
            "L_Ch": max_lift,
            "argmax": argmax,
        }
    return out


def check_table() -> dict[str, Any]:
    enum = enumerate_lifts(SEEDS_APP_A, 50)
    mismatches = []
    for N, paper_val in PAPER_L_CH.items():
        got = enum[N]["L_Ch"]
        if got != paper_val:
            mismatches.append({"N": N, "paper_L_Ch": paper_val, "ours": got})
    if mismatches:
        fail(f"L_Ch mismatch vs paper Table 1: {mismatches}")

    # The printed Table 2 seed must be a maximizer (not necessarily unique).
    table2_ok = True
    table2_rows = []
    for N, (n, m) in PAPER_TABLE2_SEED.items():
        lifts = [r for r in enum[N]["factorizations"] if r.get("n") == n and r.get("m") == m]
        if not lifts or not lifts[0].get("seed_known"):
            fail(f"Table 2 seed (n,m)=({n},{m}) missing for N={N}")
        lift = lifts[0]["lift"]
        if lift != PAPER_L_CH[N] or lift != enum[N]["L_Ch"]:
            table2_ok = False
            fail(f"Table 2 N={N} seed does not achieve L_Ch")
        table2_rows.append(
            {
                "N": N,
                "n": n,
                "m": m,
                "L_pub_n": SEEDS_APP_A[n],
                "lift": lift,
                "matches_paper": True,
            }
        )

    four = {}
    beats = []
    for N, paper_val in PAPER_FOUR_NEW.items():
        got = enum[N]["L_Ch"]
        four[str(N)] = {
            "paper": paper_val,
            "ours": got,
            "argmax": enum[N]["argmax"],
            "all_known_lifts": [r for r in enum[N]["factorizations"] if r["seed_known"]],
            "beats_paper": got > paper_val,
        }
        if got > paper_val:
            beats.append(N)

    # Replay Table 1 Δ.
    table1 = []
    for N in sorted(PAPER_L_CH):
        lpub = PAPER_TABLE1_L_PUB[N]
        lch = enum[N]["L_Ch"]
        delta = lch - lpub
        table1.append(
            {
                "N": N,
                "L_pub": lpub,
                "L_Ch": lch,
                "paper_L_Ch": PAPER_L_CH[N],
                "seed_nm": {"n": PAPER_TABLE2_SEED[N][0], "m": PAPER_TABLE2_SEED[N][1]},
                "delta": delta,
                "paper_delta": PAPER_L_CH[N] - lpub,
                "match": lch == PAPER_L_CH[N],
            }
        )

    # Extra N<=50 with a defined L_Ch that Table 1 does not print.
    extra = []
    for N, row in enum.items():
        if row["L_Ch"] is None or N in PAPER_L_CH:
            continue
        extra.append(
            {
                "N": N,
                "L_Ch": row["L_Ch"],
                "argmax": row["argmax"],
                "note": (
                    "one-step lift from Appendix A seeds; not in Table 1; "
                    "not claimed as a new H(N) (no published L_pub replayed here)"
                ),
            }
        )

    # Sensitivity: add H(2)>=4, H(3)>=13, and Table 1-only Han–Li rows.
    extra_seeds = dict(SEEDS_APP_A)
    extra_seeds.update(SMALL_PUB)
    extra_seeds.update(HAN_LI_TABLE1_ONLY)
    enum_extra = enumerate_lifts(extra_seeds, 50)
    four_with_extra = {}
    extra_beats = []
    for N, paper_val in PAPER_FOUR_NEW.items():
        got = enum_extra[N]["L_Ch"]
        four_with_extra[str(N)] = {
            "paper": paper_val,
            "ours": got,
            "argmax": enum_extra[N]["argmax"],
            "beats_paper": got > paper_val,
        }
        if got > paper_val:
            extra_beats.append(N)

    # Confirm the paper's remark: strongest degree-11 lift is 4*H(5)=148,
    # not 9*H(3)=117, and both sit below Han–Li 153.
    lifts_11 = [r for r in enum_extra[11]["factorizations"] if r["seed_known"]]
    if enum[11]["L_Ch"] != 148:
        fail("L_Ch(11) != 148")
    h3_lift = [r for r in lifts_11 if r["n"] == 3 and r["m"] == 3]
    if h3_lift and h3_lift[0]["lift"] != 117:
        fail("9*H(3) sanity")

    return {
        "paper": "arXiv:2604.12883v1 Table 1 / Appendix A",
        "seeds_appendix_A": {str(k): v for k, v in sorted(SEEDS_APP_A.items())},
        "seed_citations": {
            "Prohens–Torregrosa 2019 Thm 1": PT_THM1,
            "Han–Li 2012 Thm 1.2(i) as quoted in 2604.12883v1 App A": HAN_LI_APP_A,
            "Prohens–Torregrosa 2019 Cor 2(a)": {str(k): v for k, v in PT_COR2.items()},
        },
        "N_max": 50,
        "table1": table1,
        "table2": table2_rows,
        "L_Ch": {str(N): enum[N]["L_Ch"] for N in sorted(PAPER_L_CH)},
        "all_N_le_50_with_L_Ch": {
            str(N): enum[N]["L_Ch"]
            for N in sorted(enum)
            if enum[N]["L_Ch"] is not None
        },
        "factorizations_of_four": four,
        "missed_factorization_beats_252_1080_1380_2012": False,
        "beats_four": beats,
        "table2_seeds_are_maximizers": table2_ok,
        "table1_L_Ch_match": True,
        "extra_N_le_50_not_in_table1": extra,
        "sensitivity_with_H2_H3_and_table1_HanLi": {
            "four": four_with_extra,
            "beats_four": extra_beats,
            "L_Ch_11_includes_9_H3": 117 if h3_lift else None,
            "L_Ch_11_best": enum_extra[11]["L_Ch"],
        },
        "H11_section6_field": 9,
        "H11_best_one_step": 148,
        "H11_HanLi": 153,
        "do_not_claim_H14_ge_252_as_ours": True,
    }


def write_json(name: str, payload: dict[str, Any]) -> str:
    os.makedirs(CERTS, exist_ok=True)
    path = os.path.join(CERTS, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")
    return path


def canonical_core(table: dict[str, Any], degree: dict[str, Any], nine: dict[str, Any]) -> dict[str, Any]:
    """Numeric core that the Rust verifier must match exactly."""
    return {
        "deg_Y": degree["Y"]["deg"],
        "deg_Yu": degree["Y"]["deg_u"],
        "deg_Yv": degree["Y"]["deg_v"],
        "deg_X": degree["X"]["deg"],
        "conjugacy": degree["conjugacy"],
        "H11_from_this_field": degree["H11_from_this_field"],
        "beats_HanLi_153": degree["beats_HanLi_153"],
        "nine_ovals": nine["nine_ovals"],
        "T3_at_1": nine["evaluations"]["T3(1)"],
        "T3_at_-1": nine["evaluations"]["T3(-1)"],
        "T3_at_1/2": nine["evaluations"]["T3(1/2)"],
        "T3_at_-1/2": nine["evaluations"]["T3(-1/2)"],
        "L_Ch": table["L_Ch"],
        "beats_four": table["beats_four"],
        "table1_L_Ch_match": table["table1_L_Ch_match"],
        "four": {k: PAPER_FOUR_NEW[int(k)] for k in PAPER_FOUR_NEW},
        "Y_u_monomials": degree["Y"]["monomials_u"],
        "Y_v_monomials": degree["Y"]["monomials_v"],
        "T_m": {str(m): poly_coeffs_asc(chebyshev_T(m)) for m in range(0, 9)},
    }


def main() -> None:
    cheb = check_chebyshev_table()
    deg_formula = check_degree_formula()
    polar = check_polar_identities(Fraction(1, 4))
    degree = check_conjugacy_and_section6()
    nine = check_nine_rectangles()
    table = check_table()
    core = canonical_core(table, degree, nine)

    write_json("chebyshev.json", cheb)
    write_json("degree_formula.json", deg_formula)
    write_json("polar.json", polar)
    write_json("section6_degree.json", degree)
    write_json("nine_rectangles.json", nine)
    write_json("table_replay.json", table)
    write_json("core.json", core)

    print("verify.py: ok")
    print(f"  deg Y = {degree['Y']['deg']} (expected 11)")
    print(f"  nine ovals = {nine['nine_ovals']}")
    print(f"  Table 1 L_Ch match = {table['table1_L_Ch_match']}")
    print(f"  beats 252/1080/1380/2012 = {table['beats_four']}")
    print(f"  extra N<=50 with L_Ch not in Table 1: {len(table['extra_N_le_50_not_in_table1'])}")


if __name__ == "__main__":
    main()
