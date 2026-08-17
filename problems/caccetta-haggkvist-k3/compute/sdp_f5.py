#!/usr/bin/env python3
"""F₅ lift of the HKN certificate.

SOS is the 14×14 Cauchy–Schwarz block on λ-flags of order 3 (product lives
on 5 vertices).  Out-regularity, induction and the fork bound are the F₄
forms pulled back along the 4-vertex marginal.

Feasibility at c: exists Q ≽ 0 (14×14), b ∈ ℝ¹⁴, cT,cV,d ≥ 0 with
    ⟨Q, AC5_t⟩ + Σ_i π_{t i} ( b·(BR−c AR)_i + cT IndT_i + cV IndV_i + d Fork_i )
    ≤ −1    for every 5-vertex type t.
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import cvxpy as cp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs

OUT = Path(__file__).resolve().parent / "certs"
CACHE = OUT / "flags5.pkl"

AR_A = np.array(AR, dtype=float)
BR_A = np.array(BR, dtype=float)
MS4 = [np.array(M, dtype=float) for M in ac_slices()]


def load():
    blob = pickle.loads(CACHE.read_bytes())
    pi = np.array(blob["pi"], dtype=float)  # T × 32
    AC = np.array(blob["AC5"], dtype=float)  # 14 × 14 × T
    return blob["n_types"], pi, AC


def solve_c(c: float, n_types, pi, AC):
    T = n_types
    Q5 = cp.Variable((14, 14), PSD=True)
    Q4 = cp.Variable((8, 8), PSD=True)
    b = cp.Variable(14)
    cT = cp.Variable(nonneg=True)
    cV = cp.Variable(nonneg=True)
    d = cp.Variable(nonneg=True)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    f4lin = (b @ (BR_A - c * AR_A)) + cT * it + cV * iv + d * fk  # 32
    sos4 = [cp.trace(Q4 @ Mk) for Mk in MS4]  # 32
    cons = []
    for t in range(T):
        sos5 = cp.trace(Q5 @ AC[:, :, t])
        pulled = 0
        for i in range(32):
            pulled += pi[t, i] * (sos4[i] + f4lin[i])
        cons.append(sos5 + pulled <= -1)
    cons.append(cp.trace(Q4) + cp.trace(Q5) + cT + cV + d + cp.norm1(b) <= 1e7)
    prob = cp.Problem(cp.Minimize(0), cons)
    status = None
    for kwargs in (
        dict(solver=cp.SCS, eps=1e-7, max_iters=30000),
        dict(solver=cp.SCS, eps=1e-5, max_iters=15000),
    ):
        try:
            prob.solve(**kwargs)
            status = prob.status
        except Exception as e:
            status = str(e)
            continue
        if Q4.value is not None:
            break
    if Q4.value is None:
        return {"c": c, "status": status, "feasible": False}

    def psd_clip(A):
        A = 0.5 * (A + A.T)
        w, V = np.linalg.eigh(A)
        return (V * np.clip(w, 0, None)) @ V.T

    Q4v = psd_clip(np.array(Q4.value))
    Q5v = psd_clip(np.array(Q5.value))
    bv = np.array(b.value)
    cTv, cVv, dv = float(cT.value), float(cV.value), float(d.value)
    f4v = (bv @ (BR_A - c * AR_A)) + cTv * it + cVv * iv + dv * fk
    sos4v = np.array([float(np.sum(Q4v * Mk)) for Mk in MS4])
    coords = np.einsum("pq,pqt->t", Q5v, AC) + pi @ (sos4v + f4v)
    return {
        "c": c,
        "status": status,
        "feasible": bool(np.all(coords < -0.5)),
        "worst": float(np.max(coords)),
        "n_pos": int(np.sum(coords >= 0)),
        "Q4_min_eig": float(np.linalg.eigvalsh(Q4v).min()),
        "Q5_min_eig": float(np.linalg.eigvalsh(Q5v).min()),
        "cT": cTv,
        "cV": cVv,
        "d": dv,
        "b": bv.tolist(),
        "Q4": Q4v.tolist(),
        "Q5": Q5v.tolist(),
        "F": coords.tolist(),
    }


def main():
    n_types, pi, AC = load()
    print(f"loaded T={n_types} AC={AC.shape} π={pi.shape}", flush=True)
    recs = []
    best = None
    grid = [0.3465, 0.3460, 0.3450, 0.3440, 0.3430, 0.3420, 0.3400, 0.3388, 0.3370, 0.3360]
    for c in grid:
        got = solve_c(c, n_types, pi, AC)
        print(
            f"c={c:.4f} st={got.get('status')} feas={got.get('feasible')} "
            f"worst={got.get('worst')} npos={got.get('n_pos')}",
            flush=True,
        )
        recs.append({k: got.get(k) for k in ("c", "status", "feasible", "worst", "n_pos", "Q4_min_eig", "Q5_min_eig")})
        if got.get("feasible") and (best is None or got["c"] < best["c"]):
            best = got
    lo, hi = 1 / 3 + 1e-4, 0.3465
    last = best
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        got = solve_c(mid, n_types, pi, AC)
        print(
            f"  bin {mid:.6f} feas={got.get('feasible')} worst={got.get('worst')} st={got.get('status')}",
            flush=True,
        )
        if got.get("feasible"):
            hi = mid
            last = got
        else:
            lo = mid
    payload = {
        "published_hkn": 0.3465,
        "personal_communication_3388": 0.3388,
        "n_types": n_types,
        "grid": recs,
        "sdp_threshold": None if last is None else last["c"],
        "certificate": None
        if last is None
        else {
            k: last[k]
            for k in ("c", "status", "feasible", "worst", "Q4_min_eig", "Q5_min_eig", "cT", "cV", "d", "b", "Q4", "Q5", "F")
        },
    }
    path = OUT / "sdp_f5.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path)
    if last:
        print(f"BEST F5 c={last['c']:.8f} worst={last['worst']}")


if __name__ == "__main__":
    main()
