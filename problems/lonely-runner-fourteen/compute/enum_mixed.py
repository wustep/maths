"""Enumerate p-independent mixed obstructions by leftover r-column size."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

K, M = 13, 14


def R(i: int) -> set[int]:
    return {r for r in range(M) if (r * i) % M in (0, M - 1)}


RS = [set()] + [R(i) for i in range(1, K + 1)]

# FAIL bits only for a single r-column: 14 bits, one per s
def col_fail(i: int, val: int, r: int) -> int:
    msk = 0
    for s in range(M):
        if (s * val + r * i) % M in (0, M - 1):
            msk |= 1 << s
    return msk


def search_columns(zero_idx: list[int], rem_r: list[int]) -> list[list[int]]:
    """Unsaved assignments of complementary coords for leftover r-columns."""
    Z = set(zero_idx)
    free = [i for i in range(1, K + 1) if i not in Z]
    # each leftover r is a 14-bit column that must be filled
    need = [(r, (1 << M) - 1) for r in rem_r]
    hits: list[list[int]] = []
    vals = [0] * len(free)
    # cap
    MAXH = 50

    def rec(pos: int, cols: list[int]) -> None:
        if len(hits) >= MAXH:
            return
        if all(c == 0 for c in cols):
            v = [0] * K
            for i in Z:
                v[i - 1] = 0
            for j, i in enumerate(free):
                v[i - 1] = vals[j] if j < pos else -1
            hits.append(v)
            return
        if pos == len(free):
            return
        # prune: remaining free can they cover leftover bits?
        i = free[pos]
        leftover_pool = [0] * len(cols)
        for j2 in range(pos, len(free)):
            ii = free[j2]
            for val in range(1, M):
                for ci, r in enumerate(rem_r):
                    leftover_pool[ci] |= col_fail(ii, val, r)
        if any(cols[ci] & ~leftover_pool[ci] for ci in range(len(cols))):
            return
        for val in range(1, M):
            vals[pos] = val
            ncols = [cols[ci] & ~col_fail(i, val, rem_r[ci]) for ci in range(len(cols))]
            rec(pos + 1, ncols)

    rec(0, [(1 << M) - 1] * len(rem_r))
    return hits


def main() -> None:
    by_rem: dict[int, int] = Counter()
    n_full = 0
    n_mixed_pat = 0
    n_mixed_hit_capped = 0
    examples = []
    for mask in range(1, (1 << K) - 1):
        Z = [i + 1 for i in range(K) if mask >> i & 1]
        cov: set[int] = set()
        for i in Z:
            cov |= RS[i]
        rem = sorted(set(range(M)) - cov)
        if not rem:
            n_full += 1
            continue
        by_rem[len(rem)] += 1
        if len(rem) > 4:
            continue  # do small remain first; larger later if needed
        hits = search_columns(Z, rem)
        if hits:
            n_mixed_pat += 1
            n_mixed_hit_capped += len(hits)
            if len(examples) < 20:
                examples.append({"Z": Z, "rem_r": rem, "hit": hits[0], "nhits_capped": len(hits)})

    print("full", n_full)
    print("remain hist", dict(sorted(by_rem.items())))
    print("mixed_patterns_remain<=4", n_mixed_pat)
    print("examples", len(examples))
    for e in examples[:10]:
        print(e)

    out = {
        "full": n_full,
        "mixed_patterns_remain_le4": n_mixed_pat,
        "examples": examples,
    }
    d = Path(__file__).resolve().parent / "certs"
    d.mkdir(exist_ok=True)
    (d / "mixed_obstructions.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
