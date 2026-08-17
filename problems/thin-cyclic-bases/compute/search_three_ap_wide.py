#!/usr/bin/env python3
"""Wider 3-AP search for a few ell: any n in the BEL-beating window,
more (d,e) pairs. Looking for even one infinite-looking pattern."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, counting_lower

BEL = math.sqrt(8 / 3)


def three_ap(n, d, e, ell):
    A = set(range(ell))
    for i in range(ell):
        A.add((i * d) % n)
        A.add((i * e) % n)
    return A


def search_ell(ell):
    m = 3 * ell
    n_hi = min(m * (m + 1) // 2, int((m / math.sqrt(2)) ** 2) + ell)
    n_lo = max(2 * ell * ell, math.ceil((m / BEL) ** 2))
    ds = []
    for k in range(1, ell + 4):
        ds.extend([k, k * ell, k * ell + 1, k * ell - 1, k * (ell + 1), k * (ell - 1) or 1])
    ds = sorted({d for d in ds if d > 1})
    hits = []
    # subsample n: step to keep this finite
    step = max(1, (n_hi - n_lo) // 40)
    for n in range(n_lo, n_hi + 1, step):
        if counting_lower(n) > m:
            continue
        for i, d in enumerate(ds):
            if d % n == 0:
                continue
            for e in ds[i + 1 :]:
                if e % n == 0 or e % n == d % n:
                    continue
                A = three_ap(n, d, e, ell)
                st = cover_stats(A, n)
                if st["ok"] and st["ratio"] < BEL:
                    st.update(d=d % n, e=e % n, ell=ell)
                    hits.append(st)
                    return hits
    return hits


def main():
    allh = []
    for ell in range(5, 13):
        h = search_ell(ell)
        print(f"ell={ell} hits={len(h)}", flush=True)
        if h:
            x = h[0]
            print(f"  n={x['n']} m={x['m']} r={x['ratio']:.4f} d={x['d']} e={x['e']}")
            allh.extend(h)
    Path("compute/three_ap_wide.json").write_text(json.dumps(allh, indent=2))


if __name__ == "__main__":
    main()
