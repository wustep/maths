#!/usr/bin/env python3
"""4-color SAT for a unit-distance graph, plus vertex-core extraction.

Uses Cadical via python-sat.  Optionally logs a DRAT proof.  Vertex
selectors give an assumption core: a subset of vertices whose induced
unit-distance graph is already not 4-colorable.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

from udg import (
    coloring_cnf,
    color_var,
    find_triangle,
    load_vtx,
    unit_edges,
    write_dimacs,
)


def solve_coloring(
    n: int,
    edges: list[tuple[int, int]],
    skip: set[int] | None = None,
    triangle: tuple[int, int, int] | None = None,
    proof_path: Path | None = None,
) -> tuple[str, list[int] | None, float]:
    nvars, clauses, _ = coloring_cnf(n, edges, skip=skip, triangle=triangle)
    kwargs = {}
    if proof_path is not None:
        kwargs["proof"] = str(proof_path)
    t0 = time.perf_counter()
    with Cadical195(**kwargs) as s:
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve()
        model = s.get_model() if sat else None
    dt = time.perf_counter() - t0
    return ("SAT" if sat else "UNSAT"), model, dt


def extract_vertex_core(
    n: int,
    edges: list[tuple[int, int]],
    triangle: tuple[int, int, int] | None = None,
) -> tuple[list[int], float]:
    """Solve under vertex-presence assumptions and return the assumption core."""
    nvars, clauses, meta = coloring_cnf(
        n, edges, triangle=None, vertex_selectors=True
    )
    sel_base = meta["sel_base"]
    assumps = [sel_base + v + 1 for v in range(n)]
    # Optional: still pin a triangle *if* those vertices stay in the core.
    # Do not add hard triangle units here; they would hide deletable vertices.
    t0 = time.perf_counter()
    with Cadical195() as s:
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve(assumptions=assumps)
        if sat:
            raise RuntimeError("graph is 4-colorable; no vertex core")
        core = s.get_core()
    dt = time.perf_counter() - t0
    present = []
    core_set = set(core or [])
    for v in range(n):
        if (sel_base + v + 1) in core_set:
            present.append(v)
    return present, dt


def model_to_colors(model: list[int], n: int, ncolors: int = 4) -> list[int]:
    pos = set(lit for lit in model if lit > 0)
    colors = []
    for v in range(n):
        found = [c for c in range(ncolors) if color_var(v, c, ncolors) in pos]
        if not found:
            raise RuntimeError(f"vertex {v} uncolored")
        colors.append(found[0])
    return colors


def check_coloring(colors: list[int], edges: list[tuple[int, int]]) -> bool:
    return all(colors[a] != colors[b] for a, b in edges)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--skip", type=int, nargs="*", default=[])
    ap.add_argument("--core", action="store_true")
    ap.add_argument("--dimacs-out", type=Path, default=None)
    ap.add_argument("--proof-out", type=Path, default=None)
    ap.add_argument("--coloring-out", type=Path, default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--no-triangle", action="store_true")
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    edges = unit_edges(pts)
    n = len(pts)
    skip = set(args.skip)
    tri = None if args.no_triangle else find_triangle(n, edges)
    print(f"n={n} m={len(edges)} skip={sorted(skip)} triangle={tri}")

    result: dict = {
        "vtx": str(args.vtx),
        "n": n,
        "m": len(edges),
        "skip": sorted(skip),
        "triangle": list(tri) if tri else None,
    }

    if args.dimacs_out:
        nvars, clauses, _ = coloring_cnf(n, edges, skip=skip, triangle=tri)
        write_dimacs(
            args.dimacs_out,
            nvars,
            clauses,
            comments=[
                f"4-coloring of {args.vtx.name}",
                f"n={n} m={len(edges)} skip={sorted(skip)} triangle={tri}",
            ],
        )
        print(f"wrote {args.dimacs_out} ({nvars} vars, {len(clauses)} clauses)")

    if args.core:
        core, dt = extract_vertex_core(n, edges, triangle=tri)
        result["status"] = "UNSAT"
        result["vertex_core"] = core
        result["core_size"] = len(core)
        result["sat_seconds"] = dt
        print(f"vertex core size {len(core)} / {n} in {dt:.3f}s")
    else:
        status, model, dt = solve_coloring(
            n, edges, skip=skip, triangle=tri, proof_path=args.proof_out
        )
        result["status"] = status
        result["sat_seconds"] = dt
        print(f"{status} in {dt:.3f}s")
        if status == "SAT":
            colors = model_to_colors(model, n)
            # skipped vertices get color -1
            if skip:
                # model is over the full variable space; skipped vertices may
                # be unconstrained.  Only check remaining edges.
                ok = all(
                    (a in skip or b in skip) or colors[a] != colors[b]
                    for a, b in edges
                )
            else:
                ok = check_coloring(colors, edges)
            result["coloring_ok"] = ok
            result["color_counts"] = [colors.count(c) for c in range(4)]
            print(f"coloring_ok={ok} counts={result['color_counts']}")
            if args.coloring_out:
                args.coloring_out.write_text(
                    " ".join(str(c) for c in colors) + "\n"
                )
        elif args.proof_out:
            print(f"wrote proof {args.proof_out} ({args.proof_out.stat().st_size} bytes)")

    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
