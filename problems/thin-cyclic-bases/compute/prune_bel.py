#!/usr/bin/env python3
"""Greedy-prune a BEL cover: drop generators that are redundant for 2A=T.

If a positive fraction can be dropped uniformly in q, that beats √(8/3).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bel import generators, add, pick_r, embed

BEL = math.sqrt(8 / 3)


def is_cover(A, r1, r2):
    n = r1 * r2 * 6
    seen = set()
    A = list(A)
    for i, a in enumerate(A):
        seen.add(add(a, a, r1, r2))
        if len(seen) == n:
            return True
        for b in A[i + 1 :]:
            seen.add(add(a, b, r1, r2))
            if len(seen) == n:
                return True
    return len(seen) == n


def prune(r1, r2):
    X, co, cu = generators(r1, r2)
    A = set(X) | {(0, 0, 0)}
    assert is_cover(A, r1, r2)
    # try to drop elements, largest-looking first (keep 0)
    order = sorted(A, key=lambda p: (-(p != (0, 0, 0)), p[2], p[0], p[1]))
    kept = set(A)
    dropped = []
    for p in order:
        if p == (0, 0, 0):
            continue
        trial = kept - {p}
        if is_cover(trial, r1, r2):
            kept = trial
            dropped.append(p)
    n = r1 * r2 * 6
    m = len(kept)
    return {
        "r1": r1,
        "r2": r2,
        "n": n,
        "m0": len(A),
        "m": m,
        "dropped": len(dropped),
        "ratio0": len(A) / math.sqrt(n),
        "ratio": m / math.sqrt(n),
        "bel": BEL,
        "beat": m / math.sqrt(n) < BEL,
    }


def main():
    rows = []
    for q in [13, 19, 25, 31]:
        rs = pick_r(q)
        if not rs:
            continue
        rec = prune(*rs)
        rec["q"] = q
        print(rec, flush=True)
        rows.append(rec)
    Path("compute/bel_prune.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
