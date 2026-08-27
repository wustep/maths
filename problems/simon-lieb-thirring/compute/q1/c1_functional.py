"""Evaluate the FHJN (arXiv:1808.09017) functional C_1.

For d = 1, Lemma 11 / (35):

    C_1[f, φ] = sqrt(∫ φ²) * (1/2) * ∫_0^∞ (1 - g(t))² t^{-3/2} dt

where g(t) = ∫_0^∞ φ(s) f(s t) ds, f,φ ≥ 0, ∫ f² = ∫ φ = 1.

Any admissible pair gives an upper bound on the infimum C_1, and
Proposition 10 converts that into

    K_1 / K_1^{cl} ≥ 16 / (243 C_1²)
    L_{1,1} / L_{1,1}^{cl} ≤ (9 √3 / 4) C_1
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad


def ratio_from_c1(c1: float) -> dict[str, float]:
    """Exact algebraic conversion from C_1 to the published ratios."""
    k_over_cl = 16.0 / (243.0 * c1 * c1)
    l_over_cl = (9.0 * math.sqrt(3.0) / 4.0) * c1
    return {
        "C_1": c1,
        "K_over_Kcl": k_over_cl,
        "L_over_Lcl": l_over_cl,
    }


def _quad(func, a, b, epsabs=1e-12, epsrel=1e-12, limit=400):
    val, err = quad(func, a, b, epsabs=epsabs, epsrel=epsrel, limit=limit)
    return val, err


def normalize_mu_power_decay(alpha: float, beta: float) -> float:
    """μ such that f(t) = (1 + μ t^α)^{-β} has ∫ f² = 1.

    ∫_0^∞ (1 + μ t^α)^{-2β} dt = μ^{-1/α} ∫_0^∞ (1 + u^α)^{-2β} du.
    """

    def integrand(u: float) -> float:
        return (1.0 + u**alpha) ** (-2.0 * beta)

    integ, err = _quad(integrand, 0.0, np.inf)
    if integ <= 0:
        raise ValueError("power-decay integral vanished")
    mu = integ**alpha
    return float(mu)


def power_decay_f(alpha: float, beta: float, mu: float | None = None):
    if mu is None:
        mu = normalize_mu_power_decay(alpha, beta)

    def f(t: float) -> float:
        if t <= 0.0:
            return 1.0
        return (1.0 + mu * (t**alpha)) ** (-beta)

    return f, mu


def normalize_phi_support(phi_raw, support: float = 1.0) -> tuple:
    integ, err = _quad(phi_raw, 0.0, support)
    if integ <= 0:
        raise ValueError("φ raw integral vanished")
    c0 = 1.0 / integ

    def phi(s: float) -> float:
        if s < 0.0 or s > support:
            return 0.0
        return c0 * phi_raw(s)

    return phi, c0, integ


@dataclass
class C1Result:
    C_1: float
    a: float  # ∫ φ²
    A_g: float  # (1/2) ∫ (1-g)² t^{-3/2}
    mu: float | None
    c0: float | None
    abs_err_est: float
    extras: dict


def evaluate_c1(f, phi, *, support: float = 1.0, t_cut: float = 1e6) -> C1Result:
    """Adaptive quadrature evaluation of C_1[f, φ]. φ supported on [0, support]."""

    def phi2(s: float) -> float:
        v = phi(s)
        return v * v

    a, a_err = _quad(phi2, 0.0, support)

    def g(t: float) -> float:
        if t <= 0.0:
            return 1.0

        def integrand(s: float) -> float:
            return phi(s) * f(s * t)

        val, _ = _quad(integrand, 0.0, support, epsabs=1e-13, epsrel=1e-13)
        return val

    def outer(t: float) -> float:
        if t <= 0.0:
            return 0.0
        one_minus = 1.0 - g(t)
        return (one_minus * one_minus) * (t ** (-1.5))

    # Split at 1 to keep the t^{-3/2} tail under control.
    i0, e0 = _quad(outer, 0.0, 1.0)
    i1, e1 = _quad(outer, 1.0, t_cut)
    # Tail t > t_cut: 0 <= g <= sqrt(a/t) so (1-g)^2 <= 1 and the
    # integrand is at most t^{-3/2}. Missing piece <= 2 t_cut^{-1/2}.
    tail_bound = 2.0 * (t_cut ** (-0.5))
    A_g = 0.5 * (i0 + i1)
    # Conservative: add half the tail bound into C_1 later if needed.
    C = math.sqrt(a) * A_g
    return C1Result(
        C_1=C,
        a=a,
        A_g=A_g,
        mu=None,
        c0=None,
        abs_err_est=0.5 * math.sqrt(a) * (abs(e0) + abs(e1) + tail_bound)
        + 0.5 * A_g * (a_err / max(math.sqrt(a), 1e-30)),
        extras={"i0": i0, "i1": i1, "tail_bound": tail_bound, "a_err": a_err},
    )


def paper_first_pair():
    """Lemma 11 first trial: C_1 ≤ 0.381378 claimed."""
    mu = (4.0 * math.pi / (9.0 * math.sqrt(3.0))) ** 1.5
    f, _ = power_decay_f(1.5, 1.0, mu=mu)

    def phi_raw(t: float) -> float:
        if t < 0.0 or t > 1.0:
            return 0.0
        return 5.0 * (1.0 - t**0.25)

    # Already normalized: ∫_0^1 5(1-t^{1/4}) dt = 5(1 - 4/5) = 1.
    return f, phi_raw, mu, 5.0


def paper_second_pair():
    """Lemma 11 second trial: C_1 ≤ 0.373556 claimed."""
    f, mu = power_decay_f(4.5, 0.25)

    def phi_raw(t: float) -> float:
        if t < 0.0 or t > 1.0:
            return 0.0
        return ((1.0 - t**0.36) ** 2.1) / (1.0 + t)

    phi, c0, _ = normalize_phi_support(phi_raw, support=1.0)
    return f, phi, mu, c0


def parametric_pair(alpha, beta, gamma, delta, eps, kappa, support=1.0):
    f, mu = power_decay_f(alpha, beta)

    def phi_raw(t: float) -> float:
        if t < 0.0 or t > support:
            return 0.0
        return ((1.0 - (t / support) ** gamma) ** delta) / ((1.0 + eps * t) ** kappa)

    phi, c0, _ = normalize_phi_support(phi_raw, support=support)
    return f, phi, mu, c0
