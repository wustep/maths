#!/usr/bin/env python3
"""240-vertex seed compatibility graph.

Two seeds are compatible if some extra of the first kisses some extra
of the second.  A clique of extras uses at most one vertex per seed, so
a 41-set with |U|=k needs a seed-clique of size at least k+1 whose
union has size k.

This file records the compatibility graph and searches for seed-cliques
C with |C| >= 20 and |union(C)| <= |C|-1.  A hit is a candidate pool
for extras_clique / SAT, not itself a 41-code.  Incomplete B&B is
residue.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from cliqueutil import clique_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402


def main() -> int:
    G = extras_and_groups(4)
    groups = G["groups"]
    thresh = G["thresh"]
    seeds = list(groups)
    n = len(seeds)
    assert n == 240

    # edge if some pair of extras kisses
    adj = [0] * n
    edges = 0
    for i in range(n):
        Pi = groups[seeds[i]]
        for j in range(i + 1, n):
            Pj = groups[seeds[j]]
            ok = False
            for a in Pi:
                if ok:
                    break
                for b in Pj:
                    if ip(a, b) <= thresh:
                        ok = True
                        break
            if ok:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1

    degs = [adj[i].bit_count() for i in range(n)]

    # We already know 18-cliques of extras exist (q4 k=18, ω=18).
    # Hunt a seed-clique of size 20 whose union is at most 19.
    hit, best, nodes, complete = clique_search(
        adj, n, target=20, node_limit=8_000_000, seed_best=18
    )

    promising = []
    if hit:
        U = 0
        for i in hit:
            U |= seeds[i]
        promising.append({
            "seed_clique": hit,
            "size": len(hit),
            "union": U.bit_count(),
        })

    # Exhaustive scan of all 18-cliques is too heavy.  Record whether
    # the first 20-search produced a tight union.
    report = {
        "n_seeds": n,
        "n_four": sum(1 for m in seeds if m.bit_count() == 4),
        "n_six": sum(1 for m in seeds if m.bit_count() == 6),
        "edges": edges,
        "min_deg": min(degs),
        "max_deg": max(degs),
        "mean_deg": sum(degs) / n,
        "seed_clique_best": best,
        "seed_clique_20": hit,
        "nodes": nodes,
        "complete": complete,
        "promising_20": promising,
        "comment": (
            "Compatibility ignores which extra is chosen inside a "
            "16-point six-seed.  A promising seed-clique is only a pool."
        ),
    }
    (HERE / "seed_graph.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "edges": edges,
        "deg": [min(degs), max(degs)],
        "best": best,
        "complete": complete,
        "promising": promising,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
