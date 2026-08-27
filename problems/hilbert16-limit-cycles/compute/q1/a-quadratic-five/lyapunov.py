#!/usr/bin/env python3
"""Poincaré–Lyapunov quantities of the unperturbed Shi field.

Gauge (same pin as line E, `l1_focal.py`): the y^n coefficient of
each homogeneous F_n is set to 0 when n is even. The identity is

    dF/dt = V1 (x²+y²)² + V2 (x²+y²)³ + V3 (x²+y²)⁴ + O(9)

On the unperturbed Shi field this produces the exact rationals

    V1 = 0,   V2 = 0,   V3 = 35625/8 ≠ 0

so the origin is a weak focus of order 3. Writes `cert.json` and
`f_coeffs.txt`.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from field import (
    X,
    Y,
    five_cycle_obstructions,
    li_chengzhi,
    origin_linear_type,
    rat,
    second_focus_linear_type,
    shi_field,
    unperturbed_equilibria,
)

HERE = Path(__file__).resolve().parent


def lie(F, field, x=X, y=Y):
    return sp.diff(F, x) * field[0] + sp.diff(F, y) * field[1]


def hom_poly(deg: int, name: str, x=X, y=Y):
    coeffs = []
    expr = 0
    for i in range(deg + 1):
        c = sp.symbols(f"{name}_{i}_{deg - i}")
        coeffs.append(c)
        expr += c * x**i * y ** (deg - i)
    return expr, coeffs


def monomials(expr, deg: int) -> list[dict]:
    poly = sp.Poly(sp.expand(expr), X, Y, domain=sp.QQ)
    out = []
    for i in range(deg + 1):
        j = deg - i
        c = poly.coeff_monomial(X**i * Y**j)
        num, den = sp.fraction(sp.together(c))
        out.append(
            {
                "i": i,
                "j": j,
                "num": int(num),
                "den": int(den),
            }
        )
    return out


def construct(p2, q2, upto: int = 3):
    """Return F_parts (dict degree -> poly) and [V1, …, V_upto]."""
    x1 = (-Y, X)
    x2 = (p2, q2)
    parts = {2: (X**2 + Y**2) / 2}
    last = parts[2]
    Vs = []
    max_n = 2 * upto + 2
    for n in range(3, max_n + 1):
        fn, cn = hom_poly(n, f"f{n}")
        if n % 2 == 0:
            v = sp.symbols(f"V{n // 2 - 1}")
            eq = sp.expand(
                lie(fn, x1) + lie(last, x2) - v * (X**2 + Y**2) ** (n // 2)
            )
            sys = [eq.coeff(X, i).coeff(Y, n - i) for i in range(n + 1)] + [
                cn[0]
            ]
            sol = sp.solve(sys, cn + [v], dict=True)[0]
            fns = sp.expand(fn.subs(sol))
            vs = sp.together(sol[v])
            Vs.append(vs)
        else:
            eq = sp.expand(lie(fn, x1) + lie(last, x2))
            sys = [eq.coeff(X, i).coeff(Y, n - i) for i in range(n + 1)]
            sol = sp.solve(sys, cn, dict=True)[0]
            fns = sp.expand(fn.subs(sol))
        parts[n] = fns
        last = fns
    return parts, Vs


def write_f_coeffs(path: Path, parts: dict, Vs: list) -> None:
    lines = [
        "# Poincaré–Lyapunov F of unperturbed Shi, gauge y^n = 0 on even F_n.",
        "# rows: F <deg> <i> <j> <num> <den>   meaning [x^i y^j] F_deg = num/den",
        "# rows: V <k> <num> <den>             V_k in dF/dt = V_k r^{2k+2} + …",
    ]
    for deg in sorted(parts):
        for mon in monomials(parts[deg], deg):
            lines.append(
                f"F {deg} {mon['i']} {mon['j']} {mon['num']} {mon['den']}"
            )
    for k, v in enumerate(Vs, 1):
        num, den = sp.fraction(sp.together(v))
        lines.append(f"V {k} {int(num)} {int(den)}")
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    P, Q = shi_field(0, 0, 0, 0)
    p2 = sp.expand(P + Y)
    q2 = sp.expand(Q - X)
    parts, Vs = construct(p2, q2, upto=3)
    assert Vs[0] == 0 and Vs[1] == 0
    assert sp.together(Vs[2]) == sp.Rational(35625, 8)

    Fall = sum(parts[k] for k in range(2, 9))
    dF = sp.expand(lie(Fall, (P, Q)))
    r2 = X**2 + Y**2
    target = Vs[2] * r2**4
    rem = sp.expand(dF - target)
    low = sum(
        rem.coeff(X, i).coeff(Y, j) * X**i * Y**j
        for i in range(9)
        for j in range(9 - i)
    )
    assert sp.expand(low) == 0

    li = li_chengzhi(-10, 5, 1, 1, -25)
    assert li[0] == 0 and li[1] == 0 and li[2] == 57000
    ratio = sp.Rational(57000) / sp.Rational(35625, 8)
    assert ratio == sp.Rational(64, 5)

    F_dump = {str(deg): monomials(parts[deg], deg) for deg in sorted(parts)}
    cert = {
        "line": "a-quadratic-five",
        "imagined_claim": (
            "An explicit quadratic, a perturbation of Shi Songling 1980 "
            "with an extra μ y² term, has five isolated periodic orbits, "
            "hence H(2) ≥ 5."
        ),
        "status": "dropped",
        "fork": (
            "Unperturbed Shi (λ = ε = δ = μ = 0) has a weak focus of "
            "order 3 at the origin, V1 = V2 = 0, V3 = 35625/8, and a "
            "strong unstable focus at (0, 1) with charpoly t^2 - 5 t + 24."
        ),
        "published_Hn_moved": False,
        "dropped_claim": "H(2) >= 5",
        "proved": {
            "system": {
                "P": "-y - 10 x^2 + 5 x y + y^2",
                "Q": "x + x^2 - 25 x y",
                "parameters": {"lambda": 0, "epsilon": 0, "delta": 0, "mu": 0},
            },
            "normalization": {
                "F2": "(x^2 + y^2)/2",
                "identity": "dF/dt = V1 r^4 + V2 r^6 + V3 r^8 + O(9)",
                "gauge": "y^n coefficient of even F_n is 0",
            },
            "V1": rat(0),
            "V2": rat(0),
            "V3": rat(35625, 8),
            "weak_focus_order": 3,
            "li_chengzhi_crosscheck": {
                "L1": 0,
                "L2": 0,
                "L3": 57000,
                "L3_over_V3": "64/5",
                "source": (
                    "Li Chengzhi, as quoted by Llibre–Schlomiuk, "
                    "Canad. J. Math. 56 (2004), after Proposition 2."
                ),
            },
            "origin": origin_linear_type(),
            "second_focus": second_focus_linear_type(),
            "equilibria": unperturbed_equilibria(),
            "F": F_dump,
        },
        "five_cycle": five_cycle_obstructions(),
        "annulus": {
            "status": "residue",
            "tried": (
                "Euclidean circles and axis-aligned ellipses about (0, 1); "
                "linear-order circles already change sign (amp^2 = 554 > 25)."
            ),
            "certificate": None,
        },
    }

    (HERE / "cert.json").write_text(json.dumps(cert, indent=2) + "\n")
    write_f_coeffs(HERE / "f_coeffs.txt", parts, Vs)
    print("wrote cert.json and f_coeffs.txt")
    print("V1 = 0, V2 = 0, V3 = 35625/8")
    print("second focus (0, 1): strong unstable, t^2 - 5 t + 24")


if __name__ == "__main__":
    main()
