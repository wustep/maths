"""Shi Songling field, equilibria, linear types, Li polynomials.

Unperturbed (λ = ε = δ = μ = 0), Yu–Zhang / Galias transcription of
Shi, Sci. Sinica 23 (1980):

    dx/dt = −y − 10 x² + 5 x y + y²
    dy/dt =  x + x² − 25 x y

The imagined five-cycle field is the same jet plus
λx in P, (8ε − 9δ) x y and μ y² in Q, and δ x y in P.
"""

from __future__ import annotations

from typing import Any

import sympy as sp

X, Y = sp.symbols("x y")
LAM, EPS, DEL, MU = sp.symbols("lambda epsilon delta mu")


def rat(n, d=1) -> dict[str, Any]:
    n, d = sp.Integer(n), sp.Integer(d)
    g = sp.gcd(n, d)
    n, d = n // g, d // g
    if d < 0:
        n, d = -n, -d
    return {
        "num": int(n),
        "den": int(d),
        "str": str(n) if d == 1 else f"{n}/{d}",
    }


def shi_field(lam=0, eps=0, delta=0, mu=0, x=X, y=Y):
    """Return (P, Q) of the imagined / Shi family."""
    P = (
        lam * x
        - y
        - 10 * x**2
        + (5 + delta) * x * y
        + y**2
    )
    Q = (
        x
        + x**2
        + (-25 + 8 * eps - 9 * delta) * x * y
        + mu * y**2
    )
    return sp.expand(P), sp.expand(Q)


def jacobian(P, Q, x=X, y=Y):
    return sp.Matrix(
        [[sp.diff(P, x), sp.diff(P, y)], [sp.diff(Q, x), sp.diff(Q, y)]]
    )


def li_chengzhi(l, r, n, a, b):
    """Li Chengzhi polynomials, as quoted by Llibre–Schlomiuk (2004).

    Normal form
        dx/dt = −y + l x² + r x y + n y²
        dy/dt =  x + a x² + b x y
    """
    L1 = r * (l + n) - a * (b + 2 * l)
    L2 = (
        r
        * a
        * (5 * a - r)
        * ((l + n) ** 2 * (n + b) - a**2 * (b + 2 * l + n))
    )
    L3 = (
        r
        * a**2
        * (2 * a**2 + n * (l + 2 * n))
        * ((l + n) ** 2 * (n + b) - a**2 * (b + 2 * l + n))
    )
    return sp.expand(L1), sp.expand(L2), sp.expand(L3)


def l1_primitive(a20, a11, a02, b20, b11, b02):
    """Integer L1 of a general quadratic focus (line E / Llibre–Valls).

    V1 in the Poincaré–Lyapunov normalisation is this polynomial over 8.
    """
    return (
        (a20 + a02) * a11
        - (b20 + b02) * b11
        - 2 * a20 * b20
        + 2 * a02 * b02
    )


def unperturbed_equilibria():
    """Exact finite equilibria of λ = ε = δ = μ = 0.

    Q = x (1 + x − 25 y) = 0. On x = 0, P = y(y − 1) = 0, so (0, 0)
    and (0, 1). On the line y = (1 + x)/25 the remaining condition is
    the quadratic 6124 x² − 102 x + 24 = 0, discriminant −577500 < 0.
    Two real, two complex; Bézout 4.
    """
    P, Q = shi_field(0, 0, 0, 0)
    # x = 0 branch
    Px0 = sp.expand(P.subs(X, 0))
    assert sp.expand(Px0 - Y * (Y - 1)) == 0
    assert sp.expand(Q.subs(X, 0)) == 0

    # second branch
    yline = (1 + X) / 25
    residual = sp.together(P.subs(Y, yline))
    quad = sp.expand(sp.numer(sp.together(residual * 625)))
    # 625 P = −6124 x² + 102 x − 24, so the monic-positive form is
    # 6124 x² − 102 x + 24.
    quad_pos = sp.expand(-quad)
    assert quad_pos == 6124 * X**2 - 102 * X + 24
    disc = sp.discriminant(sp.Poly(quad_pos, X))
    assert disc == -577500
    assert disc < 0

    sols = sp.solve([P, Q], [X, Y], dict=True)
    real = []
    complex_pts = []
    for s in sols:
        xs, ys = sp.simplify(s[X]), sp.simplify(s[Y])
        rec = {"x": str(xs), "y": str(ys)}
        if xs.is_real and ys.is_real:
            real.append(rec)
        else:
            complex_pts.append(rec)
    assert len(real) == 2 and len(complex_pts) == 2
    return {
        "real_count": 2,
        "complex_count": 2,
        "bezout_max": 4,
        "y_axis_branch": ["(0, 0)", "(0, 1)"],
        "second_branch_quadratic": "6124 x^2 - 102 x + 24",
        "second_branch_discriminant": -577500,
        "real": real,
        "complex": complex_pts,
    }


def second_focus_linear_type():
    """(0, 1) of the unperturbed field: strong unstable focus."""
    P, Q = shi_field(0, 0, 0, 0)
    J = jacobian(P, Q).subs({X: 0, Y: 1})
    assert J == sp.Matrix([[5, 1], [-24, 0]])
    tr, det = J.trace(), J.det()
    disc = sp.expand(tr**2 - 4 * det)
    assert tr == 5 and det == 24 and disc == -71
    return {
        "point": [0, 1],
        "jacobian": [[5, 1], [-24, 0]],
        "trace": 5,
        "det": 24,
        "disc": -71,
        "charpoly": "t^2 - 5 t + 24",
        "eigenvalues": "5/2 ± i sqrt(71)/2",
        "type": "strong_unstable_focus",
        "note": (
            "Trace 5 > 0, det 24 > 0, disc −71 < 0. Not a weak focus: "
            "no Hopf unfolding at (0, 1) inside a small Shi perturbation."
        ),
    }


def origin_linear_type():
    P, Q = shi_field(0, 0, 0, 0)
    J = jacobian(P, Q).subs({X: 0, Y: 0})
    assert J == sp.Matrix([[0, -1], [1, 0]])
    return {
        "point": [0, 0],
        "jacobian": [[0, -1], [1, 0]],
        "trace": 0,
        "det": 1,
        "disc": -4,
        "charpoly": "t^2 + 1",
        "type": "linear_center",
    }


def trace_det_at_01(lam, eps, delta, mu=0):
    """Jacobian trace and det at (0, 1), when that point is an equilibrium.

    (0, 1) is an equilibrium iff μ = 0 (Q(0, 1) = μ).
    """
    P, Q = shi_field(lam, eps, delta, mu)
    assert sp.expand(P.subs({X: 0, Y: 1})) == 0
    assert sp.expand(Q.subs({X: 0, Y: 1})) == mu
    J = jacobian(P, Q).subs({X: 0, Y: 1})
    return sp.expand(J.trace()), sp.expand(J.det())


def five_cycle_obstructions() -> dict[str, Any]:
    """Exact identities that kill the imagined five-cycle field."""
    # μ moves (0, 1) and drops the origin to order 1.
    l1_mu = l1_primitive(-10, 5, 1, 1, -25, MU)
    assert sp.expand(l1_mu) == 27 * MU

    # Trace at (0, 1) vanishes in the Shi family only on λ + 5 + δ = 0,
    # and then (for μ = 0) det = −21 − 8ε − 9λ.
    tr, det = trace_det_at_01(LAM, EPS, DEL, 0)
    assert sp.expand(tr - (LAM + 5 + DEL)) == 0
    assert sp.expand(det - (24 - 8 * EPS + 9 * DEL)) == 0

    # The classical attempt “make (0, 1) weak and keep the origin
    # order 3”: λ = ε = 0, δ = −5. Then det = −21 < 0 (saddle), and
    # Li’s three polynomials all vanish (origin is a center).
    li_center = li_chengzhi(-10, 5 + (-5), 1, 1, -25 - 9 * (-5))
    assert li_center == (0, 0, 0)
    tr05, det05 = trace_det_at_01(0, 0, -5, 0)
    assert tr05 == 0 and det05 == -21

    # If one insists on a focus at (0, 1) with zero trace and a weak
    # origin (λ = 0, δ = −5, μ = 0), one needs det > 0, i.e. ε < −21/8.
    # Then Li’s L1 at the origin is −8ε ≠ 0: order 1, cyclicity ≤ 1.
    # Bautin at the other focus gives ≤ 3. Total ≤ 4, not 5.
    L1_eps = li_chengzhi(-10, 0, 1, 1, 20 + 8 * EPS)[0]
    assert sp.expand(L1_eps + 8 * EPS) == 0

    # Linear-order circles about (0, 1) are not without contact:
    # V = x² + (y−1)², V̇ |_{r-circle} = r² (5 + 5 cos 2θ − 23 sin 2θ) + O(r³)
    # and 5 ± sqrt(25 + 529) = 5 ± sqrt(554) have opposite signs.
    amp2 = 5**2 + 23**2
    assert amp2 == 554
    assert amp2 > 25  # so 5 − sqrt(554) < 0 < 5 + sqrt(554)

    return {
        "mu_moves_second_equilibrium": {
            "Q_at_0_1": "mu",
            "L1_primitive_at_origin": "27 mu",
            "V1_at_origin": "27 mu / 8",
            "order_3_requires": "mu = 0",
        },
        "trace_at_0_1": {
            "formula": "lambda + 5 + delta",
            "det_formula_mu_0": "24 - 8 epsilon + 9 delta",
        },
        "delta_minus_5_lambda_eps_0": {
            "origin_Li": [0, 0, 0],
            "origin_type": "center",
            "second_point": "(0, 1)",
            "second_trace": 0,
            "second_det": -21,
            "second_type": "saddle",
        },
        "both_weak_in_family": {
            "conditions": "lambda = 0, delta = -5, mu = 0, epsilon < -21/8",
            "origin_Li_L1": "-8 epsilon != 0",
            "origin_order": 1,
            "bautin_budget": "1 + 3 = 4, not 5",
        },
        "circles_about_0_1_linear": {
            "V": "x^2 + (y-1)^2",
            "Vdot_r2": "5 + 5 cos(2 theta) - 23 sin(2 theta)",
            "amplitude_squared": 554,
            "mean_squared": 25,
            "sign_change": True,
            "note": (
                "Concentric Euclidean circles about (0, 1) already fail "
                "at linear order. Axis-aligned ellipses sampled later "
                "also change sign (residue, not a trapping pair)."
            ),
        },
        "coppel_unique_singularity": (
            "A quadratic limit cycle surrounds a unique singular point, "
            "and that point is a focus (Coppel 1966, as stated in "
            "Llibre–Schlomiuk, Canad. J. Math. 56 (2004), §7.1(iv)). "
            "A fifth cycle surrounding both foci is excluded for any "
            "quadratic, not only this family."
        ),
        "bautin": (
            "A quadratic focus has cyclicity at most 3 (Bautin). Four "
            "small cycles at the origin are impossible."
        ),
        "galias_this_system": (
            "Galias–Tucker–Wilczak (AMC 2022) prove the Songling field "
            "with μ = 0 and the classical tiny (δ, ε, λ) has exactly "
            "four cycles. That is one system, not H(2) = 4, and it is "
            "not a fifth cycle."
        ),
    }
