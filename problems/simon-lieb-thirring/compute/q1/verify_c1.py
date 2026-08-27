#!/usr/bin/env python3
"""Conservative panel-sum upper bound for the FHJN functional C_1 (d=1).

    C_1[f,φ] = sqrt(a) * (1/2) * ∫_0^∞ (1-g(t))² t^{-3/2} dt
    a = ∫ φ²,   g(t) = ∫ φ(s) f(s t) ds,   ∫ f² = ∫ φ = 1,   f,φ ≥ 0.

Family:
    f(t) = (1 + μ t^α)^{-β}     (α>0, β>0; decreasing, f(0)=1)
    φ_raw(s) = (1 - (s/S)^γ)^δ / (1 + ε s)^κ   on [0,S], zero elsewhere
    φ = φ_raw / ∫φ_raw.

Every number written as an upper (resp. lower) bound is obtained from a
monotone panel inequality plus a directed float pad. A quadrature float
is not a bound.

On each t-panel [t_i, t_{i+1}]:
    (1-g)² is increasing (g decreasing, 0 ≤ g ≤ 1),
    t^{-3/2} is decreasing,
    so the integrand ≤ (1 - g(t_{i+1}))² / t_i^{3/2}.
The panel contribution is that height times the panel length.

1-g(t) = ∫ φ_raw(s) (1-f(s t)) ds / ∫ φ_raw. On each s-panel φ_raw is
decreasing and 1-f(s t) is increasing, so the product is at most
φ_raw(s_left) (1-f(s_right t)). That gives a rigorous upper bound on
1-g without subtracting two near-1 quantities.

μ is taken large enough that ∫ f² ≤ 1 (μ_upper ≥ μ_exact). The resulting
pair is not L²-normalised, but scaling f up to unit L² only decreases C_1,
so the value at μ_upper is a valid upper bound on the infimum.

Replay:
    python3 verify_c1.py
    rustc -O -o verify_c1_bin verify_c1.rs && ./verify_c1_bin ../certs/c1_lemma11_second.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CERTS = HERE.parent / "certs"

# Directed-rounding pad. libm pow/exp/log are treated as < 1 ulp plus this
# relative/absolute blanket. Sums get an extra n * ABS term.
REL = 2.0e-14
ABS = 1.0e-15

PUBLISHED_L = 1.456  # FHJN JEMS 2021 / arXiv:1808.09017 display bound

# Exact comparison (9 √3 / 4) C_1 < 1456/1000 = 182/125
# ⇔ 243 C_1² < 728² / 125²  ⇔  C_1² * 3796875 < 529984.
_L_CMP_NUM = 529984  # 728**2
_L_CMP_DEN = 3796875  # 243 * 125**2

PAPER_SECOND = {
    "name": "lemma11_second",
    "alpha": 4.5,
    "beta": 0.25,
    "gamma": 0.36,
    "delta": 2.1,
    "eps": 1.0,
    "kappa": 1.0,
    "support": 1.0,
}


def up(x: float) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("non-finite in up()")
    if x <= 0.0:
        return ABS
    return math.nextafter(x * (1.0 + REL) + ABS, math.inf)


def down(x: float) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("non-finite in down()")
    if x <= 0.0:
        return 0.0
    return max(0.0, math.nextafter(x * (1.0 - REL) - ABS, 0.0))


def up_arr(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return np.nextafter(np.maximum(x, 0.0) * (1.0 + REL) + ABS, np.inf)


def down_arr(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    v = np.maximum(x, 0.0) * (1.0 - REL) - ABS
    return np.maximum(0.0, np.nextafter(v, 0.0))


def sum_up(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float64)
    total = float(np.sum(values))
    if not math.isfinite(total):
        raise ValueError("non-finite panel sum")
    return up(total) + float(values.size) * ABS


def sqrt3_upper() -> float:
    """Strict upper bound on √3, checked by integer arithmetic."""
    # 972222024395337 / 561477268726881 is not needed; start from math.sqrt
    # and walk up until the square exceeds 3 in exact integer-ratio form
    # via Decimal.
    getcontext().prec = 60
    s = Decimal.from_float(math.sqrt(3.0))
    three = Decimal(3)
    while s * s <= three:
        s = s + Decimal("1e-20")
    return float(s)


def beats_published_1456(c1_upper: float) -> bool:
    """True iff it is proved that (9 √3 / 4) c1_upper < 1.456."""
    getcontext().prec = 80
    c = Decimal.from_float(float(c1_upper))
    return (c * c) * Decimal(_L_CMP_DEN) < Decimal(_L_CMP_NUM)


def k_over_kcl_lower(c1_upper: float) -> float:
    c2 = up(c1_upper * c1_upper)
    return down(16.0 / up(243.0 * c2))


def l_over_lcl_upper(c1_upper: float) -> float:
    return up((9.0 * sqrt3_upper() / 4.0) * c1_upper)


# ---------------------------------------------------------------------------
# f and φ
# ---------------------------------------------------------------------------


def f_lower_arr(t: np.ndarray, mu_upper: float, alpha: float, beta: float) -> np.ndarray:
    """Pointwise lower bound of (1 + μ t^α)^{-β} using μ ≤ μ_upper."""
    t = np.asarray(t, dtype=np.float64)
    out = np.ones_like(t)
    mask = t > 0.0
    if not np.any(mask):
        return out
    tm = t[mask]
    # Overestimate t^α (larger argument ⇒ smaller f).
    ta = np.exp(alpha * np.log(tm))
    ta = up_arr(ta)
    arg = up_arr(mu_upper * ta)
    base = up_arr(1.0 + arg)
    val = np.exp(-beta * np.log(base))
    out[mask] = down_arr(val)
    return out


def h_mu_upper_arr(u: np.ndarray, alpha: float, two_beta: float) -> np.ndarray:
    """Upper bound of (1 + u^α)^{-2β} (used for I_f)."""
    u = np.asarray(u, dtype=np.float64)
    # Smaller u^α ⇒ larger h, so underestimate the power.
    ua = np.exp(alpha * np.log(np.maximum(u, 1e-300)))
    ua_dn = down_arr(ua)
    val = np.exp(-two_beta * np.log1p(ua_dn))
    return up_arr(val)


def phi_raw_arr(
    s: np.ndarray,
    support: float,
    gamma: float,
    delta: float,
    eps: float,
    kappa: float,
    which: str,
) -> np.ndarray:
    """Directed evaluation of φ_raw. which is 'lower' or 'upper'."""
    s = np.asarray(s, dtype=np.float64)
    out = np.zeros_like(s)
    if which == "upper":
        out[s <= 0.0] = 1.0
    else:
        out[s <= 0.0] = down(1.0)
    mid = (s > 0.0) & (s < support)
    if not np.any(mid):
        return out
    sm = s[mid]
    ratio = sm / support
    if which == "upper":
        # Overestimate (1 - r^γ)^δ: underestimate r^γ.
        rg = down_arr(np.exp(gamma * np.log(np.maximum(ratio, 1e-300))))
        rg = np.minimum(rg, np.nextafter(1.0, 0.0))
        one = up_arr(1.0 - rg)
        num = up_arr(np.exp(delta * np.log(np.maximum(one, 1e-300))))
        den = down_arr(np.exp(kappa * np.log1p(np.maximum(eps, 0.0) * sm)))
        den = np.maximum(den, 1e-300)
        out[mid] = num / den
    else:
        rg = up_arr(np.exp(gamma * np.log(np.maximum(ratio, 1e-300))))
        one = 1.0 - rg
        num = np.zeros_like(sm)
        ok = one > 0.0
        if np.any(ok):
            num[ok] = down_arr(np.exp(delta * np.log(one[ok])))
        den = up_arr(np.exp(kappa * np.log1p(np.maximum(eps, 0.0) * sm)))
        vals = np.zeros_like(sm)
        good = ok & (den > 0.0)
        vals[good] = num[good] / den[good]
        out[mid] = np.maximum(vals, 0.0)
    out[s >= support] = 0.0
    return out


# ---------------------------------------------------------------------------
# grids
# ---------------------------------------------------------------------------


def log_nodes(a: float, b: float, n_panels: int) -> np.ndarray:
    if a <= 0.0 or b <= a or n_panels < 1:
        raise ValueError("bad log-grid")
    return np.logspace(math.log10(a), math.log10(b), n_panels + 1)


def hybrid_t_grid(
    t_min: float,
    t_steep_lo: float,
    t_steep_hi: float,
    t_drop_hi: float,
    T: float,
    n_small: int,
    n_steep: int,
    n_drop: int,
    n_tail: int,
) -> np.ndarray:
    a = log_nodes(t_min, t_steep_lo, n_small)
    b = log_nodes(t_steep_lo, t_steep_hi, n_steep)
    c = log_nodes(t_steep_hi, t_drop_hi, n_drop)
    d = log_nodes(t_drop_hi, T, n_tail)
    return np.concatenate([a, b[1:], c[1:], d[1:]])


def uniform_s_grid(support: float, n_panels: int) -> np.ndarray:
    return np.linspace(0.0, support, n_panels + 1)


# ---------------------------------------------------------------------------
# panel bounds
# ---------------------------------------------------------------------------


def bound_I_f(alpha: float, beta: float, U: float, n_lin: int, n_log: int) -> dict:
    """Upper bound of I_f = ∫_0^∞ (1+u^α)^{-2β} du. μ = I_f^α."""
    if alpha <= 0.0 or beta <= 0.0:
        raise ValueError("alpha, beta must be positive")
    two_ab = 2.0 * alpha * beta
    if two_ab <= 1.0:
        raise ValueError("need 2αβ > 1 for ∫ f² < ∞")
    two_beta = 2.0 * beta
    u = np.linspace(0.0, 1.0, n_lin + 1)
    h = np.empty(n_lin + 1)
    h[0] = 1.0
    h[1:] = h_mu_upper_arr(u[1:], alpha, two_beta)
    core0 = sum_up(h[:-1] * np.diff(u))
    v = log_nodes(1.0, U, n_log)
    hv = h_mu_upper_arr(v, alpha, two_beta)
    core1 = sum_up(hv[:-1] * np.diff(v))
    tail = up((U ** (1.0 - two_ab)) / (two_ab - 1.0))
    I_upper = up(core0 + core1 + tail)
    mu_upper = up(I_upper**alpha)
    return {
        "I_f_upper": I_upper,
        "mu_upper": mu_upper,
        "I_f_core0": core0,
        "I_f_core1": core1,
        "I_f_tail": tail,
        "U": U,
        "n_lin": n_lin,
        "n_log": n_log,
    }


def bound_phi_mass(
    s: np.ndarray,
    support: float,
    gamma: float,
    delta: float,
    eps: float,
    kappa: float,
) -> dict:
    """Darboux bounds on ∫ φ_raw and an upper bound on ∫ φ_raw².

    φ_raw is decreasing on [0,S] when ε≥0, κ≥0, γ>0, δ>0: the numerator
    (1-(s/S)^γ)^δ decreases and the denominator (1+εs)^κ increases.
    """
    if min(eps, kappa) < 0.0:
        raise ValueError("need ε,κ ≥ 0 so that φ_raw is decreasing")
    ds = np.diff(s)
    phi_L_up = phi_raw_arr(s[:-1], support, gamma, delta, eps, kappa, "upper")
    phi_R_dn = phi_raw_arr(s[1:], support, gamma, delta, eps, kappa, "lower")
    I_lower = down(float(np.dot(phi_R_dn, ds)))
    I_upper = sum_up(phi_L_up * ds)
    a_raw_upper = sum_up((phi_L_up * phi_L_up) * ds)
    if I_lower <= 0.0:
        raise ValueError("I_φ lower bound vanished")
    a_upper = up(a_raw_upper / down(I_lower * I_lower))
    return {
        "I_phi_lower": I_lower,
        "I_phi_upper": I_upper,
        "a_raw_upper": a_raw_upper,
        "a_upper": a_upper,
        "sqrt_a_upper": up(math.sqrt(a_upper)),
        "phi_left_upper": phi_L_up,
        "phi_right_lower": phi_R_dn,
        "ds": ds,
    }


def one_minus_g_upper_on_t(
    t_right: np.ndarray,
    s_right: np.ndarray,
    phi_left_upper: np.ndarray,
    ds: np.ndarray,
    i_phi_lower: float,
    mu_upper: float,
    alpha: float,
    beta: float,
    chunk: int = 80,
) -> np.ndarray:
    """Upper bound of 1-g(t) = ∫ φ_raw(s) (1-f(s t)) ds / ∫ φ_raw.

    On each s-panel φ is decreasing and 1-f(s t) is increasing, so the
    product is ≤ φ(s_left) (1-f(s_right t)). Using φ_left_upper and
    f_lower keeps the inequality. Divide by I_φ_lower.
    """
    n_t = int(t_right.size)
    out = np.empty(n_t, dtype=np.float64)
    weight = phi_left_upper * ds
    for start in range(0, n_t, chunk):
        tr = t_right[start : start + chunk]
        st = s_right[None, :] * tr[:, None]
        fv = f_lower_arr(st, mu_upper, alpha, beta)
        one_f = np.maximum(0.0, 1.0 - fv)
        num = one_f @ weight
        out[start : start + tr.size] = num
    num_up = up_arr(out)
    omg = num_up / i_phi_lower
    return np.minimum(1.0, up_arr(omg))


def near0_I_upper(t_min: float, mu_upper: float, alpha: float, beta: float, support: float) -> float:
    """∫_0^{t_min} (1-g)² t^{-3/2} dt.

    g(t) ≥ f(S t), and 1-(1+x)^{-β} ≤ β x (convexity of (1+x)^{-β}),
    so 1-g(t) ≤ β μ (S t)^α. Need α > 1/4 so that 2α − 1/2 > 0.
    """
    if alpha <= 0.25:
        raise ValueError("near-zero power bound needs α > 1/4")
    coef = up(beta * mu_upper * up(support**alpha))
    expo = 2.0 * alpha - 0.5
    return up((coef * coef) * up(t_min**expo) / expo)


def tail_I_upper(T: float) -> float:
    """∫_T^∞ t^{-3/2} dt = 2 T^{-1/2}, using (1-g)² ≤ 1."""
    return up(2.0 / down(math.sqrt(T)))


def panel_rectangle(t_left: np.ndarray, t_right: np.ndarray, one_minus_g_upper: np.ndarray) -> np.ndarray:
    """User-specified height: (1-g_R)² / t_L^{3/2} times length."""
    one = np.maximum(0.0, np.minimum(1.0, one_minus_g_upper))
    height = (one * one) / down_arr(np.power(t_left, 1.5))
    return up_arr((t_right - t_left) * height)


def panel_exact_weight(t_left: np.ndarray, t_right: np.ndarray, one_minus_g_upper: np.ndarray) -> np.ndarray:
    """Same freeze of (1-g)², exact ∫ t^{-3/2} dt = 2(t_L^{-1/2}-t_R^{-1/2})."""
    one = np.maximum(0.0, np.minimum(1.0, one_minus_g_upper))
    w = 2.0 * (down_arr(np.power(t_left, -0.5)) - up_arr(np.power(t_right, -0.5)))
    w = np.maximum(w, 0.0)
    return up_arr((one * one) * w)


# ---------------------------------------------------------------------------
# pair certification
# ---------------------------------------------------------------------------


def default_grids() -> dict:
    return {
        "t_min": 0.02,
        "t_steep_lo": 0.25,
        "t_steep_hi": 20.0,
        "t_drop_hi": 400.0,
        "T": 1.0e12,
        "n_small": 1500,
        "n_steep": 36000,
        "n_drop": 12000,
        "n_tail": 6000,
        "n_s": 80000,
        "n_phi": 400000,
        "n_lin_mu": 200000,
        "n_log_mu": 200000,
        "U_mu": 1.0e7,
        "chunk": 80,
    }


def certify_pair(params: dict, grids: dict | None = None) -> dict:
    p = dict(params)
    gspec = default_grids() if grids is None else {**default_grids(), **grids}
    alpha = float(p["alpha"])
    beta = float(p["beta"])
    gamma = float(p["gamma"])
    delta = float(p["delta"])
    eps = float(p.get("eps", 1.0))
    kappa = float(p.get("kappa", 1.0))
    support = float(p.get("support", p.get("T", 1.0)))
    name = str(p.get("name", "pair"))
    if min(alpha, beta, gamma, delta, support) <= 0.0:
        raise ValueError("alpha, beta, gamma, delta, support must be positive")

    mu_b = bound_I_f(alpha, beta, gspec["U_mu"], gspec["n_lin_mu"], gspec["n_log_mu"])
    mu_u = mu_b["mu_upper"]

    s_mass = uniform_s_grid(support, int(gspec["n_phi"]))
    phi_b = bound_phi_mass(s_mass, support, gamma, delta, eps, kappa)

    s = uniform_s_grid(support, int(gspec["n_s"]))
    ds = np.diff(s)
    phi_L_up = phi_raw_arr(s[:-1], support, gamma, delta, eps, kappa, "upper")
    phi_R_dn = phi_raw_arr(s[1:], support, gamma, delta, eps, kappa, "lower")

    t = hybrid_t_grid(
        gspec["t_min"],
        gspec["t_steep_lo"],
        gspec["t_steep_hi"],
        gspec["t_drop_hi"],
        gspec["T"],
        int(gspec["n_small"]),
        int(gspec["n_steep"]),
        int(gspec["n_drop"]),
        int(gspec["n_tail"]),
    )
    t_left = t[:-1]
    t_right = t[1:]
    omg = one_minus_g_upper_on_t(
        t_right,
        s[1:],
        phi_L_up,
        ds,
        phi_b["I_phi_lower"],
        mu_u,
        alpha,
        beta,
        chunk=int(gspec["chunk"]),
    )

    rect = panel_rectangle(t_left, t_right, omg)
    exactw = panel_exact_weight(t_left, t_right, omg)
    panels_rect = sum_up(rect)
    panels_exact = sum_up(exactw)
    near = near0_I_upper(gspec["t_min"], mu_u, alpha, beta, support)
    tail = tail_I_upper(gspec["T"])

    I_rect = up(near + panels_rect + tail)
    I_exact = up(near + panels_exact + tail)
    Ag_rect = up(0.5 * I_rect)
    Ag_exact = up(0.5 * I_exact)
    C1_rect = up(phi_b["sqrt_a_upper"] * Ag_rect)
    C1_exact = up(phi_b["sqrt_a_upper"] * Ag_exact)

    # Official bound: freeze (1-g)² at the right endpoint (user inequality)
    # times the exact ∫ t^{-3/2} dt. The stored panels are the rectangle
    # form (height / t_left^{3/2} * length); both are rigorous. The
    # certified number uses the tighter exact-weight integral.
    C1 = C1_exact
    Ag_used = Ag_exact
    L_up = l_over_lcl_upper(C1)
    K_lo = k_over_kcl_lower(C1)
    moved = beats_published_1456(C1)

    bounds = {
        "I_f_upper": mu_b["I_f_upper"],
        "mu_upper": mu_u,
        "I_phi_lower": phi_b["I_phi_lower"],
        "I_phi_upper": phi_b["I_phi_upper"],
        "a_raw_upper": phi_b["a_raw_upper"],
        "a_upper": phi_b["a_upper"],
        "sqrt_a_upper": phi_b["sqrt_a_upper"],
        "near0_I_upper": near,
        "panels_rectangle_I_upper": panels_rect,
        "panels_exactweight_I_upper": panels_exact,
        "tail_I_upper": tail,
        "I_upper_rectangle": I_rect,
        "I_upper_exactweight": I_exact,
        "Ag_upper": Ag_used,
        "C_1_upper": C1,
        "C_1_upper_rectangle": C1_rect,
        "C_1_upper_exactweight": C1_exact,
        "K_over_Kcl_lower": K_lo,
        "L_over_Lcl_upper": L_up,
        "sqrt3_upper": sqrt3_upper(),
        "published_L_record": PUBLISHED_L,
        "beats_1456": bool(moved),
        "n_t_panels": int(t_left.size),
        "n_s_panels": int(s.size - 1),
        "n_phi_panels": int(s_mass.size - 1),
        "one_minus_g_first": float(omg[0]),
        "one_minus_g_last": float(omg[-1]),
    }

    cert = {
        "schema": "fhjn-c1-panel-v1",
        "name": name,
        "params": {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "delta": delta,
            "eps": eps,
            "kappa": kappa,
            "support": support,
        },
        "grids": {
            "t_min": gspec["t_min"],
            "t_steep_lo": gspec["t_steep_lo"],
            "t_steep_hi": gspec["t_steep_hi"],
            "t_drop_hi": gspec["t_drop_hi"],
            "T": gspec["T"],
            "n_small": int(gspec["n_small"]),
            "n_steep": int(gspec["n_steep"]),
            "n_drop": int(gspec["n_drop"]),
            "n_tail": int(gspec["n_tail"]),
            "n_s": int(gspec["n_s"]),
            "n_phi": int(gspec["n_phi"]),
            "n_lin_mu": int(gspec["n_lin_mu"]),
            "n_log_mu": int(gspec["n_log_mu"]),
            "U_mu": gspec["U_mu"],
        },
        "bounds": bounds,
        "method": {
            "python": (
                "t-panels: (1-g)² increasing so integrand ≤ (1-g_upper(t_right))² "
                "t^{-3/2}; certified contribution uses exact ∫ t^{-3/2} dt. "
                "Rectangle height/t_left^{3/2}*length is also stored. "
                "1-g = ∫ φ_raw(1-f)/I_φ ≤ Σ φ_left_upper (1-f_lower(s_right t)) Δs "
                "/ I_φ_lower. Tail 2 T^{-1/2}. Near 0: (1-g)² ≤ (β μ S^α)² t^{2α}."
            ),
            "rust": (
                "u=log t: integrand becomes (1-g(e^u))² e^{-u/2}; panel uses "
                "exact ∫ e^{-u/2} du times (1-g_right)². s-grid is quadratic "
                "s=S (j/n)². I_f via v=u^α Beta-form Darboux."
            ),
        },
        "t_nodes": [float(x) for x in t],
        "one_minus_g_upper_right": [float(x) for x in omg],
        "g_lower_right": [float(x) for x in np.maximum(0.0, 1.0 - omg)],
        "panel_contrib_upper": [float(x) for x in exactw],
        "panel_contrib_rectangle": [float(x) for x in rect],
        "s_nodes": [float(x) for x in s],
        "phi_right_lower": [float(x) for x in phi_R_dn],
        "phi_left_upper": [float(x) for x in phi_L_up],
        "notes": (
            "μ_upper ≥ μ_exact so ∫f² ≤ 1. Scaling f up to unit L² decreases "
            "C_1; the reported C_1_upper is therefore a valid trial bound. "
            "Replay the stored panel_contrib_upper plus near0 and tail, or "
            "recompute from params with verify_c1.py / verify_c1.rs."
        ),
    }
    return cert


def replay_stored(cert: dict) -> float:
    """Stranger replay: sum stored rectangle panels + near0 + tail."""
    b = cert["bounds"]
    panels = sum_up(np.array(cert["panel_contrib_upper"], dtype=np.float64))
    Iu = up(b["near0_I_upper"] + panels + b["tail_I_upper"])
    Ag = up(0.5 * Iu)
    return up(b["sqrt_a_upper"] * Ag)


# ---------------------------------------------------------------------------
# opt_*.json
# ---------------------------------------------------------------------------


def _as_pair(obj: dict, label: str) -> dict | None:
    if not isinstance(obj, dict):
        return None
    inner = obj
    for key in ("parameters", "params", "meta"):
        if key in obj and isinstance(obj[key], dict):
            # prefer the nested record if it carries the family fields
            cand = _as_pair(obj[key], label + "." + key)
            if cand is not None:
                return cand
    fam = inner.get("family", obj.get("family"))
    if fam not in (None, "A", "power_decay", "power_decay_A", "lemma11_second"):
        return None
    src = inner if all(k in inner for k in ("alpha", "beta", "gamma", "delta")) else obj
    if not all(k in src for k in ("alpha", "beta", "gamma", "delta")):
        return None
    support = src.get("support", src.get("T", src.get("S", 1.0)))
    return {
        "name": label,
        "alpha": float(src["alpha"]),
        "beta": float(src["beta"]),
        "gamma": float(src["gamma"]),
        "delta": float(src["delta"]),
        "eps": float(src.get("eps", 1.0)),
        "kappa": float(src.get("kappa", 1.0)),
        "support": float(support),
    }


def extract_pairs(data, label: str) -> list[dict]:
    found: list[dict] = []
    seen: set[tuple] = set()

    def add(p: dict | None) -> None:
        if p is None:
            return
        key = (
            round(p["alpha"], 12),
            round(p["beta"], 12),
            round(p["gamma"], 12),
            round(p["delta"], 12),
            round(p["eps"], 12),
            round(p["kappa"], 12),
            round(p["support"], 12),
        )
        if key in seen:
            return
        seen.add(key)
        found.append(p)

    if isinstance(data, dict):
        add(_as_pair(data, label))
        if "best" in data:
            add(_as_pair(data["best"], label + ".best"))
        fams = data.get("families")
        if isinstance(fams, dict):
            for fk, fv in fams.items():
                add(_as_pair(fv, f"{label}.families.{fk}"))
        for key in ("pairs", "candidates"):
            seq = data.get(key)
            if isinstance(seq, list):
                for i, item in enumerate(seq):
                    add(_as_pair(item, f"{label}.{key}[{i}]"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            add(_as_pair(item, f"{label}[{i}]"))
    return found


def load_opt_pairs(q1: Path) -> list[dict]:
    pairs: list[dict] = []
    for path in sorted(q1.glob("opt_*.json")):
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"warning: skip {path.name}: {exc}", file=sys.stderr)
            continue
        extracted = extract_pairs(data, path.stem)
        print(f"loaded {len(extracted)} family-A pair(s) from {path.name}")
        pairs.extend(extracted)
    return pairs


def dump_cert(cert: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Compact: panel arrays are long.
    dest.write_text(json.dumps(cert, separators=(",", ":")) + "\n")


def print_report(cert: dict, tag: str) -> None:
    b = cert["bounds"]
    print(
        f"{tag}: C_1_upper={b['C_1_upper']:.12f}  "
        f"K/Kcl_lower={b['K_over_Kcl_lower']:.12f}  "
        f"L/Lcl_upper={b['L_over_Lcl_upper']:.12f}  "
        f"beats_1.456={b['beats_1456']}"
    )
    print(
        f"  rectangle={b['C_1_upper_rectangle']:.12f}  "
        f"exactweight={b['C_1_upper_exactweight']:.12f}  "
        f"a_upper={b['a_upper']:.10f}  mu_upper={b['mu_upper']:.10f}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--certs-dir", type=Path, default=CERTS)
    ap.add_argument("--q1-dir", type=Path, default=HERE)
    ap.add_argument("--skip-opt", action="store_true")
    args = ap.parse_args()
    certs_dir: Path = args.certs_dir
    certs_dir.mkdir(parents=True, exist_ok=True)

    paper = dict(PAPER_SECOND)
    print("certifying paper Lemma 11 second pair ...", flush=True)
    paper_cert = certify_pair(paper)
    paper_path = certs_dir / "c1_lemma11_second.json"
    dump_cert(paper_cert, paper_path)
    replay = replay_stored(paper_cert)
    if replay > paper_cert["bounds"]["C_1_upper"] * (1.0 + 1e-12) + 1e-14:
        print(f"error: stored-panel replay {replay} exceeds certified", file=sys.stderr)
        return 1
    print_report(paper_cert, "lemma11_second")
    print(f"  wrote {paper_path}")

    best = paper_cert
    best_src = "lemma11_second"
    if not args.skip_opt:
        for pair in load_opt_pairs(args.q1_dir):
            # Skip the exact paper numbers if they reappear.
            if (
                abs(pair["alpha"] - 4.5) < 1e-15
                and abs(pair["beta"] - 0.25) < 1e-15
                and abs(pair["gamma"] - 0.36) < 1e-15
                and abs(pair["delta"] - 2.1) < 1e-15
                and abs(pair["support"] - 1.0) < 1e-15
            ):
                continue
            print(f"certifying {pair['name']} ...", flush=True)
            try:
                cert = certify_pair(pair)
            except ValueError as exc:
                print(f"  skip {pair['name']}: {exc}")
                continue
            print_report(cert, pair["name"])
            if cert["bounds"]["C_1_upper"] < best["bounds"]["C_1_upper"]:
                best = cert
                best_src = pair["name"]

    if best_src != "lemma11_second":
        best_path = certs_dir / "c1_opt_best.json"
        dump_cert(best, best_path)
        print(f"best certified pair: {best_src}")
        print_report(best, "opt_best")
        print(f"  wrote {best_path}")
    else:
        print("no optimized family-A pair beat the paper pair (certified)")

    C1 = best["bounds"]["C_1_upper"]
    L = best["bounds"]["L_over_Lcl_upper"]
    K = best["bounds"]["K_over_Kcl_lower"]
    print("----")
    print(f"C_1_upper={C1:.12f}")
    print(f"K/Kcl_lower={K:.12f}")
    print(f"L/Lcl_upper={L:.12f}")
    print(f"published_L=1.456  moved={best['bounds']['beats_1456']}")
    if not beats_published_1456(C1):
        print(
            "FAIL: certified C_1_upper does not beat 1.456 after conversion "
            f"(need C_1 < 1.456 * 4 / (9√3)); got {C1:.12f}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
