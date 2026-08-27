#!/usr/bin/env python3
"""Geometry of the 240 missed-set seeds on the 40 D5 roots.

The 10 special octads are the coordinate-stars: for each axis i and
sign s, the eight D5 roots with x_i = s·4.  The 16 four-seeds inside a
star are the 2^4 ways to pick one sign on each of the other four axes.
Every four-seed lives in exactly one star.  The 80 six-seeds meet every
star in at most 5 points.

A seed-union is star-containing if it has 7 or 8 points of some star
(those are the k=7,8 promising families and their extensions).
Otherwise it is star-free.
"""

from __future__ import annotations

import json
from pathlib import Path

from sphere import extras_and_groups, d5_pts

HERE = Path(__file__).resolve().parent


def main() -> int:
    G = extras_and_groups(4)
    D = G["D"]
    groups = G["groups"]
    seeds = list(groups)
    assert len(D) == 40
    assert len(seeds) == 240

    stars = []
    star_names = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            idxs = []
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
                    idxs.append(j)
            assert bits.bit_count() == 8, (i, s, bits.bit_count())
            stars.append(bits)
            star_names.append(f"e{i}{'+' if s > 0 else '-'}")

    four = [m for m in seeds if m.bit_count() == 4]
    six = [m for m in seeds if m.bit_count() == 6]
    assert len(four) == 160 and len(six) == 80

    # each four-seed sits in exactly one star
    host = []
    for m in four:
        hits = [t for t, S in enumerate(stars) if (m & S) == m]
        assert len(hits) == 1, hits
        host.append(hits[0])
    hist = {name: host.count(t) for t, name in enumerate(star_names)}
    assert all(v == 16 for v in hist.values())

    # 16 four-seeds of a star = one from each opposite pair
    pair_ok = True
    for t, S in enumerate(stars):
        pts = [j for j in range(40) if (S >> j) & 1]
        # pair by the unique other nonzero axis
        axis = int(star_names[t][1])
        pairs = {}
        for j in pts:
            r = D[j]
            other = [a for a in range(5) if a != axis and r[a] != 0]
            assert len(other) == 1
            pairs.setdefault(other[0], []).append(j)
        assert sorted(pairs) == [a for a in range(5) if a != axis]
        assert all(len(v) == 2 for v in pairs.values())
        from itertools import product
        expected = []
        for choice in product(*[pairs[a] for a in sorted(pairs)]):
            m = 0
            for j in choice:
                m |= 1 << j
            expected.append(m)
        actual = [m for m in four if (m & S) == m]
        if set(actual) != set(expected):
            pair_ok = False

    six_max = []
    for m in six:
        six_max.append(max((m & S).bit_count() for S in stars))
    assert max(six_max) <= 5

    # pairwise star unions
    unions = set()
    for a in range(10):
        for b in range(a + 1, 10):
            unions.add((stars[a] | stars[b]).bit_count())

    report = {
        "n_stars": 10,
        "star_names": star_names,
        "star_sizes": [S.bit_count() for S in stars],
        "four_seeds_per_star": hist,
        "four_seeds_are_sign_choices": pair_ok,
        "six_seeds": 80,
        "six_max_meet_star": max(six_max),
        "pairwise_star_union_sizes": sorted(unions),
        "comment": (
            "10 coordinate-stars; 16 four-seeds per star are the sign "
            "choices on the other four axes.  Every four-seed lives in "
            "exactly one star.  Promising k=7,8 unions are the 7- and "
            "8-subsets of these stars."
        ),
    }
    path = HERE / "analyze_stars.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if pair_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
