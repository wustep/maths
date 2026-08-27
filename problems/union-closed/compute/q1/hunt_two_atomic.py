"""Residue: random 2-atomic laws at (β=1, c=0.38304).

Not a proof that every measure is safe.  Isolated hits below 1 would
block any claim beyond the {b,1} ray.  Zero hits is incomplete search.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import h, h_or_example4, h_or_indep  # noqa: E402

CLAIMED_C = 0.38304
RNG = np.random.default_rng(20260827)


def c3_min(x, y, p, fn):
    best = 1e300
    for u in (p * p, p):
        pxx, pxy, pyy = u, p - u, 1.0 - 2.0 * p + u
        if pxy < -1e-15 or pyy < -1e-15:
            continue
        val = pxx * fn(x, x) + 2.0 * pxy * fn(x, y) + pyy * fn(y, y)
        if val < best:
            best = val
    return best


def ratio_ex4(x, y, p):
    eh = p * h(x) + (1.0 - p) * h(y)
    if eh <= 1e-16:
        return None
    e4 = c3_min(x, y, p, h_or_example4)
    return e4 / eh


def sample_two_atomic(n=40000):
    hits = []
    worst = None
    accepted = 0
    for _ in range(n):
        x, y = RNG.random(2)
        p = float(RNG.random())
        mean = p * x + (1.0 - p) * y
        if mean > CLAIMED_C or mean < 1e-6:
            continue
        r = ratio_ex4(float(x), float(y), p)
        if r is None:
            continue
        accepted += 1
        rec = {"x": float(x), "y": float(y), "p": p, "mean": float(mean), "ratio": float(r)}
        if worst is None or r < worst["ratio"]:
            worst = rec
        if r < 1.0:
            hits.append(rec)
    return accepted, worst, hits


def sample_near_ray(n=20000):
    """Perturb the analytic optimizer off the atom 1."""
    hits = []
    worst = None
    accepted = 0
    b0, a0 = 0.296493927746728, 0.12303721638515686
    for _ in range(n):
        b = float(np.clip(b0 + 0.04 * RNG.normal(), 0.02, 0.49))
        y = float(np.clip(1.0 - abs(0.02 * RNG.normal()), 0.7, 1.0))
        p = float(np.clip(1.0 - a0 + 0.05 * RNG.normal(), 0.4, 0.99))
        mean = p * b + (1.0 - p) * y
        if mean > CLAIMED_C:
            continue
        r = ratio_ex4(b, y, p)
        if r is None:
            continue
        accepted += 1
        rec = {"x": b, "y": y, "p": p, "mean": float(mean), "ratio": float(r)}
        if worst is None or r < worst["ratio"]:
            worst = rec
        if r < 1.0:
            hits.append(rec)
    return accepted, worst, hits


def main():
    a1, w1, h1 = sample_two_atomic()
    a2, w2, h2 = sample_near_ray()
    report = {
        "claimed_c": CLAIMED_C,
        "beta": 1.0,
        "uniform_2atomic": {
            "accepted": a1,
            "worst": w1,
            "n_hits_below_1": len(h1),
            "hits": h1[:10],
        },
        "near_ray": {
            "accepted": a2,
            "worst": w2,
            "n_hits_below_1": len(h2),
            "hits": h2[:10],
        },
        "note": "incomplete search, not a lower bound for every 2-atomic law",
    }
    path = Path(__file__).resolve().parent / "certs" / "hunt_two_atomic.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
