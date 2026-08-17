#!/usr/bin/env python3
"""Hunt a 3-AP family n = αℓ² + βℓ + γ, d = pℓ + q, e = rℓ + s
that is a sum cover for every large ℓ. That would be an infinite family.

We scan small integer coefficients and require success on a run of ℓ.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats

BEL = math.sqrt(8 / 3)


def three_ap(n, d, e, ell):
    A = set(range(ell))
    for i in range(ell):
        A.add((i * (d % n)) % n)
        A.add((i * (e % n)) % n)
    return A


def test_formula(n_coef, d_coef, e_coef, ells):
    """n_coef = (A,B,C) meaning n = A ℓ² + B ℓ + C, etc for d,e linear."""
    A, B, C = n_coef
    p, q = d_coef
    r, s = e_coef
    rows = []
    for ell in ells:
        n = A * ell * ell + B * ell + C
        if n <= 2 * ell:
            return None
        d = p * ell + q
        e = r * ell + s
        if d % n == 0 or e % n == 0 or d % n == e % n:
            return None
        st = cover_stats(three_ap(n, d, e, ell), n)
        st.update(ell=ell, d=d, e=e, n_coef=n_coef, d_coef=d_coef, e_coef=e_coef)
        if not st["ok"]:
            return None
        rows.append(st)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ell-min", type=int, default=6)
    ap.add_argument("--ell-max", type=int, default=10)
    ap.add_argument("--out", default="compute/linear_family_hits.json")
    args = ap.parse_args()
    ells = list(range(args.ell_min, args.ell_max + 1))
    # n ≈ κ ℓ² with κ in {3,4,5} to sit between counting (≤4.5) and BEL (>3.375)
    n_coefs = []
    for A in (3, 4, 5):
        for B in range(-4, 5):
            for C in range(-3, 4):
                n_coefs.append((A, B, C))
    d_lin = []
    for p in range(1, 6):
        for q in range(-2, 3):
            d_lin.append((p, q))
    hits = []
    tried = 0
    for nc in n_coefs:
        for i, dc in enumerate(d_lin):
            for ec in d_lin[i + 1 :]:
                tried += 1
                rows = test_formula(nc, dc, ec, ells)
                if not rows:
                    continue
                ratios = [r["ratio"] for r in rows]
                mx = max(ratios)
                if mx < BEL:
                    rec = {
                        "n_coef": nc,
                        "d_coef": dc,
                        "e_coef": ec,
                        "ells": ells,
                        "ratios": ratios,
                        "max_ratio": mx,
                        "ms": [r["m"] for r in rows],
                        "ns": [r["n"] for r in rows],
                    }
                    print("HIT", rec, flush=True)
                    hits.append(rec)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"tried": tried, "hits": hits}, f, indent=2)
    print(f"tried={tried} hits={len(hits)} wrote {args.out}")


if __name__ == "__main__":
    main()
