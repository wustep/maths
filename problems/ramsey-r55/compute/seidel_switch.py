#!/usr/bin/env python3
"""Seidel switching on 1 and 2 vertices of each of the 656 graphs."""

from __future__ import annotations

import time
from pathlib import Path

from r55lib import (
    complement,
    dump_json,
    is_ramsey,
    n_edges,
    parse_graph6,
    to_graph6,
)
from flip_types import color_hist

ROOT = Path(__file__).resolve().parent
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = ROOT / "certs" / "seidel_switch.json"


def switch(nbr: list[int], mask: int) -> list[int]:
    """Flip every edge between mask and its complement. Copy."""
    n = len(nbr)
    full = (1 << n) - 1
    out = list(nbr)
    for i in range(n):
        if (mask >> i) & 1:
            # flip all edges from i to V\mask except loops
            out[i] ^= (full ^ mask) & ~(1 << i)
        else:
            out[i] ^= mask
    return out


def main() -> int:
    t0 = time.time()
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    known = {}
    graphs = []
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        for side, g in (("stored", nbr), ("comp", complement(nbr))):
            known.setdefault(color_hist(g), []).append((i, side))
            graphs.append((i, side, g))

    new1 = []
    ok1 = match1 = 0
    new2 = []
    ok2 = match2 = 0
    n = 42
    for i, side, nbr in graphs:
        # 1-vertex switches
        for v in range(n):
            g = switch(nbr, 1 << v)
            if not is_ramsey(g):
                continue
            ok1 += 1
            h = color_hist(g)
            if h in known:
                match1 += 1
            else:
                new1.append({"src": i, "side": side, "set": [v], "g6": to_graph6(g),
                             "edges": n_edges(g)})
        # 2-vertex switches
        for u in range(n):
            for v in range(u + 1, n):
                g = switch(nbr, (1 << u) | (1 << v))
                if not is_ramsey(g):
                    continue
                ok2 += 1
                h = color_hist(g)
                if h in known:
                    match2 += 1
                else:
                    new2.append({"src": i, "side": side, "set": [u, v],
                                 "g6": to_graph6(g), "edges": n_edges(g)})
        if i % 40 == 0 and side == "stored":
            print(f"progress {i} ok1={ok1} new1={len(new1)} ok2={ok2} new2={len(new2)}",
                  flush=True)

    rec = {
        "n_graphs": len(graphs),
        "known_types": len(known),
        "switch1_55": ok1,
        "switch1_known_type": match1,
        "switch1_new_type": len(new1),
        "switch2_55": ok2,
        "switch2_known_type": match2,
        "switch2_new_type": len(new2),
        "new1": new1[:20],
        "new2": new2[:20],
        "seconds": round(time.time() - t0, 3),
    }
    dump_json(str(OUT), rec)
    print(rec)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
