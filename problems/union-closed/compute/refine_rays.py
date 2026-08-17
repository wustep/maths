"""Fine scan of the 2-atomic {b,1} family (the Liu / Yu–Cambie ray)
and of 2-atomic laws supported in [0,1).

Reports, for several protocol mixes, the largest mean at which the
entropy ratio stays ≥ 1, and the crossing point.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from entropy import a_example4, h, h_or_example4, h_or_example5, h_or_indep, h_or_maxent

LN2 = math.log(2)


def h_or_ex4_bb(b: float) -> float:
    return h_or_example4(b, b)


def h_or_ex5_bb(b: float) -> float:
    return h_or_example5(b, b)


def ray_terms(a: float, b: float):
    """Support {b,1}, P(1)=a, P(b)=1-a.  All pieces for the mixes."""
    if a < 0 or a > 0.5 or b < 0 or b > 1:
        return None
    eh = (1.0 - a) * h(b)
    if eh <= 1e-16:
        return None
    eiid = (1.0 - a) ** 2 * h_or_indep(b, b)
    # maxent worst: P(1,1)=0, P(b,b)=1-2a, P(b,1)=a
    emax = (1.0 - 2.0 * a) * h_or_maxent(b, b)
    # C3 endpoints for Example 4
    e4_ind = (1.0 - a) ** 2 * h_or_example4(b, b)
    e4_cor = (1.0 - a) * h_or_example4(b, b)  # P(b,b)=1-a, P(1,1)=a
    e4 = min(e4_ind, e4_cor)
    e5_ind = (1.0 - a) ** 2 * h_or_example5(b, b)
    e5_cor = (1.0 - a) * h_or_example5(b, b)
    e5 = min(e5_ind, e5_cor)
    mean = a + (1.0 - a) * b
    return dict(a=a, b=b, mean=mean, eh=eh, eiid=eiid, emax=emax, e4=e4, e5=e5)


def mix_ratio(t, w):
    num = w["iid"] * t["eiid"] + w["max"] * t["emax"] + w["ex4"] * t["e4"] + w["ex5"] * t["e5"]
    return num / t["eh"]


WEIGHTS = {
    "iid": dict(iid=1, max=0, ex4=0, ex5=0),
    "sawin": dict(iid=0.96439302, max=0.03560698, ex4=0, ex5=0),
    "liu_ex5": dict(iid=0.89994744, max=0, ex4=0, ex5=0.10005256),
    "ex4_b08": dict(iid=0.92, max=0, ex4=0.08, ex5=0),
    "ex4_b10": dict(iid=0.90, max=0, ex4=0.10, ex5=0),
    "ex4_b12": dict(iid=0.88, max=0, ex4=0.12, ex5=0),
    "ex4_b16": dict(iid=0.84, max=0, ex4=0.16, ex5=0),
    "ex4_b20": dict(iid=0.80, max=0, ex4=0.20, ex5=0),
    "triple_sawin_ex4": dict(iid=0.90, max=0.03, ex4=0.07, ex5=0),
    "triple_eq": dict(iid=0.86, max=0.0356, ex4=0.1044, ex5=0),
    "triple_more_ex4": dict(iid=0.82, max=0.03, ex4=0.15, ex5=0),
    "triple_more_max": dict(iid=0.88, max=0.06, ex4=0.06, ex5=0),
}


def scan_ray(w, n_b=800, n_a=400):
    recs = []
    for b in np.linspace(0.02, 0.499, n_b):
        for a in np.linspace(0.0, 0.499, n_a):
            t = ray_terms(float(a), float(b))
            if t is None:
                continue
            recs.append((mix_ratio(t, w), t["mean"], float(a), float(b)))
    recs.sort()
    return recs


def crossing_on_ray(w, n_b=1200):
    """For each b, take a so mean is free; find max mean with ratio≥1
    by scanning a, then polish."""
    best_c = 0.0
    best_pt = None
    worst_below = None  # min ratio among mean≤0.3832
    min_r_38271 = 10.0
    min_r_38280 = 10.0
    min_r_38300 = 10.0
    min_r_38310 = 10.0
    for b in np.linspace(0.05, 0.49, n_b):
        # a from 0 to min(0.5, (0.42-b)/(1-b))
        a_max = min(0.499, (0.42 - b) / (1 - b)) if b < 0.42 else 0.0
        if a_max <= 0:
            continue
        for a in np.linspace(0.0, a_max, 500):
            t = ray_terms(float(a), float(b))
            if t is None:
                continue
            r = mix_ratio(t, w)
            if r <= 1.0 and t["mean"] > best_c:
                best_c = t["mean"]
                best_pt = (r, t["mean"], float(a), float(b))
            if t["mean"] <= 0.38270908792:
                min_r_38271 = min(min_r_38271, r)
            if t["mean"] <= 0.38280:
                min_r_38280 = min(min_r_38280, r)
            if t["mean"] <= 0.38300:
                min_r_38300 = min(min_r_38300, r)
            if t["mean"] <= 0.38310:
                min_r_38310 = min(min_r_38310, r)
    return {
        "max_mean_ratio_le_1": best_c,
        "at": None
        if best_pt is None
        else {"ratio": best_pt[0], "mean": best_pt[1], "a": best_pt[2], "b": best_pt[3]},
        "min_ratio_le_0.382709": min_r_38271,
        "min_ratio_le_0.38280": min_r_38280,
        "min_ratio_le_0.38300": min_r_38300,
        "min_ratio_le_0.38310": min_r_38310,
    }


def interior_two_atomic(w, n=70, pgrid=50):
    """Both atoms in [0,1), plus a few with one at 1 already covered."""
    recs = []
    xs = np.linspace(0.0, 0.999, n)
    for i, x in enumerate(xs):
        for y in xs[i:]:
            if y >= 0.999:
                continue
            for p in np.linspace(0.02, 0.98, pgrid):
                eh = p * h(x) + (1 - p) * h(y)
                if eh <= 1e-16:
                    continue
                eiid = (
                    p * p * h_or_indep(x, x)
                    + 2 * p * (1 - p) * h_or_indep(x, y)
                    + (1 - p) * (1 - p) * h_or_indep(y, y)
                )
                emax_lo = p * p
                emax_hi = p
                emax = 1e9
                for u in (emax_lo, emax_hi):
                    val = (
                        u * h_or_maxent(x, x)
                        + 2 * (p - u) * h_or_maxent(x, y)
                        + (1 - 2 * p + u) * h_or_maxent(y, y)
                    )
                    emax = min(emax, val)
                e4 = 1e9
                e5 = 1e9
                for u in (p * p, p):
                    e4 = min(
                        e4,
                        u * h_or_example4(x, x)
                        + 2 * (p - u) * h_or_example4(x, y)
                        + (1 - 2 * p + u) * h_or_example4(y, y),
                    )
                    e5 = min(
                        e5,
                        u * h_or_example5(x, x)
                        + 2 * (p - u) * h_or_example5(x, y)
                        + (1 - 2 * p + u) * h_or_example5(y, y),
                    )
                mean = p * x + (1 - p) * y
                num = w["iid"] * eiid + w["max"] * emax + w["ex4"] * e4 + w["ex5"] * e5
                recs.append((num / eh, mean, float(x), float(y), float(p)))
    recs.sort()
    return recs


def summarise_interior(recs):
    out = {}
    if not recs:
        return out
    out["global_min"] = recs[0][0]
    out["at_mean"] = recs[0][1]
    out["at"] = {"x": recs[0][2], "y": recs[0][3], "p": recs[0][4]}
    for c, key in [
        (0.38234553337, "cstar"),
        (0.38270908792, "liu"),
        (0.38280, "c38280"),
        (0.38300, "c38300"),
        (0.38309929768, "c4"),
    ]:
        sub = [r for r in recs if r[1] <= c]
        if sub:
            out[key] = {"min_ratio": sub[0][0], "mean": sub[0][1], "x": sub[0][2], "y": sub[0][3], "p": sub[0][4]}
    bad = [r for r in recs if r[0] <= 1]
    if bad:
        m = max(bad, key=lambda t: t[1])
        out["max_mean_r_le_1"] = {"ratio": m[0], "mean": m[1], "x": m[2], "y": m[3], "p": m[4]}
    return out


def closed_forms():
    x = 1.0 / math.sqrt(2.0)
    p = h(x)
    c4 = 1.0 - p * x
    return {
        "x": x,
        "p": p,
        "c4": c4,
        "formula": "1 - h(2^{-1/2}) / sqrt(2)",
        "liu": 0.382709087918735,
        "cstar": 0.382345533366703,
        "phi": (3 - math.sqrt(5)) / 2,
    }


def main():
    cf = closed_forms()
    print("closed form c4", cf["c4"], flush=True)
    report = {"closed_form": cf, "rays": {}, "interior": {}}
    for name, w in WEIGHTS.items():
        print("ray", name, flush=True)
        report["rays"][name] = {"weights": w, **crossing_on_ray(w, n_b=900)}
        print("  ", report["rays"][name]["max_mean_ratio_le_1"],
              "r@liu", report["rays"][name]["min_ratio_le_0.382709"],
              "r@38280", report["rays"][name]["min_ratio_le_0.38280"],
              flush=True)

    # interior 2-atomic for the most promising mixes
    for name in ["liu_ex5", "ex4_b10", "ex4_b16", "triple_eq", "triple_more_ex4"]:
        print("interior", name, flush=True)
        recs = interior_two_atomic(WEIGHTS[name], n=50, pgrid=40)
        report["interior"][name] = summarise_interior(recs)
        print("  ", report["interior"][name].get("liu"),
              report["interior"][name].get("c38280"), flush=True)

    path = Path(__file__).resolve().parent / "refine_rays.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
