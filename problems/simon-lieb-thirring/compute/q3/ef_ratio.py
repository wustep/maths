#!/usr/bin/env python3
"""Empirical T / ∫ρ³ for orthonormal systems (Eden–Foias dual).

Eden–Foias / DLL prove T ≥ ∫ρ³, i.e. κ≥1, converting to L/Lcl ≤ π/√3 ≈ 1.8138.
To beat CCR 1.44655 via that conversion one needs κ>1.35. The one-bound-state
optimizer has T/∫ρ³ ≈ 2.467, so there is room — but a proof of κ>1.35 is
exactly a better kinetic inequality, which is the original problem.

This file only *measures* κ on Hermite blocks and finite-well eigenfunctions.
It is not a bound.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from constants import CCR_L, KCL_1, ratio_from_k_over_kcl

HERE = Path(__file__).resolve().parent


def hermite_block(n_fun: int, n_grid: int = 321, L: float = 8.0) -> dict:
    """First n_fun harmonic-oscillator functions, orthonormal in L2."""
    xs = np.linspace(-L, L, n_grid)
    h = xs[1] - xs[0]
    # Physicist Hermite via recurrence, then * e^{-x^2/2} / norm.
    psi = np.zeros((n_fun, n_grid))
    psi[0] = np.exp(-0.5 * xs**2)
    if n_fun > 1:
        psi[1] = 2.0 * xs * psi[0]
    for k in range(1, n_fun - 1):
        psi[k + 1] = 2.0 * xs * psi[k] - 2.0 * k * psi[k - 1]
    # Normalise in l2 * sqrt(h)
    for k in range(n_fun):
        nrm = math.sqrt(h * float(np.dot(psi[k], psi[k])))
        psi[k] /= nrm
    rho = np.sum(psi**2, axis=0)
    # Kinetic = Σ ∫ |ψ'|^2. Central difference.
    T = 0.0
    for k in range(n_fun):
        dpsi = np.gradient(psi[k], h)
        T += h * float(np.dot(dpsi, dpsi))
    I3 = h * float(np.sum(rho**3))
    kappa = T / I3 if I3 > 0 else 0.0
    return {
        "family": "hermite",
        "n_fun": n_fun,
        "T": T,
        "I3": I3,
        "kappa": kappa,
        "L_over_Lcl_if_K_eq_kappa": ratio_from_k_over_kcl(kappa / KCL_1) if kappa > 0 else None,
    }


def well_block(n_fun: int, n_grid: int = 241, L: float = 6.0, depth: float = 8.0) -> dict:
    xs = np.linspace(-L, L, n_grid)
    h = xs[1] - xs[0]
    v = np.where(np.abs(xs) <= 2.0, depth, 0.0)
    invh2 = 1.0 / (h * h)
    H = np.zeros((n_grid, n_grid))
    for i in range(n_grid):
        H[i, i] = 2.0 * invh2 - v[i]
        if i:
            H[i, i - 1] = -invh2
        if i + 1 < n_grid:
            H[i, i + 1] = -invh2
    evals, vecs = np.linalg.eigh(H)
    # Orthonormal in the discrete l2 inner product * sqrt(h): eigh is l2-orthonormal,
    # so scale by 1/sqrt(h) for L2.
    psi = vecs[:, :n_fun].T / math.sqrt(h)
    rho = np.sum(psi**2, axis=0)
    T = 0.0
    for k in range(n_fun):
        dpsi = np.gradient(psi[k], h)
        T += h * float(np.dot(dpsi, dpsi))
    I3 = h * float(np.sum(rho**3))
    kappa = T / I3 if I3 > 0 else 0.0
    return {
        "family": "finite-well-eigs",
        "n_fun": n_fun,
        "n_bound_available": int(np.sum(evals < 0)),
        "T": T,
        "I3": I3,
        "kappa": kappa,
    }


def main() -> int:
    print("=== q3 Eden–Foias empirical kappa ===", flush=True)
    recs = [hermite_block(n) for n in (1, 2, 3, 5, 8)]
    recs += [well_block(n) for n in (1, 2, 3, 4)]
    kappas = [r["kappa"] for r in recs]
    out = {
        "EF_kappa_proved": 1.0,
        "kappa_needed_to_beat_CCR": 1.35,
        "one_bound_state_kappa": 4.0 / (27.0 * (4.0 * math.sqrt(3.0) / (9.0 * math.pi)) ** 2),
        "min_empirical": min(kappas),
        "records": recs,
        "beats_CCR": False,
        "note": (
            "Empirical kappa sits near 2.5–4, above the 1.35 threshold, but this is "
            "not a proof that kappa≥1.35 for every orthonormal system. The EF CS "
            "step still only gives kappa≥1."
        ),
    }
    dest = HERE / "certs" / "ef_ratio.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for r in recs:
        print(f"  {r['family']} n={r['n_fun']}: kappa={r['kappa']:.4f}")
    print(f"min empirical kappa={out['min_empirical']:.4f}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
