#!/usr/bin/env python3
"""Long exact SAT pass for q2 alternate phases and split templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver

from q2_alternate_template_search import (
    build,
    expand,
    parse_representatives,
    phase_from_cyclic_multiplier,
    phase_from_file,
)
from search_shifted_sat import verify


def restricted_growth(phase: list[int]) -> list[int]:
    """Relabel a phase by first occurrence, matching the SAT symmetry break."""
    names: dict[int, int] = {}
    result: list[int] = []
    for color in phase:
        if color not in names:
            names[color] = len(names)
        result.append(names[color])
    if set(result) != set(range(7)):
        raise ValueError("phase must use all seven colors")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1697)
    parser.add_argument("--split-reps", default="")
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument("--phase-file", type=Path)
    phase.add_argument("--cyclic-multiplier", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--solver-seed", type=int, default=1)
    parser.add_argument(
        "--conflict-budget",
        type=int,
        default=2_000_000,
        help="zero requests an unbounded solve",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()

    split_reps = parse_representatives(args.split_reps)
    labels, edges, point_orbit = build(args.target, split_reps)
    if args.phase_file is not None:
        raw_phase = phase_from_file(
            args.phase_file, args.target, labels, point_orbit
        ).tolist()
        phase_description = str(args.phase_file)
    else:
        raw_phase = phase_from_cyclic_multiplier(
            labels, args.cyclic_multiplier
        ).tolist()
        phase_description = f"cyclic-1680-multiplier-{args.cyclic_multiplier}"
    preferred = restricted_growth(raw_phase)

    def variable(vertex: int, color: int) -> int:
        return 7 * vertex + color + 1

    started = monotonic()
    clause_count = 0
    with Solver(name=args.solver) as solver:
        try:
            solver.configure({"seed": args.solver_seed})
        except (NotImplementedError, ValueError):
            pass

        def add(clause: list[int]) -> None:
            nonlocal clause_count
            solver.add_clause(clause)
            clause_count += 1

        for vertex in range(len(labels)):
            add([variable(vertex, color) for color in range(7)])
            for left in range(7):
                for right in range(left + 1, 7):
                    add([-variable(vertex, left), -variable(vertex, right)])

        # Restricted-growth labels remove all 7! copies without prescribing a
        # mathematical seed.  The alternate phase is relabeled to agree.
        for vertex in range(len(labels)):
            for color in range(1, 7):
                add(
                    [-variable(vertex, color)]
                    + [variable(earlier, color - 1) for earlier in range(vertex)]
                )

        for edge in edges:
            for color in range(7):
                add([-variable(vertex, color) for vertex in edge])

        phase_literals = [
            variable(vertex, preferred[vertex]) for vertex in range(len(labels))
        ]
        try:
            solver.set_phases(phase_literals)
        except NotImplementedError:
            pass

        encoding = {
            "event": "encoding",
            "target": args.target,
            "center": args.target + 1,
            "extra_split_representatives": ",".join(map(str, split_reps)) or "none",
            "orbit_variables": len(labels),
            "boolean_variables": 7 * len(labels),
            "orbit_edges": len(edges),
            "clauses": clause_count,
            "phase": phase_description,
            "solver": args.solver,
            "solver_seed": args.solver_seed,
            "conflict_budget": args.conflict_budget,
            "encoding_seconds": round(monotonic() - started, 6),
        }
        print(json.dumps(encoding, sort_keys=True), flush=True)

        if args.conflict_budget:
            solver.conf_budget(args.conflict_budget)
            result = solver.solve_limited()
        else:
            result = solver.solve()
        solver_stats = solver.accum_stats()
        model = solver.get_model() if result is True else None

    label_result = "sat" if result is True else "unsat" if result is False else "interrupted"
    stats: dict[str, object] = {
        **encoding,
        "event": "result",
        "result": label_result,
        "elapsed_seconds": round(monotonic() - started, 6),
        "solver_stats": solver_stats,
    }

    if model is not None:
        positive = set(model)
        assignment: list[int] = []
        for vertex in range(len(labels)):
            chosen = [
                color
                for color in range(7)
                if variable(vertex, color) in positive
            ]
            if len(chosen) != 1:
                raise RuntimeError(f"orbit {labels[vertex]} has model colors {chosen}")
            assignment.append(chosen[0])
        colors = expand(assignment, args.target, point_orbit)
        verify(colors)
        if args.output is None:
            raise ValueError("--output is required when SAT is found")
        args.output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        stats["output"] = str(args.output)

    if args.log is not None:
        args.log.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, sort_keys=True), flush=True)
    if result is not True:
        raise RuntimeError(json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
