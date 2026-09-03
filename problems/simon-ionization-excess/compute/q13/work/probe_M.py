#!/usr/bin/env python3
"""Probe M at n=36/37: spectrum, PD principal submatrices, copositive split."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q2))
from beta3_kernel import assemble_mid  # noqa: E402


def build_M(R: float, n: int, target: float):
    blob = assemble_mid(R, n)
    A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
    c = np.array([float(blob["rmid2"][i]) for i in range(n)])
    ones = np.ones(n)
    M = A - 0.5 * target * (np.outer(c, ones) + np.outer(ones, c))
    M = 0.5 * (M + M.T)
    return A, c, M


def pd_count(M, k, max_check=20000, seed=0):
    n = M.shape[0]
    rng = np.random.default_rng(seed)
    from itertools import combinations

    total = 1
    for i in range(k):
        total = total * (n - i) // (i + 1)
    checked = 0
    n_pd = 0
    n_psd = 0
    worst = 1e9
    if total <= max_check:
        it = combinations(range(n), k)
        exhaustive = True
    else:
        it = (tuple(sorted(rng.choice(n, size=k, replace=False))) for _ in range(max_check))
        exhaustive = False
    for idx in it:
        S = M[np.ix_(idx, idx)]
        ev = np.linalg.eigvalsh(S)
        mn = float(ev[0])
        worst = min(worst, mn)
        checked += 1
        if mn >= 1e-12:
            n_pd += 1
        if mn >= -1e-12:
            n_psd += 1
    return {
        "k": k,
        "total": total,
        "checked": checked,
        "exhaustive": exhaustive,
        "n_pd": n_pd,
        "n_psd": n_psd,
        "worst_lmin": worst,
    }


def try_nn_plus_psd(M):
    """Zero negative off-diagonals into N>=0, rest P. Also spectral clip."""
    n = M.shape[0]
    N = np.maximum(M, 0.0)
    np.fill_diagonal(N, 0.0)
    P = M - N
    evP = np.linalg.eigvalsh(P)
    # spectral: P = sum_{λ>0} λ vv^T, N = M-P; check N>=0
    ev, V = np.linalg.eigh(M)
    P2 = (V * np.maximum(ev, 0.0)) @ V.T
    N2 = M - P2
    return {
        "nn_offdiag_P_lmin": float(evP[0]),
        "spectral_clip_N_min": float(N2.min()),
        "spectral_clip_N_offdiag_min": float(
            min(N2[i, j] for i in range(n) for j in range(n) if i != j)
        ),
        "n_neg_eigs": int((ev < -1e-12).sum()),
        "eigs_head": [float(x) for x in ev[:6]],
        "eigs_tail": [float(x) for x in ev[-3:]],
    }


def main():
    for n, target in ((36, 0.9117), (36, 0.9118), (37, 0.9119)):
        A, c, M = build_M(10.0, n, target)
        ev = np.linalg.eigvalsh(M)
        print(f"\n=== n={n} target={target} ===")
        print("c range", float(c.min()), float(c.max()))
        print("M diag range", float(np.diag(M).min()), float(np.diag(M).max()))
        print("n_neg_eigs", int((ev < -1e-12).sum()), "lmin", float(ev[0]), "lmax", float(ev[-1]))
        print("split", try_nn_plus_psd(M))
        # eigenvector of negative eigs
        w, V = np.linalg.eigh(M)
        for t in range(int((w < -1e-12).sum())):
            v = V[:, t]
            top = np.argsort(-np.abs(v))[:8]
            print(
                f"  neg{t} λ={w[t]:.4e} top coords",
                [(int(i), float(v[i])) for i in top],
                "l1",
                float(np.abs(v).sum()),
            )
        for k in range(n, max(n - 8, 1), -1):
            rec = pd_count(M, k)
            print("  PD", rec)


if __name__ == "__main__":
    main()
