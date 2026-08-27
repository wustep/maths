#!/usr/bin/env python3
"""Exact lemmas for classical van der Pol, a cubic planar field.

Imagined end-state B was an explicit cubic with 14 isolated periodic
orbits. This file does not construct 14 cycles and does not claim
H(3) >= 14. It forks to a different explicit cubic (not the radial
family) and checks the algebraic hypotheses of Liénard's uniqueness
theorem, plus a closed-form Abelian integral with exactly one
positive simple zero.

Replay: python3 verify.py --write certificate.json
        python3 verify.py --check certificate.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificate.json"

x, y, h, theta = sp.symbols("x y h theta", real=True)
mu = sp.symbols("mu", real=True, positive=True)


def field():
    """Classical van der Pol: ẋ=y, ẏ=-x-μ(x²-1)y."""
    p = y
    q = -x - mu * (x**2 - 1) * y
    return p, q


def as_xy_poly(expr: sp.Expr) -> sp.Poly:
    return sp.Poly(sp.expand(expr), x, y)


def check_degree(p, q) -> dict:
    deg_p = as_xy_poly(p).total_degree()
    deg_q = as_xy_poly(q).total_degree()
    deg = max(deg_p, deg_q)
    if deg != 3:
        raise AssertionError(f"expected a cubic field, got degrees {(deg_p, deg_q)}")
    return {"deg_P": int(deg_p), "deg_Q": int(deg_q), "degree": int(deg)}


def check_unique_equilibrium(p, q) -> dict:
    sols = sp.solve([p, q], [x, y], dict=True)
    pts = [(sol[x], sol[y]) for sol in sols]
    if pts != [(sp.Integer(0), sp.Integer(0))]:
        raise AssertionError(f"expected unique equilibrium at origin, got {pts}")
    jac = sp.Matrix([[sp.diff(p, x), sp.diff(p, y)], [sp.diff(q, x), sp.diff(q, y)]])
    j0 = sp.simplify(jac.subs({x: 0, y: 0}))
    expected = sp.Matrix([[0, 1], [-1, mu]])
    if j0 != expected:
        raise AssertionError(f"Jacobian at 0 is {j0}, expected {expected}")
    trace = sp.simplify(j0.trace())
    det = sp.simplify(j0.det())
    if trace != mu or det != 1:
        raise AssertionError("linearization at 0 should have trace μ and det 1")
    # λ² − μλ + 1. Trace μ>0 and det>0 ⇒ source (focus if μ<2, node if μ≥2).
    return {
        "unique_equilibrium": [0, 0],
        "jacobian_at_0": [["0", "1"], ["-1", "mu"]],
        "trace_at_0": "mu",
        "det_at_0": "1",
        "charpoly_lambda": "lambda**2 - mu*lambda + 1",
        "origin_is_source": True,
    }


def lienard_data(p, q) -> dict:
    """Convert ẋ=y, ẏ=-g(x)-f(x)y into Liénard form ẋ=Y-F(x), Ẏ=-g(x)."""
    if p != y:
        raise AssertionError("expected P = y")
    # Q + x must be -f(x) y, with f independent of y.
    remainder = sp.expand(q + x)
    f = -sp.together(remainder / y)
    if sp.simplify(remainder + f * y) != 0:
        raise AssertionError("Q is not of Liénard shape -x - f(x) y")
    if f.has(y):
        raise AssertionError("f depends on y")
    g = x
    F = sp.simplify(sp.integrate(f, x))
    if F.subs(x, 0) != 0:
        F = sp.simplify(F - F.subs(x, 0))
    expected_f = mu * (x**2 - 1)
    expected_F = mu * (x**3 / 3 - x)
    if sp.simplify(f - expected_f) != 0 or sp.simplify(F - expected_F) != 0:
        raise AssertionError(f"unexpected f={f}, F={F}")
    # ẋ = Y - F(x), Ẏ = -x recovers the original field on Y = y + F(x).
    Y = y + F
    xdot = sp.simplify(Y - F)
    Ydot = sp.simplify(q + f * p)
    if xdot != y or sp.simplify(Ydot + g) != 0:
        raise AssertionError("Liénard coordinate change failed")
    return {"f": f, "F": F, "g": g, "Y": Y}


def check_lienard_hypotheses(data: dict) -> dict:
    """Algebraic hypotheses of the classical Liénard uniqueness theorem.

    Theorem (Liénard). Let F be C¹ and odd. If there is a>0 such that
    F(x)<0 on (0,a), F(x)>0 on (a,∞), F'(x)>0 on [a,∞), and F(x)→∞ as
    x→∞, then ẋ=y-F(x), ẏ=-x has exactly one periodic orbit, and that
    orbit is asymptotically stable. (If also F'(0)<0 then the origin
    is a source; existence of the orbit is part of the same theorem.)

    This function checks the hypotheses for F(x)=μ(x³/3-x), μ>0. It
    does not re-prove the geometric comparison that finishes the
    theorem.
    """
    F = data["F"]
    f = data["f"]
    g = data["g"]
    if sp.simplify(F.subs(x, -x) + F) != 0:
        raise AssertionError("F is not odd")
    if sp.simplify(g.subs(x, -x) + g) != 0:
        raise AssertionError("g is not odd")
    if sp.simplify(F.subs(x, 0)) != 0:
        raise AssertionError("F(0) != 0")
    identity = sp.simplify(F - mu * x * (x**2 - 3) / 3)
    if identity != 0:
        raise AssertionError("F factorization F = (μ/3) x (x²-3) failed")
    if sp.simplify(sp.diff(F, x) - f) != 0:
        raise AssertionError("F' != f")
    if sp.simplify(f - mu * (x**2 - 1)) != 0:
        raise AssertionError("f != μ(x²-1)")
    zeros = sp.solve(sp.Eq(F, 0), x)
    zeros_set = set(sp.simplify(z) for z in zeros)
    if zeros_set != {sp.Integer(0), sp.sqrt(3), -sp.sqrt(3)}:
        raise AssertionError(f"zeros of F are {zeros_set}")
    a = sp.sqrt(3)
    # Sign of F on (0,∞) is the sign of (x²-3), because μ>0 and x>0.
    # Exact values at rational test points: F(1)=-2μ/3<0, F(2)=2μ/3>0.
    if sp.simplify(F.subs(x, 1) + (2 * mu) / 3) != 0:
        raise AssertionError("expected F(1)=-2μ/3")
    if sp.simplify(F.subs(x, 2) - (2 * mu) / 3) != 0:
        raise AssertionError("expected F(2)=2μ/3")
    # F'(x)=μ(x²-1). On [√3,∞) one has x²-1 ≥ 2, so F' ≥ 2μ > 0.
    f_at_a = sp.simplify(f.subs(x, a))
    if f_at_a != 2 * mu:
        raise AssertionError(f"F'(√3) should be 2μ, got {f_at_a}")
    if sp.simplify(f.subs(x, 0) + mu) != 0:
        raise AssertionError("expected F'(0)=-μ<0")
    lim = sp.limit(F, x, sp.oo)
    if lim != sp.oo:
        raise AssertionError(f"expected F→∞, got {lim}")
    xg = sp.simplify(x * g)
    if xg != x**2:
        raise AssertionError("expected x g(x) = x²")
    G = sp.simplify(sp.integrate(g, x))
    if G.subs(x, 0) != 0:
        G = sp.simplify(G - G.subs(x, 0))
    if sp.simplify(G - x**2 / 2) != 0:
        raise AssertionError("G is not x²/2")
    if sp.limit(G, x, sp.oo) != sp.oo:
        raise AssertionError("G does not tend to ∞")
    return {
        "F": "mu*(x**3/3 - x)",
        "F_factored": "(mu/3)*x*(x**2 - 3)",
        "f": "mu*(x**2 - 1)",
        "g": "x",
        "G": "x**2/2",
        "F_odd": True,
        "g_odd": True,
        "positive_zero_of_F": "sqrt(3)",
        "F_negative_on": "(0, sqrt(3))",
        "F_positive_on": "(sqrt(3), oo)",
        "F_prime_at_sqrt3": "2*mu",
        "F_prime_positive_on_tail": True,
        "F_prime_at_0": "-mu",
        "F_tends_to_plus_infinity": True,
        "xg_positive_off_zero": True,
        "G_tends_to_plus_infinity": True,
        "theorem": (
            "Liénard uniqueness for ẋ=y-F(x), ẏ=-x with F odd, "
            "one positive zero a, F<0 on (0,a), F>0 and F'>0 on [a,∞), "
            "F→∞. Conclusion: exactly one periodic orbit, asymptotically stable."
        ),
    }


def energy_identities(p, q, data: dict) -> dict:
    """Exact energy derivatives. A closed orbit cannot live in one strip."""
    e = (x**2 + y**2) / 2
    dedt = sp.simplify(sp.diff(e, x) * p + sp.diff(e, y) * q)
    expected = -mu * (x**2 - 1) * y**2
    if sp.simplify(dedt - expected) != 0:
        raise AssertionError(f"Cartesian energy derivative {dedt}")
    Y = data["Y"]
    F = data["F"]
    w = (x**2 + Y**2) / 2
    # In (x,Y) coordinates: ẋ=Y-F, Ẏ=-x, so dW/dt = -x F(x).
    dWdt = sp.simplify((Y - F) * x + (-x) * Y)
    if sp.simplify(dWdt + x * F) != 0:
        raise AssertionError("Liénard energy derivative failed")
    if sp.simplify(dWdt + mu * x**2 * (x**2 / 3 - 1)) != 0:
        raise AssertionError("Liénard energy did not match -μ x²(x²/3-1)")
    return {
        "cartesian_dE_dt": "-mu*(x**2 - 1)*y**2",
        "lienard_dW_dt": "-x*F(x)",
        "lienard_dW_dt_expanded": "-mu*x**2*(x**2/3 - 1)",
        "closed_orbit_must_meet_both_strips": True,
    }


def _trig_integrals() -> dict:
    c2 = sp.integrate(sp.cos(theta) ** 2, (theta, 0, 2 * sp.pi))
    s2 = sp.integrate(sp.sin(theta) ** 2, (theta, 0, 2 * sp.pi))
    c2s2 = sp.integrate(sp.cos(theta) ** 2 * sp.sin(theta) ** 2, (theta, 0, 2 * sp.pi))
    if c2 != sp.pi or s2 != sp.pi or c2s2 != sp.pi / 4:
        raise AssertionError(f"circle integrals: cos²={c2}, sin²={s2}, cos²sin²={c2s2}")
    return {"int_cos2": "pi", "int_sin2": "pi", "int_cos2_sin2": "pi/4"}


def abelian_trig() -> sp.Expr:
    """Poincaré–Pontryagin integral on H=(x²+y²)/2=h, flow orientation.

    Unperturbed flow ẋ=y, ẏ=-x is clockwise. Parametrize
    x=√(2h) cos t, y=-√(2h) sin t. Perturbation is μ(P1,Q1)=(0,-(x²-1)y).
    I(h) = ∮ Q1 dx − P1 dy.
    """
    r = sp.sqrt(2 * h)
    xt = r * sp.cos(theta)
    yt = -r * sp.sin(theta)
    p1 = 0
    q1 = -(xt**2 - 1) * yt
    dx = sp.diff(xt, theta)
    dy = sp.diff(yt, theta)
    integrand = sp.expand(q1 * dx - p1 * dy)
    raw = sp.integrate(integrand, (theta, 0, 2 * sp.pi))
    return sp.simplify(mu * raw)


def abelian_green() -> sp.Expr:
    """Same I(h) as a disk flux. Clockwise flow ⇒ I = ∬ div.

    div(μ P1, μ Q1) = −μ(x²−1). Polar: x=r cos θ, y=r sin θ,
    disk r² ≤ 2h.
    """
    r = sp.symbols("r", real=True, positive=True)
    div = -mu * (r**2 * sp.cos(theta) ** 2 - 1)
    flux = sp.integrate(sp.integrate(div * r, (r, 0, sp.sqrt(2 * h))), (theta, 0, 2 * sp.pi))
    return sp.simplify(flux)


def check_abelian() -> dict:
    _trig_integrals()
    i_trig = abelian_trig()
    i_green = abelian_green()
    expected = sp.pi * mu * h * (2 - h)
    if sp.simplify(i_trig - expected) != 0:
        raise AssertionError(f"trig Abelian integral {i_trig} != {expected}")
    if sp.simplify(i_green - expected) != 0:
        raise AssertionError(f"Green Abelian integral {i_green} != {expected}")
    # Zeros: π μ h (2-h) = 0 ⇒ h=0 (the equilibrium) or h=2 (one oval).
    poly = sp.Poly(sp.expand(expected / (sp.pi * mu)), h)
    if poly.degree() != 2:
        raise AssertionError("I(h)/(πμ) should be quadratic")
    coeffs = [sp.simplify(c) for c in poly.all_coeffs()]
    # h² coeff, h coeff, const: expected -h² + 2h + 0
    if coeffs != [-1, 2, 0]:
        raise AssertionError(f"I(h)/(πμ) coeffs {coeffs}")
    deriv = sp.simplify(sp.diff(expected, h))
    # I'(h) = πμ(2-2h); I'(2) = -2πμ ≠ 0.
    if sp.simplify(deriv.subs(h, 2) + 2 * sp.pi * mu) != 0:
        raise AssertionError("I'(2) should be -2πμ")
    if sp.simplify(expected.subs(h, 2)) != 0:
        raise AssertionError("I(2) should vanish")
    if expected.subs(h, 0) != 0:
        raise AssertionError("I(0) should vanish")
    return {
        "unperturbed_H": "(x**2 + y**2)/2",
        "perturbation_P1": "0",
        "perturbation_Q1": "-(x**2 - 1)*y",
        "I_h": "pi*mu*h*(2 - h)",
        "I_over_pi_mu_coeffs_h_high_to_low": ["-1", "2", "0"],
        "positive_zeros": ["2"],
        "simple_at_h2": True,
        "I_prime_at_2": "-2*pi*mu",
        "methods_agree": ["trig_parametrization", "green_disk_flux"],
        "note": (
            "A simple zero of the first-order Abelian integral gives a "
            "unique hyperbolic cycle near the circle of radius 2 for "
            "sufficiently small μ>0 (Poincaré–Pontryagin). Uniqueness "
            "for every μ>0 is the Liénard theorem, not this integral."
        ),
    }


def check_not_radial_family(p, q) -> dict:
    """Line D owns ẋ=y-x(r²-ρ²), ẏ=-x-y(r²-ρ²). This cubic is different."""
    r2 = x**2 + y**2
    rho = sp.symbols("rho", real=True, positive=True)
    p_rad = y - x * (r2 - rho**2)
    q_rad = -x - y * (r2 - rho**2)
    if sp.simplify(p - p_rad) == 0 and sp.simplify(q - q_rad) == 0:
        raise AssertionError("van der Pol collapsed onto the radial family")
    # No ρ, μ make the two fields identical as polynomials in (x,y).
    diff_p = sp.expand(p - p_rad)
    if diff_p == 0:
        raise AssertionError("P matches a radial field")
    return {
        "distinct_from_radial_family": True,
        "radial_P": "y - x*(x**2 + y**2 - rho**2)",
        "radial_Q": "-x - y*(x**2 + y**2 - rho**2)",
        "this_P": "y",
        "this_Q": "-x - mu*(x**2 - 1)*y",
    }


def build_certificate() -> dict:
    p, q = field()
    degree = check_degree(p, q)
    eq = check_unique_equilibrium(p, q)
    data = lienard_data(p, q)
    hypo = check_lienard_hypotheses(data)
    energy = energy_identities(p, q, data)
    abelian = check_abelian()
    radial = check_not_radial_family(p, q)
    return {
        "line": "B",
        "status": "fork",
        "hn_moved": False,
        "h3_lower_bound_claimed": False,
        "imagined_claim": (
            "An explicit real cubic planar field with 14 isolated "
            "periodic orbits, beating Li–Liu–Yang H(3)>=13."
        ),
        "exact_statement": (
            "For every real mu>0 the cubic van der Pol field "
            "dx/dt=y, dy/dt=-x-mu*(x**2-1)*y satisfies the hypotheses "
            "of Lienard's uniqueness theorem, hence has exactly one "
            "periodic orbit, and that orbit is asymptotically stable. "
            "Separately, its first-order Abelian integral on the ovals "
            "of H=(x**2+y**2)/2 is I(h)=pi*mu*h*(2-h), with exactly "
            "one positive simple zero, at h=2."
        ),
        "published_record": (
            "H(3)>=13, Li–Liu–Yang, J. Differ. Equations 246 (2009). "
            "Not replayed (paywalled). Not beaten."
        ),
        "isolated_periodic_orbits": 1,
        "parameter": "mu>0",
        "field": {
            "P": "y",
            "Q": "-x - mu*(x**2 - 1)*y",
            **degree,
        },
        "equilibrium": eq,
        "lienard_hypotheses": hypo,
        "energy": energy,
        "abelian_integral": abelian,
        "not_the_radial_family": radial,
        "what_this_is_not": [
            "not a dent of H(3)",
            "not a claim that H(3)>=14",
            "not a replay of Li–Liu–Yang's 13 cycles",
            "not a lower bound from numerics",
        ],
    }


def canonicalize(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_certificate(path: Path) -> dict:
    cert = build_certificate()
    path.write_text(canonicalize(cert), encoding="utf-8")
    return cert


def check_certificate(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"missing certificate {path}")
    stored = json.loads(path.read_text(encoding="utf-8"))
    fresh = build_certificate()
    if stored != fresh:
        raise AssertionError("certificate.json does not match a fresh replay")
    if stored.get("hn_moved") is not False:
        raise AssertionError("certificate must not claim that H(n) moved")
    if stored.get("h3_lower_bound_claimed") is not False:
        raise AssertionError("certificate must not claim a new H(3) bound")
    if stored.get("isolated_periodic_orbits") != 1:
        raise AssertionError("this fork proves exactly one cycle, not 14")
    if stored.get("status") != "fork":
        raise AssertionError("line B is a fork")
    return stored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", nargs="?", const=str(CERT_PATH), default=None)
    parser.add_argument("--check", nargs="?", const=str(CERT_PATH), default=None)
    args = parser.parse_args(argv)
    if args.write is None and args.check is None:
        args.write = str(CERT_PATH)
        args.check = str(CERT_PATH)
    if args.write is not None:
        cert = write_certificate(Path(args.write))
        print(f"WROTE {args.write}")
        print(f"STATUS {cert['status']} isolated_periodic_orbits={cert['isolated_periodic_orbits']} hn_moved={cert['hn_moved']}")
    if args.check is not None:
        cert = check_certificate(Path(args.check))
        print(f"VALID {args.check}")
        print(cert["exact_statement"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(f"FAIL {err}", file=sys.stderr)
        raise SystemExit(1)
