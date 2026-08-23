#!/usr/bin/env python3
"""Verify the exact fourth-layer extension and its stored five-coloring."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
Q3 = HERE.parent / "q3"
sys.path.insert(0, str(Q1))

from lattice import rotate_rho  # noqa: E402
from udg import F, load_vtx, sqdist  # noqa: E402


def read_edges(path: Path, expected_n: int, expected_m: int) -> list[tuple[int, int]]:
    lines = path.read_text().splitlines()
    header = lines[0].split()
    if header != ["p", "edge", str(expected_n), str(expected_m)]:
        raise ValueError(f"unexpected edge header in {path}: {header}")
    edges = []
    for line in lines[1:]:
        tag, left, right = line.split()
        if tag != "e":
            raise ValueError(f"bad edge line in {path}: {line}")
        edge = (int(left) - 1, int(right) - 1)
        if edge[0] < 0 or edge[0] >= edge[1] or edge[1] >= expected_n:
            raise ValueError(f"bad edge endpoints in {path}: {line}")
        edges.append(edge)
    if len(edges) != expected_m or len(set(edges)) != expected_m:
        raise ValueError(f"edge count or uniqueness failure in {path}")
    return edges


def main() -> None:
    old_points = load_vtx(Q3 / "combined_union.vtx")
    committed = load_vtx(HERE / "rho4_combined.vtx")
    if len(old_points) != 2010 or committed[:2010] != old_points:
        raise ValueError("q4 coordinate prefix is not q3's exact coordinate list")

    layer = load_vtx(Q1 / "parts509.vtx")
    for _ in range(3):
        layer = [rotate_rho(point) for point in layer]
    expected_points = list(old_points)
    seen = set(expected_points)
    for point in layer:
        if point not in seen:
            seen.add(point)
            expected_points.append(point)
    if committed != expected_points or len(committed) != 2434:
        raise ValueError("q4 coordinates are not q3 plus the exact rho^3 layer")

    expected_edges = set(read_edges(Q3 / "combined_union.edge", 2010, 11766))
    one = F.from_int(1)
    new_incident = 0
    for right in range(2010, len(committed)):
        for left in range(right):
            if sqdist(committed[left], committed[right]) == one:
                expected_edges.add((left, right))
                new_incident += 1
    if new_incident != 2209 or len(expected_edges) != 13975:
        raise ValueError("exact fourth-layer edge counts changed")

    stored_edges = read_edges(HERE / "rho4_combined.edge", 2434, 13975)
    if sorted(expected_edges) != stored_edges:
        raise ValueError("stored edge list differs from the exact extension rebuild")

    colors = [
        int(value)
        for value in (HERE / "rho4_combined.5color.txt").read_text().split()
    ]
    if len(colors) != 2434 or any(color < 0 or color >= 5 for color in colors):
        raise ValueError("invalid coloring vector")
    for left, right in stored_edges:
        if colors[left] == colors[right]:
            raise ValueError(f"monochromatic unit edge {left}--{right}")
    counts = [colors.count(color) for color in range(5)]
    print(
        "rho4_combined: exact n=2434 m=13975 "
        f"(424 new vertices, 2209 new incident edges); "
        f"5-coloring verified; counts={counts}"
    )


if __name__ == "__main__":
    main()
