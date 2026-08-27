"""First-crossing on {b,1} for iid / Example-4 / Example-5 / maxent mixes.

On this ray the independent C3 endpoint is always worse, so

    c(weights) = min_b  1 − (1-b) h(b) / Hmix(b)

when that equality weight is feasible.  Hmix ≤ 1, so c ≤ the
analytic ceiling 0.383051….  This scan records the numerical
confirmation: the best mix is pure Example 4.

Not a new bound.  Residue relative to 1/2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from protocols import mix_h_or

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import h  # noqa: E402

CEILING = 0.38305135658682558
CLAIMED = 0.38304


def Hmix(b: float, weights: dict[str, float], **kw) -> float:
    return mix_h_or(b, b, weights, **kw)


def equality_mean(b: float, weights: dict[str, float], **kw):
    hb = h(b)
    Hm = Hmix(b, weights, **kw)
    if hb <= 1e-18 or Hm <= 1e-18:
        return None
    one_minus_a = hb / Hm
    a = 1.0 - one_minus_a
    if a <= 0.0:
        return None
    if a > 0.5:
        a = 0.5
        one_minus_a = 0.5
    mean = 1.0 - (1.0 - b) * one_minus_a
    return dict(b=b, a=a, mean=mean, Hmix=Hm, hb=hb)


def first_crossing(weights: dict[str, float], n_grid: int = 2500, **kw):
    best = None
    for i in range(n_grid + 1):
        b = 0.02 + 0.479 * i / n_grid
        e = equality_mean(b, weights, **kw)
        if e is None:
            continue
        if best is None or e["mean"] < best["mean"]:
            best = e
    if best is None:
        return None

    def obj(bb):
        e = equality_mean(float(bb), weights, **kw)
        return e["mean"] if e is not None else 1.0

    lo = max(0.02, best["b"] - 0.04)
    hi = min(0.499, best["b"] + 0.04)
    opt = minimize_scalar(obj, bounds=(lo, hi), method="bounded", options={"xatol": 1e-12})
    refined = equality_mean(float(opt.x), weights, **kw)
    return refined if refined is not None else best


def pack(weights, rec, **extra):
    if rec is None:
        return None
    out = {"weights": weights, **rec, **extra}
    out["below_ceiling"] = rec["mean"] <= CEILING + 1e-12
    out["beats_claimed"] = rec["mean"] > CLAIMED
    return out


def main():
    rows = []
    best = None

    print("==== iid + Example-4 ====", flush=True)
    for beta in np.linspace(0.0, 1.0, 101):
        w = {"iid": 1.0 - float(beta), "ex4": float(beta)}
        rec = first_crossing(w)
        packed = pack(w, rec)
        if packed is None:
            continue
        rows.append(packed)
        if best is None or packed["mean"] > best["mean"]:
            best = packed
        if abs(beta * 10 - round(beta * 10)) < 1e-9:
            print(
                f"  β4={beta:.2f}  c={packed['mean']:.12f}  H={packed['Hmix']:.6f}",
                flush=True,
            )

    print("==== iid + Example-5 ====", flush=True)
    best5 = None
    rows5 = []
    for beta in np.linspace(0.0, 1.0, 51):
        w = {"iid": 1.0 - float(beta), "ex5": float(beta)}
        rec = first_crossing(w)
        packed = pack(w, rec)
        if packed is None:
            continue
        rows5.append(packed)
        if best5 is None or packed["mean"] > best5["mean"]:
            best5 = packed
    print("BEST ex5", best5["mean"] if best5 else None, flush=True)

    print("==== Example-4 + Example-5 (no iid) ====", flush=True)
    best45 = None
    rows45 = []
    for t in np.linspace(0.0, 1.0, 51):
        w = {"ex4": 1.0 - float(t), "ex5": float(t)}
        rec = first_crossing(w)
        packed = pack(w, rec)
        if packed is None:
            continue
        rows45.append(packed)
        if best45 is None or packed["mean"] > best45["mean"]:
            best45 = packed
    print("BEST ex4+ex5", best45["mean"] if best45 else None, flush=True)

    print("==== 3-way iid + ex4 + maxent ====", flush=True)
    best3 = None
    rows3 = []
    for gamma in np.linspace(0.0, 0.20, 11):
        for beta in np.linspace(0.0, 1.0, 21):
            if beta + gamma > 1.0 + 1e-15:
                continue
            w = {
                "iid": max(0.0, 1.0 - float(beta) - float(gamma)),
                "ex4": float(beta),
                "maxent": float(gamma),
            }
            rec = first_crossing(w, n_grid=1500)
            packed = pack(w, rec)
            if packed is None:
                continue
            rows3.append(packed)
            if best3 is None or packed["mean"] > best3["mean"]:
                best3 = packed
    print("BEST 3way", best3["mean"] if best3 else None, flush=True)

    print("==== Example-5 scale ℓ ====", flush=True)
    best_ell = None
    rows_ell = []
    for ell in np.linspace(0.0, 1.0, 21):
        w = {"ex5": 1.0}
        rec = first_crossing(w, ell=float(ell))
        packed = pack(w, rec, ell=float(ell))
        if packed is None:
            continue
        rows_ell.append(packed)
        if best_ell is None or packed["mean"] > best_ell["mean"]:
            best_ell = packed
    print("BEST ex5-ℓ", best_ell["mean"] if best_ell else None, flush=True)

    anyone_beats_claimed = any(
        r["beats_claimed"]
        for r in rows + rows5 + rows45 + rows3 + rows_ell
        if r is not None
    )
    anyone_beats_ceiling = any(
        r["mean"] > CEILING + 1e-9
        for r in rows + rows5 + rows45 + rows3 + rows_ell
        if r is not None
    )

    report = {
        "ceiling": CEILING,
        "claimed": CLAIMED,
        "ex4_best": best,
        "ex5_best": best5,
        "ex4_ex5_best": best45,
        "three_way_best": best3,
        "ex5_ell_best": best_ell,
        "ex4_curve_sample": [
            r
            for r in rows
            if abs(r["weights"]["ex4"] * 10 - round(r["weights"]["ex4"] * 10)) < 1e-9
        ],
        "anyone_beats_claimed_0_38304": anyone_beats_claimed,
        "anyone_beats_ceiling": anyone_beats_ceiling,
        "note": (
            "pure Example 4 is best on this ray and still sits at the "
            "analytic ceiling.  No mix is a dent of 0.38304 toward 1/2."
        ),
    }
    path = Path(__file__).resolve().parent / "certs" / "hunt_mixes.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("BEST overall", best["mean"] if best else None)
    print("beats claimed?", anyone_beats_claimed, "beats ceiling?", anyone_beats_ceiling)
    print("wrote", path)


if __name__ == "__main__":
    main()
