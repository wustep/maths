#!/usr/bin/env python3
"""Cheap lifts of the published Hou–Zhao R=8 floating mix.

Same kernels / mixing weights, but:
  * longer boundary L (L=4 is feasible inside L'>4 by padding w=1)
  * dyadic refinement of the histogram (m=32 -> 64, 96, 128)
  * then a short joint re-optimization of mixing weights

A floating improvement is only a candidate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_kernels import dump, evaluate  # noqa: E402
from vector_smoothing import softmax, solve_boundary_qp, symmetric_kernel_from_logits  # noqa: E402

ROOT = Path(__file__).resolve().parent


def load_r8():
    ns: dict = {}
    exec((ROOT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    ker, lam = ns["stored_candidates"]()[8]
    return np.asarray(ker, dtype=float), np.asarray(lam, dtype=float)


def refine_m(kernels: np.ndarray, factor: int) -> np.ndarray:
    """Split each bin into `factor` equal-mass sub-bins."""
    return np.repeat(kernels / factor, factor, axis=1)


def pad_or_solve(ker, lam, L):
    return evaluate(ker, lam, L, tag=f"hz-r8-m{ker.shape[1]}-L{L}-fixedp")


def reopt_mix(ker, L, lam0):
    R = ker.shape[0]

    def obj(z):
        mix = softmax(np.concatenate([z, [0.0]]))
        _, _, _, _, g = solve_boundary_qp(ker, mix, L)
        return g

    z0 = np.log(np.clip(lam0[:-1] / max(lam0[-1], 1e-12), 1e-12, None))
    res = minimize(obj, z0, method="Nelder-Mead", options={"maxiter": 200, "xatol": 1e-5, "fatol": 1e-10})
    mix = softmax(np.concatenate([res.x, [0.0]]))
    return evaluate(ker, mix, L, tag=f"hz-r8-m{ker.shape[1]}-L{L}-reoptmix")


def add_kernel(ker, lam, L, nmodes=8):
    def unpack(x):
        theta = x[:nmodes]
        logits = x[nmodes:]
        new_p = symmetric_kernel_from_logits(theta, ker.shape[1])
        mix = softmax(logits)
        return np.vstack([ker, new_p]), mix

    def obj(x):
        k, m = unpack(x)
        _, _, _, _, g = solve_boundary_qp(k, m, L)
        return g

    x0 = np.zeros(nmodes + ker.shape[0] + 1)
    # start with tiny weight on the new kernel
    x0[nmodes:-1] = np.log(np.clip(lam, 1e-12, None))
    x0[-1] = np.log(1e-3)
    res = minimize(obj, x0, method="Powell", options={"maxiter": 35, "xtol": 2e-4, "ftol": 1e-9})
    k, m = unpack(res.x)
    return evaluate(k, m, L, tag=f"hz-r9-m{ker.shape[1]}-L{L}")


def main():
    ker, lam = load_r8()
    print("baseline m=32 L=4", flush=True)
    pad_or_solve(ker, lam, 4)

    for L in (5, 6, 8, 10):
        print(f"L-lift {L}", flush=True)
        pad_or_solve(ker, lam, L)
        reopt_mix(ker, L, lam)

    for fac in (2, 3, 4):
        ker_f = refine_m(ker, fac)
        print(f"m-lift {ker_f.shape[1]}", flush=True)
        pad_or_solve(ker_f, lam, 4)
        pad_or_solve(ker_f, lam, 6)
        reopt_mix(ker_f, 6, lam)

    print("add 9th kernel at m=32 L=4", flush=True)
    add_kernel(ker, lam, 4)
    print("add 9th kernel at m=32 L=6", flush=True)
    add_kernel(ker, lam, 6)

    # joint: refined m=64, L=6, plus a 9th kernel
    ker64 = refine_m(ker, 2)
    print("add 9th kernel at m=64 L=6", flush=True)
    add_kernel(ker64, lam, 6, nmodes=8)

    print("done", flush=True)


if __name__ == "__main__":
    main()
