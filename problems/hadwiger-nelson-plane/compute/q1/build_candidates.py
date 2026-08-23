#!/usr/bin/env python3
"""Build two exact finite spawns of the Parts 509 graph.

rho-union is G union rho G for Parts' published rotation
rho = (7 + i sqrt(15))/8.

reserve-union adds the 677 points retained by the committed source enumeration
of the unrotated/rho lattice disk of radius 2.55. Each has at least four exact
unit neighbours in G. A 5-coloring of the full union simultaneously colors
every subgraph obtained by adding any subset of this named reserve.
"""

from __future__ import annotations

import json
from pathlib import Path

from lattice import rotate_rho
from udg import F, load_vtx, sqdist, unit_edges, write_edge_list, write_vtx

HERE = Path(__file__).resolve().parent
BASE = HERE / "parts509.vtx"
RADIUS = 2.55
MIN_DEGREE = 4


def unique(points):
    out = []
    seen = set()
    for point in points:
        if point not in seen:
            seen.add(point)
            out.append(point)
    return out


def rho_union(base):
    return unique(base + [rotate_rho(point) for point in base])


def reserve(base):
    extras = load_vtx(HERE / "reserve_extras.vtx")
    have = set(base)
    if len(extras) != 677 or len(set(extras)) != 677:
        raise ValueError("reserve_extras.vtx must contain 677 distinct points")
    if any(point in have for point in extras):
        raise ValueError("reserve contains a base vertex")
    base_float = [(x.to_float(), y.to_float()) for x, y in base]
    one = F.from_int(1)
    for point in extras:
        x, y = point[0].to_float(), point[1].to_float()
        if x * x + y * y > RADIUS * RADIUS + 1e-9:
            raise ValueError("reserve point lies outside radius 2.55")
        degree = 0
        for index, (bx, by) in enumerate(base_float):
            dx, dy = x - bx, y - by
            if abs(dx * dx + dy * dy - 1.0) < 1e-8:
                if sqdist(point, base[index]) == one:
                    degree += 1
        if degree >= MIN_DEGREE:
            continue
        raise ValueError(f"reserve point has exact degree {degree} < 4 into base")
    return extras


def emit(name, points):
    edges = unit_edges(points)
    write_vtx(HERE / f"{name}.vtx", points)
    write_edge_list(HERE / f"{name}.edge", len(points), edges)
    return {"name": name, "n": len(points), "m": len(edges)}


def main():
    base = load_vtx(BASE)
    base_edges = unit_edges(base)
    if (len(base), len(base_edges)) != (509, 2442):
        raise SystemExit(
            f"Parts baseline mismatch: {(len(base), len(base_edges))} != (509, 2442)"
        )

    rho_points = rho_union(base)
    extras = reserve(base)
    reserve_points = base + extras

    summary = {
        "source": "Parts arXiv:2010.12665v2",
        "base": {"n": len(base), "m": len(base_edges)},
        "rho": "(7 + i*sqrt(15))/8",
        "rho_union": emit("rho_union", rho_points),
        "reserve_parameters": {
            "radius": RADIUS,
            "minimum_exact_unit_degree_into_base": MIN_DEGREE,
            "source_table": "reserve_source.json",
            "kept": len(extras),
        },
        "reserve_union": emit("reserve_union", reserve_points),
    }
    (HERE / "build_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
