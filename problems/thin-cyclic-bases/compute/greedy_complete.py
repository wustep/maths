#!/usr/bin/env python3
"""Greedy completion of a seed set to a sum cover.

At each step add a residue that realises the most still-uncovered sums
(as seed+x or x+x). Record the added residues looking for a pattern.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import uncovered, cover_stats, counting_lower
from singer import singer_difference_set, is_prime

BEL = math.sqrt(8 / 3)


def greedy(n, seed, max_extra=None):
    A = set(a % n for a in seed)
    added = []
    miss = set(uncovered(A, n))
    budget = n if max_extra is None else max_extra
    while miss and len(added) < budget:
        best_x = None
        best_gain = -1
        # candidates: those that can cover something
        # evaluate all x not in A
        for x in range(n):
            if x in A:
                continue
            gain = 0
            if (2 * x) % n in miss:
                gain += 1
            for a in A:
                if (a + x) % n in miss:
                    gain += 1
            if gain > best_gain:
                best_gain = gain
                best_x = x
        if best_x is None or best_gain <= 0:
            break
        A.add(best_x)
        added.append((best_x, best_gain, len(miss) - best_gain))
        miss = set(uncovered(A, n))
    st = cover_stats(A, n)
    st["added"] = [x for x, _, _ in added]
    st["gains"] = added
    st["seed_m"] = len(seed)
    return st


def main():
    rows = []
    for q in [3, 5, 7, 11, 13]:
        if not is_prime(q):
            continue
        v, D = singer_difference_set(q)
        cap = max(4, int(BEL * math.sqrt(v) - len(D) + 3))
        st = greedy(v, D, max_extra=cap)
        st["kind"] = "singer-greedy"
        st["q"] = q
        print(
            f"q={q} n={v} seed={len(D)} added={len(st['added'])} "
            f"m={st['m']} ok={st['ok']} ratio={st['ratio']:.4f} "
            f"count={st['counting']} added_res={st['added']}",
            flush=True,
        )
        rows.append(
            {
                k: st[k]
                for k in (
                    "kind",
                    "q",
                    "n",
                    "m",
                    "ok",
                    "ratio",
                    "counting",
                    "added",
                    "seed_m",
                    "covered",
                )
            }
        )
    Path("compute/greedy_singer.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
