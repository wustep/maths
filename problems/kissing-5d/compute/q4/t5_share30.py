#!/usr/bin/env python3
"""Exact 36-cliques that share 30 vertices with a published 35.

For each 30-subset S of a published 35-clique, the common neighbourhood
of S in the remainder, minus S, is the set of possible extra vertices.
A 6-clique there is a 36-clique.  C(35,5)=324632 drops; this is exact
for share 30.  Shares 31–34 were emptied by the repair scripts.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from t5_36 import bits_list, build_pool, is_clique


def clique_search(adj, n, target, node_limit=200_000):
    best = 0
    found = None
    nodes = 0

    def expand(P, stack):
        nonlocal best, found, nodes
        if found is not None:
            return
        nodes += 1
        if nodes > node_limit:
            return
        rsz = len(stack)
        if rsz + P.bit_count() <= best:
            return
        if P == 0:
            if rsz > best:
                best = rsz
            return
        rem = P
        ord_v, col = [], []
        c = 0
        while rem:
            c += 1
            avail = rem
            while avail:
                v = (avail & -avail).bit_length() - 1
                ord_v.append(v)
                col.append(c)
                avail &= ~adj[v]
                avail &= ~(1 << v)
                rem &= ~(1 << v)
        Q = P
        for i in range(len(ord_v) - 1, -1, -1):
            if found is not None or nodes > node_limit:
                return
            if rsz + col[i] <= best:
                return
            v = ord_v[i]
            stack.append(v)
            if rsz + 1 >= target:
                found = list(stack)
                best = rsz + 1
                return
            expand(Q & adj[v], stack)
            stack.pop()
            Q &= ~(1 << v)

    expand((1 << n) - 1, [])
    return found, best, nodes, found is not None or nodes <= node_limit


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    allb = (1 << n) - 1
    report = {"n": n, "by_code": {}, "found_36": False, "complete": True}

    for name, rec in G["published"].items():
        C = rec["remainder_clique"]
        if len(C) != 35 or not is_clique(adj, C):
            continue
        Cbits = 0
        for v in C:
            Cbits |= 1 << v
        tried = 0
        best_out = 0
        found = False
        complete = True
        clique36 = None
        print(f"{name} share-30 ...", flush=True)
        for drop in combinations(range(35), 5):
            keep = [C[i] for i in range(35) if i not in drop]
            bits = allb
            for v in keep:
                bits &= adj[v]
            bits &= ~Cbits
            pool = bits_list(bits)
            if len(pool) < 6:
                continue
            tried += 1
            if len(pool) > best_out:
                best_out = len(pool)
            m = len(pool)
            if m > 40:
                complete = False
                continue
            hadj = [0] * m
            for i in range(m):
                for j in range(i + 1, m):
                    if (adj[pool[i]] >> pool[j]) & 1:
                        hadj[i] |= 1 << j
                        hadj[j] |= 1 << i
            hit, best, nodes, ok = clique_search(hadj, m, 6)
            complete = complete and ok
            if hit is not None:
                found = True
                clique36 = keep + [pool[i] for i in hit]
                break
        rec_out = {
            "tried": tried,
            "best_outside_pool": best_out,
            "found": found,
            "complete": complete,
        }
        report["by_code"][name] = rec_out
        report["complete"] = report["complete"] and complete
        if found:
            report["found_36"] = True
            report["clique36"] = clique36
            print(f"  FOUND 36 from {name}", flush=True)
            break
        print(f"  tried={tried} best_pool={best_out} complete={complete}",
              flush=True)

    (HERE / "t5_share30.json").write_text(json.dumps(
        {k: v for k, v in report.items() if k != "clique36"}, indent=2
    ) + "\n")
    if report["found_36"]:
        univ = G["univ"]
        keep = G["keep"]
        pool = G["pool"]
        idx = [keep[i] for i in report["clique36"]] + list(univ)
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / "code41.json").write_text(json.dumps({
            "n": 41,
            "source": "T5 share-30 with a published 35 plus 5 basis vectors",
            "remainder_clique": report["clique36"],
            "points": [list(map(str, pool[i])) for i in idx],
        }, indent=2) + "\n")
    print("found_36", report["found_36"], "complete", report["complete"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
