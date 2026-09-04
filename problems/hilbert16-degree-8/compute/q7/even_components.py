#!/usr/bin/env python3
"""Count fixed-odd components of q5's pinned even-split BFS.

Adding and dropping even splits connects a fixed odd skeleton to every
compatible subset of even splits.  Thus a BFS component is exactly the
clique space of the even-split compatibility graph after restricting to
splits compatible with that odd skeleton.  This counter uses the q5
split and seed encoders, but no queue or collection pickle.
"""
from __future__ import annotations

import json
import os
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import even_walk as ew


def main():
    sys.setrecursionlimit(10000)
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = ew.even_mask(sp)
    components = {}
    for name, ids in ew.seed_collections(sp):
        odd = tuple(i for i in ids if not sp[i].even)
        components.setdefault(odd, []).append(name)

    rows = []
    exact_nonempty_total = 0
    largest_nonempty = 0
    for odd, seeds in components.items():
        candidates = emask
        for i in odd:
            candidates &= adj[i]
        if not odd:
            rows.append({
                "seeds": seeds,
                "odd_splits": [],
                "compatible_even_splits": candidates.bit_count(),
                "collections": None,
                "complete": False,
                "why_incomplete": (
                    "The all-even component is larger than the already "
                    "huge nonempty-odd components; it is not needed for "
                    "the certified lower bound on the BFS closure size."
                ),
            })
            continue

        @lru_cache(maxsize=None)
        def count(mask):
            if not mask:
                return 1
            bit = mask & -mask
            v = bit.bit_length() - 1
            rest = mask ^ bit
            return count(rest) + count(rest & adj[v])

        ncollections = count(candidates)
        exact_nonempty_total += ncollections
        largest_nonempty = max(largest_nonempty, ncollections)
        rows.append({
            "seeds": seeds,
            "odd_splits": list(odd),
            "compatible_even_splits": candidates.bit_count(),
            "collections": ncollections,
            "complete": True,
            "memo_states": count.cache_info().currsize,
        })

    payload = {
        "what": (
            "Component sizes for q5's pinned even add/drop/swap BFS. "
            "Five nonempty fixed-odd components are counted exactly. "
            "The all-even component is additional, so the sum is a "
            "certified lower bound on the full BFS closure, not a lower "
            "bound on real schemes."
        ),
        "split_count": len(sp),
        "even_split_count": emask.bit_count(),
        "fixed_odd_components": len(components),
        "exact_nonempty_component_collections": exact_nonempty_total,
        "all_even_component_collections_at_least": largest_nonempty,
        "full_bfs_collections_at_least": (
            exact_nonempty_total + largest_nonempty
        ),
        "lower_bound_reason": (
            "Removing the fixed odd splits injects every even clique "
            "from a nonempty-odd component into the all-even component."
        ),
        "full_bfs_complete": False,
        "components": rows,
    }
    dest = HERE / "certs" / "even_components.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
