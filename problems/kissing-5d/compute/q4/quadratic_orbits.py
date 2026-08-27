#!/usr/bin/env python3
"""Q(√2) and Q(√5) orbits that are not the q3 golden (φ,1,1/φ,0,0)/√2 pool.

All comparisons are exact (integer models).  A 41-clique is a new code.
"""

from __future__ import annotations

import json
from itertools import combinations, permutations, product
from pathlib import Path

from cliqueutil import clique_search, graph_from_ok

HERE = Path(__file__).resolve().parent


def unique(pts):
    seen = set()
    out = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def signed_perm_orbit(seed):
    """seed is a 5-tuple of pairs (a,b) or of integers."""
    out = []
    seen = set()
    for perm in permutations(seed):
        # signs on each slot
        nonzero = [i for i, x in enumerate(perm) if x != (0, 0) and x != 0]
        k = len(nonzero)
        for signs in product((-1, 1), repeat=k):
            v = list(perm)
            for s, i in zip(signs, nonzero):
                x = v[i]
                if isinstance(x, tuple):
                    v[i] = (s * x[0], s * x[1])
                else:
                    v[i] = s * x
            t = tuple(v)
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


# ----- Q(√2): coordinate a + b√2 -------------------------------------------
# Inner product p + q√2.  After a global scale, kissing is p + q√2 <= bound.

def ip_sqrt2(u, v):
    p = q = 0
    for (a, b), (c, d) in zip(u, v):
        p += a * c + 2 * b * d
        q += a * d + b * c
    return p, q


def le_sqrt2(p, q, bound_p, bound_q=0):
    """p + q√2 <= bound_p + bound_q √2."""
    r = p - bound_p
    s = q - bound_q
    # r + s√2 <= 0
    if s == 0:
        return r <= 0
    if s > 0:
        return r < 0 and r * r >= 2 * s * s
    if r <= 0:
        return True
    return r * r <= 2 * s * s


def hunt_sqrt2():
    """Orbit of (1,1,√2,0,0).  Unscaled |x|^2 = 4.  Scale by 1/√2.

    Unscaled ip p+q√2; scaled ip = (p+q√2)/2.  Need <= 1 iff p+q√2 <= 2.
    """
    seed = ((1, 0), (1, 0), (0, 1), (0, 0), (0, 0))
    gold = signed_perm_orbit(seed)
    # D5 as (a,b): 1 = (1,0)
    d5 = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [(0, 0)] * 5
            v[i] = (si, 0)
            v[j] = (sj, 0)
            d5.append(tuple(v))
    # Mix: D5 already |x|^2=2; gold unscaled |x|^2=4, scale 1/√2.
    # Cross: <d, g_scaled> = <d, g>/√2 = (p+q√2)/√2.  Need <= 1
    # p + q√2 <= √2.  If q==0: p <= √2, p<=1 (p integer).  More carefully:
    # (p + q√2)^2 <= 2 if p+q√2 >= 0, else automatic.
    tagged = [("d5", p) for p in d5] + [("g", p) for p in gold]
    seen = set()
    pool, kinds = [], []
    for kind, p in tagged:
        if p in seen:
            continue
        seen.add(p)
        pool.append(p)
        kinds.append(kind)

    def ok(i, j):
        ki, kj = kinds[i], kinds[j]
        u, v = pool[i], pool[j]
        if ki == "g" and kj == "g":
            p, q = ip_sqrt2(u, v)
            return le_sqrt2(p, q, 2, 0)
        if ki == "d5" and kj == "d5":
            p, q = ip_sqrt2(u, v)
            return le_sqrt2(p, q, 1, 0)  # already |x|^2=2, need ip <= 1
        # D5 vs gold/√2
        if ki == "g":
            u, v = v, u
        p, q = ip_sqrt2(u, v)
        # p + q√2 <= √2
        # (p) + (q-1)√2 <= 0
        return le_sqrt2(p, q - 1, 0, 0)

    n = len(pool)
    adj, edges = graph_from_ok(n, ok)
    # D5 seed
    d5_idx = [i for i, k in enumerate(kinds) if k == "d5"]
    found, best, nodes, complete = clique_search(
        adj, n, 41, node_limit=2_000_000, seed_best=len(d5_idx)
    )
    return {
        "field": "Q(sqrt2)",
        "seed": "(1,1,sqrt2,0,0)/sqrt2",
        "n_orbit": len(gold),
        "n": n,
        "n_edges": edges,
        "best": best,
        "nodes": nodes,
        "found_41": found is not None,
        "complete": complete,
        "clique": found,
    }


# ----- Q(√5): coordinate (a + b√5)/den -------------------------------------

def ip_sqrt5(u, v):
    """u,v are 5-tuples of (a,b) meaning (a+b√5)/2.  ip = (p + q√5)/4."""
    p = q = 0
    for (a, b), (c, d) in zip(u, v):
        p += a * c + 5 * b * d
        q += a * d + b * c
    return p, q


def le_sqrt5_over4(p, q, bound_num=4):
    """(p + q√5)/4 <= 1 iff p-4 + q√5 <= 0, here bound_num=4."""
    r = p - bound_num
    if q == 0:
        return r <= 0
    if q > 0:
        return r < 0 and r * r >= 5 * q * q
    if r <= 0:
        return True
    return r * r <= 5 * q * q


def hunt_sqrt5_cubeish():
    """Orbit of (√5, 1, 1, 1, 0)/2.  Already |x|^2 = 2, field Q(√5).

    (0,1), (1,0), (1,0), (1,0), (0,0) in the /2 model.
    ip = (p+q√5)/4 <= 1 iff p-4 + q√5 <= 0.
    """
    seed = ((0, 1), (1, 0), (1, 0), (1, 0), (0, 0))
    orbit = signed_perm_orbit(seed)
    # D5: 1 = (2,0)/2
    d5 = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [(0, 0)] * 5
            v[i] = (2 * si, 0)
            v[j] = (2 * sj, 0)
            d5.append(tuple(v))
    tagged = [("d5", p) for p in d5] + [("o", p) for p in orbit]
    seen = set()
    pool, kinds = [], []
    for kind, p in tagged:
        if p in seen:
            continue
        seen.add(p)
        pool.append(p)
        kinds.append(kind)

    def ok(i, j):
        p, q = ip_sqrt5(pool[i], pool[j])
        return le_sqrt5_over4(p, q, 4)

    n = len(pool)
    adj, edges = graph_from_ok(n, ok)
    d5_idx = [i for i, k in enumerate(kinds) if k == "d5"]
    found, best, nodes, complete = clique_search(
        adj, n, 41, node_limit=2_000_000, seed_best=len(d5_idx)
    )
    return {
        "field": "Q(sqrt5)",
        "seed": "(sqrt5,1,1,1,0)/2",
        "n_orbit": len(orbit),
        "n": n,
        "n_edges": edges,
        "best": best,
        "nodes": nodes,
        "found_41": found is not None,
        "complete": complete,
        "clique": found,
    }


def hunt_sqrt5_mixed():
    """Orbit of (2, √5, 1, 0, 0)/√5 = (2√5/5, 1, √5/5, 0, 0).

    Store as (a,b) meaning (a + b√5)/5:
      (0,2), (5,0), (0,1), (0,0), (0,0)
    |x|^2 = (4*5 + 25 + 5)/25 = 50/25 = 2.
    ip = Σ (a+b√5)(c+d√5)/25 = (p + q√5)/25 <= 1 iff p-25 + q√5 <= 0.
    """
    seed = ((0, 2), (5, 0), (0, 1), (0, 0), (0, 0))
    orbit = signed_perm_orbit(seed)

    def ip25(u, v):
        p = q = 0
        for (a, b), (c, d) in zip(u, v):
            p += a * c + 5 * b * d
            q += a * d + b * c
        return p, q

    def le1(u, v):
        p, q = ip25(u, v)
        r = p - 25
        if q == 0:
            return r <= 0
        if q > 0:
            return r < 0 and r * r >= 5 * q * q
        if r <= 0:
            return True
        return r * r <= 5 * q * q

    n = len(orbit)
    adj, edges = graph_from_ok(n, lambda i, j: le1(orbit[i], orbit[j]))
    found, best, nodes, complete = clique_search(
        adj, n, 41, node_limit=2_000_000, seed_best=0
    )
    return {
        "field": "Q(sqrt5)",
        "seed": "(2,sqrt5,1,0,0)/sqrt5",
        "n_orbit": n,
        "n": n,
        "n_edges": edges,
        "best": best,
        "nodes": nodes,
        "found_41": found is not None,
        "complete": complete,
        "clique": found,
    }


def hunt_sqrt2_axes_mix():
    """(√2,1,1,0,0).  |x|^2 = 4, scale 1/√2 → (1, 1/√2, 1/√2, 0, 0).

    Unscaled (0,1),(1,0),(1,0),(0,0),(0,0).  Same kissing as hunt_sqrt2
    with a different seed (√2 on a different slot relative to the 1's).
    """
    seed = ((0, 1), (1, 0), (1, 0), (0, 0), (0, 0))
    orbit = signed_perm_orbit(seed)
    n = len(orbit)
    adj, edges = graph_from_ok(
        n, lambda i, j: le_sqrt2(*ip_sqrt2(orbit[i], orbit[j]), 2, 0)
    )
    found, best, nodes, complete = clique_search(
        adj, n, 41, node_limit=1_000_000, seed_best=0
    )
    return {
        "field": "Q(sqrt2)",
        "seed": "(sqrt2,1,1,0,0)/sqrt2",
        "n_orbit": n,
        "n": n,
        "n_edges": edges,
        "best": best,
        "nodes": nodes,
        "found_41": found is not None,
        "complete": complete,
        "clique": found,
    }


def main():
    hunts = [
        hunt_sqrt2(),
        hunt_sqrt2_axes_mix(),
        hunt_sqrt5_cubeish(),
        hunt_sqrt5_mixed(),
    ]
    found = any(h["found_41"] for h in hunts)
    report = {
        "hunts": [{k: v for k, v in h.items() if k != "clique"} for h in hunts],
        "found_41": found,
        "best": max(h["best"] for h in hunts),
        "complete": all(h["complete"] for h in hunts),
        "comment": (
            "Q(sqrt2) orbit of (1,1,sqrt2,0,0)/sqrt2 and (sqrt2,1,1,0,0)/sqrt2; "
            "Q(sqrt5) orbits of (sqrt5,1,1,1,0)/2 and (2,sqrt5,1,0,0)/sqrt5. "
            "Not the q3 golden (phi,1,1/phi,0,0) pool."
        ),
    }
    (HERE / "quadratic_orbits.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "best": report["best"],
        "found_41": found,
        "complete": report["complete"],
        "n": [h["n"] for h in hunts],
        "bests": [h["best"] for h in hunts],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
