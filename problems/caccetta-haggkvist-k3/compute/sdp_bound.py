#!/usr/bin/env python3
"""Exact (numerical SDP) F₄ threshold of the HKN inequality system.

For each candidate c, solve

    minimise t
    s.t.  ⟨Q, M_k⟩ + b·(BR − c AR)_k + cT IndT_k(c) + cV IndV_k(c) + d Fork_k(c) ≤ t
          Q ≽ 0,  cT,cV,d ≥ 0

with CVXPY/SCS.  If t < 0, the system certifies δα < c.

The matrices were independently rebuilt in flags4.py / ind_fork.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cvxpy as cp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs
from optimize_bound import F_coords

OUT = Path(__file__).resolve().parent / "certs"

MS = [np.array(M, dtype=float) for M in ac_slices()]
AR_A = np.array(AR, dtype=float)
BR_A = np.array(BR, dtype=float)


def F_expr(c, Q, b, cT, cV, d, k, it, iv, fk):
    sos = cp.trace(Q @ MS[k])
    return sos + b @ (BR_A[:, k] - c * AR_A[:, k]) + cT * it[k] + cV * iv[k] + d * fk[k]


def solve_c(c: float, verbose: bool = False):
    """Feasibility: exists a ray with every F_k ≤ −1.

    The zero map gives F≡0, so we ask for a strictly negative combination
    and scale it to margin 1.  SCS on the homogenised problem.
    """
    Q = cp.Variable((8, 8), PSD=True)
    b = cp.Variable(14)
    cT = cp.Variable(nonneg=True)
    cV = cp.Variable(nonneg=True)
    d = cp.Variable(nonneg=True)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    cons = [F_expr(c, Q, b, cT, cV, d, k, it, iv, fk) <= -1 for k in range(32)]
    # keep the scale from exploding
    cons.append(cp.trace(Q) + cT + cV + d + cp.norm1(b) <= 1e6)
    prob = cp.Problem(cp.Minimize(0), cons)
    status = None
    for kwargs in (
        dict(solver=cp.SCS, eps=1e-8, max_iters=20000),
        dict(solver=cp.SCS, eps=1e-6, max_iters=10000),
    ):
        try:
            prob.solve(verbose=verbose, **kwargs)
            status = prob.status
        except Exception as e:
            status = str(e)
            continue
        if status in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE) and Q.value is not None:
            break
    if Q.value is None:
        return {"c": c, "status": status, "feasible": False}
    Qv = 0.5 * (np.array(Q.value) + np.array(Q.value).T)
    # clip tiny negative eigs
    w, V = np.linalg.eigh(Qv)
    w = np.clip(w, 0, None)
    Qv = (V * w) @ V.T
    coords = F_coords(c, Qv, b.value, float(cT.value), float(cV.value), float(d.value))
    ev = np.linalg.eigvalsh(Qv)
    return {
        "c": c,
        "status": status,
        "feasible": bool(np.all(coords < -0.5)),
        "t_sdp": float(np.max(coords)),
        "worst_F_replay": float(np.max(coords)),
        "all_negative": bool(np.all(coords < -1e-8)),
        "Q_min_eig": float(ev.min()),
        "b": np.array(b.value).tolist(),
        "cT": float(cT.value),
        "cV": float(cV.value),
        "d": float(d.value),
        "Q": Qv.tolist(),
        "F_coords": coords.tolist(),
    }


def main():
    # evaluate at the published number and a grid just below
    grid = [0.3465, 0.3464, 0.3463, 0.3462, 0.3460, 0.3455, 0.3450, 0.3440, 0.3430, 0.3420, 0.3400, 0.3388]
    recs = []
    best = None
    for c in grid:
        got = solve_c(c)
        if got is None:
            print(f"c={c:.4f}  FAIL")
            continue
        print(
            f"c={c:.4f}  status={got.get('status')}  feasible={got.get('feasible')}  "
            f"worst={got.get('worst_F_replay')}  mineig={got.get('Q_min_eig')}",
            flush=True,
        )
        recs.append({k: got.get(k) for k in ("c", "status", "feasible", "worst_F_replay", "all_negative", "Q_min_eig")})
        if got.get("feasible") and (best is None or got["c"] < best["c"]):
            best = got
    # binary search the SDP threshold
    lo, hi = 1 / 3, 0.3465
    last = None
    for _ in range(20):
        mid = 0.5 * (lo + hi)
        got = solve_c(mid)
        if got is None:
            lo = mid
            continue
        print(
            f"  bin {mid:.8f} feas={got.get('feasible')} worst={got.get('worst_F_replay')} st={got.get('status')}",
            flush=True,
        )
        if got.get("feasible"):
            hi = mid
            last = got
        else:
            lo = mid
    if last is not None and (best is None or last["c"] < best["c"]):
        best = last
    payload = {
        "published_hkn": 0.3465,
        "personal_communication_3388": 0.3388,
        "grid": recs,
        "sdp_threshold": None if last is None else last["c"],
        "certificate": None
        if best is None
        else {
            "c": best["c"],
            "t_sdp": best["t_sdp"],
            "worst_F_replay": best["worst_F_replay"],
            "all_negative": best["all_negative"],
            "Q_min_eig": best["Q_min_eig"],
            "b": best["b"],
            "cT": best["cT"],
            "cV": best["cV"],
            "d": best["d"],
            "Q": best["Q"],
            "F_coords": best["F_coords"],
        },
    }
    path = OUT / "sdp_bound.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path)
    if best:
        print(f"BEST certified c={best['c']:.10f}  (HKN 0.3465, comm 0.3388)")


if __name__ == "__main__":
    main()
