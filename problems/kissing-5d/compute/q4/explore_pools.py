#!/usr/bin/env python3
"""Quick inventory of the q4 hunt pools (sizes, types, D5-degrees)."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
import sys

from sphere import d5_pts, enumerate_sphere, ip  # noqa: E402


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def sphere_inventory(d):
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    thresh = d * d
    extras = [p for p in pts if p not in Dset]
    types = Counter(type_key(p) for p in extras)
    deg_hist = Counter()
    missed_groups = defaultdict(list)
    for p in extras:
        miss = 0
        deg = 0
        for i, r in enumerate(D):
            if ip(p, r) <= thresh:
                deg += 1
            else:
                miss |= 1 << i
        deg_hist[deg] += 1
        missed_groups[miss].append(p)
    gsz = Counter(len(v) for v in missed_groups.values())
    return {
        "d": d,
        "n": len(pts),
        "n_extras": len(extras),
        "types": {str(k): v for k, v in sorted(types.items())},
        "d5_deg_hist": dict(sorted(deg_hist.items())),
        "n_missed_groups": len(missed_groups),
        "group_size_hist": dict(sorted(gsz.items())),
        "max_d5_deg": max(deg_hist) if deg_hist else None,
    }


def a5_hyperplane(target):
    """Z^6 points with sum 0 and |x|^2 = target."""
    lim = 0
    while (lim + 1) ** 2 <= target:
        lim += 1
    pts = []
    for coords in product(range(-lim, lim + 1), repeat=6):
        if sum(coords) != 0:
            continue
        if sum(c * c for c in coords) == target:
            pts.append(coords)
    types = Counter(type_key(p) for p in pts)
    return {"target": target, "n": len(pts),
            "types": {str(k): v for k, v in sorted(types.items())}}


def d6_roots():
    pts = []
    for i, j in combinations(range(6), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [0] * 6
            v[i], v[j] = si, sj
            pts.append(tuple(v))
    return pts


def main():
    for d in (3, 5, 6):
        rec = sphere_inventory(d)
        print(f"=== (1/{d})Z^5 n={rec['n']} extras={rec['n_extras']} "
              f"max_d5_deg={rec['max_d5_deg']} groups={rec['n_missed_groups']} "
              f"gsz={rec['group_size_hist']}")
        print("  types", rec["types"])
        print("  deg", rec["d5_deg_hist"])
    for t in (2, 8, 18, 32):
        rec = a5_hyperplane(t)
        print(f"=== A5-hyperplane |x|^2={t} n={rec['n']} types={rec['types']}")
    print("D6 roots", len(d6_roots()))


if __name__ == "__main__":
    main()
