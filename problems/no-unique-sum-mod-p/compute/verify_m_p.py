#!/usr/bin/env python3
"""Independently replay the witnesses and lower checks in m_p.csv.

The quick part uses only Python integer arithmetic: it recomputes every ordered
sum multiplicity, table annotation, and the complete prime index.  By default
the script also rebuilds every smaller-cardinality CP-SAT instance from the
mathematical definition and requires an INFEASIBLE result.  Pass
``--witnesses-only`` only when a fast upper-bound check is desired.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from time import monotonic

from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "m_p.csv"


def primes_up_to(bound: int) -> list[int]:
    return [
        candidate
        for candidate in range(2, bound + 1)
        if all(candidate % divisor for divisor in range(2, math.isqrt(candidate) + 1))
    ]


def ordered_counts(p: int, values: list[int]) -> list[int]:
    counts = [0] * p
    for left in values:
        for right in values:
            counts[(left + right) % p] += 1
    return counts


def midpoint_pairs(p: int, values: list[int]) -> dict[int, list[tuple[int, int]]]:
    selected = set(values)
    return {
        center: [
            ((center - difference) % p, (center + difference) % p)
            for difference in range(1, (p + 1) // 2)
            if (center - difference) % p in selected
            and (center + difference) % p in selected
        ]
        for center in values
    }


def cyclic_ap(p: int, values: list[int]) -> bool:
    selected = set(values)
    return any(
        {(start + index * step) % p for index in range(len(values))} == selected
        for start in values
        for step in range(1, p)
    )


def stabilizer_size(p: int, values: list[int]) -> int:
    if len(values) == 1:
        return p - 1
    selected = set(values)
    first, second = values[:2]
    inverse = pow(second - first, -1, p)
    stabilizer: set[tuple[int, int]] = set()
    for image_first in values:
        for image_second in values:
            if image_first == image_second:
                continue
            unit = (image_second - image_first) * inverse % p
            shift = (image_first - unit * first) % p
            if {(unit * value + shift) % p for value in values} == selected:
                stabilizer.add((unit, shift))
    return len(stabilizer)


def expected_shape(p: int, values: list[int]) -> str:
    if len(values) == p:
        return "whole group"
    if cyclic_ap(p, values):
        return "cyclic arithmetic progression"
    if stabilizer_size(p, values) > 1:
        return "non-AP, affine-symmetric"
    return "non-AP, trivial affine stabilizer"


def normalized_feasibility_model(p: int, size: int) -> cp_model.CpModel:
    """Fresh construction of the lower-bound model (no search-module import)."""

    model = cp_model.CpModel()
    residues = [model.new_int_var(0, p - 1, f"a{index}") for index in range(size)]
    model.add(residues[0] == 0)
    model.add(residues[1] == 1)
    model.add(residues[size - 1] == p - 1)
    for index in range(size - 1):
        model.add(residues[index] + 1 <= residues[index + 1])

    for center in range(1, size):
        alternatives = []
        for left in range(size):
            for right in range(left + 1, size):
                if center in (left, right):
                    continue
                for wrap in (-1, 0, 1):
                    choice = model.new_bool_var(
                        f"c{center}_l{left}_r{right}_q{wrap + 1}"
                    )
                    model.add(
                        2 * residues[center] - residues[left] - residues[right]
                        == wrap * p
                    ).only_enforce_if(choice)
                    alternatives.append(choice)
        model.add_bool_or(alternatives)
    return model


def prove_no_smaller_set(p: int, m_value: int, workers: int) -> None:
    if p == 2:
        if m_value != 2:
            raise AssertionError("the p=2 singleton lower check does not match m=2")
        return
    if m_value < 3:
        raise AssertionError(f"odd p={p} cannot have m(p)<3")
    for size in range(3, m_value):
        model = normalized_feasibility_model(p, size)
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = 0
        status = solver.solve(model)
        if status != cp_model.INFEASIBLE:
            name = solver.status_name(status)
            raise AssertionError(
                f"lower check failed for p={p}, size={size}: solver returned {name}"
            )


def parse_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "p",
        "m",
        "extremal_set",
        "internal_3aps",
        "affine_stabilizer",
        "shape",
    }
    if not rows or set(rows[0]) != required:
        raise AssertionError(f"unexpected CSV schema: {set(rows[0]) if rows else 'empty'}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--bound", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--witnesses-only",
        action="store_true",
        help="skip solver replay of all smaller cardinalities",
    )
    args = parser.parse_args()
    rows = parse_table(args.csv)
    actual_primes = [int(row["p"]) for row in rows]
    expected_primes = primes_up_to(args.bound)
    if actual_primes != expected_primes:
        raise AssertionError(
            f"prime column mismatch: expected {expected_primes}, found {actual_primes}"
        )

    started = monotonic()
    ordered_pairs_checked = 0
    lower_instances_checked = 0
    for row in rows:
        p = int(row["p"])
        m_value = int(row["m"])
        values = json.loads(row["extremal_set"])
        if (
            len(values) != m_value
            or values != sorted(set(values))
            or any(not isinstance(value, int) or not 0 <= value < p for value in values)
        ):
            raise AssertionError(f"malformed witness at p={p}: {values}")

        counts = ordered_counts(p, values)
        ordered_pairs_checked += m_value * m_value
        if any(count == 1 for count in counts):
            bad_sum = counts.index(1)
            raise AssertionError(f"p={p} has unique represented sum {bad_sum}")
        if p % 2:
            supports = midpoint_pairs(p, values)
            unsupported = [center for center, pairs in supports.items() if not pairs]
            if unsupported:
                raise AssertionError(f"p={p} has unsupported centers {unsupported}")
            progression_count = sum(len(pairs) for pairs in supports.values())
        else:
            progression_count = 0

        if progression_count != int(row["internal_3aps"]):
            raise AssertionError(f"3-AP annotation mismatch at p={p}")
        if stabilizer_size(p, values) != int(row["affine_stabilizer"]):
            raise AssertionError(f"affine-stabilizer annotation mismatch at p={p}")
        if expected_shape(p, values) != row["shape"]:
            raise AssertionError(f"shape annotation mismatch at p={p}")

        if not args.witnesses_only:
            prove_no_smaller_set(p, m_value, args.workers)
            lower_instances_checked += max(0, m_value - 3) if p != 2 else 1
        print(f"verified p={p:3d}, m={m_value:2d}", flush=True)

    mode = "witnesses and optimality" if not args.witnesses_only else "witnesses only"
    print("VALID")
    print(f"mode={mode}")
    print(f"primes={len(rows)} ordered_pairs_checked={ordered_pairs_checked}")
    print(f"lower_instances_checked={lower_instances_checked}")
    print(f"elapsed_seconds={monotonic() - started:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
