#!/usr/bin/env python3
"""Exact SAT under color-twisted reflection about 1698.

The involution on colors is (0 1)(2 3)(4 5)(6).  Thus reflected integers
usually have different colors, avoiding the 566+566=1132 obstruction to
ordinary reflection, while only 849 representative colors remain.  All
involutions with three transpositions and one fixed color are equivalent by
renaming colors.
"""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver


N = 1697
CENTER = 1698
MIDDLE = 849
COLORS = 7
PERMUTATION = (1, 0, 3, 2, 5, 4, 6)


def variable(representative: int, color: int) -> int:
    return COLORS * (representative - 1) + color + 1


def point_literal(point: int, color: int) -> int | bool:
    """Literal saying point has color, before negation in a Schur clause."""
    if point < MIDDLE:
        return variable(point, color)
    if point == MIDDLE:
        return color == 6
    return variable(CENTER - point, PERMUTATION[color])


def verify(colors: list[int]) -> None:
    if len(colors) != N or any(color not in range(COLORS) for color in colors):
        raise ValueError("malformed coloring")
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            if colors[x - 1] == colors[y - 1] == colors[x + y - 1]:
                raise ValueError(f"monochromatic triple {(x, y, x + y)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--seconds", type=float, default=180.0)
    args = parser.parse_args()

    phase: list[int] | None = None
    if args.phase is not None:
        phase = [int(token) for token in args.phase.read_text(encoding="ascii").split()]
        if len(phase) < MIDDLE - 1 or any(color not in range(COLORS) for color in phase):
            raise ValueError("phase must contain at least 848 colors in 0..6")

    events: list[dict[str, object]] = []
    started = monotonic()
    with Solver(name=args.solver) as solver:
        clauses = 0
        for representative in range(1, MIDDLE):
            solver.add_clause(
                [variable(representative, color) for color in range(COLORS)]
            )
            clauses += 1
            for left in range(COLORS):
                for right in range(left + 1, COLORS):
                    solver.add_clause(
                        [-variable(representative, left), -variable(representative, right)]
                    )
                    clauses += 1

        schur_clauses = 0
        skipped_false = 0
        skipped_incompatible = 0
        for x in range(1, N + 1):
            for y in range(x, N - x + 1):
                z = x + y
                for color in range(COLORS):
                    raw = [
                        point_literal(x, color),
                        point_literal(y, color),
                        point_literal(z, color),
                    ]
                    if any(literal is False for literal in raw):
                        skipped_false += 1
                        continue
                    symbolic = [int(literal) for literal in raw if literal is not True]
                    assignments: dict[int, int] = {}
                    incompatible = False
                    for literal in symbolic:
                        representative = (literal - 1) // COLORS
                        literal_color = (literal - 1) % COLORS
                        previous = assignments.setdefault(representative, literal_color)
                        if previous != literal_color:
                            incompatible = True
                            break
                    if incompatible:
                        skipped_incompatible += 1
                        continue
                    clause = sorted({-literal for literal in symbolic})
                    if not clause:
                        raise RuntimeError(f"fixed monochromatic triple {(x, y, z, color)}")
                    solver.add_clause(clause)
                    clauses += 1
                    schur_clauses += 1

        if phase is not None:
            solver.set_phases(
                [
                    variable(representative, phase[representative - 1])
                    for representative in range(1, MIDDLE)
                ]
            )

        encoding = {
            "event": "encoding",
            "symmetry": "c(1698-x)=pi(c(x))",
            "permutation": list(PERMUTATION),
            "fixed_middle": [MIDDLE, 6],
            "representatives": MIDDLE - 1,
            "boolean_variables": COLORS * (MIDDLE - 1),
            "clauses": clauses,
            "schur_clauses": schur_clauses,
            "skipped_fixed_false": skipped_false,
            "skipped_incompatible_same_representative": skipped_incompatible,
            "solver": args.solver,
            "encoding_seconds": round(monotonic() - started, 6),
        }
        events.append(encoding)
        print(json.dumps(encoding, sort_keys=True), flush=True)

        solve_started = monotonic()
        timer = threading.Timer(args.seconds, solver.interrupt)
        timer.start()
        try:
            sat_result = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()

        label = "sat" if sat_result is True else "unsat" if sat_result is False else "timeout"
        coloring: list[int] | None = None
        if sat_result is True:
            model = set(solver.get_model())
            representative_colors: list[int] = []
            for representative in range(1, MIDDLE):
                chosen = [
                    color
                    for color in range(COLORS)
                    if variable(representative, color) in model
                ]
                if len(chosen) != 1:
                    raise RuntimeError(
                        f"representative {representative} has colors {chosen}"
                    )
                representative_colors.append(chosen[0])
            coloring = representative_colors + [6] + [
                PERMUTATION[representative_colors[CENTER - point - 1]]
                for point in range(MIDDLE + 1, N + 1)
            ]
            verify(coloring)
            args.output.write_text(" ".join(map(str, coloring)) + "\n", encoding="ascii")

    final = {
        "event": "result",
        "result": label,
        "solve_seconds": round(monotonic() - solve_started, 6),
        "output": str(args.output) if coloring is not None else None,
        "warning": "UNSAT is only for the named color-twisted symmetry.",
    }
    events.append(final)
    args.log.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, sort_keys=True), flush=True)
    if label != "sat":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
