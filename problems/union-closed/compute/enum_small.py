"""Enumerate separating union-closed families on n ≤ 5 (n=6 optional)
and record exact max-frequency / |F|.

Not a new finite frontier (n≤12 is known).  This is a replayable
verifier for the small-n classification and a check that the
power-set tightness 1/2 is achieved.
"""

from __future__ import annotations

import json
from pathlib import Path


def popcount(x: int) -> int:
    return x.bit_count()


def is_union_closed(mask: int, n: int) -> bool:
    """mask bit i = set-with-bits i is present.  Universe [n], 2^n possible sets."""
    N = 1 << n
    present = [(mask >> i) & 1 for i in range(N)]
    for a in range(N):
        if not present[a]:
            continue
        for b in range(a, N):
            if not present[b]:
                continue
            if not present[a | b]:
                return False
    return True


def freq_and_size(mask: int, n: int):
    N = 1 << n
    size = 0
    cnt = [0] * n
    for s in range(N):
        if (mask >> s) & 1:
            size += 1
            for i in range(n):
                if s & (1 << i):
                    cnt[i] += 1
    if size == 0:
        return None
    return size, max(cnt), cnt


def enum_n(n: int, require_full_universe: bool = True):
    N = 1 << n
    # bit 0 = empty set; we allow it
    recs = []
    best = 1.0  # min of max-freq / size over nontrivial families
    best_mask = None
    n_uc = 0
    # skip empty family (mask=0) and {∅} (mask=1)
    for mask in range(2, 1 << N):
        # require the full union to be [n]: some set has all bits? more precisely
        # the OR of all members equals (1<<n)-1
        if require_full_universe:
            u = 0
            for s in range(N):
                if (mask >> s) & 1:
                    u |= s
            if u != N - 1:
                continue
        if not is_union_closed(mask, n):
            continue
        fs = freq_and_size(mask, n)
        if fs is None:
            continue
        size, mx, cnt = fs
        if size <= 1:
            continue
        n_uc += 1
        ratio = mx / size
        recs.append((ratio, size, mx, mask, cnt))
        if ratio < best:
            best = ratio
            best_mask = mask
    recs.sort()
    return {
        "n": n,
        "n_uc_full_universe": n_uc,
        "min_abundance": None if not recs else recs[0][0],
        "at_size": None if not recs else recs[0][1],
        "at_maxfreq": None if not recs else recs[0][2],
        "n_tight_half": sum(1 for r in recs if abs(r[0] - 0.5) < 1e-15),
        "n_strictly_above_half": sum(1 for r in recs if r[0] > 0.5 + 1e-15),
        "worst_10": [
            {
                "abundance": r[0],
                "size": r[1],
                "maxfreq": r[2],
                "mask": r[3],
                "counts": r[4],
            }
            for r in recs[:10]
        ],
    }


def main():
    out = {}
    for n in (1, 2, 3, 4):
        print("n", n, flush=True)
        out[str(n)] = enum_n(n)
        print("  ", out[str(n)]["n_uc_full_universe"],
              "min", out[str(n)]["min_abundance"], flush=True)
    path = Path(__file__).resolve().parent / "enum_small.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
