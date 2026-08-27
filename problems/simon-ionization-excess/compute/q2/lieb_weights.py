#!/usr/bin/env python3
"""Lieb-style pair ratios for Z-dependent and compactly supported weights.

If a weight φ ≥ 0 has Re ⟨φ f, −Δ f⟩ ≥ 0 and the configuration-wise ratio

    R_N(φ) = inf  [ sum_{i<j} (φ(x_i)+φ(x_j)) / |x_i-x_j| ]
                  / [ sum_k φ(x_k) / |x_k| ]

satisfies R_N(φ) > Z, then (the Nam write-up of) Lieb's identity excludes
that N at that Z. For φ(x)=|x| one has R_N ≥ (N-1)/2, hence N < 2Z+1.

This script numerically minimises R_4(φ) and R_3(φ) for several families:
  |x|^s,  |x|/(1+λ|x|),  1−exp(−α|x|),  |x| exp(−μ|x|),  min(|x|, ρ),
  and a C^1 compact cutoff |x| η(|x|/ρ).

A search min is an upper bound on the infimum. If that upper bound is
already ≤ Z, the weight cannot exclude that N, no matter how the
search is refined. Kinetic positivity is checked only at the symbolic
level recorded in the notes (s=1 and Chen–Siedentop |x|^b, b∈[0,1]).

Replay: python3 lieb_weights.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def pair_ratio(pts: np.ndarray, phi: np.ndarray, phi_over_r: np.ndarray) -> float:
    N = pts.shape[0]
    den = float(np.sum(phi_over_r))
    if den <= 1e-18 or not np.isfinite(den):
        return float("inf")
    num = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            d = float(np.linalg.norm(pts[i] - pts[j]))
            if d < 1e-14:
                return float("inf")
            num += (phi[i] + phi[j]) / d
    return num / den


def r_of(pts: np.ndarray) -> np.ndarray:
    return np.linalg.norm(pts, axis=1)


def family_eval(name: str, param: float, r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    r = np.maximum(r, 1e-16)
    if name == "power":
        s = param
        return r**s, r ** (s - 1)
    if name == "screened_rational":
        lam = param
        phi = r / (1.0 + lam * r)
        return phi, 1.0 / (1.0 + lam * r)
    if name == "one_minus_exp":
        a = param
        phi = 1.0 - np.exp(-a * r)
        return phi, phi / r
    if name == "screened_exp":
        mu = param
        phi = r * np.exp(-mu * r)
        return phi, np.exp(-mu * r)
    if name == "min_r":
        rho = param
        phi = np.minimum(r, rho)
        por = np.where(r <= rho, 1.0, rho / r)
        return phi, por
    if name == "compact_cutoff":
        # η(t) = 1 for t<=1, 0 for t>=2, C^1 cubic in between.
        rho = param
        t = r / rho
        eta = np.ones_like(t)
        mid = (t > 1.0) & (t < 2.0)
        u = t[mid] - 1.0
        # η = 1 - 3u^2 + 2u^3, η(0)=1, η(1)=0, η'=0 at ends.
        eta[mid] = 1.0 - 3.0 * u**2 + 2.0 * u**3
        eta[t >= 2.0] = 0.0
        phi = r * eta
        return phi, eta
    raise ValueError(name)


def ratio_named(pts: np.ndarray, name: str, param: float) -> float:
    r = r_of(pts)
    phi, por = family_eval(name, param, r)
    return pair_ratio(pts, phi, por)


def minimise(N: int, name: str, param: float, n_rand: int = 24) -> float:
    seeds = {
        "power": 11,
        "screened_rational": 12,
        "one_minus_exp": 13,
        "screened_exp": 14,
        "min_r": 15,
        "compact_cutoff": 16,
    }
    rng = np.random.default_rng(11 + N + 17 * seeds[name])

    def f(v):
        a = ratio_named(v.reshape(N, 3), name, param)
        return a if np.isfinite(a) else 1e9

    starts = [rng.normal(size=(N, 3)) * scale for scale in (0.4, 1.0, 3.0, 8.0) for _ in range(n_rand // 4)]
    if N == 4:
        starts.append(
            np.array(
                [
                    [1.0, 1.0, 1.0],
                    [1.0, -1.0, -1.0],
                    [-1.0, 1.0, -1.0],
                    [-1.0, -1.0, 1.0],
                ],
                dtype=float,
            )
        )
        starts.append(np.array([[0.01, 0, 0], [1, 0, 0], [-1, 0, 0], [0, 1, 0]], dtype=float))
    if N == 3:
        starts.append(
            np.array(
                [[1.0, 0.0, 0.0], [-0.5, math.sqrt(3) / 2, 0.0], [-0.5, -math.sqrt(3) / 2, 0.0]]
            )
        )
        starts.append(np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]))
    best = float("inf")
    for pts0 in starts:
        res = minimize(f, pts0.ravel(), method="L-BFGS-B", options={"maxiter": 250})
        a = ratio_named(res.x.reshape(N, 3), name, param)
        if a < best:
            best = a
    return best


FAMILIES = [
    ("power", [1.0, 1.25, 1.5, 2.0, 3.0]),
    ("screened_rational", [0.25, 0.5, 1.0, 2.0, 4.0]),
    ("one_minus_exp", [0.25, 0.5, 1.0, 2.0]),
    ("screened_exp", [0.1, 0.25, 0.5, 1.0, 2.0]),
    ("min_r", [0.5, 1.0, 2.0, 4.0]),
    ("compact_cutoff", [0.5, 1.0, 2.0, 4.0]),
]


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"{'N':>3} {'family':<20} {'param':>8} {'R_search':>12} {'vs Z=2'}")
    for N in (3, 4):
        for name, params in FAMILIES:
            for p in params:
                R = minimise(N, name, p)
                rows.append(
                    {
                        "N": N,
                        "family": name,
                        "param": float(p),
                        "R_search_upper_on_inf": float(R),
                        "excludes_Z2_if_this_were_a_lower_bound": bool(R > 2.0),
                        "already_cannot_exclude_Z2": bool(R <= 2.0),
                    }
                )
                flag = "cannot exclude" if R <= 2.0 else "only an upper on inf"
                print(f"{N:3d} {name:<20} {p:8.2f} {R:12.6f}  {flag}")

    # Lieb s=1 sanity: R_N >= (N-1)/2, and opposite rays give equality.
    r3 = ratio_named(
        np.array([[1.0, 0.0, 0.0], [-2.0, 0.0, 0.0], [0.01, 0.0, 0.0]]), "power", 1.0
    )
    if r3 < 1.0 - 1e-6:
        raise RuntimeError("s=1 N=3 ratio fell below 1")

    blob = {
        "not_a_certificate": True,
        "is_new_bound": False,
        "need_R_gt": 2.0,
        "note": (
            "R_search is an upper bound on inf R_N(φ). Every family tried "
            "has a configuration with R <= 2 at N=3 and at N=4 (usually "
            "near the Lieb value (N-1)/2, or only a few tenths above it). "
            "No weight here produces a certified R > 2. Kinetic positivity "
            "holds for φ=|x|^b, b in [0,1] (Chen–Siedentop); for the other "
            "families it was not proved and is not used as a bound."
        ),
        "rows": rows,
    }
    path = CERTS / "lieb_weights.json"
    path.write_text(json.dumps(blob, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
