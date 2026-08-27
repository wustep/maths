#!/usr/bin/env python3
"""Exact n1-slices of the (1/4)Z^5 extras graph, by missed-root union.

An extras-clique E contributes total = |E| + (40 - |U|) where
U = union of missed D5-root sets.  total >= 41 iff |E| >= |U| + 1,
and every extra in E has its missed set contained in U.

sphere_types.py already emptied |U| = 4 (n1=36) and the |U| = 5
cross-slice (n1=35).  This file enumerates every U that arises as a
union of actual missed sets with |U| <= 8 (n1 >= 32) and searches a
clique of size |U|+1 in the extras with M ⊆ U.

A hit is a 41-point code.  Finished empty slices are a restricted
exclusion of those n1, not an unrestricted bound.
"""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def d5_pts(d):
    pts = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [0] * 5
            v[i] = si * d
            v[j] = sj * d
            pts.append(tuple(v))
    return pts


def ip(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] + a[4] * b[4]


def enumerate_sphere(d):
    target = 2 * d * d
    lim = 0
    while (lim + 1) * (lim + 1) <= target:
        lim += 1
    squares = {i * i: i for i in range(lim + 1)}
    pts = []
    for a in range(-lim, lim + 1):
        r2 = target - a * a
        for b in range(-lim, lim + 1):
            r3 = r2 - b * b
            if r3 < 0:
                continue
            for c in range(-lim, lim + 1):
                r4 = r3 - c * c
                if r4 < 0:
                    continue
                for e in range(-lim, lim + 1):
                    rem = r4 - e * e
                    if rem not in squares:
                        continue
                    f = squares[rem]
                    for s in ((f,) if f == 0 else (f, -f)):
                        pts.append((a, b, c, e, s))
    return pts


def clique_search(adj, n, target, node_limit=3_000_000):
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


def run_d(d: int, umax: int = 8) -> dict:
    thresh = d * d
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    extras = [p for p in pts if p not in Dset]
    missed = []
    for p in extras:
        missed.append(frozenset(i for i, r in enumerate(D) if ip(p, r) > thresh))
    groups = defaultdict(list)
    for p, m in zip(extras, missed):
        groups[m].append(p)
    sets = list(groups.keys())
    print(f"d={d} extras={len(extras)} distinct missed-sets={len(sets)}",
          flush=True)

    # Generate unions of 1,2,3 missed-sets with size <= umax.
    unions = {}
    for m in sets:
        if len(m) <= umax:
            unions[m] = True
    for a, b in combinations(sets, 2):
        u = a | b
        if len(u) <= umax:
            unions[u] = True
    # triples only when both pairwise unions stayed small
    small = [m for m in sets if len(m) <= 6]
    for a, b, c in combinations(small, 3):
        u = a | b | c
        if len(u) <= umax:
            unions[u] = True
    print(f"  unions |U|<={umax}: {len(unions)}", flush=True)

    by_size = defaultdict(list)
    constructions = []
    slices = {}
    for U in unions:
        by_size[len(U)].append(U)

    for sz in sorted(by_size):
        target = sz + 1
        n1 = 40 - sz
        rec = {
            "n_U": len(by_size[sz]),
            "n1": n1,
            "target_extras": target,
            "tried": 0,
            "skipped_large": 0,
            "found": False,
            "complete": True,
            "best_extras": 0,
            "best_total": 0,
        }
        for U in by_size[sz]:
            pool = []
            for m, g in groups.items():
                if m <= U:
                    pool.extend(g)
            if len(pool) < target:
                continue
            rec["tried"] += 1
            if len(pool) > 90:
                rec["skipped_large"] += 1
                rec["complete"] = False
                continue
            k = len(pool)
            adj = [0] * k
            for i in range(k):
                for j in range(i + 1, k):
                    if ip(pool[i], pool[j]) <= thresh:
                        adj[i] |= 1 << j
                        adj[j] |= 1 << i
            hit, best, nodes, complete = clique_search(adj, k, target)
            rec["complete"] = rec["complete"] and complete
            if best > rec["best_extras"]:
                rec["best_extras"] = best
                rec["best_total"] = best + n1
            if hit is not None:
                extra = [pool[i] for i in hit]
                common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
                constructions.append({
                    "n1": len(common),
                    "n_extras": len(extra),
                    "total": len(common) + len(extra),
                })
                rec["found"] = True
                break
        slices[str(sz)] = rec
        print(f"  |U|={sz} n1={n1} {rec}", flush=True)
        if rec["found"]:
            break

    return {
        "d": d,
        "n_extras": len(extras),
        "n_missed_sets": len(sets),
        "umax": umax,
        "n_unions": len(unions),
        "slices": slices,
        "constructed_ge41": constructions,
        "found_41": bool(constructions),
        "complete_through_U": max(
            (int(s) for s, r in slices.items() if r["complete"] and not r["found"]),
            default=None,
        ),
    }


def main() -> int:
    out = {}
    for d in (4, 3, 2):
        out[str(d)] = run_d(d, umax=8)
    path = HERE / "union_slices.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
