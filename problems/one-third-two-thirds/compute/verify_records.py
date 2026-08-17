#!/usr/bin/env python3
"""Independently recheck every record claimed in the attack.

Two LE counters (ideal DP vs minima recursion) and, for pair
probabilities, forward-backward vs 'add the relation and recount'.
"""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from posetlib import (
    Poset,
    T_poset,
    balance,
    chen_poset,
    count_le_ideals,
    count_le_mins,
    hook_rectangle,
    linear_sum,
    pair_counts_by_adding,
    pair_counts_fb,
    product_of_chains,
    young_diagram,
)
from box_dp import box_counts


def both_e(P, name):
    e1 = count_le_ideals(P)
    e2 = count_le_mins(P)
    if e1 != e2:
        raise AssertionError(f"{name}: {e1} vs {e2}")
    return e1


def both_pairs(P, name):
    e1, C1 = pair_counts_fb(P)
    e2, C2 = pair_counts_by_adding(P)
    if e1 != e2:
        raise AssertionError(f"{name} e {e1} vs {e2}")
    n = P.n
    for x in range(n):
        for y in range(n):
            if C1[x][y] != C2[x][y]:
                raise AssertionError(f"{name} C[{x},{y}]")
    num, den, e, pair, _ = balance(P, C1, e1)
    g = gcd(num, den)
    return e, (num // g, den // g), pair


def poset_from_down(down):
    return Poset(len(down), list(down))


def main():
    out = {}

    print("T and Aigner linear sum")
    e, d, p = both_pairs(T_poset(), "T")
    assert d == (1, 3)
    A = linear_sum(linear_sum(T_poset(), T_poset()), T_poset())
    e, d, p = both_pairs(A, "T+T+T")
    assert d == (1, 3)
    out["T"] = {"e": 3, "delta": [1, 3]}

    print("rectangles vs hook-length")
    for m, n in [(2, 3), (2, 5), (3, 4), (3, 3)]:
        P = product_of_chains((m, n))
        e = both_e(P, f"C{m}xC{n}")
        h = hook_rectangle(m, n)
        if e != h:
            raise AssertionError(f"hook C{m}xC{n}: {e} vs {h}")
        print(f"  C{m}xC{n} e={e} hook OK")

    print("Young Y(4,4,2) = 252 (Olson-Sagan hook check)")
    P = young_diagram([4, 4, 2])
    e = both_e(P, "Y442")
    assert e == 252, e

    print("Chen E(m,n) table")
    chen_E = {(1, 1): 2, (2, 2): 5, (3, 3): 14, (4, 4): 37, (5, 5): 106, (5, 4): 69}
    for (m, n), exp in chen_E.items():
        e = both_e(chen_poset(m, n), f"Chen({m},{n})")
        if e != exp:
            raise AssertionError(f"Chen({m},{n}) {e} != {exp}")
    e, d, p = both_pairs(chen_poset(5, 5), "Chen55")
    assert d == (37, 106), d
    print(f"  Chen(5,5) δ={d[0]}/{d[1]} (Olson C)")
    out["chen55"] = {"e": e, "delta": list(d), "pair": list(p)}

    print("Saks M7 from census down-set")
    # C census BEST n=7: 0 0 1 1 7 7 31
    M7 = poset_from_down([0, 0, 1, 1, 7, 7, 31])
    e, d, p = both_pairs(M7, "M7")
    assert e == 39, e
    assert d == (14, 39), d
    print(f"  M7 e={e} δ={d[0]}/{d[1]} pair={p} width={M7.width_lower()}")
    assert M7.width_lower() == 3
    out["M7"] = {
        "e": e,
        "delta": list(d),
        "pair": list(p),
        "down": [0, 0, 1, 1, 7, 7, 31],
        "width": 3,
    }

    print("M7 ⊕ C1 (n=8 chain-sum) still 14/39")
    M8 = poset_from_down([0, 0, 1, 1, 7, 7, 31, 127])
    e, d, p = both_pairs(M8, "M7+1")
    assert d == (14, 39), d
    out["M7_plus_chain"] = {"n": 8, "e": e, "delta": list(d)}

    print("3-chain boxes: bitmask vs plane-partition DP")
    box_rows = []
    for dims in [(2, 2, 2), (2, 3, 3)]:
        e_dp, uv, vu, _, _ = box_counts(*dims)
        P = product_of_chains(dims)
        e, d, p = both_pairs(P, f"box{dims}")
        assert e == e_dp
        def idx(coords):
            i = 0
            for D, c in zip(dims, coords):
                i = i * D + c
            return i

        u, v = idx((1, 0, 0)), idx((0, 1, 0))
        _, C = pair_counts_fb(P)
        assert C[u][v] == uv and C[v][u] == vu
        print(f"  C{dims[0]}xC{dims[1]}xC{dims[2]} e={e} δ={d[0]}/{d[1]} uv={uv}/{e}")
        assert d[0] * 3 >= d[1]
        box_rows.append(
            {"dims": list(dims), "e": e, "delta": list(d), "uv": uv, "vu": vu}
        )
    e_dp, uv, vu, _, _ = box_counts(2, 3, 4)
    P = product_of_chains((2, 3, 4))
    e = both_e(P, "C2xC3xC4")
    assert e == e_dp
    print(f"  C2xC3xC4 e={e} (mins=ideals=plane DP), uv={uv}/{e}")
    box_rows.append({"dims": [2, 3, 4], "e": e, "uv": uv, "vu": vu})
    out["small_boxes"] = box_rows

    print("C2xC6xC3 distinguished pairs (plane DP only, n=36)")
    e, uv, vu, _, nst = box_counts(2, 6, 3)
    # atoms of the two largest dims: (0,1,0) vs (0,0,1) is C6 vs C3, i.e.
    # first-coord 0, so that's box_counts(6,3,2) with a different axis
    e2, uv2, vu2, _, _ = box_counts(3, 6, 2)
    print(f"  e={e} 2x6-atoms {min(uv,vu)/e:.6f}  3x6-atoms {min(uv2,vu2)/e2:.6f}")
    assert e == e2
    assert min(uv2, vu2) * 3 >= e2
    out["C2xC6xC3"] = {
        "e": e,
        "atoms_2_6": [uv, vu],
        "atoms_3_6": [uv2, vu2],
        "states": nst,
    }

    path = Path(__file__).resolve().parent / "records.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path}")
    print("ALL RECORD CHECKS PASSED")


if __name__ == "__main__":
    main()
