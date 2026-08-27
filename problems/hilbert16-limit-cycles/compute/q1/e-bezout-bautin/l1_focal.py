#!/usr/bin/env python3
"""First Lyapunov quantity of a quadratic focus, derived two ways.

Normal form

    ẋ = −y + a20 x² + a11 x y + a02 y²
    ẏ =  x + b20 x² + b11 x y + b02 y²

The primitive integer polynomial is

    L1 = (a20 + a02) a11 − (b20 + b02) b11 − 2 a20 b20 + 2 a02 b02.

Polar averaging of the return map gives a3(2π) = (π/4) L1.
The Poincaré–Lyapunov function F = r²/2 + F3 + F4 + ⋯ with
dF/dt = V1 r^4 + V2 r^6 + ⋯ gives V1 = L1/8.

The same L1 equals w1 = A α − B β of Llibre–Valls, Electron. J.
Differ. Equ. 2025, no. 36, Theorem 2.2 (opened; their display
drops the y in a11 x y / b11 x y, but the combinations
A = a20+a02, α = a11+2 b02, B = b20+b02, β = b11+2 a20 are the
standard ones and expand to L1).

L2 is computed as V2 in the same Poincaré function (gauge: the
x^4 coefficient of F4 and the x^6 coefficient of F6 are set to
zero). V2 vanishes on the Hamiltonian, reversible, holomorphic,
and Shi-unperturbed families. This is not a proof that
L1 = L2 = L3 = 0 implies a center.

Replay: python3 l1_focal.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
A20, A11, A02, B20, B11, B02 = sp.symbols("a20 a11 a02 b20 b11 b02")
COEFFS = (A20, A11, A02, B20, B11, B02)
L1_PRIMITIVE = (A20 + A02) * A11 - (B20 + B02) * B11 - 2 * A20 * B20 + 2 * A02 * B02


def l1_eval(a20, a11, a02, b20, b11, b02) -> int:
    return int(
        (a20 + a02) * a11
        - (b20 + b02) * b11
        - 2 * a20 * b20
        + 2 * a02 * b02
    )


def _to_exp(expr, th):
    return sp.expand(expr.rewrite(sp.exp))


def _integrate_from_0(expr, th):
    """Antiderivative of a finite Fourier series in exp(i k θ), vanishing at 0."""
    expr = sp.expand(expr)
    if expr == 0:
        return 0
    I = sp.I
    acc = 0
    terms = expr.as_ordered_terms() if expr.is_Add else [expr]
    for term in terms:
        term = sp.expand(term)
        exps = [e for e in term.atoms(sp.exp) if th in e.free_symbols]
        if not exps:
            acc += term * th
            continue
        e = exps[0]
        k = sp.simplify(sp.expand(e.args[0] / (I * th)))
        coeff = term / e
        if k == 0:
            acc += coeff * th
        else:
            acc += coeff * (e - 1) / (I * k)
    return sp.expand(acc)


def _integrate_0_2pi(expr, th):
    expr = sp.expand(expr)
    if expr == 0:
        return 0
    I = sp.I
    total = 0
    two_pi = 2 * sp.pi
    terms = expr.as_ordered_terms() if expr.is_Add else [expr]
    for term in terms:
        term = sp.expand(term)
        exps = [e for e in term.atoms(sp.exp) if th in e.free_symbols]
        if not exps:
            total += term * two_pi
            continue
        e = exps[0]
        k = sp.simplify(sp.expand(e.args[0] / (I * th)))
        coeff = term / e
        if k == 0:
            total += coeff * two_pi
    return sp.simplify(total)


def derive_l1_polar():
    """Return map r ↦ r + a3(2π) r³ + ⋯ with a3(2π) = (π/4) L1."""
    th = sp.symbols("theta", real=True)
    c, s = sp.cos(th), sp.sin(th)
    p2 = A20 * c**2 + A11 * c * s + A02 * s**2
    q2 = B20 * c**2 + B11 * c * s + B02 * s**2
    r_rad = sp.expand(p2 * c + q2 * s)
    s_ang = sp.expand(-p2 * s + q2 * c)
    r_e, s_e = _to_exp(r_rad, th), _to_exp(s_ang, th)
    a2 = _integrate_from_0(r_e, th)
    integrand = sp.expand(2 * r_e * a2 - r_e * s_e)
    a3 = _integrate_0_2pi(integrand, th)
    a3 = sp.simplify(sp.expand(a3))
    ratio = sp.simplify(a3 / L1_PRIMITIVE)
    return a3, ratio


def lie(F, field, x, y):
    return sp.diff(F, x) * field[0] + sp.diff(F, y) * field[1]


def hom_poly(deg, name, x, y):
    coeffs = []
    expr = 0
    for i in range(deg + 1):
        c = sp.symbols(f"{name}_{i}{deg - i}")
        coeffs.append(c)
        expr += c * x**i * y ** (deg - i)
    return expr, coeffs


def derive_v1_v2_poincare():
    """Poincaré–Lyapunov function through order 6. Returns (V1, V2)."""
    x, y = sp.symbols("x y")
    p2 = A20 * x**2 + A11 * x * y + A02 * y**2
    q2 = B20 * x**2 + B11 * x * y + B02 * y**2
    x1 = (-y, x)
    x2 = (p2, q2)
    f2 = (x**2 + y**2) / 2

    f3, c3 = hom_poly(3, "f3", x, y)
    eq3 = sp.expand(lie(f3, x1, x, y) + lie(f2, x2, x, y))
    sys3 = [eq3.coeff(x, i).coeff(y, 3 - i) for i in range(4)]
    f3s = sp.expand(f3.subs(sp.solve(sys3, c3)))

    f4, c4 = hom_poly(4, "f4", x, y)
    v1 = sp.symbols("V1")
    eq4 = sp.expand(
        lie(f4, x1, x, y) + lie(f3s, x2, x, y) - v1 * (x**2 + y**2) ** 2
    )
    sys4 = [eq4.coeff(x, i).coeff(y, 4 - i) for i in range(5)] + [c4[0]]
    sol4 = sp.solve(sys4, c4 + [v1], dict=True)[0]
    f4s = sp.expand(f4.subs(sol4))
    v1s = sp.factor(sol4[v1])

    f5, c5 = hom_poly(5, "f5", x, y)
    eq5 = sp.expand(lie(f5, x1, x, y) + lie(f4s, x2, x, y))
    sys5 = [eq5.coeff(x, i).coeff(y, 5 - i) for i in range(6)]
    f5s = sp.expand(f5.subs(sp.solve(sys5, c5)))

    f6, c6 = hom_poly(6, "f6", x, y)
    v2 = sp.symbols("V2")
    eq6 = sp.expand(
        lie(f6, x1, x, y) + lie(f5s, x2, x, y) - v2 * (x**2 + y**2) ** 3
    )
    sys6 = [eq6.coeff(x, i).coeff(y, 6 - i) for i in range(7)] + [c6[0]]
    sol6 = sp.solve(sys6, c6 + [v2], dict=True)[0]
    v2s = sp.expand(sol6[v2])
    return v1s, v2s


def llibre_w1():
    A = A20 + A02
    B = B20 + B02
    alpha = A11 + 2 * B02
    beta = B11 + 2 * A20
    return sp.expand(A * alpha - B * beta)


def monomial_dict(expr):
    expr = sp.expand(expr)
    poly = sp.Poly(expr, COEFFS, domain=sp.ZZ)
    out = []
    for monom, coeff in poly.terms():
        parts = []
        for s, e in zip(COEFFS, monom):
            if e == 1:
                parts.append(str(s))
            elif e > 1:
                parts.append(f"{s}**{e}")
        parts.sort()
        name = "*".join(parts) if parts else "1"
        out.append({"term": name, "coeff": int(coeff), "exponents": list(monom)})
    out.sort(key=lambda r: r["term"])
    return out


def center_families():
    """Named coefficient 6-tuples and the expected L1 (always 0 for centers)."""
    families = []

    # Hamiltonian: div = 0 ⇔ a11 = −2 b02, b11 = −2 a20.
    # Parameterised by a cubic H = (x²+y²)/2 + A x³ + B x²y + C xy² + D y³
    # with ẋ = −∂H/∂y, ẏ = ∂H/∂x.
    for A, B, C, D in ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (1, -2, 3, -1)):
        a20, a11, a02 = -B, -2 * C, -3 * D
        b20, b11, b02 = 3 * A, 2 * B, C
        families.append(
            {
                "name": f"hamiltonian_A{A}_B{B}_C{C}_D{D}",
                "kind": "hamiltonian",
                "coeffs": [a20, a11, a02, b20, b11, b02],
                "expect_L1": 0,
                "expect_V2_zero": True,
            }
        )

    # Reversible under (x, y, t) ↦ (−x, y, −t): P even in x, Q odd in x.
    families.append(
        {
            "name": "reversible_yaxis",
            "kind": "reversible",
            "coeffs": [2, 0, -3, 0, 7, 0],  # a11=b20=b02=0
            "expect_L1": 0,
            "expect_V2_zero": True,
        }
    )

    # Holomorphic ẋ+iẏ = i z + α z².
    for alpha in (1, -2, 5):
        families.append(
            {
                "name": f"holomorphic_alpha{alpha}",
                "kind": "holomorphic",
                "coeffs": [alpha, 0, -alpha, 0, 2 * alpha, 0],
                "expect_L1": 0,
                "expect_V2_zero": True,
            }
        )

    # Shi unperturbed, Yu–Zhang transcription of Sci. Sinica 23 (1980):
    # ẋ = −y −10 x² + 5 x y + y²,  ẏ = x + x² − 25 x y.
    families.append(
        {
            "name": "shi_unperturbed",
            "kind": "shi",
            "coeffs": [-10, 5, 1, 1, -25, 0],
            "expect_L1": 0,
            "expect_V2_zero": True,
            "note": "order-3 weak focus; L1=L2=0, L3 not computed here",
        }
    )

    # Generic first-order weak focus (not a center).
    families.append(
        {
            "name": "generic_focus_a20_b20",
            "kind": "focus",
            "coeffs": [1, 0, 0, 1, 0, 0],
            "expect_L1": -2,
            "expect_V2_zero": False,
        }
    )
    return families


def run_tests(v1, v2):
    tests = []
    for fam in center_families():
        subs = dict(zip(COEFFS, fam["coeffs"]))
        L1v = int(sp.Integer(L1_PRIMITIVE.subs(subs)))
        V1v = sp.simplify(v1.subs(subs))
        V2v = sp.expand(v2.subs(subs))
        w1v = int(sp.Integer(llibre_w1().subs(subs)))
        ok_l1 = L1v == fam["expect_L1"]
        ok_v1 = sp.simplify(V1v - sp.Rational(1, 8) * L1v) == 0
        ok_w1 = w1v == L1v
        ok_v2 = True
        if fam["expect_V2_zero"]:
            ok_v2 = V2v == 0
        tests.append(
            {
                "name": fam["name"],
                "kind": fam["kind"],
                "coeffs": fam["coeffs"],
                "L1": L1v,
                "V1": str(V1v),
                "V2": str(V2v),
                "w1": w1v,
                "ok_L1": ok_l1,
                "ok_V1": bool(ok_v1),
                "ok_w1": ok_w1,
                "ok_V2": bool(ok_v2),
                "ok": bool(ok_l1 and ok_v1 and ok_w1 and ok_v2),
            }
        )
    return tests


def run():
    a3, polar_ratio = derive_l1_polar()
    v1, v2 = derive_v1_v2_poincare()
    v1_ratio = sp.simplify(v1 / L1_PRIMITIVE)
    w1 = llibre_w1()
    w1_diff = sp.expand(w1 - L1_PRIMITIVE)
    tests = run_tests(v1, v2)
    failed = [t for t in tests if not t["ok"]]
    data = {
        "normal_form": (
            "dx/dt = -y + a20 x^2 + a11 x y + a02 y^2; "
            "dy/dt = x + b20 x^2 + b11 x y + b02 y^2"
        ),
        "L1_primitive": str(sp.expand(L1_PRIMITIVE)),
        "L1_monomials": monomial_dict(L1_PRIMITIVE),
        "polar_a3_2pi": str(a3),
        "polar_a3_over_L1": str(polar_ratio),
        "V1": str(v1),
        "V1_over_L1": str(v1_ratio),
        "V2": str(v2),
        "llibre_valls_w1": str(w1),
        "w1_minus_L1": str(w1_diff),
        "sources_opened": [
            "https://arxiv.org/abs/2604.12883",
            "https://arxiv.org/html/2604.12883v1",
            "https://ejde.math.txstate.edu/Volumes/2025/36/abstr.html",
            "https://ejde.math.txstate.edu/Volumes/2025/36/llibre.pdf",
            "https://publish.uwo.ca/~pyu/pub/preprints/YZ_IJBC2020.pdf",
        ],
        "scope": (
            "L1 kept. L2 kept as an independently computed V2 that "
            "vanishes on the listed center / Shi families. Full Bautin "
            "ideal L1=L2=L3=0 ⇒ center is dropped."
        ),
        "failed_tests": len(failed),
    }
    return data, tests, failed, v1, v2


def dump_lines(data: dict, tests: list[dict]) -> list[str]:
    lines = []
    for mon in data["L1_monomials"]:
        lines.append(f"L1 {mon['term']} {mon['coeff']}")
    lines.append(f"polar_ratio {data['polar_a3_over_L1']}")
    lines.append(f"V1_ratio {data['V1_over_L1']}")
    lines.append(f"w1_minus_L1 {data['w1_minus_L1']}")
    for t in tests:
        lines.append(f"center {t['name']} L1={t['L1']} ok={int(t['ok'])}")
    lines.append(f"l1_failed {data['failed_tests']}")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=HERE / "l1_polynomial.json")
    ap.add_argument("--tests", type=Path, default=HERE / "center_family_tests.json")
    ap.add_argument("--dump", type=Path, default=None)
    args = ap.parse_args()
    data, tests, failed, _v1, _v2 = run()
    args.json.write_text(json.dumps(data, indent=2) + "\n")
    args.tests.write_text(json.dumps({"tests": tests}, indent=2) + "\n")
    lines = dump_lines(data, tests)
    if args.dump:
        args.dump.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if failed:
        raise SystemExit(f"L1/L2 tests failed: {[t['name'] for t in failed]}")
    if data["polar_a3_over_L1"] != "pi/4":
        raise SystemExit(f"unexpected polar ratio {data['polar_a3_over_L1']}")
    if data["V1_over_L1"] != "1/8":
        raise SystemExit(f"unexpected V1 ratio {data['V1_over_L1']}")
    if data["w1_minus_L1"] != "0":
        raise SystemExit("Llibre–Valls w1 is not L1")
    print(f"wrote {args.json} and {args.tests}")


if __name__ == "__main__":
    main()
