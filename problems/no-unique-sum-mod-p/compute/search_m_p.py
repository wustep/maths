#!/usr/bin/env python3
"""Compute the exact table m(p) for primes p <= 200 with CP-SAT.

For odd p, an off-diagonal representation of a sum occurs in both orders.
Consequently the only possible unique representation is (a, a), and a set A
is admissible exactly when every a in A is the midpoint of two distinct other
members of A.

The search uses affine symmetry.  Translate one such midpoint to 0 and scale
one of its two endpoints to 1.  Every nonempty admissible set for odd p is
therefore affine-equivalent to a sorted set

    0 = v[0] < v[1] = 1 < ... < v[k-1] = p-1.

For each remaining v[i], CP-SAT selects two other entries v[j], v[l] and one
q in {-1, 0, 1} such that 2*v[i] - v[j] - v[l] = q*p.  Trying cardinalities
in increasing order gives both the UNSAT lower checks and an extremal witness.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from time import monotonic

import ortools
from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "m_p.csv"
DEFAULT_CERTIFICATES = HERE / "m_p_certificates.json"


def primes_up_to(bound: int) -> list[int]:
    primes: list[int] = []
    for candidate in range(2, bound + 1):
        if all(candidate % divisor for divisor in range(2, math.isqrt(candidate) + 1)):
            primes.append(candidate)
    return primes


def representation_counts(p: int, values: list[int]) -> list[int]:
    counts = [0] * p
    for left in values:
        for right in values:
            counts[(left + right) % p] += 1
    return counts


def midpoint_supports(p: int, values: list[int]) -> dict[int, list[tuple[int, int]]]:
    value_set = set(values)
    result: dict[int, list[tuple[int, int]]] = {}
    for center in values:
        pairs: list[tuple[int, int]] = []
        for difference in range(1, (p + 1) // 2):
            left = (center - difference) % p
            right = (center + difference) % p
            if left in value_set and right in value_set:
                pairs.append((left, right))
        result[center] = pairs
    return result


def is_cyclic_arithmetic_progression(p: int, values: list[int]) -> bool:
    target = set(values)
    length = len(values)
    return any(
        {(start + index * step) % p for index in range(length)} == target
        for start in values
        for step in range(1, p)
    )


def affine_stabilizer_size(p: int, values: list[int]) -> int:
    if len(values) == 1:
        return p - 1
    target = set(values)
    source_left, source_right = values[:2]
    denominator_inverse = pow(source_right - source_left, -1, p)
    transformations: set[tuple[int, int]] = set()
    for image_left in values:
        for image_right in values:
            if image_left == image_right:
                continue
            unit = (image_right - image_left) * denominator_inverse % p
            translation = (image_left - unit * source_left) % p
            if {(unit * value + translation) % p for value in values} == target:
                transformations.add((unit, translation))
    return len(transformations)


def shape_label(p: int, values: list[int]) -> str:
    if len(values) == p:
        return "whole group"
    if is_cyclic_arithmetic_progression(p, values):
        return "cyclic arithmetic progression"
    stabilizer = affine_stabilizer_size(p, values)
    if stabilizer > 1:
        return "non-AP, affine-symmetric"
    return "non-AP, trivial affine stabilizer"


def build_normalized_model(p: int, cardinality: int) -> tuple[cp_model.CpModel, list]:
    """Build the exact normalized midpoint model for odd p and k >= 3."""

    if p % 2 == 0 or cardinality < 3:
        raise ValueError("normalized model requires odd p and cardinality at least 3")

    model = cp_model.CpModel()
    values = [model.new_int_var(0, p - 1, f"v_{index}") for index in range(cardinality)]
    model.add(values[0] == 0)
    model.add(values[1] == 1)
    model.add(values[-1] == p - 1)
    for index in range(cardinality - 1):
        model.add(values[index] < values[index + 1])

    # The center 0 is already supported by 1 and -1.  Each other selected
    # residue chooses one unordered endpoint pair from the selected entries.
    for center in range(1, cardinality):
        selectors = []
        for left in range(cardinality):
            if left == center:
                continue
            for right in range(left + 1, cardinality):
                if right == center:
                    continue
                selected = model.new_bool_var(f"support_{center}_{left}_{right}")
                wrap = model.new_int_var(-1, 1, f"wrap_{center}_{left}_{right}")
                model.add(
                    2 * values[center] - values[left] - values[right] == p * wrap
                ).only_enforce_if(selected)
                selectors.append(selected)
        model.add_bool_or(selectors)
    return model, values


def solve_cardinality(
    p: int,
    cardinality: int,
    workers: int,
    timeout_seconds: float,
) -> tuple[str, list[int] | None, dict[str, int | float | str]]:
    model, variables = build_normalized_model(p, cardinality)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 0
    if timeout_seconds:
        solver.parameters.max_time_in_seconds = timeout_seconds

    started = monotonic()
    status_code = solver.solve(model)
    elapsed = monotonic() - started
    status = solver.status_name(status_code)
    stats: dict[str, int | float | str] = {
        "cardinality": cardinality,
        "status": status,
        "elapsed_seconds": round(elapsed, 6),
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "wall_time_seconds": round(solver.wall_time, 6),
    }
    if status_code == cp_model.INFEASIBLE:
        return status, None, stats
    if status_code not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        raise RuntimeError(
            f"solver did not decide p={p}, k={cardinality}: {json.dumps(stats)}"
        )
    witness = [solver.value(variable) for variable in variables]
    return status, witness, stats


def compute_prime(
    p: int,
    workers: int,
    timeout_seconds: float,
) -> tuple[dict[str, object], dict[str, object]]:
    if p == 2:
        witness = [0, 1]
        checks: list[dict[str, int | float | str]] = [
            {
                "cardinality": 1,
                "status": "INFEASIBLE (direct singleton argument)",
                "elapsed_seconds": 0.0,
                "branches": 0,
                "conflicts": 0,
                "wall_time_seconds": 0.0,
            }
        ]
    else:
        checks = [
            {
                "cardinality": size,
                "status": "INFEASIBLE (fewer than two other endpoints)",
                "elapsed_seconds": 0.0,
                "branches": 0,
                "conflicts": 0,
                "wall_time_seconds": 0.0,
            }
            for size in (1, 2)
        ]
        witness = []
        for cardinality in range(3, p + 1):
            _, candidate, stats = solve_cardinality(
                p, cardinality, workers, timeout_seconds
            )
            checks.append(stats)
            if candidate is not None:
                witness = candidate
                break
        if not witness:
            raise RuntimeError(f"failed to find the always-valid whole group for p={p}")

    counts = representation_counts(p, witness)
    if any(count == 1 for count in counts):
        raise AssertionError(f"solver returned an invalid witness for p={p}: {witness}")
    supports = midpoint_supports(p, witness) if p % 2 else {}
    internal_progressions = sum(len(pairs) for pairs in supports.values())
    stabilizer = affine_stabilizer_size(p, witness)
    row: dict[str, object] = {
        "p": p,
        "m": len(witness),
        "extremal_set": json.dumps(witness, separators=(",", ":")),
        "internal_3aps": internal_progressions,
        "affine_stabilizer": stabilizer,
        "shape": shape_label(p, witness),
    }
    certificate: dict[str, object] = {
        "p": p,
        "m": len(witness),
        "witness": witness,
        "ordered_representation_counts": counts,
        "midpoint_supports": {
            str(center): [list(pair) for pair in pairs]
            for center, pairs in supports.items()
        },
        "cardinality_checks": checks,
    }
    return row, certificate


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "p",
                "m",
                "extremal_set",
                "internal_3aps",
                "affine_stabilizer",
                "shape",
            ),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=0.0,
        help="per-cardinality limit; zero means no limit and is required for a full table",
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--certificates", type=Path, default=DEFAULT_CERTIFICATES)
    args = parser.parse_args()
    if args.bound < 2 or args.workers < 1:
        parser.error("bound must be at least 2 and workers must be positive")

    started = monotonic()
    rows: list[dict[str, object]] = []
    certificates: list[dict[str, object]] = []
    for p in primes_up_to(args.bound):
        row, certificate = compute_prime(p, args.workers, args.timeout_seconds)
        rows.append(row)
        certificates.append(certificate)
        print(
            f"p={p:3d} m={row['m']:>2} A={row['extremal_set']} "
            f"shape={row['shape']}",
            flush=True,
        )

    write_csv(args.csv, rows)
    payload = {
        "schema_version": 1,
        "claim": "exact m(p) for every prime p at most the requested bound",
        "bound": args.bound,
        "method": "sorted affine-normalized midpoint CP-SAT feasibility by cardinality",
        "normalization": "for odd p, 0, 1, and p-1 are selected",
        "ortools_version": ortools.__version__,
        "workers": args.workers,
        "timeout_seconds_per_cardinality": args.timeout_seconds,
        "elapsed_seconds": round(monotonic() - started, 6),
        "records": certificates,
    }
    args.certificates.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.csv}")
    print(f"wrote {args.certificates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
