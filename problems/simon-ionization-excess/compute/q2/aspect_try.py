#!/usr/bin/env python3
"""Residue: first-variation / aspect lift of the compact β_3 bound.

HPS I/D for a probability m on (0, ∞), s=3 Newton kernel
  g(r,u) = (r³+u³) / (2 max(r,u)),
  D = ∫ r² dm,  I = ∬ g dm dm,  Q = I/D.

The compact certificate (certs/beta3_compact.json) gives
  Q ≥ 0.901924 on D-aspect ≤ 4.
That is a global lower bound on β_3 iff every measure is at least
that large, in particular those with aspect > 4.

This file does not prove that. It records:

1. Equilibrium identity for a critical point among probabilities:
     V(r) = (Q/2) (r² + D) on supp(m),
   V(r) = � probabilities:
     V(r) = (Q/2) (r² + D) on supp(m),
   V(r) = ∫ g(r,u) m(du). Checked on the numerical power-law
   minimizer and on k-atomic critical points.

2. Geometric t0-chains (the pairs that saturate f = fmin).
   If any explicit chain has Q < compact γ, the lift is false.

3. Truncation: restrict a large-aspect trial to [1, 4] (after
   scaling inf supp = 1) and compare Q. A counterexample to
   “truncation never increases Q” is logged; it is not a bound.

Writes certs/aspect_try.json. Status: residue.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

T0 = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0) - (1.0 + math.sqrt(2.0)) ** (-1.0 / 3.0)
B3 = (2.0 / 3.0) * (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0) / (
    (1.0 + math.sqrt(2.0)) ** (2.0 / 3.0) - 1.0
)
FMIN = 1.0 / B3
COMPACT_GAMMA = 0.901924285641075  # R=4, n=18, certify_compact.py
COMPACT_INV = 1.0 / COMPACT_GAMMA


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


def atomic_ID(radii: np.ndarray, masses: np.ndarray) -> tuple[float, float, float]:
    """I, D, Q for a finitely atomic probability."""
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    D = float(np.dot(m, r**2))
    I = 0.0
    for i in range(len(r)):
        for j in range(len(r)):
            I += m[i] * m[j] * g_kernel(r[i], r[j])
    return I, D, I / D


def V_atomic(r: float, radii: np.ndarray, masses: np.ndarray) -> float:
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    acc = 0.0
    for u, mu in zip(radii, m):
        acc += mu * g_kernel(r, float(u))
    return acc


def power_law_nodes(alpha: float, n: float, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Quadrature of m(dr) ∝ r^α dr on [1, n] as k geometric atoms."""
    edges = np.geomspace(1.0, n, k + 1)
    radii = np.sqrt(edges[:-1] * edges[1:])
    # mass of each bin
    if abs(alpha + 1.0) < 1e-14:
        masses = np.log(edges[1:] / edges[:-1])
    else:
        masses = (edges[1:] ** (alpha + 1.0) - edges[:-1] ** (alpha + 1.0)) / (
            alpha + 1.0
        )
    return radii, masses


def t0_chain(k: int, ratio: float | None = None) -> tuple[float, float]:
    """Equal-mass (in m) geometric chain with ratio t0, aspect t0^{1-k}."""
    t = T0 if ratio is None else float(ratio)
    radii = np.array([t ** (-i) for i in range(k)], dtype=float)
    masses = np.ones(k)
    I, D, Q = atomic_ID(radii, masses)
    aspect = float(radii[-1] / radii[0])
    return Q, aspect


def t0_chain_z_equal(k: int) -> tuple[float, float]:
    """Equal D-mass (z-equal) geometric chain: m_i ∝ 1/r_i²."""
    radii = np.array([T0 ** (-i) for i in range(k)], dtype=float)
    masses = 1.0 / radii**2
    I, D, Q = atomic_ID(radii, masses)
    return Q, float(radii[-1] / radii[0])


def check_equilibrium(radii, masses, tag: str) -> dict:
    I, D, Q = atomic_ID(radii, masses)
    rhs = lambda r: 0.5 * Q * (r**2 + D)
    vals = []
    for r in radii:
        V = V_atomic(float(r), radii, masses)
        target = rhs(float(r))
        vals.append(
            {
                "r": float(r),
                "V": V,
                "rhs": target,
                "rel_err": abs(V - target) / max(abs(target), 1e-30),
            }
        )
    max_rel = max(v["rel_err"] for v in vals)
    return {
        "tag": tag,
        "Q": Q,
        "D": D,
        "I": I,
        "max_rel_err": max_rel,
        "holds_at_1e-3": bool(max_rel < 1e-3),
        "points": vals,
    }


def optimize_k_atomic(k: int) -> dict:
    """Min Q over k positive radii (log-param) and masses."""

    def unpack(x):
        logs = x[:k]
        raw = x[k:]
        radii = np.exp(logs - logs.min())  # inf supp = 1
        masses = np.exp(raw)
        masses = masses / masses.sum()
        return radii, masses

    def fun(x):
        r, m = unpack(x)
        return atomic_ID(r, m)[2]

    best = 1.0
    best_x = None
    rng = np.random.default_rng(2 + k)
    starts = []
    # geometric t0
    logs = np.array([-i * math.log(T0) for i in range(k)])
    starts.append(np.concatenate([logs, np.zeros(k)]))
    # fill [1, 3.5]
    starts.append(
        np.concatenate([np.linspace(0.0, math.log(3.5), k), np.zeros(k)])
    )
    for _ in range(8):
        starts.append(rng.normal(0.0, 0.8, size=2 * k))
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 4000})
        if res.fun < best:
            best = float(res.fun)
            best_x = res.x
    r, m = unpack(best_x)
    eq = check_equilibrium(r, m, f"{k}-atomic-opt")
    return {
        "k": k,
        "Q": best,
        "aspect": float(r.max() / r.min()),
        "radii": r.tolist(),
        "masses": m.tolist(),
        "equilibrium_max_rel_err": eq["max_rel_err"],
        "inv": 1.0 / best,
    }


def truncate_to_aspect(radii, masses, R: float = 4.0) -> dict:
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    r = r / r.min()
    Q_full = atomic_ID(r, m)[2]
    mask = r <= R + 1e-15
    if mask.sum() == 0 or mask.sum() == len(r):
        return {
            "Q_full": Q_full,
            "Q_trunc": Q_full,
            "aspect_full": float(r.max()),
            "truncated": False,
            "Q_increased": False,
        }
    rt, mt = r[mask], m[mask]
    Q_tr = atomic_ID(rt, mt)[2]
    return {
        "Q_full": Q_full,
        "Q_trunc": Q_tr,
        "aspect_full": float(r.max()),
        "truncated": True,
        "Q_increased": bool(Q_tr > Q_full + 1e-12),
        "Q_decreased": bool(Q_tr < Q_full - 1e-12),
    }


def scan_power_truncation() -> list[dict]:
    rows = []
    for n in (4.0, 6.0, 8.0, 12.0, 20.0, 40.0, 80.0):
        r, m = power_law_nodes(-2.0, n, 48)
        row = truncate_to_aspect(r, m, 4.0)
        row["n"] = n
        row["alpha"] = -2.0
        rows.append(row)
    return rows


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    chains = []
    below_compact = []
    for k in range(1, 25):
        Q, aspect = t0_chain(k)
        Qz, aspect_z = t0_chain_z_equal(k)
        rec = {
            "k": k,
            "equal_m_Q": Q,
            "equal_m_aspect": aspect,
            "equal_z_Q": Qz,
            "equal_z_aspect": aspect_z,
            "equal_m_below_compact": bool(Q < COMPACT_GAMMA),
            "equal_z_below_compact": bool(Qz < COMPACT_GAMMA),
            "equal_m_inv": 1.0 / Q,
            "equal_z_inv": 1.0 / Qz,
        }
        chains.append(rec)
        if Q < COMPACT_GAMMA or Qz < COMPACT_GAMMA:
            below_compact.append(rec)

    katoms = [optimize_k_atomic(k) for k in range(2, 7)]

    # Power-law quadrature as many atoms: equilibrium is continuous, so
    # the discrete V≈rhs test is only a consistency check.
    r_pl, m_pl = power_law_nodes(-2.0, 3.50, 64)
    eq_pl = check_equilibrium(r_pl, m_pl, "power-α=-2-n=3.5-64atoms")
    Q_pl = atomic_ID(r_pl, m_pl)[2]

    trunc_power = scan_power_truncation()
    # A long t0-chain truncated to aspect 4
    r_ch = np.array([T0 ** (-i) for i in range(16)], dtype=float)
    m_ch = np.ones(16)
    trunc_chain = truncate_to_aspect(r_ch, m_ch, 4.0)

    # Random large-aspect trials: look for Q < compact γ (would kill the lift)
    rng = np.random.default_rng(7)
    random_hits = []
    random_min = 1.0
    for _ in range(200):
        k = int(rng.integers(3, 12))
        logs = np.sort(rng.uniform(0.0, math.log(80.0), size=k))
        logs[0] = 0.0
        masses = rng.random(k)
        Q = atomic_ID(np.exp(logs), masses)[2]
        random_min = min(random_min, Q)
        if Q < COMPACT_GAMMA:
            random_hits.append({"k": k, "Q": Q, "aspect": float(np.exp(logs[-1]))})

    cert = {
        "status": "residue",
        "is_new_bound": False,
        "beats_1.1185_in_HPS_theorem": False,
        "reason": (
            "No lift of the aspect-≤4 compact γ to every radial "
            "probability. Geometric t0-chains stay above compact γ "
            "in this scan but that is a search, not a lower bound. "
            "The withdrawn h(D_L,D_R) lift remains withdrawn."
        ),
        "fmin": FMIN,
        "b3": B3,
        "t0": T0,
        "compact_gamma_R4": COMPACT_GAMMA,
        "compact_inv_R4": COMPACT_INV,
        "power_law_n35_Q": Q_pl,
        "power_law_n35_inv": 1.0 / Q_pl,
        "equilibrium_power_law": eq_pl,
        "t0_chains": chains,
        "t0_chain_min_equal_m_Q": min(c["equal_m_Q"] for c in chains),
        "t0_chain_min_equal_z_Q": min(c["equal_z_Q"] for c in chains),
        "any_chain_below_compact": bool(below_compact),
        "below_compact": below_compact,
        "k_atomic_opt": katoms,
        "truncation_power_alpha_m2": trunc_power,
        "truncation_t0_chain16": trunc_chain,
        "truncation_can_increase_Q": bool(
            trunc_chain.get("Q_increased")
            or any(r.get("Q_increased") for r in trunc_power)
        ),
        "random_atomic_min_Q": random_min,
        "random_below_compact": random_hits,
        "note_on_equilibrium": (
            "For a probability-constrained critical point, "
            "V(r)=(Q/2)(r²+D) on the support. A one-point measure "
            "satisfies it with Q=1. A discrete k-atomic local min "
            "is only approximately critical (Nelder–Mead). "
            "The identity is not used as a bound."
        ),
    }
    out = CERTS / "aspect_try.json"
    out.write_text(json.dumps(cert, indent=2) + "\n")
    print("wrote", out)
    print(f"fmin={FMIN:.6f}  compactγ={COMPACT_GAMMA:.6f}  powerQ={Q_pl:.6f}")
    print(
        f"t0-chain min Q (equal m)={cert['t0_chain_min_equal_m_Q']:.6f}  "
        f"(equal z)={cert['t0_chain_min_equal_z_Q']:.6f}"
    )
    print(f"any chain below compact: {cert['any_chain_below_compact']}")
    print(f"k-atomic opt: " + ", ".join(f"{r['k']}:{r['Q']:.5f}" for r in katoms))
    print(f"truncation can increase Q: {cert['truncation_can_increase_Q']}")
    print(f"random atomic min Q: {random_min:.6f}")
    print("status: residue")


if __name__ == "__main__":
    main()
