"""Replayable checks for the claimed ray improvement.

Exit 0 only if:
  1. independently recomputed Yu–Cambie c* and Liu c_5 match the quotes
  2. first-crossing of iid+Example-5 at β=1/10 is ≥ Liu's quote minus 2e-5
     (mesh discretisation)
  3. first-crossing of iid+Example-4 at β=1/5 is strictly larger than Liu's c_5
  4. on a fine {b,1} mesh, iid+Example-4 at β=1/5 has min ratio ≥ 1
     for every cell with mean ≤ CLAIMED_C
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import findroot, log, mp, mpf, nstr, sqrt

mp.dps = 60
LN2 = log(2)

CLAIMED_C = 0.38285
CLAIMED_BETA = 0.20
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


def h_or_ex5_np(b):
    bb = 1.0 - b
    pi0 = bb * bb + (bb * b) ** 2
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
        "b_star": float(b),
        "a_star": float(a),
        "liu_x": float(x),
        "liu_p": float(p),
        "c5": float(c5),
        "c5_str": nstr(c5, 24),
        "c5_minus_quote": float(c5) - LIU_QUOTE,
        "c_star_minus_quote": float(c_star) - CAMBIE_QUOTE,
    }


def first_crossing(proto: str, beta: float, n_b=4500, n_a=3500):
    b = np.linspace(0.02, 0.499, n_b)
    a = np.linspace(0.0, 0.499, n_a)
    B, A = np.meshgrid(b, a, indexing="ij")
    mean = A + (1.0 - A) * B
    hb = h_np(b)[:, None]
    hid = h_or_indep_np(b)[:, None]
    hp = h_or_ex4_np(b)[:, None] if proto == "ex4" else h_or_ex5_np(b)[:, None]
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


def min_ratio_below(proto: str, beta: float, c: float, n_b=4500, n_a=3500):
    b = np.linspace(0.02, 0.499, n_b)
    a = np.linspace(0.0, 0.499, n_a)
    B, A = np.meshgrid(b, a, indexing="ij")
    mean = A + (1.0 - A) * B
    hb = h_np(b)[:, None]
    hid = h_or_indep_np(b)[:, None]
    hp = h_or_ex4_np(b)[:, None] if proto == "ex4" else h_or_ex5_np(b)[:, None]
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


def main():
    pub = published()
    print("published", json.dumps({k: pub[k] for k in ("c_star", "c5", "c5_minus_quote")}, indent=2))
    print("first-crossing Example-5 β=0.10 ...", flush=True)
    fc5 = first_crossing("ex5", 0.10)
    print(fc5, flush=True)
    print("first-crossing Example-4 β=0.20 ...", flush=True)
    fc4 = first_crossing("ex4", CLAIMED_BETA)
    print(fc4, flush=True)
    print("min ratio Example-4 β=0.20 mean≤claimed ...", flush=True)
    mr = min_ratio_below("ex4", CLAIMED_BETA, CLAIMED_C)
    print(mr, flush=True)

    checks = {
        "c_star_matches_cambie": abs(pub["c_star_minus_quote"]) < 1e-14,
        "c5_matches_liu": abs(pub["c5_minus_quote"]) < 1e-14,
        "ex5_crossing_near_liu": fc5["c"] >= LIU_QUOTE - 2e-5,
        "ex4_crossing_beats_liu": fc4["c"] > LIU_QUOTE + 5e-5,
        "claimed_below_ex4_crossing": CLAIMED_C < fc4["c"],
        "claimed_mesh_ratio_ge_1": mr["min_ratio"] is not None and mr["min_ratio"] >= 1.0,
        "claimed_beats_liu": CLAIMED_C > LIU_QUOTE,
    }
    report = {
        "claimed_c": CLAIMED_C,
        "claimed_beta": CLAIMED_BETA,
        "published": pub,
        "first_crossing_ex5_beta010": fc5,
        "first_crossing_ex4_beta020": fc4,
        "min_ratio_claimed": mr,
        "checks": checks,
        "all_ok": all(checks.values()),
    }
    path = Path(__file__).resolve().parent / "verify.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("checks", json.dumps(checks, indent=2))
    print("ALL_OK" if report["all_ok"] else "FAILED")
    if not report["all_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
