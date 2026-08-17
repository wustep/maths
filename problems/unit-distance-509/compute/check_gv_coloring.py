#!/usr/bin/env python3
"""Check a stored 4-coloring of G-v against the exact unit-distance graph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from udg import load_vtx, unit_edges


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("coloring", type=Path)
    ap.add_argument("--missing", type=int, required=True)
    args = ap.parse_args()
    pts = load_vtx(args.vtx)
    edges = unit_edges(pts)
    line = [ln for ln in args.coloring.read_text().splitlines() if not ln.startswith("#")][-1]
    colors = [int(x) for x in line.split()]
    if len(colors) != len(pts):
        print(f"FAIL length {len(colors)} != {len(pts)}")
        return 1
    if colors[args.missing] != -1:
        print(f"FAIL vertex {args.missing} should be uncolored")
        return 1
    bad = []
    for a, b in edges:
        if a == args.missing or b == args.missing:
            continue
        if colors[a] == colors[b]:
            bad.append((a, b))
    if bad:
        print(f"FAIL {len(bad)} monochromatic unit edges, e.g. {bad[0]}")
        return 1
    used = [c for c in colors if c >= 0]
    if any(c not in (0, 1, 2, 3) for c in used):
        print("FAIL color not in 0..3")
        return 1
    print(f"PASS G-{args.missing} is properly 4-colored; {len(used)} vertices")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
