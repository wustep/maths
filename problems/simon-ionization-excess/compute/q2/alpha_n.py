#!/usr/bin/env python3
"""Numerical search for alpha_{N,s} at N=3,4,5 and several s.

alpha_{N,s} is the Nam–HPS classical pair ratio

    inf  [ sum_{i<j} (|x_i|^s + |x_j|^s) / |x_i-x_j| ]
         / [ (N-1) sum_k |x_k|^{s-1} ].

A certified lower bound A with A*(N-1) > Z, plus a handle on the
weighted kinetic remainder, would exclude that (N,Z). This script
does not certify a lower bound: a search min is an upper bound on
the infimum. It is used to see whether the geometry even has room
for N=4 at Z=2 (need alpha_4 > 2/3 if the kinetic term is dropped).

Structured configurations plus multi-start L-BFGS-B. A second path
(random pairwise distances via scipy, different seed) is in
alpha_n_check.py.

Replay: python3 alpha_n.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

S_LIST = (1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
N_LIST = (3, 4, 5)


def alpha_of(pts: np.ndarray, s: float) -> float:
    """pts shape (N, 3). Returns +inf if a pair coincides."""
    N = pts.shape[0]
    r = np.linalg.norm(pts, axis=1)
    if np.any(r < 1e-14) and s - 1 < 0:
        return float("inf")
    den = (N - 1) * np.sum(r ** (s - 1))
    if den <= 0 or not np.isfinite(den):
        return float("inf")
    num = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            d = float(np.linalg.norm(pts[i] - pts[j]))
            if d < 1e-14:
                return float("inf")
            num += (r[i] ** s + r[j] ** s) / d
    return float(num / den)


def flatten(pts):
    return pts.ravel()


def unflatten(v, N):
    return np.asarray(v, dtype=float).reshape(N, 3)


def structured(N: int) -> list[np.ndarray]:
    rng = np.random.default_rng(0)
    out: list[np.ndarray] = []
    # Simplex / tetrahedron / 4 of simplex, centred.
    if N == 3:
        eq = np.array(
            [[1.0, 0.0, 0.0], [-0.5, math.sqrt(3) / 2, 0.0], [-0.5, -math.sqrt(3) / 2, 0.0]]
        )
        out.append(eq)
        out.append(eq + np.array([2.0, 0.0, 0.0]))  # off-centre
        out.append(np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]))
        out.append(np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))
        out.append(np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [4.0, 0.0, 0.0]]))
    if N == 4:
        tet = np.array(
            [
                [1.0, 1.0, 1.0],
                [1.0, -1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, -1.0, 1.0],
            ],
            dtype=float,
        )
        out.append(tet)
        out.append(tet + np.array([3.0, 0.0, 0.0]))
        out.append(
            np.array(
                [
                    [1.0, 0.0, 0.0],
                    [-1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, -1.0, 0.0],
                ]
            )
        )
        out.append(
            np.array(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [-0.5, math.sqrt(3) / 2, 0.0],
                    [-0.5, -math.sqrt(3) / 2, 0.0],
                ]
            )
        )
        out.append(np.array([[k, 0.0, 0.0] for k in range(4)], dtype=float))
    if N == 5:
        tet = np.array(
            [
                [1.0, 1.0, 1.0],
                [1.0, -1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, -1.0, 1.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=float,
        )
        out.append(tet)
        out.append(np.array([[k, 0.2 * k, 0.0] for k in range(5)], dtype=float))
    # Random Gaussian clouds, several scales.
    for scale in (0.3, 1.0, 3.0, 10.0):
        for _ in range(8):
            out.append(scale * rng.normal(size=(N, 3)))
    # One close to origin, others on a sphere.
    for _ in range(6):
        pts = rng.normal(size=(N, 3))
        pts[0] *= 0.02
        out.append(pts)
    return out


def local_min(pts0: np.ndarray, s: float) -> tuple[float, np.ndarray]:
    N = pts0.shape[0]

    def f(v):
        a = alpha_of(unflatten(v, N), s)
        if not np.isfinite(a):
            return 1e9
        return a

    res = minimize(f, flatten(pts0), method="L-BFGS-B", options={"maxiter": 400})
    pts = unflatten(res.x, N)
    return alpha_of(pts, s), pts


def search(N: int, s: float) -> dict:
    best_a = float("inf")
    best_pts = None
    starts = structured(N)
    for pts0 in starts:
        a, pts = local_min(pts0, s)
        if a < best_a:
            best_a, best_pts = a, pts
    return {
        "N": N,
        "s": s,
        "search_min": best_a,
        "search_min_is_upper_on_inf": True,
        "need_for_Nc_lt_4_at_Z2_if_kinetic_dropped": (2.0 / 3.0) if N == 4 else None,
        "need_for_Nc_lt_3_at_Z2_if_kinetic_dropped": (1.0) if N == 3 else None,
        "pts": best_pts.tolist() if best_pts is not None else None,
    }


def report() -> dict:
    rows = []
    print(f"{'N':>3} {'s':>6} {'search min':>14} {'(N-1)*min':>12} {'vs Z=2':>10}")
    for N in N_LIST:
        for s in S_LIST:
            r = search(N, s)
            rows.append(r)
            prod = r["search_min"] * (N - 1)
            print(
                f"{N:3d} {s:6.2f} {r['search_min']:14.8f} {prod:12.6f} "
                f"{prod - 2.0:+10.6f}"
            )
    # Closed-form checks.
    # s=1: triangle => alpha >= 1/2, and two opposite rays give 1/2.
    a2 = alpha_of(np.array([[1.0, 0.0, 0.0], [-2.0, 0.0, 0.0]]), 1.0)
    if abs(a2 - 0.5) > 1e-12:
        raise RuntimeError(f"two-point s=1 should be 1/2, got {a2}")
    # Equilateral centred, s=2: alpha = sqrt(3)/3.
    eq = np.array(
        [[1.0, 0.0, 0.0], [-0.5, math.sqrt(3) / 2, 0.0], [-0.5, -math.sqrt(3) / 2, 0.0]]
    )
    a_eq = alpha_of(eq, 2.0)
    if abs(a_eq - math.sqrt(3) / 3) > 1e-9:
        raise RuntimeError(f"equilateral s=2 expected {math.sqrt(3)/3}, got {a_eq}")
    return {
        "not_a_certificate": True,
        "note": (
            "search_min is an upper bound on alpha_{N,s}. It cannot prove "
            "non-binding. A value below the threshold needed for Z=2 shows "
            "the Nam–HPS pair geometry does not, by itself, exclude that N."
        ),
        "rows": rows,
        "thresholds": {
            "N4_Z2_kinetic_dropped": 2.0 / 3.0,
            "N3_Z2_kinetic_dropped": 1.0,
            "Nam_sqrt5_over_4": math.sqrt(5) / 4,
        },
    }


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    blob = report()
    # Strip pts from the written cert to keep it small; keep one witness.
    slim_rows = []
    for r in blob["rows"]:
        slim_rows.append({k: v for k, v in r.items() if k != "pts"})
    out = {
        "not_a_certificate": True,
        "is_new_bound": False,
        "note": blob["note"],
        "thresholds": blob["thresholds"],
        "rows": slim_rows,
    }
    path = CERTS / "alpha_n.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
