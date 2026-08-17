#!/usr/bin/env python3
"""Search I ∪ dI ∪ eI sum covers. Look for a linear family n,d,e ~ c ℓ², αℓ, βℓ."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, counting_lower

BEL = math.sqrt(8 / 3)
SQRT2 = math.sqrt(2)


def three_ap(n, d, e, ell):
    A = set(range(ell))
    for i in range(ell):
        A.add((i * d) % n)
        A.add((i * e) % n)
    return A


def search_ell(ell: int, ratio_cap: float = BEL - 1e-6):
    """n from counting-feasible down to the BEL threshold."""
    m_guess = 3 * ell
    n_max = m_guess * (m_guess + 1) // 2  # counting
    n_min = math.ceil((m_guess / ratio_cap) ** 2) if ratio_cap > 0 else ell * ell
    # keep the range modest
    n_max = min(n_max, 5 * ell * ell)
    n_min = max(n_min, 2 * ell * ell)
    hits = []
    # differences: try small integer multiples of ell and nearby
    d_cands = []
    for k in range(1, 8):
        d_cands.append(k * ell)
        d_cands.append(k * ell + 1)
        d_cands.append(k * ell - 1)
        d_cands.append(k * (ell + 1))
        d_cands.append(k * (ell - 1) if ell > 1 else 1)
    d_cands = sorted({d for d in d_cands if d > 1})
    for n in range(n_min, n_max + 1):
        need = counting_lower(n)
        if 3 * ell < need:
            continue
        for i, d in enumerate(d_cands):
            d %= n
            if d == 0:
                continue
            for e in d_cands[i + 1 :]:
                e %= n
                if e == 0 or e == d:
                    continue
                A = three_ap(n, d, e, ell)
                st = cover_stats(A, n)
                if st["ok"] and st["ratio"] < ratio_cap:
                    st["d"] = d
                    st["e"] = e
                    st["ell"] = ell
                    hits.append(st)
                    return hits  # first hit for this ell is enough
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ell-min", type=int, default=4)
    ap.add_argument("--ell-max", type=int, default=20)
    ap.add_argument("--out", default="compute/three_ap_hits.json")
    args = ap.parse_args()
    all_hits = []
    for ell in range(args.ell_min, args.ell_max + 1):
        hits = search_ell(ell)
        print(f"ell={ell} hits={len(hits)}", flush=True)
        if hits:
            h = hits[0]
            print(
                f"  n={h['n']} m={h['m']} ratio={h['ratio']:.5f} "
                f"d={h['d']} e={h['e']} counting={h['counting']}",
                flush=True,
            )
            all_hits.extend(hits)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(all_hits, f, indent=2)
    print(f"wrote {len(all_hits)} hits to {args.out}")


if __name__ == "__main__":
    main()
