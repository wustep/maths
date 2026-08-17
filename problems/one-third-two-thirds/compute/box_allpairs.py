#!/usr/bin/env python3
"""All incomparable-pair probabilities in a 3-chain box, via plane-partition DP.

For each incomparable pair (p,q) we count e(P+p<q) by the same recurrence as
box_dp.py, restricted to ideals of the enlarged poset.
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from math import gcd
from pathlib import Path

from box_dp import (
    contains_cell,
    enumerate_plane_partitions,
    maxima_of,
    remove_cell,
)


def box_all_pairs(a: int, b: int, c: int):
    cells = [(x, y, z) for x in range(a) for y in range(b) for z in range(c)]
    n = len(cells)
    # comparable?
    def le(p, q):
        return p[0] <= q[0] and p[1] <= q[1] and p[2] <= q[2]

    incomp = [
        (p, q)
        for i, p in enumerate(cells)
        for q in cells[i + 1 :]
        if not le(p, q) and not le(q, p)
    ]

    full = tuple([c] * (a * b))
    pps = enumerate_plane_partitions(a, b, c)
    assert full in set(pps)

    @lru_cache(maxsize=None)
    def F(h):
        if all(t == 0 for t in h):
            return 1
        tot = 0
        for x, y, z in maxima_of(h, a, b, c):
            tot += F(remove_cell(h, a, b, x, y))
        return tot

    e = F(full)

    def e_add(p, q):
        """e(P + p<q)."""

        def in_I(h, cell):
            x, y, z = cell
            return h[x * b + y] > z

        def is_ideal(h):
            return (not in_I(h, q)) or in_I(h, p)

        def maxima_Q(h):
            out = []
            for x, y, z in maxima_of(h, a, b, c):
                if (x, y, z) == p and in_I(h, q):
                    continue
                out.append((x, y, z))
            return out

        @lru_cache(maxsize=None)
        def FQ(h):
            if all(t == 0 for t in h):
                return 1
            tot = 0
            for x, y, z in maxima_Q(h):
                tot += FQ(remove_cell(h, a, b, x, y))
            return tot

        val = FQ(full)
        FQ.cache_clear()
        return val

    best = (0, 1, None, None, 0, e)
    rows = []
    for p, q in incomp:
        uv = e_add(p, q)
        vu = e - uv
        mn = min(uv, vu)
        if mn * best[1] > best[0] * e:
            best = (mn, e, p, q, uv, vu)
        rows.append((p, q, uv, vu, mn))

    g = gcd(best[0], best[1])
    return {
        "dims": [a, b, c],
        "n": n,
        "e": e,
        "n_incomp": len(incomp),
        "delta": [best[0] // g, best[1] // g],
        "delta_float": best[0] / best[1],
        "best_pair": [list(best[2]), list(best[3]), best[4], best[5]],
        # keep only pairs with min/e >= 1/3 - 1e-15, and the worst few
        "good_pairs": [
            {
                "p": list(p),
                "q": list(q),
                "uv": uv,
                "vu": vu,
                "min_frac": [mn // gcd(mn, e), e // gcd(mn, e)],
                "min_float": mn / e,
            }
            for (p, q, uv, vu, mn) in rows
            if mn * 3 >= e
        ],
        "n_good": sum(1 for *_, mn in rows if mn * 3 >= e),
        "worst_atom_style": None,
    }


def main():
    jobs = [
        (2, 3, 3),
        (2, 3, 4),
        (2, 4, 3),
        (2, 5, 3),
        (2, 6, 3),
        (2, 6, 4),
        (2, 7, 3),
        (3, 4, 2),
        (3, 4, 3),
    ]
    # filter by expected state count
    out = []
    for a, b, c in jobs:
        print(f"=== C{a}xC{b}xC{c} ===", flush=True)
        rec = box_all_pairs(a, b, c)
        print(
            f"  e={rec['e']} δ={rec['delta'][0]}/{rec['delta'][1]}"
            f" = {rec['delta_float']:.6f} good={rec['n_good']}/{rec['n_incomp']}"
            f" best={rec['best_pair'][0]} vs {rec['best_pair'][1]}",
            flush=True,
        )
        if rec["delta"][0] * 3 < rec["delta"][1]:
            print("  *** BOX FAILS 1/3 ***", flush=True)
        out.append(
            {
                k: rec[k]
                for k in (
                    "dims",
                    "n",
                    "e",
                    "n_incomp",
                    "delta",
                    "delta_float",
                    "best_pair",
                    "n_good",
                )
            }
        )
    path = Path(__file__).resolve().parent / "box_delta.json"
    path.write_text(json.dumps({"boxes": out}, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
