#!/usr/bin/env python3
"""Independent arithmetic verification of the Green m(p) table.

This verifier intentionally imports nothing from ``search_green_m_p.py``.
It recomputes ordered representation counts with plain Python loops, rematches
the published OEIS A398173 prefix, fully enumerates all subsets for p <= 13,
and checks that the certificate log contains an UNSAT cardinality-SAT result
for every size below each claimed minimum.
"""

from __future__ import annotations

import argparse
import csv
from itertools import combinations
import json
import math
from pathlib import Path
from time import monotonic
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "green_m_p.csv"
DEFAULT_CERTIFICATES = HERE / "green_m_p_certificates.json"
DEFAULT_REPORT = HERE / "green_m_p_verification.txt"

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
}


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


def check_certificate_log(
    payload: dict[str, Any],
    rows_by_prime: dict[int, dict[str, str]],
) -> int:
    if payload.get("predicate") != "all ordered representation counts avoid 1 and 2":
        raise AssertionError("certificate predicate does not name the Green condition")
    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("certificate records are missing")
    records_by_prime = {int(record["p"]): record for record in records}
    if set(records_by_prime) != set(rows_by_prime):
        raise AssertionError("certificate and CSV prime sets differ")

    unsat_checks = 0
    for p, row in rows_by_prime.items():
        m_value = int(row["m"])
        record = records_by_prime[p]
        if int(record["m"]) != m_value or record["witness"] != json.loads(row["witness"]):
            raise AssertionError(f"certificate/CSV mismatch at p={p}")
        checks = {int(check["cardinality"]): check for check in record["cardinality_checks"]}
        for cardinality in range(3, m_value):
            check = checks.get(cardinality)
            if check is None or check.get("status") != "UNSAT":
                raise AssertionError(
                    f"missing exhaustive UNSAT result for p={p}, k={cardinality}"
                )
            unsat_checks += 1
    return unsat_checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--certificates", type=Path, default=DEFAULT_CERTIFICATES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--bruteforce-through", type=int, default=13)
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
        ordered_pairs_checked += m_value * m_value
        lines.append(f"WITNESS_OK p={p} m={m_value}")

    if largest_prime < 47:
        raise AssertionError("table ends before the required A398173 gate at p=47")
    observed_prefix = {p: int(rows_by_prime[p]["m"]) for p in PUBLISHED_A398173}
    if observed_prefix != PUBLISHED_A398173:
        raise AssertionError(
            f"A398173 mismatch: expected {PUBLISHED_A398173}, got {observed_prefix}"
        )
    lines.append("A398173_MATCH 14/14 terms through p=47")

    brute_force_primes = [p for p in expected_primes if p <= args.bruteforce_through]
    for p in brute_force_primes:
        exact, example = exhaustive_minimum(p)
        claimed = int(rows_by_prime[p]["m"])
        if exact != claimed:
            raise AssertionError(
                f"independent full enumeration disagrees at p={p}: {exact} != {claimed}"
            )
        lines.append(f"FULL_ENUMERATION_OK p={p} m={exact} example={example}")

    with args.certificates.open(encoding="utf-8") as handle:
        certificate_payload = json.load(handle)
    unsat_checks = check_certificate_log(certificate_payload, rows_by_prime)
    lines.extend(
        [
            "VALID",
            "predicate=ordered representation multiplicity avoids {1,2}",
            f"primes={len(rows)} largest_prime={largest_prime}",
            f"ordered_pairs_checked={ordered_pairs_checked}",
            f"full_enumerations={len(brute_force_primes)}",
            f"cardinality_sat_unsat_checks={unsat_checks}",
            "oeis_a398173=matched_14_of_14",
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
