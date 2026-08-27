"""3-atomic and 2-mixture residue at c=0.38304 and a 0.40 probe.

Same class as Liu Theorem 9 (2-mixture of iid laws).  A hit below 1
at mean ≤ 0.38304 would block extending the ray claim off {b,1}.
Zero hits is incomplete search, not a lower bound, and not a move
of 0.38304.

The 0.40 probe is the 'toward 1/2' check: if the worst 3-atomic
already fails well below 0.40, this class does not point at 1/2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from numpy.random import default_rng

from protocols import h_or_named, mix_h_or

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import h  # noqa: E402

CLAIMED = 0.38304
PROBE = 0.40
RNG = default_rng(20260827)


def ratio_atomic(vals, wts, fn):
    vals = np.asarray(vals, dtype=float)
    wts = np.asarray(wts, dtype=float)
    wts = wts / wts.sum()
    mean = float(np.dot(vals, wts))
    eh = float(sum(float(wts[i]) * h(float(vals[i])) for i in range(len(vals))))
    if eh <= 1e-16:
        return None
    eor = 0.0
    n = len(vals)
    for i in range(n):
        for j in range(n):
            eor += float(wts[i] * wts[j]) * fn(float(vals[i]), float(vals[j]))
    return eor / eh, mean


def ratio_mixture(v0, w0, v1, w1, q, fn_ciid, fn_iid):
    v0, w0 = np.asarray(v0, float), np.asarray(w0, float)
    v1, w1 = np.asarray(v1, float), np.asarray(w1, float)
    w0 = w0 / w0.sum()
    w1 = w1 / w1.sum()
    mean = (1 - q) * float(np.dot(v0, w0)) + q * float(np.dot(v1, w1))
    eh = (1 - q) * float(sum(w0[i] * h(float(v0[i])) for i in range(len(v0)))) + q * float(
        sum(w1[i] * h(float(v1[i])) for i in range(len(v1)))
    )
    if eh <= 1e-16:
        return None

    def prod(v, w, fn):
        s = 0.0
        for i in range(len(v)):
            for j in range(len(v)):
                s += float(w[i] * w[j]) * fn(float(v[i]), float(v[j]))
        return s

    e_ciid = (1 - q) * prod(v0, w0, fn_ciid) + q * prod(v1, w1, fn_ciid)
    vm = np.concatenate([v0, v1])
    wm = np.concatenate([(1 - q) * w0, q * w1])
    e_iid = prod(vm, wm, fn_iid)
    # pure CIID protocol (β=1), product iid only used if we mix; here β=1
    return e_ciid / eh, mean, e_iid / eh


def sample_atomic(n, n_atoms, c, fn, near_ray=False):
    hits = []
    worst = None
    accepted = 0
    b0, a0 = 0.29649392356933757, 0.1230372215925261
    for _ in range(n):
        if near_ray:
            b = float(np.clip(b0 + 0.05 * RNG.normal(), 0.02, 0.49))
            y = float(np.clip(1.0 - abs(0.03 * RNG.normal()), 0.65, 1.0))
            z = float(np.clip(b + 0.15 * RNG.normal(), 0.02, 0.95))
            vals = np.array([b, y, z])
            wts = np.array([1.0 - a0, a0 * 0.85, a0 * 0.15])
            wts = np.clip(wts + 0.04 * RNG.normal(size=3), 1e-6, None)
        else:
            vals = RNG.random(n_atoms)
            wts = RNG.dirichlet(np.ones(n_atoms))
        mean = float(np.dot(vals, wts / wts.sum()))
        if mean > c or mean < 1e-6:
            continue
        got = ratio_atomic(vals, wts, fn)
        if got is None:
            continue
        r, mean = got
        accepted += 1
        rec = {
            "vals": [float(v) for v in vals],
            "wts": [float(w) for w in (wts / wts.sum())],
            "mean": mean,
            "ratio": float(r),
        }
        if worst is None or r < worst["ratio"]:
            worst = rec
        if r < 1.0:
            hits.append(rec)
    return accepted, worst, hits


def sample_mixtures(n, c, fn_ciid, fn_iid):
    hits = []
    worst = None
    accepted = 0
    for _ in range(n):
        v0 = RNG.random(2)
        w0 = RNG.dirichlet(np.ones(2))
        v1 = RNG.random(2)
        w1 = RNG.dirichlet(np.ones(2))
        q = float(RNG.random())
        got = ratio_mixture(v0, w0, v1, w1, q, fn_ciid, fn_iid)
        if got is None:
            continue
        r, mean, _ = got
        if mean > c or mean < 1e-6:
            continue
        accepted += 1
        rec = {
            "v0": [float(v) for v in v0],
            "w0": [float(w) for w in w0],
            "v1": [float(v) for v in v1],
            "w1": [float(w) for w in w1],
            "q": q,
            "mean": float(mean),
            "ratio": float(r),
        }
        if worst is None or r < worst["ratio"]:
            worst = rec
        if r < 1.0:
            hits.append(rec)
    return accepted, worst, hits


def summarize(accepted, worst, hits):
    return {
        "accepted": accepted,
        "worst": worst,
        "n_hits_below_1": len(hits),
        "hits": hits[:8],
    }


def main():
    fn4 = lambda s, t: h_or_named("ex4", s, t)
    fn_half = lambda s, t: h_or_named("half", s, t)
    fn_iid = lambda s, t: h_or_named("iid", s, t)
    fn_mix = lambda s, t: mix_h_or(s, t, {"ex4": 0.7, "ex5": 0.3})

    print("3-atomic Example 4 at 0.38304", flush=True)
    a1, w1, h1 = sample_atomic(40000, 3, CLAIMED, fn4)
    print("  accepted", a1, "hits", len(h1), "worst", None if w1 is None else w1["ratio"], flush=True)

    print("3-atomic near-ray Example 4 at 0.38304", flush=True)
    a2, w2, h2 = sample_atomic(20000, 3, CLAIMED, fn4, near_ray=True)
    print("  accepted", a2, "hits", len(h2), "worst", None if w2 is None else w2["ratio"], flush=True)

    print("2-mixtures of 2-atomic Example 4 at 0.38304", flush=True)
    a3, w3, h3 = sample_mixtures(25000, CLAIMED, fn4, fn_iid)
    print("  accepted", a3, "hits", len(h3), "worst", None if w3 is None else w3["ratio"], flush=True)

    print("3-atomic half-target at 0.38304", flush=True)
    a4, w4, h4 = sample_atomic(20000, 3, CLAIMED, fn_half)
    print("  accepted", a4, "hits", len(h4), "worst", None if w4 is None else w4["ratio"], flush=True)

    print("3-atomic ex4+ex5 mix at 0.38304", flush=True)
    a5, w5, h5 = sample_atomic(15000, 3, CLAIMED, fn_mix)
    print("  accepted", a5, "hits", len(h5), "worst", None if w5 is None else w5["ratio"], flush=True)

    print("3-atomic Example 4 at 0.40 (toward 1/2 probe)", flush=True)
    a6, w6, h6 = sample_atomic(20000, 3, PROBE, fn4)
    print("  accepted", a6, "hits", len(h6), "worst", None if w6 is None else w6["ratio"], flush=True)

    # Deterministic {b,1} past the ceiling: a chosen so mean=0.39.
    bstar = 0.29649392356933757
    mean_probe = 0.39
    a_eq = (mean_probe - bstar) / (1.0 - bstar)
    ray = ratio_atomic([bstar, 1.0], [1.0 - a_eq, a_eq], fn4)
    ray_rec = None
    if ray is not None:
        ray_rec = {"b": bstar, "a": a_eq, "mean": ray[1], "ratio": ray[0]}
        print("  deterministic {b,1} at mean 0.39 ratio", ray[0], flush=True)

    report = {
        "claimed_c": CLAIMED,
        "probe_c": PROBE,
        "ex4_3atomic_claimed": summarize(a1, w1, h1),
        "ex4_near_ray_claimed": summarize(a2, w2, h2),
        "ex4_2mix_claimed": summarize(a3, w3, h3),
        "half_3atomic_claimed": summarize(a4, w4, h4),
        "ex4_ex5_3atomic_claimed": summarize(a5, w5, h5),
        "ex4_3atomic_probe_0_40": summarize(a6, w6, h6),
        "ray_at_mean_0_39": ray_rec,
        "hits_at_claimed_atomic": len(h1) + len(h2) + len(h4) + len(h5),
        "hits_at_claimed_2mix": len(h3),
        "hits_at_claimed": len(h1) + len(h2) + len(h3) + len(h4) + len(h5),
        "hits_at_probe": len(h6) + (1 if ray_rec is not None and ray_rec["ratio"] < 1.0 else 0),
        "note": (
            "incomplete search, not a lower bound for every 3-atomic law. "
            "The 0.40 probe is expected to have hits: {b,1} itself crosses "
            "at 0.383051, so 0.40 is already past the class ceiling."
        ),
    }
    path = Path(__file__).resolve().parent / "certs" / "hunt_three.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)
    print("hits at 0.38304", report["hits_at_claimed"], "hits at 0.40", report["hits_at_probe"])


if __name__ == "__main__":
    main()
