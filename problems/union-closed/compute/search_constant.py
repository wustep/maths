"""Search worst-case entropy ratios for protocol mixtures.

Goal: find the largest c such that a mixture of
  iid  /  Sawin max-entropy  /  Example-4 CIID  /  Example-5 CIID
stays ≥ 1 for every tested atomic / 2-mixture law with mean ≤ c.

A value strictly above Liu's 0.382709, independently replayed, would be
a candidate dent.  Failure is recorded as residue.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
from numpy.random import default_rng

from entropy import (
    a_example4,
    h,
    h_or_example4,
    h_or_example5,
    h_or_indep,
    h_or_maxent,
    pi_example4,
    pi_example5,
)

LN2 = math.log(2)


def h_np(p):
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p)
    m = (p > 0.0) & (p < 1.0)
    q = 1.0 - p[m]
    out[m] = -(p[m] * np.log(p[m]) + q * np.log(q)) / LN2
    return out


def two_atomic_stats(x, y, p):
    """Return mean, Eh, E_iid, E_maxent, E_ex4_indep, E_ex5_indep."""
    w = np.array([p, 1.0 - p])
    v = np.array([x, y])
    mean = p * x + (1.0 - p) * y
    eh = p * h(x) + (1.0 - p) * h(y)
    eiid = 0.0
    emax = 0.0
    e4 = 0.0
    e5 = 0.0
    for i in range(2):
        for j in range(2):
            ww = w[i] * w[j]
            eiid += ww * h_or_indep(v[i], v[j])
            emax += ww * h_or_maxent(v[i], v[j])
            e4 += ww * h_or_example4(v[i], v[j])
            e5 += ww * h_or_example5(v[i], v[j])
    return mean, eh, eiid, emax, e4, e5


def maxent_worst_two_atomic(x, y, p):
    """Sawin-style worst symmetric coupling of a 2-point law.

    Put as little mass as possible on (1-ish, 1-ish) pairs: the
    negatively-correlated coupling with P(large, large) minimised.
    For support {x,y} with x ≤ y, the greedy min-entropy-of-OR coupling
    is the one Sawin uses on the atoms, i.e. Fréchet–Hoeffding lower
    bound / 'maxent of the OR' per atom pair is already in h_or_maxent
    *if the pair (S,R) is an arbitrary coupling*.  The expectation is
    then the inf over couplings of E[h_or_maxent(S,R)].

    For two atoms the symmetric couplings are a 1-parameter family:
    let a = P(S=y) (assume y ≥ x), u = P(S=y, R=y) ∈ [max(0, 2a-1), a].
    """
    # Order so y is the larger label only for naming; works for any x,y.
    a = p  # P(S = x)
    # u = P(both x)
    lo = max(0.0, 2.0 * a - 1.0)
    hi = a
    best = None
    # sample the interval densely + endpoints
    for u in np.linspace(lo, hi, 17):
        # P(x,x)=u, P(x,y)=P(y,x)=a-u, P(y,y)=1-2a+u
        pxx, pxy, pyy = u, a - u, 1.0 - 2.0 * a + u
        val = (
            pxx * h_or_maxent(x, x)
            + 2.0 * pxy * h_or_maxent(x, y)
            + pyy * h_or_maxent(y, y)
        )
        if best is None or val < best:
            best = val
    return best


def ciid_c3_worst_two_atomic(x, y, p, proto="ex4"):
    """Inf of E[h(Π)] over C3 couplings of a 2-point law.

    C3 on two atoms is P(x,x) ∈ [p², p]  (mixtures of iid).
    The other cells are then determined by the marginals:
      P(x,y)=P(y,x)=p-P(xx), P(y,y)=1-2p+P(xx).
    """
    fn = h_or_example4 if proto == "ex4" else h_or_example5
    lo = p * p
    hi = p
    best = None
    for u in np.linspace(lo, hi, 17):
        pxx, pxy, pyy = u, p - u, 1.0 - 2.0 * p + u
        val = pxx * fn(x, x) + 2.0 * pxy * fn(x, y) + pyy * fn(y, y)
        if best is None or val < best:
            best = val
    return best


def ratio_two_atomic(x, y, p, w_iid, w_max, w_ex4, w_ex5):
    mean, eh, eiid, emax_prod, e4_prod, e5_prod = two_atomic_stats(x, y, p)
    if eh <= 1e-15:
        return mean, 10.0, eh
    emax = maxent_worst_two_atomic(x, y, p)
    e4 = ciid_c3_worst_two_atomic(x, y, p, "ex4")
    e5 = ciid_c3_worst_two_atomic(x, y, p, "ex5")
    num = w_iid * eiid + w_max * emax + w_ex4 * e4 + w_ex5 * e5
    return mean, num / eh, eh


def scan_two_atomic(w_iid, w_max, w_ex4, w_ex5, n=90, p_grid=60):
    """Dense scan of 2-atomic laws.  Returns list of (ratio, mean, x, y, p)."""
    xs = np.linspace(0.0, 1.0, n)
    ps = np.linspace(0.0, 1.0, p_grid)
    recs = []
    for i, x in enumerate(xs):
        for y in xs[i:]:  # y ≥ x to cut symmetry
            for p in ps:
                mean, r, eh = ratio_two_atomic(x, y, p, w_iid, w_max, w_ex4, w_ex5)
                if eh <= 1e-15:
                    continue
                recs.append((r, mean, float(x), float(y), float(p)))
    recs.sort(key=lambda t: t[0])
    return recs


def random_two_atomic(rng, w_iid, w_max, w_ex4, w_ex5, n=20000):
    recs = []
    for _ in range(n):
        x, y = float(rng.random()), float(rng.random())
        p = float(rng.random())
        mean, r, eh = ratio_two_atomic(x, y, p, w_iid, w_max, w_ex4, w_ex5)
        if eh <= 1e-15:
            continue
        recs.append((r, mean, x, y, p))
    recs.sort(key=lambda t: t[0])
    return recs


def three_atomic_random(rng, w_iid, w_max, w_ex4, w_ex5, n=8000):
    recs = []
    for _ in range(n):
        v = rng.random(3)
        w = rng.random(3)
        w = w / w.sum()
        mean = float(np.dot(v, w))
        eh = float(sum(w[i] * h(float(v[i])) for i in range(3)))
        if eh <= 1e-15:
            continue
        eiid = emax = e4 = e5 = 0.0
        for i in range(3):
            for j in range(3):
                ww = float(w[i] * w[j])
                eiid += ww * h_or_indep(float(v[i]), float(v[j]))
                emax += ww * h_or_maxent(float(v[i]), float(v[j]))
                e4 += ww * h_or_example4(float(v[i]), float(v[j]))
                e5 += ww * h_or_example5(float(v[i]), float(v[j]))
        num = w_iid * eiid + w_max * emax + w_ex4 * e4 + w_ex5 * e5
        recs.append((num / eh, mean, v.tolist(), w.tolist()))
    recs.sort(key=lambda t: t[0])
    return recs


def mixture_two_two(rng, w_iid, w_ex4, w_ex5, n=8000):
    """2-mixture of 2-atomic laws (Liu 9D special case, random slice)."""
    recs = []
    for _ in range(n):
        q = float(rng.random())
        # P0, P1 each 2-atomic
        a0, b0 = float(rng.random()), float(rng.random())
        p0 = float(rng.random())
        a1, b1 = float(rng.random()), float(rng.random())
        p1 = float(rng.random())

        def atoms(a, b, p):
            return np.array([a, b]), np.array([p, 1.0 - p])

        v0, w0 = atoms(a0, b0, p0)
        v1, w1 = atoms(a1, b1, p1)
        # marginal
        mean = (1 - q) * float(np.dot(v0, w0)) + q * float(np.dot(v1, w1))
        eh = (1 - q) * float(sum(w0[i] * h(float(v0[i])) for i in range(2))) + q * float(
            sum(w1[i] * h(float(v1[i])) for i in range(2))
        )
        if eh <= 1e-15:
            continue

        def prod(v, w, fn):
            s = 0.0
            for i in range(2):
                for j in range(2):
                    s += float(w[i] * w[j]) * fn(float(v[i]), float(v[j]))
            return s

        # iid term uses the *marginal* product
        vm = np.concatenate([v0, v1])
        wm = np.concatenate([(1 - q) * w0, q * w1])
        eiid = 0.0
        for i in range(4):
            for j in range(4):
                eiid += float(wm[i] * wm[j]) * h_or_indep(float(vm[i]), float(vm[j]))
        e4 = (1 - q) * prod(v0, w0, h_or_example4) + q * prod(v1, w1, h_or_example4)
        e5 = (1 - q) * prod(v0, w0, h_or_example5) + q * prod(v1, w1, h_or_example5)
        # no maxent here (C2 is not a 2-mixture)
        wsum = w_iid + w_ex4 + w_ex5
        if wsum <= 0:
            continue
        num = (w_iid * eiid + w_ex4 * e4 + w_ex5 * e5) / wsum
        # renormalise weights among {iid, ex4, ex5}
        recs.append((num / eh, mean, q, (a0, b0, p0), (a1, b1, p1)))
    recs.sort(key=lambda t: t[0])
    return recs


WEIGHT_CONFIGS = {
    "iid_only": (1.0, 0.0, 0.0, 0.0),
    "sawin_yu": (1.0 - 0.03560698, 0.03560698, 0.0, 0.0),
    "liu_ex5_beta010": (0.89994744, 0.0, 0.0, 0.10005256),
    "ex4_beta010": (0.90, 0.0, 0.10, 0.0),
    "ex4_beta020": (0.80, 0.0, 0.20, 0.0),
    "triple_small_ex4": (0.90, 0.03, 0.07, 0.0),
    "triple_small_ex5": (0.87, 0.03, 0.0, 0.10),
    "triple_balanced": (0.85, 0.05, 0.05, 0.05),
    "ex4_heavy": (0.70, 0.05, 0.25, 0.0),
}


def summarise(recs, c_cutoffs):
    out = {}
    if not recs:
        return out
    out["global_min_ratio"] = recs[0][0]
    out["at_mean"] = recs[0][1]
    out["n"] = len(recs)
    for c in c_cutoffs:
        sub = [r for r in recs if r[1] <= c + 1e-12]
        if sub:
            out[f"min_ratio_mean_le_{c:.6f}"] = sub[0][0]
            out[f"arg_mean_le_{c:.6f}"] = sub[0][1]
        else:
            out[f"min_ratio_mean_le_{c:.6f}"] = None
    # largest mean among those with ratio ≤ 1
    bad = [r for r in recs if r[0] <= 1.0]
    if bad:
        worst_c = max(bad, key=lambda t: t[1])
        out["max_mean_with_ratio_le_1"] = worst_c[1]
        out["that_ratio"] = worst_c[0]
    else:
        out["max_mean_with_ratio_le_1"] = None
    return out


def main():
    rng = default_rng(20260817)
    cutoffs = [
        0.381966011250105,
        0.382345533366703,
        0.38250,
        0.38260,
        0.382709087918735,
        0.38280,
        0.38300,
        0.39000,
        0.40000,
    ]
    report = {"configs": {}, "t0": time.time()}
    for name, weights in WEIGHT_CONFIGS.items():
        t1 = time.time()
        print(f"=== {name} {weights} ===", flush=True)
        scan = scan_two_atomic(*weights, n=70, p_grid=50)
        rnd = random_two_atomic(rng, *weights, n=12000)
        th = three_atomic_random(rng, *weights, n=4000)
        mix = []
        if weights[1] == 0.0:
            mix = mixture_two_two(rng, weights[0], weights[2], weights[3], n=4000)
        # worst 15 two-atomic
        top = [
            {"ratio": r, "mean": m, "x": x, "y": y, "p": p}
            for r, m, x, y, p in scan[:12]
        ]
        entry = {
            "weights": {
                "iid": weights[0],
                "maxent": weights[1],
                "ex4": weights[2],
                "ex5": weights[3],
            },
            "two_atomic_grid": summarise(scan, cutoffs),
            "two_atomic_random": summarise(rnd, cutoffs),
            "three_atomic_random": summarise(th, cutoffs),
            "mixture_2x2": summarise(mix, cutoffs) if mix else None,
            "worst_two_atomic": top,
            "seconds": time.time() - t1,
        }
        report["configs"][name] = entry
        ta = entry["two_atomic_grid"]
        print(
            "  grid min",
            ta.get("global_min_ratio"),
            "at mean",
            ta.get("at_mean"),
            "max mean with r≤1",
            ta.get("max_mean_with_ratio_le_1"),
            flush=True,
        )
        print(
            "  r@0.38271",
            ta.get("min_ratio_mean_le_0.382709"),
            "r@0.38235",
            ta.get("min_ratio_mean_le_0.382346"),
            flush=True,
        )

    report["elapsed"] = time.time() - report["t0"]
    out = Path(__file__).resolve().parent / "search_constant.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out, "in", report["elapsed"], "s")


if __name__ == "__main__":
    main()
