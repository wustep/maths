#!/usr/bin/env python3
"""Add the fourth exact Parts rotation layer to q3's combined graph."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
Q3 = HERE.parent / "q3"
sys.path.insert(0, str(Q1))

from lattice import rotate_rho  # noqa: E402
from udg import F, load_vtx, sqdist, write_edge_list, write_vtx  # noqa: E402


def read_edges(path: Path) -> list[tuple[int, int]]:
    lines = path.read_text().splitlines()
    edges = []
    for line in lines[1:]:
        tag, left, right = line.split()
        if tag != "e":
            raise ValueError(f"bad edge line in {path}: {line}")
        edges.append((int(left) - 1, int(right) - 1))
    return edges


def fourth_layer() -> list:
    layer = load_vtx(Q1 / "parts509.vtx")
    for _ in range(3):
        layer = [rotate_rho(point) for point in layer]
    return layer


def main() -> None:
    old_points = load_vtx(Q3 / "combined_union.vtx")
    points = list(old_points)
    point_index = {point: index for index, point in enumerate(points)}
    layer = fourth_layer()
    for point in layer:
        if point not in point_index:
            point_index[point] = len(points)
            points.append(point)

    old_n = len(old_points)
    edges = set(read_edges(Q3 / "combined_union.edge"))
    one = F.from_int(1)
    incident_edges = []
    for right in range(old_n, len(points)):
        for left in range(right):
            if sqdist(points[left], points[right]) == one:
                edges.add((left, right))
                incident_edges.append((left, right))

    edges = sorted(edges)
    layer_overlap = len(layer) - (len(points) - old_n)
    actual = (len(points), len(edges), layer_overlap, len(incident_edges))
    expected = (2434, 13975, 85, 2209)
    if actual != expected:
        raise ValueError(f"four-layer combined summary {actual} != {expected}")
    summary = {
        "base_vertices": 509,
        "old_combined_vertices": old_n,
        "fourth_layer_source_vertices": len(layer),
        "fourth_layer_overlap": layer_overlap,
        "new_vertices": len(points) - old_n,
        "new_incident_edges": len(incident_edges),
        "n": len(points),
        "m": len(edges),
        "rho": "(7 + i*sqrt(15))/8",
        "rotation_exponents": [0, 1, 2, 3],
    }
    write_vtx(HERE / "rho4_combined.vtx", points)
    write_edge_list(HERE / "rho4_combined.edge", len(points), edges)
    (HERE / "build_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
