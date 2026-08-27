#!/usr/bin/env python3
"""Exact reconstruction of the Prohens–Torregrosa H_{4,5} Darboux
field, and the quadratic contact / collinearity identities that sit
under Coppel 1966 Theorem 2.

Python uses sympy. A second, independent expansion is verify.rs
(sparse BTreeMap products, Sylvester determinant, integer box).
The imagined H(4) >= 29 claim is not certified here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certs" / "identities.json"

X, Y = sp.symbols("x y")
T = sp.symbols("t")
T1, T2, T3 = sp.symbols("t1 t2 t3")
A00, A10, A01, A20, A11, A02 = sp.symbols("a00 a10 a01 a20 a11 a02")
B00, B10, B01, B20, B11, B02 = sp.symbols("b00 b10 b01 b20 b11 b02")

XY = (X, Y)
QUAD_COEFFS = (A00, A10, A01, A20, A11, A02, B00, B10, B01, B20, B11, B02)
LINE_VARS = (T, A00, A10, A20, B00, B10, B20)
RES_VARS = (X,) + QUAD_COEFFS
VANDER_VARS = (T1, T2, T3)
SHI_RES_VARS = (X,)


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
    diff = sp.expand(left - right)
    if hasattr(diff, "rows"):
        flat = [diff[i, j] for i in range(diff.rows) for j in range(diff.cols)]
        if any(sp.expand(entry) != 0 for entry in flat):
            raise AssertionError(f"{label} mismatch: {diff}")
        return
    if diff != 0:
        raise AssertionError(f"{label} mismatch: {diff}")


def require_terms(variables, terms, expr, label: str) -> None:
    require_equal(from_terms(variables, terms), expr, label)


def total_degree(expr, variables) -> int:
    if sp.expand(expr) == 0:
        return -1
    return int(sp.Poly(sp.expand(expr), *variables, domain="ZZ").total_degree())


def content_of(expr, variables) -> int:
    poly = sp.Poly(sp.expand(expr), *variables, domain="ZZ")
    if poly == 0:
        return 0
    return int(sp.gcd([sp.Integer(int(c)) for c in poly.coeffs()]))


# ---------------------------------------------------------------------------
# Darboux seed
# ---------------------------------------------------------------------------


def A_poly():
    return 2 * X**4 - X**2 + Y**2 - 2 * X - 2


def B_poly():
    return 8 * X**5 - 5 * X**3 + 5 * X * Y**2 - 10 * X**2 - 5 * X - 4


def darboux_raw() -> dict[str, sp.Expr]:
    a, b = A_poly(), B_poly()
    ax, ay = sp.diff(a, X), sp.diff(a, Y)
    bx, by = sp.diff(b, X), sp.diff(b, Y)
    p_raw = sp.expand(-5 * b * ay + 4 * a * by)
    q_raw = sp.expand(5 * b * ax - 4 * a * bx)
    inner = sp.expand(-b + 4 * X * a)
    return {
        "A": a,
        "B": b,
        "Ax": ax,
        "Ay": ay,
        "Bx": bx,
        "By": by,
        "inner": inner,
        "P_raw": p_raw,
        "Q_raw": q_raw,
    }


def darboux_primitive() -> dict[str, sp.Expr]:
    raw = darboux_raw()
    content = content_of(raw["P_raw"], XY)
    q_content = content_of(raw["Q_raw"], XY)
    if content != 10 or q_content != 10:
        raise AssertionError(f"expected content 10, got {content}, {q_content}")
    p = sp.expand(raw["P_raw"] / 10)
    q = sp.expand(raw["Q_raw"] / 10)
    if sp.gcd(p, q) != 1:
        raise AssertionError("primitive components still share a factor")
    return {**raw, "P": p, "Q": q, "content": 10}


def jacobian(p, q, point: tuple[int, int]):
    j = sp.Matrix([[sp.diff(p, X), sp.diff(p, Y)], [sp.diff(q, X), sp.diff(q, Y)]])
    j = sp.simplify(j.subs({X: point[0], Y: point[1]}))
    return j


def dhdt_numerator(p, q) -> sp.Expr:
    raw = darboux_raw()
    # Cleared numerator of H_x P + H_y Q for H = A^5 / B^4.
    return sp.expand(
        (5 * raw["B"] * raw["Ax"] - 4 * raw["A"] * raw["Bx"]) * p
        + (5 * raw["B"] * raw["Ay"] - 4 * raw["A"] * raw["By"]) * q
    )


def check_darboux() -> dict[str, int]:
    data = darboux_primitive()
    require_equal(data["Ay"], 2 * Y, "A_y")
    require_equal(data["By"], 10 * X * Y, "B_y")
    require_equal(data["Ax"], 8 * X**3 - 2 * X - 2, "A_x")
    require_equal(data["Bx"], 40 * X**4 - 15 * X**2 + 5 * Y**2 - 20 * X - 5, "B_x")
    require_equal(data["P_raw"], 10 * Y * data["inner"], "P_raw = 10 y inner")
    if total_degree(data["inner"], XY) != 3:
        raise AssertionError("inner did not drop to degree 3")
    if total_degree(data["P"], XY) != 4 or total_degree(data["Q"], XY) != 4:
        raise AssertionError("primitive field is not degree 4")

    claimed_p = Y * (X**3 + 2 * X**2 - X * Y**2 - 3 * X + 4)
    claimed_q = (
        15 * X**4
        - 21 * X**3
        + 3 * X**2 * Y**2
        - 15 * X**2
        + 7 * X * Y**2
        - 11 * X
        - 2 * Y**4
        + 6 * Y**2
    )
    require_equal(data["P"], claimed_p, "primitive P")
    require_equal(data["Q"], claimed_q, "primitive Q")

    centers = ((0, 0), (1, 2), (1, -2))
    dets = []
    for pt in centers:
        if data["P"].subs({X: pt[0], Y: pt[1]}) != 0 or data["Q"].subs({X: pt[0], Y: pt[1]}) != 0:
            raise AssertionError(f"{pt} is not an equilibrium")
        j = jacobian(data["P"], data["Q"], pt)
        if j.trace() != 0:
            raise AssertionError(f"trace at {pt} is {j.trace()}")
        if j.det() <= 0:
            raise AssertionError(f"det at {pt} is {j.det()}")
        dets.append(int(j.det()))
    if dets != [44, 64, 64]:
        raise AssertionError(f"unexpected dets {dets}")
    j00 = jacobian(data["P"], data["Q"], (0, 0))
    j12 = jacobian(data["P"], data["Q"], (1, 2))
    require_equal(j00, sp.Matrix([[0, 4], [-11, 0]]), "J(0,0)")
    require_equal(j12, sp.Matrix([[0, -8], [8, 0]]), "J(1,2)")
    require_equal(jacobian(data["P"], data["Q"], (1, -2)), j12, "J(1,-2)")

    numer = dhdt_numerator(data["P"], data["Q"])
    require_zero(numer, "dH/dt numerator")
    # The same vanishing as a rational identity: H = A^5/B^4.
    h = data["A"] ** 5 / data["B"] ** 4
    dhdt = sp.together(sp.diff(h, X) * data["P"] + sp.diff(h, Y) * data["Q"])
    require_zero(sp.numer(sp.together(dhdt)), "rational dH/dt")

    p_bad = data["P"] + 1
    if dhdt_numerator(p_bad, data["Q"]) == 0:
        raise AssertionError("perturbed field unexpectedly had dH/dt = 0")

    return {
        "inner_degree": total_degree(data["inner"], XY),
        "P_terms": len(terms_of(data["P"], XY)),
        "Q_terms": len(terms_of(data["Q"], XY)),
        "P_degree": total_degree(data["P"], XY),
        "Q_degree": total_degree(data["Q"], XY),
        "content": 10,
        "dHdt_terms": len(terms_of(numer, XY)),
        "det00": dets[0],
        "det12": dets[1],
        "det1m2": dets[2],
    }


# ---------------------------------------------------------------------------
# Cubic system (20)
# ---------------------------------------------------------------------------


def cubic20() -> dict[str, sp.Expr]:
    h = -8 * X**4 - Y**4 - 4 * X**3 + 2 * X**2 + 2 * Y**2
    p = Y**3 - Y
    q = -8 * X**3 - 3 * X**2 + X
    return {"H": h, "P": p, "Q": q, "dHdt": sp.expand(sp.diff(h, X) * p + sp.diff(h, Y) * q)}


def check_cubic20() -> dict[str, int]:
    data = cubic20()
    require_zero(data["dHdt"], "cubic20 dH/dt")
    # Paper (20) is (1/4) of (-H_y, H_x).
    hx, hy = sp.diff(data["H"], X), sp.diff(data["H"], Y)
    require_equal(4 * data["P"], -hy, "4 P = -H_y")
    require_equal(4 * data["Q"], hx, "4 Q = H_x")
    j = jacobian(data["P"], data["Q"], (0, 0))
    if j.trace() != 0 or j.det() != 1:
        raise AssertionError(f"cubic20 origin type {j}")
    require_zero(data["P"].subs(Y, 0), "cubic20 P(t,0)")
    q_line = sp.expand(data["Q"].subs(Y, 0))
    require_equal(q_line, -T.subs(T, X) * (8 * X**2 + 3 * X - 1), "cubic20 Q(x,0)")
    # Use t as the univariate parameter.
    q_t = -T * (8 * T**2 + 3 * T - 1)
    require_equal(sp.discriminant(sp.Poly(8 * T**2 + 3 * T - 1, T)), 41, "disc 41")
    # Three distinct real roots: t = 0 and the two real quadratic roots.
    if q_t.subs(T, 0) != 0:
        raise AssertionError("t=0 is not a root")
    if (8 * T**2 + 3 * T - 1).subs(T, 0) == 0:
        raise AssertionError("quadratic shares the root 0")
    return {
        "dHdt_terms": len(terms_of(data["dHdt"], XY)),
        "origin_trace": 0,
        "origin_det": 1,
        "collinear": 3,
        "q_line_degree": int(sp.degree(q_t, T)),
    }


# ---------------------------------------------------------------------------
# Coppel identities
# ---------------------------------------------------------------------------


def generic_quadratic():
    p = A00 + A10 * X + A01 * Y + A20 * X**2 + A11 * X * Y + A02 * Y**2
    q = B00 + B10 * X + B01 * Y + B20 * X**2 + B11 * X * Y + B02 * Y**2
    return p, q


def line_restrictions() -> dict[str, sp.Expr]:
    p, q = generic_quadratic()
    return {
        "P_on_y0": sp.expand(p.subs({X: T, Y: 0})),
        "Q_on_y0": sp.expand(q.subs({X: T, Y: 0})),
    }


def vandermonde() -> dict[str, sp.Expr]:
    v = sp.Matrix([[1, T1, T1**2], [1, T2, T2**2], [1, T3, T3**2]])
    det = sp.expand(v.det())
    claimed = sp.expand(-(T1 - T2) * (T1 - T3) * (T2 - T3))
    adj = v.adjugate()
    ident = sp.expand(adj * v - v.det() * sp.eye(3))
    diffs = [ident[i, j] for i in range(3) for j in range(3)]
    return {"V": v, "det": det, "claimed_det": claimed, "diffs": diffs}


def sylvester_res_y(p, q) -> sp.Expr:
    """Resultant in y via the 4x4 Sylvester matrix of two quadratics."""
    py = sp.Poly(sp.expand(p), Y)
    qy = sp.Poly(sp.expand(q), Y)

    def coeff(poly, k):
        return sp.expand(poly.nth(k)) if poly.degree() >= k else 0

    p2, p1, p0 = coeff(py, 2), coeff(py, 1), coeff(py, 0)
    q2, q1, q0 = coeff(qy, 2), coeff(qy, 1), coeff(qy, 0)
    s = sp.Matrix(
        [
            [p2, p1, p0, 0],
            [0, p2, p1, p0],
            [q2, q1, q0, 0],
            [0, q2, q1, q0],
        ]
    )
    return sp.expand(s.det())


def shi_field():
    p = -Y - 10 * X**2 + 5 * X * Y + Y**2
    q = X + X**2 - 25 * X * Y
    return p, q


def check_coppel() -> dict[str, int]:
    line = line_restrictions()
    require_equal(line["P_on_y0"], A00 + A10 * T + A20 * T**2, "P(t,0)")
    require_equal(line["Q_on_y0"], B00 + B10 * T + B20 * T**2, "Q(t,0)")
    if int(sp.degree(line["P_on_y0"], T)) != 2:
        raise AssertionError("generic P(t,0) is not degree 2")
    if int(sp.degree(line["Q_on_y0"], T)) != 2:
        raise AssertionError("generic Q(t,0) is not degree 2")

    van = vandermonde()
    require_equal(van["det"], van["claimed_det"], "Vandermonde det")
    for i, diff in enumerate(van["diffs"]):
        require_zero(diff, f"vandermonde adj V - det I entry {i}")

    # Three marked roots 0, 1, 2: the inverse identity is integral.
    # f(t) = c0 + c1 t + c2 t^2, V at (0,1,2) has det 2.
    c0, c1, c2 = sp.symbols("c0 c1 c2")
    f = c0 + c1 * T + c2 * T**2
    vals = sp.Matrix([f.subs(T, 0), f.subs(T, 1), f.subs(T, 2)])
    v012 = sp.Matrix([[1, 0, 0], [1, 1, 1], [1, 2, 4]])
    ident012 = sp.expand(v012.adjugate() * vals - v012.det() * sp.Matrix([c0, c1, c2]))
    for i, entry in enumerate(ident012):
        require_zero(entry, f"sample Vandermonde 0,1,2 entry {i}")

    p, q = generic_quadratic()
    res = sylvester_res_y(p, q)
    res_sympy = sp.expand(sp.resultant(p, q, Y))
    require_equal(res, res_sympy, "Sylvester vs sympy resultant")
    if int(sp.degree(res, X)) != 4:
        raise AssertionError(f"generic Res_y degree {sp.degree(res, X)}")

    shi_p, shi_q = shi_field()
    shi_res = sylvester_res_y(shi_p, shi_q)
    require_equal(shi_res, -6124 * X**4 + 102 * X**3 - 24 * X**2, "Shi Res_y")
    require_equal(shi_res, sp.expand(sp.resultant(shi_p, shi_q, Y)), "Shi sympy Res_y")
    require_zero(shi_p.subs({X: 0, Y: 0}), "Shi P(0,0)")
    require_zero(shi_q.subs({X: 0, Y: 0}), "Shi Q(0,0)")
    require_zero(shi_p.subs({X: 0, Y: 1}), "Shi P(0,1)")
    require_zero(shi_q.subs({X: 0, Y: 1}), "Shi Q(0,1)")
    # Remaining real x: 6124 x^2 - 102 x + 24 has negative discriminant.
    quad = 6124 * X**2 - 102 * X + 24
    require_equal(sp.expand(-2 * X**2 * (3062 * X**2 - 51 * X + 12)), shi_res, "Shi factor")
    disc = int(sp.discriminant(sp.Poly(quad, X)))
    if disc != -577500:
        raise AssertionError(f"Shi leftover disc {disc}")
    if disc >= 0:
        raise AssertionError("Shi leftover quadratic is not definite")
    # No third real finite equilibrium: resultant in x likewise.
    shi_res_x = sp.expand(sp.resultant(shi_p, shi_q, X))
    require_equal(shi_res_x, -6124 * Y**4 + 6618 * Y**3 - 504 * Y**2 + 10 * Y, "Shi Res_x")

    return {
        "line_P_degree": 2,
        "line_Q_degree": 2,
        "vandermonde_diffs": 0,
        "shi_real": 2,
        "shi_res_degree": int(sp.degree(shi_res, X)),
        "generic_res_degree": int(sp.degree(res, X)),
        "generic_res_terms": len(terms_of(res, RES_VARS)),
        "shi_disc": disc,
    }


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------


def build_certificate() -> dict:
    data = darboux_primitive()
    numer = dhdt_numerator(data["P"], data["Q"])
    c20 = cubic20()
    line = line_restrictions()
    van = vandermonde()
    p, q = generic_quadratic()
    res = sylvester_res_y(p, q)
    shi_p, shi_q = shi_field()
    shi_res = sylvester_res_y(shi_p, shi_q)
    return {
        "schema": "hilbert16-q-pt-darboux/v1",
        "claim": (
            "unperturbed PT Darboux field of degree 4 with three linear "
            "centers and dH/dt = 0; quadratic line-restriction and "
            "Vandermonde identities; Shi has two real finite equilibria"
        ),
        "darboux": {
            "variables": ["x", "y"],
            "A": terms_of(data["A"], XY),
            "B": terms_of(data["B"], XY),
            "inner": terms_of(data["inner"], XY),
            "P_raw": terms_of(data["P_raw"], XY),
            "Q_raw": terms_of(data["Q_raw"], XY),
            "P": terms_of(data["P"], XY),
            "Q": terms_of(data["Q"], XY),
            "dHdt_numer": terms_of(numer, XY),
            "content": 10,
            "deg_P": 4,
            "deg_Q": 4,
        },
        "centers": {
            "points": [[0, 0], [1, 2], [1, -2]],
            "traces": [0, 0, 0],
            "dets": [44, 64, 64],
        },
        "cubic20": {
            "variables": ["x", "y"],
            "H": terms_of(c20["H"], XY),
            "P": terms_of(c20["P"], XY),
            "Q": terms_of(c20["Q"], XY),
            "dHdt": terms_of(c20["dHdt"], XY),
            "origin_trace": 0,
            "origin_det": 1,
            "collinear_equilibria": 3,
        },
        "line": {
            "variables": ["t", "a00", "a10", "a20", "b00", "b10", "b20"],
            "P_on_y0": terms_of(line["P_on_y0"], LINE_VARS),
            "Q_on_y0": terms_of(line["Q_on_y0"], LINE_VARS),
            "deg_P": 2,
            "deg_Q": 2,
        },
        "vandermonde": {
            "variables": ["t1", "t2", "t3"],
            "det": terms_of(van["det"], VANDER_VARS),
            "claimed_det": terms_of(van["claimed_det"], VANDER_VARS),
        },
        "shi": {
            "variables": ["x", "y"],
            "P": terms_of(shi_p, XY),
            "Q": terms_of(shi_q, XY),
            "res_y": terms_of(shi_res, SHI_RES_VARS),
            "real_equilibria": [[0, 0], [0, 1]],
            "leftover_discriminant": -577500,
        },
        "resultant": {
            "variables": [str(v) for v in RES_VARS],
            "res_y": terms_of(res, RES_VARS),
            "deg_x": 4,
        },
    }


def check_certificate(payload: dict) -> None:
    data = darboux_primitive()
    block = payload["darboux"]
    require_terms(XY, block["A"], data["A"], "cert A")
    require_terms(XY, block["B"], data["B"], "cert B")
    require_terms(XY, block["inner"], data["inner"], "cert inner")
    require_terms(XY, block["P"], data["P"], "cert P")
    require_terms(XY, block["Q"], data["Q"], "cert Q")
    require_terms(XY, block["P_raw"], data["P_raw"], "cert P_raw")
    require_terms(XY, block["Q_raw"], data["Q_raw"], "cert Q_raw")
    require_terms(XY, block["dHdt_numer"], 0, "cert dHdt")
    if block["content"] != 10 or block["deg_P"] != 4 or block["deg_Q"] != 4:
        raise AssertionError("darboux metadata mismatch")
    if payload["centers"]["dets"] != [44, 64, 64]:
        raise AssertionError("center dets mismatch")
    if payload["centers"]["traces"] != [0, 0, 0]:
        raise AssertionError("center traces mismatch")

    c20 = cubic20()
    cblock = payload["cubic20"]
    require_terms(XY, cblock["H"], c20["H"], "cert cubic H")
    require_terms(XY, cblock["P"], c20["P"], "cert cubic P")
    require_terms(XY, cblock["Q"], c20["Q"], "cert cubic Q")
    require_terms(XY, cblock["dHdt"], 0, "cert cubic dHdt")
    if cblock["collinear_equilibria"] != 3:
        raise AssertionError("cubic collinear count")

    line = line_restrictions()
    lblock = payload["line"]
    require_terms(LINE_VARS, lblock["P_on_y0"], line["P_on_y0"], "cert P(t,0)")
    require_terms(LINE_VARS, lblock["Q_on_y0"], line["Q_on_y0"], "cert Q(t,0)")

    van = vandermonde()
    vblock = payload["vandermonde"]
    require_terms(VANDER_VARS, vblock["det"], van["det"], "cert vandermonde det")
    require_terms(VANDER_VARS, vblock["claimed_det"], van["claimed_det"], "cert claimed det")

    shi_p, shi_q = shi_field()
    sblock = payload["shi"]
    require_terms(XY, sblock["P"], shi_p, "cert Shi P")
    require_terms(XY, sblock["Q"], shi_q, "cert Shi Q")
    require_terms(SHI_RES_VARS, sblock["res_y"], sylvester_res_y(shi_p, shi_q), "cert Shi res")
    if sblock["leftover_discriminant"] != -577500:
        raise AssertionError("Shi disc")

    p, q = generic_quadratic()
    rblock = payload["resultant"]
    require_terms(RES_VARS, rblock["res_y"], sylvester_res_y(p, q), "cert generic res")
    if rblock["deg_x"] != 4:
        raise AssertionError("generic res degree")


def dump_lines(darboux: dict[str, int], cubic: dict[str, int], coppel: dict[str, int]) -> list[str]:
    return [
        f"darboux inner degree {darboux['inner_degree']}",
        f"darboux primitive P terms {darboux['P_terms']} degree {darboux['P_degree']}",
        f"darboux primitive Q terms {darboux['Q_terms']} degree {darboux['Q_degree']}",
        f"darboux content {darboux['content']}",
        f"darboux dHdt numer terms {darboux['dHdt_terms']}",
        (
            f"centers traces 0 0 0 dets {darboux['det00']} "
            f"{darboux['det12']} {darboux['det1m2']}"
        ),
        f"cubic20 dHdt terms {cubic['dHdt_terms']}",
        f"cubic20 origin trace {cubic['origin_trace']} det {cubic['origin_det']}",
        f"line P(t,0) degree {coppel['line_P_degree']}",
        f"line Q(t,0) degree {coppel['line_Q_degree']}",
        f"vandermonde diffs {coppel['vandermonde_diffs']}",
        f"shi real equilibria {coppel['shi_real']}",
        f"shi res_y degree {coppel['shi_res_degree']}",
        f"generic res_y degree {coppel['generic_res_degree']}",
        f"cubic20 collinear equilibria {cubic['collinear']}",
        "negative perturbation rejected",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    darboux = check_darboux()
    cubic = check_cubic20()
    coppel = check_coppel()
    payload = build_certificate()
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

    lines = dump_lines(darboux, cubic, coppel)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID pt-darboux identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
