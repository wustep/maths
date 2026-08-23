#!/usr/bin/env python3
"""Exact SAT search under the color-twisted translation by 537.

The named family is c(x + 537) = c(x) + 1 (mod 7) whenever both arguments
lie in [1697]. In particular c(1074) != c(537) and c(1177) != c(640), so the
two q3 violations cannot occur in this family.
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
SHIFT = 537


def representative(vertex: int) -> tuple[int, int]:
    return (vertex - 1) % SHIFT + 1, (vertex - 1) // SHIFT


def variable(rep: int, base_color: int) -> int:
    return COLORS * (rep - 1) + base_color + 1


def actual_color(base: list[int], vertex: int) -> int:
    rep, layer = representative(vertex)
    return (base[rep - 1] + layer) % COLORS


def violations(colors: list[int]) -> list[list[int]]:
    bad: list[list[int]] = []
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            z = x + y
            if colors[x - 1] == colors[y - 1] == colors[z - 1]:
                bad.append([x, y, z, colors[x - 1]])
    return bad


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", type=Path, help="q3 vector used only for SAT phases")
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    phase = [int(token) for token in args.phase.read_text(encoding="ascii").split()]
    if len(phase) != N or any(color not in range(COLORS) for color in phase):
        raise ValueError(f"expected a {N}-entry phase vector in 0..{COLORS - 1}")

    started = monotonic()
    clauses = 0
    forced_safe_edge_colors = 0
    encoded_edge_colors = 0
    result = "timeout"
    candidate = None
    with Solver(name=args.solver) as solver:
        for rep in range(1, SHIFT + 1):
            solver.add_clause([variable(rep, color) for color in range(COLORS)])
            clauses += 1
            for left in range(COLORS):
                for right in range(left + 1, COLORS):
                    solver.add_clause([-variable(rep, left), -variable(rep, right)])
                    clauses += 1

        for x in range(1, N + 1):
            for y in range(x, N - x + 1):
                z = x + y
                for monochromatic_color in range(COLORS):
                    requirements: dict[int, int] = {}
                    possible = True
                    for vertex in {x, y, z}:
                        rep, layer = representative(vertex)
                        required = (monochromatic_color - layer) % COLORS
                        if rep in requirements and requirements[rep] != required:
                            possible = False
                            break
                        requirements[rep] = required
                    if not possible:
                        forced_safe_edge_colors += 1
                        continue
                    solver.add_clause(
                        [-variable(rep, color) for rep, color in sorted(requirements.items())]
                    )
                    clauses += 1
                    encoded_edge_colors += 1

        solver.set_phases([variable(rep, phase[rep - 1]) for rep in range(1, SHIFT + 1)])
        encoding_seconds = monotonic() - started
        timer = threading.Timer(args.seconds, solver.interrupt)
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
        if sat is False:
            result = "unsat"
        elif sat is True:
            model = set(solver.get_model())
            base = []
            for rep in range(1, SHIFT + 1):
                chosen = [
                    color
                    for color in range(COLORS)
                    if variable(rep, color) in model
                ]
                if len(chosen) != 1:
                    raise AssertionError(f"representative {rep} has colors {chosen}")
                base.append(chosen[0])
            candidate = [actual_color(base, vertex) for vertex in range(1, N + 1)]
            bad = violations(candidate)
            if bad:
                raise AssertionError(f"expanded SAT model has violations {bad[:10]}")
            if candidate[1074 - 1] == candidate[537 - 1]:
                raise AssertionError("shift symmetry did not separate 537 and 1074")
            if candidate[1177 - 1] == candidate[640 - 1]:
                raise AssertionError("shift symmetry did not separate 640 and 1177")
            result = "sat"

    report = {
        "family": "c(x + 537) = c(x) + 1 mod 7",
        "representatives": SHIFT,
        "expanded_length": N,
        "solver": args.solver,
        "seconds_limit": args.seconds,
        "clauses": clauses,
        "encoded_edge_colors": encoded_edge_colors,
        "forced_safe_edge_colors": forced_safe_edge_colors,
        "encoding_seconds": round(encoding_seconds, 6),
        "solver_and_encoding_seconds": round(monotonic() - started, 6),
        "target_separation": {
            "c(1074)-c(537) mod 7": 1,
            "c(1177)-c(640) mod 7": 1,
        },
        "result": result,
        "warning": "UNSAT or timeout concerns only this named symmetry family.",
    }
    args.log.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True), flush=True)
    if candidate is not None:
        if args.output is None:
            raise ValueError("SAT found: pass --output to preserve the coloring")
        args.output.write_text(" ".join(map(str, candidate)) + "\n", encoding="ascii")
    elif args.output:
        args.output.unlink(missing_ok=True)
    if result != "sat":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
