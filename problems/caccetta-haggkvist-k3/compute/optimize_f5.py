#!/usr/bin/env python3
"""Random-PSD + LP search on the F5 lift.

Same Farkas form as sdp_f5.py, but Q4/Q5 are sampled (Cholesky) and the
linear multipliers are fitted by HiGHS, which is the loop that actually
produced a strict F4 certificate.
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hkn_replay import AR, BR, A_VECS, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs
from optimize_bound import Q_from_as

OUT = Path(__file__).resolve().parent / "certs"
AR_A = np.array(AR, dtype=float)
BR_A = np.array(BR, dtype=float)
MS4 = [np.array(M, dtype=float) for M in ac_slices()]


def load():
    blob = pickle.loads((OUT / "flags5.pkl").read_bytes())
    return blob["n_types"], np.array(blob["pi"]), np.array(blob["AC5"])


def try_lp(c, Q4, Q5, pi, AC):
    T = pi.shape[0]
    sos4 = np.array([float(np.sum(Q4 * Mk)) for Mk in MS4])  # 32
    sos5 = np.einsum("pq,pqt->t", Q5, AC)  # T
    pulled_sos = pi @ sos4 + sos5  # T
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    # F_t = pulled_sos_t + π_t · (b(BR-cAR) + cT it + cV iv + d fk)
    # vars: t, b[14], cT, cV, d
    nvar = 1 + 14 + 3
    A_ub = np.zeros((T, nvar))
    b_ub = np.zeros(T)
    reg = BR_A - c * AR_A  # 14 × 32
    # π @ reg.T  is T × 14
    pi_reg = pi @ reg.T
    pi_it = pi @ it
    pi_iv = pi @ iv
    pi_fk = pi @ fk
    for t in range(T):
        A_ub[t, 0] = -1.0
        A_ub[t, 1:15] = pi_reg[t]
        A_ub[t, 15] = pi_it[t]
        A_ub[t, 16] = pi_iv[t]
        A_ub[t, 17] = pi_fk[t]
        b_ub[t] = -pulled_sos[t]
    bounds = [(None, None)] + [(None, None)] * 14 + [(0, None)] * 3
    cobj = np.zeros(nvar)
    cobj[0] = 1.0
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        return None
    return {
        "t": float(res.x[0]),
        "b": res.x[1:15].tolist(),
        "cT": float(res.x[15]),
        "cV": float(res.x[16]),
        "d": float(res.x[17]),
        "ok": float(res.x[0]) < -1e-4,
    }


def rand_psd(rng, dim, scale=30.0, rnk=None):
    if rnk is None:
        rnk = int(rng.integers(1, dim + 1))
    A = rng.normal(scale=scale, size=(dim, rnk))
    return A @ A.T


def main():
    n_types, pi, AC = load()
    print(f"T={n_types}", flush=True)
    Q4_0 = Q_from_as(A_VECS)
    rng = np.random.default_rng(0)
    best_by_c = {}
    grid = [0.3465, 0.3464, 0.3460, 0.3450, 0.3440, 0.3430, 0.3420, 0.3400, 0.3388]
    for c in grid:
        best = None
        # include F4-only (Q5=0) and some random Q5
        cands = [(Q4_0, np.zeros((14, 14)))]
        for _ in range(25):
            Q4 = 0.5 * Q4_0 + 0.5 * rand_psd(rng, 8)
            Q5 = rand_psd(rng, 14, scale=10.0)
            cands.append((Q4, Q5))
            cands.append((Q4_0, Q5))
            cands.append((rand_psd(rng, 8), np.zeros((14, 14))))
        for Q4, Q5 in cands:
            got = try_lp(c, Q4, Q5, pi, AC)
            if got is None:
                continue
            if best is None or got["t"] < best["t"]:
                best = {**got, "Q4": Q4.tolist(), "Q5": Q5.tolist(), "c": c}
        rec = None if best is None else {k: best[k] for k in ("c", "t", "ok", "cT", "cV", "d")}
        print(f"c={c:.4f}  {rec}", flush=True)
        if best is not None:
            best_by_c[str(c)] = rec
            if best["ok"]:
                (OUT / "f5_best.json").write_text(json.dumps(best, indent=2))
    path = OUT / "optimize_f5.json"
    path.write_text(json.dumps(best_by_c, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
