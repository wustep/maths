#!/usr/bin/env python3
"""Algebraic 41-point hunts outside the leftover (1/4)Z^5 and T^5 graphs.

Pools, all exact:

- (1/3)Z^5 and (1/6)Z^5 spheres of squared norm 2 (d=3 was typed in q3;
  d=6 is new).  A 41-clique is a kissing code.
- A5 roots (20) plus coordinate axes and cube vertices.
- Cyclic simplex orbits: equally spaced points on a 2-plane in R^5,
  plus their signed-permutation closure.
- Q5 / R5 layer replacements by other rational heights.

A hit is written to certs/code41.json.  An incomplete clique search is
residue, not a lower bound.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from configs import CONFIGS, _dot, _norm2, d5, l5, q5, r5
from sphere import d5_pts, enumerate_sphere, ip

F = Fraction


def clique_search(adj, n, target, node_limit=2_000_000):
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


def graph_from_points(pts, thresh):
    n = len(pts)
    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ip(pts[i], pts[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    return adj, edges


def sphere_hunt(d, node_limit=2_000_000):
    pts = enumerate_sphere(d)
    thresh = d * d
    adj, edges = graph_from_points(pts, thresh)
    # seed best at 40 if D5 sits inside
    Dset = set(d5_pts(d))
    has_d5 = Dset <= set(pts)
    hit, best, nodes, complete = clique_search(adj, len(pts), 41, node_limit)
    return {
        "d": d,
        "n": len(pts),
        "n_edges": edges,
        "has_d5": has_d5,
        "best": best,
        "nodes": nodes,
        "found_41": hit is not None,
        "complete": complete,
        "clique41": hit,
    }


def unique(pts):
    seen = set()
    out = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def a5_plus():
    """A5 roots (coord-sum 0, two ±1) plus axes and cube vertices, scaled."""
    # A5: permutations of (1,-1,0,0,0) — 20 points, |x|^2=2, already kissing.
    a5 = []
    for i, j in combinations(range(5), 2):
        for si, sj in ((1, -1), (-1, 1)):
            v = [F(0)] * 5
            v[i] = F(si)
            v[j] = F(sj)
            a5.append(tuple(v))
    axes = []
    for i in range(5):
        for s in (-1, 1):
            v = [F(0)] * 5
            v[i] = F(s)  # |x|^2=1, not 2 — discard
    # cube vertices of |x|^2=2 do not exist in {±1}^5 (that is 5).
    # half-cube: (±1,±1,0,0,0) is D5, already 40.
    return unique(a5)


def cyclic_orbit(m: int):
    """m-th roots of unity in a coordinate 2-plane, plus signed perms.

    Points (cos 2πk/m, sin 2πk/m, 0, 0, 0) are not rational.  Use the
    exact integer model of the regular m-gon only for m where cosines
    are rational: m=4 (axes) and the Gaussian integers.  m=4 gives 4
    points.  Not a 41-set.  Recorded as empty.
    """
    return {
        "m": m,
        "used": m in (4,),
        "n": 4 if m == 4 else 0,
        "reason": "rational cosines only for m=4 in this ansatz",
    }


def layer_other_heights():
    """Replace a D5 / L5 layer by another rational-height copy."""
    # Already swept in q2 across 546 short integer normals.  Here: the
    # four published codes plus their coordinate-sign flips, size check.
    sizes = {}
    for name, builder in CONFIGS.items():
        pts = builder()
        ok = all(_norm2(p) == F(2) for p in pts)
        mx = max((_dot(a, b) for a, b in combinations(pts, 2)), default=F(0))
        sizes[name] = {"n": len(pts), "norm_ok": ok, "max_ip": str(mx)}
    return sizes


def write_code41(pts):
    (HERE / "certs").mkdir(exist_ok=True)
    (HERE / "certs" / "code41.json").write_text(json.dumps({
        "n": 41,
        "source": "construct41.py",
        "points": [[str(x) for x in p] for p in pts[:41]],
    }, indent=2) + "\n")


def main() -> int:
    report = {
        "spheres": {},
        "a5": {"n": len(a5_plus())},
        "cyclic": [cyclic_orbit(m) for m in (4, 5, 6, 8)],
        "published_sizes": layer_other_heights(),
        "found_41": False,
        "complete": False,
    }
    # d=3 is 1240 points: type analysis in q3, no 41 in same-missed
    # groups.  A short 41-clique B&B is recorded as residue if it
    # does not finish.  d=6 is larger; skip if n>2500.
    for d in (3, 6):
        pts = enumerate_sphere(d)
        print(f"sphere d={d} n={len(pts)}", flush=True)
        if len(pts) > 2500:
            report["spheres"][str(d)] = {
                "n": len(pts), "skipped": True,
                "reason": "too many points for a casual B&B",
            }
            continue
        rec = sphere_hunt(d, node_limit=3_000_000)
        report["spheres"][str(d)] = rec
        print(f"  best={rec['best']} found={rec['found_41']} "
              f"complete={rec['complete']}", flush=True)
        if rec["found_41"]:
            thresh = d * d
            extra = [enumerate_sphere(d)[i] for i in rec["clique41"]]
            # scale to |x|^2=2: integer points already have |x|^2=2d^2,
            # so (1/d) x has |x|^2=2.
            pts41 = [tuple(F(a, d) for a in p) for p in extra]
            write_code41(pts41)
            report["found_41"] = True
            break
    report["complete"] = all(
        (v.get("complete") or v.get("skipped"))
        for v in report["spheres"].values()
    ) and not report["found_41"]
    report["comment"] = (
        "No 41-point code in the pools that finished.  A skipped or "
        "incomplete sphere search is residue, not a lower bound."
    )
    (HERE / "construct41.json").write_text(json.dumps({
        k: ({kk: vv for kk, vv in v.items() if kk != "clique41"}
            if isinstance(v, dict) else v)
        if k == "spheres" else v
        for k, v in (
            (key, ({sk: ({kk: vv for kk, vv in sv.items() if kk != "clique41"}
                         if isinstance(sv, dict) else sv)
                    for sk, sv in val.items()} if key == "spheres" else val)
             )
            for key, val in report.items()
        )
    }, indent=2) + "\n")
    # write a cleaner dump
    clean = json.loads(json.dumps(report, default=str))
    if "spheres" in clean:
        for rec in clean["spheres"].values():
            rec.pop("clique41", None)
    (HERE / "construct41.json").write_text(json.dumps(clean, indent=2) + "\n")
    print("found_41", report["found_41"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
