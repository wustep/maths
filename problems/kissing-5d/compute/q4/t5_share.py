#!/usr/bin/env python3
"""36-cliques that share many vertices with a published 35.

q3 emptied share 34 and 33 (remove 1 add 2; remove 2 add 3).
q4 t5_repair_deep emptied share 32 and 31 (remove 3 add 4; remove 4 add 5).
A remaining 36-clique K satisfies |K ∩ C| ≤ 30 for every published
35-clique C, so it uses at least 6 outsiders, each adjacent to those
30 vertices of C.  Those outsiders therefore have d_C ≥ 30.

This file lists, for each published 35, the outsiders with d_C ≥ 30
and searches a 6-clique among them whose common neighbourhood in C
has size ≥ 30.  That is a complete search of 36-cliques that share
30 vertices with that C.  Lower shares are a further residue.
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


def clique_search(adj, n, target, node_limit=5_000_000):
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
    report = {"n": n, "by_code": {}, "found_36": False, "complete_share30": True}

    for name, rec in G["published"].items():
        C = rec["remainder_clique"]
        if len(C) != 35 or not is_clique(adj, C):
            continue
        Cset = set(C)
        Cbits = 0
        for v in C:
            Cbits |= 1 << v
        degC = []
        heavy = []
        for v in range(n):
            if v in Cset:
                continue
            d = bin(adj[v] & Cbits).count("1")
            degC.append(d)
            if d >= 30:
                heavy.append((v, d))
        hist = {}
        for d in degC:
            hist[d] = hist.get(d, 0) + 1
        print(f"{name} outside=320 heavy_dC>=30: {len(heavy)} "
              f"degC_hist={dict(sorted(hist.items()))}", flush=True)

        rec_out = {
            "n_heavy": len(heavy),
            "degC_hist": {str(a): b for a, b in sorted(hist.items())},
            "found": False,
            "best_outsiders": 0,
            "complete": True,
        }
        if len(heavy) >= 6:
            verts = [v for v, _ in heavy]
            remap = {v: i for i, v in enumerate(verts)}
            m = len(verts)
            hadj = [0] * m
            for i, a in enumerate(verts):
                for j, b in enumerate(verts):
                    if i < j and ((adj[a] >> b) & 1):
                        hadj[i] |= 1 << j
                        hadj[j] |= 1 << i
            # search 6-clique, then check common in C
            hit, best, nodes, ok = clique_search(hadj, m, 6)
            rec_out["best_outsiders"] = best
            rec_out["nodes"] = nodes
            rec_out["complete"] = ok
            print(f"  6-clique among heavy: best={best} found={hit is not None} "
                  f"nodes={nodes} complete={ok}", flush=True)
            if hit is not None:
                O = [verts[i] for i in hit]
                common = Cbits
                for v in O:
                    common &= adj[v]
                ncommon = bin(common).count("1")
                rec_out["n_common"] = ncommon
                if ncommon >= 30 and is_clique(adj, O + bits_list(common)[:30]):
                    K = O + bits_list(common)[:30]
                    rec_out["found"] = True
                    report["found_36"] = True
                    report["clique36"] = K[:36]
            # even if a 6-clique exists, filter by common neighbourhood
            # exhaustively when m is small
            if m <= 28 and not rec_out["found"]:
                hits = 0
                for add in combinations(range(m), 6):
                    if not is_clique(hadj, add):
                        continue
                    O = [verts[i] for i in add]
                    common = Cbits
                    for v in O:
                        common &= adj[v]
                    if bin(common).count("1") >= 30:
                        hits += 1
                        rec_out["found"] = True
                        report["found_36"] = True
                        report["clique36"] = O + bits_list(common)[:30]
                        break
                rec_out["six_cliques_checked"] = True
                rec_out["hits_share30"] = hits
        else:
            rec_out["best_outsiders"] = len(heavy)
            rec_out["complete"] = True
        report["by_code"][name] = rec_out
        report["complete_share30"] = report["complete_share30"] and rec_out["complete"]

    (HERE / "t5_share.json").write_text(json.dumps(
        {k: v for k, v in report.items() if k != "clique36"}, indent=2
    ) + "\n")
    print("found_36", report["found_36"],
          "complete_share30", report["complete_share30"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
