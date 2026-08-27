#!/usr/bin/env python3
"""Cubic-jet L1 and Poincaré V2 of the two-well van der Pol field.

Imagined: L2 = 0 while L1 ≠ 0, or else L2 supplies extra small
cycles and H(3) >= 14. Not produced. Order is 1: L1 = sqrt(2) mu
already uses the budget at each well. Kept: L1 replay, the cubic
correction L1 = L1_E + 3 a30 + a12 + b21 + 3 b03, V2 of this
3-jet in the q1 Poincaré gauge, and the mu = 0 centers.

A second, independent check is verify.rs (sparse jets plus
Gaussian elimination over Q(sqrt(2)) at integer mu).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
CORE_PATH = CERTS / "core.json"
JETS_PATH = CERTS / "jets.json"

X, Y, MU = sp.symbols("x y mu")
U, V, S = sp.symbols("u v s")
A20, A11, A02, B20, B11, B02 = sp.symbols("a20 a11 a02 b20 b11 b02")
A30, A21, A12, A03 = sp.symbols("a30 a21 a12 a03")
B30, B21, B12, B03 = sp.symbols("b30 b21 b12 b03")

L1_E = (A20 + A02) * A11 - (B20 + B02) * B11 - 2 * A20 * B20 + 2 * A02 * B02
L1_CUBIC = 3 * A30 + A12 + B21 + 3 * B03
L1_FULL = L1_E + L1_CUBIC

QUAD_NAMES = ("a20", "a11", "a02", "b20", "b11", "b02")
CUBIC_NAMES = ("a30", "a21", "a12", "a03", "b30", "b21", "b12", "b03")
JET_KEYS = (
    "a20",
    "a11",
    "a02",
    "a30",
    "a21",
    "a12",
    "a03",
    "b20",
    "b11",
    "b02",
    "b30",
    "b21",
    "b12",
    "b03",
)

V2_CLOSED = -S * MU * (23 * MU**2 + 18) / 96
V1_CLOSED = S * MU / 8


def require_zero(expr, label: str) -> None:
    if sp.expand(expr) != 0:
        raise AssertionError(f"{label} is not zero: {sp.expand(expr)}")


def require_equal(left, right, label: str) -> None:
    if sp.expand(left - right) != 0:
        raise AssertionError(f"{label} mismatch: {sp.expand(left - right)}")


def reduce_s(expr) -> sp.Expr:
    expr = sp.expand(expr)
    dummy = sp.Dummy("sred")
    poly = sp.expand(expr).subs(S, dummy).as_poly(dummy)
    if poly is None:
        return expr
    acc = sp.Integer(0)
    for n, coeff in enumerate(reversed(poly.all_coeffs())):
        acc += coeff * (dummy ** (n % 2)) * (2 ** (n // 2))
    return sp.expand(acc.subs(dummy, S))


def fmt_rat(r) -> str:
    r = sp.Rational(r)
    if r.q == 1:
        return str(int(r.p))
    return f"{int(r.p)}/{int(r.q)}"


def fmt_k_sqrt2(k, extra: str = "") -> str:
    """Format k * sqrt(2) * extra with k rational, extra e.g. '' or '*mu'."""
    k = sp.Rational(k)
    if k == 0:
        return "0"
    sign = "-" if k < 0 else ""
    k = abs(k)
    if k.q == 1:
        if k.p == 1:
            body = f"sqrt(2){extra}"
        else:
            body = f"{int(k.p)}*sqrt(2){extra}"
    elif k.p == 1:
        body = f"sqrt(2){extra}/{int(k.q)}"
    else:
        body = f"{int(k.p)}*sqrt(2){extra}/{int(k.q)}"
    return sign + body


def fmt_s_mu(expr) -> str:
    """Canonical string for an element of Q(s)[mu] with s^2 = 2."""
    reduced = reduce_s(expr)
    if reduced == 0:
        return "0"
    dummy = sp.symbols("_s")
    poly_s = sp.Poly(sp.expand(reduced).subs(S, dummy), dummy, domain=sp.QQ[MU])
    c0 = poly_s.nth(0) if poly_s.degree() >= 0 else 0
    c1 = poly_s.nth(1) if poly_s.degree() >= 1 else 0
    if c0 != 0:
        raise AssertionError(f"unexpected rational-in-mu piece {c0} in {expr}")
    if c1 == 0:
        return "0"
    poly_mu = sp.Poly(sp.expand(c1), MU, domain=sp.QQ)
    deg = poly_mu.degree()
    if deg <= 0:
        return fmt_k_sqrt2(poly_mu.nth(0))
    if deg == 1 and poly_mu.nth(0) == 0:
        return fmt_k_sqrt2(poly_mu.nth(1), "*mu")
    if deg == 3 and poly_mu.nth(0) == 0 and poly_mu.nth(2) == 0:
        p_r = sp.Rational(poly_mu.nth(1))
        q_r = sp.Rational(poly_mu.nth(3))
        den = int(sp.ilcm(p_r.q, q_r.q))
        pn, qn = int(p_r * den), int(q_r * den)
        g = int(sp.gcd(sp.gcd(abs(pn), abs(qn)), den))
        pn //= g
        qn //= g
        den //= g
        if pn < 0 or (pn == 0 and qn < 0):
            sign = "-"
            pn, qn = -pn, -qn
        else:
            sign = ""
        if qn == 1:
            inner = f"mu^2+{pn}"
        elif qn == -1:
            inner = f"-mu^2+{pn}" if pn != 0 else "-mu^2"
        elif pn > 0:
            inner = f"{qn}*mu^2+{pn}"
        elif pn < 0:
            inner = f"{qn}*mu^2{pn}"
        else:
            inner = f"{qn}*mu^2"
        body = f"{sign}sqrt(2)*mu*({inner})"
        if den != 1:
            body = f"{body}/{den}"
        return body
    raise AssertionError(f"unhandled s-mu polynomial {c1}")


def lie(f, field, x, y):
    return sp.diff(f, x) * field[0] + sp.diff(f, y) * field[1]


def hom_poly(deg: int, name: str, x, y):
    coeffs = []
    expr = 0
    for i in range(deg + 1):
        c = sp.symbols(f"{name}_{i}{deg - i}")
        coeffs.append(c)
        expr += c * x**i * y ** (deg - i)
    return expr, coeffs


def derive_v1_general() -> sp.Expr:
    """Poincaré V1 for a general quadratic+cubic jet. Gauge: y^4 of F4 = 0."""
    x, y = sp.symbols("xx yy")
    p2 = A20 * x**2 + A11 * x * y + A02 * y**2
    q2 = B20 * x**2 + B11 * x * y + B02 * y**2
    p3 = A30 * x**3 + A21 * x**2 * y + A12 * x * y**2 + A03 * y**3
    q3 = B30 * x**3 + B21 * x**2 * y + B12 * x * y**2 + B03 * y**3
    x1 = (-y, x)
    x2 = (p2, q2)
    x3 = (p3, q3)
    f2 = (x**2 + y**2) / 2
    f3, c3 = hom_poly(3, "f3g", x, y)
    eq3 = sp.expand(lie(f3, x1, x, y) + lie(f2, x2, x, y))
    sys3 = [eq3.coeff(x, i).coeff(y, 3 - i) for i in range(4)]
    f3s = sp.expand(f3.subs(sp.solve(sys3, c3)))
    f4, c4 = hom_poly(4, "f4g", x, y)
    v1 = sp.symbols("V1g")
    eq4 = sp.expand(
        lie(f4, x1, x, y) + lie(f3s, x2, x, y) + lie(f2, x3, x, y) - v1 * (x**2 + y**2) ** 2
    )
    sys4 = [eq4.coeff(x, i).coeff(y, 4 - i) for i in range(5)] + [c4[0]]
    sol4 = sp.solve(sys4, c4 + [v1], dict=True)[0]
    return sp.factor(sol4[v1])


def derive_v1_v2(subs: dict) -> tuple[sp.Expr, sp.Expr]:
    """V1, V2 of a substituted 3-jet in the q1 gauge."""
    x, y = sp.symbols("xx yy")
    p2 = (A20 * x**2 + A11 * x * y + A02 * y**2).subs(subs)
    q2 = (B20 * x**2 + B11 * x * y + B02 * y**2).subs(subs)
    p3 = (A30 * x**3 + A21 * x**2 * y + A12 * x * y**2 + A03 * y**3).subs(subs)
    q3 = (B30 * x**3 + B21 * x**2 * y + B12 * x * y**2 + B03 * y**3).subs(subs)
    x1 = (-y, x)
    x2 = (sp.expand(p2), sp.expand(q2))
    x3 = (sp.expand(p3), sp.expand(q3))
    f2 = (x**2 + y**2) / 2

    f3, c3 = hom_poly(3, "f3", x, y)
    eq3 = sp.expand(lie(f3, x1, x, y) + lie(f2, x2, x, y))
    f3s = sp.expand(f3.subs(sp.solve([eq3.coeff(x, i).coeff(y, 3 - i) for i in range(4)], c3)))

    f4, c4 = hom_poly(4, "f4", x, y)
    v1 = sp.symbols("V1")
    eq4 = sp.expand(
        lie(f4, x1, x, y) + lie(f3s, x2, x, y) + lie(f2, x3, x, y) - v1 * (x**2 + y**2) ** 2
    )
    sol4 = sp.solve(
        [eq4.coeff(x, i).coeff(y, 4 - i) for i in range(5)] + [c4[0]],
        c4 + [v1],
        dict=True,
    )[0]
    f4s = sp.expand(f4.subs(sol4))
    v1s = sp.factor(sol4[v1])

    f5, c5 = hom_poly(5, "f5", x, y)
    eq5 = sp.expand(lie(f5, x1, x, y) + lie(f4s, x2, x, y) + lie(f3s, x3, x, y))
    f5s = sp.expand(f5.subs(sp.solve([eq5.coeff(x, i).coeff(y, 5 - i) for i in range(6)], c5)))

    f6, c6 = hom_poly(6, "f6", x, y)
    v2 = sp.symbols("V2")
    eq6 = sp.expand(
        lie(f6, x1, x, y) + lie(f5s, x2, x, y) + lie(f4s, x3, x, y) - v2 * (x**2 + y**2) ** 3
    )
    sol6 = sp.solve(
        [eq6.coeff(x, i).coeff(y, 6 - i) for i in range(7)] + [c6[0]],
        c6 + [v2],
        dict=True,
    )[0]
    v2s = sp.expand(sol6[v2])

    # Residual through degree 6.
    field = (x1[0] + x2[0] + x3[0], x1[1] + x2[1] + x3[1])
    ftot = f2 + f3s + f4s + f5s + f6.subs(sol6)
    residual = sp.expand(
        lie(ftot, field, x, y) - sol4[v1] * (x**2 + y**2) ** 2 - sol6[v2] * (x**2 + y**2) ** 3
    )
    poly = sp.Poly(residual, x, y, domain=sp.QQ[MU, S])
    for exp, coeff in poly.as_dict().items():
        if sum(exp) <= 6 and sp.expand(coeff) != 0:
            raise AssertionError(f"Poincaré residual degree {sum(exp)}: {coeff}")
    return v1s, v2s


def jet_plus() -> dict:
    return {
        A20: 0,
        A11: 0,
        A02: 0,
        B20: sp.Rational(3, 2),
        B11: -S * MU,
        B02: 0,
        A30: 0,
        A21: 0,
        A12: 0,
        A03: 0,
        B30: sp.Rational(1, 2),
        B21: -S * MU / 2,
        B12: 0,
        B03: 0,
    }


def jet_minus() -> dict:
    return {
        A20: 0,
        A11: 0,
        A02: 0,
        B20: -sp.Rational(3, 2),
        B11: S * MU,
        B02: 0,
        A30: 0,
        A21: 0,
        A12: 0,
        A03: 0,
        B30: sp.Rational(1, 2),
        B21: -S * MU / 2,
        B12: 0,
        B03: 0,
    }


def named_field() -> tuple[sp.Expr, sp.Expr]:
    p = Y
    q = X - X**3 + MU * (1 - X**2) * Y
    return sp.expand(p), sp.expand(q)


def check_equilibria() -> None:
    p, q = named_field()
    for xv in (0, 1, -1):
        require_zero(p.subs({X: xv, Y: 0}), f"P({xv},0)")
        require_zero(q.subs({X: xv, Y: 0}), f"Q({xv},0)")
    j00 = sp.Matrix([[sp.diff(p, X), sp.diff(p, Y)], [sp.diff(q, X), sp.diff(q, Y)]])
    for xv, expect_tr, expect_det in ((0, MU, -1), (1, 0, 2), (-1, 0, 2)):
        j = j00.subs({X: xv, Y: 0})
        require_equal(sp.expand(j[0, 0] + j[1, 1]), expect_tr, f"trace({xv},0)")
        require_equal(sp.expand(j.det()), expect_det, f"det({xv},0)")


def translate_q(sign: int) -> tuple[sp.Expr, sp.Expr]:
    """Q after x = sign + X, y = Y, and the claimed 3-jet."""
    xx, yy = sp.symbols("X Y")
    p, q = named_field()
    qt = sp.expand(q.subs({X: sign + xx, Y: yy}))
    if sign == 1:
        claimed = -2 * xx - 3 * xx**2 - xx**3 - 2 * MU * xx * yy - MU * xx**2 * yy
    else:
        claimed = -2 * xx + 3 * xx**2 - xx**3 + 2 * MU * xx * yy - MU * xx**2 * yy
    require_zero(qt - claimed, f"translate {sign}")
    return qt, claimed


def focal_from_q(q_xy: sp.Expr, xx, yy) -> sp.Expr:
    """Nonlinear dv/dτ after u=X, v=-Y/s, τ = s t, s^2=2. Q_nl = -N/2."""
    n = sp.expand(q_xy.subs({xx: U, yy: -S * V}) + 2 * U)
    return reduce_s(n)


def coeffs_from_n(n_poly: sp.Expr) -> dict[str, sp.Expr]:
    """Q_nl = -N/2 in (u,v)."""
    out = {name: sp.Integer(0) for name in JET_KEYS}
    poly = sp.Poly(sp.expand(n_poly), U, V, MU, S, domain=sp.ZZ)
    for exp, coeff in poly.as_dict().items():
        iu, iv, imu, is_ = (int(e) for e in exp)
        if imu not in (0, 1) or is_ not in (0, 1):
            raise AssertionError(f"unexpected N monomial {exp}")
        # Q coeff of u^iu v^iv mu^imu s^is = -coeff/2
        qcoeff = -sp.Integer(int(coeff)) / 2 * (MU**imu) * (S**is_)
        key = None
        if iu + iv == 2:
            key = { (2, 0): "b20", (1, 1): "b11", (0, 2): "b02" }.get((iu, iv))
        elif iu + iv == 3:
            key = { (3, 0): "b30", (2, 1): "b21", (1, 2): "b12", (0, 3): "b03" }.get((iu, iv))
        if key is None:
            raise AssertionError(f"N term not in 3-jet: {exp}")
        out[key] = sp.expand(out[key] + qcoeff)
    return {k: reduce_s(v) for k, v in out.items()}


def l1_e_of(c: dict[str, sp.Expr]) -> sp.Expr:
    return sp.expand(
        (c["a20"] + c["a02"]) * c["a11"]
        - (c["b20"] + c["b02"]) * c["b11"]
        - 2 * c["a20"] * c["b20"]
        + 2 * c["a02"] * c["b02"]
    )


def l1_cubic_of(c: dict[str, sp.Expr]) -> sp.Expr:
    return sp.expand(3 * c["a30"] + c["a12"] + c["b21"] + 3 * c["b03"])


def l1_full_of(c: dict[str, sp.Expr]) -> sp.Expr:
    return sp.expand(l1_e_of(c) + l1_cubic_of(c))


def extract_jets() -> tuple[dict[str, sp.Expr], dict[str, sp.Expr]]:
    xx, yy = sp.symbols("X Y")
    q_plus, _ = translate_q(1)
    q_minus, _ = translate_q(-1)
    n_plus = focal_from_q(q_plus, xx, yy)
    n_minus = focal_from_q(q_minus, xx, yy)
    # N(+1) = -3 u^2 - u^3 + 2 mu s u v + mu s u^2 v
    np = sp.Poly(sp.expand(n_plus), U, V, MU, S, domain=sp.ZZ)
    require_equal(int(np.coeff_monomial(U**2)), -3, "N+ u^2")
    require_equal(int(np.coeff_monomial(U**3)), -1, "N+ u^3")
    require_equal(int(np.coeff_monomial(U * V * MU * S)), 2, "N+ mu s u v")
    require_equal(int(np.coeff_monomial(U**2 * V * MU * S)), 1, "N+ mu s u^2 v")
    nm = sp.Poly(sp.expand(n_minus), U, V, MU, S, domain=sp.ZZ)
    require_equal(int(nm.coeff_monomial(U**2)), 3, "N- u^2")
    require_equal(int(nm.coeff_monomial(U**3)), -1, "N- u^3")
    require_equal(int(nm.coeff_monomial(U * V * MU * S)), -2, "N- mu s u v")
    require_equal(int(nm.coeff_monomial(U**2 * V * MU * S)), 1, "N- mu s u^2 v")
    jet_p = coeffs_from_n(n_plus)
    jet_m = coeffs_from_n(n_minus)
    require_equal(jet_p["b20"], sp.Rational(3, 2), "plus b20")
    require_equal(jet_p["b11"], -S * MU, "plus b11")
    require_equal(jet_p["b30"], sp.Rational(1, 2), "plus b30")
    require_equal(jet_p["b21"], -S * MU / 2, "plus b21")
    require_equal(jet_m["b20"], -sp.Rational(3, 2), "minus b20")
    require_equal(jet_m["b11"], S * MU, "minus b11")
    require_equal(jet_m["b30"], sp.Rational(1, 2), "minus b30")
    require_equal(jet_m["b21"], -S * MU / 2, "minus b21")
    for name in JET_KEYS:
        if name.startswith("a") or name in ("b02", "b12", "b03"):
            require_zero(jet_p[name], f"plus {name}")
            require_zero(jet_m[name], f"minus {name}")
    return jet_p, jet_m


def monomials(expr, names: tuple[str, ...]) -> list[dict]:
    symbols = [sp.symbols(n) for n in names]
    poly = sp.Poly(sp.expand(expr), *symbols, domain=sp.ZZ)
    out = []
    for monom, coeff in poly.terms():
        parts = []
        for name, power in zip(names, monom):
            if power == 1:
                parts.append(name)
            elif power > 1:
                parts.append(f"{name}**{power}")
        parts.sort()
        out.append({"term": "*".join(parts), "coeff": int(coeff)})
    out.sort(key=lambda r: r["term"])
    return out


def check_formula() -> None:
    v1 = derive_v1_general()
    require_equal(sp.expand(8 * v1 - L1_FULL), 0, "8 V1 = L1")
    focus = {
        A20: 1,
        A11: 0,
        A02: 0,
        B20: 1,
        B11: 0,
        B02: 0,
        A30: 0,
        A21: 0,
        A12: 0,
        A03: 0,
        B30: 0,
        B21: 0,
        B12: 0,
        B03: 0,
    }
    require_equal(L1_FULL.subs(focus), -2, "generic focus L1")
    # Hamiltonian ẋ = −∂H/∂y, ẏ = ∂H/∂x for H = r²/2 + x³ − 2 x² y + 3 x y² − y³.
    ham = {
        A20: 2,
        A11: -6,
        A02: 3,
        B20: 3,
        B11: -4,
        B02: 3,
        A30: 0,
        A21: 0,
        A12: 0,
        A03: 0,
        B30: 0,
        B21: 0,
        B12: 0,
        B03: 0,
    }
    require_zero(L1_FULL.subs(ham), "hamiltonian L1")


def check_l1(jet_p, jet_m) -> dict:
    pieces = {}
    for name, jet in (("plus", jet_p), ("minus", jet_m)):
        lq = reduce_s(l1_e_of(jet))
        lc = reduce_s(l1_cubic_of(jet))
        lf = reduce_s(l1_full_of(jet))
        require_equal(lq, 3 * S * MU / 2, f"L1_E {name}")
        require_equal(lc, -S * MU / 2, f"L1_cubic {name}")
        require_equal(lf, S * MU, f"L1 {name}")
        require_equal(lf.subs(MU, 0), 0, f"L1 {name} at mu=0")
        # L1_E alone is not L1.
        if sp.expand(lq - lf) == 0:
            raise AssertionError("L1_E unexpectedly equals L1")
        pieces[name] = {"L1_E": lq, "L1_cubic": lc, "L1_full": lf}
    return pieces


def check_v2() -> dict:
    v1p, v2p = derive_v1_v2(jet_plus())
    v1m, v2m = derive_v1_v2(jet_minus())
    require_equal(reduce_s(v1p), V1_CLOSED, "V1 plus")
    require_equal(reduce_s(v1m), V1_CLOSED, "V1 minus")
    require_equal(reduce_s(v2p), reduce_s(V2_CLOSED), "V2 plus")
    require_equal(reduce_s(v2m), reduce_s(V2_CLOSED), "V2 minus")
    require_zero(reduce_s(v1p).subs(MU, 0), "V1(0)")
    require_zero(reduce_s(v2p).subs(MU, 0), "V2(0)")
    # V2 is not the zero polynomial, and not a multiple of mu^2 only.
    if reduce_s(v2p) == 0:
        raise AssertionError("V2 unexpectedly zero")
    v2_mu = reduce_s(v2p)
    if v2_mu.subs(MU, 1) == 0:
        raise AssertionError("V2(1) unexpectedly zero")
    # Samples.
    s1 = reduce_s(v2p.subs(MU, 1))
    s2 = reduce_s(v2p.subs(MU, 2))
    sm = reduce_s(v2p.subs(MU, -1))
    require_equal(s1, -sp.Integer(41) * S / 96, "V2(1)")
    require_equal(s2, -sp.Integer(55) * S / 24, "V2(2)")
    require_equal(sm, sp.Integer(41) * S / 96, "V2(-1)")
    if fmt_s_mu(V2_CLOSED) != "-sqrt(2)*mu*(23*mu^2+18)/96":
        raise AssertionError(f"V2 string {fmt_s_mu(V2_CLOSED)}")
    if fmt_s_mu(V1_CLOSED) != "sqrt(2)*mu/8":
        raise AssertionError(f"V1 string {fmt_s_mu(V1_CLOSED)}")
    return {"V1": reduce_s(v1p), "V2": reduce_s(v2p)}


def check_mu0_hamiltonian() -> None:
    # Plus: ú = -v, v́ = u + (3/2) u^2 + (1/2) u^3
    # 4H+ = 4 v^2 + 4 u^2 + 4 u^3 + u^4
    h4p = 4 * V**2 + 4 * U**2 + 4 * U**3 + U**4
    pu, qv = -V, U + sp.Rational(3, 2) * U**2 + sp.Rational(1, 2) * U**3
    require_zero(sp.diff(h4p, U) * pu + sp.diff(h4p, V) * qv, "4H+ at mu=0")
    h4m = 4 * V**2 + 4 * U**2 - 4 * U**3 + U**4
    qvm = U - sp.Rational(3, 2) * U**2 + sp.Rational(1, 2) * U**3
    require_zero(sp.diff(h4m, U) * pu + sp.diff(h4m, V) * qvm, "4H- at mu=0")
    # A dropped u^4 is not a first integral.
    bad = 4 * V**2 + 4 * U**2 + 4 * U**3
    if sp.expand(sp.diff(bad, U) * pu + sp.diff(bad, V) * qv) == 0:
        raise AssertionError("dropped-u^4 energy unexpectedly conserved")


def jet_record(jet: dict[str, sp.Expr]) -> dict[str, str]:
    out = {}
    for name in JET_KEYS:
        val = reduce_s(jet[name])
        if name in ("b20", "b30"):
            out[name] = fmt_rat(val)
        elif name in ("b11", "b21"):
            out[name] = fmt_s_mu(val)
        else:
            if val != 0:
                raise AssertionError(f"{name} expected 0, got {val}")
            out[name] = "0"
    return out


def build_core(v1v2: dict) -> dict:
    return {
        "schema": "hilbert16-ss-cubic-l2-core/v1",
        "claim": (
            "L1 = sqrt(2)*mu at both wells of the two-well van der Pol "
            "3-jet; V2 = -sqrt(2)*mu*(23*mu^2+18)/96 in the q1 Poincaré "
            "gauge. Order is 1, so L2 does not add a small cycle. Not a "
            "bound on H(n)."
        ),
        "hn_moved": False,
        "fourteen_from_L2": False,
        "L2_zero_while_L1": False,
        "L2_extra_cycles": False,
        "cycles_proved": 0,
        "two_hopf_cycles": 0,
        "degree": 3,
        "weak_focus_order": 1,
        "L2_first_nonzero": False,
        "L2_irrelevant_to_cyclicity": True,
        "trace_at_wells": "0",
        "L1_plus": "sqrt(2)*mu",
        "L1_minus": "sqrt(2)*mu",
        "L1_E_plus": "3*sqrt(2)*mu/2",
        "L1_cubic_plus": "-sqrt(2)*mu/2",
        "L1_E_minus": "3*sqrt(2)*mu/2",
        "L1_cubic_minus": "-sqrt(2)*mu/2",
        "V1_plus": "sqrt(2)*mu/8",
        "V1_minus": "sqrt(2)*mu/8",
        "V2_plus": "-sqrt(2)*mu*(23*mu^2+18)/96",
        "V2_minus": "-sqrt(2)*mu*(23*mu^2+18)/96",
        "V1_mu0": "0",
        "V2_mu0": "0",
        "V2_sample_mu1": "-41*sqrt(2)/96",
        "V2_sample_mu2": "-55*sqrt(2)/24",
        "V2_sample_mu_m1": "41*sqrt(2)/96",
        "centers_at_mu0": True,
        "what_this_is_not": [
            "not a dent of H(n)",
            "not fourteen cycles from L2",
            "not a proved pair of Hopf cycles",
            "not L2 as the first nonzero quantity",
            "not a new H(3)",
        ],
        "V1_closed_ok": reduce_s(v1v2["V1"] - V1_CLOSED) == 0,
        "V2_closed_ok": reduce_s(v1v2["V2"] - V2_CLOSED) == 0,
    }


def build_jets(jet_p, jet_m, pieces) -> dict:
    return {
        "schema": "hilbert16-ss-cubic-l2-jets/v1",
        "L1_formula": {
            "quad": monomials(L1_E, QUAD_NAMES),
            "cubic": monomials(L1_CUBIC, CUBIC_NAMES),
        },
        "plus": {
            "jet": jet_record(jet_p),
            "L1_E": fmt_s_mu(pieces["plus"]["L1_E"]),
            "L1_cubic": fmt_s_mu(pieces["plus"]["L1_cubic"]),
            "L1_full": fmt_s_mu(pieces["plus"]["L1_full"]),
        },
        "minus": {
            "jet": jet_record(jet_m),
            "L1_E": fmt_s_mu(pieces["minus"]["L1_E"]),
            "L1_cubic": fmt_s_mu(pieces["minus"]["L1_cubic"]),
            "L1_full": fmt_s_mu(pieces["minus"]["L1_full"]),
        },
        "V2": {
            "plus": "-sqrt(2)*mu*(23*mu^2+18)/96",
            "minus": "-sqrt(2)*mu*(23*mu^2+18)/96",
            "gauge": "y^n coefficient of even F_n vanishes",
        },
        "mu0_hamiltonian": {
            "H4_plus": "4*v^2+4*u^2+4*u^3+u^4",
            "H4_minus": "4*v^2+4*u^2-4*u^3+u^4",
        },
    }


def check_core(payload: dict) -> None:
    if payload.get("hn_moved") is not False:
        raise AssertionError("core must not claim that H(n) moved")
    if payload.get("fourteen_from_L2") is not False:
        raise AssertionError("must not claim 14 from L2")
    if payload.get("L2_extra_cycles") is not False:
        raise AssertionError("must not claim extra cycles from L2")
    if payload.get("L2_zero_while_L1") is not False:
        raise AssertionError("must not claim L2=0 while L1≠0")
    if payload.get("cycles_proved") != 0:
        raise AssertionError("must not claim proved cycles")
    if payload.get("two_hopf_cycles") != 0:
        raise AssertionError("must not claim two Hopf cycles")
    if payload.get("weak_focus_order") != 1:
        raise AssertionError("order is 1")
    if payload.get("L2_first_nonzero") is not False:
        raise AssertionError("L2 is not first nonzero")
    if payload.get("L1_plus") != "sqrt(2)*mu" or payload.get("L1_minus") != "sqrt(2)*mu":
        raise AssertionError("L1 replay")
    if payload.get("V2_plus") != "-sqrt(2)*mu*(23*mu^2+18)/96":
        raise AssertionError("V2 plus")
    if payload.get("V2_minus") != "-sqrt(2)*mu*(23*mu^2+18)/96":
        raise AssertionError("V2 minus")
    if payload.get("degree") != 3:
        raise AssertionError("degree")


def check_jets(payload: dict, jet_p, jet_m, pieces) -> None:
    if payload["schema"] != "hilbert16-ss-cubic-l2-jets/v1":
        raise AssertionError("jets schema")
    if payload["L1_formula"]["quad"] != monomials(L1_E, QUAD_NAMES):
        raise AssertionError("L1_E monomials")
    if payload["L1_formula"]["cubic"] != monomials(L1_CUBIC, CUBIC_NAMES):
        raise AssertionError("L1 cubic monomials")
    if payload["plus"]["jet"] != jet_record(jet_p):
        raise AssertionError("plus jet cert")
    if payload["minus"]["jet"] != jet_record(jet_m):
        raise AssertionError("minus jet cert")
    if payload["plus"]["L1_full"] != fmt_s_mu(pieces["plus"]["L1_full"]):
        raise AssertionError("plus L1 cert")
    if payload["V2"]["plus"] != "-sqrt(2)*mu*(23*mu^2+18)/96":
        raise AssertionError("V2 cert")


def dump_lines() -> list[str]:
    quad = monomials(L1_E, QUAD_NAMES)
    cubic = monomials(L1_CUBIC, CUBIC_NAMES)
    lines = [
        "imagined_H3_ge_14 DROP",
        "imagined_L2_zero_while_L1 DROP",
        "imagined_L2_extra_cycles DROP",
        "L1_replay KEEP",
        "L1_cubic_formula KEEP",
        "V2_3jet KEEP",
        "mu0_all_lyapunov KEEP",
        "hn_moved 0",
        "fourteen_from_L2 0",
        "L2_extra_cycles 0",
        "L2_zero_while_L1 0",
        "cycles_proved 0",
        "two_hopf_cycles 0",
        "degree 3",
        "weak_focus_order 1",
        "L2_first_nonzero 0",
        "L2_irrelevant_to_cyclicity 1",
        "trace_at_wells 0",
        "plus_jet b20=3/2 b11=-sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2",
        "minus_jet b20=-3/2 b11=sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2",
        "L1_formula_quad (a20+a02)*a11-(b20+b02)*b11-2*a20*b20+2*a02*b02",
        "L1_formula_cubic 3*a30+a12+b21+3*b03",
    ]
    for mon in quad:
        lines.append(f"L1_E {mon['term']} {mon['coeff']}")
    for mon in cubic:
        lines.append(f"L1_cubic {mon['term']} {mon['coeff']}")
    lines.extend(
        [
            "L1_E_plus 3*sqrt(2)*mu/2",
            "L1_cubic_plus -sqrt(2)*mu/2",
            "L1_plus sqrt(2)*mu",
            "L1_E_minus 3*sqrt(2)*mu/2",
            "L1_cubic_minus -sqrt(2)*mu/2",
            "L1_minus sqrt(2)*mu",
            "V1_over_L1 1/8",
            "V1_plus sqrt(2)*mu/8",
            "V1_minus sqrt(2)*mu/8",
            "V2_plus -sqrt(2)*mu*(23*mu^2+18)/96",
            "V2_minus -sqrt(2)*mu*(23*mu^2+18)/96",
            "V1_mu0 0",
            "V2_mu0 0",
            "V2_sample_mu1 -41*sqrt(2)/96",
            "V2_sample_mu2 -55*sqrt(2)/24",
            "V2_sample_mu-1 41*sqrt(2)/96",
            "centers_at_mu0 1",
            "generic_focus_L1 -2",
            "hamiltonian_L1 0",
        ]
    )
    return lines


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    check_equilibria()
    check_formula()
    jet_p, jet_m = extract_jets()
    pieces = check_l1(jet_p, jet_m)
    v1v2 = check_v2()
    check_mu0_hamiltonian()

    core = build_core(v1v2)
    jets = build_jets(jet_p, jet_m, pieces)
    check_core(core)
    check_jets(jets, jet_p, jet_m, pieces)

    if args.write_cert:
        write_json(CORE_PATH, core)
        write_json(JETS_PATH, jets)
        print(f"wrote {CORE_PATH}")
        print(f"wrote {JETS_PATH}")

    if not CORE_PATH.is_file() or not JETS_PATH.is_file():
        raise SystemExit("missing certificates; run with --write-cert")

    saved_core = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    saved_jets = json.loads(JETS_PATH.read_text(encoding="utf-8"))
    check_core(saved_core)
    check_jets(saved_jets, jet_p, jet_m, pieces)
    if saved_core != core:
        raise AssertionError("committed core.json is not the canonical dump")
    if saved_jets != jets:
        raise AssertionError("committed jets.json is not the canonical dump")

    lines = dump_lines()
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID ss-cubic-l2 replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
