"""Exact maxima for small n by diameter-bounded exhaustive search.

Normalisation: min=0, gcd=1. Diameter is searched up to a given cap.
A set of diameter D is represented as a bitset on {1,...,D} together
with 0. Incremental T-update when adding/removing a point.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import interval_t, t_count, affine_normalise  # noqa: E402


def delta_on_add(present: set[int], p: int) -> int:
    """How many new triples appear when p is added to present.

    New triples have p in at least one coordinate. The three roles
    (x, y, z) are counted separately; a triple with two p's is only
    the trivial (p,p,p), which is added once at the end.
    """
    d = 1  # (p,p,p)
    # p as x, y,z in old set
    for y in present:
        tot = p + 2 * y
        if tot % 3 == 0 and tot // 3 in present:
            d += 1
    # p as y, x,z in old set
    for x in present:
        tot = x + 2 * p
        if tot % 3 == 0 and tot // 3 in present:
            d += 1
    # p as z, x,y in old set
    target = 3 * p
    for x in present:
        #  x + 2y = 3p  =>  2y = 3p-x  => y = (3p-x)/2
        num = target - x
        if num % 2 == 0:
            y = num // 2
            if y in present:
                d += 1
    return d


def exhaustive(n: int, dmax: int) -> tuple[int, list[tuple[int, ...]], int]:
    """Max T among n-subsets of {0,...,dmax} containing 0.

    Returns (best_T, list of affine-normalised maximisers, n_sets_seen).
    """
    if n == 1:
        return 1, [(0,)], 1
    best = interval_t(n)
    best_sets: list[tuple[int, ...]] = [tuple(range(n))]
    seen = 0

    def rec(start: int, remaining: int, present: list[int], tcur: int) -> None:
        nonlocal best, best_sets, seen
        if remaining == 0:
            seen += 1
            s = tuple(present)
            if tcur > best:
                best = tcur
                best_sets = [affine_normalise(s)]
            elif tcur == best:
                ns = affine_normalise(s)
                if ns not in best_sets:
                    best_sets.append(ns)
            return
        # need `remaining` more points from start..dmax
        last_ok = dmax - remaining + 1
        for p in range(start, last_ok + 1):
            dlt = delta_on_add(set(present), p)
            present.append(p)
            rec(p + 1, remaining - 1, present, tcur + dlt)
            present.pop()

    rec(1, n - 1, [0], 1)
    return best, best_sets, seen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=1)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--dmax-mult", type=int, default=4, help="dmax = n * this")
    ap.add_argument("--dmax", type=int, default=0, help="override diameter cap")
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    rows = []
    for n in range(args.nmin, args.nmax + 1):
        dmax = args.dmax if args.dmax else min(n * args.dmax_mult, 40)
        # for n<=7 we can take a generous diameter
        if n <= 7:
            dmax = max(dmax, 24)
        best, sets, seen = exhaustive(n, dmax)
        it = interval_t(n)
        row = {
            "n": n,
            "dmax": dmax,
            "T_max_found": best,
            "T_interval": it,
            "beats_interval": best > it,
            "ratio": best / (n * n),
            "interval_ratio": it / (n * n),
            "n_sets_seen": seen,
            "n_maximisers": len(sets),
            "maximisers": [list(s) for s in sets[:12]],
        }
        rows.append(row)
        print(
            f"n={n:2d} dmax={dmax:2d} T={best:4d} I={it:4d} "
            f"ratio={best/(n*n):.5f} I-ratio={it/(n*n):.5f} "
            f"beat={best>it} seen={seen} #ext={len(sets)} "
            f"ex={list(sets[0]) if sets else None}",
            flush=True,
        )

    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
