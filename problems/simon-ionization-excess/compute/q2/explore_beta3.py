#!/usr/bin/env python3
"""Numerical upper bounds on β_3^{rad} = inf I/D (radial, s=3).

HPS arXiv:2504.18487v1 Prop. 4.5: I/D ≥ min_t f(t) = 1/b(3) ≈ 0.89412
with f(t)=(1+t^3)/(1+t^2). Figure 2: explicit measures give b_num(3)
about 3% below b(3). Those trials are UPPER bounds on β_3 (wrong
direction for the ionization coefficient). This file only locates the
apparent infimum so the certified lower bound knows the target.

Families:
  (a) power-law radial pushforwards m(dr) ∝ r^α dr on [1, n]
      (HPS used 3D density A|x|^{-p} ⇒ α = 2-p)
  (b) k-atomic measures on (0, ∞)
  (c) piecewise-constant densities on a geometric grid

Also records b(s) for s = 3.1, 3.5, 4, 5 (what s>3 would be worth).

Writes certs/beta3_explore.json. Not a lower bound.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
WORK = HERE / "work"

# Closed form, HPS (2.9) / Prop. 4.5
T0 = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0) - (1.0 + math.sqrt(2.0)) ** (-1.0 / 3.0)
B3 = (2.0 / 3.0) * (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0) / (
    (1.0 + math.sqrt(2.0)) ** (2.0 / 3.0) - 1.0
)
FMIN = 1.0 / B3  # = (3/2) * T0


def f_ratio(t: float) -> float:
    t = float(t)
    if t <= 0.0:
        return 1.0
    return (1.0 + t**3) / (1.0 + t**2)


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


# ---------------------------------------------------------------------------
# (a) power laws, closed form + quadrature fallback
# ---------------------------------------------------------------------------


def power_law_CD(alpha: float, n: float) -> tuple[float, float]:
    """C, D for m(dr) = C r^α dr on [1, n]."""
    if abs(alpha + 1.0) < 1e-14:
        C = 1.0 / math.log(n)
    else:
        C = (alpha + 1.0) / (n ** (alpha + 1.0) - 1.0)
    if abs(alpha + 3.0) < 1e-14:
        D = C * math.log(n)
    else:
        D = C * (n ** (alpha + 3.0) - 1.0) / (alpha + 3.0)
    return C, D


def power_law_I_quad(alpha: float, n: float, C: float) -> float:
    """I = C² ∫_1^n u^{α-1} (∫_1^u r^{α+3} dr + u³ ∫_1^u r^α dr) du."""

    def inner(u: float) -> float:
        if abs(alpha + 4.0) < 1e-14:
            a = math.log(u)
        else:
            a = (u ** (alpha + 4.0) - 1.0) / (alpha + 4.0)
        if abs(alpha + 1.0) < 1e-14:
            b = math.log(u)
        else:
            b = (u ** (alpha + 1.0) - 1.0) / (alpha + 1.0)
        return u ** (alpha - 1.0) * (a + (u**3) * b)

    # Gauss–Legendre on [1, n] after log map u = exp(s), s ∈ [0, log n]
    L = math.log(n)
    # 96-point GL on [0, 1]
    nodes, weights = np.polynomial.legendre.leggauss(96)
    acc = 0.0
    for x, w in zip(nodes, weights):
        s = 0.5 * L * (x + 1.0)
        u = math.exp(s)
        acc += w * inner(u) * u  # du = u ds, ds weight = L/2
    return C * C * acc * (0.5 * L)


def power_law_ID(alpha: float, n: float) -> float:
    if n <= 1.0 + 1e-12:
        return 1.0
    C, D = power_law_CD(alpha, n)
    I = power_law_I_quad(alpha, n, C)
    return I / D


def scan_power_laws() -> dict:
    best = {"I_over_D": 1.0, "alpha": None, "n": None, "p": None}
    rows = []
    alphas = np.linspace(-2.8, 1.5, 87)
    ns = np.unique(
        np.concatenate(
            [
                np.array([1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5]),
                np.geomspace(2.5, 80.0, 40),
            ]
        )
    )
    for a in alphas:
        for n in ns:
            val = power_law_ID(float(a), float(n))
            p = 2.0 - float(a)  # HPS 3D exponent
            rec = {"alpha": float(a), "n": float(n), "p": p, "I_over_D": val}
            rows.append(rec)
            if val < best["I_over_D"]:
                best = {
                    "I_over_D": val,
                    "alpha": float(a),
                    "n": float(n),
                    "p": p,
                    "inv": 1.0 / val,
                }

    # local polish around the coarse min
    a0, n0 = best["alpha"], best["n"]

    def obj(x):
        a, ln = float(x[0]), float(x[1])
        nn = math.exp(ln)
        if nn <= 1.05 or a < -4.0 or a > 3.0:
            return 10.0
        return power_law_ID(a, nn)

    opt = minimize(obj, [a0, math.log(n0)], method="Nelder-Mead", options={"maxiter": 400})
    if opt.success and opt.fun < best["I_over_D"]:
        best = {
            "I_over_D": float(opt.fun),
            "alpha": float(opt.x[0]),
            "n": float(math.exp(opt.x[1])),
            "p": 2.0 - float(opt.x[0]),
            "inv": 1.0 / float(opt.fun),
            "polished": True,
        }
    else:
        best["polished"] = False
    return {"best": best, "n_evals": len(rows)}


# ---------------------------------------------------------------------------
# (b) k-atomic
# ---------------------------------------------------------------------------


def atomic_ID(radii: np.ndarray, masses: np.ndarray) -> float:
    r = np.asarray(radii, dtype=float)
    p = np.asarray(masses, dtype=float)
    p = np.clip(p, 0.0, None)
    s = p.sum()
    if s <= 0:
        return 1e9
    p = p / s
    # g_ij
    r = np.clip(r, 1e-12, 1e8)
    R, U = np.meshgrid(r, r, indexing="ij")
    mx = np.maximum(R, U)
    G = (R**3 + U**3) / (2.0 * mx)
    I = float(p @ G @ p)
    D = float(p @ (r**2))
    return I / D


def optimize_atomic(k: int, n_starts: int = 24, rng=None) -> dict:
    rng = np.random.default_rng(rng if rng is not None else 1000 + k)
    best_val = 1.0
    best = None

    def unpack(x):
        # x = [log gaps (k-1), unconstrained masses (k)]
        # r_1 = 1, r_{i+1} = r_i * exp(g_i), g_i > 0
        gaps = np.exp(x[: k - 1]) if k > 1 else np.array([])
        r = np.ones(k)
        for i, g in enumerate(gaps):
            r[i + 1] = r[i] * (1.0 + g)
        raw = x[k - 1 :]
        p = np.exp(raw - raw.max())
        p = p / p.sum()
        return r, p

    def obj(x):
        r, p = unpack(x)
        return atomic_ID(r, p)

    for s in range(n_starts):
        if k == 1:
            val = 1.0
            cand = {"k": 1, "radii": [1.0], "masses": [1.0], "I_over_D": 1.0}
        else:
            x0 = np.concatenate(
                [
                    np.log(rng.uniform(0.05, 1.2, size=k - 1)),
                    rng.normal(0.0, 0.8, size=k),
                ]
            )
            opt = minimize(obj, x0, method="Nelder-Mead", options={"maxiter": 800})
            r, p = unpack(opt.x)
            val = atomic_ID(r, p)
            cand = {
                "k": k,
                "radii": [float(v) for v in r],
                "masses": [float(v) for v in p],
                "I_over_D": float(val),
                "inv": 1.0 / float(val),
            }
        if best is None or val < best_val:
            best_val = val
            best = cand
    return best


# ---------------------------------------------------------------------------
# (c) piecewise-constant density on a geometric grid
# ---------------------------------------------------------------------------


def piecewise_ID(heights: np.ndarray, edges: np.ndarray) -> float:
    """m has density h_i on [e_i, e_{i+1}) (Lebesgue on the radius line)."""
    h = np.clip(np.asarray(heights, dtype=float), 0.0, None)
    e = np.asarray(edges, dtype=float)
    # mass and D per bin: ∫_a^b h r^0 dr = h (b-a), ∫ h r² dr = h (b³-a³)/3
    widths = e[1:] - e[:-1]
    masses = h * widths
    tot = masses.sum()
    if tot <= 0:
        return 1e9
    masses = masses / tot
    h = h / tot  # renormalise so total mass 1; widths unchanged
    D = float(np.sum(h * (e[1:] ** 3 - e[:-1] ** 3) / 3.0))

    # I via bin-pair quadrature (2-point endpoints + midpoint, cheap)
    n = len(h)
    I = 0.0
    # For i ≤ j, r ≤ u typically if bins are ordered. Use 3×3 product.
    nodes_frac = np.array([0.5 - math.sqrt(0.15), 0.5, 0.5 + math.sqrt(0.15)])
    wts = np.array([5.0 / 18.0, 8.0 / 18.0, 5.0 / 18.0])
    for i in range(n):
        if h[i] <= 0:
            continue
        ai, bi = e[i], e[i + 1]
        ri = ai + (bi - ai) * nodes_frac
        dri = bi - ai
        for j in range(n):
            if h[j] <= 0:
                continue
            aj, bj = e[j], e[j + 1]
            uj = aj + (bj - aj) * nodes_frac
            duj = bj - aj
            acc = 0.0
            for a, wa in enumerate(wts):
                for b, wb in enumerate(wts):
                    acc += wa * wb * g_kernel(ri[a], uj[b])
            I += h[i] * h[j] * dri * duj * acc
    return I / D


def optimize_piecewise(n_bins: int = 16, R: float = 12.0) -> dict:
    edges = np.geomspace(1.0, R, n_bins + 1)
    rng = np.random.default_rng(7)
    best_val = 1.0
    best_h = None
    for trial in range(12):
        # log-heights
        x0 = rng.normal(0.0, 0.6, size=n_bins)
        # also a power-law-like start
        if trial == 0:
            alpha = -0.5
            mid = 0.5 * (edges[:-1] + edges[1:])
            x0 = alpha * np.log(mid)
        if trial == 1:
            x0 = np.zeros(n_bins)

        def obj(x):
            h = np.exp(x - np.max(x))
            return piecewise_ID(h, edges)

        opt = minimize(obj, x0, method="Nelder-Mead", options={"maxiter": 600})
        h = np.exp(opt.x - np.max(opt.x))
        val = piecewise_ID(h, edges)
        if val < best_val:
            best_val = val
            best_h = h / h.sum()
    return {
        "n_bins": n_bins,
        "R": R,
        "I_over_D": float(best_val),
        "inv": 1.0 / float(best_val),
        "heights": [float(v) for v in best_h] if best_h is not None else None,
    }


# ---------------------------------------------------------------------------
# b(s) for s > 3 (what a hypothetical s>3 theorem would be worth)
# ---------------------------------------------------------------------------


def t0_of(s: float) -> float:
    # t^s + s t + 1 - s = 0 on (0,1)
    lo, hi = 1e-16, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid**s + s * mid + 1.0 - s < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def b_of(s: float) -> dict:
    t0 = t0_of(s)
    b = (s - 1.0) / (s * t0)
    # numerical max of (1+t^{s-1})/(1+t^s)
    ts = np.linspace(0.0, 1.0, 20001)
    num = np.empty_like(ts)
    num[0] = 1.0
    tpos = ts[1:]
    num[1:] = (1.0 + tpos ** (s - 1.0)) / (1.0 + tpos**s)
    return {
        "s": s,
        "t0": t0,
        "b": b,
        "b_inv": 1.0 / b,
        "grid_max": float(num.max()),
        "grid_max_t": float(ts[int(num.argmax())]),
    }


def quadratic_minorant() -> dict:
    """min_{t∈[0,1]\\{t0}} (f(t)-fmin)/(t-t0)^2  and endpoint values."""
    ts = np.linspace(0.0, 1.0, 100001)
    num = np.array([f_ratio(t) for t in ts])
    den = (ts - T0) ** 2
    mask = den > 1e-16
    ratio = (num[mask] - FMIN) / den[mask]
    return {
        "t0": T0,
        "fmin": FMIN,
        "alpha_grid_min": float(ratio.min()),
        "alpha_at": float(ts[mask][int(ratio.argmin())]),
        "fpp_over_2_near_t0": float(
            (f_ratio(T0 + 1e-5) + f_ratio(T0 - 1e-5) - 2.0 * FMIN) / (2.0 * 1e-10)
        ),
    }


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    print(f"b(3)={B3:.12f}  1/b(3)={FMIN:.12f}  t0={T0:.12f}")

    print("=== power laws ===")
    pl = scan_power_laws()
    print("  best", pl["best"])

    print("=== k-atomic ===")
    atomics = []
    for k in range(1, 7):
        rec = optimize_atomic(k)
        atomics.append(rec)
        print(f"  k={k}  I/D={rec['I_over_D']:.8f}  1/(I/D)={rec.get('inv', 1/rec['I_over_D']):.8f}")

    print("=== piecewise log-grid ===")
    pw_list = []
    for n_bins, R in ((12, 8.0), (16, 12.0), (20, 16.0)):
        rec = optimize_piecewise(n_bins, R)
        pw_list.append(rec)
        print(f"  bins={n_bins} R={R}  I/D={rec['I_over_D']:.8f}  inv={rec['inv']:.8f}")

    print("=== b(s) for s>3 ===")
    bs = [b_of(s) for s in (3.0, 3.1, 3.5, 4.0, 5.0)]
    for rec in bs:
        print(f"  s={rec['s']}  b={rec['b']:.8f}  1/b={rec['b_inv']:.8f}")

    qm = quadratic_minorant()
    print("=== quadratic minorant of f ===")
    print(f"  α_grid_min={qm['alpha_grid_min']:.6f} at t={qm['alpha_at']:.6f}")

    candidates = (
        [pl["best"]["I_over_D"]]
        + [r["I_over_D"] for r in atomics]
        + [r["I_over_D"] for r in pw_list]
    )
    apparent = min(candidates)
    blob = {
        "not_a_lower_bound": True,
        "b3": B3,
        "fmin_HPS": FMIN,
        "apparent_inf_beta3": apparent,
        "apparent_inf_inv": 1.0 / apparent,
        "gap_vs_b3_percent": 100.0 * (1.0 - (1.0 / apparent) / B3),
        "power_law": pl,
        "atomic": atomics,
        "piecewise": pw_list,
        "b_s": bs,
        "quadratic_minorant": qm,
        "note": (
            "These I/D values are numerical upper bounds on β_3^{rad}. "
            "The ionization coefficient needs a lower bound on β_3."
        ),
    }
    out = CERTS / "beta3_explore.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("wrote", out)
    print(
        f"apparent inf β_3 ≈ {apparent:.8f}   β_3^{{-1}} ≈ {1.0/apparent:.8f}  "
        f"(b(3)={B3:.6f}, ~{blob['gap_vs_b3_percent']:.2f}% below)"
    )


if __name__ == "__main__":
    main()
