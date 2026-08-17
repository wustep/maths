#!/usr/bin/env python3
"""Start from the elementary two-AP cover and drop redundant points.

If a uniform fraction drops for every n, that is an all-n improvement of
the constant 2. We record the surviving ratio versus n.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import is_sum_cover, cover_stats
from constructions import two_ap

BEL = math.sqrt(8 / 3)
SQRT3 = math.sqrt(3)


def prune(n: int) -> dict:
    A = set(two_ap(n))
    assert is_sum_cover(A, n)
    m0 = len(A)
    # drop from the AP part first, then the interval, largest first
    a = math.ceil(math.sqrt(n))
    order = list(range(a - 1, 0, -1))  # interval, skip 0
    order += [(i * a) % n for i in range(a - 1, 0, -1)]
    # unique, preserve order
    seen = set()
    seq = []
    for x in order:
        x %= n
        if x not in seen and x in A and x != 0:
            seen.add(x)
            seq.append(x)
    for x in sorted(A, reverse=True):
        if x not in seen and x != 0:
            seq.append(x)
    kept = set(A)
    dropped = []
    for x in seq:
        trial = kept - {x}
        if is_sum_cover(trial, n):
            kept = trial
            dropped.append(x)
    st = cover_stats(kept, n)
    st.update(
        m0=m0,
        dropped=len(dropped),
        ratio0=m0 / math.sqrt(n),
        beat_bel=st["ratio"] < BEL,
        beat_sqrt3=st["ratio"] < SQRT3,
        dropped_res=dropped,
    )
    return st


def main():
    ns = [12, 20, 30, 42, 56, 72, 90, 110, 132, 156, 182, 210]
    # also Singer and square orders
    ns += [13, 31, 57, 25, 49, 64, 81, 121]
    rows = []
    for n in ns:
        rec = prune(n)
        print(
            f"n={n} m0={rec['m0']} m={rec['m']} dropped={rec['dropped']} "
            f"ratio={rec['ratio']:.4f} ok={rec['ok']} bel={rec['beat_bel']}",
            flush=True,
        )
        rec.pop("dropped_res", None)
        rows.append(rec)
    Path("compute/two_ap_prune.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
