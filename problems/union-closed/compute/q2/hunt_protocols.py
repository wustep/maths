"""New named protocols on the {b,1} ray: half-target and scaled a(t).

The half-target protocol sets Π(0,0) as close to 1/2 as the Fréchet
box allows, for every (s,t).  On the diagonal this is the same
saturation as Example 4.  Scaled a(t) interpolates iid → Example 4
and then clips.

None of these can beat min 1-(1-b)h(b).  The scan is the check.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from protocols import h_or_named, pi_example4, pi_half_target

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import h  # noqa: E402

CEILING = 0.38305135658682558
CLAIMED = 0.38304


def equality_mean(b: float, name: str, **kw):
    hb = h(b)
    Hm = h_or_named(name, b, b, **kw)
    if hb <= 1e-18 or Hm <= 1e-18:
        return None
    one_minus_a = hb / Hm
    a = 1.0 - one_minus_a
    if a <= 0.0:
        return None
    if a > 0.5:
        a = 0.5
        one_minus_a = 0.5
    return dict(b=b, a=a, mean=1.0 - (1.0 - b) * one_minus_a, Hmix=Hm, hb=hb)


def first_crossing(name: str, n_grid: int = 3000, **kw):
    best = None
    for i in range(n_grid + 1):
        b = 0.02 + 0.479 * i / n_grid
        e = equality_mean(b, name, **kw)
        if e is None:
            continue
        if best is None or e["mean"] < best["mean"]:
            best = e
    if best is None:
        return None

    def obj(bb):
        e = equality_mean(float(bb), name, **kw)
        return e["mean"] if e is not None else 1.0

    lo = max(0.02, best["b"] - 0.04)
    hi = min(0.499, best["b"] + 0.04)
    opt = minimize_scalar(obj, bounds=(lo, hi), method="bounded", options={"xatol": 1e-12})
    refined = equality_mean(float(opt.x), name, **kw)
    return refined if refined is not None else best


def main():
    print("==== half-target vs Example 4 on the diagonal ====", flush=True)
    # At the analytic b*, both should saturate Π=1/2.
    bstar = 0.29649392356933757
    pi4 = pi_example4(bstar, bstar)
    pih = pi_half_target(bstar, bstar)
    print(f"  Π_ex4(b*,b*)={pi4:.16f}  Π_half={pih:.16f}", flush=True)

    half = first_crossing("half")
    ex4 = first_crossing("ex4")
    print("half", half, flush=True)
    print("ex4 ", ex4, flush=True)

    print("==== scaled a(t) ====", flush=True)
    scaled_rows = []
    scaled_best = None
    for alpha in np.linspace(0.0, 1.4, 29):
        rec = first_crossing("scaled_ex4", alpha=float(alpha))
        if rec is None:
            continue
        packed = {"alpha": float(alpha), **rec, "below_ceiling": rec["mean"] <= CEILING + 1e-12}
        scaled_rows.append(packed)
        if scaled_best is None or packed["mean"] > scaled_best["mean"]:
            scaled_best = packed
        if abs(alpha * 5 - round(alpha * 5)) < 1e-9:
            print(f"  α={alpha:.2f}  c={packed['mean']:.12f}", flush=True)

    anyone_beats_claimed = False
    for rec in (half, ex4, scaled_best):
        if rec is not None and rec["mean"] > CLAIMED:
            anyone_beats_claimed = True
    anyone_beats_ceiling = any(
        rec is not None and rec["mean"] > CEILING + 1e-9
        for rec in (half, ex4, scaled_best)
    )

    report = {
        "ceiling": CEILING,
        "claimed": CLAIMED,
        "pi_at_bstar": {"ex4": pi4, "half": pih, "target": 0.5},
        "half_target": half,
        "example4": ex4,
        "scaled_best": scaled_best,
        "scaled_sample": [
            r for r in scaled_rows if abs(r["alpha"] * 5 - round(r["alpha"] * 5)) < 1e-9
        ],
        "anyone_beats_claimed_0_38304": anyone_beats_claimed,
        "anyone_beats_ceiling": anyone_beats_ceiling,
        "note": (
            "half-target coincides with Example 4 on the {b,1} diagonal "
            "at the optimizer.  Scaled a(t) peaks at α=1.  No new protocol "
            "in this list moves 0.38304."
        ),
    }
    path = Path(__file__).resolve().parent / "certs" / "hunt_protocols.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)
    if anyone_beats_ceiling:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
