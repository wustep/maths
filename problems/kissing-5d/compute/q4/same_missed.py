#!/usr/bin/env python3
"""Same-missed-set extras in (1/d)Z^5.

A 41-set with n1 = 40-|M| D5-type points needs |M|+1 extras whose
missed-root sets sit inside one M.  When every extra in a group has
missed set exactly M, that is a clique search on that group alone.
"""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from sphere import d5_pts, enumerate_sphere, ip

HERE = Path(__file__).resolve().parent


def clique_search(adj, n, target, node_limit=2_000_000):
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


def hunt(d):
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    thresh = d * d
    extras = [p for p in pts if p not in Dset]
    groups = defaultdict(list)
    for p in extras:
        m = 0
        for i, r in enumerate(D):
            if ip(p, r) > thresh:
                m |= 1 << i
        groups[m].append(p)
    recs = []
    best_total = 0
    hit41 = None
    for M, pool in groups.items():
        k = M.bit_count()
        n1 = 40 - k
        target = k + 1
        n = len(pool)
        if n < 2:
            recs.append({"missed": k, "n_extras": n, "best": n,
                         "target": target, "found": False, "complete": True})
            best_total = max(best_total, n1 + n)
            continue
        adj = [0] * n
        for i, j in combinations(range(n), 2):
            if ip(pool[i], pool[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
        found, best, nodes, complete = clique_search(adj, n, target)
        total = n1 + best
        best_total = max(best_total, total)
        recs.append({
            "missed": k, "n_extras": n, "best": best, "target": target,
            "found": found is not None, "complete": complete, "nodes": nodes,
            "total": n1 + best,
        })
        if found is not None and n1 + len(found) >= 41:
            extra = [pool[i] for i in found]
            common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
            hit41 = {
                "d": d,
                "n1": len(common),
                "n_extras": len(extra),
                "points_int": extra + common,
            }
            break
    return {
        "d": d,
        "n": len(pts),
        "n_groups": len(groups),
        "best_total": best_total,
        "found_41": hit41 is not None,
        "n_groups_searched": len(recs),
        "max_group": max((r["n_extras"] for r in recs), default=0),
        "max_best_extras": max((r["best"] for r in recs), default=0),
        "any_incomplete": any(not r["complete"] for r in recs),
        "sample": sorted(recs, key=lambda r: -r.get("total", r["best"]))[:8],
        "hit": hit41,
    }


def write_code41(d, points_int):
    from fractions import Fraction
    (HERE / "certs").mkdir(exist_ok=True)
    pts = [tuple(Fraction(a, d) for a in p) for p in points_int[:41]]
    (HERE / "certs" / "code41.json").write_text(json.dumps({
        "n": 41,
        "source": f"same_missed.py d={d}",
        "points": [[str(x) for x in p] for p in pts],
    }, indent=2) + "\n")


def main():
    report = {}
    for d in (3, 5, 6):
        rec = hunt(d)
        report[str(d)] = {k: v for k, v in rec.items() if k != "hit"}
        print(f"d={d} best_total={rec['best_total']} found_41={rec['found_41']} "
              f"max_group={rec['max_group']} max_best_ex={rec['max_best_extras']}",
              flush=True)
        if rec["hit"]:
            write_code41(d, rec["hit"]["points_int"])
            report["found_41"] = True
            break
    else:
        report["found_41"] = False
    (HERE / "same_missed.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
