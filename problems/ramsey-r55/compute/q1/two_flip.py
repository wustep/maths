#!/usr/bin/env python3
"""Radius-2 one-edge-flip ball of the 656 published (5,5,42)-graphs.

A second flip is tested with the same local K5 / I5 rule on the already
flipped graph. Colour-refinement types are compared to the published 194.
New types, if any, are recorded; this script does not claim a bound.
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import complement, dump_json, parse_graph6

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = Path(__file__).resolve().parent / "certs" / "two_flip.json"


def color_hist(nbr: list[int]) -> tuple:
    n = len(nbr)
    color = [nbr[i].bit_count() for i in range(n)]
    for _ in range(n + 2):
        keys = []
        for i in range(n):
            neigh_cols = []
            m = nbr[i]
            while m:
                b = m & -m
                neigh_cols.append(color[b.bit_length() - 1])
                m ^= b
            keys.append((color[i], tuple(sorted(neigh_cols))))
        ranks = {k: i for i, k in enumerate(sorted(set(keys)))}
        nxt = [ranks[k] for k in keys]
        if nxt == color:
            break
        color = nxt
    return tuple(sorted(Counter(color).items()))


def has_triangle_in_mask(nbr: list[int], mask: int) -> bool:
    m = mask
    while m:
        ubit = m & -m
        u = ubit.bit_length() - 1
        r = nbr[u] & (m ^ ubit)
        while r:
            vbit = r & -r
            v = vbit.bit_length() - 1
            if nbr[v] & r:
                return True
            r ^= vbit
        m ^= ubit
    return False


def flip_ok(nbr: list[int], u: int, v: int, is_edge: bool, n: int) -> bool:
    if is_edge:
        full = (1 << n) - 1
        common_non = full ^ (nbr[u] | nbr[v] | (1 << u) | (1 << v))
        c_nbr = [(~nbr[i]) & full & ~(1 << i) for i in range(n)]
        return not has_triangle_in_mask(c_nbr, common_non)
    return not has_triangle_in_mask(nbr, nbr[u] & nbr[v])


def main() -> int:
    t0 = time.time()
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    known = set()
    graphs = []
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        for side, g in (("stored", nbr), ("comp", complement(nbr))):
            known.add(color_hist(g))
            graphs.append((i, side, [x for x in g]))
    print(f"known types {len(known)}", flush=True)

    n1 = 0
    n2 = 0
    n2_new = 0
    new_sample = []
    for gi, (i, side, nbr) in enumerate(graphs):
        n = len(nbr)
        first = []
        for u in range(n):
            for v in range(u + 1, n):
                is_edge = bool((nbr[u] >> v) & 1)
                if flip_ok(nbr, u, v, is_edge, n):
                    first.append((u, v, is_edge))
        n1 += len(first)
        for u, v, e1 in first:
            nbr[u] ^= 1 << v
            nbr[v] ^= 1 << u
            for x in range(n):
                for y in range(x + 1, n):
                    if x == u and y == v:
                        continue
                    e2 = bool((nbr[x] >> y) & 1)
                    if not flip_ok(nbr, x, y, e2, n):
                        continue
                    n2 += 1
                    nbr[x] ^= 1 << y
                    nbr[y] ^= 1 << x
                    h = color_hist(nbr)
                    nbr[x] ^= 1 << y
                    nbr[y] ^= 1 << x
                    if h not in known:
                        n2_new += 1
                        if len(new_sample) < 20:
                            new_sample.append(
                                {"src": i, "side": side, "uv": [u, v], "xy": [x, y]}
                            )
            nbr[u] ^= 1 << v
            nbr[v] ^= 1 << u
        if (gi + 1) % 40 == 0:
            print(
                f"progress {gi+1}/{len(graphs)} n1={n1} n2={n2} new={n2_new}",
                flush=True,
            )

    summary = {
        "n_graphs": len(graphs),
        "n_known_types": len(known),
        "n_radius1": n1,
        "n_radius2": n2,
        "n_radius2_new_type": n2_new,
        "new_sample": new_sample,
        "seconds": round(time.time() - t0, 3),
        "note": (
            "Radius-2 walks of legal 1-flips. New 1-WL type is not a bound. "
            "Same type as the 656 is not an isomorphism test."
        ),
    }
    dump_json(str(OUT), summary)
    print(
        f"r1={n1} r2={n2} new_type={n2_new} sec={summary['seconds']}"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
