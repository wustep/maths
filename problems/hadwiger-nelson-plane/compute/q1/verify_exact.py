#!/usr/bin/env python3
"""Rebuild all exact unit edges and check the stored five-colorings."""

from __future__ import annotations

from pathlib import Path

from udg import load_vtx, unit_edges

HERE = Path(__file__).resolve().parent

EXPECTED = {
    "rho_union": (933, 4651),
    "reserve_union": (1186, 7440),
}


def read_edges(path):
    lines = path.read_text().splitlines()
    head = lines[0].split()
    if len(head) != 4 or head[:2] != ["p", "edge"]:
        raise ValueError(f"bad edge header in {path}")
    n, m = int(head[2]), int(head[3])
    edges = []
    for line in lines[1:]:
        tag, left, right = line.split()
        if tag != "e":
            raise ValueError(f"bad edge line {line}")
        edges.append((int(left) - 1, int(right) - 1))
    if len(edges) != m:
        raise ValueError(f"{path}: {len(edges)} edges != header {m}")
    return n, edges


def check(name):
    points = load_vtx(HERE / f"{name}.vtx")
    rebuilt = unit_edges(points)
    edge_n, stored = read_edges(HERE / f"{name}.edge")
    if edge_n != len(points):
        raise ValueError(f"{name}: edge n={edge_n}, coordinate n={len(points)}")
    if stored != rebuilt:
        raise ValueError(f"{name}: committed edge list differs from exact rebuild")

    expected = EXPECTED[name]
    if (len(points), len(rebuilt)) != expected:
        raise ValueError(
            f"{name}: {(len(points), len(rebuilt))} != expected {expected}"
        )

    colors = [
        int(value)
        for value in (HERE / f"{name}.5color.txt").read_text().split()
    ]
    if len(colors) != len(points):
        raise ValueError(f"{name}: {len(colors)} colors for {len(points)} vertices")
    if any(color < 0 or color >= 5 for color in colors):
        raise ValueError(f"{name}: color outside 0..4")
    for left, right in rebuilt:
        if colors[left] == colors[right]:
            raise ValueError(f"{name}: monochromatic unit edge {left}--{right}")
    counts = [colors.count(color) for color in range(5)]
    print(
        f"{name}: exact n={len(points)} m={len(rebuilt)}; "
        f"5-coloring verified; counts={counts}"
    )


def main():
    base = load_vtx(HERE / "parts509.vtx")
    base_edges = unit_edges(base)
    if (len(base), len(base_edges)) != (509, 2442):
        raise ValueError("Parts baseline did not rebuild to 509 vertices, 2442 edges")
    print("parts509: exact n=509 m=2442")
    for name in EXPECTED:
        check(name)


if __name__ == "__main__":
    main()
