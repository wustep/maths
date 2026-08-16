#!/usr/bin/env python3
"""Search a complement-symmetric 7-coloring near Rowley's S(7) seed.

The six-color seed is the 536-point Fredricksen--Sweet partition.  Its
published table lists the smaller member of each pair {x, 537-x}, except
for the explicitly asymmetric pair 179/358.  For a requested target N we
freeze this seed and reflect it about N+1, put 537 in the seventh color,
and ask Z3 to color the remaining complement orbits.

This is a construction search, not an optimality encoding.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import monotonic

from z3 import Bool, Or, Solver, is_true, sat


SEED_HALF: tuple[tuple[int, ...], ...] = (
    (
        1, 5, 8, 11, 14, 24, 27, 30, 33, 36, 40, 43, 46, 49, 52, 65,
        71, 77, 81, 84, 90, 93, 99, 103, 109, 112, 115, 125, 128, 131,
        134, 137, 144, 147, 150, 153, 160, 163, 166, 169, 172, 181, 185,
        188, 191, 194, 201, 204, 207, 213, 220, 223, 226, 229, 232, 235,
        238, 242, 245, 248, 251, 254, 264, 267, 358,
    ),
    (
        2, 12, 19, 25, 26, 34, 41, 57, 58, 63, 72, 79, 85, 86, 95, 96,
        102, 118, 123, 124, 140, 141, 145, 146, 155, 156, 162, 173, 183,
        193, 200, 206, 211, 215, 216, 222, 233, 239, 244, 253, 260, 261,
        266,
    ),
    (
        3, 10, 16, 22, 23, 29, 35, 42, 48, 56, 60, 62, 67, 68, 69, 74,
        75, 80, 87, 88, 94, 100, 101, 106, 107, 113, 114, 119, 121, 126,
        133, 139, 151, 152, 158, 159, 164, 165, 171, 178, 184, 192, 197,
        198, 203, 205, 210, 217, 237, 241, 243, 249, 250, 255, 256,
    ),
    (
        4, 13, 20, 28, 31, 38, 50, 61, 64, 73, 83, 91, 98, 108, 110,
        117, 120, 132, 135, 142, 143, 154, 161, 168, 177, 179, 187, 195,
        209, 212, 214, 219, 221, 224, 231, 236, 246, 258, 265,
    ),
    (
        6, 9, 17, 21, 32, 39, 44, 51, 54, 55, 66, 70, 82, 89, 92, 104,
        111, 127, 129, 130, 149, 167, 175, 189, 190, 202, 225, 227, 247,
        252, 262, 263,
    ),
    (
        7, 15, 18, 37, 45, 47, 53, 59, 76, 78, 97, 105, 116, 122, 136,
        138, 148, 157, 170, 174, 176, 180, 182, 186, 196, 199, 208, 218,
        228, 230, 234, 240, 257, 259, 268,
    ),
)


def seed_coloring() -> list[int]:
    """Return the Fredricksen--Sweet coloring of [536], zero-indexed."""
    colors = [-1] * 537
    for color, entries in enumerate(SEED_HALF):
        for x in entries:
            if colors[x] != -1:
                raise ValueError(f"duplicate seed entry {x}")
            colors[x] = color

    # Every unlisted point is the complement of one listed point.  The sole
    # exception was already listed on both sides: 179 has color 3 and 358 color 0.
    for x in range(1, 537):
        if colors[x] == -1:
            colors[x] = colors[537 - x]
        if colors[x] == -1:
            raise ValueError(f"uncovered seed entry {x}")
    return colors


def verify(colors: list[int]) -> None:
    """Raise on a malformed coloring or the first monochromatic Schur triple."""
    n = len(colors) - 1
    if colors[0] != -1 or any(not 0 <= colors[x] < 7 for x in range(1, n + 1)):
        raise ValueError("color vector must be [-1, c(1), ..., c(N)] with colors 0..6")
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            z = x + y
            if colors[x] == colors[y] == colors[z]:
                raise ValueError(f"monochromatic triple ({x}, {y}, {z}) in color {colors[x]}")


def search(target: int, timeout_ms: int) -> tuple[list[int], dict[str, int | float | str]]:
    if target < 1073:
        raise ValueError("target must leave room for the seed and its reflection")

    seed = seed_coloring()
    verify(seed)
    center = target + 1

    def representative(x: int) -> int:
        return min(x, center - x)

    # Representatives up through 536 are frozen; representative 537 gets the
    # new color.  All higher representatives are SAT variables.
    variable_reps = list(range(538, (center // 2) + 1))
    cells = {(rep, color): Bool(f"x_{rep}_{color}") for rep in variable_reps for color in range(7)}
    solver = Solver()
    if timeout_ms:
        solver.set(timeout=timeout_ms)

    for rep in variable_reps:
        solver.add(Or(*(cells[rep, color] for color in range(7))))
        for left in range(7):
            for right in range(left + 1, 7):
                solver.add(Or(~cells[rep, left], ~cells[rep, right]))

    def literal(x: int, color: int):
        rep = representative(x)
        if rep <= 536:
            return seed[rep] == color
        if rep == 537:
            return color == 6
        return cells[rep, color]

    # Deduplicate clauses after orbit folding.  Constants are simplified here,
    # so contradictions in the fixed seed are detected before solver search.
    clauses: set[tuple[str, ...]] = set()
    for x in range(1, target + 1):
        for y in range(x, target - x + 1):
            z = x + y
            for color in range(7):
                lits = (literal(x, color), literal(y, color), literal(z, color))
                if any(value is False for value in lits):
                    continue
                symbolic = tuple(sorted({str(value) for value in lits if value is not True}))
                if not symbolic:
                    raise ValueError(f"fixed monochromatic triple ({x}, {y}, {z}), color {color}")
                clauses.add(symbolic)

    name_to_cell = {str(cell): cell for cell in cells.values()}
    for clause in clauses:
        solver.add(Or(*(~name_to_cell[name] for name in clause)))

    started = monotonic()
    result = solver.check()
    elapsed = monotonic() - started
    stats: dict[str, int | float | str] = {
        "target": target,
        "center": center,
        "variable_orbits": len(variable_reps),
        "boolean_variables": len(cells),
        "schur_clauses_after_folding": len(clauses),
        "elapsed_seconds": round(elapsed, 6),
        "solver_result": str(result),
    }
    if result != sat:
        raise RuntimeError(json.dumps(stats, sort_keys=True))

    model = solver.model()
    representative_colors = seed[:]
    representative_colors.extend([-1] * (max(variable_reps, default=537) - 536))
    representative_colors[537] = 6
    for rep in variable_reps:
        chosen = [color for color in range(7) if is_true(model.eval(cells[rep, color], model_completion=True))]
        if len(chosen) != 1:
            raise RuntimeError(f"model assigns representative {rep} colors {chosen}")
        representative_colors[rep] = chosen[0]

    colors = [-1] + [representative_colors[representative(x)] for x in range(1, target + 1)]
    verify(colors)
    return colors, stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1697)
    parser.add_argument("--timeout-ms", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    colors, stats = search(args.target, args.timeout_ms)
    print(json.dumps(stats, sort_keys=True))
    if args.output:
        args.output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        print(f"wrote {args.output} ({len(colors) - 1} colors)")


if __name__ == "__main__":
    main()
