#!/usr/bin/env python3
"""Exact constraints on a kissing code in R^5 that contains A4.

The 20 roots e_i - e_j live in the hyperplane sum x_i = 0.  Write an extra
point as x = y + (s/5) 1 with sum y = 0.  Compatibility with every A4 root
is x_i - x_j ≤ 1, i.e. y lies in the polytope

    Π = { y : sum y_i = 0, y_i - y_j ≤ 1 }.

The vertices of Π are two-level: k coordinates equal to (5-k)/5 and the
rest equal to -k/5.  Then |y|^2 = k(5-k)/5, whose maximum is 6/5.

On the sphere |x|^2 = 2 one has |y|^2 + s^2/5 = 2, so s^2/5 ≥ 2 - 6/5 = 4/5
and |s| ≥ 2.  Poles ±√(2/5) 1 have s = ±√10 and conflict with every other
extra point in the same closed hemisphere:

    <pole, x> = √(2/5) |s| ≥ 2 √(2/5) = 2 √10 / 5 > 1.

The vertices of Π, completed to |x|^2 = 2 at |s| = 2, are exactly the two
10-point D5 layers (coordinate-sum ±2) and the two 10-point Q5 reflection
layers.  Those 40 discrete extras plus the two poles are the complete list
of two-level candidates.  This file records the kissing graph on that
finite set and its maximum A4-compatible subset.

A continuous extra with |s| > 2 is not excluded here; the polar-vertex
enumeration treats a fixed 40-point code.  The discrete graph is the
exact independence number of the vertex extras, not an unrestricted bound.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import _coord_sum, _dot, _norm2, _reflect_coord_sum, d5
from fractions import Fraction

F = Fraction


def a4_roots():
    return [p for p in d5() if _coord_sum(p) == 0]


def two_level_extras():
    """The 40 vertex extras at |s|=2, as vectors of squared-norm 2."""
    plus_d5 = [p for p in d5() if _coord_sum(p) == F(2)]
    minus_d5 = [p for p in d5() if _coord_sum(p) == F(-2)]
    plus_q = [_reflect_coord_sum(p) for p in minus_d5]
    minus_q = [_reflect_coord_sum(p) for p in plus_d5]
    families = {
        "plus_D5": plus_d5,
        "minus_D5": minus_d5,
        "plus_Q5": plus_q,
        "minus_Q5": minus_q,
    }
    for name, pts in families.items():
        assert len(pts) == 10
        assert all(_norm2(p) == F(2) for p in pts)
    return families


def max_independent(pts, already=None, seed_mask=0):
    """Maximum subset with all pairwise <,> ≤ 1, optionally kissing `already`."""
    n = len(pts)
    adj_bad = [0] * n
    for i, j in combinations(range(n), 2):
        if _dot(pts[i], pts[j]) > 1:
            adj_bad[i] |= 1 << j
            adj_bad[j] |= 1 << i
    blocked = 0
    if already:
        for i, p in enumerate(pts):
            if any(_dot(p, a) > 1 for a in already):
                blocked |= 1 << i
    best = seed_mask.bit_count()
    best_mask = seed_mask

    def rec(used, start, sz):
        nonlocal best, best_mask
        rem = 0
        for v in range(start, n):
            if (used | blocked) & (1 << v):
                continue
            if adj_bad[v] & used:
                continue
            rem += 1
        if sz + rem <= best:
            return
        if sz > best:
            best, best_mask = sz, used
        for v in range(start, n):
            if (used | blocked) & (1 << v):
                continue
            if adj_bad[v] & used:
                continue
            rec(used | (1 << v), v + 1, sz + 1)

    rec(0, 0, 0)
    return best, best_mask


def polytope_max_norm2():
    vals = [F(k * (5 - k), 5) for k in range(1, 5)]
    return max(vals), {k: str(F(k * (5 - k), 5)) for k in range(1, 5)}


def pole_conflict():
    # (2 √(2/5))^2 = 8/5 > 1
    return {
        "min_<pole,extra>^2": str(F(8, 5)),
        "threshold^2": "1",
        "pole_conflicts_same_hemisphere": F(8, 5) > 1,
    }


def main() -> int:
    max_n2, n2_by_k = polytope_max_norm2()
    families = two_level_extras()
    # One hemisphere: plus_D5 ∪ plus_Q5 (20 points).
    north = families["plus_D5"] + families["plus_Q5"]
    south = families["minus_D5"] + families["minus_Q5"]
    a4 = a4_roots()
    n_north, mask_n = max_independent(north)
    n_south, mask_s = max_independent(south)
    # Both hemispheres together (40 vertex extras).
    both = north + south
    # plus_D5 is indices 0..9, plus_Q5 10..19, minus_D5 20..29, minus_Q5 30..39.
    d5_seed = (1 << 10) - 1           # north D5
    d5_seed |= ((1 << 10) - 1) << 20  # south D5
    n_both, mask_b = max_independent(both, seed_mask=d5_seed)
    # Must also kiss A4 — vertex extras were built to do so.
    a4_ok = all(_dot(p, a) <= 1 for p in both for a in a4 if p != a)

    # Cross-hemisphere: a plus_D5 point is antipodal to a minus_D5 point.
    # Q5 takes minus_D5 ∪ plus_Q5 (size 20 extras + 20 A4 = 40).
    q5_like = families["minus_D5"] + families["plus_Q5"]
    d5_like = families["minus_D5"] + families["plus_D5"]
    n_q5, _ = max_independent(q5_like)
    n_d5, _ = max_independent(d5_like)

    report = {
        "A4_polytope_max_norm2": str(max_n2),
        "norm2_by_k": n2_by_k,
        "height": {
            "min_s^2": "4",
            "min_|s|": "2",
            "from": "2 - 6/5 = 4/5 = s^2/5",
        },
        "poles": pole_conflict(),
        "discrete_vertex_extras": {
            "north_independence": n_north,
            "south_independence": n_south,
            "both_independence": n_both,
            "Q5_layer_pair_size": n_q5,
            "D5_layer_pair_size": n_d5,
            "all_kiss_A4": a4_ok,
            "A4_plus_max_vertex_extras": 20 + n_both,
        },
        "comment": (
            "Vertex extras in one hemisphere have independence number 10 "
            "(either the D5 layer or the Q5 reflection layer). Both "
            "hemispheres together still max out at 20 extras, hence 40 "
            "with A4. Continuous extras with |s|>2 are not in this graph."
        ),
    }
    out = Path(__file__).resolve().parent / "a4_containing.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    assert max_n2 == F(6, 5)
    assert n_north == 10 and n_south == 10
    assert n_q5 == 20 and n_d5 == 20
    assert n_both == 20
    print("PASS: A4 height |s|≥2; same-hemisphere vertex extras cap at 10; both hemispheres at 20.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
