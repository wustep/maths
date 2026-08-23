#!/usr/bin/env python3
"""Core-guided CEGAR repair of an unrestricted 1697 near-coloring.

Unlike q1/q2, this script has one variable per integer and imposes no
reflection.  It begins with every integer pinned to the supplied coloring.
An UNSAT core releases pins; a SAT candidate is checked against every Schur
pair, and all color clauses for each newly violated edge are then added.
"""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver


N = 1697
COLORS = 7


def variable(vertex: int, color: int) -> int:
    """One-based vertex and zero-based color to a DIMACS variable."""
    return COLORS * (vertex - 1) + color + 1


def read_colors(path: Path) -> list[int]:
    colors = [int(token) for token in path.read_text(encoding="ascii").split()]
    if len(colors) != N or any(color not in range(COLORS) for color in colors):
        raise ValueError(f"expected exactly {N} colors in 0..{COLORS - 1}")
    return colors


def violations(colors: list[int]) -> list[tuple[int, int]]:
    bad: list[tuple[int, int]] = []
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            if colors[x - 1] == colors[y - 1] == colors[x + y - 1]:
                bad.append((x, y))
    return bad


def write_colors(path: Path, colors: list[int]) -> None:
    path.write_text(" ".join(map(str, colors)) + "\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--near-output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--max-iterations", type=int, default=100_000)
    args = parser.parse_args()

    initial = read_colors(args.input)
    initial_bad = violations(initial)
    best = initial
    best_bad = initial_bad
    write_colors(args.near_output, best)
    started = monotonic()
    deadline = started + args.seconds
    events: list[dict[str, object]] = []

    with Solver(name=args.solver) as solver:
        clause_count = 0
        for vertex in range(1, N + 1):
            solver.add_clause([variable(vertex, color) for color in range(COLORS)])
            clause_count += 1
            for left in range(COLORS):
                for right in range(left + 1, COLORS):
                    solver.add_clause([-variable(vertex, left), -variable(vertex, right)])
                    clause_count += 1

        active_edges: set[tuple[int, int]] = set()

        def add_edge(x: int, y: int) -> None:
            nonlocal clause_count
            if (x, y) in active_edges:
                return
            active_edges.add((x, y))
            vertices = sorted({x, y, x + y})
            for color in range(COLORS):
                solver.add_clause([-variable(vertex, color) for vertex in vertices])
                clause_count += 1

        for edge in initial_bad:
            add_edge(*edge)

        phases = [variable(vertex, initial[vertex - 1]) for vertex in range(1, N + 1)]
        solver.set_phases(phases)
        pinned = set(phases)

        encoding = {
            "event": "encoding",
            "initial_violations": len(initial_bad),
            "one_hot_clauses": N * (1 + COLORS * (COLORS - 1) // 2),
            "initial_active_edges": len(active_edges),
            "solver": args.solver,
        }
        events.append(encoding)
        print(json.dumps(encoding, sort_keys=True), flush=True)

        result = "timeout"
        iterations = 0
        released = 0
        while iterations < args.max_iterations and monotonic() < deadline:
            iterations += 1
            remaining = deadline - monotonic()
            timer = threading.Timer(max(0.001, remaining), solver.interrupt)
            timer.start()
            try:
                sat_result = solver.solve_limited(
                    assumptions=sorted(pinned), expect_interrupt=True
                )
            finally:
                timer.cancel()
                if sat_result is None:
                    try:
                        solver.clear_interrupt()
                    except NotImplementedError:
                        pass

            if sat_result is None:
                result = "timeout"
                break
            if sat_result is False:
                core = solver.get_core() or []
                if not core:
                    result = "partial-cnf-unsat"
                    break
                pinned.difference_update(core)
                released += len(core)
                if iterations <= 20 or iterations % 100 == 0:
                    event = {
                        "event": "release",
                        "iteration": iterations,
                        "core_size": len(core),
                        "pinned": len(pinned),
                        "released_events": released,
                        "active_edges": len(active_edges),
                        "elapsed_seconds": round(monotonic() - started, 6),
                    }
                    events.append(event)
                    print(json.dumps(event, sort_keys=True), flush=True)
                continue

            model = set(solver.get_model())
            candidate: list[int] = []
            for vertex in range(1, N + 1):
                chosen = [
                    color
                    for color in range(COLORS)
                    if variable(vertex, color) in model
                ]
                if len(chosen) != 1:
                    raise RuntimeError(f"vertex {vertex} has colors {chosen}")
                candidate.append(chosen[0])
            bad = violations(candidate)
            if len(bad) < len(best_bad):
                best = candidate
                best_bad = bad
                write_colors(args.near_output, best)
                event = {
                    "event": "improvement",
                    "iteration": iterations,
                    "violations": len(bad),
                    "pinned": len(pinned),
                    "active_edges": len(active_edges),
                    "elapsed_seconds": round(monotonic() - started, 6),
                }
                events.append(event)
                print(json.dumps(event, sort_keys=True), flush=True)
            if not bad:
                write_colors(args.output, candidate)
                result = "sat"
                break
            before = len(active_edges)
            for edge in bad:
                add_edge(*edge)
            if len(active_edges) == before:
                raise RuntimeError("SAT model violates only already-active edges")
            if iterations <= 20 or iterations % 100 == 0:
                event = {
                    "event": "refine",
                    "iteration": iterations,
                    "candidate_violations": len(bad),
                    "new_edges": len(active_edges) - before,
                    "active_edges": len(active_edges),
                    "pinned": len(pinned),
                    "elapsed_seconds": round(monotonic() - started, 6),
                }
                events.append(event)
                print(json.dumps(event, sort_keys=True), flush=True)

    final = {
        "event": "result",
        "result": result,
        "iterations": iterations,
        "initial_violations": len(initial_bad),
        "best_violations": len(best_bad),
        "active_edges": len(active_edges),
        "pinned": len(pinned),
        "released_events": released,
        "clauses": clause_count,
        "elapsed_seconds": round(monotonic() - started, 6),
        "first_best_violations": [
            [x, y, x + y, best[x - 1]] for x, y in best_bad[:20]
        ],
    }
    events.append(final)
    args.log.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, sort_keys=True), flush=True)
    if result != "sat":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
