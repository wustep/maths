#!/usr/bin/env python3
"""Complete n1-slices for (1/4)Z^5: every U containing an actual missed set.

If an extras-clique has missed-root union U, then U contains every
member's missed set, hence contains at least one actual missed 4-set
(or 6-set).  Enumerating all k-supersets of actual missed sets is
therefore a complete generation of candidate U of size k.

k = 4,5,6,7 (n1 = 36..33).  A miss is a restricted exclusion of those
n1 on this graph, not an unrestricted bound.
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


def clique_search(adj, n, target, node_limit=1_000_000):
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
    d = 4
    thresh = d * d
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    extras = [p for p in pts if p not in Dset]
    masks = []
    for p in extras:
        m = 0
        for i, r in enumerate(D):
            if ip(p, r) > thresh:
                m |= 1 << i
        masks.append(m)
    # unique missed masks (seeds)
    seed_set = set(masks)
    seeds = list(seed_set)
    print(f"extras={len(extras)} seeds={len(seeds)}", flush=True)

    constructions = []
    slices = {}
    for k in (4, 5, 6, 7):
        target = k + 1
        n1 = 40 - k
        seen = set()
        rec = {
            "k": k,
            "n1": n1,
            "target_extras": target,
            "n_U": 0,
            "tried": 0,
            "found": False,
            "complete": True,
            "best_extras": 0,
            "best_total": 0,
        }
        for M in seeds:
            popM = bin(M).count("1")
            if popM > k:
                continue
            rest = [i for i in range(40) if not (M >> i) & 1]
            need = k - popM
            for extra_idx in combinations(rest, need):
                U = M
                for i in extra_idx:
                    U |= 1 << i
                if U in seen:
                    continue
                seen.add(U)
                rec["n_U"] += 1
                pool = [extras[i] for i, m in enumerate(masks) if (m & ~U) == 0]
                if len(pool) < target:
                    continue
                rec["tried"] += 1
                kk = len(pool)
                adj = [0] * kk
                for i in range(kk):
                    for j in range(i + 1, kk):
                        if ip(pool[i], pool[j]) <= thresh:
                            adj[i] |= 1 << j
                            adj[j] |= 1 << i
                hit, best, nodes, complete = clique_search(adj, kk, target)
                rec["complete"] = rec["complete"] and complete
                if best > rec["best_extras"]:
                    rec["best_extras"] = best
                    rec["best_total"] = best + n1
                if hit is not None:
                    extra = [pool[i] for i in hit]
                    common = [r for r in D
                              if all(ip(p, r) <= thresh for p in extra)]
                    constructions.append({
                        "n1": len(common),
                        "n_extras": len(extra),
                        "total": len(common) + len(extra),
                    })
                    rec["found"] = True
                    break
            if rec["found"]:
                break
        slices[str(k)] = rec
        print(f"k={k} n1={n1} {rec}", flush=True)

    report = {
        "d": 4,
        "n": 1480,
        "n_extras": len(extras),
        "slices": slices,
        "constructed_ge41": constructions,
        "found_41": bool(constructions),
        "n1_ge_33_empty": (
            all(slices[str(k)]["complete"] and not slices[str(k)]["found"]
                for k in (4, 5, 6, 7))
        ),
        "comment": (
            "Complete generation: every U of size k that can arise contains "
            "an actual missed set.  Empty at k=4,5,6,7 means no 41-point "
            "code in (1/4)Z^5 uses 33 or more D5-type points.  n1<=32 is "
            "a leftover slice, not an emptiness proof of the whole graph."
        ),
    }
    (HERE / "complete_slices.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote complete_slices.json found_41=", report["found_41"],
          "n1_ge_33_empty=", report["n1_ge_33_empty"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
