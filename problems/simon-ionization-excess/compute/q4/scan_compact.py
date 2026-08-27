#!/usr/bin/env python3
"""Cheap scan: predicted compact γ(R,n) from SLSQP φ minus P_max error.

Not a certificate. Used to pick face-enumeration targets. A predicted
γ is only a dent after faces say M is copositive at that φ_target.

Writes certs/scan_compact.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from mpmath import iv, mpf
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q2))

from beta3_kernel import FMIN_MP, assemble_mid  # noqa: E402

CERTS = HERE / "certs"
FMIN = float(FMIN_MP)
Q3_LEAD = 1.1118
R4_INV = 1.108741


def slsqp_phi(A, c):
    n = A.shape[0]

    def fun(m):
        den = float(c @ m)
        if den <= 0:
            return 1e9
        return float(m @ A @ m) / den

    cons = {"type": "eq", "fun": lambda z: np.sum(z) - 1.0}
    bounds = [(0.0, 1.0)] * n
    best = 1e9
    rng = np.random.default_rng(1)
    starts = [np.ones(n) / n]
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        starts.append(e)
        best = min(best, fun(e))
    for _ in range(12):
        v = rng.random(n)
        starts.append(v / v.sum())
    for z0 in starts:
        res = minimize(
            fun,
            z0,
            bounds=bounds,
            constraints=cons,
            method="SLSQP",
            options={"maxiter": 400, "ftol": 1e-14},
        )
        if res.success:
            best = min(best, float(res.fun))
    return best


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    configs = [
        (4, 18),
        (8, 20),
        (9, 20),
        (9, 22),
        (10, 22),
        (10, 24),
        (10, 26),
        (12, 22),
        (12, 24),
        (12, 26),
        (12, 28),
        (14, 24),
        (16, 26),
    ]
    rows = []
    for R, n in configs:
        blob = assemble_mid(R, n)
        A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
        c = np.array([float(blob["rmid2"][i]) for i in range(n)])
        phi = slsqp_phi(A, c)
        q = blob["q_iv"]
        P = (q - 1) / (q + 1)
        err = P * (1 - blob["fmin_iv"])
        err_hi = float(mpf(err.b))
        P_hi = float(mpf(P.b))
        q_hi = float(mpf(q.b))
        # conservative target a hair under SLSQP
        target = float(np.floor((phi - 1e-4) * 1e4) / 1e4)
        gamma_pred = target - err_hi
        inv_pred = 1.0 / gamma_pred if gamma_pred > 0 else 1e9
        cut = R / (R + 1.0)
        split = min(gamma_pred, cut)
        split_inv = 1.0 / split
        rows.append(
            {
                "R": R,
                "n": n,
                "n_faces": (1 << n) - 1,
                "slsqp_phi": phi,
                "target_suggest": target,
                "q_hi": q_hi,
                "P_max_hi": P_hi,
                "err_P_hi": err_hi,
                "gamma_pred": gamma_pred,
                "inv_pred": inv_pred,
                "cut_R_over_R1": cut,
                "split_gamma": split,
                "split_inv": split_inv,
                "beats_1.1118_if_certified": bool(split_inv < Q3_LEAD),
                "beats_1.108741_if_certified": bool(split_inv < R4_INV),
                "cut_ge_gamma": bool(cut >= gamma_pred),
            }
        )
        print(
            f"R={R:2d} n={n:2d}  φ={phi:.6f}  tgt={target:.4f}  "
            f"err={err_hi:.5f}  γ={gamma_pred:.6f}  1/γ={inv_pred:.6f}  "
            f"cut={cut:.4f}  split={split_inv:.6f}  faces={((1<<n)-1):,}"
        )

    best = min(rows, key=lambda r: r["split_inv"])
    out = {
        "note": (
            "Predicted only. Face copositivity at target_suggest is required "
            "before quoting split_inv as a leading coefficient."
        ),
        "q3_leading": Q3_LEAD,
        "r4_class_only": R4_INV,
        "fmin": FMIN,
        "best_split": best,
        "rows": rows,
    }
    path = CERTS / "scan_compact.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("best split", best["R"], best["n"], best["split_inv"])
    print("wrote", path)


if __name__ == "__main__":
    main()
