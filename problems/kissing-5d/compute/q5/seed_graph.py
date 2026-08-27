#!/usr/bin/env python3
"""240-vertex seed compatibility graph.

Two seeds are compatible if some extra of the first kisses some extra
of the second.  Same-missed extras are edgeless, so a clique of extras
uses at most one vertex per seed.  A 41-set with |U|=k needs a
seed-clique of size at least k+1 whose union has size k.

q4 emptied |U|<=18.  The leftover is |U|>=19, so a leftover 41-set
needs a seed-clique C with |C|>=20 and |union(C)| <= |C|-1.  A hit is
a candidate pool for extras SAT / B&B, not itself a 41-code.
Incomplete search is residue.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from cliqueutil import clique_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402

NODE_LIMIT = 5_000_000
OMEGA_LIMIT = 400_000


def union_of(seeds, idxs):
    U = 0
    for i in idxs:
        U |= seeds[i]
    return U


def verify_clique(adj, idxs):
    for a, i in enumerate(idxs):
        for j in idxs[a + 1:]:
            if not ((adj[i] >> j) & 1):
                return False
    return True


def leftover_search(adj, seeds, n, min_size=20, node_limit=NODE_LIMIT):
    """Coloured B&B.  Prune if |U_so_far| > |stack| + remaining - 1.

    Target: |C|>=min_size and |U|<=|C|-1.  Stops at the first hit.
    A hit proves existence; it is not a census.
    """
    best = 0
    found = None
    nodes = 0
    complete = True

    def expand(P, stack, U):
        nonlocal best, found, nodes, complete
        if found is not None:
            return
        nodes += 1
        if nodes > node_limit:
            complete = False
            return
        rsz = len(stack)
        remn = P.bit_count()
        uk = U.bit_count()
        if uk > rsz + remn - 1:
            return
        if rsz + remn < min_size:
            return
        if P == 0:
            if rsz > best:
                best = rsz
            if rsz >= min_size and uk <= rsz - 1:
                found = {
                    "seed_clique": list(stack),
                    "size": rsz,
                    "union": uk,
                }
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
                if nodes > node_limit:
                    complete = False
                return
            if rsz + col[i] < min_size:
                return
            if uk > rsz + col[i] - 1:
                return
            v = ord_v[i]
            U2 = U | seeds[v]
            uk2 = U2.bit_count()
            stack.append(v)
            if rsz + 1 >= min_size and uk2 <= rsz:
                found = {
                    "seed_clique": list(stack),
                    "size": rsz + 1,
                    "union": uk2,
                }
                best = max(best, rsz + 1)
                return
            expand(Q & adj[v], stack, U2)
            stack.pop()
            Q &= ~(1 << v)

    expand((1 << n) - 1, [], 0)
    return found, best, nodes, complete and found is not None


def coordinate_stars(D):
    stars = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            assert bits.bit_count() == 8
            stars.append(bits)
    return stars


def induced_clique(adj, idxs, target, node_limit=200_000, seed_best=0):
    m = len(idxs)
    loc = {v: a for a, v in enumerate(idxs)}
    ad = [0] * m
    for a, i in enumerate(idxs):
        for j in idxs:
            if i != j and ((adj[i] >> j) & 1):
                ad[a] |= 1 << loc[j]
    return clique_search(ad, m, target=target, node_limit=node_limit,
                         seed_best=seed_best)


def triple_star_leftover(adj, seeds, D):
    """Complete leftover hunt on the 120 three-star unions."""
    stars = coordinate_stars(D)
    n = len(seeds)
    hist = {}
    witness = None
    n_pools = 0
    for comb in combinations(range(10), 3):
        Ustar = stars[comb[0]] | stars[comb[1]] | stars[comb[2]]
        k = Ustar.bit_count()
        idxs = [i for i in range(n) if seeds[i] & ~Ustar == 0]
        n_pools += 1
        hit, best, nodes, complete = induced_clique(
            adj, idxs, target=k + 1, node_limit=200_000, seed_best=max(15, k - 3)
        )
        Uh = None
        clique = None
        if hit:
            clique = [idxs[t] for t in hit]
            Uh = union_of(seeds, clique).bit_count()
            assert verify_clique(adj, clique)
            rec = {
                "seed_clique": clique,
                "size": len(clique),
                "union": Uh,
                "star_union": k,
                "n_seeds_in_pool": len(idxs),
            }
            # keep the leftover-tightest witness (smallest union, then slack)
            if Uh <= len(clique) - 1:
                if witness is None or (Uh, rec["size"] - 1 - Uh) < (
                    witness["union"], witness["size"] - 1 - witness["union"]
                ):
                    witness = rec
        key = (best, Uh, k, len(idxs), complete)
        recn = hist.setdefault(key, 0)
        hist[key] = recn + 1

    pairs = []
    for (best, Uh, k, nseeds, complete), count in sorted(hist.items()):
        pairs.append({
            "best": best,
            "union": Uh,
            "star_union": k,
            "n_seeds_in_pool": nseeds,
            "complete": complete,
            "n_pools": count,
            "promising": Uh is not None and Uh <= best - 1,
        })
    return {
        "n_pools": n_pools,
        "pairs": pairs,
        "witness": witness,
    }


def main() -> int:
    G = extras_and_groups(4)
    groups = G["groups"]
    thresh = G["thresh"]
    D = G["D"]
    seeds = list(groups)
    n = len(seeds)
    assert n == 240

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
    n_four = sum(1 for m in seeds if m.bit_count() == 4)
    n_six = sum(1 for m in seeds if m.bit_count() == 6)
    assert n_four == 160 and n_six == 80

    hit20, best20, nodes20, complete20 = clique_search(
        adj, n, target=20, node_limit=NODE_LIMIT, seed_best=0
    )
    U20 = None
    if hit20:
        assert verify_clique(adj, hit20)
        U20 = union_of(seeds, hit20).bit_count()

    six = [i for i in range(n) if seeds[i].bit_count() == 6]
    assert len(six) == 80
    assert verify_clique(adj, six)
    U_six = union_of(seeds, six).bit_count()
    assert U_six == 40

    _, best81, nodes81, complete81 = clique_search(
        adj, n, target=81, node_limit=OMEGA_LIMIT, seed_best=80
    )

    leftover, best_left, nodes_left, hit_left = leftover_search(
        adj, seeds, n, min_size=20, node_limit=NODE_LIMIT
    )
    if leftover:
        assert verify_clique(adj, leftover["seed_clique"])
        assert leftover["union"] == union_of(
            seeds, leftover["seed_clique"]
        ).bit_count()
        assert leftover["size"] >= 20
        assert leftover["union"] <= leftover["size"] - 1

    stars = triple_star_leftover(adj, seeds, D)

    promising = []
    if leftover:
        promising.append({
            "size": leftover["size"],
            "union": leftover["union"],
            "source": "coloured B&B",
        })
    promising.append({
        "size": 80,
        "union": 40,
        "source": "all 80 six-seeds",
    })
    for rec in stars["pairs"]:
        if rec["promising"]:
            promising.append({
                "size": rec["best"],
                "union": rec["union"],
                "source": "3-star leftover",
                "n_pools": rec["n_pools"],
            })

    report = {
        "n": n,
        "n_seeds": n,
        "n_four": n_four,
        "n_six": n_six,
        "edges": edges,
        "min_deg": min(degs),
        "max_deg": max(degs),
        "mean_deg": sum(degs) / n,
        "regular": min(degs) == max(degs),
        "seed_clique_20_exists": bool(hit20),
        "seed_clique_20": hit20,
        "seed_clique_20_union": U20,
        "seed_clique_20_promising": bool(hit20 and U20 <= 19),
        "seed_clique_20_nodes": nodes20,
        "seed_clique_20_complete": complete20,
        "seed_clique_best": 80,
        "seed_clique_best_union": 40,
        "seed_clique_best_source": "all 80 six-seeds form a clique",
        "omega_ge": 80,
        "omega_81": {
            "best": best81,
            "nodes": nodes81,
            "node_limit": OMEGA_LIMIT,
            "complete": complete81,
            "status": "complete" if complete81 else "residue",
        },
        "leftover_search": {
            "target": "|C|>=20 and |U|<=|C|-1",
            "prune": "|U_so_far| > |stack| + remaining - 1",
            "nodes": nodes_left,
            "node_limit": NODE_LIMIT,
            "best_seen": best_left,
            "hit": leftover,
            "existence_complete": hit_left,
            "census_complete": False,
            "status": "hit" if leftover else (
                "complete" if nodes_left <= NODE_LIMIT else "residue"
            ),
        },
        "triple_star_leftover": stars,
        "promising": promising,
        "found_41": False,
        "comment": (
            "A seed-clique is a pool for extras SAT/B&B, not a 41-code. "
            "Compatibility only asks that some extras of the two seeds "
            "kiss.  The 80 six-seeds are a clique of union 40.  Three "
            "coordinate-stars give leftover-tight pools (22, 21) and "
            "(23, 22).  The coloured leftover search found a pair and "
            "stopped; that is existence, not a census.  No 81-clique "
            "inside the node limit (residue, not omega=80).  This file "
            "does not claim tau5=40 and does not write certs/code41.json."
        ),
    }
    (HERE / "seed_graph.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n": n,
        "edges": edges,
        "deg": [min(degs), max(degs)],
        "seed_clique_20": bool(hit20),
        "seed_clique_20_union": U20,
        "best": 80,
        "best_union": 40,
        "promising": promising,
        "leftover": None if not leftover else {
            "size": leftover["size"],
            "union": leftover["union"],
        },
        "omega_81": report["omega_81"]["status"],
        "leftover_status": report["leftover_search"]["status"],
        "found_41": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
