#!/usr/bin/env python3
"""Peczarski ladders with broken rungs, independently counted.

Definition (Peczarski, Exp. Math. 28 (2019), §1; as used by Gupta
arXiv:2607.23926v2): on {x_0,...,x_{n-1}} take x_i < x_{i+2} for every i,
add the rungs x_i < x_{i+3} for every i not listed as broken, and close
transitively. Gupta writes L_{n,i_1,...,i_k} for broken rungs i_1,...,i_k
(0-based indices in 0..n-4).

Linear-extension counts use the parent folder's two pair counters.
A ladder that splits into more than one incomparability component is a
nontrivial ordinal sum and is skipped when reporting a 'non-sum' minimum,
matching Peczarski's restriction and Gupta Table 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))

from posetlib import Poset, balance, pair_counts_fb, transitive_closure


# Gupta / Peczarski Table 1 (non-sum ladder minima).
PUBLISHED = {
    7: ((9, 25), (1, 2)),
    8: ((17, 46), (1, 2, 3)),
    9: ((6, 17), (1, 2, 3, 4)),
    10: ((37, 106), (1, 5)),
    11: ((20, 57), (1, 6)),
    12: ((97, 277), (1, 7)),
    13: ((157, 448), (1, 8)),
    14: ((254, 725), (1, 9)),
    15: (None, (1, 5, 6, 10)),  # Gupta quotes the broken set, not the fraction
    17: (None, (1, 5, 8, 12)),
}


def ladder_up(n: int, broken: tuple[int, ...]) -> list[int]:
    """Strict upper-set masks of L_{n, broken}."""
    rel = [0] * n
    for i in range(n - 2):
        rel[i] |= 1 << (i + 2)
    broken_set = set(broken)
    for i in range(n - 3):
        if i not in broken_set:
            rel[i] |= 1 << (i + 3)
    return transitive_closure(n, rel)


def ladder_poset(n: int, broken: tuple[int, ...] = ()) -> Poset:
    succ = ladder_up(n, broken)
    down = [0] * n
    for i in range(n):
        s = succ[i]
        while s:
            lsb = s & -s
            j = lsb.bit_length() - 1
            down[j] |= 1 << i
            s ^= lsb
    return Poset(n, down)


def n_ordinal_summands(P: Poset) -> int:
    """Connected components of the incomparability graph."""
    n = P.n
    full = (1 << n) - 1
    unseen = full
    count = 0
    while unseen:
        bit = unseen & -unseen
        root = bit.bit_length() - 1
        frontier = bit
        unseen ^= bit
        while frontier:
            x = (frontier & -frontier).bit_length() - 1
            frontier ^= frontier & -frontier
            inc = full ^ P.down[x] ^ P.succ[x] ^ (1 << x)
            add = inc & unseen
            unseen ^= add
            frontier |= add
        count += 1
    return count


def delta_of(P: Poset) -> tuple[int, int, int, tuple]:
    e, C = pair_counts_fb(P)
    num, den, e2, pair, _ = balance(P, C, e)
    g = gcd(num, den)
    return num // g, den // g, e2, pair


def worst_ladder(n: int, skip_sums: bool = True):
    """Least δ over broken-rung ladders. Returns (frac, broken, e, pair, n_seen)."""
    rungs = tuple(range(max(0, n - 3)))
    best = None
    n_seen = 0
    n_skip = 0
    for k in range(len(rungs) + 1):
        for broken in combinations(rungs, k):
            P = ladder_poset(n, broken)
            if skip_sums and n_ordinal_summands(P) != 1:
                n_skip += 1
                continue
            n_seen += 1
            num, den, e, pair = delta_of(P)
            if best is None or num * best[1] < best[0] * den:
                best = (num, den, broken, e, pair)
    return best, n_seen, n_skip


def named(n: int, broken: tuple[int, ...]) -> dict:
    P = ladder_poset(n, broken)
    num, den, e, pair = delta_of(P)
    return {
        "n": n,
        "broken": list(broken),
        "delta": [num, den],
        "e": e,
        "pair": list(pair) if pair else None,
        "width": P.width_lower() if n <= 16 else None,
        "n_summands": n_ordinal_summands(P),
    }


def replay_published() -> list[dict]:
    rows = []
    for n, (frac, broken) in PUBLISHED.items():
        row = named(n, broken)
        row["published_delta"] = list(frac) if frac else None
        if frac:
            if tuple(row["delta"]) != frac:
                raise AssertionError(
                    f"L_{n},{broken}: got {row['delta']} want {frac}"
                )
            if row["n_summands"] != 1:
                raise AssertionError(f"L_{n} unexpectedly splits")
        rows.append(row)
        print(
            f"  L_{n},{','.join(map(str, broken))}  "
            f"δ={row['delta'][0]}/{row['delta'][1]}  e={row['e']}  "
            f"summands={row['n_summands']}"
        )
    return rows


def census_range(n0: int, n1: int) -> list[dict]:
    out = []
    for n in range(n0, n1 + 1):
        best, n_seen, n_skip = worst_ladder(n)
        if best is None:
            raise RuntimeError(f"no non-sum ladder at n={n}")
        num, den, broken, e, pair = best
        row = {
            "n": n,
            "min_delta": [num, den],
            "broken": list(broken),
            "e": e,
            "pair": list(pair) if pair else None,
            "n_non_sum": n_seen,
            "n_skipped_sums": n_skip,
        }
        if n in PUBLISHED and PUBLISHED[n][0]:
            pub = PUBLISHED[n][0]
            if (num, den) != pub:
                raise AssertionError(f"n={n} min {num}/{den} != published {pub}")
            if tuple(broken) != PUBLISHED[n][1]:
                # Dual or other labelling of the same poset is allowed only if
                # the fraction matches; still record the mismatch.
                row["published_broken"] = list(PUBLISHED[n][1])
                row["broken_mismatch"] = True
        out.append(row)
        print(
            f"n={n} min {num}/{den}  L_{n},{','.join(map(str, broken))}  "
            f"e={e}  non-sum={n_seen} skipped_sums={n_skip}",
            flush=True,
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", action="store_true", help="named published ladders")
    ap.add_argument("--census", type=int, nargs=2, metavar=("N0", "N1"))
    args = ap.parse_args()
    if not args.replay and not args.census:
        args.replay = True
        args.census = (7, 18)

    path = HERE / "ladder_census.json"
    blob = {}
    if path.exists():
        blob = json.loads(path.read_text())
    if args.replay:
        print("named published ladders")
        blob["named"] = replay_published()
        named_path = HERE / "ladder_named.json"
        named_path.write_text(json.dumps({"named": blob["named"]}, indent=2) + "\n")
        print(f"wrote {named_path}")
    if args.census:
        print(f"non-sum ladder census {args.census[0]}..{args.census[1]}")
        blob["census"] = census_range(args.census[0], args.census[1])
        path.write_text(json.dumps(blob, indent=2) + "\n")
        print(f"wrote {path}")
    elif args.replay and "census" not in blob:
        # replay-only: do not clobber a committed census
        pass


if __name__ == "__main__":
    main()
