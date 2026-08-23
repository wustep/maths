#!/usr/bin/env python3
"""Exact bounded repair around the two vertices in the q3 violations.

Every vertex outside the selected neighborhood is fixed to the q3 color.
Thus SAT produces a genuine 1697 coloring, while UNSAT rules out only the
explicit, replayable neighborhood printed in the JSON result.
"""

from __future__ import annotations

import argparse
import json
import threading
from collections import Counter
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver


N = 1697
COLORS = 7
CORE = (537, 640, 1074, 1177)
EXPECTED_BAD = {(537, 537, 1074), (537, 640, 1177)}


def read_colors(path: Path) -> list[int]:
    colors = [int(token) for token in path.read_text(encoding="ascii").split()]
    if len(colors) != N or any(color not in range(COLORS) for color in colors):
        raise ValueError(f"expected {N} colors in 0..{COLORS - 1}")
    return colors


def edges():
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            yield x, y, x + y


def violations(colors: list[int]) -> list[tuple[int, int, int]]:
    return [
        (x, y, z)
        for x, y, z in edges()
        if colors[x - 1] == colors[y - 1] == colors[z - 1]
    ]


def blocker_order(colors: list[int]) -> tuple[list[int], Counter[int]]:
    """Rank vertices occurring in immediate alternative-color blockers.

    If a core vertex alone were recolored to c, a triple whose other fixed
    vertices all have color c would become monochromatic. Vertices in those
    triples are the first ejection-chain neighborhood; repeated occurrence
    gives the deterministic ranking.
    """

    core = set(CORE)
    score: Counter[int] = Counter()
    for x, y, z in edges():
        vertices = {x, y, z}
        for vertex in vertices & core:
            others = vertices - {vertex}
            other_colors = {colors[other - 1] for other in others}
            if len(other_colors) != 1 or next(iter(other_colors)) == colors[vertex - 1]:
                continue
            for other in others - core:
                score[other] += 1
    order = sorted(score, key=lambda vertex: (-score[vertex], vertex))
    return order, score


def variable(index: dict[int, int], vertex: int, color: int) -> int:
    return COLORS * index[vertex] + color + 1


def solve_local(
    colors: list[int], mutable: set[int], solver_name: str, seconds: float
) -> tuple[dict[str, object], list[int] | None]:
    index = {vertex: offset for offset, vertex in enumerate(sorted(mutable))}
    started = monotonic()
    clauses = 0
    relevant_edges = 0

    with Solver(name=solver_name) as solver:
        for vertex in sorted(mutable):
            solver.add_clause([variable(index, vertex, color) for color in range(COLORS)])
            clauses += 1
            for left in range(COLORS):
                for right in range(left + 1, COLORS):
                    solver.add_clause(
                        [-variable(index, vertex, left), -variable(index, vertex, right)]
                    )
                    clauses += 1

        for x, y, z in edges():
            vertices = {x, y, z}
            moving = vertices & mutable
            if not moving:
                continue
            relevant_edges += 1
            fixed = vertices - mutable
            for color in range(COLORS):
                if any(colors[vertex - 1] != color for vertex in fixed):
                    continue
                clause = [-variable(index, vertex, color) for vertex in sorted(moving)]
                if not clause:
                    raise AssertionError(f"fixed monochromatic edge {(x, y, z)}")
                solver.add_clause(clause)
                clauses += 1

        solver.set_phases(
            [variable(index, vertex, colors[vertex - 1]) for vertex in sorted(mutable)]
        )
        timer = threading.Timer(seconds, solver.interrupt)
        timer.start()
        try:
            sat = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
            if sat is None:
                try:
                    solver.clear_interrupt()
                except NotImplementedError:
                    pass

        candidate = None
        result = "timeout" if sat is None else "unsat"
        changed: list[list[int]] = []
        if sat is True:
            model = set(solver.get_model())
            candidate = colors.copy()
            for vertex in sorted(mutable):
                chosen = [
                    color
                    for color in range(COLORS)
                    if variable(index, vertex, color) in model
                ]
                if len(chosen) != 1:
                    raise AssertionError(f"model gives {vertex} colors {chosen}")
                candidate[vertex - 1] = chosen[0]
                if chosen[0] != colors[vertex - 1]:
                    changed.append([vertex, colors[vertex - 1], chosen[0]])
            bad = violations(candidate)
            if bad:
                raise AssertionError(f"local SAT model has violations {bad[:5]}")
            result = "sat"

    return (
        {
            "result": result,
            "mutable_vertices": len(mutable),
            "clauses": clauses,
            "relevant_edges": relevant_edges,
            "changed": changed,
            "elapsed_seconds": round(monotonic() - started, 6),
        },
        candidate,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--sizes", default="0,16,32,64")
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--log", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    colors = read_colors(args.input)
    bad = set(violations(colors))
    if bad != EXPECTED_BAD:
        raise ValueError(f"expected q3 violations {sorted(EXPECTED_BAD)}, got {sorted(bad)}")
    order, score = blocker_order(colors)
    sizes = [int(token) for token in args.sizes.split(",")]
    runs: list[dict[str, object]] = []
    final_candidate = None
    for size in sizes:
        mutable = set(CORE) | set(order[:size])
        result, candidate = solve_local(colors, mutable, args.solver, args.seconds)
        result["requested_blockers"] = size
        result["mutable"] = sorted(mutable)
        result["minimum_blocker_score"] = min(
            (score[vertex] for vertex in mutable - set(CORE)), default=None
        )
        runs.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
        if candidate is not None:
            final_candidate = candidate
            break

    report = {
        "input": args.input.name,
        "solver": args.solver,
        "seconds_per_neighborhood": args.seconds,
        "ranking": "frequency in immediate alternative-color blockers of the four core vertices",
        "core": list(CORE),
        "runs": runs,
        "result": "sat" if final_candidate is not None else "no-local-coloring-found",
        "warning": "UNSAT applies only to the named fixed-outside neighborhood; timeout is residue.",
    }
    if args.log:
        args.log.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if final_candidate is not None:
        if args.output is None:
            raise ValueError("SAT found: pass --output to preserve the coloring")
        args.output.write_text(" ".join(map(str, final_candidate)) + "\n", encoding="ascii")
    elif args.output:
        args.output.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
