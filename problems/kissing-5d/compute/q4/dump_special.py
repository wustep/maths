#!/usr/bin/env python3
"""Dump the 8-sets that contain 9+ seeds, and check larger supersets.

If every high-seed k-set is one of these 10 octads plus unused roots,
then the extras pool never grows past the ω=8 graphs already searched,
and n1 <= 31 is empty for any k whose target exceeds 8 — except k=9
already found best_extras=9, so some 9-set has a genuinely new pool.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from sphere import extras_and_groups

HERE = Path(__file__).resolve().parent


def main() -> int:
    G = extras_and_groups(4)
    seeds = list(G["groups"])
    special = []
    seen = set()
    for m in seeds:
        pop = m.bit_count()
        if pop > 8:
            continue
        rest = [i for i in range(40) if not ((m >> i) & 1)]
        for extra in combinations(rest, 8 - pop):
            U = m
            for i in extra:
                U |= 1 << i
            if U in seen:
                continue
            seen.add(U)
            contained = [s for s in seeds if (s & ~U) == 0]
            if len(contained) >= 9:
                special.append({
                    "U": U,
                    "U_bits": [i for i in range(40) if (U >> i) & 1],
                    "n_seeds": len(contained),
                    "n_four": sum(1 for s in contained if s.bit_count() == 4),
                    "n_six": sum(1 for s in contained if s.bit_count() == 6),
                    "pool": sum(len(G["groups"][s]) for s in contained),
                })
    print(f"special 8-sets: {len(special)}", flush=True)
    for s in special:
        print(s["U_bits"], "seeds", s["n_seeds"], "4s", s["n_four"],
              "6s", s["n_six"], "pool", s["pool"], flush=True)

    # pairwise unions of specials
    unions = set()
    for a, b in combinations(special, 2):
        u = a["U"] | b["U"]
        unions.add((u, u.bit_count()))
    print("pairwise special unions sizes",
          sorted({sz for _, sz in unions}), flush=True)

    (HERE / "special_octads.json").write_text(json.dumps({
        "n": len(special),
        "octads": special,
        "pairwise_union_sizes": sorted({sz for _, sz in unions}),
    }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
