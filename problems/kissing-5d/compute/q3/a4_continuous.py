#!/usr/bin/env python3
"""Continuous extras over a fixed A4 equator at height |s| > 2.

q1 treated the two-level vertices of the A4 polar polytope
    Π = { y : sum y_i = 0, y_i - y_j ≤ 1 },
which have |y|^2 ≤ 6/5 and force |s| ≥ 2.  The vertex extras give at
most 10 points per hemisphere.  A continuous extra has |y|^2 < 6/5 and
|s| > 2, with |y|^2 + s^2/5 = 2.

This file searches a rational mesh of Π at several heights |s| > 2 for
an 11-point kissing set in one open hemisphere (that plus A4 plus a
10-point opposite layer would be 41).  Exact inner products; a hit is
a construction.  A miss on a finite mesh is residue.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(ROOT))

from configs import _coord_sum, _dot, _norm2, _reflect_coord_sum, d5, is_kissing

F = Fraction


def a4_roots():
    return [p for p in d5() if _coord_sum(p) == 0]


def two_level_layers():
    plus_d5 = [p for p in d5() if _coord_sum(p) == F(2)]
    minus_d5 = [p for p in d5() if _coord_sum(p) == F(-2)]
    plus_q = [_reflect_coord_sum(p) for p in minus_d5]
    minus_q = [_reflect_coord_sum(p) for p in plus_d5]
    return {
        "plus_D5": plus_d5,
        "minus_D5": minus_d5,
        "plus_Q5": plus_q,
        "minus_Q5": minus_q,
    }


def in_pi(y):
    if sum(y) != 0:
        return False
    for i, j in combinations(range(5), 2):
        if y[i] - y[j] > 1:
            return False
    return True


def mesh_pi(den: int):
    """Rational points of Π with denominator `den` in the first 4 coords.

    y_4 = -sum_{0..3} y_i.  Then filter Π.
    """
    # |y_i| is at most 4/5 at vertices; pad to 1.
    vals = [F(k, den) for k in range(-den, den + 1)]
    out = []
    for a, b, c, d in product(vals, repeat=4):
        e = -(a + b + c + d)
        y = (a, b, c, d, e)
        if in_pi(y):
            out.append(y)
    return out


def lift(y, s):
    """x = y + (s/5) 1.  Need |x|^2 = 2, i.e. |y|^2 + s^2/5 = 2."""
    return tuple(y[i] + s / 5 for i in range(5))


def feasible_s2(y):
    n2 = _norm2(y)
    # s^2/5 = 2 - |y|^2 >= 4/5, so |y|^2 <= 6/5
    return F(2) - n2


def max_independent(pts, already, target):
    n = len(pts)
    adj_ok = [0] * n
    for i in range(n):
        if any(_dot(pts[i], a) > 1 for a in already):
            continue
        for j in range(i + 1, n):
            if any(_dot(pts[j], a) > 1 for a in already):
                continue
            if _dot(pts[i], pts[j]) <= 1:
                adj_ok[i] |= 1 << j
                adj_ok[j] |= 1 << i
    best = 0
    found = None

    def rec(used, start, sz):
        nonlocal best, found
        if found is not None:
            return
        rem = 0
        for v in range(start, n):
            if (used >> v) & 1:
                continue
            # adjacent to all used?
            if (adj_ok[v] & used) != used:
                continue
            rem += 1
        if sz + rem <= best:
            return
        if sz > best:
            best = sz
        if sz >= target:
            found = [k for k in range(n) if (used >> k) & 1]
            return
        for v in range(start, n):
            if (used >> v) & 1:
                continue
            if (adj_ok[v] & used) != used:
                continue
            rec(used | (1 << v), v + 1, sz + 1)

    rec(0, 0, 0)
    return best, found


def main() -> int:
    a4 = a4_roots()
    layers = two_level_layers()
    # Mesh at den=2 and den=3 (den=4 is 9^4 = 6561 * filter, still fine;
    # den=5 is 11^4 = 14641).
    meshes = {}
    constructions = []
    for den in (2, 3, 4):
        Y = mesh_pi(den)
        # Keep only strictly interior points (|y|^2 < 6/5) so |s| > 2.
        interior = []
        for y in Y:
            s2_over_5 = feasible_s2(y)
            if s2_over_5 <= 0:
                continue
            s2 = s2_over_5 * 5
            if s2 <= 4:
                continue
            # s = ±√(s2) is generally not rational.  We only lift when
            # s2 is a perfect square in Q, so the extra is exact over Q.
            # s2 = p/q; want p/q = (a/b)^2.
            num, den_s = s2.numerator, s2.denominator
            # perfect square rational iff num and den are squares
            def is_sq(m):
                r = int(m ** 0.5 + 0.5)
                return r * r == m
            if is_sq(num) and is_sq(den_s):
                s = F(int(num ** 0.5 + 0.5), int(den_s ** 0.5 + 0.5))
                interior.append((y, s))
                interior.append((y, -s))
        meshes[str(den)] = {
            "n_pi": len(Y),
            "n_exact_height": len(interior),
        }
        print(f"den={den} Π={len(Y)} exact-height extras={len(interior)}",
              flush=True)
        if not interior:
            continue
        pts = [lift(y, s) for y, s in interior]
        # Split by sign of s
        north = [p for p, (y, s) in zip(pts, interior) if s > 0]
        # Need 11 in one hemisphere, kissing A4
        best, found = max_independent(north, a4, target=11)
        meshes[str(den)]["north"] = len(north)
        meshes[str(den)]["north_best"] = best
        print(f"  north {len(north)} best {best}", flush=True)
        if found is not None:
            extra = [north[i] for i in found]
            # try to complete with a 10-point opposite layer + A4
            for lname, layer in layers.items():
                if _coord_sum(layer[0]) > 0:
                    continue
                cand = a4 + extra + layer
                if is_kissing(cand) and len(cand) >= 41:
                    constructions.append({
                        "den": den,
                        "layer": lname,
                        "n": len(cand),
                        "points": [[str(x) for x in p] for p in cand],
                    })

    report = {
        "meshes": meshes,
        "n_constructions": len(constructions),
        "found_41": bool(constructions),
        "constructions": constructions[:3],
        "comment": (
            "Rational mesh of the A4 polar at denominators 2,3,4.  Only "
            "heights whose s^2 is a square in Q are lifted (exact points). "
            "An 11-point northern set plus A4 plus a 10-point southern "
            "vertex layer would be a 41-point code.  A miss is residue."
        ),
    }
    (HERE / "a4_continuous.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("meshes", "n_constructions", "found_41")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
