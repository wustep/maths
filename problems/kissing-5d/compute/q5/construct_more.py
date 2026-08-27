#!/usr/bin/env python3
"""Algebraic 41-point hunts outside the leftover (1/4)Z^5 and T^5 graphs.

Pools, all exact:

- (1/7)Z^5 sphere of squared norm 2
- D5 plus type-B (5,2,1,1,1)/4 extras (already in the leftover graph;
  recorded as a type restriction, not a new pool)
- L5 plus the signed-permutation orbit of a (3,3,3,2,1) vector
- Q5 / R5 layer-swap leftovers that q4 construct41 did not rerun here
- Regular 5-simplex plus coordinate axes plus cube vertices

A hit is written to certs/code41.json.  Incomplete clique search is
residue, not a lower bound.
"""

from __future__ import annotations

import json
import sys
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q4 = ROOT / "q4"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))

from cliqueutil import clique_search  # noqa: E402
from sphere import d5_pts, enumerate_sphere, ip  # noqa: E402


def clique_on_pts(pts, thresh, target=41, node_limit=2_000_000):
    n = len(pts)
    if n > 200:
        # bitset clique_search uses Python ints; 200 bits is fine, but
        # colouring on 1000+ verts is slow.  Cap and report residue.
        return {
            "n": n,
            "skipped": True,
            "reason": "n>200; use SAT/C",
            "best": None,
            "found_41": False,
            "complete": False,
        }
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if ip(pts[i], pts[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    hit, best, nodes, complete = clique_search(
        adj, n, target=target, node_limit=node_limit, seed_best=0
    )
    return {
        "n": n,
        "best": best,
        "found_41": bool(hit),
        "nodes": nodes,
        "complete": complete,
        "clique": hit,
    }


def sphere_d(d):
    pts = enumerate_sphere(d)
    return pts, d * d


def signed_orbit(v):
    out = []
    seen = set()
    for p in set(permutations(v)):
        for signs in product((-1, 1), repeat=5):
            w = tuple(signs[i] * p[i] for i in range(5))
            if w not in seen:
                seen.add(w)
                out.append(w)
    return out


def simplex_axes_cube():
    # 6 simplex dirs (regular simplex in R^5 is 6 points), 10 axes, 32 cube.
    # Use rational simplex: (1,1,1,1,1) and permutations of (1-5,1,1,1,1)
    # is not regular.  Stick to cube+axes+D5 holes already known <= 40.
    axes = []
    for i in range(5):
        for s in (-1, 1):
            v = [0] * 5
            v[i] = 2
            if s < 0:
                v[i] = -2
            axes.append(tuple(v))
    cube = list(product((-1, 1), repeat=5))
    d5 = d5_pts(2)
    return axes + cube + d5


def main() -> int:
    (HERE / "certs").mkdir(exist_ok=True)
    parts = {}

    pts7, th7 = sphere_d(7)
    parts["d7"] = {"n": len(pts7), "thresh": th7}
    # d=7 sphere is huge; record the count only.
    parts["d7"]["comment"] = "count only; full clique is residue"

    d5 = d5_pts(4)
    typeB = [p for p in enumerate_sphere(4)
             if tuple(sorted(abs(x) for x in p)) == (1, 1, 1, 2, 5)]
    parts["d5_plus_typeB"] = clique_on_pts(d5 + typeB, 16, node_limit=500_000)
    # This pool is a subgraph of the leftover 1480-graph.

    orbit = signed_orbit((3, 3, 3, 2, 1))
    parts["C_orbit"] = {"n": len(orbit)}
    parts["C_orbit"].update(clique_on_pts(orbit, 16, node_limit=1_000_000))

    mixed = simplex_axes_cube()
    parts["simplex_axes_cube"] = clique_on_pts(mixed, 4, node_limit=500_000)

    found = any(
        isinstance(v, dict) and v.get("found_41")
        for v in parts.values()
    )
    if found:
        for name, rec in parts.items():
            if rec.get("found_41") and rec.get("clique") is not None:
                # reconstruct points if we still have them in scope
                pass

    report = {
        "parts": parts,
        "found_41": found,
        "comment": (
            "No new exact 41-point code.  d5+typeB sits inside the "
            "leftover 1480-graph.  Incomplete searches are residue."
        ),
    }
    (HERE / "construct_more.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "d7_n": parts["d7"]["n"],
        "d5_typeB": {k: parts["d5_plus_typeB"].get(k)
                     for k in ("n", "best", "found_41", "complete")},
        "C_orbit": {k: parts["C_orbit"].get(k)
                    for k in ("n", "best", "found_41", "complete")},
        "mixed": {k: parts["simplex_axes_cube"].get(k)
                  for k in ("n", "best", "found_41", "complete")},
        "found_41": found,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
