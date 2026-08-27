#!/usr/bin/env python3
"""Project D6's 60 roots into 5-spaces and hunt a 41-clique.

Two exact models, both in the 5-space orthogonal to an integer normal n:

- equal-length: keep roots with a fixed |r·n|, no rescaling
- radial: drop the n-component and rescale each nonzero projection
  to squared norm 2 (compare after clearing denominators)

A 41-clique is a kissing code in S^4.
"""

from __future__ import annotations

import json
from itertools import combinations, product
from pathlib import Path

from cliqueutil import clique_search

HERE = Path(__file__).resolve().parent


def d6_roots():
    pts = []
    for i, j in combinations(range(6), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [0] * 6
            v[i], v[j] = si, sj
            pts.append(tuple(v))
    return pts


def ip6(a, b):
    return sum(x * y for x, y in zip(a, b))


def short_normals(lim=2, n2max=12):
    ns = []
    seen = set()
    for coords in product(range(-lim, lim + 1), repeat=6):
        n2 = sum(c * c for c in coords)
        if n2 == 0 or n2 > n2max:
            continue
        key = coords if coords > tuple(-c for c in coords) else tuple(-c for c in coords)
        if key in seen:
            continue
        seen.add(key)
        ns.append(coords)
    return ns


def equal_length_graph(roots, n, alpha2):
    """Roots with (r·n)^2 = alpha2, kissing of the raw projections."""
    nn = ip6(n, n)
    subset = [r for r in roots if ip6(r, n) ** 2 == alpha2]
    # |proj|^2 = 2 - alpha2/nn, thresh = |proj|^2 / 2 = 1 - alpha2/(2nn)
    # <proj a,b> = a·b - (a·n)(b·n)/nn
    # a·b - αβ/nn <= 1 - alpha2/(2nn)
    # 2 nn (a·b) - 2 αβ <= 2 nn - alpha2
    m = len(subset)
    if m < 2:
        return subset, [0] * m, 0
    adj = [0] * m
    edges = 0
    als = [ip6(r, n) for r in subset]
    rhs = 2 * nn - alpha2
    for i, j in combinations(range(m), 2):
        lhs = 2 * nn * ip6(subset[i], subset[j]) - 2 * als[i] * als[j]
        if lhs <= rhs:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
            edges += 1
    return subset, adj, edges


def radial_graph(roots, n):
    """Rescaled projections; drop zeros; merge parallel same-sign rays."""
    nn = ip6(n, n)
    raw = []
    for r in roots:
        alpha = ip6(r, n)
        pa2_num = 2 * nn - alpha * alpha  # |proj|^2 * nn
        if pa2_num <= 0:
            continue
        raw.append((r, alpha, pa2_num))
    # Dedup parallel same-sign projections.
    keep = []
    for i, (r, alpha, pa2) in enumerate(raw):
        unique = True
        for j, (s, beta, pb2) in enumerate(keep):
            # <proj r, proj s>^2 == |pr|^2|ps|^2 and <proj> > 0
            # (rs*nn - αβ)^2 == pa2 * pb2 / something wait:
            # <proj> = (rs*nn - αβ)/nn
            # |pr|^2 = pa2/nn, |ps|^2 = pb2/nn
            # <proj>^2 = |pr|^2|ps|^2 iff (rs*nn-αβ)^2 = pa2 * pb2
            cross = ip6(r, s) * nn - alpha * beta
            if cross > 0 and cross * cross == pa2 * pb2:
                unique = False
                break
        if unique:
            keep.append((r, alpha, pa2))
    m = len(keep)
    adj = [0] * m
    edges = 0
    for i, j in combinations(range(m), 2):
        r, alpha, pa2 = keep[i]
        s, beta, pb2 = keep[j]
        cross = ip6(r, s) * nn - alpha * beta  # <proj>*nn
        # want 2 <proj> <= |pr||ps| after scale-to-2:
        # 2 * (cross/nn) <= sqrt(pa2/nn)*sqrt(pb2/nn)
        # if cross <= 0: yes
        # else 4 cross^2 <= pa2 * pb2
        if cross <= 0 or 4 * cross * cross <= pa2 * pb2:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
            edges += 1
    return [t[0] for t in keep], adj, edges


def hunt_graph(adj, n, label):
    if n < 41:
        return {"n": n, "best": n, "found_41": False, "complete": True,
                "label": label}
    found, best, nodes, complete = clique_search(adj, n, 41, node_limit=500_000)
    return {
        "n": n, "best": best, "found_41": found is not None,
        "complete": complete, "nodes": nodes, "label": label,
        "clique": found,
    }


def main():
    roots = d6_roots()
    normals = short_normals()
    best = 0
    best_rec = None
    hit = None
    n_equal = 0
    n_radial = 0
    complete = True
    for n in normals:
        nn = ip6(n, n)
        # equal-length classes
        alphas = sorted({ip6(r, n) ** 2 for r in roots})
        for a2 in alphas:
            subset, adj, edges = equal_length_graph(roots, n, a2)
            n_equal += 1
            rec = hunt_graph(adj, len(subset), f"eq n2={nn} a2={a2}")
            complete = complete and rec["complete"]
            if rec["best"] > best:
                best = rec["best"]
                best_rec = {"normal": list(n), **{k: rec[k] for k in rec if k != "clique"}}
            if rec["found_41"]:
                hit = {"kind": "equal", "normal": list(n), "alpha2": a2,
                       "roots": [list(subset[i]) for i in rec["clique"][:41]]}
                break
        if hit:
            break
        subset, adj, edges = radial_graph(roots, n)
        n_radial += 1
        rec = hunt_graph(adj, len(subset), f"rad n2={nn}")
        complete = complete and rec["complete"]
        if rec["best"] > best:
            best = rec["best"]
            best_rec = {"normal": list(n), **{k: rec[k] for k in rec if k != "clique"}}
        if rec["found_41"]:
            hit = {"kind": "radial", "normal": list(n),
                   "roots": [list(subset[i]) for i in rec["clique"][:41]]}
            break
    report = {
        "n_d6": len(roots),
        "n_normals": len(normals),
        "n_equal_graphs": n_equal,
        "n_radial_graphs": n_radial,
        "best": best,
        "best_rec": best_rec,
        "found_41": hit is not None,
        "complete": complete and hit is None,
        "hit": hit,
        "comment": (
            "Exact projections of the 60 D6 roots orthogonal to short "
            "integer normals.  Incomplete clique search is residue."
        ),
    }
    (HERE / "proj_d6.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n_normals", "best", "found_41", "complete")}, indent=2))
    return 0 if not (hit and False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
