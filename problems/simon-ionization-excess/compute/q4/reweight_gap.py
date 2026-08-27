#!/usr/bin/env python3
"""Numerical slack in the P_max reweighting error.

On a fixed mid-radius grid the exact discrete lower form is

    I/D ≥ ∑_{ij} F_ij (s_i c_i + s_j c_j) μ_i μ_j / (2 ∑ s_k c_k μ_k)

with s_i ∈ [1/q, q]. The compact certificate replaces this by
φ(μ) − P (1−fmin), P=(q−1)/(q+1). If the true min over (μ,s) sits
well above that, a tighter error would move the leading coefficient.

Writes certs/reweight_gap.json. Not a lower bound by itself.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q2))

from beta3_kernel import FMIN_MP, assemble_mid  # noqa: E402

CERTS = HERE / "certs"
FMIN = float(FMIN_MP)


def slsqp_phi(A, c):
    n = A.shape[0]

    def fun(m):
        den = float(c @ m)
        if den <= 0:
            return 1e9
        return float(m @ A @ m) / den

    cons = {"type": "eq", "fun": lambda z: np.sum(z) - 1.0}
    bounds = [(0.0, 1.0)] * n
    best = 1e9
    rng = np.random.default_rng(2)
    starts = [np.ones(n) / n]
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        starts.append(e)
        best = min(best, fun(e))
    for _ in range(10):
        v = rng.random(n)
        starts.append(v / v.sum())
    for z0 in starts:
        res = minimize(
            fun,
            z0,
            bounds=bounds,
            constraints=cons,
            method="SLSQP",
            options={"maxiter": 400, "ftol": 1e-14},
        )
        if res.success:
            best = min(best, float(res.fun))
    return best


def exact_reweighted(F, c, mu, s):
    mu = np.clip(mu, 0.0, None)
    if mu.sum() <= 0:
        return 1e9
    mu = mu / mu.sum()
    sc = s * c * mu
    den = float(sc.sum())
    if den <= 0:
        return 1e9
    # num = ∑_i s_i c_i μ_i (∑_j F_ij μ_j)
    lam = F @ mu
    num = float(sc @ lam)
    return num / den


def min_reweighted(F, c, q, n_starts: int = 24):
    n = len(c)
    lo = 1.0 / q
    hi = q

    def unpack(x):
        z = x[:n]
        mu = np.exp(z - np.max(z))
        mu = mu / mu.sum()
        s = lo + (hi - lo) * 1.0 / (1.0 + np.exp(-np.clip(x[n:], -20, 20)))
        return mu, s

    def fun(x):
        mu, s = unpack(x)
        return exact_reweighted(F, c, mu, s)

    rng = np.random.default_rng(7)
    starts = [np.zeros(2 * n)]
    starts.append(np.concatenate([np.zeros(n), np.full(n, 2.0)]))  # s near q
    starts.append(np.concatenate([np.zeros(n), np.full(n, -2.0)]))  # s near 1/q
    for _ in range(n_starts):
        starts.append(rng.normal(0.0, 0.8, size=2 * n))
    best = 1e9
    best_mu = None
    best_s = None
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 4000})
        val = float(res.fun)
        if val < best:
            best = val
            best_mu, best_s = unpack(res.x)
    return best, best_mu, best_s


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for R, n in ((4, 18), (8, 20), (12, 22)):
        blob = assemble_mid(R, n)
        F = np.array([[float(blob["F_lo"][i][j]) for j in range(n)] for i in range(n)])
        c = np.array([float(blob["rmid2"][i]) for i in range(n)])
        A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
        q = float(blob["q_iv"].b) if hasattr(blob["q_iv"], "b") else None
        # q as float from interval upper
        from mpmath import mpf

        q = float(mpf(blob["q_iv"].b))
        P = (q - 1.0) / (q + 1.0)
        phi = slsqp_phi(A, c)
        bound = phi - P * (1.0 - FMIN)
        rw, mu, s = min_reweighted(F, c, q)
        slack = rw - bound
        rows.append(
            {
                "R": R,
                "n": n,
                "q": q,
                "P": P,
                "phi": phi,
                "P_bound": bound,
                "reweighted_min": rw,
                "slack": slack,
                "s_min": float(np.min(s)),
                "s_max": float(np.max(s)),
                "mu_entropy": float(-(mu * np.log(np.clip(mu, 1e-30, 1))).sum()),
            }
        )
        print(
            f"R={R} n={n}  φ={phi:.6f}  P-bound={bound:.6f}  "
            f"reweight_min={rw:.6f}  slack={slack:.6f}"
        )

    out = {
        "not_a_lower_bound": True,
        "rows": rows,
        "note": (
            "Positive slack means the TV error P(1-fmin) is pessimistic "
            "on this grid. Slack is not a certificate."
        ),
    }
    path = CERTS / "reweight_gap.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
