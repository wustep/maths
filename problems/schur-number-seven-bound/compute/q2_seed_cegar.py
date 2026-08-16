#!/usr/bin/env python3
"""Enumerate new six-color 536 seeds and test them in Rowley's frame.

The outer solver produces almost-symmetric Schur colorings of [536].  The
inner solver fixes each candidate into the target 7-color reflection frame,
with 537 in the new color.  An inner UNSAT core is translated back to a
blocking clause for the outer solver, so one failed extension can discard a
whole family of seeds rather than just one specimen.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver

from q2_alternate_template_search import build, expand
from search_shifted_sat import seed_coloring, verify


def add_exactly_one(solver: Solver, vertices: int, colors: int) -> int:
    clauses = 0

    def variable(vertex: int, color: int) -> int:
        return colors * vertex + color + 1

    for vertex in range(vertices):
        solver.add_clause([variable(vertex, color) for color in range(colors)])
        clauses += 1
        for left in range(colors):
            for right in range(left + 1, colors):
                solver.add_clause([-variable(vertex, left), -variable(vertex, right)])
                clauses += 1
    return clauses


def add_restricted_growth(solver: Solver, vertices: int, colors: int) -> int:
    clauses = 0

    def variable(vertex: int, color: int) -> int:
        return colors * vertex + color + 1

    for vertex in range(vertices):
        for color in range(1, colors):
            solver.add_clause(
                [-variable(vertex, color)]
                + [variable(earlier, color - 1) for earlier in range(vertex)]
            )
            clauses += 1
    return clauses


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1697)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--solver-seed", type=int, default=536)
    parser.add_argument("--candidates", type=int, default=10_000)
    parser.add_argument("--inner-conflict-budget", type=int, default=50_000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed-output", type=Path)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()

    outer_labels, outer_edges, outer_point_orbit = build(536, ())
    inner_labels, inner_edges, inner_point_orbit = build(args.target, ())
    inner_index = {label: position for position, label in enumerate(inner_labels)}

    def outer_variable(vertex: int, color: int) -> int:
        return 6 * vertex + color + 1

    def inner_variable(vertex: int, color: int) -> int:
        return 7 * vertex + color + 1

    started = monotonic()
    events: list[dict[str, object]] = []
    with Solver(name=args.solver) as outer, Solver(name=args.solver) as inner:
        for solver, offset in ((outer, 0), (inner, 1)):
            try:
                solver.configure({"seed": args.solver_seed + offset})
            except (NotImplementedError, ValueError):
                pass

        outer_clauses = add_exactly_one(outer, len(outer_labels), 6)
        outer_clauses += add_restricted_growth(outer, len(outer_labels), 6)
        for edge in outer_edges:
            for color in range(6):
                outer.add_clause(
                    [-outer_variable(vertex, color) for vertex in edge]
                )
                outer_clauses += 1

        # Explicitly exclude the q1 Fredricksen--Sweet specimen.  The outer
        # model can still find any other almost-symmetric 536 seed.
        fredricksen_sweet = seed_coloring()
        fs_block: set[int] = set()
        for x in range(1, 537):
            fs_block.add(
                -outer_variable(outer_point_orbit[x], fredricksen_sweet[x])
            )
        outer.add_clause(sorted(fs_block))
        outer_clauses += 1

        inner_clauses = add_exactly_one(inner, len(inner_labels), 7)
        for edge in inner_edges:
            for color in range(7):
                inner.add_clause(
                    [-inner_variable(vertex, color) for vertex in edge]
                )
                inner_clauses += 1
        inner.add_clause(
            [inner_variable(inner_point_orbit[537], 6)]
        )
        inner_clauses += 1

        encoding: dict[str, object] = {
            "event": "encoding",
            "target": args.target,
            "solver": args.solver,
            "outer_orbits": len(outer_labels),
            "outer_edges": len(outer_edges),
            "outer_clauses": outer_clauses,
            "inner_orbits": len(inner_labels),
            "inner_edges": len(inner_edges),
            "inner_clauses": inner_clauses,
            "inner_conflict_budget": args.inner_conflict_budget,
            "candidate_limit": args.candidates,
            "encoding_seconds": round(monotonic() - started, 6),
        }
        events.append(encoding)
        print(json.dumps(encoding, sort_keys=True), flush=True)

        result_coloring: list[int] | None = None
        result_seed: list[int] | None = None
        unsat_candidates = 0
        interrupted_candidates = 0
        core_sizes: list[int] = []
        tested = 0

        for candidate in range(1, args.candidates + 1):
            if outer.solve() is not True:
                event = {
                    "event": "outer-exhausted",
                    "candidate": candidate,
                    "elapsed_seconds": round(monotonic() - started, 6),
                }
                events.append(event)
                print(json.dumps(event, sort_keys=True), flush=True)
                break
            tested = candidate
            outer_model = set(outer.get_model())
            orbit_colors: list[int] = []
            for vertex in range(len(outer_labels)):
                chosen = [
                    color
                    for color in range(6)
                    if outer_variable(vertex, color) in outer_model
                ]
                if len(chosen) != 1:
                    raise RuntimeError(
                        f"outer orbit {outer_labels[vertex]} has colors {chosen}"
                    )
                orbit_colors.append(chosen[0])
            seed = expand(orbit_colors, 536, outer_point_orbit)
            verify(seed)

            assumptions: list[int] = []
            assumption_to_outer: dict[int, int] = {}
            for x in range(1, 537):
                literal = inner_variable(inner_index[x], seed[x])
                assumptions.append(literal)
                assumption_to_outer[literal] = outer_variable(
                    outer_point_orbit[x], seed[x]
                )

            if args.inner_conflict_budget:
                inner.conf_budget(args.inner_conflict_budget)
                inner_result = inner.solve_limited(assumptions=assumptions)
            else:
                inner_result = inner.solve(assumptions=assumptions)

            if inner_result is True:
                inner_model = set(inner.get_model())
                inner_colors: list[int] = []
                for vertex in range(len(inner_labels)):
                    chosen = [
                        color
                        for color in range(7)
                        if inner_variable(vertex, color) in inner_model
                    ]
                    if len(chosen) != 1:
                        raise RuntimeError(
                            f"inner orbit {inner_labels[vertex]} has colors {chosen}"
                        )
                    inner_colors.append(chosen[0])
                result_coloring = expand(
                    inner_colors, args.target, inner_point_orbit
                )
                verify(result_coloring)
                result_seed = seed
                event = {
                    "event": "sat",
                    "candidate": candidate,
                    "elapsed_seconds": round(monotonic() - started, 6),
                }
                events.append(event)
                print(json.dumps(event, sort_keys=True), flush=True)
                break

            if inner_result is False:
                unsat_candidates += 1
                core = inner.get_core() or assumptions
                outer_core = {
                    assumption_to_outer[literal]
                    for literal in core
                    if literal in assumption_to_outer
                }
                if not outer_core:
                    raise RuntimeError("inner UNSAT core does not mention the seed")
                outer.add_clause(sorted(-literal for literal in outer_core))
                core_sizes.append(len(outer_core))
                label = "unsat"
                blocked_size = len(outer_core)
            else:
                interrupted_candidates += 1
                full_seed = {
                    outer_variable(outer_point_orbit[x], seed[x])
                    for x in range(1, 537)
                }
                outer.add_clause(sorted(-literal for literal in full_seed))
                label = "interrupted"
                blocked_size = len(full_seed)

            if candidate <= 10 or candidate % 100 == 0:
                event = {
                    "event": "candidate",
                    "candidate": candidate,
                    "inner_result": label,
                    "blocked_outer_literals": blocked_size,
                    "unsat_candidates": unsat_candidates,
                    "interrupted_candidates": interrupted_candidates,
                    "elapsed_seconds": round(monotonic() - started, 6),
                }
                events.append(event)
                print(json.dumps(event, sort_keys=True), flush=True)

    result = "sat" if result_coloring is not None else "no-witness"
    stats: dict[str, object] = {
        "event": "result",
        "result": result,
        "target": args.target,
        "candidates_tested": tested,
        "unsat_candidates": unsat_candidates,
        "interrupted_candidates": interrupted_candidates,
        "minimum_core_size": min(core_sizes) if core_sizes else None,
        "maximum_core_size": max(core_sizes) if core_sizes else None,
        "elapsed_seconds": round(monotonic() - started, 6),
    }
    events.append(stats)

    if result_coloring is not None:
        if args.output is None or args.seed_output is None:
            raise ValueError("--output and --seed-output are required on SAT")
        args.output.write_text(
            " ".join(map(str, result_coloring[1:])) + "\n", encoding="ascii"
        )
        args.seed_output.write_text(
            " ".join(map(str, result_seed[1:])) + "\n", encoding="ascii"
        )
        stats["output"] = str(args.output)
        stats["seed_output"] = str(args.seed_output)

    if args.log is not None:
        args.log.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, sort_keys=True), flush=True)
    if result_coloring is None:
        raise RuntimeError(json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
