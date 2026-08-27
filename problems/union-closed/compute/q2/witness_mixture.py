"""Constructed 2-mixture that pure Example 4 fails at mean 0.38304.

P0 is the {b*,1} law with mean 0.45.  P1 is a point mass at 0.01.
Weights make the mixture mean equal the claimed ray constant.
The CIID (2-mixture-of-products) Example-4 ratio is < 1.

This does not move the {b,1} ray number.  It shows that β=1 does
not extend off the ray to every 2-mixture, which is why Liu kept a
positive iid weight.  A little iid restores ratio > 1 on this
witness and drops the {b,1} first-crossing below 0.38304.

Replay: python3 witness_mixture.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import h, h_or_example4, h_or_example5, h_or_indep  # noqa: E402

CLAIMED = 0.38304
BSTAR = 0.29649392356933757
MEAN0 = 0.45
ATOM1 = 0.01


def pack(vals, wts, fn):
    wsum = sum(wts)
    wts = [w / wsum for w in wts]
    mean = sum(v * w for v, w in zip(vals, wts))
    eh = sum(w * h(v) for v, w in zip(vals, wts))
    eor = 0.0
    for i, vi in enumerate(vals):
        for j, vj in enumerate(vals):
            eor += wts[i] * wts[j] * fn(vi, vj)
    return mean, eh, eor


def main():
    a = (MEAN0 - BSTAR) / (1.0 - BSTAR)
    v0, w0 = [BSTAR, 1.0], [1.0 - a, a]
    v1, w1 = [ATOM1], [1.0]
    m0, eh0, e40 = pack(v0, w0, h_or_example4)
    _, _, e50 = pack(v0, w0, h_or_example5)
    _, _, ei0 = pack(v0, w0, h_or_indep)
    m1, eh1, e41 = pack(v1, w1, h_or_example4)
    _, _, e51 = pack(v1, w1, h_or_example5)
    _, _, ei1 = pack(v1, w1, h_or_indep)
    q = (m0 - CLAIMED) / (m0 - m1)
    mean = (1.0 - q) * m0 + q * m1
    eh = (1.0 - q) * eh0 + q * eh1
    e4 = (1.0 - q) * e40 + q * e41
    e5 = (1.0 - q) * e50 + q * e51

    # product μ⊗μ
    vals = [BSTAR, 1.0, ATOM1]
    wts = [(1.0 - q) * (1.0 - a), (1.0 - q) * a, q]
    _, eh_mu, ei_mu = pack(vals, wts, h_or_indep)
    _, _, e4_mu = pack(vals, wts, h_or_example4)

    r_ciid4 = e4 / eh
    r_ciid5 = e5 / eh
    r_prod_iid = ei_mu / eh_mu
    r_liu = (0.9 * ei_mu + 0.1 * e5) / eh
    r_q1 = (0.8 * ei_mu + 0.2 * e4) / eh

    report = {
        "claimed_c": CLAIMED,
        "P0": {"atoms": v0, "weights": w0, "mean": m0, "ratio_ex4": e40 / eh0},
        "P1": {"atoms": v1, "weights": w1, "mean": m1, "ratio_ex4": e41 / eh1},
        "q": q,
        "mixture_mean": mean,
        "ciid_example4_ratio": r_ciid4,
        "ciid_example5_ratio": r_ciid5,
        "product_iid_ratio": r_prod_iid,
        "liu_beta_0_10_ex5_ratio": r_liu,
        "repo_beta_0_20_ex4_ratio": r_q1,
        "product_ex4_ratio": e4_mu / eh_mu,
        "fails_pure_ex4": r_ciid4 < 1.0,
        "mean_matches_claimed": abs(mean - CLAIMED) < 1e-12,
        "iid_weight_saves": r_liu > 1.0 and r_q1 > 1.0,
        "note": (
            "pure Example 4 on this 2-mixture is below 1.  "
            "The {b,1} ray claim is a single 2-atomic law and is untouched.  "
            "Liu's positive iid weight saves the witness and lowers the ray."
        ),
    }
    path = Path(__file__).resolve().parent / "certs" / "mixture_witness.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["fails_pure_ex4"] or not report["mean_matches_claimed"]:
        raise SystemExit(1)
    if not report["iid_weight_saves"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
