#!/usr/bin/env python3
"""Two-atom mass-critical and fully-critical Q(R).

Mass-opt on fixed (1,R): one mass parameter. Fully critical also
sets dQ/dR=0 (radius-stationary outer atom).

Used to see whether Q>R/(R+1) is loose at the R that would lift
the aspect-≤4 class. Not a global lower bound.

Writes certs/two_atom_crit.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


def two_atom_Q(R: float, p: float) -> float:
    """p = mass at r=1, 1-p at r=R."""
    p = float(np.clip(p, 1e-12, 1 - 1e-12))
    D = p + (1.0 - p) * R * R
    I = (
        p * p * g_kernel(1.0, 1.0)
        + 2.0 * p * (1.0 - p) * g_kernel(1.0, R)
        + (1.0 - p) * (1.0 - p) * g_kernel(R, R)
    )
    return I / D


def mass_crit(R: float) -> dict:
    res = minimize_scalar(
        lambda p: two_atom_Q(R, p),
        bounds=(1e-8, 1 - 1e-8),
        method="bounded",
        options={"xatol": 1e-12},
    )
    p = float(res.x)
    Q = two_atom_Q(R, p)
    cut = R / (R + 1.0)
    return {
        "R": R,
        "p": p,
        "Q": Q,
        "cut": cut,
        "Q_minus_cut": Q - cut,
        "inv": 1.0 / Q,
    }


def V(r, R, p) -> float:
    return p * g_kernel(r, 1.0) + (1.0 - p) * g_kernel(r, R)


def stationarity_err(R: float, p: float) -> float:
    Q = two_atom_Q(R, p)
    D = p + (1.0 - p) * R * R
    e1 = abs(V(1.0, R, p) - 0.5 * Q * (1.0 + D))
    eR = abs(V(R, R, p) - 0.5 * Q * (R * R + D))
    return max(e1, eR) / max(Q, 1e-30)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    Rs = [2.0, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 9.0, 10.0, 12.0, 16.0, 20.0]
    mass_rows = []
    for R in Rs:
        rec = mass_crit(R)
        rec["stat_err"] = stationarity_err(R, rec["p"])
        mass_rows.append(rec)
        print(
            f"mass-crit R={R:5.1f}  Q={rec['Q']:.6f}  cut={rec['cut']:.6f}  "
            f"gap={rec['Q_minus_cut']:.4f}  inv={rec['inv']:.5f}"
        )

    # fully critical: min over R of mass-crit Q(R)
    def q_of_R(R):
        return mass_crit(float(R))["Q"]

    resR = minimize_scalar(q_of_R, bounds=(1.2, 20.0), method="bounded")
    Rstar = float(resR.x)
    full = mass_crit(Rstar)
    full["stat_err"] = stationarity_err(Rstar, full["p"])

    # also scan dQ/dR numerically at mass-crit p
    dQ = []
    for R in Rs:
        h = 1e-5
        d = (q_of_R(R + h) - q_of_R(R - h)) / (2 * h)
        dQ.append({"R": R, "dQ_dR_at_masscrit": d})

    out = {
        "not_a_lower_bound": True,
        "mass_crit_rows": mass_rows,
        "fully_crit_approx": full,
        "dQ_dR": dQ,
        "note": (
            "Two-atomic only. Mass-critical Q(R) sits well above R/(R+1), "
            "but k-atomic mass-opt on a filled window can be lower."
        ),
    }
    path = CERTS / "two_atom_crit.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("fully-crit R*", Rstar, "Q", full["Q"])
    print("wrote", path)


if __name__ == "__main__":
    main()
