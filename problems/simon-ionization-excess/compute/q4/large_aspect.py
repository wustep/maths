#!/usr/bin/env python3
"""Large-aspect probes: power-law Q(R) and forced-endpoint mass-opt.

If mass-stationary measures of aspect ≥ R0 have Q ≥ γ_4 ≈ 0.901924,
the aspect-≤4 number becomes unrestricted. The q3 cut Q>R/(R+1) is
0.8 at R=4, so it does not lift. This file only records numerical
floors. Not a lower bound.

Writes certs/large_aspect.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
GAMMA4 = 0.901924285641075
CUT4 = 4.0 / 5.0


def g_kernel(r, u):
    m = np.maximum(r, u)
    return (r**3 + u**3) / (2.0 * m)


def atomic_Q(radii, masses):
    r = np.asarray(radii, dtype=float)
    m = np.clip(np.asarray(masses, dtype=float), 0.0, None)
    s = m.sum()
    if s <= 0:
        return 1e9
    m = m / s
    R, U = np.meshgrid(r, r, indexing="ij")
    I = float(m @ g_kernel(R, U) @ m)
    D = float(m @ (r**2))
    return I / D


def power_law_Q(alpha: float, n: float, k: int = 96) -> float:
    edges = np.geomspace(1.0, n, k + 1)
    r = np.sqrt(edges[:-1] * edges[1:])
    # m(dr) ∝ r^α dr, log-bin width constant ⇒ mass ∝ r^{α+1} Δlog
    raw = r ** (alpha + 1.0)
    return atomic_Q(r, raw)


def mass_opt_forced(R: float, k: int = 8) -> dict:
    r = np.geomspace(1.0, R, k)

    def fun(x):
        # keep endpoints used: add a floor
        m = np.exp(x - np.max(x))
        m[0] = max(m[0], 1e-3)
        m[-1] = max(m[-1], 1e-3)
        return atomic_Q(r, m)

    best = 1.0
    best_m = None
    rng = np.random.default_rng(int(1000 * R + k))
    starts = [np.zeros(k), np.log(1.0 / (r**2))]
    for _ in range(8):
        starts.append(rng.normal(0.0, 0.6, size=k))
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 2500})
        val = float(res.fun)
        if val < best:
            best = val
            m = np.exp(res.x - np.max(res.x))
            m[0] = max(m[0], 1e-3)
            m[-1] = max(m[-1], 1e-3)
            best_m = (m / m.sum()).tolist()
    return {"R": R, "k": k, "Q": best, "masses": best_m}


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    alphas = [-2.2, -2.0, -1.8, -1.5]
    aspects = [3.5, 4.0, 6.0, 8.0, 12.0, 20.0]
    power_rows = []
    for a in alphas:
        for n in aspects:
            Q = power_law_Q(a, n)
            power_rows.append(
                {
                    "alpha": a,
                    "aspect": n,
                    "Q": Q,
                    "inv": 1.0 / Q,
                    "below_gamma4": bool(Q < GAMMA4),
                }
            )

    forced = []
    for R in (4.0, 6.0, 8.0, 12.0):
        rec = mass_opt_forced(R, k=8)
        rec["below_gamma4"] = bool(rec["Q"] < GAMMA4)
        rec["cut"] = R / (R + 1.0)
        forced.append(rec)
        print(
            f"forced R={R:.0f}  Q={rec['Q']:.6f}  cut={rec['cut']:.4f}  "
            f"below γ4={rec['below_gamma4']}"
        )

    best_power = min(power_rows, key=lambda r: r["Q"])
    out = {
        "not_a_lower_bound": True,
        "gamma4": GAMMA4,
        "cut4": CUT4,
        "best_power": best_power,
        "power_rows": power_rows,
        "forced_endpoint": [
            {k: v for k, v in r.items() if k != "masses"} for r in forced
        ],
        "any_power_below_gamma4": any(r["below_gamma4"] for r in power_rows),
        "note": (
            "Numerical only. A trial below γ4 with aspect>4 would kill an "
            "R=4 lift; none is expected near the known minimizer (aspect~3.5)."
        ),
    }
    path = CERTS / "large_aspect.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("best power", best_power)
    print("wrote", path)


if __name__ == "__main__":
    main()
