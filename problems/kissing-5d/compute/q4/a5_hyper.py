#!/usr/bin/env python3
"""A5 root system in the sum-zero hyperplane of R^6, plus integer extras.

Points of Z^6 with coordinate-sum 0 and |x|^2 = 2 d^2 live in a 5-space
isometric to R^5.  Kissing is a·b <= d^2.  d=1 is the 30 A5 roots.
d=2 is 270 points; d=3 is 570.  A 41-clique is a kissing code in S^4.

Also records the regular 5-simplex (6 vertices e_i − ones/6) and its
Weyl orbit, which sits in this hyperplane.
"""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from cliqueutil import clique_search, graph_from_ok

HERE = Path(__file__).resolve().parent


def enumerate_a5(target):
    lim = 0
    while (lim + 1) * (lim + 1) <= target:
        lim += 1
    pts = []
    rng = range(-lim, lim + 1)
    for coords in product(rng, repeat=6):
        if sum(coords) != 0:
            continue
        if sum(c * c for c in coords) == target:
            pts.append(coords)
    return pts


def ip(a, b):
    return sum(x * y for x, y in zip(a, b))


def hunt(target, node_limit=2_000_000):
    pts = enumerate_a5(target)
    thresh = target // 2
    n = len(pts)
    types = Counter(tuple(sorted(abs(x) for x in p)) for p in pts)
    adj, edges = graph_from_ok(n, lambda i, j: ip(pts[i], pts[j]) <= thresh)
    # A5 roots: type (t,t,0,0,0,0) with t^2 + t^2 = target, t^2 = target/2
    seed_best = 0
    if target % 2 == 0:
        t = 0
        while 2 * t * t < target:
            t += 1
        if 2 * t * t == target:
            a5 = [i for i, p in enumerate(pts)
                  if sorted(abs(x) for x in p) == [0, 0, 0, 0, t, t]]
            seed_best = len(a5)
    found, best, nodes, complete = clique_search(
        adj, n, 41, node_limit=node_limit, seed_best=seed_best
    )
    return {
        "target": target,
        "n": n,
        "n_edges": edges,
        "types": {str(k): v for k, v in sorted(types.items())},
        "seed_best": seed_best,
        "best": best,
        "nodes": nodes,
        "found_41": found is not None,
        "complete": complete,
        "clique": found,
        "points": pts,
    }


def simplex_note():
    """Regular 5-simplex: 6 points e_i − ones/6 in the hyperplane.

    Inner products −1/6, |x|^2 = 5/6.  After scaling, max normalised
    inner product is −1/5 <= 1/2.  Size 6.  Weyl orbit of one vertex
    is the simplex itself.  Recorded so the cyclic/simplex box is not
    empty; it is not a 41-set.
    """
    return {
        "n": 6,
        "max_normalized_ip": "-1/5",
        "weyl_orbit": 6,
        "beats_40": False,
    }


def main():
    hunts = []
    hit = None
    for target, lim in ((2, 200_000), (8, 2_000_000), (18, 2_000_000)):
        rec = hunt(target, node_limit=lim)
        hunts.append({k: v for k, v in rec.items() if k not in ("clique", "points")})
        print(f"A5 |x|^2={target} n={rec['n']} best={rec['best']} "
              f"found={rec['found_41']} complete={rec['complete']}", flush=True)
        if rec["found_41"]:
            hit = rec
            break
    report = {
        "hunts": hunts,
        "simplex": simplex_note(),
        "found_41": hit is not None,
        "best": max((h["best"] for h in hunts), default=0),
        "complete": all(h["complete"] for h in hunts) and hit is None,
        "comment": (
            "Integer points of the A5 hyperplane sum_i x_i = 0 in R^6. "
            "d=1,2,3 (squared norms 2, 8, 18).  Incomplete is residue."
        ),
    }
    (HERE / "a5_hyper.json").write_text(json.dumps(report, indent=2) + "\n")
    print("found_41", report["found_41"], "best", report["best"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
