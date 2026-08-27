#!/usr/bin/env python3
"""Large-n φ_mid and a longer DNN attempt."""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize

from probe_discrete import assemble, f_of


FMIN = 0.8941074569749823


def build_AF(n, R):
    edges = np.geomspace(1.0, R, n + 1)
    a, b = edges[:-1], edges[1:]
    # t-range via corners; f min from unimodality
    t0 = 0.5960716379833215
    F = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            ts = []
            for r in (a[i], b[i]):
                for u in (a[j], b[j]):
                    mn, mx = (r, u) if r <= u else (u, r)
                    ts.append(mn / mx)
            tlo, thi = min(ts), max(ts)
            if a[i] <= b[j] and a[j] <= b[i]:
                thi = 1.0
            if thi <= t0:
                F[i, j] = f_of(thi)
            elif tlo >= t0:
                F[i, j] = f_of(tlo)
            else:
                F[i, j] = f_of(t0)
    rmid2 = a * b
    A = F * 0.5 * (rmid2[:, None] + rmid2[None, :])
    return A, rmid2, F, edges


def min_rayleigh_slsqp(A, c):
    n = len(c)

    def phi(x):
        m = np.clip(x, 0, None)
        s = m.sum()
        m = m / s
        return float(m @ A @ m) / float(c @ m)

    cons = {"type": "eq", "fun": lambda x: np.sum(x) - 1.0}
    bnds = [(0, None)] * n
    best = 1.0
    starts = [np.ones(n) / n, 1.0 / c]
    # power-law-like
    edges_ratio = np.linspace(0, 1, n)
    starts.append(np.exp(-2.0 * edges_ratio))
    rng = np.random.default_rng(2)
    for _ in range(6):
        starts.append(rng.random(n))
    for s in starts:
        s = np.asarray(s, float)
        s = s / s.sum()
        opt = minimize(phi, s, method="SLSQP", bounds=bnds, constraints=cons,
                       options={"maxiter": 400, "ftol": 1e-12})
        best = min(best, phi(opt.x), phi(s))
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1
        best = min(best, phi(e))
    return best


def dnn_split(M, iters=2000):
    A = np.array(M, float, copy=True)
    B = np.zeros_like(A)
    for k in range(iters):
        S = A + B
        corr = 0.5 * (M - S)
        A = A + corr
        B = B + corr
        A = 0.5 * (A + A.T)
        w, V = np.linalg.eigh(A)
        A = (V * np.clip(w, 0, None)) @ V.T
        B = np.maximum(B, 0.0)
    resid = float(np.max(np.abs(A + B - M)))
    wmin = float(np.linalg.eigvalsh(0.5 * (A + A.T))[0])
    return resid, wmin, float(np.min(B)), A, B


def main():
    configs = [
        (20, 4.0),
        (24, 8.0),
        (32, 8.0),
        (32, 16.0),
        (40, 16.0),
        (48, 16.0),
        (64, 16.0),
        (48, 32.0),
        (64, 32.0),
        (80, 32.0),
    ]
    for n, R in configs:
        A, c, F, edges = build_AF(n, R)
        phi = min_rayleigh_slsqp(A, c)
        q = R ** (1.0 / n)
        theta = q - 1.0
        err = (theta / (1.0 - theta)) * (1.0 - FMIN)
        print(f"n={n:3d} R={R:5.1f} q={q:.4f} φ={phi:.6f} err={err:.5f} "
              f"γ≤{phi-err:.6f}  beats={phi-err>FMIN}")
        g_asp = phi - err
        # tail factor for α = 1/sqrt(R)  (window [α,1/α] has aspect R)
        alpha2 = 1.0 / R
        factor = (1.0 - alpha2) ** 2
        print(f"         tail factor (1-1/R)^2={factor:.5f}  global≥{factor*g_asp:.6f}  "
              f"global_beats={factor*g_asp>FMIN}")
        # DNN at target slightly below φ
        for claimed in (0.896, 0.898, 0.900):
            target = claimed + err
            if target > phi + 0.002:
                continue
            M = A - (target / 2.0) * (np.outer(c, np.ones(n)) + np.outer(np.ones(n), c))
            resid, wmin, bmin, _, _ = dnn_split(M, iters=800)
            print(f"           claimed {claimed} targetφ {target:.5f}  "
                  f"DNN resid={resid:.2e} wmin={wmin:.2e}")


if __name__ == "__main__":
    main()
