#!/usr/bin/env python3
"""Finite one-swap and one-cut template scans of the q3 residue."""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path


N = 1697
COLORS = 7
CORE = (537, 640, 1074, 1177)


def read_colors(path: Path) -> list[int]:
    colors = [int(token) for token in path.read_text(encoding="ascii").split()]
    if len(colors) != N or any(color not in range(COLORS) for color in colors):
        raise ValueError(f"expected {N} colors in 0..{COLORS - 1}")
    return colors


def all_edges():
    for x in range(1, N + 1):
        for y in range(x, N - x + 1):
            yield x, y, x + y


def incident_edges(vertex: int):
    # vertex is an addend, including vertex + vertex when it lies in range.
    for other in range(1, N - vertex + 1):
        x, y = sorted((vertex, other))
        yield x, y, vertex + other
    # vertex is the sum.
    for x in range(1, vertex // 2 + 1):
        y = vertex - x
        if x <= y:
            yield x, y, vertex


def is_bad(colors: list[int], edge: tuple[int, int, int]) -> bool:
    x, y, z = edge
    return colors[x - 1] == colors[y - 1] == colors[z - 1]


def violations(colors: list[int]) -> list[list[int]]:
    return [
        [x, y, z, colors[x - 1]]
        for x, y, z in all_edges()
        if colors[x - 1] == colors[y - 1] == colors[z - 1]
    ]


def apply_suffix_swap(
    colors: list[int], left: int, right: int, cut: int
) -> list[int]:
    result = colors.copy()
    for vertex in range(cut + 1, N + 1):
        if result[vertex - 1] == left:
            result[vertex - 1] = right
        elif result[vertex - 1] == right:
            result[vertex - 1] = left
    return result


def scan_core_swaps(initial: list[int]) -> tuple[dict[str, object], list[int] | None]:
    initial_bad = {tuple(row[:3]) for row in violations(initial)}
    best_count = N * N
    best_transform = None
    tested = 0
    core_incident = {vertex: set(incident_edges(vertex)) for vertex in CORE}
    for core_vertex in CORE:
        for other in range(1, N + 1):
            if other == core_vertex or initial[other - 1] == initial[core_vertex - 1]:
                continue
            tested += 1
            changed = {
                core_vertex: initial[other - 1],
                other: initial[core_vertex - 1],
            }
            touched = core_incident[core_vertex] | set(incident_edges(other))
            bad = sum(
                changed.get(x, initial[x - 1])
                == changed.get(y, initial[y - 1])
                == changed.get(z, initial[z - 1])
                for x, y, z in touched
            )
            bad += sum(
                core_vertex not in edge and other not in edge for edge in initial_bad
            )
            if bad < best_count:
                best_count = bad
                best_transform = [core_vertex, other]

    if best_transform is None:
        raise AssertionError("no proper core swap tested")
    u, v = best_transform
    candidate = initial.copy()
    candidate[u - 1], candidate[v - 1] = candidate[v - 1], candidate[u - 1]
    exact_bad = violations(candidate)
    if len(exact_bad) != best_count:
        raise AssertionError("incremental core-swap count failed exact replay")
    return (
        {
            "family": "swap one defect vertex with one differently-colored vertex",
            "tested": tested,
            "minimum_violations": best_count,
            "best_swap": {
                "vertices": best_transform,
                "old_colors": [initial[u - 1], initial[v - 1]],
            },
            "best_violations": exact_bad,
            "result": "coloring" if not exact_bad else "no-coloring",
        },
        candidate if not exact_bad else None,
    )


def scan_suffix_swaps(initial: list[int]) -> tuple[dict[str, object], list[int] | None]:
    best = (N * N, None)
    separating_best = (N * N, None)
    tested = 0
    for left, right in combinations(range(COLORS), 2):
        candidate = initial.copy()
        bad_count = len(violations(candidate))
        for vertex in range(N, 1, -1):
            old = candidate[vertex - 1]
            if old in (left, right):
                incident = tuple(incident_edges(vertex))
                before = sum(is_bad(candidate, edge) for edge in incident)
                candidate[vertex - 1] = right if old == left else left
                after = sum(is_bad(candidate, edge) for edge in incident)
                bad_count += after - before
            cut = vertex - 1
            tested += 1
            if bad_count < best[0]:
                best = (bad_count, (left, right, cut))
            # This swaps color 6 on at least one but not all defect vertices.
            if right == 6 and 537 <= cut < 1177 and bad_count < separating_best[0]:
                separating_best = (bad_count, (left, right, cut))

        # cut 0 is a global color renaming and is deliberately excluded.

    best_count, best_transform = best
    if best_transform is None or separating_best[1] is None:
        raise AssertionError("suffix scan found no transform")
    left, right, cut = best_transform
    best_candidate = apply_suffix_swap(initial, left, right, cut)
    exact_bad = violations(best_candidate)
    if len(exact_bad) != best_count:
        raise AssertionError("incremental suffix count failed exact replay")
    sep_count, sep_transform = separating_best
    sep_left, sep_right, sep_cut = sep_transform
    sep_bad = violations(apply_suffix_swap(initial, sep_left, sep_right, sep_cut))
    if len(sep_bad) != sep_count:
        raise AssertionError("defect-separating suffix count failed exact replay")
    return (
        {
            "family": "swap two color labels on one proper suffix x > cut",
            "tested": tested,
            "minimum_violations": best_count,
            "best_transform": {
                "colors": [left, right],
                "cut": cut,
                "violations": exact_bad,
            },
            "minimum_defect_separating_violations": sep_count,
            "best_defect_separating_transform": {
                "colors": [sep_left, sep_right],
                "cut": sep_cut,
                "first_violations": sep_bad[:20],
            },
            "result": "coloring" if not exact_bad else "no-coloring",
        },
        best_candidate if not exact_bad else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    colors = read_colors(args.input)
    initial_bad = violations(colors)
    if [row[:3] for row in initial_bad] != [[537, 537, 1074], [537, 640, 1177]]:
        raise ValueError(f"unexpected input violations {initial_bad}")
    swap_report, swap_coloring = scan_core_swaps(colors)
    suffix_report, suffix_coloring = scan_suffix_swaps(colors)
    coloring = swap_coloring or suffix_coloring
    report = {
        "input": args.input.name,
        "initial_violations": initial_bad,
        "core_swap": swap_report,
        "suffix_color_swap": suffix_report,
        "result": "coloring" if coloring is not None else "no-coloring",
        "warning": "The negative result applies only to the two finite transform families.",
    }
    args.log.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    if coloring is not None:
        if args.output is None:
            raise ValueError("coloring found: pass --output to preserve it")
        args.output.write_text(" ".join(map(str, coloring)) + "\n", encoding="ascii")
    elif args.output:
        args.output.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
