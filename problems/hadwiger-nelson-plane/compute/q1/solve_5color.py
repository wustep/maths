#!/usr/bin/env python3
"""SAT-color a committed edge list with five colors and store the model."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

from udg import coloring_cnf, find_triangle


def read_edges(path):
    lines = path.read_text().splitlines()
    head = lines[0].split()
    if len(head) != 4 or head[:2] != ["p", "edge"]:
        raise ValueError(f"bad edge header in {path}")
    n, claimed_m = int(head[2]), int(head[3])
    edges = []
    for line in lines[1:]:
        fields = line.split()
        if len(fields) != 3 or fields[0] != "e":
            raise ValueError(f"bad edge line: {line}")
        a, b = int(fields[1]) - 1, int(fields[2]) - 1
        edges.append((a, b))
    if len(edges) != claimed_m:
        raise ValueError(f"edge count {len(edges)} != header {claimed_m}")
    return n, edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("edge", type=Path)
    parser.add_argument("coloring", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()

    n, edges = read_edges(args.edge)
    triangle = find_triangle(n, edges)
    nvars, clauses, _ = coloring_cnf(
        n, edges, ncolors=5, triangle=triangle
    )

    start = time.perf_counter()
    with Cadical195() as solver:
        for clause in clauses:
            solver.add_clause(clause)
        sat = solver.solve()
        model = solver.get_model() if sat else None
    seconds = time.perf_counter() - start

    result = {
        "edge": args.edge.name,
        "n": n,
        "m": len(edges),
        "colors": 5,
        "nvars": nvars,
        "clauses": len(clauses),
        "triangle": list(triangle) if triangle else None,
        "solver": "PySAT Cadical195",
        "status": "SAT" if sat else "UNSAT",
        "seconds": seconds,
    }
    if not sat:
        args.json.write_text(json.dumps(result, indent=2) + "\n")
        raise SystemExit("UNSAT: preserve the instance and produce a proof before claiming")

    positive = {literal for literal in model if literal > 0}
    colors = []
    for vertex in range(n):
        choices = [
            color
            for color in range(5)
            if vertex * 5 + color + 1 in positive
        ]
        if not choices:
            raise RuntimeError(f"model leaves vertex {vertex} uncolored")
        colors.append(choices[0])
    if any(colors[a] == colors[b] for a, b in edges):
        raise RuntimeError("SAT model is not a proper coloring")

    args.coloring.write_text("\n".join(map(str, colors)) + "\n")
    result["model_checked"] = True
    result["color_counts"] = [colors.count(color) for color in range(5)]
    args.json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
