#!/usr/bin/env python3
"""Verify the exact union decomposition, cross edges, and stored coloring."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q1))

from udg import F, load_vtx, sqdist  # noqa: E402


def read_edges(path, expected_n, expected_m):
    lines = path.read_text().splitlines()
    if lines[0].split() != ["p", "edge", str(expected_n), str(expected_m)]:
        raise ValueError(f"unexpected header in {path}")
    edges = []
    for line in lines[1:]:
        tag, left, right = line.split()
        if tag != "e":
            raise ValueError(f"bad line in {path}: {line}")
        edges.append((int(left) - 1, int(right) - 1))
    if len(edges) != expected_m:
        raise ValueError(f"edge count in {path} differs from header")
    return edges


def main():
    reserve = load_vtx(Q1 / "reserve_union.vtx")
    rotation = load_vtx(Q2 / "rho3_union.vtx")
    committed = load_vtx(HERE / "combined_union.vtx")

    expected_points = list(reserve)
    index = {point: position for position, point in enumerate(expected_points)}
    rotation_map = []
    for point in rotation:
        if point not in index:
            index[point] = len(expected_points)
            expected_points.append(point)
        rotation_map.append(index[point])
    if committed != expected_points or len(committed) != 2010:
        raise ValueError("combined coordinate file is not the claimed exact union")

    expected_edges = set(read_edges(Q1 / "reserve_union.edge", 1186, 7440))
    for left, right in read_edges(Q2 / "rho3_union.edge", 1357, 6860):
        mapped_left, mapped_right = rotation_map[left], rotation_map[right]
        expected_edges.add((min(mapped_left, mapped_right), max(mapped_left, mapped_right)))

    rotation_set = set(rotation)
    reserve_only = [index for index, point in enumerate(reserve) if point not in rotation_set]
    rotation_new = list(range(len(reserve), len(expected_points)))
    one = F.from_int(1)
    cross_count = 0
    for left in reserve_only:
        for right in rotation_new:
            if sqdist(expected_points[left], expected_points[right]) == one:
                expected_edges.add((left, right))
                cross_count += 1
    if (len(reserve_only), len(rotation_new), cross_count) != (653, 824, 50):
        raise ValueError("exact cross-part summary changed")

    stored_edges = read_edges(HERE / "combined_union.edge", 2010, 11766)
    if sorted(expected_edges) != stored_edges:
        raise ValueError("combined edge list differs from exact decomposition")

    colors = [
        int(value)
        for value in (HERE / "combined_union.5color.txt").read_text().split()
    ]
    if len(colors) != 2010 or any(color < 0 or color >= 5 for color in colors):
        raise ValueError("invalid coloring vector")
    for left, right in stored_edges:
        if colors[left] == colors[right]:
            raise ValueError(f"monochromatic unit edge {left}--{right}")
    counts = [colors.count(color) for color in range(5)]
    print(
        "combined_union: exact decomposition n=2010 m=11766 "
        f"(50 cross edges); 5-coloring verified; counts={counts}"
    )


if __name__ == "__main__":
    main()
