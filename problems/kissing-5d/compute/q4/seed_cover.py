#!/usr/bin/env python3
"""How many actual missed-sets sit inside a k-set of D5 roots?

Same-missed extras are an independent set (q3 max_best=1). A clique of
extras therefore takes at most one vertex from each missed-set group.
A 41-set with n1 = 40-k needs k+1 extras, hence at least k+1 groups
whose missed sets are subsets of some k-set U.

This file rebuilds the 240 seeds and, for every k, reports the maximum
number of seeds contained in any k-set that contains at least one seed.
If that maximum is < k+1, the n1 = 40-k slice is empty with no clique
search.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def d5_pts(d):
    pts = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [0] * 5
            v[i] = si * d
            v[j] = sj * d
            pts.append(tuple(v))
    return pts


def ip(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] + a[4] * b[4]


def enumerate_sphere(d):
    target = 2 * d * d
    lim = 0
    while (lim + 1) * (lim + 1) <= target:
        lim += 1
    squares = {i * i: i for i in range(lim + 1)}
    pts = []
    for a in range(-lim, lim + 1):
        r2 = target - a * a
        for b in range(-lim, lim + 1):
            r3 = r2 - b * b
            if r3 < 0:
                continue
            for c in range(-lim, lim + 1):
                r4 = r3 - c * c
                if r4 < 0:
                    continue
                for e in range(-lim, lim + 1):
                    rem = r4 - e * e
                    if rem not in squares:
                        continue
                    f = squares[rem]
                    for s in ((f,) if f == 0 else (f, -f)):
                        pts.append((a, b, c, e, s))
    return pts


def group_edges(g, thresh):
    e = 0
    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            if ip(g[i], g[j]) <= thresh:
                e += 1
    return e


def analyse(d: int) -> dict:
    thresh = d * d
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    extras = [p for p in pts if p not in Dset]
    groups = defaultdict(list)
    for p in extras:
        m = 0
        for i, r in enumerate(D):
            if ip(p, r) > thresh:
                m |= 1 << i
        groups[m].append(p)

    seeds = list(groups)
    four = [m for m in seeds if m.bit_count() == 4]
    six = [m for m in seeds if m.bit_count() == 6]
    other = [m for m in seeds if m.bit_count() not in (4, 6)]
    edges_hist = Counter(group_edges(g, thresh) for g in groups.values())

    # For each seed, how many other seeds are subsets of a k-superset
    # is global: for k in 4..12, scan unique U generated from seeds.
    # Fast path: each pair/triple of seeds, record their union size and
    # then, for representative U, count contained seeds.
    # Complete for k<=8 via all k-supersets of 4-seeds (and 6-seeds).
    max_in = {}
    hist_in = {}
    empty_slice = {}
    for k in range(4, 13):
        seen = set()
        best = 0
        hist = Counter()
        # generate U from every seed of size <= k
        for m in seeds:
            pop = m.bit_count()
            if pop > k:
                continue
            rest = [i for i in range(40) if not ((m >> i) & 1)]
            need = k - pop
            if need == 0:
                cands = [m]
            else:
                cands = []
                for extra in combinations(rest, need):
                    U = m
                    for i in extra:
                        U |= 1 << i
                    cands.append(U)
            for U in cands:
                if U in seen:
                    continue
                seen.add(U)
                cnt = sum(1 for s in seeds if (s & ~U) == 0)
                hist[cnt] += 1
                if cnt > best:
                    best = cnt
        max_in[str(k)] = best
        hist_in[str(k)] = dict(sorted(hist.items()))
        empty_slice[str(k)] = best < (k + 1)
        print(f"d={d} k={k} n_U={len(seen)} max_seeds_in_U={best} "
              f"need={k+1} empty={best < k+1}", flush=True)

    return {
        "d": d,
        "n": len(pts),
        "n_extras": len(extras),
        "n_seeds": len(seeds),
        "n_four": len(four),
        "n_six": len(six),
        "n_other": len(other),
        "group_edge_hist": {str(a): b for a, b in sorted(edges_hist.items())},
        "groups_edgeless": edges_hist.get(0, 0) == len(groups),
        "max_seeds_in_k": max_in,
        "hist_seeds_in_k": hist_in,
        "slice_empty_by_part_count": empty_slice,
        "comment": (
            "If every same-missed group is edgeless, a clique takes at "
            "most one extra per seed. Then n1=40-k is empty whenever no "
            "k-set contains k+1 seeds."
        ),
    }


def main() -> int:
    out = {}
    for d in (4, 3, 2):
        out[str(d)] = analyse(d)
    path = HERE / "seed_cover.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
