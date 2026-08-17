#!/usr/bin/env python3
"""Emit explicit 4-colorings of G-v for the degree-4 vertices.

These are the short witnesses that the published 509-graph is vertex-critical.
"""

from __future__ import annotations

import json
from pathlib import Path

from udg import coloring_cnf, degrees, find_triangle, load_vtx, unit_edges
from color_sat import model_to_colors, check_coloring, solve_coloring


def main() -> None:
    pts = load_vtx("509_parts.vtx")
    edges = unit_edges(pts)
    n = len(pts)
    deg = degrees(n, edges)
    tri = find_triangle(n, edges)
    targets = [v for v in range(n) if deg[v] == 4]
    out = []
    for v in targets:
        status, model, dt = solve_coloring(n, edges, skip={v}, triangle=tri)
        assert status == "SAT", (v, status)
        colors = [-1] * n
        remaining = [i for i in range(n) if i != v]
        # model_to_colors expects every vertex; fill skipped as -1
        from color_sat import color_var
        pos = set(lit for lit in model if lit > 0)
        for i in remaining:
            found = [c for c in range(4) if color_var(i, c) in pos]
            assert found, i
            colors[i] = found[0]
        ok = all((a == v or b == v) or colors[a] != colors[b] for a, b in edges)
        assert ok
        counts = [colors.count(c) for c in range(4) if c != -1]
        counts = [sum(1 for x in colors if x == c) for c in range(4)]
        rec = {"v": v, "degree": 4, "seconds": dt, "color_counts": counts}
        Path(f"coloring_Gminus_{v}.txt").write_text(
            f"# 4-coloring of published 509-graph minus vertex {v}\n"
            + " ".join(str(c) for c in colors)
            + "\n"
        )
        out.append(rec)
        print(rec, flush=True)
    Path("critical_deg4.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
