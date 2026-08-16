#!/usr/bin/env python3
"""Test modular equivalents of the 536-point seed in Rowley's search frame."""

from __future__ import annotations

import argparse
import json
from math import gcd
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver

from search_shifted_sat import seed_coloring, verify


def transformed_seed(multiplier: int) -> list[int]:
    if gcd(multiplier, 537) != 1:
        raise ValueError("seed multiplier must be a unit modulo 537")
    seed = seed_coloring()
    colors = [-1] + [seed[(multiplier * x) % 537] for x in range(1, 537)]
    # Normalize the color at 1 to zero.  This is only a color-name permutation.
    first = colors[1]
    if first:
        colors = [-1] + [0 if color == first else first if color == 0 else color for color in colors[1:]]
    verify(colors)
    return colors


def build(target: int) -> tuple[list[list[int]], list[int], dict[int, int], callable]:
    center = target + 1
    exceptional = (center // 3, 2 * center // 3) if center % 3 == 0 else None

    def key(x: int) -> int:
        if exceptional is not None and x in exceptional:
            return x
        return min(x, center - x)

    keys = sorted({key(x) for x in range(1, target + 1)})
    key_index = {value: index for index, value in enumerate(keys)}

    def variable(key_value: int, color: int) -> int:
        return 7 * key_index[key_value] + color + 1

    clauses: list[list[int]] = []
    for key_value in keys:
        clauses.append([variable(key_value, color) for color in range(7)])
        for left in range(7):
            for right in range(left + 1, 7):
                clauses.append([-variable(key_value, left), -variable(key_value, right)])
    clauses.append([variable(key(1), 0)])
    clauses.append([variable(key(537), 6)])
    for x in range(1, 537):
        clauses.append([-variable(key(x), 6)])

    orbit_triples: set[tuple[int, ...]] = set()
    for x in range(1, target + 1):
        for y in range(x, target - x + 1):
            orbit_triples.add(tuple(sorted({key_index[key(x)], key_index[key(y)], key_index[key(x + y)]})))
    for triple in orbit_triples:
        for color in range(7):
            clauses.append([-(7 * index + color + 1) for index in triple])
    return clauses, keys, key_index, variable


def search(target: int, solver_name: str, conflict_budget: int) -> tuple[list[int], dict[str, int | float | str]]:
    started = monotonic()
    clauses, keys, key_index, variable = build(target)
    center = target + 1
    exceptional = (center // 3, 2 * center // 3) if center % 3 == 0 else None

    def key(x: int) -> int:
        if exceptional is not None and x in exceptional:
            return x
        return min(x, center - x)

    candidates = [m for m in range(1, 537) if gcd(m, 537) == 1]
    results = {"unsat": 0, "interrupted": 0}
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        for position, multiplier in enumerate(candidates, start=1):
            seed = transformed_seed(multiplier)
            assumptions = [variable(key(x), seed[x]) for x in range(1, 537)]
            if conflict_budget:
                solver.conf_budget(conflict_budget)
                result = solver.solve_limited(assumptions=assumptions)
            else:
                result = solver.solve(assumptions=assumptions)
            label = "sat" if result is True else "unsat" if result is False else "interrupted"
            print(
                json.dumps(
                    {
                        "candidate": position,
                        "multiplier": multiplier,
                        "result": label,
                        "elapsed_seconds": round(monotonic() - started, 3),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            if result is not True:
                results[label] += 1
                continue

            model = set(solver.get_model())
            key_colors: dict[int, int] = {}
            for key_value in keys:
                chosen = [color for color in range(7) if variable(key_value, color) in model]
                if len(chosen) != 1:
                    raise RuntimeError(f"orbit {key_value} has colors {chosen}")
                key_colors[key_value] = chosen[0]
            colors = [-1] + [key_colors[key(x)] for x in range(1, target + 1)]
            verify(colors)
            stats: dict[str, int | float | str] = {
                "target": target,
                "solver": solver_name,
                "seed_multiplier": multiplier,
                "candidates_tested": position,
                "unsat_candidates": results["unsat"],
                "budget_interrupted_candidates": results["interrupted"],
                "elapsed_seconds": round(monotonic() - started, 6),
                "solver_result": "sat",
            }
            return colors, stats
    raise RuntimeError(
        json.dumps(
            {
                "target": target,
                "solver": solver_name,
                "candidates_tested": len(candidates),
                "unsat_candidates": results["unsat"],
                "budget_interrupted_candidates": results["interrupted"],
                "elapsed_seconds": round(monotonic() - started, 6),
                "solver_result": "no-sat-candidate",
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1696)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--conflict-budget", type=int, default=100_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    colors, stats = search(args.target, args.solver, args.conflict_budget)
    print(json.dumps(stats, sort_keys=True), flush=True)
    if args.output:
        args.output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        print(f"wrote {args.output} ({len(colors) - 1} colors)", flush=True)


if __name__ == "__main__":
    main()
