"""1-D first-crossing of iid + Example-4 (and + maxent) on {b,1}.

On support {b,1} with P(S=1)=a, independent C3 is always the worse
Example-4 endpoint (e_ind = (1-a)^2 hp <= (1-a) hp = e_cor).  The
Gilmer ratio is then

    ratio = (1-a) * Hmix(b) / h(b)

with Hmix = (1-beta)*h(2b-b^2) + beta*h_or_ex4(b,b) [+ gamma maxent].
Equality forces a = 1 - h(b)/Hmix, so the first mean with ratio < 1 is

    c(weights) = min_b  1 - (1-b) h(b) / Hmix(b)

when that a sits in (0, 1/2].  This is the mesh first-crossing, not
the envelope maximum that best_on_ray.py reported.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import h, h_or_example4, h_or_indep, h_or_maxent

LN2 = math.log(2)


def Hmix(b: float, beta: float, gamma: float = 0.0) -> float:
    hid = h_or_indep(b, b)
    hp = h_or_example4(b, b)
    hm = h_or_maxent(b, b)
    w_iid = 1.0 - beta - gamma
    if w_iid < -1e-15:
        raise ValueError("weights")
    return max(w_iid, 0.0) * hid + beta * hp + gamma * hm


def equality_mean(b: float, beta: float, gamma: float = 0.0):
    hb = h(b)
    Hm = Hmix(b, beta, gamma)
    if hb <= 1e-18 or Hm <= 1e-18:
        return None
    one_minus_a = hb / Hm
    a = 1.0 - one_minus_a
    if a <= 0.0:
        # even a=0 has ratio >= 1; this b is not a crossing
        return None
    if a > 0.5:
        # a=0.5 is already bad; crossing at a=0.5
        a = 0.5
        one_minus_a = 0.5
    mean = 1.0 - (1.0 - b) * one_minus_a
    return dict(b=b, a=a, mean=mean, Hmix=Hm, hb=hb)


def first_crossing(beta: float, gamma: float = 0.0, n_grid: int = 4000):
    best = None
    # coarse grid then local refine
    for i in range(n_grid + 1):
        b = 0.02 + 0.479 * i / n_grid
        e = equality_mean(b, beta, gamma)
        if e is None:
            continue
        if best is None or e["mean"] < best["mean"]:
            best = e
    if best is None:
        return None

    def obj(b):
        e = equality_mean(float(b), beta, gamma)
        return e["mean"] if e is not None else 1.0

    lo = max(0.02, best["b"] - 0.04)
    hi = min(0.499, best["b"] + 0.04)
    opt = minimize_scalar(obj, bounds=(lo, hi), method="bounded", options={"xatol": 1e-14})
    refined = equality_mean(float(opt.x), beta, gamma)
    return refined if refined is not None else best


def main():
    rows = []
    best = None
    betas = np.linspace(0.0, 1.0, 201)
    print("==== iid + Example-4, gamma=0 ====", flush=True)
    for beta in betas:
        rec = first_crossing(float(beta), 0.0)
        if rec is None:
            continue
        rec = {"beta": float(beta), "gamma": 0.0, **rec}
        rows.append(rec)
        if best is None or rec["mean"] > best["mean"]:
            best = rec
        if abs(beta * 20 - round(beta * 20)) < 1e-9 or rec is best:
            print(
                f"  β={beta:.4f}  c={rec['mean']:.12f}  b={rec['b']:.8f}  a={rec['a']:.8f}",
                flush=True,
            )

    print("BEST ex4", best, flush=True)

    # 3-way: iid + ex4 + maxent.  Small gamma grid.
    print("==== iid + Example-4 + maxent ====", flush=True)
    mix_rows = []
    mix_best = None
    for gamma in np.linspace(0.0, 0.12, 25):
        for beta in np.linspace(0.0, 0.90, 91):
            if beta + gamma > 0.999:
                continue
            rec = first_crossing(float(beta), float(gamma), n_grid=2000)
            if rec is None:
                continue
            rec = {"beta": float(beta), "gamma": float(gamma), **rec}
            mix_rows.append(rec)
            if mix_best is None or rec["mean"] > mix_best["mean"]:
                mix_best = rec
        print(
            f"  γ={gamma:.4f}  local-best so far c={mix_best['mean']:.12f}  "
            f"β={mix_best['beta']:.4f}",
            flush=True,
        )

    print("BEST 3way", mix_best, flush=True)

    # replay the published β=1/5 number
    replay = first_crossing(0.20, 0.0)
    print("replay β=1/5", replay, flush=True)

    report = {
        "ex4_curve": rows,
        "ex4_best": best,
        "three_way_best": mix_best,
        "three_way_sample": [
            r
            for r in mix_rows
            if abs(r["gamma"] * 20 - round(r["gamma"] * 20)) < 1e-9
            and abs(r["beta"] * 10 - round(r["beta"] * 10)) < 1e-9
        ],
        "replay_beta_0_20": replay,
        "repo_claimed": 0.38285,
        "liu_quote": 0.382709087918741,
    }
    path = Path(__file__).resolve().parent / "scan_beta.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
