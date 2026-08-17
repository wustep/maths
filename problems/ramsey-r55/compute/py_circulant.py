#!/usr/bin/env python3
"""Independent Python circulant (5,5) census. Cross-check of circulant_census.c."""

from __future__ import annotations

import sys
import time

from r55lib import circulant_nbr, dump_json, is_ramsey, legal_degree_range


def main() -> int:
    n = int(sys.argv[1])
    lo, hi = legal_degree_range(n)
    nd = n // 2
    half = n // 2 if n % 2 == 0 else None
    hits = []
    scanned = 0
    legal = 0
    t0 = time.time()

    # iterative Gray-ish recursion via integer mask
    # prune on degree as we build
    chosen = [0] * (nd + 1)

    def rec(dist: int, deg: int) -> None:
        nonlocal scanned, legal
        if deg > hi:
            return
        if dist > nd:
            scanned += 1
            if deg < lo:
                return
            legal += 1
            S = [i for i in range(1, nd + 1) if chosen[i]]
            nbr = circulant_nbr(n, S)
            if is_ramsey(nbr):
                hits.append({"S": S, "deg": deg})
            return
        add = 1 if dist == half else 2
        rem = 0
        for i in range(dist + 1, nd + 1):
            rem += 1 if i == half else 2
        if deg + rem < lo:
            return
        chosen[dist] = 0
        rec(dist + 1, deg)
        chosen[dist] = 1
        rec(dist + 1, deg + add)
        chosen[dist] = 0

    rec(1, 0)
    out = {
        "n": n,
        "deg": [lo, hi],
        "scanned": scanned,
        "legal": legal,
        "hits": len(hits),
        "hit_list": hits,
        "seconds": round(time.time() - t0, 3),
    }
    dest = f"certs/py_circulant_{n}.json"
    dump_json(dest, out)
    print(f"n={n} scanned={scanned} legal={legal} hits={len(hits)} sec={out['seconds']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
