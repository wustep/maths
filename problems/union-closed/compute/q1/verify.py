"""Official q1 checks: analytic crossing and mesh for pure Example 4.

Exit 0 only if:
  1. published Yu–Cambie c* and Liu c_5 match the quotes
  2. the 1-D critical point of (1-b)h(b) solves h(b)=(1-b)log2((1-b)/b)
     with residual < 1e-20 and second derivative of g negative
  3. analytic first-crossing > claimed 0.38304 > repo 0.38285 > Liu
  4. on a fine {b,1} mesh, pure Example 4 has min ratio ≥ 1 for every
     cell with mean ≤ 0.38304
  5. the same mesh at the old (β=1/5, 0.38285) still has min ratio ≥ 1
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import findroot, log, mp, mpf, nstr, sqrt

mp.dps = 80
LN2 = log(2)

CLAIMED_C = 0.38304
CLAIMED_BETA = 1.0
REPO_C = 0.38285
REPO_BETA = 0.20
LIU_QUOTE = 0.382709087918741
CAMBIE_QUOTE = 0.382345533366703


def hm(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return -(p * log(p) + (1 - p) * log(1 - p)) / LN2


def h_np(p):
    p = np.asarray(p, dtype=np.float64)
    out = np.zeros_like(p)
    m = (p > 0.0) & (p < 1.0)
    q = 1.0 - p[m]
    out[m] = -(p[m] * np.log(p[m]) + q * np.log(q)) / math.log(2.0)
    return out


def a_ex4_np(t):
    t = np.asarray(t, dtype=np.float64)
    out = np.zeros_like(t)
    out[t >= 0.5] = 1.0
    thresh = 1.0 - 1.0 / np.sqrt(2.0)
    mid = (t > thresh) & (t < 0.5)
    tm = t[mid]
    tb = 1.0 - tm
    num = 1.0 - 2.0 * tb * tb
    den = 2.0 * tm * tb
    out[mid] = np.sqrt(np.maximum(num, 0.0) / np.maximum(den, 1e-30))
    return out


def h_or_indep_np(b):
    return h_np(1.0 - (1.0 - b) ** 2)


def h_or_ex4_np(b):
    bb = 1.0 - b
    aa = a_ex4_np(b)
    pi0 = bb * bb + aa * aa * (bb - bb * bb)
    return h_np(1.0 - pi0)


def published():
    phi = (3 - sqrt(5)) / 2

    def cambie_eq(b):
        return hm(b) * (2 - hm(b)) - hm((1 - b) ** 2)

    b = findroot(cambie_eq, mpf("0.33"))
    a = 1 - hm(b) / hm((1 - b) ** 2)
    c_star = a + (1 - a) * b

    def liu_eq(x):
        x = mpf(x)
        return x**2 + x**2 * (1 + (1 - x) ** 2) - 1

    x = findroot(liu_eq, mpf("0.69"))
    p = hm(x) / hm(x**2)
    c5 = 1 - p * x
    return {
        "phi": float(phi),
        "c_star": float(c_star),
        "c_star_str": nstr(c_star, 24),
        "c5": float(c5),
        "c5_str": nstr(c5, 24),
        "c5_minus_quote": float(c5) - LIU_QUOTE,
        "c_star_minus_quote": float(c_star) - CAMBIE_QUOTE,
    }


def analytic_crossing():
    def eq(b):
        b = mpf(b)
        return hm(b) - (1 - b) * log((1 - b) / b) / LN2

    b = findroot(eq, mpf("0.2965"))
    hb = hm(b)
    c = 1 - (1 - b) * hb
    gpp = -2 * log((1 - b) / b) / LN2 - 1 / (b * LN2)
    return {
        "b_star": nstr(b, 24),
        "b_star_float": float(b),
        "crossing": nstr(c, 24),
        "crossing_float": float(c),
        "residual": float(eq(b)),
        "g_second_deriv": float(gpp),
    }


def min_ratio_below(beta: float, c: float, n_b=4500, n_a=3500):
    b = np.linspace(0.02, 0.499, n_b)
    a = np.linspace(0.0, 0.499, n_a)
    B, A = np.meshgrid(b, a, indexing="ij")
    mean = A + (1.0 - A) * B
    hb = h_np(b)[:, None]
    hid = h_or_indep_np(b)[:, None]
    hp = h_or_ex4_np(b)[:, None]
    eh = (1.0 - A) * hb
    eiid = (1.0 - A) ** 2 * hid
    ep = np.minimum((1.0 - A) ** 2 * hp, (1.0 - A) * hp)
    num = (1.0 - beta) * eiid + beta * ep
    ratio = np.divide(num, eh, out=np.full_like(num, 10.0), where=eh > 1e-16)
    keep = (mean <= c + 1e-15) & (eh > 1e-16)
    if not np.any(keep):
        return {"min_ratio": None, "n": 0}
    rmin = float(ratio[keep].min())
    idx = np.argmin(np.where(keep, ratio, 1e9))
    ib, ia = np.unravel_index(idx, mean.shape)
    return {
        "min_ratio": rmin,
        "n": int(keep.sum()),
        "at_mean": float(mean[ib, ia]),
        "at_a": float(A[ib, ia]),
        "at_b": float(B[ib, ia]),
    }


def first_crossing_mesh(beta: float, n_b=4500, n_a=3500):
    b = np.linspace(0.02, 0.499, n_b)
    a = np.linspace(0.0, 0.499, n_a)
    B, A = np.meshgrid(b, a, indexing="ij")
    mean = A + (1.0 - A) * B
    hb = h_np(b)[:, None]
    hid = h_or_indep_np(b)[:, None]
    hp = h_or_ex4_np(b)[:, None]
    eh = (1.0 - A) * hb
    eiid = (1.0 - A) ** 2 * hid
    ep = np.minimum((1.0 - A) ** 2 * hp, (1.0 - A) * hp)
    num = (1.0 - beta) * eiid + beta * ep
    ratio = np.divide(num, eh, out=np.full_like(num, 10.0), where=eh > 1e-16)
    bad = ratio < 1.0
    if not np.any(bad):
        return {"c": float(mean.max()), "n_bad": 0}
    idx = np.argmin(np.where(bad, mean, 1e9))
    ib, ia = np.unravel_index(idx, mean.shape)
    return {
        "c": float(mean[bad].min()),
        "a": float(A[ib, ia]),
        "b": float(B[ib, ia]),
        "ratio": float(ratio[ib, ia]),
        "n_bad": int(bad.sum()),
        "n_cells": int(mean.size),
    }


def main():
    pub = published()
    print("published", json.dumps({k: pub[k] for k in ("c_star", "c5")}, indent=2), flush=True)
    ana = analytic_crossing()
    print("analytic", json.dumps(ana, indent=2), flush=True)
    print("mesh first-crossing β=1 ...", flush=True)
    fc1 = first_crossing_mesh(1.0)
    print(fc1, flush=True)
    print("min ratio β=1 mean≤0.38304 ...", flush=True)
    mr = min_ratio_below(1.0, CLAIMED_C)
    print(mr, flush=True)
    print("min ratio β=1/5 mean≤0.38285 (repo replay) ...", flush=True)
    mr_old = min_ratio_below(REPO_BETA, REPO_C)
    print(mr_old, flush=True)

    checks = {
        "c_star_matches_cambie": abs(pub["c_star_minus_quote"]) < 1e-14,
        "c5_matches_liu": abs(pub["c5_minus_quote"]) < 1e-14,
        "critical_residual_tiny": abs(ana["residual"]) < 1e-20,
        "g_second_deriv_negative": ana["g_second_deriv"] < 0,
        "analytic_beats_claimed": ana["crossing_float"] > CLAIMED_C,
        "claimed_beats_repo": CLAIMED_C > REPO_C,
        "claimed_beats_liu": CLAIMED_C > LIU_QUOTE,
        "mesh_crossing_above_claimed": fc1["c"] > CLAIMED_C,
        "claimed_mesh_ratio_ge_1": mr["min_ratio"] is not None and mr["min_ratio"] >= 1.0,
        "repo_mesh_still_ok": mr_old["min_ratio"] is not None and mr_old["min_ratio"] >= 1.0,
    }
    report = {
        "claimed_c": CLAIMED_C,
        "claimed_beta": CLAIMED_BETA,
        "published": pub,
        "analytic": ana,
        "first_crossing_mesh_beta1": fc1,
        "min_ratio_claimed": mr,
        "min_ratio_repo_replay": mr_old,
        "checks": checks,
        "all_ok": all(checks.values()),
    }
    path = Path(__file__).resolve().parent / "certs" / "verify.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("checks", json.dumps(checks, indent=2))
    print("ALL_OK" if report["all_ok"] else "FAILED")
    if not report["all_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
