#!/usr/bin/env python3
"""Type census of the 1480-point (1/4)Z^5 leftover.

Integer model: a in Z^5, a·a = 32, edge iff a·b <= 16.
D5 is the 40 vectors of type (4,4,0,0,0).  The 1440 extras split as

- type A (4,2,2,2,2): 160 points
- type B (5,2,1,1,1): 640 points
- type C (3,3,3,2,1): 640 points

The 160 four-seeds each contain 5 extras (1 type A + 4 type B).
The 80 six-seeds each contain 8 extras, all type C.
Same-missed extras are edgeless, so a clique takes at most one extra
per seed.  A 41-set with n1 = 40-k needs a (k+1)-clique of extras
whose missed-union has size k.

This file records the type split and the exact clique number of the
type-A graph (160 vertices).  It does not claim an unrestricted bound.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from cliqueutil import clique_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def bit_graph(pts, thresh):
    n = len(pts)
    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ip(pts[i], pts[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    return adj, edges


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    groups = G["groups"]
    thresh = G["thresh"]
    assert len(D) == 40
    assert len(extras) == 1440
    assert len(groups) == 240

    hist = Counter(type_key(p) for p in extras)
    four = [m for m in groups if m.bit_count() == 4]
    six = [m for m in groups if m.bit_count() == 6]
    other = [m for m in groups if m.bit_count() not in (4, 6)]
    assert len(four) == 160 and len(six) == 80 and not other

    type_A = [p for p in extras if type_key(p) == (2, 2, 2, 2, 4)]
    type_B = [p for p in extras if type_key(p) == (1, 1, 1, 2, 5)]
    type_C = [p for p in extras if type_key(p) == (1, 2, 3, 3, 3)]
    assert len(type_A) == 160
    assert len(type_B) == 640
    assert len(type_C) == 640

    four_sizes = [len(groups[m]) for m in four]
    six_sizes = [len(groups[m]) for m in six]
    assert all(s == 5 for s in four_sizes)
    assert all(s == 8 for s in six_sizes)

    # type A: one extra per four-seed.  Clique search is exact (n=160).
    adj_A, e_A = bit_graph(type_A, thresh)
    hit, best_A, nodes_A, complete_A = clique_search(
        adj_A, len(type_A), target=41, node_limit=20_000_000, seed_best=8
    )

    # intra-type B and C graphs are larger; record degrees only.
    def deg_stats(pts):
        n = len(pts)
        degs = []
        for i, p in enumerate(pts):
            d = sum(1 for j, q in enumerate(pts) if i != j and ip(p, q) <= thresh)
            degs.append(d)
        return {
            "n": n,
            "min_deg": min(degs),
            "max_deg": max(degs),
            "mean_deg": sum(degs) / n,
        }

    # six-seed extras: 8 of type B and 8 of type C.
    six_split = []
    for m in six:
        keys = Counter(type_key(p) for p in groups[m])
        six_split.append({str(k): v for k, v in keys.items()})
    six_split_u = {json.dumps(s, sort_keys=True) for s in six_split}

    report = {
        "n": 1480,
        "n_d5": 40,
        "n_extras": 1440,
        "n_groups": 240,
        "n_four_seeds": 160,
        "n_six_seeds": 80,
        "type_hist": {str(k): v for k, v in sorted(hist.items())},
        "four_seed_group_size": 5,
        "six_seed_group_size": 8,
        "four_seed_type_split_unique": sorted({
            json.dumps({str(k): v for k, v in Counter(type_key(p) for p in groups[m]).items()},
                       sort_keys=True)
            for m in four
        }),
        "six_seed_type_split_unique": sorted(six_split_u),
        "type_A_clique": {
            "n": 160,
            "edges": e_A,
            "best": best_A,
            "found_41": bool(hit),
            "nodes": nodes_A,
            "complete": complete_A,
        },
        "type_B_degrees": deg_stats(type_B),
        "type_C_degrees": deg_stats(type_C),
        "comment": (
            "Each four-seed is 1 type-A plus 4 type-B extras.  Each "
            "six-seed is 8 type-C extras.  Same-missed extras are "
            "edgeless.  A 41-set needs |E| >= |U|+1."
        ),
    }
    out = HERE / "extras_types.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "type_hist": report["type_hist"],
        "type_A_omega": best_A,
        "type_A_complete": complete_A,
        "six_split": sorted(six_split_u),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
