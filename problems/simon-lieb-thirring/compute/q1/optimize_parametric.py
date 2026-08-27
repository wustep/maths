#!/usr/bin/env python3
"""Parametric search for an FHJN pair beating Lemma 11.

Families (μ, c always normalized so ∫f² = ∫φ = 1, f(0) = 1):

  A  f(t)=(1+μ t^α)^{-β}
     φ(t)=c (1-(t/T)^γ)^δ / (1+ε t)^κ  1_{t≤T}

  B  same f; φ gets an extra rational factor (1+a t^p)/(1+b t^q)

  C  two-scale f: ψ(u)=[(1+u^{α1})^{-β1} + λ(1+(u/r)^{α2})^{-β2}]/(1+λ),
     f(t)=ψ(t/σ) with σ so that ∫f²=1
     φ as in A

  D  f as in A; two-piece φ on [0,T1] ∪ [T1,T2]

Inner loop is the numpy log-grid evaluator. Finalists are re-scored
with ``c1_functional.evaluate_c1`` (unchanged API).
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

from c1_functional import evaluate_c1, normalize_phi_support, ratio_from_c1
from grid_c1 import FastC1, normalize_mu, power_decay_vec, ratio_L, stretch_l2_unit

HERE = Path(__file__).resolve().parent

# Coarse grid for DE / multi-start; fine grid for polish.
GRID_FAST = FastC1(ns=256, nt=1280, tmin=1e-8, tmax=1e8)
GRID_FINE = FastC1(ns=640, nt=2560, tmin=1e-9, tmax=1e9)


def _phiA_raw(s: np.ndarray, T: float, gamma: float, delta: float, eps: float, kappa: float) -> np.ndarray:
    s = np.asarray(s, dtype=np.float64)
    out = np.zeros_like(s)
    m = (s >= 0.0) & (s <= T)
    if not np.any(m):
        return out
    sm = s[m]
    u = np.clip(np.exp(gamma * (np.log(np.maximum(sm, 1e-300)) - math.log(T))), 0.0, 1.0)
    num = np.exp(delta * np.log(np.maximum(1.0 - u, 0.0)))
    den = np.exp(kappa * np.log1p(eps * sm))
    out[m] = num / den
    return out


def _phiB_raw(
    s: np.ndarray,
    T: float,
    gamma: float,
    delta: float,
    eps: float,
    kappa: float,
    a: float,
    p: float,
    b: float,
    q: float,
) -> np.ndarray:
    base = _phiA_raw(s, T, gamma, delta, eps, kappa)
    s = np.asarray(s, dtype=np.float64)
    extra = (1.0 + a * np.power(np.maximum(s, 0.0), p)) / (1.0 + b * np.power(np.maximum(s, 0.0), q))
    return base * extra


def _phiD_raw(
    s: np.ndarray,
    T1: float,
    T2: float,
    g1: float,
    d1: float,
    e1: float,
    k1: float,
    g2: float,
    d2: float,
    e2: float,
    k2: float,
    rho: float,
) -> np.ndarray:
    s = np.asarray(s, dtype=np.float64)
    out = np.zeros_like(s)
    out += _phiA_raw(s, T1, g1, d1, e1, k1)
    m2 = (s > T1) & (s <= T2)
    if np.any(m2) and T2 > T1:
        sm = s[m2]
        u = np.clip((sm - T1) / (T2 - T1), 0.0, 1.0)
        u = np.clip(np.power(u, g2), 0.0, 1.0)
        num = np.exp(d2 * np.log(np.maximum(1.0 - u, 0.0)))
        den = np.exp(k2 * np.log1p(e2 * sm))
        out[m2] = rho * num / den
    return out


def _f_two_scale_on(t: np.ndarray, alpha1, beta1, alpha2, beta2, lam, r, sigma) -> np.ndarray:
    t = np.asarray(t, dtype=np.float64)
    u = t / sigma
    term1 = power_decay_vec(u, 1.0, alpha1, beta1)
    term2 = power_decay_vec(u / r, 1.0, alpha2, beta2)
    return (term1 + lam * term2) / (1.0 + lam)


def _two_scale_sigma(alpha1, beta1, alpha2, beta2, lam, r, grid: FastC1) -> float:
    psi = _f_two_scale_on(grid.u, alpha1, beta1, alpha2, beta2, lam, r, 1.0)
    return stretch_l2_unit(psi, grid.u, grid.logu, grid.tmin, grid.tmax)


# ---------------------------------------------------------------------------
# Family packs: vector x -> (C_1_grid, meta)
# ---------------------------------------------------------------------------

def _finite_pos(xs) -> bool:
    return all(np.isfinite(v) and v > 0.0 for v in xs)


def eval_A(x, grid: FastC1) -> tuple[float, dict]:
    alpha, beta, gamma, delta, eps, kappa, T = [float(v) for v in x]
    if not _finite_pos((alpha, beta, gamma, delta, T)):
        return 1e9, {}
    if eps < 0.0 or kappa < 0.0 or T <= 0.05:
        return 1e9, {}
    if 2.0 * alpha * beta <= 1.05:
        return 1e9, {}
    try:
        mu = normalize_mu(alpha, beta)
    except ValueError:
        return 1e9, {}

    def f_vec(t):
        return power_decay_vec(np.asarray(t), mu, alpha, beta)

    def phi_vec(s):
        return _phiA_raw(np.asarray(s), T, gamma, delta, eps, kappa)

    out = grid.eval_callables(f_vec, phi_vec, [(0.0, T)])
    meta = {
        "family": "A",
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "delta": delta,
        "eps": eps,
        "kappa": kappa,
        "T": T,
        "mu": mu,
    }
    return out["C_1"], {**meta, **out}


def eval_B(x, grid: FastC1) -> tuple[float, dict]:
    alpha, beta, gamma, delta, eps, kappa, T, a, p, b, q = [float(v) for v in x]
    if not _finite_pos((alpha, beta, gamma, delta, T)):
        return 1e9, {}
    if min(eps, kappa, a, p, b, q) < 0.0 or T <= 0.05:
        return 1e9, {}
    if 2.0 * alpha * beta <= 1.05:
        return 1e9, {}
    try:
        mu = normalize_mu(alpha, beta)
    except ValueError:
        return 1e9, {}

    def f_vec(t):
        return power_decay_vec(np.asarray(t), mu, alpha, beta)

    def phi_vec(s):
        return _phiB_raw(np.asarray(s), T, gamma, delta, eps, kappa, a, p, b, q)

    out = grid.eval_callables(f_vec, phi_vec, [(0.0, T)])
    meta = {
        "family": "B",
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "delta": delta,
        "eps": eps,
        "kappa": kappa,
        "T": T,
        "a": a,
        "p": p,
        "b": b,
        "q": q,
        "mu": mu,
    }
    return out["C_1"], {**meta, **out}


def eval_C(x, grid: FastC1) -> tuple[float, dict]:
    alpha1, beta1, alpha2, beta2, lam, r, gamma, delta, eps, kappa, T = [float(v) for v in x]
    if not _finite_pos((alpha1, beta1, alpha2, beta2, r, gamma, delta, T)):
        return 1e9, {}
    if lam < 0.0 or eps < 0.0 or kappa < 0.0 or T <= 0.05:
        return 1e9, {}
    if 2.0 * alpha1 * beta1 <= 1.05:
        return 1e9, {}
    sigma = _two_scale_sigma(alpha1, beta1, alpha2, beta2, lam, r, grid)
    if not np.isfinite(sigma) or sigma <= 0.0:
        return 1e9, {}

    def f_vec(t):
        return _f_two_scale_on(np.asarray(t), alpha1, beta1, alpha2, beta2, lam, r, sigma)

    def phi_vec(s):
        return _phiA_raw(np.asarray(s), T, gamma, delta, eps, kappa)

    out = grid.eval_callables(f_vec, phi_vec, [(0.0, T)])
    meta = {
        "family": "C",
        "alpha1": alpha1,
        "beta1": beta1,
        "alpha2": alpha2,
        "beta2": beta2,
        "lam": lam,
        "r": r,
        "sigma": sigma,
        "gamma": gamma,
        "delta": delta,
        "eps": eps,
        "kappa": kappa,
        "T": T,
    }
    return out["C_1"], {**meta, **out}


def eval_D(x, grid: FastC1) -> tuple[float, dict]:
    alpha, beta, T1, T2, g1, d1, e1, k1, g2, d2, e2, k2, rho = [float(v) for v in x]
    if not _finite_pos((alpha, beta, T1, T2, g1, d1, g2, d2)):
        return 1e9, {}
    if T2 <= T1 + 1e-4 or min(e1, k1, e2, k2, rho) < 0.0:
        return 1e9, {}
    if 2.0 * alpha * beta <= 1.05:
        return 1e9, {}
    try:
        mu = normalize_mu(alpha, beta)
    except ValueError:
        return 1e9, {}

    def f_vec(t):
        return power_decay_vec(np.asarray(t), mu, alpha, beta)

    def phi_vec(s):
        return _phiD_raw(np.asarray(s), T1, T2, g1, d1, e1, k1, g2, d2, e2, k2, rho)

    out = grid.eval_callables(f_vec, phi_vec, [(0.0, T1), (T1, T2)])
    meta = {
        "family": "D",
        "alpha": alpha,
        "beta": beta,
        "T1": T1,
        "T2": T2,
        "g1": g1,
        "d1": d1,
        "e1": e1,
        "k1": k1,
        "g2": g2,
        "d2": d2,
        "e2": e2,
        "k2": k2,
        "rho": rho,
        "mu": mu,
    }
    return out["C_1"], {**meta, **out}


FAMILIES = {
    "A": {
        "eval": eval_A,
        "bounds": [
            (0.8, 10.0),   # alpha
            (0.08, 2.5),   # beta
            (0.08, 3.5),   # gamma
            (0.3, 6.0),    # delta
            (0.0, 12.0),   # eps
            (0.0, 5.0),    # kappa
            (0.35, 3.5),   # T
        ],
        "paper": np.array([4.5, 0.25, 0.36, 2.1, 1.0, 1.0, 1.0]),
        "n_de": 120,
        "popsize": 16,
    },
    "B": {
        "eval": eval_B,
        "bounds": [
            (0.8, 10.0),
            (0.08, 2.5),
            (0.08, 3.5),
            (0.3, 6.0),
            (0.0, 12.0),
            (0.0, 5.0),
            (0.35, 3.5),
            (0.0, 8.0),    # a
            (0.2, 4.0),    # p
            (0.0, 8.0),    # b
            (0.2, 4.0),    # q
        ],
        "paper": np.array([4.5, 0.25, 0.36, 2.1, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0]),
        "n_de": 80,
        "popsize": 12,
    },
    "C": {
        "eval": eval_C,
        "bounds": [
            (0.8, 10.0),   # alpha1
            (0.08, 2.5),   # beta1
            (0.8, 10.0),   # alpha2
            (0.08, 2.5),   # beta2
            (0.0, 4.0),    # lam
            (0.15, 8.0),   # r
            (0.08, 3.5),   # gamma
            (0.3, 6.0),    # delta
            (0.0, 12.0),   # eps
            (0.0, 5.0),    # kappa
            (0.35, 3.5),   # T
        ],
        "paper": np.array([4.5, 0.25, 1.5, 1.0, 0.15, 2.0, 0.36, 2.1, 1.0, 1.0, 1.0]),
        "n_de": 80,
        "popsize": 12,
    },
    "D": {
        "eval": eval_D,
        "bounds": [
            (0.8, 10.0),   # alpha
            (0.08, 2.5),   # beta
            (0.25, 1.8),   # T1
            (0.6, 4.0),    # T2
            (0.08, 3.5),   # g1
            (0.3, 6.0),    # d1
            (0.0, 12.0),   # e1
            (0.0, 5.0),    # k1
            (0.08, 3.5),   # g2
            (0.3, 6.0),    # d2
            (0.0, 12.0),   # e2
            (0.0, 5.0),    # k2
            (0.0, 3.0),    # rho
        ],
        "paper": np.array([4.5, 0.25, 1.0, 1.6, 0.36, 2.1, 1.0, 1.0, 0.5, 1.5, 1.0, 1.0, 0.15]),
        "n_de": 70,
        "popsize": 11,
    },
}


def _obj(x, family: str, grid: FastC1) -> float:
    val, _ = FAMILIES[family]["eval"](x, grid)
    if not np.isfinite(val):
        return 1e9
    return float(val)


def _coord_refine(family: str, x0: np.ndarray, grid: FastC1) -> tuple[np.ndarray, float, dict]:
    ev = FAMILIES[family]["eval"]
    bounds = FAMILIES[family]["bounds"]
    x = np.asarray(x0, dtype=float).copy()
    best_v, best_m = ev(x, grid)
    for span_frac in (0.20, 0.07, 0.02):
        for i, (lo, hi) in enumerate(bounds):
            span = span_frac * (hi - lo)
            for t in (-1.0, -0.5, -0.25, 0.25, 0.5, 1.0):
                x2 = x.copy()
                x2[i] = float(np.clip(x[i] + t * span, lo, hi))
                v, m = ev(x2, grid)
                if v < best_v:
                    best_v, best_m, x = v, m, x2
    return x, float(best_v), best_m


def _lbfgs(family: str, x0: np.ndarray, grid: FastC1, maxiter: int = 250) -> tuple[np.ndarray, float, dict]:
    bounds = FAMILIES[family]["bounds"]
    ev = FAMILIES[family]["eval"]

    def fun(x):
        return _obj(x, family, grid)

    res = minimize(
        fun,
        np.asarray(x0, dtype=float),
        method="L-BFGS-B",
        bounds=bounds,
        options={
            "maxiter": maxiter,
            "maxfun": max(80, 8 * maxiter),
            "ftol": 1e-12,
            "gtol": 1e-8,
            "maxls": 20,
        },
    )
    val, meta = ev(res.x, grid)
    return np.asarray(res.x, dtype=float), float(val), meta


def _de(family: str, grid: FastC1, seed: int, x0=None) -> tuple[np.ndarray, float, dict]:
    spec = FAMILIES[family]
    ev = spec["eval"]

    def fun(x):
        return _obj(x, family, grid)

    res = differential_evolution(
        fun,
        spec["bounds"],
        strategy="best1bin",
        maxiter=spec["n_de"],
        popsize=spec["popsize"],
        mutation=(0.4, 1.0),
        recombination=0.75,
        tol=1e-8,
        atol=1e-10,
        polish=False,
        seed=seed,
        updating="immediate",
        init="latinhypercube",
        x0=x0,
        workers=1,
        disp=True,
    )
    val, meta = ev(res.x, grid)
    return np.asarray(res.x, dtype=float), float(val), meta


def _sobol_starts(family: str, n: int, seed: int, grid: FastC1) -> list[tuple[float, np.ndarray]]:
    bounds = FAMILIES[family]["bounds"]
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    rng = np.random.default_rng(seed)
    # Sobol if available, else uniform
    try:
        from scipy.stats import qmc

        m = int(math.ceil(math.log2(max(n, 2))))
        samp = qmc.Sobol(d=len(bounds), scramble=True, seed=seed).random_base2(m)[:n]
        xs = lo + samp * (hi - lo)
    except Exception:
        xs = rng.uniform(lo, hi, size=(n, len(bounds)))
    scored = []
    ev = FAMILIES[family]["eval"]
    for x in xs:
        val, _ = ev(x, grid)
        if np.isfinite(val) and val < 10.0:
            scored.append((float(val), np.asarray(x, dtype=float)))
    scored.sort(key=lambda z: z[0])
    return scored


def pair_callables(meta: dict):
    """Build scalar callables for ``evaluate_c1`` from a family meta dict."""
    fam = meta["family"]
    if fam in ("A", "B", "D"):
        mu = float(meta["mu"])
        if fam == "A":
            alpha, beta = meta["alpha"], meta["beta"]
            T = meta["T"]

            def f(t: float) -> float:
                if t <= 0.0:
                    return 1.0
                return (1.0 + mu * (t**alpha)) ** (-beta)

            def phi_raw(t: float) -> float:
                return float(_phiA_raw(np.array([t]), T, meta["gamma"], meta["delta"], meta["eps"], meta["kappa"])[0])

            phi, c0, _ = normalize_phi_support(phi_raw, support=T)
            return f, phi, T, {"mu": mu, "c0": c0}

        if fam == "B":
            alpha, beta, T = meta["alpha"], meta["beta"], meta["T"]

            def f(t: float) -> float:
                if t <= 0.0:
                    return 1.0
                return (1.0 + mu * (t**alpha)) ** (-beta)

            def phi_raw(t: float) -> float:
                return float(
                    _phiB_raw(
                        np.array([t]),
                        T,
                        meta["gamma"],
                        meta["delta"],
                        meta["eps"],
                        meta["kappa"],
                        meta["a"],
                        meta["p"],
                        meta["b"],
                        meta["q"],
                    )[0]
                )

            phi, c0, _ = normalize_phi_support(phi_raw, support=T)
            return f, phi, T, {"mu": mu, "c0": c0}

        # D
        alpha, beta = meta["alpha"], meta["beta"]
        T2 = meta["T2"]

        def f(t: float) -> float:
            if t <= 0.0:
                return 1.0
            return (1.0 + mu * (t**alpha)) ** (-beta)

        def phi_raw(t: float) -> float:
            return float(
                _phiD_raw(
                    np.array([t]),
                    meta["T1"],
                    meta["T2"],
                    meta["g1"],
                    meta["d1"],
                    meta["e1"],
                    meta["k1"],
                    meta["g2"],
                    meta["d2"],
                    meta["e2"],
                    meta["k2"],
                    meta["rho"],
                )[0]
            )

        phi, c0, _ = normalize_phi_support(phi_raw, support=T2)
        return f, phi, T2, {"mu": mu, "c0": c0}

    if fam == "C":
        sigma = meta["sigma"]

        def f(t: float) -> float:
            return float(
                _f_two_scale_on(
                    np.array([t]),
                    meta["alpha1"],
                    meta["beta1"],
                    meta["alpha2"],
                    meta["beta2"],
                    meta["lam"],
                    meta["r"],
                    sigma,
                )[0]
            )

        T = meta["T"]

        def phi_raw(t: float) -> float:
            return float(_phiA_raw(np.array([t]), T, meta["gamma"], meta["delta"], meta["eps"], meta["kappa"])[0])

        phi, c0, _ = normalize_phi_support(phi_raw, support=T)
        return f, phi, T, {"c0": c0, "sigma": sigma}

    raise ValueError(f"unknown family {fam}")


def rescore_official(meta: dict) -> dict:
    """Quad at t_cut=1e6 (stable; same convention as paper_replay).

    ``evaluate_c1`` with t_cut ≳ 1e7 is unreliable (nested quad on a long
    tail). The full-integral estimate adds the g≈0 tail
    ½√a · 2 t_cut^{-1/2} that FHJN fold into the published 0.373556.
    """
    f, phi, support, extra = pair_callables(meta)
    r6 = evaluate_c1(f, phi, support=support, t_cut=1e6)
    tail = 0.5 * math.sqrt(max(r6.a, 0.0)) * 2.0 * (1e6 ** -0.5)
    c1_full = r6.C_1 + tail
    return {
        "C_1_float_tcut1e6": r6.C_1,
        "C_1_plus_err_tcut1e6": r6.C_1 + r6.abs_err_est,
        "C_1_full_est": c1_full,
        "C_1_tail_added": tail,
        "a_quad": r6.a,
        "A_g_tcut1e6": r6.A_g,
        "abs_err_est_1e6": r6.abs_err_est,
        "ratios_tcut1e6": ratio_from_c1(r6.C_1),
        "ratios_full_est": ratio_from_c1(c1_full),
        **extra,
    }


def _run_family(name: str, grid: FastC1, seed: int) -> dict:
    spec = FAMILIES[name]
    ev = spec["eval"]
    t0 = time.time()
    print(f"\n=== family {name} ===", flush=True)

    x_paper = spec["paper"]
    v0, m0 = ev(x_paper, grid)
    print(f"  seed/paper grid C_1={v0:.8f}", flush=True)

    x_loc, v_loc, m_loc = _lbfgs(name, x_paper, grid, maxiter=80)
    x_loc, v_loc, m_loc = _coord_refine(name, x_loc, grid)
    print(f"  L-BFGS+coord from paper: {v_loc:.8f}", flush=True)

    n_sobol = 96 if name == "A" else 64
    scored = _sobol_starts(name, n_sobol, seed, grid)
    print(f"  Sobol {n_sobol}: best raw {scored[0][0]:.8f}" if scored else "  Sobol: none", flush=True)

    candidates = [(v_loc, x_loc, m_loc)]
    for val, x in scored[:6]:
        xb, vb, mb = _lbfgs(name, x, grid, maxiter=50)
        candidates.append((vb, xb, mb))
        print(f"    polish {val:.6f} -> {vb:.8f}", flush=True)

    x_de0 = min(candidates, key=lambda z: z[0])[1]
    x_de, v_de, m_de = _de(name, grid, seed=seed + 17, x0=x_de0)
    x_de, v_de, m_de = _coord_refine(name, x_de, grid)
    print(f"  DE+coord: {v_de:.8f}", flush=True)
    x_fin, v_fin, m_fin = _lbfgs(name, x_de, GRID_FINE, maxiter=80)
    print(f"  fine L-BFGS: {v_fin:.8f}  ({time.time()-t0:.1f}s)", flush=True)

    # also refine the best coarse candidate on the fine grid
    best_coarse = min(candidates + [(v_de, x_de, m_de)], key=lambda z: z[0])
    x_alt, v_alt, m_alt = _lbfgs(name, best_coarse[1], GRID_FINE, maxiter=80)
    if v_alt < v_fin:
        x_fin, v_fin, m_fin = x_alt, v_alt, m_alt
        print(f"  alt fine better: {v_fin:.8f}", flush=True)

    return {
        "family": name,
        "x": x_fin.tolist(),
        "C_1_grid": v_fin,
        "L_over_Lcl_grid": ratio_L(v_fin),
        "meta": {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in m_fin.items()},
        "paper_grid": v0,
        "seconds": time.time() - t0,
    }


def validate_paper() -> dict:
    """Replay Lemma 11 second pair on the fast grid."""
    x = FAMILIES["A"]["paper"]
    v_fast, m_fast = eval_A(x, GRID_FAST)
    v_fine, m_fine = eval_A(x, GRID_FINE)
    official = rescore_official(m_fine)
    print("validate paper second pair:")
    print(f"  grid-fast  C_1={v_fast:.10f}  trunc={m_fast['C_1_trunc']:.10f}")
    print(f"  grid-fine  C_1={v_fine:.10f}  trunc={m_fine['C_1_trunc']:.10f}")
    print(f"  quad t=1e6 {official['C_1_float_tcut1e6']:.10f}")
    print(f"  full est   {official['C_1_full_est']:.10f}")
    return {"grid_fast": m_fast, "grid_fine": m_fine, "official": official}


def main() -> int:
    t_all = time.time()
    validation = validate_paper()

    results = {}
    best = None
    for i, name in enumerate(("A", "B", "C", "D")):
        rec = _run_family(name, GRID_FAST, seed=20260827 + 13 * i)
        print(f"  rescoring {name} with evaluate_c1 ...", flush=True)
        rec["official"] = rescore_official(rec["meta"])
        rec["L_over_Lcl"] = rec["official"]["ratios_full_est"]["L_over_Lcl"]
        results[name] = rec
        score = rec["official"]["C_1_full_est"]
        print(
            f"  official C_1_full={score:.10f}  "
            f"t_cut=1e6={rec['official']['C_1_float_tcut1e6']:.10f}  "
            f"L/Lcl={rec['L_over_Lcl']:.8f}",
            flush=True,
        )
        if best is None or score < best["official"]["C_1_full_est"]:
            best = rec

    # Fine-grid polish of the winner (DE on GRID_FINE is too expensive).
    win = best["family"]
    print(f"\n=== fine L-BFGS on winner {win} ===", flush=True)
    x_fin, v_fin, m_fin = _lbfgs(win, np.asarray(best["x"], dtype=float), GRID_FINE, maxiter=100)
    extra = {
        "family": win,
        "x": x_fin.tolist(),
        "C_1_grid": v_fin,
        "meta": {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in m_fin.items()},
        "seconds": 0.0,
    }
    extra["official"] = rescore_official(extra["meta"])
    extra["L_over_Lcl"] = extra["official"]["ratios_full_est"]["L_over_Lcl"]
    results[f"{win}_fine"] = extra
    if extra["official"]["C_1_full_est"] < best["official"]["C_1_full_est"]:
        best = extra

    payload = {
        "note": (
            "Parametric search for FHJN C_1. C_1_float_tcut1e6 is the same "
            "truncation as c1_functional.evaluate_c1 default / paper_replay. "
            "C_1_full_est adds the g≈0 tail ½√a · 2·t_cut^{-1/2}. "
            "Published Lemma 11 claims C_1 <= 0.373556 (conservative). "
            "Paper second-pair float at t_cut=1e6 is ~0.371716."
        ),
        "published_C1": 0.373556,
        "paper_second_float_tcut1e6": 0.37171594648351386,
        "validation": {
            "grid_fast_C1": validation["grid_fast"]["C_1"],
            "grid_fine_C1": validation["grid_fine"]["C_1"],
            "official": validation["official"],
        },
        "families": {
            k: {
                "family": v["family"],
                "x": v["x"],
                "C_1_grid": v["C_1_grid"],
                "official": v["official"],
                "meta": v["meta"],
                "L_over_Lcl": v["L_over_Lcl"],
                "seconds": v["seconds"],
            }
            for k, v in results.items()
        },
        "best": {
            "family": best["family"],
            "parameters": best["meta"],
            "x": best["x"],
            "C_1": best["official"]["C_1_full_est"],
            "C_1_tcut1e6": best["official"]["C_1_float_tcut1e6"],
            "C_1_plus_err_tcut1e6": best["official"]["C_1_plus_err_tcut1e6"],
            "C_1_grid": best["C_1_grid"],
            "L_over_Lcl": best["L_over_Lcl"],
            "L_over_Lcl_from_C1": ratio_L(best["official"]["C_1_full_est"]),
            "beats_published_0.373556": bool(best["official"]["C_1_full_est"] < 0.373556),
            "beats_paper_float_0.37172": bool(best["official"]["C_1_float_tcut1e6"] < 0.37171594648351386),
        },
        "seconds_total": time.time() - t_all,
    }
    dest = HERE / "opt_parametric.json"
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {dest}")
    print(
        f"BEST C_1_full={payload['best']['C_1']:.10f}  "
        f"t=1e6={payload['best']['C_1_tcut1e6']:.10f}  "
        f"L/Lcl={payload['best']['L_over_Lcl']:.8f}  family={best['family']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
