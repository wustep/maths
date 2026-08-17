#!/usr/bin/env python3
"""Exact balance of products of three chains C_a × C_b × C_c.

Olson–Sagan (Order 2018) Question 3.9: is every product of k≥3 chains
1/3-balanced? Rectangles (k=2) and C2×C2×Cn (almost-twins) are already
known. This script computes δ and the distinguished pair
    u = (1,0,0), v = (0,1,0)
for every non-chain box with abc ≤ 24 (bitmask limit ~ n=24 is comfortable
at a few million ideals).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from posetlib import (
    Poset,
    balance,
    count_le_ideals,
    count_le_mins,
    pair_counts_fb,
    product_of_chains,
)


def cell_index(dims, coords):
    idx = 0
    for d, c in zip(dims, coords):
        idx = idx * d + c
    return idx


def box_report(dims):
    P = product_of_chains(dims)
    e1 = count_le_mins(P)
    e2 = count_le_ideals(P)
    if e1 != e2:
        raise AssertionError(f"{dims}: {e1} vs {e2}")
    e, C = pair_counts_fb(P)
    if e != e1:
        raise AssertionError(f"{dims}: fb e={e} vs {e1}")
    num, den, _, pair, pairs = balance(P, C, e)
    g = _gcd(num, den)
    # distinguished pair u=(1,0,0), v=(0,1,0) when a,b ≥ 2
    dist = None
    if dims[0] >= 2 and dims[1] >= 2:
        u = cell_index(dims, (1, 0) + (0,) * (len(dims) - 2))
        v = cell_index(dims, (0, 1) + (0,) * (len(dims) - 2))
        a, b = C[u][v], C[v][u]
        dist = {
            "u": u,
            "v": v,
            "e_uv": a,
            "e_vu": b,
            "min": min(a, b),
            "frac": [min(a, b) // _gcd(min(a, b), e), e // _gcd(min(a, b), e)],
        }
    return {
        "dims": list(dims),
        "n": P.n,
        "e": e,
        "delta": [num // g, den // g],
        "best_pair": list(pair) if pair else None,
        "distinguished": dist,
        "n_incomp": len(pairs),
    }


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def main():
    rows = []
    # all a≤b≤c, a*b*c ≤ 24, a≥1, skip chains (two of a,b,c equal 1)
    boxes = []
    for a in range(1, 9):
        for b in range(a, 9):
            for c in range(b, 13):
                n = a * b * c
                if n > 24:
                    continue
                if a == 1 and b == 1:
                    continue  # chain
                boxes.append((a, b, c))
    print(f"{len(boxes)} boxes")
    for dims in boxes:
        rec = box_report(dims)
        rows.append(rec)
        dlt = rec["delta"]
        dist = rec["distinguished"]
        extra = ""
        if dist:
            extra = f"  uv={dist['frac'][0]}/{dist['frac'][1]}"
        print(
            f"  C{dims[0]}xC{dims[1]}xC{dims[2]} n={rec['n']} e={rec['e']}"
            f" δ={dlt[0]}/{dlt[1]}{extra}"
        )
        # flag any box that fails 1/3
        if dlt[0] * 3 < dlt[1]:
            print("    *** BELOW 1/3 ***")

    path = Path(__file__).resolve().parent / "three_chains.json"
    path.write_text(json.dumps({"boxes": rows}, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
