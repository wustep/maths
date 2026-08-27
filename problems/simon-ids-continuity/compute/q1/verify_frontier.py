#!/usr/bin/env python3
"""Verify the exact Bourgain--Klein frontier and free-direction powers."""

from __future__ import annotations

import csv
import sys
from fractions import Fraction
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def shown(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def verify_frontier(root: Path) -> list[str]:
    rows = read_rows(root / "frontier_certificate.csv")
    dimensions = [int(row["dimension"]) for row in rows]
    if dimensions != list(range(2, 9)):
        raise ValueError(f"unexpected dimension range: {dimensions}")

    report = ["Bourgain-Klein frontier", "d,gap,kappa,works"]
    for row in rows:
        dimension = int(row["dimension"])
        expected_gap = Fraction(4 - dimension, 3 * (dimension - 1))
        expected_kappa = Fraction(4 - dimension, 8)
        expected_works = dimension < 4

        stored_gap = Fraction(int(row["gap_num"]), int(row["gap_den"]))
        stored_kappa = Fraction(
            int(row["kappa_num"]), int(row["kappa_den"])
        )
        stored_works = row["works"] == "true"
        if (stored_gap, stored_kappa, stored_works) != (
            expected_gap,
            expected_kappa,
            expected_works,
        ):
            raise ValueError(f"frontier mismatch at d={dimension}")

        report.append(
            f"{dimension},{shown(expected_gap)},{shown(expected_kappa)},"
            f"{str(expected_works).lower()}"
        )
    return report


def verify_free_directions(root: Path) -> list[str]:
    rows = read_rows(root / "free_direction_certificate.csv")
    dimensions = [int(row["free_dimensions"]) for row in rows]
    if dimensions != list(range(1, 9)):
        raise ValueError(f"unexpected free-dimension range: {dimensions}")

    report = ["free-direction modulus", "m,alpha,theta"]
    for row in rows:
        dimension = int(row["free_dimensions"])
        expected_alpha = Fraction(dimension, 2)
        expected_modulus = min(Fraction(1), expected_alpha)
        stored_alpha = Fraction(int(row["alpha_num"]), int(row["alpha_den"]))
        stored_modulus = Fraction(
            int(row["modulus_num"]), int(row["modulus_den"])
        )
        if (stored_alpha, stored_modulus) != (
            expected_alpha,
            expected_modulus,
        ):
            raise ValueError(f"free-direction mismatch at m={dimension}")

        report.append(
            f"{dimension},{shown(expected_alpha)},{shown(expected_modulus)}"
        )
    return report


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).parent
    report = verify_frontier(root) + verify_free_directions(root)
    report.append("certificate verified")
    print("\n".join(report))


if __name__ == "__main__":
    main()
