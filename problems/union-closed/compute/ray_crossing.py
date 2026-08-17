"""1-D polish of the {b,1} ray: largest mean with mix ratio ≥ 1."""

from __future__ import annotations

import json
import math
from pathlib import Path

from entropy import h, h_or_example4, h_or_example5, h_or_indep, h_or_maxent


def terms(a, b):
    eh = (1.0 - a) * h(b)
    if eh <= 1e-18:
        return None
    eiid = (1.0 - a) ** 2 * h_or_indep(b, b)
    emax = (1.0 - 2.0 * a) * h_or_maxent(b, b)
    e4i = (1.0 - a) ** 2 * h_or_example4(b, b)
    e4c = (1.0 - a) * h_or_example4(b, b)
    e5i = (1.0 - a) ** 2 * h_or_example5(b, b)
    e5c = (1.0 - a) * h_or_example5(b, b)
    return eh, eiid, emax, min(e4i, e4c), min(e5i, e5c), a + (1.0 - a) * b


def ratio(a, b, w):
    t = terms(a, b)
    if t is None:
        return None
    eh, eiid, emax, e4, e5, mean = t
    num = w[0] * eiid + w[1] * emax + w[2] * e4 + w[3] * e5
    return num / eh, mean


WEIGHTS = {
    "iid": (1, 0, 0, 0),
    "sawin": (0.96439302, 0.03560698, 0, 0),
    "liu_ex5": (0.89994744, 0, 0, 0.10005256),
    "ex4_08": (0.92, 0, 0.08, 0),
    "ex4_10": (0.90, 0, 0.10, 0),
    "ex4_14": (0.86, 0, 0.14, 0),
    "ex4_18": (0.82, 0, 0.18, 0),
    "triple": (0.86, 0.0356, 0.1044, 0),
    "triple2": (0.84, 0.04, 0.12, 0),
    "triple3": (0.80, 0.05, 0.15, 0),
    "almost_ex4": (0.70, 0.05, 0.25, 0),
}


def scan(w, nb=2000, na=1500):
    # min ratio at various c thresholds; max mean with r<1
    thresholds = [0.38196601125, 0.38234553337, 0.38250, 0.38260,
                  0.38270908792, 0.38280, 0.38290, 0.38300, 0.38310, 0.38320]
    min_at = {c: 10.0 for c in thresholds}
    arg_at = {c: None for c in thresholds}
    max_bad = 0.0
    max_bad_pt = None
    # also track min ratio among r and the (a,b) that first crosses 1 as mean grows
    for i in range(nb + 1):
        b = 0.05 + 0.44 * i / nb
        amax = min(0.499, max(0.0, (0.40 - b) / (1.0 - b)))
        for j in range(na + 1):
            a = amax * j / na
            rr = ratio(a, b, w)
            if rr is None:
                continue
            r, mean = rr
            for c in thresholds:
                if mean <= c + 1e-15 and r < min_at[c]:
                    min_at[c] = r
                    arg_at[c] = (a, b, mean, r)
            if r < 1.0 and mean > max_bad:
                max_bad = mean
                max_bad_pt = (a, b, mean, r)
    return {
        "min_at": {str(c): {"ratio": min_at[c], "a": None if arg_at[c] is None else arg_at[c][0],
                           "b": None if arg_at[c] is None else arg_at[c][1],
                           "mean": None if arg_at[c] is None else arg_at[c][2]}
                   for c in thresholds},
        "max_mean_r_lt_1": max_bad,
        "max_bad_pt": None if max_bad_pt is None else {
            "a": max_bad_pt[0], "b": max_bad_pt[1],
            "mean": max_bad_pt[2], "ratio": max_bad_pt[3]
        },
    }


def main():
    out = {}
    for name, w in WEIGHTS.items():
        print(name, flush=True)
        out[name] = {"weights": w, **scan(w)}
        m = out[name]["min_at"]
        print("  r@c* ", m["0.38234553337"]["ratio"],
              "r@liu", m["0.38270908792"]["ratio"],
              "r@38280", m["0.3828"]["ratio"],
              "r@38310", m["0.3831"]["ratio"],
              "maxbad", out[name]["max_mean_r_lt_1"],
              flush=True)
    path = Path(__file__).resolve().parent / "ray_crossing.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
