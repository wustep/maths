#!/usr/bin/env python3
"""Exact type analysis of the (1/d)Z^5 kissing graph on |x|^2 = 2.

Integer model: a in Z^5, a·a = 2 d^2, edge iff a·b <= d^2.
d = 4 is the 1480-point leftover from q2.  d = 3 is a new smaller graph.
d = 2 was emptied at 41 in q2; replayed here by the same case analysis.

A 41-clique cannot contain a whole copy of D5 (polar max |x|^2 = 5/4 < 2).
Every extra vector kisses at most 36 of the 40 D5 roots, so a 41-set has
n1 <= 36 D5-type points and therefore at least 5 extras.

Two extras with missed-root sets M, M' have common D5-neighbourhood
    40 - |M ∪ M'|.
For n1 = 36 the extras must all share the same 4-set of missed roots.
Those groups are tiny and are searched exactly.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def d5_pts(d: int):
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


def enumerate_sphere(d: int):
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


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def clique_search(adj, n, target, node_limit=2_000_000):
    """Return (found_clique or None, best, nodes, complete)."""
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


def analyse(d: int) -> dict:
    thresh = d * d
    need_extras = 41  # will tighten after max_deg
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    extras = [p for p in pts if p not in Dset]
    # missed D5 indices and type stats
    missed = []
    by_type = defaultdict(list)
    for p in extras:
        miss = tuple(i for i, r in enumerate(D) if ip(p, r) > thresh)
        missed.append(miss)
        by_type[type_key(p)].append((p, miss))

    type_stats = {}
    degs = []
    for key, items in sorted(by_type.items()):
        ds = [40 - len(m) for _, m in items]
        degs.extend(ds)
        type_stats[str(key)] = {
            "n": len(items),
            "min_d5_deg": min(ds),
            "max_d5_deg": max(ds),
            "d5_deg_hist": dict(sorted(Counter(ds).items())),
        }
    max_deg = max(degs) if degs else 0
    n1_max = min(39, max_deg)
    min_extras = 41 - n1_max

    # Group extras that miss exactly the same D5 roots (n1 = 40-|M| case).
    groups = defaultdict(list)
    for p, m in zip(extras, missed):
        groups[m].append(p)
    group_sizes = Counter(len(g) for g in groups.values())
    constructions = []
    group_reports = []
    all_groups_complete = True
    for m, g in groups.items():
        n1 = 40 - len(m)
        target = 41 - n1
        if target <= 0:
            continue
        if len(g) < target:
            group_reports.append({
                "missed": len(m),
                "n1": n1,
                "n_extras": len(g),
                "target": target,
                "best": len(g),
                "found": False,
                "complete": True,
            })
            continue
        # build kissing graph on the group
        k = len(g)
        adj = [0] * k
        for i in range(k):
            for j in range(i + 1, k):
                if ip(g[i], g[j]) <= thresh:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
        hit, best, nodes, complete = clique_search(adj, k, target)
        all_groups_complete = all_groups_complete and complete
        group_reports.append({
            "missed": len(m),
            "n1": n1,
            "n_extras": k,
            "target": target,
            "best": best,
            "nodes": nodes,
            "found": hit is not None,
            "complete": complete,
        })
        if hit is not None:
            extra = [g[i] for i in hit]
            common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
            constructions.append({
                "n1": len(common),
                "n_extras": len(extra),
                "total": len(common) + len(extra),
                "extras": [list(p) for p in extra],
            })

    # Cross-group n1=35: extras of missed-size 4 whose 4-sets lie in a
    # common 5-set.  Collect all 4-sets and, for every pair of 4-sets with
    # union size 5, search 6-cliques in the union of those two groups
    # (and similarly for more 4-subsets of the same 5-set).
    four_sets = {m: g for m, g in groups.items() if len(m) == 4}
    cross35 = {"n_four_sets": len(four_sets), "tried": 0, "found": False,
               "complete": True, "best_total": 0}
    # Map each 4-set to a frozenset
    fsets = [(frozenset(m), g) for m, g in four_sets.items()]
    # Group by all 5-sets that arise as union of two 4-sets.
    by_five = defaultdict(list)
    for i in range(len(fsets)):
        for j in range(i + 1, len(fsets)):
            u = fsets[i][0] | fsets[j][0]
            if len(u) == 5:
                by_five[u].append(fsets[i][0])
                by_five[u].append(fsets[j][0])
    for u, members in by_five.items():
        # extras whose missed 4-set is a subset of u
        pool = []
        for m, g in four_sets.items():
            if frozenset(m) <= u:
                pool.extend(g)
        # unique
        pool = list(dict.fromkeys(pool))
        target = 6  # 35 + 6 = 41
        if len(pool) < target:
            continue
        cross35["tried"] += 1
        k = len(pool)
        if k > 60:
            # too large for a casual B&B; mark incomplete
            cross35["complete"] = False
            continue
        adj = [0] * k
        for i in range(k):
            for j in range(i + 1, k):
                if ip(pool[i], pool[j]) <= thresh:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
        hit, best, nodes, complete = clique_search(adj, k, target)
        cross35["complete"] = cross35["complete"] and complete
        total = 35 + best
        if total > cross35["best_total"]:
            cross35["best_total"] = total
        if hit is not None:
            extra = [pool[i] for i in hit]
            common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
            constructions.append({
                "n1": len(common),
                "n_extras": len(extra),
                "total": len(common) + len(extra),
                "extras": [list(p) for p in extra],
            })
            cross35["found"] = True

    # Mixed n1=34: a deg-34 extra misses a 6-set M; any other extra in
    # the 41-set must miss a subset of M.  Search 7-cliques in that pool
    # (34 + 7 = 41).  Same-missed groups of size 8 already cover the
    # pure-M slice; this adds the deg-36 extras whose 4-set sits in M.
    mixed34 = {"tried": 0, "found": False, "complete": True, "best_total": 0}
    six_sets = {m: g for m, g in groups.items() if len(m) == 6}
    for M, g6 in six_sets.items():
        Mset = frozenset(M)
        pool = list(g6)
        for m4, g4 in four_sets.items():
            if frozenset(m4) <= Mset:
                pool.extend(g4)
        pool = list(dict.fromkeys(pool))
        target = 7
        mixed34["tried"] += 1
        if len(pool) < target:
            continue
        k = len(pool)
        if k > 80:
            mixed34["complete"] = False
            continue
        adj = [0] * k
        for i in range(k):
            for j in range(i + 1, k):
                if ip(pool[i], pool[j]) <= thresh:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
        hit, best, nodes, complete = clique_search(adj, k, target)
        mixed34["complete"] = mixed34["complete"] and complete
        total = 34 + best
        if total > mixed34["best_total"]:
            mixed34["best_total"] = total
        if hit is not None:
            extra = [pool[i] for i in hit]
            common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
            constructions.append({
                "n1": len(common),
                "n_extras": len(extra),
                "total": len(common) + len(extra),
                "extras": [list(p) for p in extra],
            })
            mixed34["found"] = True

    found_41 = any(c["total"] >= 41 for c in constructions)
    # Same-missed-set groups cover every n1 = 40-|M| with extras that
    # all miss exactly M.  That is the complete n1=36 case (and the
    # n1=34 case when extras miss the same 6-set).  Cross-group n1=35
    # and mixed n1=34 are the next slices.  Lower n1 is residue unless
    # found_41.
    same_complete = all_groups_complete
    report = {
        "d": d,
        "n": len(pts),
        "n_d5": 40,
        "n_extras": len(extras),
        "thresh": thresh,
        "type_stats": type_stats,
        "max_d5_deg_of_extra": max_deg,
        "n1_max": n1_max,
        "min_extras_for_41": min_extras,
        "n_missed_groups": len(groups),
        "group_size_hist": dict(sorted(group_sizes.items())),
        "same_missed_groups": {
            "n": len(group_reports),
            "complete": same_complete,
            "any_hit": any(g["found"] for g in group_reports),
            "max_best": max((g["best"] for g in group_reports), default=0),
            "sample": sorted(group_reports, key=lambda g: -g["n_extras"])[:8],
        },
        "cross_n1_35": cross35,
        "mixed_n1_34": mixed34,
        "constructed_ge41": constructions,
        "found_41": found_41,
        "n1_36_empty": same_complete and not any(
            g["found"] for g in group_reports if g["n1"] == 36
        ),
        "comment": (
            f"Every extra kisses at most {max_deg} of the 40 D5 roots. "
            "A 41-set therefore uses at least "
            f"{min_extras} extras.  Same-missed-set groups settle the "
            "n1 = 40-|M| slices (in particular n1=36).  Lower-n1 mixed "
            "missed-sets are a separate search."
        ),
    }
    return report


def main() -> int:
    out = {}
    for d in (2, 3, 4):
        print(f"analyse d={d} ...", flush=True)
        rec = analyse(d)
        out[str(d)] = rec
        print(
            f"  n={rec['n']} extras={rec['n_extras']} "
            f"max_d5_deg={rec['max_d5_deg_of_extra']} "
            f"groups={rec['n_missed_groups']} "
            f"found_41={rec['found_41']} "
            f"n1_36_empty={rec['n1_36_empty']}",
            flush=True,
        )
        print(f"  group sizes {rec['group_size_hist']}", flush=True)
        print(f"  cross35 {rec['cross_n1_35']}", flush=True)
        print(f"  mixed34 {rec['mixed_n1_34']}", flush=True)
    path = HERE / "sphere_types.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
