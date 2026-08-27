#!/usr/bin/env python3
"""Try a DNN (PSD + nonnegative) certificate for the discrete Rayleigh."""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize

from probe_discrete import assemble, min_rayleigh


def dnn_split(M, iters=400):
    """Alternating projection: A ⪰ 0, B ≥ 0, A+B ≈ M."""
    n = M.shape[0]
    A = np.array(M, dtype=float, copy=True)
    B = np.zeros_like(A)
    for _ in range(iters):
        # project A+B onto A+B=M
        S = A + B
        corr = 0.5 * (M - S)
        A = A + corr
        B = B + corr
        # A ⪰ 0
        A = 0.5 * (A + A.T)
        w, V = np.linalg.eigh(A)
        w = np.clip(w, 0.0, None)
        A = (V * w) @ V.T
        # B ≥ 0
        B = np.maximum(B, 0.0)
    resid = np.max(np.abs(A + B - M))
    # verify A PSD and B nonnegative
    wmin = float(np.linalg.eigvalsh(0.5 * (A + A.T))[0])
    bmin = float(np.min(B))
    return A, B, resid, wmin, bmin


def main():
    fmin = 0.8941074569749823
    for n, R in ((12, 4.0), (16, 4.0), (20, 4.0), (16, 6.0), (20, 8.0), (24, 8.0)):
        edges, F, G, cmax, amin2, rmid2 = assemble(n, R)
        A = 0.5 * (F * rmid2[:, None] + (F * rmid2[None, :]))
        # wait A_ij should be F_ij * (rmid2_i + rmid2_j)/2
        A = F * 0.5 * (rmid2[:, None] + rmid2[None, :])
        c = rmid2
        phi = min_rayleigh(A, c, n_starts=12)
        q = R ** (1.0 / n)
        theta = q - 1.0
        err = (theta / (1.0 - theta)) * (1.0 - fmin)
        print(f"\nn={n} R={R}  φ_mid={phi:.6f}  θ={theta:.4f}  err={err:.5f}  "
              f"γ≤{phi-err:.6f}")
        for gtry in (0.896, 0.898, 0.900, 0.902):
            # need φ ≥ gtry + err, i.e. Rayleigh ≥ gtarget
            gtarget = gtry + err
            M = A - (gtarget / 2.0) * (np.outer(c, np.ones(n)) + np.outer(np.ones(n), c))
            # test min on simplex of m^T M m via SLSQP
            def psi(m):
                m = np.clip(m, 0, None)
                s = m.sum()
                m = m / s
                return float(m @ M @ m)

            best = min(psi(np.ones(n)), min(psi(np.eye(n)[i]) for i in range(n)))
            rng = np.random.default_rng(1)
            for _ in range(8):
                opt = minimize(psi, rng.random(n), method="Nelder-Mead",
                               options={"maxiter": 400})
                best = min(best, psi(opt.x))
            AA, BB, resid, wmin, bmin = dnn_split(M)
            print(f"  γ={gtry} target_φ={gtarget:.5f}  min mᵀMm≈{best:.5e}  "
                  f"DNN resid={resid:.2e} wmin={wmin:.2e} bmin={bmin:.2e}  "
                  f"ok={resid<1e-8 and wmin>=-1e-10 and bmin>=-1e-12 and best>=-1e-8}")


if __name__ == "__main__":
    main()
