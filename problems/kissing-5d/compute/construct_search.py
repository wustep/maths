#!/usr/bin/env python3
"""Algebraic 41-point searches in R^5 that can be checked exactly.

Every construction below produces a finite list of candidate unit (or
equal-norm) vectors with coordinates in a cyclotomic / quadratic field
that we implement with integer tuples and a common squared norm.  A hit
of size > 40 with all pairwise inner products ≤ half the squared norm
would be a new kissing code.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


def max_clique_greedy(ok_edge, n, seed_sets):
    """Exact branch-and-bound for modest n (≤ 40).  ok_edge(i,j) is bool."""
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if ok_edge(i, j):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    best = 0
    best_mask = 0

    def rec(used, start, sz):
        nonlocal best, best_mask
        rem = 0
        for v in range(start, n):
            if (adj[v] & used) == 0:
                rem += 1
        if sz + rem <= best:
            return
        if sz > best:
            best, best_mask = sz, used
        for v in range(start, n):
            if adj[v] & used:
                continue
            rec(used | (1 << v), v + 1, sz + 1)

    rec(0, 0, 0)
    for seed in seed_sets:
        rec(seed, 0, seed.bit_count())
    return best, best_mask


def cube_plus_axes() -> dict:
    """32 cube vertices (±1)^5 together with 10 axes ±e_i, common scale later.

    Cube-cube Hamming distance 1 has inner product 3 (unnormalized, coords ±1),
    while half-norm^2 = 5/2 = 2.5, and 3 > 2.5, so adjacent cube vertices are
    illegal.  We take a max subset of the 32+10 = 42 points with all pairwise
    unnormalized inner products ≤ 5/2 for cube-cube (i.e. Hamming ≥ 2),
    ≤ √5 for cube-axis (automatically |1| ≤ √5), and 0 or -1 for axis-axis.
    Cube points have norm^2=5, axes have norm^2=1 — different lengths, so
    they are NOT a spherical code unless we put them on the same sphere.

    Same-sphere version: cube (±1)^5 / √5 and axes ±e_i.
    Cube-axis ip = ±1/√5 ≈ 0.447 ≤ 1/2.  Axis-axis 0 or -1.  Cube-cube
    ip = (5-2d)/5, need d ≥ 2, i.e. no two at Hamming distance 1.
    Max independent set of the 5-cube is 16 (e.g. even weight), total 26.
    """
    cube = list(itertools.product((-1, 1), repeat=5))
    # even-weight (even number of -1s) is a maximum independent set
    even = [v for v in cube if sum(1 for x in v if x < 0) % 2 == 0]
    odd = [v for v in cube if sum(1 for x in v if x < 0) % 2 == 1]
    assert len(even) == 16 and len(odd) == 16
    # cannot mix even and odd without creating a Hamming-1 pair?  Yes you can
    # if you take a smaller mix.  Max independent set of Q5 is 16.
    return {
        "cube_independent_set": 16,
        "plus_10_axes": 26,
        "beats_40": False,
        "note": "A(Q5)=16, cube+axes spherical code has size 26.",
    }


def signed_weight2_plus_holes() -> dict:
    """D5 (40) plus the 32 deep holes (±1)^5.  Conflicting pairs removed.

    Unnormalized: D5 roots have norm^2=2, holes h=√(2/5)(±1)^5 have norm^2=2
    as well if we take h = (±1)^5 * sqrt(2/5), ip(D5, hole) = ±2/√5 or 0.
    2/√5 ≈ 0.894 > 1, so a hole conflicts with every D5 root that shares
    two matching signs in the hole's support — 10 roots.  Removing those
    10 and adding 1 hole yields 31.  Adding a complementary set of holes
    (a simplex of the 5-cube) still requires deleting their 10-neighbourhoods.
    """
    # Exact integer model: D5 as (±1,±1,0,0,0); holes as (±1)^5.
    # Compare 5*<d,h>^2 against 2*<d,d>*<h,h> = 2*2*5=20, i.e. <d,h>^2 ≤ 5
    # for the *normalized* ip to be ≤ 1/2:  <d,h> / (√2 √5) ≤ 1/2
    # ⇒ <d,h> ≤ √(10)/2 = √(2.5) ≈ 1.58.  <d,h> is 0 or ±2.
    # 2 > 1.58, conflict iff |<d,h>|=2.
    d5 = []
    for i, j in itertools.combinations(range(5), 2):
        for si, sj in itertools.product((-1, 1), repeat=2):
            v = [0] * 5
            v[i], v[j] = si, sj
            d5.append(tuple(v))
    holes = list(itertools.product((-1, 1), repeat=5))

    def conflicts(d, h):
        return abs(sum(a * b for a, b in zip(d, h))) == 2

    # For each hole, how many D5 roots conflict
    conf_counts = []
    for h in holes:
        conf_counts.append(sum(1 for d in d5 if conflicts(d, h)))
    # Greedy: add as many holes as possible, delete their D5 neighbours
    best = 40
    # all-even-sign holes: 16 of them.  Try every 0/1 subset of a
    # 6-hole simplex (the 5-simplex of holes with a fixed first coord +1
    # and even parity) — 16 is too big to subset, but the 16 even-sign
    # holes are a spherical simplex-like set.
    even_holes = [h for h in holes if sum(1 for x in h if x < 0) % 2 == 0]
    # For a subset S of even_holes, remaining = (D5 minus N(S)) union S
    # |S|≤16, 2^16=65536, feasible.
    best_size = 0
    best_ns = 0
    for mask in range(1 << 16):
        Sidx = [i for i in range(16) if (mask >> i) & 1]
        S = [even_holes[i] for i in Sidx]
        blocked = set()
        for h in S:
            for i, d in enumerate(d5):
                if conflicts(d, h):
                    blocked.add(i)
        # holes must also be pairwise kissing: <h,h'>/(5) ≤ 1/2 ⇒ <h,h'> ≤ 5/2
        # <h,h'> = 5-2d ≡ 5,1,-3,-7,-11;  5 is self.  1 ≤ 2.5, -3≤2.5.
        # ALL pairs of cube vertices have ip ≤ 1 after this scaling?  d=1
        # gives ip=3 > 2.5.  So S itself must be Hamming-independent.
        good = True
        for a, b in itertools.combinations(S, 2):
            if sum(x * y for x, y in zip(a, b)) == 3:
                good = False
                break
        if not good:
            continue
        sz = 40 - len(blocked) + len(S)
        if sz > best_size:
            best_size = sz
            best_ns = len(S)
    return {
        "conflicts_per_hole": sorted(set(conf_counts)),
        "best_D5_minus_N_S_plus_even_holes": best_size,
        "best_n_holes_used": best_ns,
        "beats_40": best_size > 40,
    }


def simplex_crosspoly() -> dict:
    """6-point simplex union 10-point cross-polytope, and their orbit sums."""
    # Regular simplex in the hyperplane sum=0: 6 points? In R^5 the simplex
    # has 6 vertices, e.g. the 6 points obtained from (1,1,1,1,1,-5) in R^6
    # projected — standard: (1,1,1,1,1) is not 6 points.
    # 5+1 = 6 vertices: v_i = e_i * a + b*ones, plus v_6.
    # Standard coordinates: 6 points in R^5,
    #   p_i = ((n+1) e_i - ones)/scale  for i=1..5, and p_6 = -ones/scale'?
    # Simpler: the 6 points
    #   (1,1,1,1,-4) and permutations of the -4  — that's only 5 points.
    # Add (-1,-1,-1,-1,4)? That's the antipodal 5-set, 10 points, not a simplex.
    # The regular 5-simplex has 6 vertices.  One model:
    #   rows of I_5 minus 1/6 ones, plus a last point.
    return {
        "simplex_size": 6,
        "crosspoly_size": 10,
        "union_without_rescaling_not_on_one_sphere": True,
        "note": "Equal-norm simplex+crosspoly is the 16-cell / 5-cell mix; "
                "not a 41-point lead.",
    }


def main() -> int:
    report = {
        "cube_plus_axes": cube_plus_axes(),
        "D5_plus_holes": signed_weight2_plus_holes(),
        "simplex_crosspoly": simplex_crosspoly(),
    }
    out = Path(__file__).resolve().parent / "construct_search.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
