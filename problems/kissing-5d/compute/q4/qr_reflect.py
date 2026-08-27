#!/usr/bin/env python3
"""Layer-swaps and second reflections of Q5 and R5.

q2 already swapped D5 and L5 across short integer normals.  This file
does the same move on Q5 and R5 (which are themselves one swap), and
also the composition of two swaps.  Polar maximality forbids adding a
41st point to either code, so every candidate replaces a level set.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from configs import CONFIGS, _dot, _norm2, is_kissing, q5, r5

F = Fraction


def _reflect(v, n):
    nn = _dot(n, n)
    if nn == 0:
        return v
    scale = 2 * _dot(v, n) / nn
    return tuple(x - scale * ni for x, ni in zip(v, n))


def _unique(pts):
    seen = set()
    out = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def swap_level(pts, n, c):
    if c == 0:
        return None
    keep = [p for p in pts if _dot(p, n) != c]
    opposite = [p for p in pts if _dot(p, n) == -c]
    if not opposite:
        return None
    return _unique(keep + [_reflect(p, n) for p in opposite])


def short_normals(lim=2, n2max=10):
    ns = []
    seen = set()
    for coords in product(range(-lim, lim + 1), repeat=5):
        n = tuple(F(x) for x in coords)
        n2 = _norm2(n)
        if n2 == 0 or n2 > n2max:
            continue
        key = n if n > tuple(-x for x in n) else tuple(-x for x in n)
        if key in seen:
            continue
        seen.add(key)
        ns.append(n)
    return ns


def levels_of(pts, n):
    buckets = {}
    for p in pts:
        s = _dot(p, n)
        buckets.setdefault(s, []).append(p)
    return buckets


def main():
    normals = short_normals()
    best = 0
    best_rec = None
    n41 = []
    n_swaps = 0
    sizes = {}
    for name, builder in (("Q5", q5), ("R5", r5)):
        base = builder()
        for n in normals:
            lev = levels_of(base, n)
            for c in lev:
                if c <= 0:
                    continue
                new = swap_level(base, n, c)
                if new is None:
                    continue
                n_swaps += 1
                kiss = is_kissing(new)
                sz = len(new)
                if kiss:
                    sizes[sz] = sizes.get(sz, 0) + 1
                    if sz > best:
                        best = sz
                        best_rec = {
                            "source": name,
                            "normal": [str(x) for x in n],
                            "c": str(c),
                            "size": sz,
                        }
                    if sz == 41:
                        n41.append(best_rec)
        # Second swap: only on kissing 40-sets produced by the first pass,
        # and only across normals of squared length <= 5, so the
        # composition stays a finite exact search.
        ones = tuple(F(1) for _ in range(5))
        short = [n for n in normals if _norm2(n) <= 5]
        n_second = 0
        for n in short:
            if n == ones or n == tuple(-x for x in ones):
                continue
            lev = levels_of(base, n)
            for c in lev:
                if c <= 0:
                    continue
                mid = swap_level(base, n, c)
                if mid is None or not is_kissing(mid) or len(mid) != 40:
                    continue
                n_second += 1
                if n_second > 40:
                    break
                for n2 in short:
                    lev2 = levels_of(mid, n2)
                    for c2 in lev2:
                        if c2 <= 0:
                            continue
                        new = swap_level(mid, n2, c2)
                        if new is None:
                            continue
                        n_swaps += 1
                        if is_kissing(new):
                            sz = len(new)
                            sizes[sz] = sizes.get(sz, 0) + 1
                            if sz > best:
                                best = sz
                                best_rec = {
                                    "source": name + "+2",
                                    "size": sz,
                                }
                            if sz == 41:
                                n41.append({"source": name + "+2", "size": 41})
            if n_second > 40:
                break
    report = {
        "n_normals": len(normals),
        "n_swaps_tried": n_swaps,
        "best_kissing_size": best,
        "best": best_rec,
        "n_size_41": len(n41),
        "kissing_sizes": sorted(sizes),
        "found_41": len(n41) > 0,
        "complete": True,
        "comment": (
            "Layer-swaps of Q5 and R5, and compositions of two swaps. "
            "A kissing 41-set would be written to certs/code41.json."
        ),
    }
    (HERE / "qr_reflect.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n_swaps_tried", "best_kissing_size", "found_41",
                       "kissing_sizes")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
