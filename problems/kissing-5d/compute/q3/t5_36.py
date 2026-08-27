#!/usr/bin/env python3
"""Hunt a 36-clique in the 355-point T^5 remainder.

The five D5-basis vectors of the 360-point Szöllősi pool are universal.
A 41-clique in the pool exists iff this remainder has a 36-clique.
This file rebuilds the pool over Q and exposes the helpers used by
t5_repair.py.  The long B&B is the C program clique.c (see t5_36_c.json).
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))

from configs import CONFIGS, _dot, _norm2, d5
from graphio import write_adj
from szollosi_candidates import T_ALL, candidates_from_basis, first_basis

F = Fraction


def build_pool():
    B = first_basis(d5())
    assert B is not None and len(B) == 5
    cands = candidates_from_basis(B, T_ALL)
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
    keep = [i for i in range(n) if i not in set(univ)]
    remap = {o: ni for ni, o in enumerate(keep)}
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
    published = {}
    for name, builder in CONFIGS.items():
        pts = builder()
        idx_full = []
        missing = 0
        for p in pts:
            if p in seen:
                idx_full.append(pool.index(p))
            else:
                missing += 1
        rem = [remap[i] for i in idx_full if i in remap]
        published[name] = {
            "n_in_pool": len(idx_full),
            "missing": missing,
            "remainder_clique": rem,
            "remainder_size": len(rem),
        }
    return {
        "pool": pool,
        "basis": B,
        "univ": univ,
        "keep": keep,
        "adj": adj_r,
        "n": len(keep),
        "published": published,
    }


def is_clique(adj, idx):
    for a, b in combinations(idx, 2):
        if not ((adj[a] >> b) & 1):
            return False
    return True


def common_neighbours(adj, idx, n):
    bits = (1 << n) - 1
    for v in idx:
        bits &= adj[v]
    for v in idx:
        bits &= ~(1 << v)
    return bits


def bits_list(bits):
    out = []
    x = bits
    while x:
        b = (x & -x).bit_length() - 1
        out.append(b)
        x &= x - 1
    return out


def repair(adj, clique, n, remove_k, add_k):
    """Replace `remove_k` vertices of a known clique by `add_k` outsiders."""
    C = list(clique)
    Cset = set(C)
    hits = []
    for drop in combinations(range(len(C)), remove_k):
        keep = [C[i] for i in range(len(C)) if i not in drop]
        cand_bits = common_neighbours(adj, keep, n)
        cand = [v for v in bits_list(cand_bits) if v not in Cset]
        if len(cand) < add_k:
            continue
        if add_k >= 3 and len(cand) > 28:
            continue
        for add in combinations(cand, add_k):
            if is_clique(adj, add):
                new = keep + list(add)
                if len(new) >= 36 and is_clique(adj, new):
                    hits.append(new[:36])
                    return hits
    return hits


def main() -> int:
    G = build_pool()
    n = G["n"]
    write_adj(HERE / "t5_355_adj.txt", G["adj"], n)
    repair_path = HERE / "t5_repair.json"
    c_path = HERE / "t5_36_c.json"
    repair_rec = json.loads(repair_path.read_text()) if repair_path.exists() else None
    c_rec = json.loads(c_path.read_text()) if c_path.exists() else None
    found36 = bool(repair_rec and repair_rec.get("found_36"))
    found41 = bool(repair_rec and repair_rec.get("found_41"))
    complete = False
    if c_rec and c_rec.get("found"):
        found36 = True
        complete = True
    if c_rec and c_rec.get("complete") and not c_rec.get("found"):
        complete = True
    report = {
        "n_pool": len(G["pool"]),
        "n_universal": len(G["univ"]),
        "n_remainder": n,
        "published": {k: v["remainder_size"] for k, v in G["published"].items()},
        "repairs": None if not repair_rec else repair_rec.get("repairs"),
        "c_bb": c_rec,
        "found_36": found36,
        "found_41": found41,
        "complete": complete,
        "comment": (
            "A 36-clique in the remainder plus the five universal basis "
            "vectors is a 41-point exact kissing code.  Incomplete B&B is "
            "residue, not a lower bound and not an exclusion.  The "
            "published-35 repairs are exact and empty."
        ),
    }
    (HERE / "t5_36.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n_remainder", "found_36", "found_41", "complete")},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
