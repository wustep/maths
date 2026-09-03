#!/usr/bin/env python3
"""Mass-optimised atomics with used aspect ≥ R have Q > R/(R+1).

Numerical check, not a substitute for the moment algebra.
Writes certs/mass_opt.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from select_row import best_row

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


def atomic_Q(radii, masses) -> float:
    r = np.asarray(radii, dtype=float)
    m = np.clip(np.asarray(masses, dtype=float), 0.0, None)
    s = m.sum()
    if s <= 0:
        return 1e9
    m = m / s
    R, U = np.meshgrid(r, r, indexing="ij")
    G = (R**3 + U**3) / (2.0 * np.maximum(R, U))
    I = float(m @ G @ m)
    D = float(m @ (r**2))
    return I / D


def mass_opt(radii, n_starts: int = 8) -> dict:
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
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 2000})
        val = float(res.fun)
        if val < best:
            best = val
            m = np.exp(res.x - np.max(res.x))
            best_m = (m / m.sum()).tolist()
    used = [i for i, mi in enumerate(best_m) if mi > 1e-8]
    aspect = float(r[used[-1]] / r[used[0]]) if used else 1.0
    return {"Q": best, "aspect_used": aspect, "n_used": len(used), "masses": best_m}


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    row = best_row()
    R0 = float(row["R"])
    cut = R0 / (R0 + 1.0)
    configs = [np.array([1.0, R0]), np.array([1.0, 1.5 * R0])]
    for k, R in ((4, R0), (8, R0), (8, 1.6 * R0), (6, 1.3 * R0)):
        configs.append(np.geomspace(1.0, R, k))
    rng = np.random.default_rng(11)
    for _ in range(12):
        k = int(rng.integers(4, 8))
        mid = np.sort(rng.uniform(1.05, R0 - 0.4, size=k - 2))
        configs.append(np.concatenate(([1.0], mid, [R0])))

    rows = []
    below = []
    for r in configs:
        rec = mass_opt(r)
        rec["k"] = int(len(r))
        rec["aspect_nominal"] = float(r[-1] / r[0])
        rec["below_cut"] = bool(
            rec["Q"] <= cut + 1e-12 and rec["aspect_used"] >= R0 - 1e-12
        )
        rows.append(rec)
        if rec["below_cut"]:
            below.append(rec)

    blob = {
        "R": R0,
        "cut": cut,
        "n_configs": len(rows),
        "min_mass_opt_Q": min(r["Q"] for r in rows),
        "any_below_cut_with_aspect_ge_R": bool(below),
        "rows": [
            {
                "k": r["k"],
                "aspect_nominal": r["aspect_nominal"],
                "aspect_used": r["aspect_used"],
                "Q": r["Q"],
                "n_used": r["n_used"],
            }
            for r in rows
        ],
    }
    out = CERTS / "mass_opt.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(
        f"min mass-opt Q={blob['min_mass_opt_Q']:.6f}  cut={cut:.6f}  "
        f"below={blob['any_below_cut_with_aspect_ge_R']}"
    )
    print("wrote", out)
    if below:
        raise SystemExit("mass_opt_check.py FAIL")
    print("mass_opt_check.py PASS")


if __name__ == "__main__":
    main()
