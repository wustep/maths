#!/usr/bin/env python3
"""Try to beat the cyclic construction by one extra out-edge per vertex.

Start from the circulant C(n; {1,…,r}) with r=⌊(n−1)/3⌋, which is C3-free.
Search for an oriented r+1-outregular C3-free graph: first by adding a
1-factor of extra arcs to the circulant, then by random rewiring.

A success would be a counterexample to Caccetta–Häggkvist (except when
r+1 < n/3, which never happens).  Hamidoune already forbids Cayley extras.
"""

from __future__ import annotations

import itertools
import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / "certs"


def circulant(n: int, r: int) -> list[set[int]]:
    return [{(i + s) % n for s in range(1, r + 1)} for i in range(n)]


def has_c3(outs: list[set[int]]) -> bool:
    n = len(outs)
    for i in range(n):
        for j in outs[i]:
            for k in outs[j]:
                if i in outs[k]:
                    return True
    return False


def count_c3(outs) -> int:
    n = len(outs)
    c = 0
    for i in range(n):
        for j in outs[i]:
            for k in outs[j]:
                if i in outs[k] and i < j and i < k:
                    c += 1
    return c


def add_matching(n, r, seed=0):
    """Each vertex tries to add one extra out-neighbour not already used,
    not a 2-cycle, not immediately creating a C3.  Greedy + random restarts.
    """
    rng = random.Random(seed)
    best = 0
    for trial in range(200):
        outs = circulant(n, r)
        added = 0
        verts = list(range(n))
        rng.shuffle(verts)
        for i in verts:
            cand = [j for j in range(n) if j != i and j not in outs[i] and i not in outs[j]]
            rng.shuffle(cand)
            for j in cand:
                # adding i→j creates a C3 iff exists k with i→k→j→i or j in N+(N+(i)) ∩ N-(i)
                # i→j→k→i: j→k and k→i
                # k→i→j→k: k→i and j→k ... 
                bad = False
                # triangles using the new arc i→j:
                # i→j→k→i
                if any(k in outs[j] and i in outs[k] for k in range(n)):
                    bad = True
                # k→i→j→k
                if not bad and any(j in outs[k] and i in outs[k] for k in range(n) if k != i and k != j):
                    # wait: k→i and j→k. j→k is outs[j], k→i is i in outs[k]
                    pass
                if not bad:
                    if any((i in outs[k]) and (k in outs[j]) for k in range(n)):
                        bad = True  # i→j→k→i already; this is j→k and k→i
                if not bad:
                    # k→i→j→k : i in outs[k] and k in outs[j]
                    if any((i in outs[k]) and (k in outs[j]) for k in range(n) if k != i):
                        bad = True
                if not bad:
                    # i→j and existing i→k→?  already covered
                    # last: i→k→j→i but j→i is forbidden (2-cycle)
                    outs[i].add(j)
                    added += 1
                    break
        best = max(best, added)
        if added == n and not has_c3(outs):
            return {"n": n, "r": r, "added": added, "success": True, "trial": trial}
    return {"n": n, "r": r, "added_best": best, "success": False}


def rewire_search(n, d, steps=20000, seed=0):
    """Start from circulant of degree d-1 plus random extra stubs; flip arcs."""
    rng = random.Random(seed)
    r = d - 1
    if r < 1:
        return {"n": n, "d": d, "status": "skip"}
    outs = circulant(n, r)
    # add as many extras as possible greedily
    for i in range(n):
        while len(outs[i]) < d:
            cand = [j for j in range(n) if j != i and j not in outs[i] and i not in outs[j]]
            if not cand:
                break
            outs[i].add(rng.choice(cand))
    cur = count_c3(outs)
    degs = [len(outs[i]) for i in range(n)]
    best_c3 = cur
    for _ in range(steps):
        i = rng.randrange(n)
        if not outs[i]:
            continue
        a = rng.choice(tuple(outs[i]))
        cand = [j for j in range(n) if j != i and j not in outs[i] and i not in outs[j]]
        if not cand:
            continue
        b = rng.choice(cand)
        outs[i].remove(a)
        outs[i].add(b)
        nxt = count_c3(outs)
        if nxt <= cur or rng.random() < 0.02:
            cur = nxt
            best_c3 = min(best_c3, cur)
        else:
            outs[i].remove(b)
            outs[i].add(a)
        if cur == 0 and min(len(s) for s in outs) >= d:
            return {"n": n, "d": d, "success": True, "c3": 0, "degs": [len(s) for s in outs]}
    return {
        "n": n,
        "d": d,
        "success": False,
        "best_c3": best_c3,
        "min_deg": min(len(s) for s in outs),
        "mean_deg": sum(len(s) for s in outs) / n,
    }


def main():
    recs = []
    for n in range(5, 25):
        r = (n - 1) // 3
        rec = add_matching(n, r, seed=n)
        recs.append(rec)
        print(rec, flush=True)
    hunts = []
    for n, d in [(6, 2), (8, 3), (9, 3), (12, 4), (15, 5), (18, 6), (21, 7)]:
        h = rewire_search(n, d, steps=30000, seed=n * 17)
        hunts.append(h)
        print("rewire", h, flush=True)
    path = OUT / "hunt_plus_one.json"
    path.write_text(json.dumps({"matching": recs, "rewire": hunts}, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
