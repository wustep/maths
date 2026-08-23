#!/usr/bin/env python3
"""Rebuild every exact unit edge of the three-layer graph and check colors."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
sys.path.insert(0, str(Q1))

from udg import load_vtx, unit_edges  # noqa: E402


def read_edges(path):
    lines = path.read_text().splitlines()
    header = lines[0].split()
    if header != ["p", "edge", "1357", "6860"]:
        raise ValueError(f"unexpected edge header: {header}")
    edges = []
    for line in lines[1:]:
        tag, left, right = line.split()
        if tag != "e":
            raise ValueError(f"bad edge line: {line}")
        edges.append((int(left) - 1, int(right) - 1))
    if len(edges) != 6860:
        raise ValueError(f"stored edge count {len(edges)} != 6860")
    return edges


def main():
    points = load_vtx(HERE / "rho3_union.vtx")
    if len(points) != 1357:
        raise ValueError(f"coordinate count {len(points)} != 1357")
    rebuilt = unit_edges(points)
    stored = read_edges(HERE / "rho3_union.edge")
    if rebuilt != stored:
        raise ValueError("stored edge list differs from exact all-pairs rebuild")

    colors = [int(value) for value in (HERE / "rho3_union.5color.txt").read_text().split()]
    if len(colors) != 1357 or any(color < 0 or color >= 5 for color in colors):
        raise ValueError("invalid coloring vector")
    for left, right in rebuilt:
        if colors[left] == colors[right]:
            raise ValueError(f"monochromatic unit edge {left}--{right}")
    counts = [colors.count(color) for color in range(5)]
    print(f"rho3_union: exact n=1357 m=6860; 5-coloring verified; counts={counts}")


if __name__ == "__main__":
    main()
