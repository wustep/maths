#!/usr/bin/env python3
"""Independent verification of the Green m(p) table.

This verifier intentionally imports nothing from ``search_green_m_p.py``.
It recomputes ordered representation counts with plain Python loops, rematches
the published OEIS A398173 prefix, fully enumerates all subsets for p <= 13,
and compiles a Rust progression-branching search to exclude every smaller size.
The Rust algorithm does not read or rebuild the cardinality-SAT encoding.
"""

from __future__ import annotations

import argparse
import csv
from itertools import combinations
import json
import math
from pathlib import Path
import subprocess
import tempfile
from time import monotonic


HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "green_m_p.csv"
DEFAULT_REPORT = HERE / "green_m_p_verification.txt"
DEFAULT_RUST_SOURCE = HERE / "q3" / "verify_exact.rs"

PUBLISHED_A398173 = {
    3: 3,
    5: 4,
    7: 5,
    11: 7,
    13: 7,
    17: 8,
    19: 9,
    23: 10,
    29: 11,
    31: 11,
    37: 12,
    41: 13,
    43: 13,
    47: 13,
    53: 14,
}
PUBLISHED_BOUND = max(PUBLISHED_A398173)


def primes_up_to(bound: int) -> list[int]:
    return [
        candidate
        for candidate in range(3, bound + 1, 2)
        if all(candidate % divisor for divisor in range(2, math.isqrt(candidate) + 1))
    ]


def ordered_counts(p: int, values: list[int] | tuple[int, ...]) -> list[int]:
    result = [0] * p
    for left in values:
        for right in values:
            result[(left + right) % p] += 1
    return result


def independently_admissible(p: int, values: list[int] | tuple[int, ...]) -> bool:
    return all(count not in (1, 2) for count in ordered_counts(p, values))


def cyclic_arithmetic_progression(p: int, values: list[int]) -> bool:
    target = set(values)
    return any(
        {(start + index * step) % p for index in range(len(values))} == target
        for start in range(p)
        for step in range(1, p)
    )


def affine_stabilizer_size(p: int, values: list[int]) -> int:
    """Brute-force every invertible affine map, unlike the producer."""

    target = set(values)
    return sum(
        {(multiplier * value + translation) % p for value in values} == target
        for multiplier in range(1, p)
        for translation in range(p)
    )


def shape_label(p: int, values: list[int], stabilizer_size: int) -> str:
    if len(values) == p:
        return "whole group"
    if cyclic_arithmetic_progression(p, values):
        return "cyclic arithmetic progression"
    if stabilizer_size > 1:
        return "non-AP, affine-symmetric"
    return "non-AP, trivial affine stabilizer"


def exhaustive_minimum(p: int) -> tuple[int, list[int]]:
    """No symmetry reduction: inspect every subset in cardinality order."""

    residues = range(p)
    for size in range(2, p + 1):
        for candidate in combinations(residues, size):
            if independently_admissible(p, candidate):
                return size, list(candidate)
    raise AssertionError(f"the whole group should be admissible modulo {p}")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "p",
        "m",
        "witness",
        "sumset_size",
        "max_ordered_multiplicity",
        "affine_stabilizer",
        "shape",
    }
    if not rows or set(rows[0]) != required:
        raise AssertionError(f"unexpected CSV schema: {set(rows[0]) if rows else 'empty'}")
    return rows


def run_progression_branch_checks(
    rust_source: Path,
    rows_by_prime: dict[int, dict[str, str]],
) -> list[str]:
    """Compile and run the independent Rust lower-bound search."""

    if not rust_source.is_file():
        raise AssertionError(f"Rust verifier source is missing: {rust_source}")
    results: list[str] = []
    with tempfile.TemporaryDirectory(prefix="unique-sum-verify-") as temp_dir:
        executable = Path(temp_dir) / "verify_exact"
        subprocess.run(
            ["rustc", "-D", "warnings", "-O", str(rust_source), "-o", str(executable)],
            check=True,
        )
        for p, row in rows_by_prime.items():
            lower_limit = int(row["m"]) - 1
            completed = subprocess.run(
                [str(executable), str(p), str(lower_limit)],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = completed.stdout.strip().splitlines()
            if len(summary) != 1 or "status=UNSAT" not in summary[0]:
                raise AssertionError(
                    f"independent lower check failed at p={p}: {completed.stdout!r}"
                )
            print(summary[0], flush=True)
            results.append(f"EXACT_LOWER_OK {summary[0]}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--rust-source", type=Path, default=DEFAULT_RUST_SOURCE)
    parser.add_argument("--bruteforce-through", type=int, default=13)
    parser.add_argument(
        "--witnesses-only",
        action="store_true",
        help="skip the long independent lower-bound replay",
    )
    args = parser.parse_args()

    started = monotonic()
    rows = read_rows(args.csv)
    rows_by_prime = {int(row["p"]): row for row in rows}
    if len(rows_by_prime) != len(rows):
        raise AssertionError("duplicate prime in CSV")
    largest_prime = max(rows_by_prime)
    expected_primes = primes_up_to(largest_prime)
    if list(rows_by_prime) != expected_primes:
        raise AssertionError(
            f"table is not a consecutive odd-prime prefix: {list(rows_by_prime)}"
        )

    lines: list[str] = []
    ordered_pairs_checked = 0
    for p, row in rows_by_prime.items():
        values = json.loads(row["witness"])
        m_value = int(row["m"])
        if (
            len(values) != m_value
            or values != sorted(set(values))
            or any(type(value) is not int or not 0 <= value < p for value in values)
        ):
            raise AssertionError(f"malformed witness at p={p}: {values}")
        counts = ordered_counts(p, values)
        bad = [(residue, count) for residue, count in enumerate(counts) if count in (1, 2)]
        if bad:
            raise AssertionError(f"Green predicate failed at p={p}: {bad}")
        if sum(count > 0 for count in counts) != int(row["sumset_size"]):
            raise AssertionError(f"sumset-size annotation mismatch at p={p}")
        if max(counts) != int(row["max_ordered_multiplicity"]):
            raise AssertionError(f"maximum-multiplicity annotation mismatch at p={p}")
        stabilizer_size = affine_stabilizer_size(p, values)
        if stabilizer_size != int(row["affine_stabilizer"]):
            raise AssertionError(f"affine-stabilizer annotation mismatch at p={p}")
        if shape_label(p, values, stabilizer_size) != row["shape"]:
            raise AssertionError(f"shape annotation mismatch at p={p}")
        ordered_pairs_checked += m_value * m_value
        lines.append(f"WITNESS_OK p={p} m={m_value}")

    if largest_prime < PUBLISHED_BOUND:
        raise AssertionError(
            f"table ends before the required A398173 gate at p={PUBLISHED_BOUND}"
        )
    observed_prefix = {p: int(rows_by_prime[p]["m"]) for p in PUBLISHED_A398173}
    if observed_prefix != PUBLISHED_A398173:
        raise AssertionError(
            f"A398173 mismatch: expected {PUBLISHED_A398173}, got {observed_prefix}"
        )
    lines.append(
        f"A398173_MATCH {len(PUBLISHED_A398173)}/{len(PUBLISHED_A398173)} "
        f"terms through p={PUBLISHED_BOUND}"
    )

    brute_force_primes = [p for p in expected_primes if p <= args.bruteforce_through]
    for p in brute_force_primes:
        exact, example = exhaustive_minimum(p)
        claimed = int(rows_by_prime[p]["m"])
        if exact != claimed:
            raise AssertionError(
                f"independent full enumeration disagrees at p={p}: {exact} != {claimed}"
            )
        lines.append(f"FULL_ENUMERATION_OK p={p} m={exact} example={example}")

    exact_lines = (
        []
        if args.witnesses_only
        else run_progression_branch_checks(args.rust_source, rows_by_prime)
    )
    lines.extend(exact_lines)
    lines.extend(
        [
            "VALID",
            "predicate=ordered representation multiplicity avoids {1,2}",
            f"primes={len(rows)} largest_prime={largest_prime}",
            f"ordered_pairs_checked={ordered_pairs_checked}",
            f"full_enumerations={len(brute_force_primes)}",
            f"progression_branch_lower_checks={len(exact_lines)}",
            f"oeis_a398173=matched_{len(PUBLISHED_A398173)}_of_"
            f"{len(PUBLISHED_A398173)}",
            f"elapsed_seconds={monotonic() - started:.6f}",
        ]
    )
    report = "\n".join(lines) + "\n"
    args.report.write_text(report, encoding="utf-8")
    print(report, end="")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
