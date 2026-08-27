#!/usr/bin/env python3
"""Predicted compact γ(R,n) from SLSQP φ minus P_max error.

Not a certificate. Used to pick face-enumeration targets that can
beat printed 1.1021. A predicted γ is only a dent after faces say
M is copositive at that φ_target.

Printed leading uses the same ceil-to-next-10^{-4} as
tighten_leading.py: 1.102041 prints as 1.1021, so the leftover
n=33 target 0.9111 is not a printed dent.

Writes certs/scan_compact.json.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import mpf
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q2))

from beta3_kernel import FMIN_MP, assemble_mid  # noqa: E402

CERTS = HERE / "certs"
FMIN = float(FMIN_MP)
Q7_LEAD = 1.1021


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
    for _ in range(10):
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


def printed_lead(x: float) -> float:
    """Same ceil-to-next-grid as tighten_leading.ceil_dec(..., 4)."""
    return (math.floor(x * 10000.0 + 1e-12) + 1) / 10000.0


def row_from_phi(R, n, phi, err_hi, target, note=""):
    gamma_pred = target - err_hi
    inv_pred = 1.0 / gamma_pred if gamma_pred > 0 else 1e9
    cut = R / (R + 1.0)
    split = min(gamma_pred, cut)
    split_inv = 1.0 / split
    printed = printed_lead(split_inv)
    return {
        "R": R,
        "n": n,
        "n_faces": (1 << n) - 1,
        "slsqp_phi": phi,
        "target_suggest": target,
        "err_P_hi": err_hi,
        "gamma_pred": gamma_pred,
        "inv_pred": inv_pred,
        "cut_R_over_R1": cut,
        "split_gamma": split,
        "split_inv": split_inv,
        "printed_lead": printed,
        "beats_1.1021_if_certified": bool(printed < Q7_LEAD),
        "cut_ge_gamma": bool(cut >= gamma_pred),
        "note": note,
    }


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    configs = [
        (9.0, 34),
        (9.5, 34),
        (9.8, 33),
        (9.8, 34),
        (9.9, 33),
        (9.9, 34),
        (10.0, 33),
        (10.0, 34),
        (10.0, 35),
        (10.5, 34),
        (11.0, 34),
    ]
    rows = []
    cache = {}
    for R, n in configs:
        blob = assemble_mid(R, n)
        A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
        c = np.array([float(blob["rmid2"][i]) for i in range(n)])
        phi = slsqp_phi(A, c)
        q = blob["q_iv"]
        P = (q - 1) / (q + 1)
        err = P * (1 - blob["fmin_iv"])
        err_hi = float(mpf(err.b))
        target = float(np.floor((phi - 1e-4) * 1e4) / 1e4)
        rec = row_from_phi(R, n, phi, err_hi, target)
        rec["P_max_hi"] = float(mpf(P.b))
        rows.append(rec)
        cache[(R, n)] = rec
        print(
            f"R={R:4.1f} n={n:2d}  φ={phi:.6f}  tgt={target:.4f}  "
            f"err={err_hi:.5f}  γ={rec['gamma_pred']:.6f}  "
            f"1/γ={rec['inv_pred']:.6f}  printed={rec['printed_lead']:.4f}  "
            f"cut={rec['cut_R_over_R1']:.5f}  faces={rec['n_faces']:,}"
        )

    # Leftover: q7's n=33 SLSQP φ sits above the stored target 0.9111.
    # Raising the target on the same 2^33 faces can print below 1.1021
    # if faces still certify.
    base = cache[(10.0, 33)]
    extras = []
    for tgt in (0.91115, 0.9112):
        rec = row_from_phi(
            10.0,
            33,
            base["slsqp_phi"],
            base["err_P_hi"],
            tgt,
            note="same n=33 matrix as q7; higher target than 0.9111",
        )
        rec["P_max_hi"] = base.get("P_max_hi")
        extras.append(rec)
        print(
            f"R=10.0 n=33  raise tgt={tgt:.5f}  γ={rec['gamma_pred']:.6f}  "
            f"1/γ={rec['inv_pred']:.6f}  printed={rec['printed_lead']:.4f}  "
            f"cut_ge_γ={rec['cut_ge_gamma']}"
        )
    rows.extend(extras)

    feasible = [
        r
        for r in rows
        if r["beats_1.1021_if_certified"]
        and r["cut_ge_gamma"]
        and r["R"] == 10.0
    ]
    # cheapest certified path first: fewer faces, then smaller printed lead
    best = (
        min(feasible, key=lambda r: (r["n_faces"], r["printed_lead"]))
        if feasible
        else None
    )
    out = {
        "note": (
            "Predicted only. Face copositivity at target_suggest is required "
            "before quoting split_inv as a leading coefficient. printed_lead "
            "uses the notebook ceil-to-next-10^{-4}; 1.102041 prints as 1.1021."
        ),
        "q7_leading": Q7_LEAD,
        "fmin": FMIN,
        "best_split": best,
        "rows": rows,
    }
    path = CERTS / "scan_compact.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    if best:
        print(
            "best split",
            best["R"],
            best["n"],
            "target",
            best["target_suggest"],
            "printed",
            best["printed_lead"],
        )
    else:
        print("no predicted R=10 row prints below 1.1021")
    print("wrote", path)


if __name__ == "__main__":
    main()
