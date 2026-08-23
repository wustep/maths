#!/usr/bin/env python3
"""Build G union rho G union rho^2 G from the exact Parts coordinates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
sys.path.insert(0, str(Q1))

from lattice import rotate_rho  # noqa: E402
from udg import load_vtx, unit_edges, write_edge_list, write_vtx  # noqa: E402


def main():
    base = load_vtx(Q1 / "parts509.vtx")
    points = []
    seen = set()
    layer = base
    new_per_layer = []
    for _ in range(3):
        new = 0
        for point in layer:
            if point not in seen:
                seen.add(point)
                points.append(point)
                new += 1
        new_per_layer.append(new)
        layer = [rotate_rho(point) for point in layer]

    edges = unit_edges(points)
    if (len(points), len(edges)) != (1357, 6860):
        raise ValueError(
            f"three-layer graph rebuilt to {(len(points), len(edges))}, "
            "expected (1357, 6860)"
        )
    write_vtx(HERE / "rho3_union.vtx", points)
    write_edge_list(HERE / "rho3_union.edge", len(points), edges)
    summary = {
        "source": "Parts arXiv:2010.12665v2",
        "rho": "(7 + i*sqrt(15))/8",
        "layers": 3,
        "new_vertices_per_layer": new_per_layer,
        "n": len(points),
        "m": len(edges),
    }
    (HERE / "build_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
