#!/usr/bin/env python3
"""Build the Golay radius-3 descendants via Construction QM_5^3.

This implements Davydov--Marcugini--Pambianco, arXiv:2511.02542,
Theorem 7.3 (also denoted QM_3^5).  It glues the perfect binary Golay
[23,12,7] radius-3 code to certified radius-2 codes V_{2m}.  Repeated
--radius2/--output options build the m=5,9,10 cases at r=26,38,41.

The builder checks its inputs and output structurally, but it is not the
certificate.  The standalone checks verify each V_{2m}, every construction
identity, and (only where feasible) sweep all 2^26 output syndromes.

Run from problems/covering/:

  python3 compute/build_qm35.py \
      --radius2 compute/H_r10_n50.txt \
      --radius2 result/data/H_r18_n815.txt \
      --radius2 result/data/H_r20_n1631.txt \
      --output compute/H_R3_r26_n817.txt \
      --output compute/H_R3_r38_n13102.txt \
      --output compute/H_R3_r41_n26206.txt \
      --manifest compute/qm35_build_manifest.json

All integer columns are LSB-first: bit i is matrix row i+1.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

from build_qm3 import (
    MODULUS,
    binary_rank,
    gf_mul,
    gf_selftest,
    has_dependent_triple,
    read_matrix,
    write_matrix,
)


GOLAY_GENERATOR_POLYNOMIAL = sum(
    1 << exponent for exponent in (0, 1, 5, 6, 7, 9, 11)
)

EXPECTED_CASES = {
    5: {
        "radius2_redundancy": 10,
        "radius2_length": 50,
        "output_redundancy": 26,
        "output_length": 817,
        "published_length": 818,
    },
    9: {
        "radius2_redundancy": 18,
        "radius2_length": 815,
        "output_redundancy": 38,
        "output_length": 13102,
        "published_length": 13118,
    },
    10: {
        "radius2_redundancy": 20,
        "radius2_length": 1631,
        "output_redundancy": 41,
        "output_length": 26206,
        "published_length": 26238,
    },
}


def parity(value: int) -> int:
    return value.bit_count() & 1


def nullspace_basis(rows: list[int], width: int) -> list[int]:
    """Return a binary nullspace basis for row vectors of the given width."""
    reduced = list(rows)
    pivot_columns: list[int] = []
    next_row = 0
    for column in range(width):
        pivot_row = next(
            (
                row
                for row in range(next_row, len(reduced))
                if (reduced[row] >> column) & 1
            ),
            None,
        )
        if pivot_row is None:
            continue
        reduced[next_row], reduced[pivot_row] = (
            reduced[pivot_row],
            reduced[next_row],
        )
        for row in range(len(reduced)):
            if row != next_row and ((reduced[row] >> column) & 1):
                reduced[row] ^= reduced[next_row]
        pivot_columns.append(column)
        next_row += 1
        if next_row == len(reduced):
            break
    assert next_row == len(rows), "generator rows are not independent"

    pivot_set = set(pivot_columns)
    free_columns = [
        column for column in range(width) if column not in pivot_set
    ]
    basis: list[int] = []
    for free in free_columns:
        vector = 1 << free
        for row, pivot_column in enumerate(pivot_columns):
            if (reduced[row] >> free) & 1:
                vector |= 1 << pivot_column
        basis.append(vector)
    assert all(parity(row & vector) == 0 for row in rows for vector in basis)
    return basis


def golay_parity_check() -> tuple[list[int], list[int]]:
    """Construct and recheck a cyclic perfect binary Golay code."""
    generator_rows = [GOLAY_GENERATOR_POLYNOMIAL << shift for shift in range(12)]
    assert all(row < (1 << 23) for row in generator_rows)

    # Exhaust all 4095 nonzero codewords rather than trusting the polynomial's
    # label.  This certifies the generated [23,12] code has minimum distance 7.
    minimum_distance = 23
    for message in range(1, 1 << 12):
        codeword = 0
        for row, generator in enumerate(generator_rows):
            if (message >> row) & 1:
                codeword ^= generator
        minimum_distance = min(minimum_distance, codeword.bit_count())
    assert minimum_distance == 7

    check_rows = nullspace_basis(generator_rows, 23)
    assert len(check_rows) == 11
    columns = [
        sum(((row >> column) & 1) << index for index, row in enumerate(check_rows))
        for column in range(23)
    ]
    assert binary_rank(columns) == 11
    assert len(set(columns)) == 23 and all(columns)

    # A perfect [23,12,7] code has 1+23+C(23,2)+C(23,3)=2^11 distinct
    # syndromes of weight at most 3.  Recompute all of them explicitly.
    covered = {0}
    for left, a in enumerate(columns):
        covered.add(a)
        for middle in range(left):
            ab = a ^ columns[middle]
            covered.add(ab)
            for right in range(middle):
                covered.add(ab ^ columns[right])
    assert len(covered) == 1 << 11
    assert 1 + 23 + math.comb(23, 2) + math.comb(23, 3) == 1 << 11
    return columns, check_rows


def exact_three_sum_count(columns: list[int], redundancy: int) -> int:
    """Count syndromes represented by exactly 3 distinct input columns."""
    covered = bytearray(1 << redundancy)
    for left, a in enumerate(columns):
        for middle in range(left):
            ab = a ^ columns[middle]
            for right in range(middle):
                covered[ab ^ columns[right]] = 1
    return sum(covered)


def build_qm35(
    golay_columns: list[int],
    radius2_redundancy: int,
    radius2_columns: list[int],
) -> tuple[int, list[int], list[int], int]:
    """Return the QM_5^3 matrix with D=D_4 and V_{2m}."""
    assert radius2_redundancy % 2 == 0
    m = radius2_redundancy // 2
    assert m in EXPECTED_CASES
    size = 1 << m
    r0 = 11
    gf_selftest(m)
    assert len(golay_columns) == 23 <= size - 1
    assert len(radius2_columns) == EXPECTED_CASES[m]["radius2_length"]

    # The Golay seed uses the trivial (3,0)-partition, so its 23 columns get
    # 23 distinct nonzero field indicators, as required by Theorem 7.3.
    indicators = list(range(1, len(golay_columns) + 1))
    assert len(set(indicators)) == 23 and all(indicators)

    shift_u1 = r0
    shift_u2 = r0 + m
    shift_u3 = r0 + 2 * m
    columns: list[int] = []

    # D_4 = [(0,W_m,0,0) | (0,0,H_{2m})].
    for value in range(1, size):
        columns.append(value << shift_u1)
    for column in radius2_columns:
        columns.append(column << shift_u2)

    # A(h,beta) for R=3 is (h,xi,beta*xi,beta^2*xi).
    for column, beta in zip(golay_columns, indicators):
        beta_squared = gf_mul(beta, beta, m)
        for xi in range(size):
            columns.append(
                column
                | (xi << shift_u1)
                | (gf_mul(beta, xi, m) << shift_u2)
                | (gf_mul(beta_squared, xi, m) << shift_u3)
            )

    r = r0 + 3 * m
    expected_n = size * (len(golay_columns) + 1) + len(radius2_columns) - 1
    case = EXPECTED_CASES[m]
    assert r == case["output_redundancy"]
    assert expected_n == case["output_length"]
    assert len(columns) == expected_n
    assert all(0 < column < (1 << r) for column in columns)
    assert len(set(columns)) == expected_n
    assert binary_rank(columns) == r
    assert has_dependent_triple(columns), "output should have minimum distance 3"
    return r, columns, indicators, m


def density(n: int, r: int) -> Fraction:
    return Fraction(sum(math.comb(n, weight) for weight in range(4)), 1 << r)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--radius2", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, action="append", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    assert len(args.radius2) == len(args.output), (
        "each --radius2 must have one corresponding --output")
    assert len(set(args.radius2)) == len(args.radius2), (
        "radius-2 input paths must be distinct")
    assert len(set(args.output)) == len(args.output), (
        "output paths must be distinct")

    golay_columns, golay_check_rows = golay_parity_check()
    records = []
    seen_m: set[int] = set()
    for radius2_path, output_path in zip(args.radius2, args.output):
        radius2_r, radius2_n, radius2_columns = read_matrix(radius2_path)
        assert radius2_r % 2 == 0
        m = radius2_r // 2
        assert m in EXPECTED_CASES, "unsupported V_2m redundancy %d" % radius2_r
        assert m not in seen_m, "duplicate m=%d case" % m
        seen_m.add(m)
        case = EXPECTED_CASES[m]
        assert (radius2_r, radius2_n) == (
            case["radius2_redundancy"], case["radius2_length"]
        ), (
            "radius-2 input is %d x %d, expected %d x %d for m=%d" %
            (
                radius2_r,
                radius2_n,
                case["radius2_redundancy"],
                case["radius2_length"],
                m,
            )
        )
        assert binary_rank(radius2_columns) == radius2_r
        assert len(set(radius2_columns)) == radius2_n and all(radius2_columns)

        three_sum_count = None
        if m == 5:
            three_sum_count = exact_three_sum_count(radius2_columns, radius2_r)
            assert three_sum_count == 1 << radius2_r, (
                "V_10 fails exact-three-sum property: %d/%d" %
                (three_sum_count, 1 << radius2_r)
            )

        r, columns, indicators, built_m = build_qm35(
            golay_columns, radius2_r, radius2_columns)
        assert built_m == m
        n = len(columns)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_matrix(
            output_path,
            r,
            columns,
            [
                "Construction QM_5^3 / QM_3^5 (arXiv:2511.02542 Theorem 7.3),",
                "with m=%d and D=D_4." % m,
                "C0 is the cyclic perfect binary Golay [23,12,7]_2 radius-3",
                "code; V_%d is the certified %s radius-2 code." %
                (2 * m, radius2_path),
                "Golay generator polynomial 0x%X; GF(2^%d) modulus 0x%X." %
                (GOLAY_GENERATOR_POLYNOMIAL, m, MODULUS[m]),
                "The 23 Golay singleton blocks use distinct indicators 1..23.",
                "r=11+3*%d=%d; n=2^%d*(23+1)+%d-1=%d." %
                (m, r, m, radius2_n, n),
                "LSB-first: bit i of a column integer is row i+1.",
                "%d rows, %d columns; generated by compute/build_qm35.py." %
                (r, n),
            ],
        )

        mu = density(n, r)
        records.append({
            "m": m,
            "radius2_input": str(radius2_path),
            "radius2_redundancy": radius2_r,
            "radius2_length": radius2_n,
            "radius2_exact_three_sum_syndromes": three_sum_count,
            "field_modulus_hex": "0x%X" % MODULUS[m],
            "indicators_decimal": indicators,
            "golay_partition_blocks": 23,
            "matrix": str(output_path),
            "redundancy": r,
            "length": n,
            "rank": binary_rank(columns),
            "distinct_nonzero_columns": len(set(columns)),
            "published_length_arxiv_2511_02542": case["published_length"],
            "improvement": case["published_length"] - n,
            "density_numerator": mu.numerator,
            "density_denominator": mu.denominator,
            "coverage_status": (
                "exhaustive matrix sweep" if r == 26
                else "Theorem 7.3 after independent hypothesis and identity checks"
            ),
        })
        print(
            "built %s: m=%d r=%d n=%d rank=%d improvement=%d" %
            (
                output_path,
                m,
                r,
                n,
                r,
                case["published_length"] - n,
            )
        )

    manifest = {
        "format": "covering-qm35-build-manifest-v2",
        "construction": "QM_5^3 / QM_3^5, arXiv:2511.02542 Theorem 7.3",
        "golay_generator_polynomial_hex": "0x%X" % GOLAY_GENERATOR_POLYNOMIAL,
        "golay_parity_check_rows_hex": ["0x%X" % row for row in golay_check_rows],
        "golay_parity_check_columns_decimal": golay_columns,
        "golay_partition": "23 singleton blocks (a (3,0)-partition)",
        "records": sorted(records, key=lambda record: record["m"]),
        "warning": "Builder checks are not the certificate; run run_qm35_checks.sh.",
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
