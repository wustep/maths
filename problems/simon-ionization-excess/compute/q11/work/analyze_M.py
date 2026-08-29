#!/usr/bin/env python3
"""Inertia of M = A − γ Sym(c,1)/2 at predicted q11 targets.

Not a certificate. Used to decide whether a PD+NN shortcut or
PD-pruning can beat brute-force 2^n faces.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
Q7 = HERE.parent
Q2 = Q7.parent / "q2"
sys.path.insert(0, str(Q2))

from beta3_kernel import assemble_mid  # noqa: E402

CERTS = Q7 / "certs"
WORK = HERE


def build_M(R: float, n: int, gamma: float):
    blob = assemble_mid(R, n)
    A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
    c = np.array([float(blob["rmid2"][i]) for i in range(n)])
    M = A - 0.5 * gamma * (c[:, None] + c[None, :])
    return A, c, M


def inertia(evals):
    pos = int(np.sum(evals > 1e-14))
    neg = int(np.sum(evals < -1e-14))
    zer = int(evals.size - pos - neg)
    return pos, zer, neg


def principal_pd_rate(M, k: int, samples: int, rng) -> dict:
    n = M.shape[0]
    if k == n:
        evals = np.linalg.eigvalsh(M)
        return {
            "k": k,
            "mode": "exact",
            "n_checked": 1,
            "n_pd": int(evals.min() > 1e-14),
            "min_eval": float(evals.min()),
        }
    from math import comb

    total = comb(n, k)
    if total <= samples:
        idx = range(n)
        # all k-subsets via combinations
        from itertools import combinations

        n_pd = 0
        min_ev = 1e300
        n_checked = 0
        for S in combinations(idx, k):
            ev = np.linalg.eigvalsh(M[np.ix_(S, S)])
            min_ev = min(min_ev, float(ev.min()))
            n_pd += int(ev.min() > 1e-14)
            n_checked += 1
        return {
            "k": k,
            "mode": "exact",
            "n_checked": n_checked,
            "n_pd": n_pd,
            "pd_rate": n_pd / n_checked,
            "min_eval": min_ev,
        }
    n_pd = 0
    min_ev = 1e300
    for _ in range(samples):
        S = rng.choice(n, size=k, replace=False)
        ev = np.linalg.eigvalsh(M[np.ix_(S, S)])
        min_ev = min(min_ev, float(ev.min()))
        n_pd += int(ev.min() > 1e-14)
    return {
        "k": k,
        "mode": "sample",
        "n_checked": samples,
        "n_pd": n_pd,
        "pd_rate": n_pd / samples,
        "min_eval": min_ev,
    }


def psd_plus_nn(M) -> dict:
    """Sufficient copositivity: exists N>=0 elementwise with M-N PSD.

    Try lifting negative off-diagonals to 0.
    """
    N = np.maximum(-M, 0.0)
    np.fill_diagonal(N, 0.0)
    P = M + N
    ev = np.linalg.eigvalsh(P)
    return {
        "zeroed_neg_offdiag_min_eval": float(ev.min()),
        "psd_plus_nn_by_zeroing": bool(ev.min() > 1e-12),
    }


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    configs = [
        (10.0, 35, 0.9115),
        (10.0, 35, 0.9116),
        (10.0, 36, 0.9117),
    ]
    rows = []
    for R, n, gamma in configs:
        A, c, M = build_M(R, n, gamma)
        ev = np.linalg.eigvalsh(M)
        pos, zer, neg = inertia(ev)
        rates = [
            principal_pd_rate(M, k, 400, rng)
            for k in (n, n - 1, n - 2, n - 3, max(2, n // 2), 4, 3, 2)
        ]
        rec = {
            "R": R,
            "n": n,
            "gamma": gamma,
            "eig_min": float(ev[0]),
            "eig_max": float(ev[-1]),
            "n_neg": neg,
            "n_zero": zer,
            "n_pos": pos,
            "diag_min": float(np.min(np.diag(M))),
            "offdiag_min": float(np.min(M - np.diag(np.diag(M)))),
            "psd_nn": psd_plus_nn(M),
            "principal": rates,
        }
        rows.append(rec)
        print(
            f"R={R} n={n} γ={gamma}  λmin={ev[0]:.4e}  "
            f"inertia=({pos},{zer},{neg})  diagmin={rec['diag_min']:.4e}  "
            f"psd+nn={rec['psd_nn']['psd_plus_nn_by_zeroing']}"
        )
        for r in rates:
            print(
                f"  k={r['k']:2d} {r['mode']:6s} pd={r.get('pd_rate', r['n_pd'])} "
                f"min_ev={r['min_eval']:.3e}"
            )

    out = WORK / "analyze_M.json"
    out.write_text(json.dumps({"rows": rows}, indent=2) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
