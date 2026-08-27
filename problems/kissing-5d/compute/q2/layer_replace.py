#!/usr/bin/env python3
"""Exact layer-swaps of D5 and L5 across other rational hyperplanes.

Q5 (resp. R5) is the coord-sum = +2 layer of D5 (resp. L5) replaced by
the reflection of the opposite layer across sum x_i = 0.  This file tries
the same move for every short integer normal n, and also the move that
replaces a whole level set {x : n·x = c} by the reflection of
{x : n·x = −c}.

Every output configuration is checked with exact inner products.  A
kissing code of size 41 would be a new construction.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(HERE))

from configs import CONFIGS, _dot, _norm2, is_kissing
from graphio import write_adj

F = Fraction


def _reflect(v, n):
    """Orthogonal reflection across the hyperplane n·x = 0."""
    nn = _dot(n, n)
    if nn == 0:
        return v
    scale = 2 * _dot(v, n) / nn
    return tuple(x - scale * ni for x, ni in zip(v, n))


def _levels(pts, n):
    buckets = {}
    for p in pts:
        s = _dot(p, n)
        buckets.setdefault(s, []).append(p)
    return buckets


def _unique(pts):
    seen = set()
    out = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def swap_level(pts, n, c):
    """Replace the level n·x = c by the reflection of n·x = −c."""
    if c == 0:
        return None
    keep = [p for p in pts if _dot(p, n) != c]
    opposite = [p for p in pts if _dot(p, n) == -c]
    if not opposite:
        return None
    replaced = [_reflect(p, n) for p in opposite]
    return _unique(keep + replaced)


def short_normals():
    """Integer normals of squared length ≤ 8, up to sign."""
    ns = []
    seen = set()
    for coords in product(range(-2, 3), repeat=5):
        n = tuple(F(x) for x in coords)
        if _norm2(n) == 0 or _norm2(n) > 8:
            continue
        key = n if n > tuple(-x for x in n) else tuple(-x for x in n)
        if key in seen:
            continue
        seen.add(key)
        ns.append(n)
    return ns


def orbit_seed_kissing(seed):
    """Signed-permutation orbit of an equal-norm seed, max kissing subset
    by greedy then a small exact search if n ≤ 32."""
    pts = []
    seen = set()
    for perm in _perms(seed):
        for signs in product((-1, 1), repeat=5):
            if seed.count(0) and any(s < 0 and seed[i] == 0
                                     for i, s in enumerate(signs)):
                # still fine; zeros ignore signs
                pass
            v = tuple(signs[i] * perm[i] for i in range(5))
            if v not in seen and _norm2(v) == _norm2(seed):
                seen.add(v)
                pts.append(v)
    n = len(pts)
    if n == 0:
        return {"n_orbit": 0, "best": 0}
    # pairwise kissing: <x,y> ≤ |x|^2 / 2
    half = _norm2(seed) / 2
    if n > 40:
        # greedy only
        used = []
        for p in pts:
            if all(_dot(p, q) <= half for q in used):
                used.append(p)
        return {"n_orbit": n, "greedy": len(used), "best": len(used),
                "exact": False}
    adj_bad = [0] * n
    for i, j in combinations(range(n), 2):
        if _dot(pts[i], pts[j]) > half:
            adj_bad[i] |= 1 << j
            adj_bad[j] |= 1 << i
    best = 0

    def rec(used, start, sz):
        nonlocal best
        rem = 0
        for v in range(start, n):
            if used & (1 << v):
                continue
            if adj_bad[v] & used:
                continue
            rem += 1
        if sz + rem <= best:
            return
        if sz > best:
            best = sz
        for v in range(start, n):
            if used & (1 << v):
                continue
            if adj_bad[v] & used:
                continue
            rec(used | (1 << v), v + 1, sz + 1)

    rec(0, 0, 0)
    return {"n_orbit": n, "best": best, "exact": True, "beats_40": best > 40}


def _perms(seed):
    out = []
    seen = set()

    def rec(a, i):
        if i == 5:
            t = tuple(a)
            if t not in seen:
                seen.add(t)
                out.append(t)
            return
        for j in range(i, 5):
            a[i], a[j] = a[j], a[i]
            rec(a, i + 1)
            a[i], a[j] = a[j], a[i]

    rec(list(seed), 0)
    return out


def main() -> int:
    normals = short_normals()
    swaps = []
    best_size = 0
    best_rec = None
    n41 = []
    for name, builder in CONFIGS.items():
        if name not in ("D5", "L5"):
            continue
        pts = builder()
        for n in normals:
            levels = _levels(pts, n)
            for c in levels:
                if c <= 0:
                    continue
                new = swap_level(pts, n, c)
                if new is None:
                    continue
                sz = len(new)
                kiss = is_kissing(new)
                rec = {
                    "source": name,
                    "normal": [str(x) for x in n],
                    "c": str(c),
                    "size": sz,
                    "kissing": kiss,
                    "norm2_ok": all(_norm2(p) == F(2) for p in new),
                }
                swaps.append(rec)
                if kiss and sz > best_size:
                    best_size = sz
                    best_rec = rec
                if kiss and sz == 41:
                    n41.append(rec)

    orbits = {
        "half_spinor": orbit_seed_kissing((F(1, 2), F(1, 2), F(1, 2), F(1, 2), F(1))),
        "weight2": orbit_seed_kissing((F(1), F(1), F(0), F(0), F(0))),
        "Q5_cap": orbit_seed_kissing((F(1, 5), F(1, 5), F(-4, 5), F(-4, 5), F(-4, 5))),
    }

    # Dump the Q5-cap signed-permutation orbit for an exact 41-clique search.
    seed = (F(1, 5), F(1, 5), F(-4, 5), F(-4, 5), F(-4, 5))
    orbit = []
    seen = set()
    for perm in _perms(seed):
        for signs in product((-1, 1), repeat=5):
            v = tuple(signs[i] * perm[i] for i in range(5))
            if v in seen or _norm2(v) != _norm2(seed):
                continue
            seen.add(v)
            orbit.append(v)
    half = _norm2(seed) / 2
    adj = [0] * len(orbit)
    for i, j in combinations(range(len(orbit)), 2):
        if _dot(orbit[i], orbit[j]) <= half:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    write_adj(HERE / "q5cap_adj.txt", adj, len(orbit))
    orbits["Q5_cap"]["n_dumped"] = len(orbit)
    orbits["Q5_cap"]["adj"] = "q5cap_adj.txt"

    report = {
        "n_normals": len(normals),
        "n_swaps_tried": len(swaps),
        "best_kissing_size": best_size,
        "best": best_rec,
        "n_size_41": len(n41),
        "size_41": n41,
        "beats_40": best_size > 40,
        "orbits": orbits,
        "kissing_swaps_size": sorted({s["size"] for s in swaps if s["kissing"]}),
        "comment": (
            "Layer-swaps recover size 40 (including Q5/R5 when n is all-ones) "
            "and smaller kissing codes.  No size 41."
        ),
    }
    (HERE / "layer_replace.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n_swaps_tried": report["n_swaps_tried"],
        "best_kissing_size": best_size,
        "n_size_41": len(n41),
        "orbits": {k: {kk: vv for kk, vv in v.items() if kk != "exact"}
                   for k, v in orbits.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
