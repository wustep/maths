#!/usr/bin/env python3
"""Core-guided exact SAT repair of an almost-symmetric near-coloring.

The local search often reaches a coloring with one bad orbit edge.  This
program pins every orbit to that coloring, asks a SAT solver for an UNSAT
core, releases the pinned orbits in that core, and repeats.  Every accepted
output is checked against all integer triples, not merely the folded graph.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver

from search_orbit_minconflicts import build
from search_shifted_sat import verify


def read_coloring(path: Path, target: int) -> list[int]:
    tokens = path.read_text(encoding="ascii").split()
    if len(tokens) != target:
        raise ValueError(f"expected {target} colors in {path}, found {len(tokens)}")
    colors = [-1] + [int(token) for token in tokens]
    if any(color < 0 or color >= 7 for color in colors[1:]):
        raise ValueError("colors must lie in 0..6")
    return colors


def repair(
    path: Path,
    target: int,
    solver_name: str,
    output: Path,
) -> dict[str, int | float | str]:
    colors = read_coloring(path, target)
    keys, edges, _incident, key = build(target)
    key_index = {key_value: position for position, key_value in enumerate(keys)}

    assignment = [-1] * len(keys)
    for x in range(1, target + 1):
        position = key_index[key(x)]
        if assignment[position] == -1:
            assignment[position] = colors[x]
        elif assignment[position] != colors[x]:
            raise ValueError(f"input does not respect the required orbit at {x}")

    violations = [
        eid
        for eid, edge in enumerate(edges)
        if len({assignment[vertex] for vertex in edge}) == 1
    ]
    if not violations:
        verify(colors)
        output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        return {
            "target": target,
            "result": "input-already-sat",
            "initial_violations": 0,
            "relaxed_orbits": 0,
        }

    def variable(vertex: int, color: int) -> int:
        return 7 * vertex + color + 1

    started = monotonic()
    with Solver(name=solver_name) as solver:
        for vertex in range(len(keys)):
            solver.add_clause([variable(vertex, color) for color in range(7)])
            for left in range(7):
                for right in range(left + 1, 7):
                    solver.add_clause([-variable(vertex, left), -variable(vertex, right)])
        for edge in edges:
            for color in range(7):
                solver.add_clause([-variable(vertex, color) for vertex in edge])

        phases = [variable(vertex, assignment[vertex]) for vertex in range(len(keys))]
        try:
            solver.set_phases(phases)
        except NotImplementedError:
            pass

        pinned = set(phases)
        iterations = 0
        while True:
            iterations += 1
            result = solver.solve(assumptions=sorted(pinned))
            if result is True:
                break
            if result is None:
                raise RuntimeError("solver interrupted during core-guided repair")
            core = solver.get_core() or []
            if not core:
                raise RuntimeError("the unpinned almost-symmetric CNF is UNSAT")
            pinned.difference_update(core)
            print(
                json.dumps(
                    {
                        "iteration": iterations,
                        "core_size": len(core),
                        "pinned_orbits": len(pinned),
                        "relaxed_orbits": len(keys) - len(pinned),
                        "elapsed_seconds": round(monotonic() - started, 3),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

        model = set(solver.get_model())

    key_colors: dict[int, int] = {}
    for position, key_value in enumerate(keys):
        chosen = [
            color for color in range(7) if variable(position, color) in model
        ]
        if len(chosen) != 1:
            raise RuntimeError(f"model assigns orbit {key_value} colors {chosen}")
        key_colors[key_value] = chosen[0]

    repaired = [-1] + [key_colors[key(x)] for x in range(1, target + 1)]
    verify(repaired)
    output.write_text(" ".join(map(str, repaired[1:])) + "\n", encoding="ascii")
    return {
        "target": target,
        "solver": solver_name,
        "result": "sat",
        "initial_violations": len(violations),
        "orbit_variables": len(keys),
        "orbit_edges": len(edges),
        "iterations": iterations,
        "relaxed_orbits": len(keys) - len(pinned),
        "elapsed_seconds": round(monotonic() - started, 6),
        "output": str(output),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--target", type=int, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            repair(args.input, args.target, args.solver, args.output),
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
