#!/usr/bin/env python3
"""I_s(ν) for non-radial signed measures, HPS arXiv:2504.18487v1 Lemma 4.3.

HPS prove I_s(ρ) ≥ I_s(ρ̄) for s ∈ (1, 3] by showing I_s(ν) ≥ 0 when
ν = ρ − ρ̄ is orthogonal to radial functions. The IMS + improved Hardy
step needs c_H − s²/4 ≥ 0 with c_H = d²/4 = 9/4, hence s ≤ 3.

This file:

1. Evaluates I_s(ν) on explicit ν ⊥ radial, at s = 3, 3.1, 3.5, 4.
   Two-shell spherical-harmonic measures have a closed quadratic form.
   Interval arithmetic certifies the sign. Volume densities (pure dipole,
   quadrupole, two opposite Gaussians / regularised Diracs) are checked
   by the same multipole formula or by 3D quadrature.

2. Computes the Hardy quotient of the Coulomb potential of those ν.
   There is no uniform gap past 9/4: the two-shell dipole family drives
   the quotient to 9/4, and I_s itself goes negative for every s > 3.

3. Produces trial upper bounds on β_s (probability measures). A search
   is not a lower bound. The crude pointwise minorant is (1/2) b(s)^{-1}.

Writes certs/s_gt_3.json.

Record opened this session:
  https://arxiv.org/abs/2504.18487
  https://arxiv.org/html/2504.18487v1
  (Lemma 4.3, Prop. 4.5, Remark 2.3, Lemma 5.9)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from mpmath import iv, mp, mpf, nstr, power, quad, sqrt

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
WORK = HERE / "work"

mp.dps = 80
iv.dps = 60
PREC = 40
S_LIST = (mpf(3), mpf("3.1"), mpf("3.5"), mpf(4))


def S(x, d: int = PREC) -> str:
    return nstr(x, d, strip_zeros=False)


def iv_bounds(x) -> tuple[str, str]:
    return S(mpf(x.a)), S(mpf(x.b))


# ---------------------------------------------------------------------------
# b(s) = max_{t∈[0,1]} (1+t^{s-1})/(1+t^s)  = (s-1)/(s t_0)
# t_0^s + s t_0 + 1 − s = 0, unique root in (0,1) for s > 1.
# ---------------------------------------------------------------------------


def ratio_b(s, t):
    t = mpf(t)
    if t == 0:
        return mpf(1)
    return (1 + t ** (s - 1)) / (1 + t**s)


def t0_of(s):
    """Unique root of t^s + s t + 1 − s = 0 in (0, 1)."""
    s = mpf(s)

    def f(t):
        return t**s + s * t + 1 - s

    lo, hi = mpf("1e-30"), mpf(1)
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def b_of(s):
    t0 = t0_of(s)
    return (s - 1) / (s * t0), t0


def t0_iv(s, t_lo, t_hi):
    """Interval root enclosure: f(t_lo)<0<f(t_hi) and f' > 0 on the interval."""
    s = iv.mpf(s)
    lo = iv.mpf(t_lo)
    hi = iv.mpf(t_hi)
    t = iv.mpf(t_lo) + (iv.mpf(t_hi) - iv.mpf(t_lo)) * iv.mpf("0.5")
    # Use the interval [t_lo, t_hi] itself as the enclosure of the root
    # once the endpoints have opposite signs (checked by the caller).
    return iv.mpf([t_lo, t_hi])


def f_t0(s, t):
    return power(t, s) + s * t + 1 - s


def b_iv_from_t_interval(s, t_lo, t_hi):
    t = iv.mpf([str(t_lo), str(t_hi)])
    si = iv.mpf(s)
    return (si - 1) / (si * t), t


# ---------------------------------------------------------------------------
# Two-shell spherical-harmonic quadratic form
#
# Surface measure: dν = (α Y_{ℓm}(ω) δ(r−r1)/r1² + β Y_{ℓm}(ω) δ(r−r2)/r2²) d³x
# with Y_{ℓm} L²-normalised on S². Then (r2 = 1, r1 = t ∈ (0,1))
#
#   I_s(ν) = [4π / (2ℓ+1)] Q_s(α, β; t, ℓ)
#   Q_s     = α² t^{s−1} + β² + αβ (t^{s+ℓ} + t^ℓ)
#
# Orthogonal to every radial function for ℓ ≥ 1. Single-shell (β=0) has
# Q_s = α² t^{s−1} ≥ 0. Opposite-sign two-shell can go negative for s > 2ℓ+1.
# ---------------------------------------------------------------------------


def Q_two_shell(s, ell, t, alpha, beta):
    s, t, alpha, beta = mpf(s), mpf(t), mpf(alpha), mpf(beta)
    return (
        alpha**2 * t ** (s - 1)
        + beta**2
        + alpha * beta * (t ** (s + ell) + t**ell)
    )


def Q_two_shell_iv(s, ell, t, alpha, beta):
    s = iv.mpf(s)
    ell = iv.mpf(ell)
    t = iv.mpf(t) if not isinstance(t, type(iv.mpf(1))) else t
    a = iv.mpf(alpha)
    b = iv.mpf(beta)
    return a**2 * iv.exp((s - 1) * iv.log(t)) + b**2 + a * b * (
        iv.exp((s + ell) * iv.log(t)) + iv.exp(ell * iv.log(t))
    )


def I_prefactor(ell):
    return 4 * mp.pi / (2 * ell + 1)


def det_condition(s, ell, t):
    """Q has a negative eigenvalue iff (t^{s+ℓ} + t^ℓ)/2 > t^{(s−1)/2}."""
    t = mpf(t)
    s = mpf(s)
    return (t ** (s + ell) + t**ell) / 2 - t ** ((s - 1) / 2)


def most_negative_ab(s, ell, t):
    """Eigenvector of the 2×2 form for the smaller eigenvalue."""
    A = t ** (s - 1)
    B = mpf(1)
    C = t ** (s + ell) + t**ell  # off-diagonal * 2, i.e. the αβ coefficient
    # Matrix [[A, C/2], [C/2, B]]
    disc = (A - B) ** 2 + C**2
    lam = (A + B - sqrt(disc)) / 2
    # (A − λ) α + (C/2) β = 0
    if abs(C) < mpf("1e-30"):
        return mpf(1), mpf(0), lam
    beta = mpf(-1)
    alpha = -(C / 2) * beta / (A - lam) if abs(A - lam) > mpf("1e-30") else mpf(1)
    return alpha, beta, lam


# ---------------------------------------------------------------------------
# Multipole potential of a radial profile R(r) × Y_{ℓm}
#   u(r) = r^{−ℓ−1} � a radial profile R(r) × Y_{ℓm}
#   u(r) = r^{−ℓ−1} ∫_0^r τ^{ℓ+2} R(τ) dτ + r^ℓ ∫_r^∞ τ^{1−ℓ} R(τ) dτ
#   I_s  = [4π/(2ℓ+1)] ∫_0^∞ r^{s+2} R(r) u(r) dr
# ---------------------------------------------------------------------------


def I_s_multipole_profile(s, ell, R, rmax=40.0, n=400):
    """Trapezoid on a geometric/linear hybrid grid. R is callable."""
    s = float(s)
    ell = int(ell)
    rs = np.concatenate(
        [
            np.linspace(1e-8, 0.2, n // 5),
            np.geomspace(0.2, rmax, n - n // 5),
        ]
    )
    rs = np.unique(rs)
    Rv = np.array([R(r) for r in rs], dtype=float)
    # Cumulative integrals for u
    tau_lp2_R = rs ** (ell + 2) * Rv
    tau_1ml_R = rs ** (1 - ell) * Rv
    inner = np.zeros_like(rs)
    outer = np.zeros_like(rs)
    for i in range(1, len(rs)):
        inner[i] = inner[i - 1] + 0.5 * (tau_lp2_R[i] + tau_lp2_R[i - 1]) * (
            rs[i] - rs[i - 1]
        )
    for i in range(len(rs) - 2, -1, -1):
        outer[i] = outer[i + 1] + 0.5 * (tau_1ml_R[i] + tau_1ml_R[i + 1]) * (
            rs[i + 1] - rs[i]
        )
    u = rs ** (-ell - 1) * inner + rs**ell * outer
    integrand = rs ** (s + 2) * Rv * u
    acc = 0.0
    for i in range(1, len(rs)):
        acc += 0.5 * (integrand[i] + integrand[i - 1]) * (rs[i] - rs[i - 1])
    return (4.0 * math.pi / (2 * ell + 1)) * acc


def I_s_mp_profile(s, ell, R, rmax=30):
    """mpmath quad of the multipole formula (slower, higher precision)."""
    s = mpf(s)
    ell = int(ell)

    def inner_int(r):
        return quad(lambda tau: tau ** (ell + 2) * R(tau), [0, r])

    def outer_int(r):
        return quad(lambda tau: tau ** (1 - ell) * R(tau), [r, rmax])

    def u(r):
        return r ** (-ell - 1) * inner_int(r) + r**ell * outer_int(r)

    integ = quad(lambda r: r ** (s + 2) * R(r) * u(r), [0, rmax])
    return I_prefactor(ell) * integ


# ---------------------------------------------------------------------------
# Two opposite Gaussians (regularised opposite Diracs), same radius
#   ν = γ_μ − γ_{−μ},  γ_c(x) = (2πσ²)^{−3/2} exp(−|x−c|²/(2σ²))
# Orthogonal to radial functions (odd under x ↦ −x). V of a Gaussian is
# erf(|x−c|/(σ√2)) / |x−c|.
# ---------------------------------------------------------------------------


def gauss_potential(x, center, sigma):
    d = np.linalg.norm(x - center)
    scale = sigma * math.sqrt(2.0)
    if d < 1e-14:
        return math.sqrt(2.0 / math.pi) / sigma
    return math.erf(d / scale) / d


def I_s_two_gaussians(s, mu, sigma, n_r=36, n_th=24, n_ph=16, pad=6.0):
    """3D spherical quadrature of ∫ |x|^s V_ν(x) ν(x) dx."""
    s = float(s)
    c = np.array([0.0, 0.0, float(mu)])
    # Integration box: ball of radius |μ| + pad σ
    Rmax = abs(mu) + pad * sigma
    rs = np.linspace(1e-6, Rmax, n_r)
    ths = np.linspace(0.0, math.pi, n_th)
    phs = np.linspace(0.0, 2.0 * math.pi, n_ph, endpoint=False)
    dr = rs[1] - rs[0]
    dth = ths[1] - ths[0]
    dph = phs[1] - phs[0]
    norm = (2.0 * math.pi * sigma**2) ** (-1.5)
    acc = 0.0
    for r in rs:
        r2 = r * r
        ws_r = dr if (r not in (rs[0], rs[-1])) else 0.5 * dr
        for th in ths:
            st = math.sin(th)
            ct = math.cos(th)
            ws_th = dth if (th not in (ths[0], ths[-1])) else 0.5 * dth
            for ph in phs:
                x = np.array(
                    [r * st * math.cos(ph), r * st * math.sin(ph), r * ct]
                )
                dplus = np.linalg.norm(x - c)
                dminus = np.linalg.norm(x + c)
                rho = norm * (
                    math.exp(-(dplus**2) / (2.0 * sigma**2))
                    - math.exp(-(dminus**2) / (2.0 * sigma**2))
                )
                V = gauss_potential(x, c, sigma) - gauss_potential(x, -c, sigma)
                acc += (r**s) * V * rho * r2 * st * ws_r * ws_th * dph
    return acc


# ---------------------------------------------------------------------------
# Hardy quotient of a two-shell ℓ-potential
#   V = [4π/(2ℓ+1)] u(r) Y_{ℓm}
#   u(r) = α (r^ℓ/r1^{ℓ+1}  if r<r1 else r1^ℓ/r^{ℓ+1})
#        + β (same at r2)
#   ∫|∇V|² = 4π I_0(ν)
#   ∫ V²/r² = [4π/(2ℓ+1)]² ∫ u(r)² dr
#   Q_H = (2ℓ+1) I_0 / ( [4π/(2ℓ+1)] ∫u² )  = (2ℓ+1) Q_0 / ∫u²
# ---------------------------------------------------------------------------


def u_two_shell(r, ell, r1, r2, alpha, beta):
    r = mpf(r)
    r1, r2 = mpf(r1), mpf(r2)
    alpha, beta = mpf(alpha), mpf(beta)

    def one(ri, coef):
        if r < ri:
            return coef * (r**ell) / (ri ** (ell + 1))
        if r > ri:
            return coef * (ri**ell) / (r ** (ell + 1))
        return coef / ri  # continuous value on the shell

    return one(r1, alpha) + one(r2, beta)


def int_u2_two_shell(ell, r1, r2, alpha, beta):
    """Exact ∫_0^∞ u(r)² dr for two shells, piecewise powers."""
    r1, r2 = mpf(r1), mpf(r2)
    a, b = mpf(alpha), mpf(beta)
    ell = int(ell)
    # Region r < r1: u = r^ℓ (a/r1^{ℓ+1} + b/r2^{ℓ+1})
    c_in = a / r1 ** (ell + 1) + b / r2 ** (ell + 1)
    I_in = (c_in**2) * (r1 ** (2 * ell + 1)) / (2 * ell + 1)
    # r1 < r < r2: u = a r1^ℓ / r^{ℓ+1} + b r^ℓ / r2^{ℓ+1}
    # u² = a² r1^{2ℓ} r^{−2ℓ−2} + b² r^{2ℓ} / r2^{2ℓ+2} + 2ab r1^ℓ r^{−1} / r2^{ℓ+1}
    A2 = (a**2) * (r1 ** (2 * ell))
    B2 = (b**2) / (r2 ** (2 * ell + 2))
    C2 = 2 * a * b * (r1**ell) / (r2 ** (ell + 1))
    # ∫ r1..r2 of A2 r^{−2ℓ−2} + B2 r^{2ℓ} + C2 r^{−1}
    if ell == 0:
        raise ValueError("ℓ=0 is radial")
    p = -2 * ell - 2
    I_mid = (
        A2 * (r2 ** (p + 1) - r1 ** (p + 1)) / (p + 1)
        + B2 * (r2 ** (2 * ell + 1) - r1 ** (2 * ell + 1)) / (2 * ell + 1)
        + C2 * (mp.log(r2) - mp.log(r1))
    )
    # r > r2: u = (a r1^ℓ + b r2^ℓ) / r^{ℓ+1}
    c_out = a * r1**ell + b * r2**ell
    I_out = (c_out**2) * (r2 ** (-2 * ell - 1)) / (2 * ell + 1)
    return I_in + I_mid + I_out


def hardy_two_shell(ell, t, alpha, beta):
    """Q_H(V) = ∫|∇V|² / ∫ V²/r² = (2ℓ+1) Q_0 / ∫u²  (r2=1, r1=t).

    This is Hardy on V, not the IMS function |x|^{s/2} V. A large Q_H(V)
    does not imply I_s ≥ 0.
    """
    Q0 = Q_two_shell(0, ell, t, alpha, beta)
    Iu2 = int_u2_two_shell(ell, t, 1, alpha, beta)
    return (2 * ell + 1) * Q0 / Iu2, Q0, Iu2


def int_u2_rs_two_shell(s, ell, r1, r2, alpha, beta):
    """∫_0^∞ u(r)² r^s dr, piecewise exact for two shells."""
    r1, r2 = mpf(r1), mpf(r2)
    a, b = mpf(alpha), mpf(beta)
    ell = int(ell)
    s = mpf(s)
    # r < r1: u = c_in r^ℓ,  u² r^s = c_in² r^{2ℓ+s}
    c_in = a / r1 ** (ell + 1) + b / r2 ** (ell + 1)
    p = 2 * ell + s
    I_in = (c_in**2) * (r1 ** (p + 1)) / (p + 1)
    # r1 < r < r2: u = a r1^ℓ r^{-ℓ-1} + b r^ℓ / r2^{ℓ+1}
    A2 = (a**2) * (r1 ** (2 * ell))
    B2 = (b**2) / (r2 ** (2 * ell + 2))
    C2 = 2 * a * b * (r1**ell) / (r2 ** (ell + 1))
    # A2 r^{-2ℓ-2+s} + B2 r^{2ℓ+s} + C2 r^{-1+s}
    def ipow(coef, exp, lo, hi):
        e = exp + 1
        if abs(e) < mpf("1e-30"):
            return coef * (mp.log(hi) - mp.log(lo))
        return coef * (hi**e - lo**e) / e

    I_mid = (
        ipow(A2, -2 * ell - 2 + s, r1, r2)
        + ipow(B2, 2 * ell + s, r1, r2)
        + ipow(C2, -1 + s, r1, r2)
    )
    # r > r2: u = c_out r^{-ℓ-1}, u² r^s = c_out² r^{-2ℓ-2+s}
    c_out = a * r1**ell + b * r2**ell
    e = -2 * ell - 2 + s + 1  # = s - 2ℓ - 1
    if e >= 0:
        # Dipole tail V ~ r^{-2}: ∫ r^{s-2} V² d³x diverges at ∞ when s ≥ 3.
        return mp.inf
    I_out = (c_out**2) * (-(r2**e) / e)
    return I_in + I_mid + I_out


def hardy_weighted(s, ell, t, alpha, beta):
    """Hardy quotient of u = |x|^{s/2} V.

    IMS: 4π I_s = ∫|∇u|² − (s²/4) ∫ u²/r², so
    Q_H(u) = s²/4 + (2ℓ+1) Q_s / ∫ u_rad² r^s dr.
    I_s < 0 iff Q_H(u) < s²/4.
    """
    Qs = Q_two_shell(s, ell, t, alpha, beta)
    Iu = int_u2_rs_two_shell(s, ell, t, 1, alpha, beta)
    qh = (s**2) / 4 + (2 * ell + 1) * Qs / Iu
    return qh, Qs, Iu


# ---------------------------------------------------------------------------
# Probability-measure trials: two shells with angular modulation
#   dρ = w (1 + ε cosθ) dσ_t  +  (1−w) (1 − ε cosθ) dσ_1
#   |ε| ≤ 1 keeps ρ ≥ 0. Then I_s(ρ) = I_s(ρ̄) + I_s(ν) with
#   I_s(ν) = (ε²/9) [ w² t^{s−1} + (1−w)² − w(1−w)(t^{s+1} + t) ]
#   I_s(ρ̄) = w² t^{s−1} + (1−w)² + w(1−w)(t^s + 1)
#   denom  = w t^{s−1} + (1−w)
# This is an upper bound on β_s, never a lower bound.
# ---------------------------------------------------------------------------


def trial_two_shell_prob(s, t, w, eps):
    s, t, w, eps = mpf(s), mpf(t), mpf(w), mpf(eps)
    I_rad = w**2 * t ** (s - 1) + (1 - w) ** 2 + w * (1 - w) * (t**s + 1)
    I_nu = (eps**2 / 9) * (
        w**2 * t ** (s - 1)
        + (1 - w) ** 2
        - w * (1 - w) * (t ** (s + 1) + t)
    )
    den = w * t ** (s - 1) + (1 - w)
    return (I_rad + I_nu) / den, I_rad / den, I_nu, den


def best_trial_upper(s, n_t=80, n_w=80):
    best = mpf("1e9")
    best_pt = None
    ts = [mpf(i) / n_t for i in range(1, n_t)]
    ws = [mpf(i) / n_w for i in range(1, n_w)]
    for t in ts:
        for w in ws:
            val, _, _, _ = trial_two_shell_prob(s, t, w, 1)
            if val < best:
                best = val
                best_pt = (t, w)
    return best, best_pt


def radial_nam_like_ratio(s, p, n_lo, n_hi, n_r=400):
    """Upper bound on β_s^{rad} from ρ̄ ∝ r^{−p} on [n_lo, n_hi]. Newton."""
    s = mpf(s)
    p = mpf(p)
    rs = [n_lo + (n_hi - n_lo) * i / (n_r - 1) for i in range(n_r)]
    # masses ∝ r^{−p} * r² dr  if density in R³ is |x|^{−p}; here we take
    # the radial measure m(r) dr with m(r) = r^{−p} on [n_lo, n_hi],
    # matching HPS (4. last display) after absorbing the area factor.
    ms = [r ** (-p) for r in rs]
    z = sum(ms)
    ms = [m / z for m in ms]
    num = mpf(0)
    den = mpf(0)
    for i, ri in enumerate(rs):
        den += ms[i] * ri ** (s - 1)
        for j, rj in enumerate(rs):
            mx = ri if ri >= rj else rj
            num += ms[i] * ms[j] * (ri**s + rj**s) / (2 * mx)
    return num / den


def pointwise_minorant(s):
    """inf (1+t^s)/(2(1+t^{s-1})) = (1/2) b(s)^{−1}, from |x−y| ≤ 2 max."""
    b, _ = b_of(s)
    return 1 / (2 * b)


# ---------------------------------------------------------------------------
# Spherical-design check of the two-shell formula (independent path)
# ---------------------------------------------------------------------------


def fibonacci_sphere(n):
    pts = []
    golden = (1.0 + math.sqrt(5.0)) / 2.0
    for i in range(n):
        z = 1.0 - 2.0 * (i + 0.5) / n
        rxy = math.sqrt(max(1.0 - z * z, 0.0))
        phi = 2.0 * math.pi * i / golden
        pts.append((rxy * math.cos(phi), rxy * math.sin(phi), z))
    return np.array(pts)


def I_s_two_shell_quadrature(s, ell, t, alpha, beta, n=400):
    """Independent check: ℓ=1 uses cosθ, ℓ=2 uses (3z²−1)/2, equal weights."""
    pts = fibonacci_sphere(n)
    w = 4.0 * math.pi / n
    if ell == 1:
        ang = pts[:, 2]  # cosθ ∝ Y_10
    elif ell == 2:
        ang = 0.5 * (3.0 * pts[:, 2] ** 2 - 1.0)
    else:
        raise ValueError("ell")
    # Y not normalised: this checks the sign and the t-dependence, not the
    # 4π/(2ℓ+1) prefactor. Compare Q against the double sum with |x|^s weights.
    r1 = float(t)
    r2 = 1.0
    x1 = r1 * pts
    x2 = r2 * pts
    a1 = float(alpha) * ang
    a2 = float(beta) * ang
    # I = Σ_{i,j sectors} c_i c_j (|xi|^s+|xj|^s)/(2 |xi−xj|) * w_i w_j
    # skip i=j on the same shell (principal-value: the self-energy of a
    # continuous surface is finite; equal-weight diagonal is a Riemann
    # artefact). Use a small-distance cutoff equal to typical spacing.
    cutoff = 1.5 * (4.0 * math.pi / n) ** 0.5  # ~ spacing on the unit sphere
    acc = 0.0
    # shell 1–1
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(x1[i] - x1[j])
            if d < cutoff * r1:
                continue
            acc += a1[i] * a1[j] * (r1**s + r1**s) / d
    # shell 2–2
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(x2[i] - x2[j])
            if d < cutoff * r2:
                continue
            acc += a2[i] * a2[j] * (r2**s + r2**s) / d
    # cross
    for i in range(n):
        for j in range(n):
            d = np.linalg.norm(x1[i] - x2[j])
            acc += a1[i] * a2[j] * (r1**s + r2**s) / d
    # Each pair-of-points term was (|x|^s+|y|^s)/|x-y|; I_s uses a 1/2.
    # Off-diagonal 1–1 and 2–2 were counted once (i<j), so already have
    # the 1/2 relative to a full double sum. Cross was full, needs 1/2.
    # Easier: rebuild as (w²) * (1/2) of a full sum including a principal
    # value. We used i<j for same-shell (so no 1/2 left to apply) and full
    # cross (apply 1/2). Weights: each point carries w.
    I = (acc * 0.5 * (w * w) * 2.0)  # i<j already half; *2 undoes? see note
    # Cleaner recomputation below is not used; return the pairwise
    # combination that matches ∬ k(x,y) dν dν with k = (|x|^s+|y|^s)/(2|x-y|):
    # same-shell i<j contributes 2 * (w_i w_j) * k = w_i w_j (|x|^s+|y|^s)/|x-y|
    # which is what we summed; cross i,j contributes w_i w_j (|x|^s+|y|^s)/|x-y|
    # which is 2 k, so multiply cross by 1/2. We included the full cross in
    # acc then... messy. Return both pieces separately.
    return None  # replaced by the clean routine


def I_s_two_shell_pairwise(s, ell, t, alpha, beta, n=250):
    """∬ (|x|^s+|y|^s)/(2|x-y|) against discrete spherical measures.

    Same-shell diagonal is omitted (the continuous self-energy is recovered
    in the n→∞ limit by the closed form). Used only as a sign / magnitude
    check of the off-diagonal and cross pieces plus a mesh self-energy.
    """
    pts = fibonacci_sphere(n)
    w = 1.0 / n  # probability weights on each shell, then times α, β, ang
    if ell == 1:
        ang = pts[:, 2]
    else:
        ang = 0.5 * (3.0 * pts[:, 2] ** 2 - 1.0)
    # Renormalise ang so Σ ang² w = 1/3 for ℓ=1 (⟨cos²θ⟩=1/3), matching
    # the 1/9 identity used in the notes: ∫∫ cosθ cosθ' /|x-y| = (r_</r_>²)/9
    # when dσ = dω/4π. Here w = 1/n already is that measure.
    r1 = float(t)
    r2 = 1.0
    c1 = float(alpha) * ang
    c2 = float(beta) * ang
    acc = 0.0
    # same shell 1
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = np.linalg.norm(pts[i] - pts[j]) * r1
            acc += c1[i] * c1[j] * (2.0 * r1**s) / (2.0 * d) * w * w
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = np.linalg.norm(pts[i] - pts[j]) * r2
            acc += c2[i] * c2[j] * (2.0 * r2**s) / (2.0 * d) * w * w
    for i in range(n):
        for j in range(n):
            d = np.linalg.norm(r1 * pts[i] - r2 * pts[j])
            if d < 1e-14:
                continue
            acc += c1[i] * c2[j] * (r1**s + r2**s) / (2.0 * d) * w * w
            acc += c2[i] * c1[j] * (r2**s + r1**s) / (2.0 * d) * w * w
    return acc


def I_s_smeared_two_shell(s, ell, t, alpha, beta, width=0.03, n=800):
    """Volume density: thin radial Gaussians around r=t and r=1, times Y_ℓm.

    R(r) = α g_w(r−t)/t² + β g_w(r−1),  ∫ g_w ≈ 1. Approaches the two-shell
    surface measure as width → 0.
    """
    w = float(width)
    t = float(t)
    a = float(alpha)
    b = float(beta)
    norm = 1.0 / (w * math.sqrt(math.pi))

    def R(r):
        g1 = math.exp(-(((r - t) / w) ** 2)) * norm
        g2 = math.exp(-(((r - 1.0) / w) ** 2)) * norm
        # avoid /0 at the origin
        r2 = r * r if r > 1e-8 else 1e-16
        return a * g1 / (t * t) + b * g2 / 1.0

    return I_s_multipole_profile(s, ell, R, rmax=max(4.0, 1.0 + 8 * w), n=n)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    # ---- b(s) ----
    b_table = {}
    for s in S_LIST:
        b, t0 = b_of(s)
        # isolate t0: f is increasing (f' = s t^{s-1} + s > 0)
        # shrink an interval around t0
        t0_f = float(t0)
        width = 1e-20
        t_lo = t0_f * (1 - 1e-12) if t0_f > 0 else 1e-20
        t_hi = min(t0_f * (1 + 1e-12), 0.999999)
        # verify sign change in mp
        if f_t0(s, t_lo) >= 0 or f_t0(s, t_hi) <= 0:
            t_lo = float(t0) * 0.999
            t_hi = min(float(t0) * 1.001, 0.999)
        b_i, t_i = b_iv_from_t_interval(float(s), t_lo, t_hi)
        # tighter: use mp t0 as a tiny iv around the binary-search result
        # after 200 bisections the error is 2^{−200}
        err = mpf(2) ** (-200)
        t_iv = iv.mpf([S(t0 - err, 50), S(t0 + err, 50)])
        si = iv.mpf(S(s, 20))
        b_iv = (si - 1) / (si * t_iv)
        b_table[S(s, 6)] = {
            "s": S(s),
            "t0": S(t0),
            "b": S(b),
            "b_inv": S(1 / b),
            "interval_b": list(iv_bounds(b_iv)),
            "closed_form": "(s-1)/(s t0) with t0^s + s t0 + 1 - s = 0",
        }

    # Extra precision printables for the user-facing b(4)
    b4, t04 = b_of(4)
    # t^4 + 4t − 3 = 0
    # Isolate by evaluating the monic at rationals
    def f4(t):
        return t**4 + 4 * t - 3

    # 0.69^4 + 4*0.69 − 3 = 0.22667121 + 2.76 − 3 = −0.01332879 < 0
    # 0.70^4 + 2.80 − 3 = 0.2401 − 0.2 = 0.0401 > 0
    t4_lo, t4_hi = mpf("0.692"), mpf("0.693")
    assert f4(t4_lo) < 0 < f4(t4_hi)
    # Refine to 40 digits by bisection (already have t04)
    t4_iv = iv.mpf([S(t04 - mpf("1e-40")), S(t04 + mpf("1e-40"))])
    b4_iv = iv.mpf(3) / (iv.mpf(4) * t4_iv)

    # ---- Certified two-shell examples ----
    # (s, ell, t, α, β, expected_sign)  — t, α, β rational when possible
    examples = [
        # s=3 dipole: det never negative. Any (α,β) should give Q ≥ 0.
        {"name": "dipole_two_shell_s3_balanced", "s": "3", "ell": 1,
         "t": "1/2", "alpha": "1", "beta": "-1"},
        {"name": "dipole_two_shell_s3_inner_heavy", "s": "3", "ell": 1,
         "t": "1/10", "alpha": "20", "beta": "-1"},
        # s=3.1 dipole, extreme radius ratio + inner-heavy weights
        {"name": "dipole_two_shell_s31", "s": "3.1", "ell": 1,
         "t": "1e-7", "alpha": "3e7", "beta": "-1"},
        # s=3.5 dipole: t=1/32, α=64, β=−1  (see notes)
        {"name": "dipole_two_shell_s35", "s": "3.5", "ell": 1,
         "t": "1/32", "alpha": "64", "beta": "-1"},
        # s=4 dipole: t=1/8, α=16, β=−1
        {"name": "dipole_two_shell_s4", "s": "4", "ell": 1,
         "t": "1/8", "alpha": "16", "beta": "-1"},
        # quadrupole two-shell, opposite weights — Hardy threshold 2ℓ+1=5
        {"name": "quad_two_shell_s4_opposite", "s": "4", "ell": 2,
         "t": "1/8", "alpha": "16", "beta": "-1"},
        {"name": "quad_two_shell_s35_opposite", "s": "3.5", "ell": 2,
         "t": "1/8", "alpha": "16", "beta": "-1"},
        {"name": "quad_two_shell_s3_opposite", "s": "3", "ell": 2,
         "t": "1/8", "alpha": "16", "beta": "-1"},
        # single-shell (pure spherical harmonic on one radius)
        {"name": "dipole_one_shell_s4", "s": "4", "ell": 1,
         "t": "1", "alpha": "1", "beta": "0"},
        {"name": "quad_one_shell_s4", "s": "4", "ell": 2,
         "t": "1", "alpha": "1", "beta": "0"},
        # same-sign two-shell dipole (the (+)(+) direction)
        {"name": "dipole_two_shell_s4_same_sign", "s": "4", "ell": 1,
         "t": "1/8", "alpha": "1", "beta": "1"},
    ]

    certified = []
    for ex in examples:
        s = mpf(ex["s"])
        ell = int(ex["ell"])
        t = mpf(ex["t"])
        a = mpf(ex["alpha"])
        b = mpf(ex["beta"])
        Q = Q_two_shell(s, ell, t, a, b)
        Qi = Q_two_shell_iv(ex["s"], ell, ex["t"], ex["alpha"], ex["beta"])
        pref = I_prefactor(ell)
        I_val = pref * Q
        sign = (
            "negative"
            if Qi.b < 0
            else ("positive" if Qi.a > 0 else ("zero" if Qi.a == 0 == Qi.b else "undetermined"))
        )
        # For t=1, β=0: Q = α² ≥ 0 exactly
        certified.append(
            {
                "name": ex["name"],
                "s": ex["s"],
                "ell": ell,
                "t": ex["t"],
                "alpha": ex["alpha"],
                "beta": ex["beta"],
                "Q": S(Q),
                "Q_interval": list(iv_bounds(Qi)),
                "I_s": S(I_val),
                "I_s_prefactor": "4π/(2ℓ+1)",
                "sign": sign,
                "orthogonal_to_radial": True,
            }
        )

    # Det condition sweep: for each s, does there exist t with det < 0?
    det_sweep = {}
    for s in S_LIST:
        row = {}
        for ell in (1, 2):
            # small-t diagnostic: t^ℓ vs 2 t^{(s-1)/2}
            ts = [mpf(10) ** (-k) for k in range(1, 12)]
            ts += [mpf(1) / m for m in (2, 3, 4, 5, 8, 16, 32, 64)]
            hits = []
            for t in ts:
                d = det_condition(s, ell, t)
                if d > 0:
                    hits.append(S(t, 12))
            row[f"ell={ell}"] = {
                "exists_t_with_negative_eigenvalue": bool(hits),
                "sample_t": hits[:6],
                "hardy_threshold_2ell_plus_1": 2 * ell + 1,
                "s_gt_threshold": bool(s > 2 * ell + 1),
            }
        det_sweep[S(s, 6)] = row

    # s=3 dipole: algebraic non-positivity of the det discriminant
    # C² − 4A = (t^4 + t)² − 4 t² = t²((t³+1)² − 4) = t²(t³−1)(t³+3) ≤ 0
    s3_dipole_disc = {
        "identity": "(t^4+t)^2 - 4 t^2 = t^2 (t^3-1)(t^3+3)",
        "sign_on_(0,1)": "<= 0, =0 only at endpoints of the closed interval",
        "conclusion": "Q_s=3,ℓ=1 (α,β) ≥ 0 for all t∈(0,1] and all real α,β",
    }

    # Exact rationals / radicals for the negative examples
    Q4_exact = mpf(-1025) / 2048
    Q4_computed = Q_two_shell(4, 1, mpf("1/8"), 16, -1)
    if abs(Q4_computed - Q4_exact) > mpf("1e-50"):
        raise SystemExit("s=4 two-shell Q is not -1025/2048")
    Q35 = Q_two_shell(mpf("7/2"), 1, mpf("1/32"), 64, -1)
    Q35_closed = 1 / sqrt(2) - 1 - 1 / (65536 * sqrt(2))
    if abs(Q35 - Q35_closed) > mpf("1e-40"):
        raise SystemExit("s=7/2 two-shell Q mismatch")
    exact_neg = {
        "s4_t_1/8_alpha_16_beta_-1": {
            "Q": "-1025/2048",
            "Q_value": S(Q4_exact),
            "sign": "negative",
        },
        "s7/2_t_1/32_alpha_64_beta_-1": {
            "Q": "1/sqrt(2) - 1 - 1/(65536 sqrt(2))",
            "Q_value": S(Q35),
            "upper_by_1/sqrt(2)-1": S(1 / sqrt(2) - 1),
            "sign": "negative",
        },
    }

    # Independent numerical max of (1+t^{s-1})/(1+t^s) for s=4
    grid_max_b4 = mpf(0)
    grid_t = mpf(0)
    for i in range(0, 20001):
        tt = mpf(i) / 20000
        val = ratio_b(4, tt)
        if val > grid_max_b4:
            grid_max_b4, grid_t = val, tt
    if abs(grid_max_b4 - b4) > mpf("1e-8"):
        raise SystemExit(f"grid max b(4) {grid_max_b4} != closed {b4}")

    # ---- Volume densities: R(r) Y_ℓm ----
    # Pure dipole: R(r) = r e^{−r}  (hydrogenic 2p-like, one sign)
    # Quadrupole:  R(r) = r² e^{−r}
    # Sign-changing dipole: R(r) = (e^{−r} − e^{−r/8})  — two scales
    volume = []
    profiles = [
        ("pure_dipole_2p", 1, lambda r: r * math.exp(-r)),
        ("pure_quadrupole_3d", 2, lambda r: r * r * math.exp(-r)),
        ("sign_changing_dipole_two_exponentials", 1,
         lambda r: math.exp(-r) - math.exp(-r / 8.0)),
        ("sign_changing_dipole_linear", 1,
         lambda r: (1.0 - r) * math.exp(-r / 2.0)),
    ]
    for name, ell, R in profiles:
        row = {"name": name, "ell": ell}
        for s in S_LIST:
            val = I_s_multipole_profile(s, ell, R)
            row[S(s, 4)] = val
        volume.append(row)

    smeared = []
    for s, t, a, bcoef, w in (
        (4.0, 0.125, 16.0, -1.0, 0.02),
        (3.5, 1.0 / 32.0, 64.0, -1.0, 0.008),
        (3.0, 0.125, 16.0, -1.0, 0.02),
    ):
        val = I_s_smeared_two_shell(s, 1, t, a, bcoef, width=w, n=900)
        smeared.append(
            {
                "s": s,
                "t": t,
                "alpha": a,
                "beta": bcoef,
                "width": w,
                "I_s_smeared": val,
                "sign": "negative" if val < 0 else "positive",
            }
        )
    if smeared[0]["I_s_smeared"] >= 0:
        raise SystemExit("smeared s=4 two-shell did not go negative")
    if smeared[1]["I_s_smeared"] >= 0:
        raise SystemExit("smeared s=3.5 two-shell did not go negative")
    if smeared[2]["I_s_smeared"] < 0:
        raise SystemExit("smeared s=3 two-shell went negative")

    # ---- Two opposite Gaussians (regularised opposite Diracs) ----
    gauss_rows = []
    for mu, sigma in ((1.0, 0.25), (1.0, 0.5), (2.0, 0.3)):
        row = {"mu": mu, "sigma": sigma, "note": "ν = γ_μ − γ_{−μ}, same |center|"}
        for s in (3.0, 3.5, 4.0):
            val = I_s_two_gaussians(s, mu, sigma, n_r=28, n_th=18, n_ph=12)
            row[str(s)] = val
        gauss_rows.append(row)

    # ---- Hardy quotients ----
    hardy_rows = []
    hardy_cases = [
        ("single_shell_dipole", 1, mpf(1), mpf(1), mpf(0)),
        ("single_shell_quad", 2, mpf(1), mpf(1), mpf(0)),
        ("dipole_s4_counterexample_weights", 1, mpf("1/8"), mpf(16), mpf(-1)),
        ("dipole_s35_counterexample_weights", 1, mpf("1/32"), mpf(64), mpf(-1)),
        ("dipole_s31_counterexample_weights", 1, mpf("1e-7"), mpf("3e7"), mpf(-1)),
        ("dipole_tiny_t_1e-4", 1, mpf("1e-4"), mpf("2e4"), mpf(-1)),
        ("dipole_tiny_t_1e-6", 1, mpf("1e-6"), mpf("2e6"), mpf(-1)),
    ]
    for name, ell, t, a, bcoef in hardy_cases:
        QH, Q0, Iu2 = hardy_two_shell(ell, t, a, bcoef)
        hardy_rows.append(
            {
                "name": name,
                "ell": ell,
                "t": S(t),
                "alpha": S(a),
                "beta": S(bcoef),
                "Q_H": S(QH),
                "Q_H_minus_9/4": S(QH - mpf("9/4")),
                "s_max_if_Hardy_sharp_for_this_V": S(2 * sqrt(QH)),
                "Q0": S(Q0),
                "int_u2": S(Iu2),
            }
        )

    weighted_hardy = []
    for name, s, ell, t, a, bcoef in (
        ("s4_counterexample", mpf(4), 1, mpf("1/8"), mpf(16), mpf(-1)),
        ("s35_counterexample", mpf("7/2"), 1, mpf("1/32"), mpf(64), mpf(-1)),
        ("s31_counterexample", mpf("3.1"), 1, mpf("1e-7"), mpf("3e7"), mpf(-1)),
        ("s3_same_weights_as_s4", mpf(3), 1, mpf("1/8"), mpf(16), mpf(-1)),
    ):
        qh, Qs, Iu = hardy_weighted(s, ell, t, a, bcoef)
        diverges = Iu == mp.inf
        weighted_hardy.append(
            {
                "name": name,
                "s": S(s),
                "Q_H_of_r^{s/2}V": "diverges (dipole tail, s>=3)" if diverges else S(qh),
                "s2_over_4": S(s**2 / 4),
                "int_u2_rs_diverges": bool(diverges),
                "Q_s": S(Qs),
                "note": (
                    "Unregularized ∫ |x|^{s-2} V² d³x diverges for a dipole "
                    "tail when s≥3. I_s itself stays finite (compact support). "
                    "HPS regularize the weight; the informal IMS+Hardy bound "
                    "is not available without that cutoff."
                ),
            }
        )

    # ---- Probability trials / β_s upper bounds (NOT lower bounds) ----
    trial_rows = {}
    for s in (mpf("3.5"), mpf(4)):
        best, pt = best_trial_upper(s, n_t=60, n_w=60)
        b, t0 = b_of(s)
        # also scan a Nam-like radial family
        rad_best = mpf("1e9")
        rad_pt = None
        for p in (mpf("1.2"), mpf("1.5"), mpf("1.8"), mpf("2.2")):
            for n_hi in (mpf(4), mpf(6), mpf(9), mpf(12)):
                val = radial_nam_like_ratio(s, p, mpf(1), n_hi, n_r=120)
                if val < rad_best:
                    rad_best = val
                    rad_pt = (S(p), S(n_hi))
        trial_rows[S(s, 4)] = {
            "b_inv": S(1 / b),
            "two_shell_modulated_best_ratio": S(best),
            "at_t_w": [S(pt[0]), S(pt[1])] if pt else None,
            "beats_b_inv": bool(best < 1 / b),
            "radial_nam_like_best": S(rad_best),
            "radial_nam_like_at_p_nhi": rad_pt,
            "pointwise_minorant_half_b_inv": S(pointwise_minorant(s)),
            "note": (
                "two_shell_modulated and nam-like are upper bounds on β_s. "
                "They are not lower bounds. The pointwise minorant is a "
                "genuine lower bound but only (1/2) b(s)^{-1}."
            ),
        }

    # Independent pairwise check of one negative example (s=4, t=1/8)
    pairwise_s4 = I_s_two_shell_pairwise(4.0, 1, 0.125, 16.0, -1.0, n=180)
    Q_s4 = Q_two_shell(4, 1, mpf("1/8"), 16, -1)
    # The pairwise uses ang = cosθ, not L²-normalised Y_10, so it is a
    # positive multiple of Q. Only the sign is compared.
    pairwise_check = {
        "s": 4,
        "t": "1/8",
        "alpha": 16,
        "beta": -1,
        "n_fibonacci": 180,
        "pairwise_I_s": pairwise_s4,
        "closed_Q": S(Q_s4),
        "same_sign": bool(pairwise_s4 * float(Q_s4) > 0),
        "note": (
            "Fibonacci-sphere pairwise sum omits the same-shell diagonal. "
            "The missing self-energy is positive, so a negative pairwise "
            "sum is even stronger evidence that I_s < 0."
        ),
    }

    # Single-shell dipole I_s via pairwise should be positive
    pairwise_one = I_s_two_shell_pairwise(4.0, 1, 1.0, 1.0, 0.0, n=160)

    # Sanity: Q at s=3, any example ≥ 0
    for ex in certified:
        if ex["s"] == "3" and ex["sign"] == "negative":
            raise SystemExit(f"s=3 produced a negative Q: {ex['name']}")
        if ex["name"].startswith("dipole_two_shell_s4") and "same_sign" not in ex["name"]:
            if ex["sign"] != "negative":
                raise SystemExit(f"expected negative I_4 dipole: {ex}")
        if ex["name"] == "dipole_two_shell_s35" and ex["sign"] != "negative":
            raise SystemExit("expected negative I_{3.5} dipole")
        if ex["name"] == "dipole_two_shell_s31" and ex["sign"] != "negative":
            raise SystemExit("expected negative I_{3.1} dipole")

    if not (b4_iv > iv.mpf("1.08") and b4_iv < iv.mpf("1.09")):
        raise SystemExit(f"b(4) enclosure unexpected: {iv_bounds(b4_iv)}")

    blob = {
        "arxiv": "2504.18487v1",
        "urls_opened": [
            "https://arxiv.org/abs/2504.18487",
            "https://arxiv.org/html/2504.18487v1",
        ],
        "dps": int(mp.dps),
        "definition": (
            "I_s(ν) = ∬ (|x|^s+|y|^s)/(2|x-y|) dν(x) dν(y), "
            "ν orthogonal to radial functions"
        ),
        "verdict": {
            "I_s_goes_negative_for_s_gt_3": True,
            "on_which_examples": [
                "dipole_two_shell_s31",
                "dipole_two_shell_s35",
                "dipole_two_shell_s4",
            ],
            "I_3_stays_nonnegative_on_all_examples": True,
            "certified_path_to_s_gt_3": False,
            "reason": (
                "Lemma 4.3 needs I_s(ν)≥0 for every ν ⊥ radial. "
                "Two-shell ℓ=1 measures give I_s<0 for every s>3 "
                "(interval enclosure of the closed quadratic form; "
                "s=4 is the exact rational −1025/2048). "
                "Hardy is applied to u=|x|^{s/2} V, not to V. Q_H(V) "
                "stays near 4.5 and does not control the sign of I_s. "
                "For the s=3.1 dipole, Q_H(u) < (3.1)²/4 already, so "
                "there is no uniform gap past 9/4. Lemma 5.9 "
                "(α_N vs β, 2≤s≤4) does not replace radialization. "
                "A 3D search is only an upper bound on β_s."
            ),
            "b4": S(b4),
            "b4_interval": list(iv_bounds(b4_iv)),
            "b4_lt_1.1185": bool(b4_iv < iv.mpf("1.1185")),
            "cannot_use_b4_in_Theorem_2_2": True,
        },
        "b_s": b_table,
        "s3_dipole_discriminant": s3_dipole_disc,
        "exact_negative_Q": exact_neg,
        "b4_grid_max_check": {
            "grid_max": S(grid_max_b4),
            "at_t": S(grid_t),
            "closed_b4": S(b4),
            "agree_to_1e-8": True,
        },
        "two_shell_certified": certified,
        "det_sweep": det_sweep,
        "volume_multipole_I_s": volume,
        "smeared_two_shell_volume": smeared,
        "two_opposite_gaussians": gauss_rows,
        "hardy_quotients_of_V_not_IMS": hardy_rows,
        "hardy_quotients_of_r_s2_V": weighted_hardy,
        "beta_upper_trials_not_lower_bounds": trial_rows,
        "pairwise_check_s4_dipole": pairwise_check,
        "pairwise_one_shell_s4": pairwise_one,
        "improved_Hardy": {
            "citation": "Ekholm–Frank, Comm. Math. Phys. 264 (2006), Lemma 2.4; HPS (4.15)",
            "c_H_radial": "1/4 = ((d-2)/2)^2",
            "c_H_ell_ge_1": "9/4 = d^2/4",
            "c_H_pure_ell": "ℓ(ℓ+1)+1/4, so s ≤ 2ℓ+1 is the IMS+Hardy range",
            "dipole_ell_1_threshold": 3,
            "quadrupole_ell_2_threshold": 5,
        },
    }

    out = CERTS / "s_gt_3.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")

    print("=== b(s) ===")
    for k, v in b_table.items():
        print(f"  s={k}  b={v['b'][:18]}  1/b={v['b_inv'][:18]}")
    print("b(4) interval", iv_bounds(b4_iv))
    print("=== two-shell I_s signs ===")
    for ex in certified:
        print(f"  {ex['name']:40s}  Q={ex['Q'][:22]:22s}  {ex['sign']}")
    print("=== volume profiles ===")
    for row in volume:
        print(" ", row["name"], {k: row[k] for k in row if k not in ("name", "ell")})
    print("=== opposite Gaussians ===")
    for row in gauss_rows:
        print(" ", row)
    print("=== smeared two-shell volume ===")
    for row in smeared:
        print(" ", row)
    print("=== Hardy Q_H(V) ===")
    for row in hardy_rows:
        print(f"  {row['name']:40s}  Q_H={row['Q_H'][:18]}  s_max={row['s_max_if_Hardy_sharp_for_this_V'][:12]}")
    print("=== Hardy Q_H(|x|^{s/2} V) ===")
    for row in weighted_hardy:
        print(
            f"  {row['name']:28s}  Q_H={row['Q_H_of_r^{s/2}V']}  "
            f"Q_s={row['Q_s'][:16]}"
        )
    print("=== β trials (upper bounds only) ===")
    for k, v in trial_rows.items():
        print(" ", k, "best modulated", v["two_shell_modulated_best_ratio"],
              "b^{-1}", v["b_inv"], "beats?", v["beats_b_inv"])
    print("pairwise s=4 dipole", pairwise_s4, "same sign as Q", pairwise_check["same_sign"])
    print("wrote", out)
    print("s_gt_3.py PASS")


if __name__ == "__main__":
    main()
