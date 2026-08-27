#!/usr/bin/env python3
"""Census of 4-star unions: leftover n1<=21 after 3-star extras emptied.

A remaining 41-set has U not contained in any 3-star union, so the
star-cover of U is at least 4.  This file only counts 4-star unions
and the seeds they contain.  It does not search extras and does not
claim emptiness or a 41-code.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from sphere import extras_and_groups  # noqa: E402


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            out.append(bits)
    return out


def main() -> int:
    G = extras_and_groups(4)
    D = G["D"]
    seeds = list(G["groups"])
    stars = stars_of(D)
    hist = Counter()
    n_promising = 0
    max_ns = 0
    for comb in combinations(range(10), 4):
        U = stars[comb[0]] | stars[comb[1]] | stars[comb[2]] | stars[comb[3]]
        k = U.bit_count()
        ns = sum(1 for m in seeds if m & ~U == 0)
        hist[(k, ns)] += 1
        if ns >= k + 1 and k >= 19:
            n_promising += 1
        if ns > max_ns:
            max_ns = ns
    pairs = [
        {"k": k, "n_seeds": ns, "n_pools": c, "promising": ns >= k + 1 and k >= 19}
        for (k, ns), c in sorted(hist.items())
    ]
    report = {
        "n_pools": 210,
        "pairs": pairs,
        "n_promising_by_part_count": n_promising,
        "max_seeds_in_a_pool": max_ns,
        "found_41": False,
        "comment": (
            "Census only.  3-star extras are empty of a leftover 41-set.  "
            "A 4-star union can contain enough seeds to be promising by "
            "part-count; that is not a 41-code.  Did not claim tau5=40."
        ),
    }
    (HERE / "four_star_census.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n_pools": 210,
        "n_promising": n_promising,
        "max_ns": max_ns,
        "pairs": pairs,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
