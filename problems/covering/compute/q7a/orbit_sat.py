#!/usr/bin/env python3
"""Exact SAT search for a G-invariant 49-column radius-two covering.

This is an independent replacement for the subset DFS used in q4.  It
rebuilds point orbits directly from a .grp file, uses one Boolean per orbit,
and Tseitin variables for cross-orbit sums.  A small BDD enforces the exact
weighted cardinality 49.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195, Kissat404


R = 10
V = 1 << R


def read_group(path: Path) -> list[list[int]]:
    generators: list[list[int]] = []
    for line in path.read_text().splitlines():
        if not line or line.lstrip().startswith("#"):
            continue
        images = [int(token, 0) for token in line.split()]
        if len(images) != R or any(not 0 <= value < V for value in images):
            raise ValueError(f"malformed generator in {path}")
        generators.append(images)
    if not generators:
        raise ValueError(f"no generators in {path}")
    return generators


def apply_generator(images: list[int], value: int) -> int:
    output = 0
    while value:
        bit = (value & -value).bit_length() - 1
        output ^= images[bit]
        value &= value - 1
    return output


def point_orbits(generators: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    orbit_of = [-1] * V
    raw: list[list[int]] = []
    for start in range(1, V):
        if orbit_of[start] >= 0:
            continue
        orbit_id = len(raw)
        orbit_of[start] = orbit_id
        queue = deque([start])
        points: list[int] = []
        while queue:
            value = queue.popleft()
            points.append(value)
            for generator in generators:
                image = apply_generator(generator, value)
                if orbit_of[image] < 0:
                    orbit_of[image] = orbit_id
                    queue.append(image)
        raw.append(sorted(points))
    orbits = sorted(raw, key=lambda orbit: (-len(orbit), orbit[0]))
    class_of = [-1] * V
    for orbit_id, orbit in enumerate(orbits):
        for value in orbit:
            class_of[value] = orbit_id
    return orbits, class_of


def add_exact_weight_bdd(
    clauses: list[list[int]], pool: IDPool, literals: list[int],
    weights: list[int], target: int,
) -> None:
    true_var = pool.id(("constant", True))
    false_var = pool.id(("constant", False))
    clauses.extend([[true_var], [-false_var]])
    memo: dict[tuple[int, int], int] = {}

    def node(index: int, remaining: int) -> int:
        if remaining < 0:
            return false_var
        if index == len(literals):
            return true_var if remaining == 0 else false_var
        key = (index, remaining)
        if key in memo:
            return memo[key]
        output = pool.id(("weight", index, remaining))
        low = node(index + 1, remaining)
        high = node(index + 1, remaining - weights[index])
        selected = literals[index]
        # output <-> (selected ? high : low)
        clauses.extend([
            [-output, -selected, high],
            [-output, selected, low],
            [output, -selected, -high],
            [output, selected, -low],
        ])
        memo[key] = output
        return output

    clauses.append([node(0, target)])


def verify(columns: list[int]) -> tuple[int, int]:
    covered = bytearray(V)
    covered[0] = 1
    basis = [0] * R
    rank = 0
    for index, left in enumerate(columns):
        covered[left] = 1
        for right in columns[:index]:
            covered[left ^ right] = 1
        value = left
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return V - covered.count(0), rank


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--n", type=int, default=49)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--solver", choices=("cadical", "kissat"),
                        default="cadical")
    parser.add_argument(
        "--size-count", action="append", default=[], metavar="SIZE=COUNT",
        help="branch on exactly COUNT selected point-orbits of the given SIZE",
    )
    parser.add_argument(
        "--projection-atmost-one", type=int, metavar="BITS",
        help="allow at most one selected orbit above each nonzero orbit in "
             "the low-BITS coordinate projection",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    generators = read_group(args.group)
    orbits, class_of = point_orbits(generators)
    pool = IDPool()
    selected = [pool.id(("orbit", index)) for index in range(len(orbits))]
    clauses: list[list[int]] = []
    coverage: list[list[int]] = [[] for _ in orbits]

    for index, orbit in enumerate(orbits):
        classes = {index}
        for left_index, left in enumerate(orbit):
            for right in orbit[:left_index]:
                classes.add(class_of[left ^ right])
        for syndrome_class in classes:
            coverage[syndrome_class].append(selected[index])

    for left_index, left_orbit in enumerate(orbits):
        for right_index in range(left_index):
            right_orbit = orbits[right_index]
            pair = pool.id(("pair", right_index, left_index))
            clauses.extend([
                [-pair, selected[right_index]],
                [-pair, selected[left_index]],
                [-selected[right_index], -selected[left_index], pair],
            ])
            classes = {
                class_of[left ^ right]
                for left in left_orbit
                for right in right_orbit
            }
            for syndrome_class in classes:
                coverage[syndrome_class].append(pair)

    if any(not literals for literals in coverage):
        print(f"RESULT group={args.group} n={args.n} witnesses=0 "
              "(empty orbit-coverage clause)", flush=True)
        return 0
    clauses.extend(coverage)
    add_exact_weight_bdd(
        clauses, pool, selected, [len(orbit) for orbit in orbits], args.n
    )
    for specification in args.size_count:
        size_text, separator, count_text = specification.partition("=")
        if not separator:
            raise SystemExit("--size-count must have the form SIZE=COUNT")
        size = int(size_text)
        count = int(count_text)
        literals = [
            selected[index] for index, orbit in enumerate(orbits)
            if len(orbit) == size
        ]
        clauses.extend(CardEnc.equals(
            literals, count, vpool=pool, encoding=EncType.seqcounter
        ).clauses)
    if args.projection_atmost_one is not None:
        mask = (1 << args.projection_atmost_one) - 1
        projected: dict[tuple[int, ...], list[int]] = {}
        for index, orbit in enumerate(orbits):
            image = tuple(sorted({value & mask for value in orbit}))
            if image == (0,):
                continue
            projected.setdefault(image, []).append(selected[index])
        for literals in projected.values():
            clauses.extend(CardEnc.atmost(
                literals, 1, vpool=pool, encoding=EncType.seqcounter
            ).clauses)
    histogram: dict[int, int] = {}
    for orbit in orbits:
        histogram[len(orbit)] = histogram.get(len(orbit), 0) + 1
    print(
        f"group={args.group} generators={len(generators)} "
        f"orbits={len(orbits)} sizes={histogram} vars={pool.top} "
        f"clauses={len(clauses)}",
        flush=True,
    )
    solver_class = Cadical195 if args.solver == "cadical" else Kissat404
    with solver_class(bootstrap_with=clauses) as solver:
        if args.solver == "cadical":
            solver.configure({"seed": args.seed})
        satisfiable = solver.solve()
        stats = solver.accum_stats()
        if not satisfiable:
            print(
                f"RESULT group={args.group} n={args.n} witnesses=0 "
                f"conflicts={stats.get('conflicts', -1)} "
                "(exhausted by orbit SAT)",
                flush=True,
            )
            return 0
        model = {literal for literal in solver.get_model() if literal > 0}

    chosen = [
        index for index, literal in enumerate(selected) if literal in model
    ]
    columns = sorted(value for index in chosen for value in orbits[index])
    covered, rank = verify(columns)
    if (len(columns) != args.n or len(columns) != len(set(columns)) or
            any(not 0 < value < V for value in columns) or
            rank != R or covered != V):
        raise RuntimeError(
            f"bad SAT model: n={len(columns)} rank={rank} covered={covered}/{V}"
        )
    print("WITNESS columns: " + " ".join(map(str, columns)), flush=True)
    print(
        f"RESULT group={args.group} n={args.n} witnesses=1 "
        f"rank={rank} covered={covered}/{V}",
        flush=True,
    )
    if args.output:
        args.output.write_text(" ".join(map(str, columns)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
