#!/usr/bin/env python3
"""Predicted compact γ(R,n) from SLSQP φ minus P_max error.

Not a certificate. Used to pick face-enumeration targets that can
beat printed 1.1010. A predicted γ is only a dent after faces say
M is copositive at that φ_target.

Printed leading uses the same ceil-to-next-10^{-4} as
tighten_leading.py: 1.10094 prints as 1.1010.

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
Q11_LEAD = 1.1010


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


def printed_lead(x: float) -> str:
    """Same ceil-to-next-grid as tighten_leading.ceil_dec(..., 4)."""
    val = (math.floor(x * 10000.0 + 1e-12) + 1) / 10000.0
    return format(val, ".4f")


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
        "beats_1.1010_if_certified": bool(float(printed) < Q11_LEAD),
        "cut_ge_gamma": bool(cut >= gamma_pred),
        "note": note,
    }


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    configs = [
        (10.0, 35),
        (10.0, 36),
        (10.0, 37),
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
            f"1/γ={rec['inv_pred']:.6f}  printed={rec['printed_lead']}  "
            f"cut={rec['cut_R_over_R1']:.5f}  faces={rec['n_faces']:,}"
        )

    extras = []
    base35 = cache[(10.0, 35)]
    rec = row_from_phi(
        10.0,
        35,
        base35["slsqp_phi"],
        base35["err_P_hi"],
        0.9116,
        note="optional probe on the frozen n=35 matrix; not an n=37 dent",
    )
    rec["P_max_hi"] = base35.get("P_max_hi")
    extras.append(rec)
    print(
        f"R=10.0 n=35  raise tgt=0.9116  γ={rec['gamma_pred']:.6f}  "
        f"1/γ={rec['inv_pred']:.6f}  printed={rec['printed_lead']}  "
        f"cut_ge_γ={rec['cut_ge_gamma']}"
    )

    base36 = cache[(10.0, 36)]
    rec = row_from_phi(
        10.0,
        36,
        base36["slsqp_phi"],
        base36["err_P_hi"],
        0.9118,
        note="optional probe on the frozen n=36 matrix; not an n=37 dent",
    )
    rec["P_max_hi"] = base36.get("P_max_hi")
    extras.append(rec)
    print(
        f"R=10.0 n=36  raise tgt=0.9118  γ={rec['gamma_pred']:.6f}  "
        f"1/γ={rec['inv_pred']:.6f}  printed={rec['printed_lead']}  "
        f"cut_ge_γ={rec['cut_ge_gamma']}"
    )

    base37 = cache[(10.0, 37)]
    rec = dict(base37)
    rec["note"] = "primary leftover: n=37 mid-radius bins at aspect 10"
    extras.append(rec)
    print(
        f"R=10.0 n=37  primary tgt={rec['target_suggest']:.4f}  "
        f"γ={rec['gamma_pred']:.6f}  1/γ={rec['inv_pred']:.6f}  "
        f"printed={rec['printed_lead']}  cut_ge_γ={rec['cut_ge_gamma']}"
    )
    rows.extend(extras)

    feasible = [
        r
        for r in rows
        if r["beats_1.1010_if_certified"]
        and r["cut_ge_gamma"]
        and r["R"] == 10.0
        and r["n"] == 37
    ]
    best = (
        min(feasible, key=lambda r: (r["n_faces"], float(r["printed_lead"])))
        if feasible
        else None
    )
    out = {
        "note": (
            "Predicted only. Face copositivity at target_suggest is required "
            "before quoting split_inv as a leading coefficient. printed_lead "
            "uses the notebook ceil-to-next-10^{-4}; 1.10094 prints as 1.1010. "
            "An n=35 or n=36 higher-target probe is not an n=37 dent. "
            "The stored q11 n=36 faces stay frozen."
        ),
        "q11_leading": Q11_LEAD,
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
        print("no predicted R=10 n=37 row prints below 1.1010")
    print("wrote", path)


if __name__ == "__main__":
    main()
