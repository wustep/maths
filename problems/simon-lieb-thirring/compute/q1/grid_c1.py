"""Fast log-grid evaluator for the FHJN C_1 functional (d=1).

Does not replace ``c1_functional.evaluate_c1`` (adaptive quad). This is
the inner-loop approximation used by the optimizers. Finalists should be
re-scored with ``evaluate_c1``.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np


def gauss_legendre(a: float, b: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    x, w = np.polynomial.legendre.leggauss(int(n))
    mid = 0.5 * (b + a)
    half = 0.5 * (b - a)
    return mid + half * x, half * w


def power_decay_vec(t: np.ndarray, mu: float, alpha: float, beta: float) -> np.ndarray:
    t = np.asarray(t, dtype=np.float64)
    out = np.empty_like(t)
    pos = t > 0.0
    out[~pos] = 1.0
    if not np.any(pos):
        return out
    u = mu * np.exp(alpha * np.log(t[pos]))
    out[pos] = np.exp(-beta * np.log1p(u))
    return out


def integrate_log(
    t: np.ndarray,
    logt: np.ndarray,
    values: np.ndarray,
) -> float:
    """Trapezoid of ``values`` against ``dt`` on a log-spaced ``t`` grid.

    ``values`` is the integrand h(t); the measure is ``h(t) t d(log t)``.
    """
    trap = getattr(np, "trapezoid", None) or np.trapz
    return float(trap(values * t, logt))


def l2_power_decay_integrand_I(alpha: float, beta: float, n: int = 8000) -> float:
    """I = ∫_0^∞ (1 + u^α)^{-2β} du, so μ = I^α gives ∫ f² = 1."""
    if alpha <= 0.0 or beta <= 0.0:
        return np.inf
    if 2.0 * alpha * beta <= 1.02:
        return np.inf
    umin, umax = 1e-12, 1e12
    u = np.logspace(np.log10(umin), np.log10(umax), n)
    logu = np.log(u)
    val = np.exp(-2.0 * beta * np.log1p(np.exp(alpha * np.log(u))))
    core = integrate_log(u, logu, val)
    small = umin
    p = 2.0 * alpha * beta
    tail = (umax ** (1.0 - p)) / (p - 1.0)
    return float(core + small + tail)


@lru_cache(maxsize=8192)
def normalize_mu(alpha: float, beta: float) -> float:
    I = l2_power_decay_integrand_I(alpha, beta)
    if not np.isfinite(I) or I <= 0.0:
        raise ValueError("power-decay L2 integral failed")
    return float(I**alpha)


def stretch_l2_unit(psi_on_grid, t: np.ndarray, logt: np.ndarray, tmin: float, tmax: float) -> float:
    """Horizontal stretch σ so that f(t)=ψ(t/σ) has ∫ f² = 1, given ψ(0)=1.

    ∫ [ψ(t/σ)]² dt = σ ∫ ψ(u)² du, hence σ = 1 / ∫ψ².
    ``psi_on_grid`` is ψ evaluated on the same ``t`` grid used as u.
    """
    psi2 = psi_on_grid * psi_on_grid
    core = integrate_log(t, logt, psi2)
    small = tmin * float(psi_on_grid[0] ** 2)
    # power-law tail from last two points
    if psi_on_grid[-1] > 0.0 and psi_on_grid[-2] > 0.0:
        p = -np.log(psi_on_grid[-1] / psi_on_grid[-2]) / (logt[-1] - logt[-2])
        p = float(np.clip(p, 0.51, 40.0))
        tail = (psi_on_grid[-1] ** 2) * tmax / (2.0 * p - 1.0)
    else:
        tail = 0.0
    I = core + small + tail
    if I <= 0.0 or not np.isfinite(I):
        return np.nan
    return float(1.0 / I)


class FastC1:
    """Log-grid C_1 with Gauss–Legendre in s and analytic t-tails."""

    def __init__(
        self,
        *,
        ns: int = 512,
        nt: int = 2048,
        tmin: float = 1e-8,
        tmax: float = 1e8,
    ) -> None:
        self.ns = int(ns)
        self.nt = int(nt)
        self.tmin = float(tmin)
        self.tmax = float(tmax)
        self.t = np.logspace(np.log10(self.tmin), np.log10(self.tmax), self.nt)
        self.logt = np.log(self.t)
        # reference grid for L2 / stretch of f-shapes
        self.u = self.t
        self.logu = self.logt

    def s_nodes(self, pieces: list[tuple[float, float]]) -> tuple[np.ndarray, np.ndarray]:
        ss = []
        ws = []
        n_each = max(16, self.ns // max(len(pieces), 1))
        for a, b in pieces:
            if b <= a:
                continue
            s, w = gauss_legendre(a, b, n_each)
            ss.append(s)
            ws.append(w)
        if not ss:
            raise ValueError("empty φ support")
        return np.concatenate(ss), np.concatenate(ws)

    def c1_from_g(
        self,
        g: np.ndarray,
        a_phi2: float,
        *,
        include_tails: bool = True,
    ) -> dict[str, float]:
        omg = 1.0 - g
        integrand = (omg * omg) * np.power(self.t, -1.5)
        core = integrate_log(self.t, self.logt, integrand)

        small = 0.0
        tail = 0.0
        if include_tails:
            # small-t: 1-g ~ c t^p
            om0 = max(float(omg[0]), 0.0)
            om1 = max(float(omg[1]), 0.0)
            if om0 > 0.0 and om1 > 0.0:
                p = math.log(om1 / om0) / (self.logt[1] - self.logt[0])
                p = float(np.clip(p, 0.26, 40.0))
                small = (om0 * om0) * (self.tmin ** -0.5) / (2.0 * p - 0.5)
            # large-t: g(t) ~ g∞ (t/tmax)^{-q}
            g_end = max(float(g[-1]), 0.0)
            if g_end > 1e-18 and g[-2] > 1e-18:
                q = -math.log(float(g[-1] / g[-2])) / (self.logt[-1] - self.logt[-2])
                q = float(np.clip(q, 0.05, 40.0))
            else:
                q = 2.0
            invsqrt = self.tmax ** -0.5
            tail = 2.0 * invsqrt * (
                1.0 - 2.0 * g_end / (q + 0.5) + (g_end * g_end) / (2.0 * q + 0.5)
            )
            tail = max(tail, 0.0)

        I = core + small + tail
        A_g = 0.5 * I
        sqrt_a = math.sqrt(max(a_phi2, 0.0))
        C = sqrt_a * A_g
        # truncated-at-tmax analogue of evaluate_c1(t_cut=tmax)
        A_trunc = 0.5 * core
        C_trunc = sqrt_a * A_trunc
        return {
            "C_1": float(C),
            "C_1_trunc": float(C_trunc),
            "a": float(a_phi2),
            "A_g": float(A_g),
            "I_core": float(core),
            "I_small": float(small),
            "I_tail": float(tail),
        }

    def c1_from_f_phi_arrays(
        self,
        s: np.ndarray,
        w: np.ndarray,
        phi: np.ndarray,
        f_st: np.ndarray,
        *,
        include_tails: bool = True,
    ) -> dict[str, float]:
        mass = float(np.dot(w, phi))
        if mass <= 0.0 or not np.isfinite(mass):
            return {"C_1": 1e9, "C_1_trunc": 1e9, "a": 0.0, "A_g": 0.0}
        phi_n = phi / mass
        a = float(np.dot(w, phi_n * phi_n))
        g = f_st @ (w * phi_n)
        g = np.clip(g, 0.0, 1.0)
        return self.c1_from_g(g, a, include_tails=include_tails)

    def eval_callables(self, f_vec, phi_vec, pieces: list[tuple[float, float]]) -> dict[str, float]:
        s, w = self.s_nodes(pieces)
        phi = np.clip(phi_vec(s), 0.0, np.inf)
        st = self.t[:, None] * s[None, :]
        f_st = np.clip(f_vec(st), 0.0, np.inf)
        return self.c1_from_f_phi_arrays(s, w, phi, f_st)


def ratio_L(c1: float) -> float:
    return (9.0 * math.sqrt(3.0) / 4.0) * c1
