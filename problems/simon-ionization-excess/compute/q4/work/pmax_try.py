#!/usr/bin/env python3
"""Check candidate replacements for P(1-fmin) in the compact TV step.

Stdlib + numpy only. Not a certificate.

Tests:
  (A) per-mu spread  P * (max_i λ_i - min_i λ_i)  vs  P(1-fmin)
  (B) per-mu ceiling P * (max_i λ_i - fmin)         vs  P(1-fmin)
  (C) pair-aware λ spread on off-diagonal mass only
  (D) mixed F_hi on near pairs — soundness (must be ≤ true min f)

Writes stdout only; see pmax_notes.md for verdicts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
Q2 = HERE.parent.parent / "q2"
sys.path.insert(0, str(Q2))

from beta3_kernel import FMIN_MP, assemble_mid  # noqa: E402

FMIN = float(FMIN_MP)


def slsqp_phi(A, c, return_mu=False):
    n = A.shape[0]

    def fun(m):
        den = float(c @ m)
        if den <= 0:
            return 1e9
        return float(m @ A @ m) / den

    cons = {"type": "eq", "fun": lambda z: np.sum(z) - 1.0}
    bounds = [(0.0, 1.0)] * n
    best = 1e9
    best_mu = None
    rng = np.random.default_rng(3)
    starts = [np.ones(n) / n]
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        starts.append(e)
        best = min(best, fun(e))
    for _ in range(12):
        v = rng.random(n)
        starts.append(v / v.sum())
    for z0 in starts:
        res = minimize(
            fun,
            z0,
            bounds=bounds,
            constraints=cons,
            method="SLSQP",
            options={"maxiter": 500, "ftol": 1e-14},
        )
        if res.success:
            val = float(res.fun)
            if val < best:
                best = val
                best_mu = res.x / res.x.sum()
    if return_mu:
        return best, best_mu
    return best


def exact_q(F, c, mu, s):
    mu = np.clip(mu, 0.0, None)
    if mu.sum() <= 0:
        return 1e9
    mu = mu / mu.sum()
    sc = s * c * mu
    den = float(sc.sum())
    if den <= 0:
        return 1e9
    lam = F @ mu
    return float(sc @ lam) / den


def phi_of_mu(F, c, mu):
    mu = mu / mu.sum()
    lam = F @ mu
    sc = c * mu
    return float(sc @ lam) / float(sc.sum())


def min_q_over_s(F, c, mu, q, n_starts=16):
    n = len(c)
    lo, hi = 1.0 / q, q

    def unpack(x):
        s = lo + (hi - lo) / (1.0 + np.exp(-np.clip(x, -20, 20)))
        return s

    def fun(x):
        return exact_q(F, c, mu, unpack(x))

    rng = np.random.default_rng(11)
    starts = [np.zeros(n), np.full(n, 2.0), np.full(n, -2.0)]
    for _ in range(n_starts):
        starts.append(rng.normal(0.0, 0.5, size=n))
    best = 1e9
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 3000})
        best = min(best, float(res.fun))
    return best


def lam_stats(F, mu):
    lam = F @ (mu / mu.sum())
    return float(lam.max()), float(lam.min()), float(lam.max() - lam.min())


def adversarial_two_value_drop(lam, q):
    """Sharp TV drop for values lam_i with s in {1/q, q}."""
    lo, hi = 1.0 / q, q
    P = (q - 1.0) / (q + 1.0)
    # Optimal: low s on high lam, high s on low lam
    lam_sorted = np.sort(lam)
    # Greedy two-group: split at median
    n = len(lam)
    best = 0.0
    for k in range(1, n):
        low = lam_sorted[:k]
        high = lam_sorted[k:]
        mean_lo = low.mean()
        mean_hi = high.mean()
        # weight fraction at s=hi on low-lam group, s=lo on high-lam group
        q_lo = exact_q_from_groups(mean_lo, mean_hi, lo, hi, k / n)
        q_hi = exact_q_from_groups(mean_hi, mean_lo, lo, hi, k / n)
        base = lam.mean()
        drop = base - min(q_lo, q_hi)
        best = max(best, drop)
    return min(best, P * (lam.max() - lam.min()) + 1e-12)


def exact_q_from_groups(m1, m2, slo, shi, frac):
  """Two-point measure: frac at value m1, 1-frac at m2; assign slo to larger."""
  w1, w2 = frac, 1.0 - frac
  # put shi on smaller m
  if m1 <= m2:
    num = shi * w1 * m1 + slo * w2 * m2
    den = shi * w1 + slo * w2
  else:
    num = slo * w1 * m1 + shi * w2 * m2
    den = slo * w1 + shi * w2
  return num / den


def test_lambda_replacements(R, n):
    blob = assemble_mid(R, n)
    F = np.array([[float(blob["F_lo"][i][j]) for j in range(n)] for i in range(n)])
    c = np.array([float(blob["rmid2"][i]) for i in range(n)])
    A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
    from mpmath import mpf

    q = float(mpf(blob["q_iv"].b))
    P = (q - 1.0) / (q + 1.0)

    phi, mu_star = slsqp_phi(A, c, return_mu=True)
    lam_max, lam_min, spread = lam_stats(F, mu_star)
    q_min = min_q_over_s(F, c, mu_star, q)

    # Proposed bounds at phi minimizer
    err_1mf = P * (1.0 - FMIN)
    err_spread = P * spread
    err_lmax = P * (lam_max - FMIN)

    # Counterexample hunt: find mu where actual drop > P*(lam_max - fmin)
    worst_gap = -1e9
    worst = None
    rng = np.random.default_rng(99)
    trial_mus = [mu_star]
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        trial_mus.append(e)
    for _ in range(80):
        v = rng.random(n)
        trial_mus.append(v / v.sum())

    for mu in trial_mus:
        mu = np.asarray(mu, float)
        ph = phi_of_mu(F, c, mu)
        qm = min_q_over_s(F, c, mu, q)
        lmax, lmin, dsp = lam_stats(F, mu)
        actual_drop = ph - qm
        bound_spread = P * dsp
        bound_lmax = P * (lmax - FMIN)
        bound_1mf = P * (1.0 - FMIN)
        for name, bnd in (
            ("spread", bound_spread),
            ("lmax-fmin", bound_lmax),
            ("1-fmin", bound_1mf),
        ):
            gap = actual_drop - bnd
            if gap > worst_gap:
                worst_gap = gap
                worst = {
                    "name": name,
                    "actual_drop": actual_drop,
                    "bound": bnd,
                    "gap": gap,
                    "lam_max": lmax,
                    "spread": dsp,
                    "phi": ph,
                    "q_min": qm,
                }

    return {
        "R": R,
        "n": n,
        "q": q,
        "P": P,
        "phi_min": phi,
        "q_min_at_phi_star": q_min,
        "lam_max_at_phi_star": lam_max,
        "spread_at_phi_star": spread,
        "err_1mf": err_1mf,
        "err_spread": err_spread,
        "err_lmax": err_lmax,
        "savings_spread": err_1mf - err_spread,
        "savings_lmax": err_1mf - err_lmax,
        "worst_counterexample": worst,
    }


def test_mixed_F(R, n, near_width=1):
    """F_hi on |i-j|<=near_width invalidates lower bound if any F_hi > F_lo true."""
    blob = assemble_mid(R, n)
    Flo = np.array([[float(blob["F_lo"][i][j]) for j in range(n)] for i in range(n)])
    Fhi = np.array([[float(blob["F_hi"][i][j]) for j in range(n)] for i in range(n)])
    violations = []
    for i in range(n):
        for j in range(n):
            if abs(i - j) <= near_width:
                used = Fhi[i, j]
            else:
                used = Flo[i, j]
            if used > Flo[i, j] + 1e-15:
                violations.append((i, j, Flo[i, j], used, Fhi[i, j]))
    return {
        "R": R,
        "n": n,
        "near_width": near_width,
        "n_violations_Fhi_gt_Flo": len(violations),
        "max_overshoot": max((v[3] - v[1] for v in violations), default=0.0),
        "sample": violations[:5],
    }


def test_pair_aware_lambda(F, c, mu, q):
    """Off-diagonal-only spread: λ_i = μ_i + Σ_{j≠i} F_ij μ_j if F_ii=1."""
    n = len(mu)
    mu = mu / mu.sum()
    lam_full = F @ mu
  # If diagonal F_ii=1, rewrite spread excluding diagonal floor
    lam_off = lam_full - mu  # subtract 1*mu_i from diagonal
    spread_off = float(lam_full.max() - lam_full.min())
    return spread_off


def main() -> None:
    results = {"lambda_tests": [], "mixed_F": []}
    for R, n in ((12, 22), (4, 18)):
        results["lambda_tests"].append(test_lambda_replacements(R, n))
        for w in (0, 1, 2, 3):
            results["mixed_F"].append(test_mixed_F(R, n, w))

    print(json.dumps(results, indent=2))
    for row in results["lambda_tests"]:
        w = row["worst_counterexample"]
        print(
            f"\nR={row['R']} n={row['n']}: "
            f"savings spread={row['savings_spread']:.6f} "
            f"lmax={row['savings_lmax']:.6f} "
            f"worst_ce gap={w['gap']:.6f} ({w['name']})"
        )


if __name__ == "__main__":
    main()
