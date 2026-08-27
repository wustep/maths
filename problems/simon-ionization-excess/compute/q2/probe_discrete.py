#!/usr/bin/env python3
"""Probe how tight G_min / c_max and F-average discrete bounds are."""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize


def f_of(t):
    if t <= 0:
        return 1.0
    return (1.0 + t**3) / (1.0 + t**2)


def g_of(r, u):
    return (r**3 + u**3) / (2.0 * max(r, u))


def fmin_on_bins(a1, b1, a2, b2):
    # t = min/max; range of t on the rectangle
    # evaluate f at corners and, if t0 is inside, at t0
    ts = []
    for r in (a1, b1):
        for u in (a2, b2):
            mn, mx = (r, u) if r <= u else (u, r)
            ts.append(mn / mx)
    tlo, thi = min(ts), max(ts)
    t0 = 0.596071637983
    samples = [tlo, thi]
    if tlo <= t0 <= thi:
        samples.append(t0)
    # also a few interior
    for k in range(1, 6):
        samples.append(tlo + (thi - tlo) * k / 6)
    return min(f_of(t) for t in samples)


def gmin_on_bins(a1, b1, a2, b2):
    # min of g on the closed rectangle. Critical points:
    # g is increasing in both arguments in a weak sense; check boundary.
    # Use a dense corner+edge sample plus analytic corners.
    rs = np.linspace(a1, b1, 9)
    us = np.linspace(a2, b2, 9)
    return min(g_of(r, u) for r in rs for u in us)


def assemble(n, R):
    edges = np.geomspace(1.0, R, n + 1)
    a, b = edges[:-1], edges[1:]
    F = np.zeros((n, n))
    G = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            F[i, j] = fmin_on_bins(a[i], b[i], a[j], b[j])
            G[i, j] = gmin_on_bins(a[i], b[i], a[j], b[j])
    cmax = b**2
    amin2 = a**2
    rmid2 = a * b  # geometric-mean squared
    return edges, F, G, cmax, amin2, rmid2


def min_rayleigh(A, c, n_starts=20):
    n = len(c)

    def phi(m):
        m = np.clip(m, 0, None)
        s = m.sum()
        if s <= 0:
            return 1e9
        m = m / s
        return float(m @ A @ m) / float(c @ m)

    best = 1e9
    rng = np.random.default_rng(0)
    for t in range(n_starts):
        if t == 0:
            x0 = np.ones(n)
        elif t == 1:
            x0 = 1.0 / c
        else:
            x0 = rng.random(n)
        opt = minimize(
            phi,
            x0,
            method="Nelder-Mead",
            options={"maxiter": 1500, "xatol": 1e-10, "fatol": 1e-12},
        )
        val = phi(opt.x)
        if val < best:
            best = val
    # also vertices
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1
        best = min(best, phi(e))
    return best


def main():
    fmin = 0.8941074569749823
    print(f"HPS fmin = {fmin:.8f}")
    for n, R in ((8, 4.0), (12, 4.0), (16, 4.0), (12, 6.0), (20, 4.0), (24, 5.0)):
        edges, F, G, cmax, amin2, rmid2 = assemble(n, R)
        # loose: Gmin / cmax
        loose = min_rayleigh(G, cmax)
        # F with a^2 in num and b^2 in den
        A_ab = F * amin2[:, None]  # (F_ij * a_i^2); quad form m^T A m = sum F a_i^2 m_i m_j
        # symmetrize for the optimizer (same quad form)
        A_ab_s = 0.5 * (A_ab + A_ab.T)
        fab = min_rayleigh(A_ab_s, cmax)
        # F with mid r^2 in both
        A_mid = 0.5 * (F * rmid2[:, None] + (F * rmid2[:, None]).T)
        fmid = min_rayleigh(A_mid, rmid2)
        print(
            f"n={n:2d} R={R:.1f}  G/cmax={loose:.6f}  F a^2/b^2={fab:.6f}  "
            f"F mid={fmid:.6f}  beats={loose>fmin}/{fab>fmin}/{fmid>fmin}"
        )


if __name__ == "__main__":
    main()
