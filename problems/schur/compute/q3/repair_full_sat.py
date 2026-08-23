#!/usr/bin/env python3
"""Exact full-CNF, core-guided repair of an unrestricted near-coloring.

This deliberately differs from the lazy repair in repair_cegar.py: all
719,952 Schur edges and all seven color clauses are loaded before solving.
The supplied coloring is phase guidance and a set of removable assumptions,
not a structural restriction on the eventual model.
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
    return COLORS * (vertex - 1) + color + 1


def read_colors(path: Path) -> list[int]:
    colors = [int(token) for token in path.read_text(encoding="ascii").split()]
    if len(colors) != N or any(color not in range(COLORS) for color in colors):
        raise ValueError(f"expected exactly {N} colors in 0..{COLORS - 1}")
    return colors


def violations(colors: list[int]) -> list[list[int]]:
    bad: list[list[int]] = []
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            if colors[x - 1] == colors[y - 1] == colors[x + y - 1]:
                bad.append([x, y, x + y, colors[x - 1]])
    return bad


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--seconds", type=float, default=300.0)
    args = parser.parse_args()

    initial = read_colors(args.input)
    initial_bad = violations(initial)
    events: list[dict[str, object]] = []
    encoded_at = monotonic()

    with Solver(name=args.solver) as solver:
        clauses = 0
        for vertex in range(1, N + 1):
            solver.add_clause([variable(vertex, color) for color in range(COLORS)])
            clauses += 1
            for left in range(COLORS):
                for right in range(left + 1, COLORS):
                    solver.add_clause([-variable(vertex, left), -variable(vertex, right)])
                    clauses += 1

        edges = 0
        for x in range(1, N + 1):
            for y in range(x, N - x + 1):
                vertices = sorted({x, y, x + y})
                for color in range(COLORS):
                    solver.add_clause([-variable(vertex, color) for vertex in vertices])
                    clauses += 1
                edges += 1

        phases = [variable(vertex, initial[vertex - 1]) for vertex in range(1, N + 1)]
        solver.set_phases(phases)
        pinned = set(phases)
        encoding = {
            "event": "encoding",
            "solver": args.solver,
            "vertices": N,
            "colors": COLORS,
            "schur_edges": edges,
            "clauses": clauses,
            "initial_violations": len(initial_bad),
            "encoding_seconds": round(monotonic() - encoded_at, 6),
        }
        events.append(encoding)
        print(json.dumps(encoding, sort_keys=True), flush=True)

        solve_started = monotonic()
        deadline = solve_started + args.seconds
        result = "timeout"
        iterations = 0
        released_events = 0
        coloring: list[int] | None = None
        while monotonic() < deadline:
            iterations += 1
            timer = threading.Timer(
                max(0.001, deadline - monotonic()), solver.interrupt
            )
            timer.start()
            try:
                sat_result = solver.solve_limited(
                    assumptions=sorted(pinned), expect_interrupt=True
                )
            finally:
                timer.cancel()

            if sat_result is None:
                result = "timeout"
                break
            if sat_result is False:
                core = solver.get_core() or []
                if not core:
                    result = "full-cnf-unsat-no-proof-recorded"
                    break
                pinned.difference_update(core)
                released_events += len(core)
                event = {
                    "event": "release",
                    "iteration": iterations,
                    "core_size": len(core),
                    "pinned": len(pinned),
                    "released_events": released_events,
                    "elapsed_seconds": round(monotonic() - solve_started, 6),
                }
                events.append(event)
                print(json.dumps(event, sort_keys=True), flush=True)
                continue

            model = set(solver.get_model())
            coloring = []
            for vertex in range(1, N + 1):
                chosen = [
                    color
                    for color in range(COLORS)
                    if variable(vertex, color) in model
                ]
                if len(chosen) != 1:
                    raise RuntimeError(f"vertex {vertex} has colors {chosen}")
                coloring.append(chosen[0])
            bad = violations(coloring)
            if bad:
                raise RuntimeError(f"full CNF model failed verifier: {bad[0]}")
            args.output.write_text(" ".join(map(str, coloring)) + "\n", encoding="ascii")
            result = "sat"
            break

    final = {
        "event": "result",
        "result": result,
        "iterations": iterations,
        "initial_violations": len(initial_bad),
        "pinned": len(pinned),
        "released_events": released_events,
        "encoding_seconds": round(solve_started - encoded_at, 6),
        "solve_seconds": round(monotonic() - solve_started, 6),
        "output": str(args.output) if result == "sat" else None,
    }
    events.append(final)
    args.log.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, sort_keys=True), flush=True)
    if result != "sat":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
