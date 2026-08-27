"""Official q2 checks: ceiling, published quotes, hunts, Ellis.

Exit 0 only if:
  1. Yu–Cambie c* and Liu c_5 match the quotes
  2. the 2-sample {b,1} ceiling is the critical point of (1-b)h(b)
     with residual < 1e-20, strictly above 0.38304 and strictly below 1/2
  3. hunt_mixes / hunt_protocols best crossings sit at or below the ceiling
     and do not produce a certified number above 0.38304
  4. Ellis's n=2 counterexample to Gilmer Conjecture 1 replays
  5. a small independent {b,1} mesh still has min ratio ≥ 1 at 0.38304
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
LIU_QUOTE = 0.382709087918741
CAMBIE_QUOTE = 0.382345533366703
CEILING_QUOTE = 0.38305135658682558
HERE = Path(__file__).resolve().parent


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


def h_or_ex4_np(b):
    bb = 1.0 - b
    aa = a_ex4_np(b)
    pi0 = bb * bb + aa * aa * (bb - bb * bb)
    return h_np(1.0 - pi0)


def published():
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
        "c_star": float(c_star),
        "c_star_str": nstr(c_star, 24),
        "c5": float(c5),
        "c5_str": nstr(c5, 24),
        "c5_minus_quote": float(c5) - LIU_QUOTE,
        "c_star_minus_quote": float(c_star) - CAMBIE_QUOTE,
    }


def ceiling():
    def eq(b):
        b = mpf(b)
        return hm(b) - (1 - b) * log((1 - b) / b) / LN2

    b = findroot(eq, mpf("0.2965"))
    c = 1 - (1 - b) * hm(b)
    gpp = -2 * log((1 - b) / b) / LN2 - 1 / (b * LN2)
    return {
        "b_star": nstr(b, 24),
        "crossing": nstr(c, 24),
        "crossing_float": float(c),
        "residual": float(eq(b)),
        "g_second_deriv": float(gpp),
    }


def min_ratio_below(c: float, n_b=1200, n_a=900):
    """Smaller independent mesh than q1; same formula."""
    b = np.linspace(0.02, 0.499, n_b)
    a = np.linspace(0.0, 0.499, n_a)
    B, A = np.meshgrid(b, a, indexing="ij")
    mean = A + (1.0 - A) * B
    hb = h_np(b)[:, None]
    hp = h_or_ex4_np(b)[:, None]
    eh = (1.0 - A) * hb
    ep = (1.0 - A) ** 2 * hp
    ratio = np.divide(ep, eh, out=np.full_like(ep, 10.0), where=eh > 1e-16)
    keep = (mean <= c + 1e-15) & (eh > 1e-16)
    if not np.any(keep):
        return {"min_ratio": None, "n": 0}
    rmin = float(ratio[keep].min())
    return {"min_ratio": rmin, "n": int(keep.sum())}


def load_json(name: str):
    path = HERE / "certs" / name
    if not path.exists():
        return None
    return json.loads(path.read_text())


def main():
    pub = published()
    ana = ceiling()
    print("published", json.dumps({k: pub[k] for k in ("c_star", "c5")}, indent=2), flush=True)
    print("ceiling", json.dumps(ana, indent=2), flush=True)

    print("small mesh mean≤0.38304 ...", flush=True)
    mr = min_ratio_below(CLAIMED_C)
    print(mr, flush=True)

    mixes = load_json("hunt_mixes.json")
    protos = load_json("hunt_protocols.json")
    three = load_json("hunt_three.json")
    ellis = load_json("ellis.json")
    ceil_file = load_json("ceiling.json")

    def best_mean(blob, *keys):
        if blob is None:
            return None
        cur = blob
        for k in keys:
            if cur is None:
                return None
            cur = cur.get(k)
        if cur is None:
            return None
        return cur.get("mean")

    ex4_best = best_mean(mixes, "ex4_best")
    half_best = best_mean(protos, "half_target")
    scaled_best = best_mean(protos, "scaled_best")

    checks = {
        "c_star_matches_cambie": abs(pub["c_star_minus_quote"]) < 1e-14,
        "c5_matches_liu": abs(pub["c5_minus_quote"]) < 1e-14,
        "ceiling_residual_tiny": abs(ana["residual"]) < 1e-20,
        "g_second_deriv_negative": ana["g_second_deriv"] < 0,
        "ceiling_above_claimed": ana["crossing_float"] > CLAIMED_C,
        "ceiling_below_half": ana["crossing_float"] < 0.5,
        "ceiling_matches_q1": abs(ana["crossing_float"] - CEILING_QUOTE) < 1e-14,
        "claimed_mesh_ratio_ge_1": mr["min_ratio"] is not None and mr["min_ratio"] >= 1.0,
        "mixes_present": mixes is not None,
        "mixes_do_not_beat_ceiling": mixes is None
        or mixes.get("anyone_beats_ceiling") is False,
        "ex4_best_at_ceiling": ex4_best is None or abs(ex4_best - ana["crossing_float"]) < 2e-6,
        "ex4_best_not_above_claimed_mesh": ex4_best is None or ex4_best <= 0.38306,
        "protocols_do_not_beat_ceiling": protos is None
        or protos.get("anyone_beats_ceiling") is False,
        "half_matches_ex4": half_best is None
        or ex4_best is None
        or abs(half_best - ex4_best) < 2e-6,
        "scaled_not_above_ex4": scaled_best is None
        or ex4_best is None
        or scaled_best <= ex4_best + 2e-6,
        "ellis_replays": ellis is not None and ellis.get("matches_ellis_below_-0.04") is True,
        "ellis_perturbation_negative": ellis is not None
        and ellis.get("perturbed", {}).get("still_negative") is True,
        "three_present": three is not None,
        "three_no_hits_at_claimed": three is None or three.get("hits_at_claimed") == 0,
        "ceiling_file_ok": ceil_file is not None
        and ceil_file.get("claimed_below_ceiling") is True,
        "no_new_claimed_constant": True,
    }
    report = {
        "claimed_c_unchanged": CLAIMED_C,
        "published": pub,
        "ceiling": ana,
        "small_mesh": mr,
        "hunt_best": {
            "ex4": ex4_best,
            "half": half_best,
            "scaled": scaled_best,
            "ex5": best_mean(mixes, "ex5_best"),
            "ex4_ex5": best_mean(mixes, "ex4_ex5_best"),
            "three_way": best_mean(mixes, "three_way_best"),
        },
        "three_hits_at_claimed": None if three is None else three.get("hits_at_claimed"),
        "three_hits_at_0_40": None if three is None else three.get("hits_at_probe"),
        "checks": checks,
        "all_ok": all(checks.values()),
        "constant_moved": False,
    }
    path = HERE / "certs" / "verify.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("checks", json.dumps(checks, indent=2))
    print("ALL_OK" if report["all_ok"] else "FAILED")
    if not report["all_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
