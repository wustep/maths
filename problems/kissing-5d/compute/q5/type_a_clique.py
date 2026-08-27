#!/usr/bin/env python3
"""Exact 20-clique in the 160 type-A extras, and the missed-union size.

Type A is (4,2,2,2,2).  Each misses a 4-set of D5 roots.  A 20-clique
plus D5 \\ U is a 41-set iff |U| <= 19.
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
from sphere import d5_pts, extras_and_groups, ip  # noqa: E402


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    thresh = G["thresh"]
    type_A = [p for p in extras if type_key(p) == (2, 2, 2, 2, 4)]
    n = len(type_A)
    assert n == 160
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if ip(type_A[i], type_A[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    hit, best, nodes, complete = clique_search(
        adj, n, target=20, node_limit=5_000_000, seed_best=19
    )
    Dlist = d5_pts(4)
    assert Dlist == list(D)
    U = 0
    if hit:
        for i in hit:
            for r, root in enumerate(D):
                if ip(type_A[i], root) > thresh:
                    U |= 1 << r
    report = {
        "n": n,
        "best": best,
        "found_20": bool(hit),
        "nodes": nodes,
        "complete": complete,
        "clique": hit,
        "U": None if not hit else U.bit_count(),
        "n1": None if not hit else 40 - U.bit_count(),
        "total": None if not hit else 20 + (40 - U.bit_count()),
        "gives_41": bool(hit and U.bit_count() <= 19),
    }
    if report["gives_41"]:
        Uset = {r for r in range(40) if (U >> r) & 1}
        pts = [list(type_A[i]) for i in hit]
        for r, p in enumerate(D):
            if r not in Uset:
                pts.append(list(p))
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / "code41.json").write_text(json.dumps({
            "n": len(pts),
            "source": "q5 type-A 20-clique plus D5\\\\U",
            "points": pts,
        }, indent=2) + "\n")
    (HERE / "type_a_clique.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("best", "found_20", "U", "total", "gives_41",
                       "complete", "nodes")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
