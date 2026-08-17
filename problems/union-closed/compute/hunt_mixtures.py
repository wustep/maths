"""Search for measures worse than the {b,1} ray at a candidate (β, c).

If a 3-atomic law or a 2-mixture of 2-atomic laws with mean ≤ c has
iid+Example-4 ratio < 1, the ray-constant is not a bound even under
Liu's 2-mixture reduction (Theorem 9).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from numpy.random import default_rng

from entropy import h, h_or_example4, h_or_indep

BETA = 0.20
C = 0.38285


def ratio_atomic(vals, wts, beta=BETA):
    vals = np.asarray(vals, dtype=float)
    wts = np.asarray(wts, dtype=float)
    wts = wts / wts.sum()
    mean = float(np.dot(vals, wts))
    eh = float(sum(wts[i] * h(float(vals[i])) for i in range(len(vals))))
    if eh <= 1e-16:
        return None
    eiid = 0.0
    e4 = 0.0
    n = len(vals)
    for i in range(n):
        for j in range(n):
            ww = float(wts[i] * wts[j])
            eiid += ww * h_or_indep(float(vals[i]), float(vals[j]))
            e4 += ww * h_or_example4(float(vals[i]), float(vals[j]))
    r = ((1.0 - beta) * eiid + beta * e4) / eh
    return r, mean, eh


def ratio_mixture(v0, w0, v1, w1, q, beta=BETA):
    """μ = (1-q) P0 + q P1; CIID uses the 2-mixture coupling; iid uses μ⊗μ."""
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

    e4 = (1 - q) * prod(v0, w0, h_or_example4) + q * prod(v1, w1, h_or_example4)
    vm = np.concatenate([v0, v1])
    wm = np.concatenate([(1 - q) * w0, q * w1])
    eiid = prod(vm, wm, h_or_indep)
    r = ((1 - beta) * eiid + beta * e4) / eh
    return r, mean, eh


def main():
    rng = default_rng(20260817)
    hits = []
    # 3-atomic random, biased toward mean ~ c
    print("3-atomic", flush=True)
    worst3 = None
    n3 = 0
    for _ in range(30000):
        v = rng.random(3)
        # reject if mean far above C
        w = rng.dirichlet(np.ones(3))
        rec = ratio_atomic(v, w)
        if rec is None:
            continue
        r, mean, eh = rec
        if mean > C + 0.002:
            continue
        n3 += 1
        if worst3 is None or (mean <= C and r < worst3[0]) or (
            r < 1 and mean < (worst3[1] if worst3[0] < 1 else 1)
        ):
            if mean <= C and (worst3 is None or r < worst3[0]):
                worst3 = (r, mean, v.tolist(), w.tolist())
        if r < 1.0 and mean <= C:
            hits.append(("3atomic", r, mean, v.tolist(), w.tolist()))
    print("  checked", n3, "worst", worst3, "n_hits", len(hits), flush=True)

    print("2-mixture of 2-atomic", flush=True)
    worstm = None
    nm = 0
    hits_m = []
    for _ in range(40000):
        q = float(rng.random())
        v0 = rng.random(2)
        w0 = rng.dirichlet(np.ones(2))
        v1 = rng.random(2)
        w1 = rng.dirichlet(np.ones(2))
        rec = ratio_mixture(v0, w0, v1, w1, q)
        if rec is None:
            continue
        r, mean, eh = rec
        if mean > C + 0.002:
            continue
        nm += 1
        if mean <= C and (worstm is None or r < worstm[0]):
            worstm = (r, mean, q, v0.tolist(), w0.tolist(), v1.tolist(), w1.tolist())
        if r < 1.0 and mean <= C:
            hits_m.append((r, mean, q, v0.tolist(), w0.tolist(), v1.tolist(), w1.tolist()))
    print("  checked", nm, "worst", worstm, "n_hits", len(hits_m), flush=True)

    # local polish: start from {b,1} worst and add a small third atom
    print("perturb {b,1} with a third atom", flush=True)
    b0, a0 = 0.308, 0.108
    worstp = None
    for _ in range(15000):
        z = float(rng.random())
        eps = float(rng.random() * 0.08)
        # masses: (1-a0-eps) on b0, a0 on 1, eps on z
        if a0 + eps >= 0.999:
            continue
        v = [b0, 1.0, z]
        w = [1.0 - a0 - eps, a0, eps]
        rec = ratio_atomic(v, w)
        if rec is None:
            continue
        r, mean, eh = rec
        if mean <= C and (worstp is None or r < worstp[0]):
            worstp = (r, mean, v, w)

    # also perturb b,a themselves
    for _ in range(10000):
        b = b0 + float(rng.normal() * 0.02)
        a = a0 + float(rng.normal() * 0.02)
        z = float(rng.random())
        eps = abs(float(rng.normal() * 0.03))
        if not (0 < b < 1 and 0 < a < 0.5 and a + eps < 0.99):
            continue
        v = [b, 1.0, z]
        w = [1.0 - a - eps, a, eps]
        rec = ratio_atomic(v, w)
        if rec is None:
            continue
        r, mean, eh = rec
        if mean <= C and (worstp is None or r < worstp[0]):
            worstp = (r, mean, v, w)
    print("  worst perturb", worstp, flush=True)

    out = {
        "beta": BETA,
        "c": C,
        "n_3atomic": n3,
        "worst_3atomic": None
        if worst3 is None
        else {"ratio": worst3[0], "mean": worst3[1], "vals": worst3[2], "wts": worst3[3]},
        "n_hits_3": len(hits),
        "hits_3_head": hits[:8],
        "n_mixture": nm,
        "worst_mixture": None
        if worstm is None
        else {
            "ratio": worstm[0],
            "mean": worstm[1],
            "q": worstm[2],
            "v0": worstm[3],
            "w0": worstm[4],
            "v1": worstm[5],
            "w1": worstm[6],
        },
        "n_hits_mix": len(hits_m),
        "hits_mix_head": hits_m[:8],
        "worst_perturb": None
        if worstp is None
        else {"ratio": worstp[0], "mean": worstp[1], "vals": worstp[2], "wts": worstp[3]},
    }
    path = Path(__file__).resolve().parent / "hunt_mixtures.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
