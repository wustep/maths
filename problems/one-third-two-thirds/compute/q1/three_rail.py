#!/usr/bin/env python3
"""Width-3 rail posets: three chains x_i < x_{i+3} with optional long rungs.

This is the three-rail analogue of Peczarski's two-rail ladder. Rails
x_i < x_{i+3} are always present. Optional rungs are x_i < x_{i+4} and
x_i < x_{i+5}. At n=15 there are 11+10 = 21 optional rungs (2,097,152
subsets); the default census stops at a complete n=12 pass (2^{13}=8192)
and a sampled / greedy n=15 search, and records which of those is
exhaustive.

A width-3 poset with δ < 6/17 at n ≤ 14 would contradict Gupta v2's
published tail. The first unused order is 15.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(HERE))

from posetlib import Poset, balance, pair_counts_fb, transitive_closure  # noqa: E402
from ladders import n_ordinal_summands  # noqa: E402


def rail_poset(n: int, broken4: tuple[int, ...], broken5: tuple[int, ...]) -> Poset:
    rel = [0] * n
    for i in range(n - 3):
        rel[i] |= 1 << (i + 3)
    b4, b5 = set(broken4), set(broken5)
    for i in range(n - 4):
        if i not in b4:
            rel[i] |= 1 << (i + 4)
    for i in range(n - 5):
        if i not in b5:
            rel[i] |= 1 << (i + 5)
    succ = transitive_closure(n, rel)
    down = [0] * n
    for i in range(n):
        s = succ[i]
        while s:
            lsb = s & -s
            j = lsb.bit_length() - 1
            down[j] |= 1 << i
            s ^= lsb
    return Poset(n, down)


def delta_of(P: Poset):
    e, C = pair_counts_fb(P)
    num, den, e2, pair, _ = balance(P, C, e)
    g = gcd(num, den)
    return num // g, den // g, e2, pair


def census(n: int, skip_sums: bool = True):
    r4 = tuple(range(max(0, n - 4)))
    r5 = tuple(range(max(0, n - 5)))
    best = None
    n_seen = 0
    n_below = 0
    for k4 in range(len(r4) + 1):
        for b4 in combinations(r4, k4):
            for k5 in range(len(r5) + 1):
                for b5 in combinations(r5, k5):
                    P = rail_poset(n, b4, b5)
                    if skip_sums and n_ordinal_summands(P) != 1:
                        continue
                    n_seen += 1
                    num, den, e, pair = delta_of(P)
                    if num * 17 < den * 6:
                        n_below += 1
                    if best is None or num * best[1] < best[0] * den:
                        best = (num, den, b4, b5, e, pair)
    return best, n_seen, n_below


def greedy_n15():
    """Hill-climb on which +4/+5 rungs to break, starting from none broken."""
    n = 15
    r4 = list(range(n - 4))
    r5 = list(range(n - 5))
    broken4, broken5 = (), ()
    P = rail_poset(n, broken4, broken5)
    best = (*delta_of(P), broken4, broken5)
    improved = True
    steps = 0
    while improved and steps < 40:
        improved = False
        steps += 1
        candidates = []
        for i in r4:
            b4 = tuple(sorted(set(broken4) ^ {i}))
            candidates.append((b4, broken5))
        for i in r5:
            b5 = tuple(sorted(set(broken5) ^ {i}))
            candidates.append((broken4, b5))
        for b4, b5 in candidates:
            Q = rail_poset(n, b4, b5)
            if n_ordinal_summands(Q) != 1:
                continue
            num, den, e, pair = delta_of(Q)
            if num * best[1] < best[0] * den:
                best = (num, den, e, pair, b4, b5)
                broken4, broken5 = b4, b5
                improved = True
    return {
        "n": 15,
        "method": "greedy flip of +4/+5 rungs",
        "delta": [best[0], best[1]],
        "e": best[2],
        "pair": list(best[3]) if best[3] else None,
        "broken4": list(best[4]),
        "broken5": list(best[5]),
        "steps": steps,
        "beats_6_17": best[0] * 17 < best[1] * 6,
        "complete": False,
    }


def main():
    out = {"exhaustive": [], "note": "n<=12 exhaustive; n=15 greedy only"}
    for n in range(8, 13):
        best, n_seen, n_below = census(n)
        row = {
            "n": n,
            "min_delta": [best[0], best[1]],
            "broken4": list(best[2]),
            "broken5": list(best[3]),
            "e": best[4],
            "pair": list(best[5]) if best[5] else None,
            "n_non_sum": n_seen,
            "n_below_6_17": n_below,
            "complete": True,
        }
        out["exhaustive"].append(row)
        print(
            f"n={n} min {best[0]}/{best[1]} e={best[4]} "
            f"seen={n_seen} below_6/17={n_below}",
            flush=True,
        )
        if n <= 14 and n_below:
            raise AssertionError(f"width-3 rail below 6/17 at n={n}")
    print("n=15 greedy")
    out["n15_greedy"] = greedy_n15()
    print(
        f"  greedy δ={out['n15_greedy']['delta'][0]}/{out['n15_greedy']['delta'][1]} "
        f"beats_6_17={out['n15_greedy']['beats_6_17']}"
    )
    path = HERE / "three_rail.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
