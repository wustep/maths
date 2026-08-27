#!/usr/bin/env python3
"""Discretized search for an FHJN pair (f, φ).

φ is a nonnegative histogram on M equal bins of [0, T_φ].
f is a nonnegative histogram on a log-grid of [tmin, tmax] plus a
power-law tail, with f(0)=1 and a horizontal stretch so that ∫f²=1.

Alternates projected gradient and L-BFGS-B. Finalists are re-scored
with ``c1_functional.evaluate_c1``.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from c1_functional import evaluate_c1, paper_second_pair, ratio_from_c1
from grid_c1 import FastC1, normalize_mu, power_decay_vec, ratio_L, stretch_l2_unit
from optimize_parametric import pair_callables, _f_two_scale_on, _two_scale_sigma

HERE = Path(__file__).resolve().parent

GRID = FastC1(ns=256, nt=2048, tmin=1e-8, tmax=1e8)


def project_simplex(v: np.ndarray, z: float = 1.0) -> np.ndarray:
    """Euclidean projection onto {x >= 0, sum x = z}."""
    v = np.asarray(v, dtype=np.float64)
    n = v.size
    u = np.sort(v)[::-1]
    cssv = np.cumsum(u) - z
    ind = np.arange(1, n + 1)
    cond = u - cssv / ind > 0
    rho = int(ind[cond][-1])
    theta = cssv[rho - 1] / rho
    return np.maximum(v - theta, 0.0)


class PhiHist:
    def __init__(self, T: float, M: int, heights: np.ndarray | None = None):
        self.T = float(T)
        self.M = int(M)
        self.dx = self.T / self.M
        self.centers = (np.arange(self.M) + 0.5) * self.dx
        if heights is None:
            h = np.ones(self.M)
        else:
            h = np.maximum(np.asarray(heights, dtype=float), 0.0)
        mass = float(h.sum() * self.dx)
        self.h = h / mass if mass > 0 else np.ones(self.M) / (self.M * self.dx)

    def values_on(self, s: np.ndarray) -> np.ndarray:
        s = np.asarray(s, dtype=float)
        out = np.zeros_like(s)
        m = (s >= 0.0) & (s <= self.T)
        idx = np.minimum((s[m] / self.dx).astype(int), self.M - 1)
        out[m] = self.h[idx]
        return out

    def a_phi2(self) -> float:
        return float(np.dot(self.h, self.h) * self.dx)

    def callable(self):
        T, dx, M, h = self.T, self.dx, self.M, self.h.copy()

        def phi(s: float) -> float:
            if s < 0.0 or s > T:
                return 0.0
            i = min(int(s / dx), M - 1)
            return float(h[i])

        return phi


class FHist:
    """Log-grid shape ψ with ψ=1 on [0, tmin], power-law tail, stretch to L2=1."""

    def __init__(
        self,
        *,
        n: int = 48,
        tmin: float = 1e-3,
        tmax: float = 80.0,
        p: float = 1.2,
        shape: np.ndarray | None = None,
    ):
        self.n = int(n)
        self.tmin = float(tmin)
        self.tmax = float(tmax)
        self.p = float(p)
        self.nodes = np.logspace(np.log10(self.tmin), np.log10(self.tmax), self.n)
        self.log_nodes = np.log(self.nodes)
        if shape is None:
            self.shape = np.ones(self.n)
        else:
            self.shape = np.maximum(np.asarray(shape, dtype=float), 1e-12)
            self.shape[0] = 1.0
        self.sigma = self._sigma()

    def _psi_on_ref(self, u: np.ndarray) -> np.ndarray:
        u = np.asarray(u, dtype=float)
        out = np.empty_like(u)
        small = u <= self.tmin
        large = u >= self.tmax
        mid = ~small & ~large
        out[small] = 1.0
        tail_c = self.shape[-1] * (self.tmax ** self.p)
        out[large] = tail_c * np.power(np.maximum(u[large], self.tmax), -self.p)
        if np.any(mid):
            log_shape = np.log(np.maximum(self.shape, 1e-30))
            out[mid] = np.exp(np.interp(np.log(u[mid]), self.log_nodes, log_shape))
        return out

    def _sigma(self) -> float:
        psi = self._psi_on_ref(GRID.u)
        sig = stretch_l2_unit(psi, GRID.u, GRID.logu, GRID.tmin, GRID.tmax)
        if not np.isfinite(sig) or sig <= 0.0:
            return 1.0
        return float(sig)

    def refresh(self) -> None:
        self.shape = np.maximum(self.shape, 1e-12)
        self.shape[0] = 1.0
        if self.p <= 0.52:
            self.p = 0.52
        self.sigma = self._sigma()

    def eval(self, t: np.ndarray) -> np.ndarray:
        return self._psi_on_ref(np.asarray(t, dtype=float) / self.sigma)

    def callable(self):
        def f(t: float) -> float:
            if t <= 0.0:
                return 1.0
            return float(self.eval(np.array([t]))[0])

        return f

    def to_dict(self) -> dict:
        return {
            "n": self.n,
            "tmin": self.tmin,
            "tmax": self.tmax,
            "p": self.p,
            "sigma": self.sigma,
            "shape": self.shape.tolist(),
            "nodes": self.nodes.tolist(),
        }


def f_from_power(alpha: float, beta: float) -> tuple:
    mu = normalize_mu(alpha, beta)

    def f_vec(t):
        return power_decay_vec(np.asarray(t), mu, alpha, beta)

    def f_scalar(t: float) -> float:
        if t <= 0.0:
            return 1.0
        return float((1.0 + mu * (t**alpha)) ** (-beta))

    return f_vec, f_scalar, mu


def discretize_phi_from_callable(phi, T: float, M: int) -> PhiHist:
    dx = T / M
    centers = (np.arange(M) + 0.5) * dx
    h = np.array([max(phi(s), 0.0) for s in centers], dtype=float)
    return PhiHist(T, M, h)


def discretize_f_from_callable(f, n: int = 48, tmin=1e-3, tmax=80.0) -> FHist:
    nodes = np.logspace(np.log10(tmin), np.log10(tmax), n)
    # f already has f(0)=1 and ∫f²=1; treat it as the shape on the actual axis,
    # then let FHist re-stretch (should recover σ≈1).
    vals = np.array([max(f(t), 1e-12) for t in nodes], dtype=float)
    # normalize so vals[0] corresponds to nearly 1
    if vals[0] <= 0:
        vals[0] = 1.0
    scale0 = vals[0]
    vals = vals / scale0
    # estimate p from the last two nodes
    if vals[-1] > 0 and vals[-2] > 0:
        p = -math.log(vals[-1] / vals[-2]) / math.log(nodes[-1] / nodes[-2])
        p = float(np.clip(p, 0.55, 8.0))
    else:
        p = 1.2
    fh = FHist(n=n, tmin=tmin, tmax=tmax, p=p, shape=vals)
    return fh


def c1_pair(f_vec, phi: PhiHist, grid: FastC1 = GRID) -> dict:
    s, w = grid.s_nodes([(0.0, phi.T)])
    pv = phi.values_on(s)
    st = grid.t[:, None] * s[None, :]
    f_st = np.clip(f_vec(st), 0.0, np.inf)
    return grid.c1_from_f_phi_arrays(s, w, pv, f_st)


def design_matrix(f_vec, phi: PhiHist, grid: FastC1 = GRID) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A[j,i] = dx * f(center_i * t_j), so g = A @ h."""
    t = grid.t
    c = phi.centers
    st = t[:, None] * c[None, :]
    A = f_vec(st) * phi.dx
    return A, t, grid.logt


def c1_from_A(A: np.ndarray, h: np.ndarray, phi: PhiHist, grid: FastC1 = GRID) -> tuple[float, np.ndarray, float]:
    g = np.clip(A @ h, 0.0, 1.0)
    a = float(np.dot(h, h) * phi.dx)
    rec = grid.c1_from_g(g, a, include_tails=True)
    return rec["C_1"], g, a


def grad_phi(A: np.ndarray, h: np.ndarray, g: np.ndarray, a: float, phi: PhiHist, grid: FastC1) -> np.ndarray:
    omg = 1.0 - g
    # dI/dg_j ≈ -2 (1-g_j) * (t_j^{-1/2} * dlogt) with trap weights
    dlog = grid.logt[1] - grid.logt[0]
    wt = np.power(grid.t, -0.5) * dlog
    wt[0] *= 0.5
    wt[-1] *= 0.5
    dI_dg = -2.0 * omg * wt
    A_g = 0.5 * (float(np.dot(omg * omg, wt)) + rec_tail_I(g, grid))
    # use stored A_g from definition C=sqrt(a)*A_g; recompute consistently
    rec = grid.c1_from_g(g, a, include_tails=True)
    A_g = rec["A_g"]
    sqrt_a = math.sqrt(max(a, 1e-30))
    dC_dh = (h * phi.dx / sqrt_a) * A_g + sqrt_a * 0.5 * (A.T @ dI_dg)
    return dC_dh


def rec_tail_I(g: np.ndarray, grid: FastC1) -> float:
    return 0.0


def optimize_phi_lbfgs(A: np.ndarray, phi: PhiHist, grid: FastC1, maxiter: int = 250) -> tuple[PhiHist, float]:
    M = phi.M
    z0 = np.log(np.maximum(phi.h, 1e-12))

    def unpack(z):
        e = np.exp(z - np.max(z))
        h = e / (e.sum() * phi.dx)
        return h

    def fun(z):
        h = unpack(z)
        C, _, _ = c1_from_A(A, h, phi, grid)
        return C

    def jac(z):
        h = unpack(z)
        C, g, a = c1_from_A(A, h, phi, grid)
        dC_dh = grad_phi(A, h, g, a, phi, grid)
        # h_i = e_i / (S dx), S=sum e
        e = np.exp(z - np.max(z))
        S = float(e.sum())
        # dh_k/dz_j = (1/dx) * (δ_{kj} e_k / S - e_k e_j / S²)
        # dC/dz_j = sum_k dC/dh_k * dh_k/dz_j
        dC_de_scaled = dC_dh / phi.dx  # wrt (e/S)
        mean = float(np.dot(dC_de_scaled, e / S))
        dC_dz = (e / S) * (dC_de_scaled - mean)
        return dC_dz

    res = minimize(
        fun,
        z0,
        method="L-BFGS-B",
        jac=jac,
        options={"maxiter": maxiter, "maxfun": 8 * maxiter, "ftol": 1e-12},
    )
    h = unpack(res.x)
    out = PhiHist(phi.T, M, h)
    C, _, _ = c1_from_A(A, out.h, out, grid)
    return out, float(C)


def optimize_phi_pg(A: np.ndarray, phi: PhiHist, grid: FastC1, steps: int = 400) -> tuple[PhiHist, float]:
    h = phi.h.copy()
    # work in probability weights y = h*dx, sum y=1
    y = h * phi.dx
    C, g, a = c1_from_A(A, y / phi.dx, phi, grid)
    step = 0.25
    for _ in range(steps):
        dC_dh = grad_phi(A, y / phi.dx, g, a, phi, grid)
        dC_dy = dC_dh / phi.dx
        improved = False
        for _bt in range(18):
            y_new = project_simplex(y - step * dC_dy, 1.0)
            h_new = y_new / phi.dx
            C_new, g_new, a_new = c1_from_A(A, h_new, phi, grid)
            if C_new <= C + 1e-16:
                y, C, g, a = y_new, C_new, g_new, a_new
                improved = True
                step *= 1.15
                break
            step *= 0.45
        if not improved:
            break
        step = min(step, 4.0)
    out = PhiHist(phi.T, phi.M, y / phi.dx)
    return out, float(C)


def optimize_f_power(phi: PhiHist, x0: np.ndarray, grid: FastC1) -> tuple[tuple, float, np.ndarray]:
    bounds = [(0.8, 10.0), (0.08, 2.5)]

    def fun(x):
        alpha, beta = float(x[0]), float(x[1])
        if 2.0 * alpha * beta <= 1.05:
            return 1e9
        f_vec, _, _ = f_from_power(alpha, beta)
        return c1_pair(f_vec, phi, grid)["C_1"]

    res = minimize(
        fun,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 80, "maxfun": 400, "ftol": 1e-12},
    )
    alpha, beta = float(res.x[0]), float(res.x[1])
    f_vec, f_sc, mu = f_from_power(alpha, beta)
    C = c1_pair(f_vec, phi, grid)["C_1"]
    return (f_vec, f_sc, mu, alpha, beta), float(C), res.x


def optimize_f_twoscale(phi: PhiHist, x0: np.ndarray, grid: FastC1) -> tuple[tuple, float, np.ndarray]:
    bounds = [
        (0.8, 14.0),
        (0.06, 2.5),
        (0.8, 14.0),
        (0.06, 2.5),
        (0.0, 5.0),
        (0.1, 10.0),
    ]

    def fun(x):
        a1, b1, a2, b2, lam, r = [float(v) for v in x]
        if min(a1, b1, a2, b2, r) <= 0.0 or lam < 0.0:
            return 1e9
        if 2.0 * a1 * b1 <= 1.05:
            return 1e9
        sigma = _two_scale_sigma(a1, b1, a2, b2, lam, r, grid)
        if not np.isfinite(sigma) or sigma <= 0.0:
            return 1e9

        def f_vec(t):
            return _f_two_scale_on(np.asarray(t), a1, b1, a2, b2, lam, r, sigma)

        return c1_pair(f_vec, phi, grid)["C_1"]

    res = minimize(
        fun,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 70, "maxfun": 400, "ftol": 1e-12},
    )
    a1, b1, a2, b2, lam, r = [float(v) for v in res.x]
    sigma = _two_scale_sigma(a1, b1, a2, b2, lam, r, grid)

    def f_vec(t):
        return _f_two_scale_on(np.asarray(t), a1, b1, a2, b2, lam, r, sigma)

    def f_sc(t: float) -> float:
        if t <= 0.0:
            return 1.0
        return float(f_vec(np.array([t]))[0])

    C = c1_pair(f_vec, phi, grid)["C_1"]
    return (f_vec, f_sc, dict(alpha1=a1, beta1=b1, alpha2=a2, beta2=b2, lam=lam, r=r, sigma=sigma)), float(C), res.x


def optimize_f_hist_lbfgs(phi: PhiHist, fh: FHist, grid: FastC1, maxiter: int = 120) -> tuple[FHist, float]:
    # free vars: log(shape[1:]), log(p-0.5)
    nfree = fh.n - 1
    z0 = np.empty(nfree + 1)
    z0[:nfree] = np.log(np.maximum(fh.shape[1:], 1e-12))
    z0[-1] = math.log(max(fh.p - 0.5, 1e-3))

    def unpack(z):
        shape = np.empty(fh.n)
        shape[0] = 1.0
        shape[1:] = np.exp(np.clip(z[:nfree], -20.0, 8.0))
        p = 0.5 + math.exp(float(np.clip(z[-1], -6.0, 4.0)))
        out = FHist(n=fh.n, tmin=fh.tmin, tmax=fh.tmax, p=p, shape=shape)
        return out

    def fun(z):
        cur = unpack(z)
        rec = c1_pair(cur.eval, phi, grid)
        return rec["C_1"]

    res = minimize(
        fun,
        z0,
        method="L-BFGS-B",
        options={"maxiter": maxiter, "maxfun": 6 * maxiter, "ftol": 1e-12, "maxls": 20},
    )
    best = unpack(res.x)
    C = c1_pair(best.eval, phi, grid)["C_1"]
    return best, float(C)


def optimize_f_hist_pg(phi: PhiHist, fh: FHist, grid: FastC1, steps: int = 80) -> tuple[FHist, float]:
    log_s = np.log(np.maximum(fh.shape, 1e-12))
    log_s[0] = 0.0
    p = fh.p
    C = c1_pair(fh.eval, phi, grid)["C_1"]
    step = 0.08
    eps = 1e-4
    for _ in range(steps):
        # finite-diff gradient on a random subset + p (cheaper than full)
        rng_idx = np.arange(1, fh.n)
        g_log = np.zeros_like(log_s)
        for k in rng_idx:
            log_s[k] += eps
            trial = FHist(n=fh.n, tmin=fh.tmin, tmax=fh.tmax, p=p, shape=np.exp(log_s))
            Cp = c1_pair(trial.eval, phi, grid)["C_1"]
            log_s[k] -= eps
            g_log[k] = (Cp - C) / eps
        trial_p = FHist(n=fh.n, tmin=fh.tmin, tmax=fh.tmax, p=max(p + eps, 0.55), shape=np.exp(log_s))
        gp = (c1_pair(trial_p.eval, phi, grid)["C_1"] - C) / eps
        improved = False
        for _bt in range(12):
            log_new = log_s - step * g_log
            log_new[0] = 0.0
            log_new = np.clip(log_new, -18.0, 6.0)
            p_new = float(np.clip(p - step * gp, 0.55, 8.0))
            trial = FHist(n=fh.n, tmin=fh.tmin, tmax=fh.tmax, p=p_new, shape=np.exp(log_new))
            Cn = c1_pair(trial.eval, phi, grid)["C_1"]
            if Cn <= C + 1e-16:
                log_s, p, C, fh = log_new, p_new, Cn, trial
                improved = True
                step *= 1.1
                break
            step *= 0.4
        if not improved:
            break
        step = min(step, 1.0)
    return fh, float(C)


def rescore_hist(f_sc, phi: PhiHist) -> dict:
    r6 = evaluate_c1(f_sc, phi.callable(), support=phi.T, t_cut=1e6)
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
    }


def load_parametric_seed() -> dict | None:
    path = HERE / "opt_parametric.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data.get("best")


def run_support(T: float, M: int, n_f: int, seed_meta: dict | None) -> dict:
    print(f"\n--- hist support T={T} M={M} ---", flush=True)
    twoscale_x = np.array([4.5, 0.25, 1.5, 1.0, 0.15, 2.0])
    used_seed = False
    if seed_meta and seed_meta.get("parameters"):
        try:
            params = seed_meta["parameters"]
            f0, phi0, support0, extra = pair_callables(params)
            phi = discretize_phi_from_callable(phi0, T, M)
            if params.get("family") == "C":
                twoscale_x = np.array(
                    [
                        params["alpha1"],
                        params["beta1"],
                        params["alpha2"],
                        params["beta2"],
                        params["lam"],
                        params["r"],
                    ],
                    dtype=float,
                )
                sigma = float(params["sigma"])

                def f_vec(t, _p=params, _s=sigma):
                    return _f_two_scale_on(
                        np.asarray(t),
                        _p["alpha1"],
                        _p["beta1"],
                        _p["alpha2"],
                        _p["beta2"],
                        _p["lam"],
                        _p["r"],
                        _s,
                    )

                f_sc = f0
                mu = None
                alpha, beta = float(params["alpha1"]), float(params["beta1"])
            elif params.get("family") in ("A", "B", "D") and "alpha" in params:
                f_vec, f_sc, mu = f_from_power(params["alpha"], params["beta"])
                alpha, beta = params["alpha"], params["beta"]
            else:
                f_sc = f0
                mu = extra.get("mu")
                alpha, beta = params.get("alpha", 4.5), params.get("beta", 0.25)

                def f_vec(t, _f=f0):
                    arr = np.asarray(t, dtype=float)
                    return np.vectorize(_f)(arr)

            used_seed = True
        except Exception as exc:
            print(f"  seed failed ({exc}); using paper pair", flush=True)
            used_seed = False

    if not used_seed:
        f_paper, phi_paper, mu, c0 = paper_second_pair()
        phi = discretize_phi_from_callable(phi_paper, T, M)
        f_vec, f_sc, mu = f_from_power(4.5, 0.25)
        alpha, beta = 4.5, 0.25

    rec0 = c1_pair(f_vec, phi, GRID)
    print(f"  init grid C_1={rec0['C_1']:.8f}", flush=True)

    A, _, _ = design_matrix(f_vec, phi, GRID)
    phi_a, Ca = optimize_phi_lbfgs(A, phi, GRID, maxiter=160)
    phi_b, Cb = optimize_phi_pg(A, phi_a, GRID, steps=180)
    phi = phi_b if Cb <= Ca else phi_a
    print(f"  φ L-BFGS {Ca:.8f}  PG {Cb:.8f}", flush=True)

    (pack_ts, C_ts, xts) = optimize_f_twoscale(phi, twoscale_x, GRID)
    f_vec, f_sc, ts_meta = pack_ts
    print(f"  f two-scale C_1={C_ts:.8f} {ts_meta}", flush=True)

    (f_vec_p, f_sc_p, mu, alpha, beta), C_f, xab = optimize_f_power(phi, np.array([alpha, beta]), GRID)
    print(f"  f power L-BFGS α={alpha:.4f} β={beta:.4f} C_1={C_f:.8f}", flush=True)
    if C_f < C_ts:
        f_vec, f_sc = f_vec_p, f_sc_p
        C_ts = C_f

    A, _, _ = design_matrix(f_vec, phi, GRID)
    phi_a, Ca = optimize_phi_lbfgs(A, phi, GRID, maxiter=140)
    phi_b, Cb = optimize_phi_pg(A, phi_a, GRID, steps=140)
    phi = phi_b if Cb <= Ca else phi_a
    print(f"  φ again {min(Ca,Cb):.8f}", flush=True)

    (pack_ts, C_ts, xts) = optimize_f_twoscale(phi, xts, GRID)
    f_vec, f_sc, ts_meta = pack_ts
    print(f"  f two-scale again C_1={C_ts:.8f}", flush=True)

    fh = discretize_f_from_callable(f_sc, n=n_f)
    rec_h = c1_pair(fh.eval, phi, GRID)
    print(f"  f-hist init {rec_h['C_1']:.8f}", flush=True)
    fh, C_fh = optimize_f_hist_lbfgs(phi, fh, GRID, maxiter=50)
    print(f"  f-hist L-BFGS {C_fh:.8f}", flush=True)
    fh, C_pg = optimize_f_hist_pg(phi, fh, GRID, steps=18)
    print(f"  f-hist PG {C_pg:.8f}", flush=True)

    A, _, _ = design_matrix(fh.eval, phi, GRID)
    phi_a, Ca = optimize_phi_lbfgs(A, phi, GRID, maxiter=100)
    phi_b, Cb = optimize_phi_pg(A, phi_a, GRID, steps=100)
    phi = phi_b if Cb <= Ca else phi_a
    C_end = c1_pair(fh.eval, phi, GRID)["C_1"]
    C_par = c1_pair(f_vec, phi, GRID)["C_1"]
    print(f"  end hist-f {C_end:.8f}  two-scale-f {C_par:.8f}", flush=True)

    if C_end <= C_par:
        f_sc_best = fh.callable()
        C_grid = C_end
        f_kind = "hist"
    else:
        f_sc_best = f_sc
        C_grid = C_par
        f_kind = "twoscale"
        fh = discretize_f_from_callable(f_sc, n=n_f)

    official = rescore_hist(f_sc_best, phi)
    print(
        f"  official C_1_full {official['C_1_full_est']:.10f}  "
        f"t=1e6 {official['C_1_float_tcut1e6']:.10f}",
        flush=True,
    )
    return {
        "T": T,
        "M": M,
        "f_kind": f_kind,
        "C_1_grid": C_grid,
        "alpha": alpha,
        "beta": beta,
        "mu": mu if f_kind == "power" else None,
        "twoscale": ts_meta,
        "phi_heights": phi.h.tolist(),
        "phi_dx": phi.dx,
        "f_hist": fh.to_dict(),
        "official": official,
        "L_over_Lcl": official["ratios_full_est"]["L_over_Lcl"],
    }


def main() -> int:
    t0 = time.time()
    seed = load_parametric_seed()
    if seed:
        print(f"loaded parametric seed C_1={seed.get('C_1')}", flush=True)
    else:
        print("no parametric seed; starting from Lemma 11 second pair", flush=True)

    T_seed = 1.66
    if seed and seed.get("parameters", {}).get("T"):
        T_seed = float(seed["parameters"]["T"])
    jobs = [
        (T_seed, 72, 40),
        (1.0, 64, 40),
        (2.1, 80, 40),
        (1.35, 72, 40),
    ]
    runs = []
    best = None
    for T, M, nf in jobs:
        rec = run_support(T, M, nf, seed)
        runs.append(rec)
        score = rec["official"]["C_1_full_est"]
        if best is None or score < best["official"]["C_1_full_est"]:
            best = rec

    # refine winner at higher M
    print("\n=== refine winner at higher resolution ===", flush=True)
    rec = run_support(best["T"], min(best["M"] + 32, 128), 56, seed)
    runs.append(rec)
    if rec["official"]["C_1_full_est"] < best["official"]["C_1_full_est"]:
        best = rec

    payload = {
        "note": (
            "Histogram search for FHJN C_1. φ is a nonnegative step function "
            "on equal bins of [0,T]. f is either a normalized power decay or "
            "a log-grid histogram with power-law tail and f(0)=1. "
            "Official numbers come from c1_functional.evaluate_c1."
        ),
        "published_C1": 0.373556,
        "paper_second_float_tcut1e6": 0.37171594648351386,
        "runs": [
            {
                "T": r["T"],
                "M": r["M"],
                "f_kind": r["f_kind"],
                "C_1_grid": r["C_1_grid"],
                "official": r["official"],
                "L_over_Lcl": r["L_over_Lcl"],
                "alpha": r["alpha"],
                "beta": r["beta"],
            }
            for r in runs
        ],
        "best": {
            "T": best["T"],
            "M": best["M"],
            "f_kind": best["f_kind"],
            "parameters": {
                "T_phi": best["T"],
                "M": best["M"],
                "phi_heights": best["phi_heights"],
                "phi_dx": best["phi_dx"],
                "alpha": best["alpha"],
                "beta": best["beta"],
                "mu": best["mu"],
                "f_hist": best["f_hist"],
                "f_kind": best["f_kind"],
            },
            "C_1": best["official"]["C_1_full_est"],
            "C_1_tcut1e6": best["official"]["C_1_float_tcut1e6"],
            "C_1_plus_err_tcut1e6": best["official"]["C_1_plus_err_tcut1e6"],
            "C_1_grid": best["C_1_grid"],
            "L_over_Lcl": best["L_over_Lcl"],
            "L_over_Lcl_from_C1": ratio_L(best["official"]["C_1_full_est"]),
            "beats_published_0.373556": bool(best["official"]["C_1_full_est"] < 0.373556),
            "beats_paper_float_0.37172": bool(
                best["official"]["C_1_float_tcut1e6"] < 0.37171594648351386
            ),
        },
        "seconds_total": time.time() - t0,
    }
    dest = HERE / "opt_hist.json"
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {dest}")
    print(
        f"BEST hist C_1_full={payload['best']['C_1']:.10f}  "
        f"t=1e6={payload['best']['C_1_tcut1e6']:.10f}  "
        f"L/Lcl={payload['best']['L_over_Lcl']:.8f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
