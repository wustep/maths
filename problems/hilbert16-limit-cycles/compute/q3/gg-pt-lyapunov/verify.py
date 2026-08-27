#!/usr/bin/env python3
"""First Lyapunov quantity at the three Prohens–Torregrosa Darboux
centers of the explicit degree-4 field from q2/q-pt-darboux.

The unperturbed field is a Darboux center: dH/dt = 0, so every
Lyapunov quantity vanishes. The q1 line-E polynomial L1_E is the
quadratic piece. A degree-4 jet also contributes the cubic terms
that the same Poincaré construction produces:

    L1 = L1_E + 3 a30 + a12 + b21 + 3 b03,    V1 = L1 / 8.

L1_E is not zero at (1, ±2). The cubic piece cancels it. The
imagined H(4) >= 29 claim is not certified here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certs" / "lyapunov.json"

X, Y = sp.symbols("x y")
MU = sp.symbols("mu")
SQRT11 = sp.sqrt(11)
XY = (X, Y)

A20, A11, A02, B20, B11, B02 = sp.symbols("a20 a11 a02 b20 b11 b02")
A30, A21, A12, A03 = sp.symbols("a30 a21 a12 a03")
B30, B21, B12, B03 = sp.symbols("b30 b21 b12 b03")

L1_E = (A20 + A02) * A11 - (B20 + B02) * B11 - 2 * A20 * B20 + 2 * A02 * B02
L1_CUBIC = 3 * A30 + A12 + B21 + 3 * B03
L1_FULL = L1_E + L1_CUBIC

QUAD_NAMES = ("a20", "a11", "a02", "b20", "b11", "b02")
CUBIC_NAMES = ("a30", "a21", "a12", "a03", "b30", "b21", "b12", "b03")
JET_KEYS = {
    (2, 0, "P"): "a20",
    (1, 1, "P"): "a11",
    (0, 2, "P"): "a02",
    (3, 0, "P"): "a30",
    (2, 1, "P"): "a21",
    (1, 2, "P"): "a12",
    (0, 3, "P"): "a03",
    (2, 0, "Q"): "b20",
    (1, 1, "Q"): "b11",
    (0, 2, "Q"): "b02",
    (3, 0, "Q"): "b30",
    (2, 1, "Q"): "b21",
    (1, 2, "Q"): "b12",
    (0, 3, "Q"): "b03",
}

CENTERS = ((0, 0), (1, 2), (1, -2))


def terms_of(expr, variables) -> list[dict]:
    poly = sp.Poly(sp.expand(expr), *variables, domain="ZZ")
    items: list[dict] = []
    names = [str(v) for v in variables]
    for exp, coeff in poly.as_dict().items():
        coeff = int(coeff)
        if coeff == 0:
            continue
        item: dict[str, int | str] = {"coeff": str(coeff)}
        for name, power in zip(names, exp):
            if power:
                item[name] = int(power)
        items.append(item)
    items.sort(key=lambda it: tuple(int(it.get(n, 0)) for n in names))
    return items


def from_terms(variables, terms) -> sp.Expr:
    acc = sp.Integer(0)
    names = [str(v) for v in variables]
    for item in terms:
        mon = sp.Integer(int(item["coeff"]))
        for name, var in zip(names, variables):
            power = int(item.get(name, 0))
            if power:
                mon *= var**power
        acc += mon
    return sp.expand(acc)


def require_zero(expr, label: str) -> None:
    if sp.expand(expr) != 0:
        raise AssertionError(f"{label} is not zero: {sp.expand(expr)}")


def require_equal(left, right, label: str) -> None:
    if sp.expand(left - right) != 0:
        raise AssertionError(f"{label} mismatch: {sp.expand(left - right)}")


def require_terms(variables, terms, expr, label: str) -> None:
    require_equal(from_terms(variables, terms), expr, label)


def primitive_field() -> tuple[sp.Expr, sp.Expr]:
    p = Y * (X**3 + 2 * X**2 - X * Y**2 - 3 * X + 4)
    q = (
        15 * X**4
        - 21 * X**3
        + 3 * X**2 * Y**2
        - 15 * X**2
        + 7 * X * Y**2
        - 11 * X
        - 2 * Y**4
        + 6 * Y**2
    )
    return sp.expand(p), sp.expand(q)


def add_perturbation(p, q, kind: str):
    if kind == "none":
        return p, q
    if kind == "user_xy":
        return sp.expand(p + MU * X * (X - 1) * Y), q
    if kind == "tracefree_xy":
        return sp.expand(p + MU * X * (X - 1) ** 2 * Y), q
    if kind == "x2_shift":
        return sp.expand(p + MU * X**2 * (X - 1) ** 2), q
    raise ValueError(kind)


def jacobian(p, q, point: tuple[int, int]):
    j = sp.Matrix(
        [
            [sp.diff(p, X), sp.diff(p, Y)],
            [sp.diff(q, X), sp.diff(q, Y)],
        ]
    )
    return sp.simplify(j.subs({X: point[0], Y: point[1]}))


def homog(expr, u, v, degree: int) -> sp.Expr:
    poly = sp.Poly(sp.expand(expr), u, v)
    acc = sp.Integer(0)
    for exp, coeff in poly.as_dict().items():
        if sum(exp) == degree:
            acc += coeff * u ** exp[0] * v ** exp[1]
    return acc


def jet_coeffs(p_expr, q_expr, u, v) -> dict[str, sp.Expr]:
    pp = sp.Poly(sp.expand(p_expr), u, v)
    qp = sp.Poly(sp.expand(q_expr), u, v)
    out: dict[str, sp.Expr] = {}
    for (i, j, which), name in JET_KEYS.items():
        src = pp if which == "P" else qp
        out[name] = src.coeff_monomial(u**i * v**j)
    return out


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


def derive_v1() -> sp.Expr:
    """Poincaré V1 for a quadratic+cubic jet in the q1 normal form."""
    x, y = sp.symbols("x y")
    p2 = A20 * x**2 + A11 * x * y + A02 * y**2
    q2 = B20 * x**2 + B11 * x * y + B02 * y**2
    p3 = A30 * x**3 + A21 * x**2 * y + A12 * x * y**2 + A03 * y**3
    q3 = B30 * x**3 + B21 * x**2 * y + B12 * x * y**2 + B03 * y**3
    x1 = (-y, x)
    x2 = (p2, q2)
    x3 = (p3, q3)
    f2 = (x**2 + y**2) / 2

    f3, c3 = hom_poly(3, "f3", x, y)
    eq3 = sp.expand(lie(f3, x1, x, y) + lie(f2, x2, x, y))
    sys3 = [eq3.coeff(x, i).coeff(y, 3 - i) for i in range(4)]
    f3s = sp.expand(f3.subs(sp.solve(sys3, c3)))

    f4, c4 = hom_poly(4, "f4", x, y)
    v1 = sp.symbols("V1")
    eq4 = sp.expand(
        lie(f4, x1, x, y)
        + lie(f3s, x2, x, y)
        + lie(f2, x3, x, y)
        - v1 * (x**2 + y**2) ** 2
    )
    # Same gauge as q1/l1_focal.py: y^4 coefficient of F4 vanishes.
    sys4 = [eq4.coeff(x, i).coeff(y, 4 - i) for i in range(5)] + [c4[0]]
    sol4 = sp.solve(sys4, c4 + [v1], dict=True)[0]
    return sp.factor(sol4[v1])


def fmt_rat(r) -> str:
    r = sp.Rational(r)
    if r.q == 1:
        return str(int(r.p))
    return f"{int(r.p)}/{int(r.q)}"


def split_qsqrt(expr) -> tuple[sp.Rational, sp.Rational]:
    dummy = sp.symbols("S")
    expanded = sp.expand(expr).subs(SQRT11, dummy)
    poly = sp.Poly(expanded, dummy, domain=sp.QQ)
    if poly.degree() > 1:
        raise AssertionError(f"not in Q(sqrt(11)): {expr}")
    a = poly.nth(0) if poly.degree() >= 0 else 0
    b = poly.nth(1) if poly.degree() >= 1 else 0
    return sp.Rational(a), sp.Rational(b)


def fmt_qsqrt(expr) -> str:
    a, b = split_qsqrt(expr)
    if b == 0:
        return fmt_rat(a)
    irr = f"{fmt_rat(b)}*sqrt(11)"
    if a == 0:
        return irr
    if b > 0:
        return f"{fmt_rat(a)}+{irr}"
    return f"{fmt_rat(a)}{irr}"


def fmt_in_mu(expr) -> str:
    if expr is None:
        return "strong"
    expanded = sp.expand(sp.simplify(expr))
    if expanded == 0:
        return "0"
    c0 = sp.expand(expanded.subs(MU, 0))
    c1 = sp.expand(expanded.coeff(MU, 1))
    c2 = sp.expand(expanded.coeff(MU, 2))
    parts: list[str] = []
    if c0 != 0:
        parts.append(fmt_qsqrt(c0))
    if c1 != 0:
        parts.append(fmt_qsqrt(c1) + "*mu")
    if c2 != 0:
        parts.append(fmt_qsqrt(c2) + "*mu^2")
    if not parts:
        return "0"
    out = parts[0]
    for part in parts[1:]:
        if part.startswith("-"):
            out += part
        else:
            out += "+" + part
    return out


def fmt_bi(expr, u=X, v=Y) -> str:
    poly = sp.Poly(sp.expand(expr), u, v, domain=sp.ZZ)
    items = [(exp, int(coeff)) for exp, coeff in poly.as_dict().items() if coeff]
    items.sort(key=lambda it: (-it[0][0], -it[0][1]))
    if not items:
        return "0"
    chunks: list[str] = []
    for (i, j), coeff in items:
        vars_part = ""
        if i == 1:
            vars_part += "*x"
        elif i > 1:
            vars_part += f"*x^{i}"
        if j == 1:
            vars_part += "*y"
        elif j > 1:
            vars_part += f"*y^{j}"
        if vars_part:
            if coeff == 1:
                body = vars_part[1:]
            elif coeff == -1:
                body = "-" + vars_part[1:]
            else:
                body = f"{coeff}{vars_part}"
        else:
            body = str(coeff)
        if not chunks:
            chunks.append(body)
        elif body.startswith("-"):
            chunks.append(body)
        else:
            chunks.append("+" + body)
    return "".join(chunks)


def l1_formula_monomials() -> tuple[list[dict], list[dict]]:
    quad: list[dict] = []
    poly_e = sp.Poly(sp.expand(L1_E), A20, A11, A02, B20, B11, B02, domain=sp.ZZ)
    names_e = list(QUAD_NAMES)
    for monom, coeff in poly_e.terms():
        parts = []
        for name, power in zip(names_e, monom):
            if power == 1:
                parts.append(name)
            elif power > 1:
                parts.append(f"{name}**{power}")
        parts.sort()
        quad.append({"term": "*".join(parts), "coeff": int(coeff)})
    quad.sort(key=lambda r: r["term"])

    cubic: list[dict] = []
    poly_c = sp.Poly(sp.expand(L1_CUBIC), A30, A21, A12, A03, B30, B21, B12, B03, domain=sp.ZZ)
    names_c = list(CUBIC_NAMES)
    for monom, coeff in poly_c.terms():
        parts = []
        for name, power in zip(names_c, monom):
            if power == 1:
                parts.append(name)
            elif power > 1:
                parts.append(f"{name}**{power}")
        parts.sort()
        cubic.append({"term": "*".join(parts), "coeff": int(coeff)})
    cubic.sort(key=lambda r: r["term"])
    return quad, cubic


def normalize_jet(p, q, x0: int, y0: int) -> dict:
    """Translate, put the linear part in (-η, ξ) form, return L1 pieces."""
    u, v = sp.symbols("u v")
    pt = sp.expand(p.subs({X: x0 + u, Y: y0 + v}))
    qt = sp.expand(q.subs({X: x0 + u, Y: y0 + v}))
    j = jacobian(p, q, (x0, y0))
    a, b, c, d = j[0, 0], j[0, 1], j[1, 0], j[1, 1]
    trace = sp.expand(a + d)
    det = sp.expand(j.det())
    eq_p = sp.expand(p.subs({X: x0, Y: y0}))
    eq_q = sp.expand(q.subs({X: x0, Y: y0}))
    if eq_p != 0 or eq_q != 0:
        raise AssertionError(f"({x0},{y0}) is not an equilibrium")

    p1, q1 = homog(pt, u, v, 1), homog(qt, u, v, 1)
    p2, q2 = homog(pt, u, v, 2), homog(qt, u, v, 2)
    p3, q3 = homog(pt, u, v, 3), homog(qt, u, v, 3)

    result = {
        "point": [x0, y0],
        "jacobian": [a, b, c, d],
        "trace": trace,
        "det": det,
        "P1": p1,
        "Q1": q1,
        "P2": p2,
        "Q2": q2,
        "P3": p3,
        "Q3": q3,
        "L1_E": None,
        "L1_cubic": None,
        "L1_full": None,
        "coeffs": None,
        "omega": None,
        "alpha": None,
        "beta": None,
    }

    # Weak-focus L1 is only defined when the trace vanishes.
    if sp.expand(trace.subs(MU, 0)) != 0 or (trace != 0 and trace.free_symbols):
        # Constant nonzero trace, or a μ-dependent trace.
        if trace != 0:
            return result

    if sp.simplify(a.subs(MU, 0)) != 0 or sp.simplify(d.subs(MU, 0)) != 0:
        raise AssertionError(f"linear part not off-diagonal at ({x0},{y0}): {j}")

    p_lin, q_lin = b, c
    omega2 = sp.simplify(-p_lin * q_lin)
    if omega2.free_symbols or omega2 <= 0:
        raise AssertionError(f"cannot form a linear center at ({x0},{y0}): ω²={omega2}")
    omega = sp.sqrt(omega2)
    alpha = sp.Integer(1)
    beta = sp.simplify(-omega / p_lin)
    xi, eta = sp.symbols("xi eta")
    p_n = sp.expand(pt.subs({u: alpha * xi, v: beta * eta}) / (alpha * omega))
    q_n = sp.expand(qt.subs({u: alpha * xi, v: beta * eta}) / (beta * omega))
    require_equal(homog(p_n, xi, eta, 1), -eta, f"normal ẋ linear at ({x0},{y0})")
    require_equal(homog(q_n, xi, eta, 1), xi, f"normal ẏ linear at ({x0},{y0})")
    coeffs = jet_coeffs(p_n, q_n, xi, eta)
    result.update(
        {
            "alpha": alpha,
            "beta": beta,
            "omega": omega,
            "coeffs": {k: sp.simplify(val) for k, val in coeffs.items()},
            "L1_E": sp.simplify(l1_e_of(coeffs)),
            "L1_cubic": sp.simplify(l1_cubic_of(coeffs)),
            "L1_full": sp.simplify(l1_full_of(coeffs)),
        }
    )
    return result


def check_formula() -> None:
    v1 = derive_v1()
    require_equal(sp.expand(8 * v1 - L1_FULL), 0, "8 V1 = L1")
    require_equal(sp.expand(v1 * 8 - L1_E - L1_CUBIC), 0, "V1 split")
    # Quadratic-only reduction: cubics off, recover the q1 polynomial.
    require_equal(sp.expand(L1_E - ((A20 + A02) * A11 - (B20 + B02) * B11 - 2 * A20 * B20 + 2 * A02 * B02)), 0, "L1_E")
    # q1 generic focus and a Hamiltonian cubic (center).
    focus = {"a20": 1, "a11": 0, "a02": 0, "b20": 1, "b11": 0, "b02": 0, "a30": 0, "a21": 0, "a12": 0, "a03": 0, "b30": 0, "b21": 0, "b12": 0, "b03": 0}
    if l1_full_of(focus) != -2:
        raise AssertionError("generic focus L1")
    # Hamiltonian ẋ = −∂H/∂y, ẏ = ∂H/∂x for
    # H = r²/2 + x³ − 2 x² y + 3 x y² − y³.
    # Then (a20, a11, a02, b20, b11, b02) = (2, −6, 3, 3, −4, 3).
    ham = {"a20": 2, "a11": -6, "a02": 3, "b20": 3, "b11": -4, "b02": 3, "a30": 0, "a21": 0, "a12": 0, "a03": 0, "b30": 0, "b21": 0, "b12": 0, "b03": 0}
    if l1_full_of(ham) != 0:
        raise AssertionError(f"hamiltonian L1 {l1_full_of(ham)}")
    shi = {"a20": -10, "a11": 5, "a02": 1, "b20": 1, "b11": -25, "b02": 0, "a30": 0, "a21": 0, "a12": 0, "a03": 0, "b30": 0, "b21": 0, "b12": 0, "b03": 0}
    if l1_full_of(shi) != 0:
        raise AssertionError("Shi L1")


def check_unperturbed() -> list[dict]:
    p, q = primitive_field()
    if int(sp.Poly(p, X, Y).total_degree()) != 4 or int(sp.Poly(q, X, Y).total_degree()) != 4:
        raise AssertionError("field is not degree 4")
    rows = []
    expected = {
        (0, 0): {"det": 44, "J": (0, 4, -11, 0), "L1_E": 0, "L1_cubic": 0},
        (1, 2): {"det": 64, "J": (0, -8, 8, 0), "L1_E": sp.Rational(9, 2), "L1_cubic": -sp.Rational(9, 2)},
        (1, -2): {"det": 64, "J": (0, -8, 8, 0), "L1_E": -sp.Rational(9, 2), "L1_cubic": sp.Rational(9, 2)},
    }
    for pt in CENTERS:
        row = normalize_jet(p, q, pt[0], pt[1])
        exp = expected[pt]
        if row["trace"] != 0:
            raise AssertionError(f"trace at {pt}")
        if row["det"] != exp["det"]:
            raise AssertionError(f"det at {pt}: {row['det']}")
        got_j = tuple(int(sp.Integer(entry)) for entry in row["jacobian"])
        if got_j != exp["J"]:
            raise AssertionError(f"J at {pt}: {got_j}")
        require_equal(row["L1_E"], exp["L1_E"], f"L1_E at {pt}")
        require_equal(row["L1_cubic"], exp["L1_cubic"], f"L1_cubic at {pt}")
        require_zero(row["L1_full"], f"L1_full at {pt}")
        rows.append(row)
    return rows


def check_origin_jet() -> dict[str, str]:
    p, q = primitive_field()
    u, v = X, Y  # already at the origin
    p2, q2 = homog(p, u, v, 2), homog(q, u, v, 2)
    p3, q3 = homog(p, u, v, 3), homog(q, u, v, 3)
    require_equal(p2, -3 * X * Y, "origin P2")
    require_equal(q2, -15 * X**2 + 6 * Y**2, "origin Q2")
    require_equal(p3, 2 * X**2 * Y, "origin P3")
    require_equal(q3, -21 * X**3 + 7 * X * Y**2, "origin Q3")
    require_equal(homog(p, u, v, 1), 4 * Y, "origin P1")
    require_equal(homog(q, u, v, 1), -11 * X, "origin Q1")
    return {
        "P1": fmt_bi(4 * Y),
        "Q1": fmt_bi(-11 * X),
        "P2": fmt_bi(p2),
        "Q2": fmt_bi(q2),
        "P3": fmt_bi(p3),
        "Q3": fmt_bi(q3),
    }


def check_perturbations() -> dict[str, dict]:
    p0, q0 = primitive_field()
    out: dict[str, dict] = {}
    specs = {
        "user_xy": {
            "delta_P": "mu*x*(x-1)*y",
            "delta_Q": "0",
            "traces": ["0", "2*mu", "-2*mu"],
            "L1_full": ["0", "strong", "strong"],
        },
        "tracefree_xy": {
            "delta_P": "mu*x*(x-1)^2*y",
            "delta_Q": "0",
            "traces": ["0", "0", "0"],
            "L1_full": ["0", "-1*mu", "1*mu"],
        },
        "x2_shift": {
            "delta_P": "mu*x^2*(x-1)^2",
            "delta_Q": "0",
            "traces": ["0", "0", "0"],
            "L1_full": ["-351/968*sqrt(11)*mu", "-1/8*mu", "-1/8*mu"],
        },
    }
    for kind, spec in specs.items():
        p, q = add_perturbation(p0, q0, kind)
        traces = []
        l1s = []
        for pt in CENTERS:
            row = normalize_jet(p, q, pt[0], pt[1])
            traces.append(fmt_in_mu(row["trace"]))
            l1s.append(fmt_in_mu(row["L1_full"]))
        if traces != spec["traces"]:
            raise AssertionError(f"{kind} traces {traces} != {spec['traces']}")
        if l1s != spec["L1_full"]:
            raise AssertionError(f"{kind} L1 {l1s} != {spec['L1_full']}")
        # Equilibria stay put for every μ.
        for pt in CENTERS:
            if sp.expand(p.subs({X: pt[0], Y: pt[1]})) != 0:
                raise AssertionError(f"{kind} moved P at {pt}")
            if sp.expand(q.subs({X: pt[0], Y: pt[1]})) != 0:
                raise AssertionError(f"{kind} moved Q at {pt}")
        out[kind] = {**spec, "traces": traces, "L1_full": l1s}
    return out


def build_certificate(unperturbed: list[dict], origin_jet: dict[str, str], perts: dict) -> dict:
    p, q = primitive_field()
    quad_m, cubic_m = l1_formula_monomials()
    centers = []
    for row in unperturbed:
        centers.append(
            {
                "point": row["point"],
                "trace": 0,
                "det": int(row["det"]),
                "jacobian": [int(sp.Integer(v)) for v in row["jacobian"]],
                "L1_E": fmt_in_mu(row["L1_E"]),
                "L1_cubic": fmt_in_mu(row["L1_cubic"]),
                "L1_full": fmt_in_mu(row["L1_full"]),
            }
        )
    return {
        "schema": "hilbert16-gg-pt-lyapunov/v1",
        "claim": (
            "unperturbed PT Darboux centers have vanishing first Lyapunov "
            "quantity after the q1 normal form plus the cubic jet; "
            "not a dent of H(4)"
        ),
        "field": {
            "variables": ["x", "y"],
            "P": terms_of(p, XY),
            "Q": terms_of(q, XY),
            "deg_P": 4,
            "deg_Q": 4,
        },
        "L1_formula": {"quad": quad_m, "cubic": cubic_m},
        "centers": centers,
        "origin_jet": origin_jet,
        "perturbations": perts,
    }


def check_certificate(payload: dict) -> None:
    p, q = primitive_field()
    if payload["schema"] != "hilbert16-gg-pt-lyapunov/v1":
        raise AssertionError("schema")
    block = payload["field"]
    require_terms(XY, block["P"], p, "cert P")
    require_terms(XY, block["Q"], q, "cert Q")
    if block["deg_P"] != 4 or block["deg_Q"] != 4:
        raise AssertionError("degree")
    quad_m, cubic_m = l1_formula_monomials()
    if payload["L1_formula"]["quad"] != quad_m:
        raise AssertionError("L1 quad monomials")
    if payload["L1_formula"]["cubic"] != cubic_m:
        raise AssertionError("L1 cubic monomials")
    dets = [c["det"] for c in payload["centers"]]
    traces = [c["trace"] for c in payload["centers"]]
    if dets != [44, 64, 64] or traces != [0, 0, 0]:
        raise AssertionError("center linearization")
    if [c["L1_full"] for c in payload["centers"]] != ["0", "0", "0"]:
        raise AssertionError("unperturbed L1_full")
    if [c["L1_E"] for c in payload["centers"]] != ["0", "9/2", "-9/2"]:
        raise AssertionError("unperturbed L1_E")
    if [c["L1_cubic"] for c in payload["centers"]] != ["0", "-9/2", "9/2"]:
        raise AssertionError("unperturbed L1_cubic")
    jet = payload["origin_jet"]
    if jet["P2"] != "-3*x*y" or jet["Q2"] != "-15*x^2+6*y^2":
        raise AssertionError("origin quadratic jet")
    if jet["P3"] != "2*x^2*y" or jet["Q3"] != "-21*x^3+7*x*y^2":
        raise AssertionError("origin cubic jet")
    if payload["perturbations"]["tracefree_xy"]["L1_full"] != ["0", "-1*mu", "1*mu"]:
        raise AssertionError("tracefree L1")
    if payload["perturbations"]["x2_shift"]["L1_full"] != [
        "-351/968*sqrt(11)*mu",
        "-1/8*mu",
        "-1/8*mu",
    ]:
        raise AssertionError("x2 L1")
    if payload["perturbations"]["user_xy"]["L1_full"] != ["0", "strong", "strong"]:
        raise AssertionError("user L1")
    if payload["perturbations"]["user_xy"]["traces"] != ["0", "2*mu", "-2*mu"]:
        raise AssertionError("user traces")


def dump_lines(
    unperturbed: list[dict],
    origin_jet: dict[str, str],
    perts: dict,
) -> list[str]:
    quad_m, cubic_m = l1_formula_monomials()
    lines = [
        "status DROP 29 KEEP L1=0",
        "field_degree 4 4",
    ]
    for row in unperturbed:
        x0, y0 = row["point"]
        lines.append(f"center {x0} {y0} equilibrium 1 trace 0 det {int(row['det'])}")
    for row in unperturbed:
        x0, y0 = row["point"]
        j = " ".join(str(int(sp.Integer(v))) for v in row["jacobian"])
        lines.append(f"jacobian {x0} {y0} {j}")
    lines.append(f"origin_after_linear P2 {origin_jet['P2']}")
    lines.append(f"origin_after_linear Q2 {origin_jet['Q2']}")
    lines.append(f"origin_after_linear P3 {origin_jet['P3']}")
    lines.append(f"origin_after_linear Q3 {origin_jet['Q3']}")
    l1e = " ".join(fmt_in_mu(r["L1_E"]) for r in unperturbed)
    l1c = " ".join(fmt_in_mu(r["L1_cubic"]) for r in unperturbed)
    l1f = " ".join(fmt_in_mu(r["L1_full"]) for r in unperturbed)
    lines.append(f"L1_E_unperturbed {l1e}")
    lines.append(f"L1_cubic_unperturbed {l1c}")
    lines.append(f"L1_full_unperturbed {l1f}")
    for mon in quad_m:
        lines.append(f"L1_E {mon['term']} {mon['coeff']}")
    for mon in cubic_m:
        lines.append(f"L1_cubic {mon['term']} {mon['coeff']}")
    lines.append("V1_over_L1 1/8")
    lines.append("generic_focus_L1 -2")
    lines.append("hamiltonian_L1 0")
    lines.append(
        "user_pert_trace " + " ".join(perts["user_xy"]["traces"])
    )
    lines.append(
        "user_pert_L1_full " + " ".join(perts["user_xy"]["L1_full"])
    )
    lines.append(
        "tf_pert_L1_full " + " ".join(perts["tracefree_xy"]["L1_full"])
    )
    lines.append(
        "x2_pert_L1_full " + " ".join(perts["x2_shift"]["L1_full"])
    )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    check_formula()
    unperturbed = check_unperturbed()
    origin_jet = check_origin_jet()
    perts = check_perturbations()
    payload = build_certificate(unperturbed, origin_jet, perts)
    check_certificate(payload)
    if args.write_cert:
        CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {CERT_PATH}")
    if not CERT_PATH.is_file():
        raise SystemExit(f"missing certificate {CERT_PATH}")
    saved = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    check_certificate(saved)
    if saved != payload:
        raise AssertionError("committed certificate is not the canonical dump")

    lines = dump_lines(unperturbed, origin_jet, perts)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID gg-pt-lyapunov identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
