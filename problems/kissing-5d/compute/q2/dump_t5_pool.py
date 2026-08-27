#!/usr/bin/env python3
"""Dump the Szöllősi T^5 pool and its exact kissing graph.

The 17 August / 27 August notes left a 355-vertex compatibility graph
unsearched.  This file rebuilds that pool from a D5 basis over Q, writes
the points and the adjacency bitsets, and records the four published
40-point codes that sit inside the pool.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(HERE))

from configs import CONFIGS, _dot, _norm2, d5
from graphio import write_adj
from szollosi_candidates import T_ALL, candidates_from_basis, first_basis

F = Fraction


def _fracs(v):
    return [str(x) for x in v]


def main() -> int:
    B = first_basis(d5())
    assert B is not None and len(B) == 5
    cands = candidates_from_basis(B, T_ALL)
    pool = []
    seen = set()
    for v in list(B) + cands:
        if v in seen:
            continue
        if _norm2(v) != F(2):
            continue
        if any(v != b and _dot(v, b) > 1 for b in B):
            continue
        seen.add(v)
        pool.append(v)
    n = len(pool)
    adj = [0] * n
    deg = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if _dot(pool[i], pool[j]) <= 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                deg[i] += 1
                deg[j] += 1

    inside = {}
    for name, builder in CONFIGS.items():
        pts = builder()
        idx = []
        missing = 0
        for p in pts:
            if p in seen:
                idx.append(pool.index(p))
            else:
                missing += 1
        # Is this 40-set a clique in the pool?
        clique = missing == 0
        if clique:
            for a, b in ((i, j) for i in idx for j in idx if i < j):
                if _dot(pool[a], pool[b]) > 1:
                    clique = False
                    break
        inside[name] = {
            "n_in_pool": len(idx),
            "missing": missing,
            "is_clique": clique,
        }

    write_adj(HERE / "t5_adj.txt", adj, n)
    univ = [i for i, d in enumerate(deg) if d == n - 1]
    keep = [i for i in range(n) if i not in set(univ)]
    remap = {o: i for i, o in enumerate(keep)}
    adj355 = []
    for o in keep:
        bits = 0
        x = adj[o]
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            if b in remap:
                bits |= 1 << remap[b]
        adj355.append(bits)
    write_adj(HERE / "t5_355_adj.txt", adj355, len(keep))
    report_univ = {
        "n_universal": len(univ),
        "universal": univ,
        "n_remainder": len(keep),
        "comment": (
            "The five basis vectors are adjacent to every other pool point. "
            "A 41-clique in the 360-point pool exists iff the 355-point "
            "remainder has a 36-clique.  The 41-search on the 355-graph is "
            "complete; the 36-search is recorded separately."
        ),
    }
    pts_out = HERE / "t5_points.json"
    pts_out.write_text(json.dumps([_fracs(v) for v in pool], indent=2) + "\n")
    report = {
        "n": n,
        "basis": [_fracs(b) for b in B],
        "T": [str(t) for t in T_ALL],
        "min_deg": min(deg) if deg else None,
        "max_deg": max(deg) if deg else None,
        "n_edges": sum(deg) // 2,
        "published_40_in_pool": inside,
        "adj": "t5_adj.txt",
        "adj_355": "t5_355_adj.txt",
        "universal": report_univ,
        "points": "t5_points.json",
        "comment": (
            "A 41-clique here would be an exact kissing code whose inner "
            "products against the D5 basis lie in the union of the four "
            "published angle sets.  Empty at 41 is residue for this ansatz."
        ),
    }
    (HERE / "t5_pool.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n", "min_deg", "max_deg", "n_edges",
                       "published_40_in_pool")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
