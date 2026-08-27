#!/usr/bin/env python3
"""Numerical check: mass-optimised atomics with aspect ≥ 12 have Q > 12/13.

Not a substitute for the algebra in aspect_identities.py. A mass-opt
Q ≤ 12/13 on a support that uses both endpoints would kill the lift.

Writes certs/mass_opt.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

CUT = 12.0 / 13.0


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


def atomic_Q(radii, masses) -> float:
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = np.clip(m, 0.0, None)
    s = m.sum()
    if s <= 0:
        return 1e9
    m = m / s
    R, U = np.meshgrid(r, r, indexing="ij")
    G = (R**3 + U**3) / (2.0 * np.maximum(R, U))
    I = float(m @ G @ m)
    D = float(m @ (r**2))
    return I / D


def mass_opt(radii, n_starts: int = 10) -> dict:
    r = np.asarray(radii, dtype=float)
    k = len(r)

    def fun(x):
        m = np.exp(x - np.max(x))
        return atomic_Q(r, m)

    best = 1.0
    best_m = None
    starts = [np.zeros(k), np.log(1.0 / (r**2))]
    rng = np.random.default_rng(3 + k + int(r[-1] * 10))
    for _ in range(n_starts):
        starts.append(rng.normal(0.0, 0.7, size=k))
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 2500})
        val = float(res.fun)
        if val < best:
            best = val
            m = np.exp(res.x - np.max(res.x))
            best_m = (m / m.sum()).tolist()
    used = [i for i, mi in enumerate(best_m) if mi > 1e-8]
    aspect = float(r[used[-1]] / r[used[0]]) if used else 1.0
    return {
        "Q": best,
        "aspect_used": aspect,
        "n_used": len(used),
        "masses": best_m,
        "below_cut": bool(best <= CUT + 1e-12 and aspect >= 12.0 - 1e-12),
    }


def V_atomic(r, radii, masses) -> float:
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    return float(sum(mi * g_kernel(float(r), float(u)) for u, mi in zip(radii, m)))


def stationarity(radii, masses) -> float:
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    Q = atomic_Q(r, m)
    D = float(m @ (r**2))
    errs = []
    for ri, mi in zip(r, m):
        if mi < 1e-8:
            continue
        V = V_atomic(ri, r, m)
        rhs = 0.5 * Q * (ri**2 + D)
        errs.append(abs(V - rhs) / max(abs(rhs), 1e-30))
    return max(errs) if errs else 0.0


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = []
    below = []
    configs = []
    # two-atom
    configs.append(np.array([1.0, 12.0]))
    configs.append(np.array([1.0, 20.0]))
    # geometric
    for k, R in ((4, 12.0), (8, 12.0), (8, 20.0), (12, 12.0), (6, 16.0)):
        configs.append(np.geomspace(1.0, R, k))
    # random interiors, endpoints pinned
    rng = np.random.default_rng(11)
    for _ in range(16):
        k = int(rng.integers(4, 9))
        mid = np.sort(rng.uniform(1.05, 11.5, size=k - 2))
        configs.append(np.concatenate(([1.0], mid, [12.0])))

    for r in configs:
        rec = mass_opt(r)
        rec["radii"] = [float(x) for x in r]
        rec["k"] = int(len(r))
        rec["aspect_nominal"] = float(r[-1] / r[0])
        rec["stat_rel"] = stationarity(r, rec["masses"])
        rows.append(rec)
        if rec["below_cut"]:
            below.append(rec)

    # also: un-optimised power-law quadrature at n=12 should stay above cut
    edges = np.geomspace(1.0, 12.0, 33)
    rq = np.sqrt(edges[:-1] * edges[1:])
    mq = 1.0 / rq**2  # α=-2 bins ~ equal log-mass after jacobian-ish
    Q_quad = atomic_Q(rq, mq)

    blob = {
        "cut": CUT,
        "n_configs": len(rows),
        "min_mass_opt_Q": min(r["Q"] for r in rows),
        "any_below_cut_with_aspect_ge_12": bool(below),
        "below": below,
        "quad_n12_Q": Q_quad,
        "quad_n12_above_cut": bool(Q_quad > CUT),
        "max_stat_rel": max(r["stat_rel"] for r in rows),
        "rows": [
            {
                "k": r["k"],
                "aspect_nominal": r["aspect_nominal"],
                "aspect_used": r["aspect_used"],
                "Q": r["Q"],
                "stat_rel": r["stat_rel"],
                "n_used": r["n_used"],
            }
            for r in rows
        ],
    }
    out = CERTS / "mass_opt.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(
        f"min mass-opt Q={blob['min_mass_opt_Q']:.6f}  cut={CUT:.6f}  "
        f"below={blob['any_below_cut_with_aspect_ge_12']}"
    )
    print(f"quad n=12 Q={Q_quad:.6f}  max stat rel={blob['max_stat_rel']:.2e}")
    print("wrote", out)
    if below or Q_quad <= CUT:
        raise SystemExit("mass_opt_check.py FAIL (would kill the lift)")
    print("mass_opt_check.py PASS")


if __name__ == "__main__":
    main()
