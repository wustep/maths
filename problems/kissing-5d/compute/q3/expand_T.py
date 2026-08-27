#!/usr/bin/env python3
"""Szöllősi T^5 pools on larger exact angle sets than the published union.

q2 used the nine published 40-point angles.  This file adds other short
rationals that a 41-point code could use, rebuilds the compatible-vector
graph over Q, and searches for a 41-clique.

T_fat = published union plus {±1/3, ±2/5, ±3/8, ±1/8, ±3/5}.
9+8 = 17 values; 17^5 is 1.4e6 linear solves, fine over Q.

A 41-clique is a new exact code.  Empty at 41 is residue for this ansatz.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))

from configs import CONFIGS, _dot, _norm2, d5
from szollosi_candidates import T_ALL, candidates_from_basis, first_basis

F = Fraction

T_FAT = sorted(set(T_ALL + [
    F(-1, 3), F(1, 3),
    F(-2, 5), F(2, 5),
    F(-3, 5), F(3, 5),
]))


def build(T):
    B = first_basis(d5())
    cands = candidates_from_basis(B, T)
    pool = []
    seen = set()
    for v in list(B) + cands:
        if v in seen:
            continue
        if _norm2(v) != F(2):
            continue
        if any(v != b and _dot(v, b) > 1 for b in B):
            continue
        seen.add(v)
        pool.append(v)
    n = len(pool)
    adj = [0] * n
    deg = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if _dot(pool[i], pool[j]) <= 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                deg[i] += 1
                deg[j] += 1
    univ = [i for i, d in enumerate(deg) if d == n - 1]
    inside = {}
    for name, builder in CONFIGS.items():
        pts = builder()
        idx = [pool.index(p) for p in pts if p in seen]
        inside[name] = {"n_in_pool": len(idx), "missing": 40 - len(idx)}
    return pool, adj, deg, univ, inside


def greedy_colour_order(adj, P):
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
    return ord_v, col


def bb_target(adj, n, target, node_limit=4_000_000):
    best = target - 1
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
        ord_v, col = greedy_colour_order(adj, P)
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
    return found, best, nodes


def main() -> int:
    print(f"|T_fat|={len(T_FAT)}", flush=True)
    pool, adj, deg, univ, inside = build(T_FAT)
    n = len(pool)
    print(f"pool {n} univ {len(univ)} edges {sum(deg)//2}", flush=True)
    print("published in pool", inside, flush=True)
    # Peel universals: 41-clique iff remainder has clique of size 41-|U|
    keep = [i for i in range(n) if i not in set(univ)]
    remap = {o: i for i, o in enumerate(keep)}
    adj_r = []
    for o in keep:
        bits = 0
        x = adj[o]
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            if b in remap:
                bits |= 1 << remap[b]
        adj_r.append(bits)
    target = 41 - len(univ)
    print(f"remainder {len(keep)} target {target}", flush=True)
    hit, best, nodes = bb_target(adj_r, len(keep), target, node_limit=5_000_000)
    clique41 = None
    if hit is not None:
        full = [keep[i] for i in hit] + univ
        pts = [pool[i] for i in full[:41]]
        ok = all(_dot(pts[a], pts[b]) <= 1 for a in range(41) for b in range(a + 1, 41))
        clique41 = {
            "ok": ok,
            "indices": full[:41],
            "points": [[str(x) for x in p] for p in pts],
        }
        if ok:
            (HERE / "certs" / "code41_expandT.json").write_text(
                json.dumps(clique41, indent=2) + "\n"
            )
    report = {
        "T": [str(t) for t in T_FAT],
        "n": n,
        "n_universal": len(univ),
        "n_remainder": len(keep),
        "remainder_target": target,
        "n_edges": sum(deg) // 2,
        "published": inside,
        "best_lifted": best + len(univ),
        "nodes": nodes,
        "found_41": bool(clique41 and clique41["ok"]),
        "complete": hit is not None or nodes <= 5_000_000,
        "clique41": clique41,
        "comment": (
            "T^5 pool on the published angles plus {±1/3,±2/5,±3/5}. "
            "A 41-clique is a new exact code.  Incomplete search is residue."
        ),
    }
    (HERE / "expand_T.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n", "n_remainder", "remainder_target", "best_lifted",
                       "found_41", "complete", "nodes")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
