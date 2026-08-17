#!/usr/bin/env python3
"""Color-refinement types of the 656 graphs vs their 1-flip (5,5) neighbours."""

from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

from r55lib import complement, dump_json, parse_graph6

ROOT = Path(__file__).resolve().parent
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = ROOT / "certs" / "flip_types.json"


def color_hist(nbr: list[int]) -> tuple:
    """1-dimensional Weisfeiler–Leman colour histogram (stable)."""
    n = len(nbr)
    color = [nbr[i].bit_count() for i in range(n)]
    for _ in range(n + 2):
        keys = []
        for i in range(n):
            neigh_cols = []
            m = nbr[i]
            while m:
                b = m & -m
                j = b.bit_length() - 1
                neigh_cols.append(color[j])
                m ^= b
            keys.append((color[i], tuple(sorted(neigh_cols))))
        ranks = {k: i for i, k in enumerate(sorted(set(keys)))}
        nxt = [ranks[k] for k in keys]
    return tuple(sorted(Counter(color).items()))


def has_triangle_in_mask(nbr: list[int], mask: int) -> bool:
    m = mask
    while m:
        ubit = m & -m
        u = ubit.bit_length() - 1
        rest = m ^ ubit
        r = nbr[u] & rest
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
    known = {}
    graphs = []
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        for side, g in (("stored", nbr), ("comp", complement(nbr))):
            h = color_hist(g)
            known.setdefault(h, []).append((i, side))
            graphs.append((i, side, g))
    print(f"known color types: {len(known)} from {len(graphs)} graphs", flush=True)

    new_types = []
    n_flips_ok = 0
    type_match = 0
    for i, side, nbr in graphs:
        n = len(nbr)
        for u in range(n):
            for v in range(u + 1, n):
                is_edge = (nbr[u] >> v) & 1
                if not flip_ok(nbr, u, v, bool(is_edge), n):
                    continue
                n_flips_ok += 1
                nbr[u] ^= 1 << v
                nbr[v] ^= 1 << u
                h = color_hist(nbr)
                nbr[u] ^= 1 << v
                nbr[v] ^= 1 << u
                if h in known:
                    type_match += 1
                else:
                    new_types.append(
                        {
                            "src": i,
                            "side": side,
                            "uv": [u, v],
                            "op": "del" if is_edge else "add",
                            "hist": [list(x) for x in h],
                        }
                    )
    summary = {
        "n_known_graphs": len(graphs),
        "n_known_color_types": len(known),
        "n_one_flip_55": n_flips_ok,
        "n_flip_matching_known_type": type_match,
        "n_flip_new_type": len(new_types),
        "new_types": new_types[:50],
        "seconds": round(time.time() - t0, 3),
    }
    dump_json(str(OUT), summary)
    print(
        f"ok_flips={n_flips_ok} match_type={type_match} new_type={len(new_types)} "
        f"known_types={len(known)} sec={summary['seconds']}"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
