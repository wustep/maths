#!/usr/bin/env python3
"""Merge the exact 677-point reserve and the three-layer rotation graph."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q1))

from udg import F, load_vtx, sqdist, write_edge_list, write_vtx  # noqa: E402


def read_edges(path):
    lines = path.read_text().splitlines()
    edges = []
    for line in lines[1:]:
        tag, left, right = line.split()
        if tag != "e":
            raise ValueError(f"bad edge line in {path}: {line}")
        edges.append((int(left) - 1, int(right) - 1))
    return edges


def main():
    reserve_points = load_vtx(Q1 / "reserve_union.vtx")
    rotation_points = load_vtx(Q2 / "rho3_union.vtx")
    reserve_edges = read_edges(Q1 / "reserve_union.edge")
    rotation_edges = read_edges(Q2 / "rho3_union.edge")

    points = list(reserve_points)
    point_index = {point: index for index, point in enumerate(points)}
    rotation_map = []
    for point in rotation_points:
        if point not in point_index:
            point_index[point] = len(points)
            points.append(point)
        rotation_map.append(point_index[point])

    edges = set(reserve_edges)
    for left, right in rotation_edges:
        mapped_left, mapped_right = rotation_map[left], rotation_map[right]
        edges.add((min(mapped_left, mapped_right), max(mapped_left, mapped_right)))

    rotation_set = set(rotation_points)
    reserve_only = [
        index for index, point in enumerate(reserve_points) if point not in rotation_set
    ]
    rotation_new = list(range(len(reserve_points), len(points)))
    one = F.from_int(1)
    cross_edges = []
    for left in reserve_only:
        for right in rotation_new:
            if sqdist(points[left], points[right]) == one:
                edges.add((left, right))
                cross_edges.append((left, right))

    edges = sorted(edges)
    expected = (2010, 11766, 653, 824, 50)
    actual = (
        len(points),
        len(edges),
        len(reserve_only),
        len(rotation_new),
        len(cross_edges),
    )
    if actual != expected:
        raise ValueError(f"combined graph summary {actual} != expected {expected}")

    write_vtx(HERE / "combined_union.vtx", points)
    write_edge_list(HERE / "combined_union.edge", len(points), edges)
    summary = {
        "base_vertices": 509,
        "added_vertices": 1501,
        "n": len(points),
        "m": len(edges),
        "reserve_only_vertices": len(reserve_only),
        "rotation_new_vertices": len(rotation_new),
        "exact_cross_edges": len(cross_edges),
        "pieces": ["q1/reserve_union", "q2/rho3_union"],
    }
    (HERE / "build_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
