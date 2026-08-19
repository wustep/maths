#!/usr/bin/env python3
"""Build the r=31, n=689 radius-4 descendant via Construction QM_4^4.

This implements Davydov--Marcugini--Pambianco, arXiv:2511.02542,
Theorem 9.1.  It glues the Oestergaard--Kaikkonen [19,8]_2 radius-4
code to the certified r=10, n=50 radius-2 code through D_5.

The accompanying top-syndrome certificate gives a nonempty sum of at most
four distinct OK2 columns for every vector of F_2^11.  The builder performs
structural checks only; compute/verify_qm44.c independently checks the matrix,
certificate, constituent coverings, and the blockwise proof for all bottom
syndromes without enumerating F_2^31.

All integer columns are LSB-first: bit i is matrix row i+1.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from fractions import Fraction
from itertools import combinations
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


OK2_HEX = (0x4EA, 0x771, 0x006, 0x086, 0x1CD, 0x3B4, 0x17E, 0x7AB)
OK2_REDUNDANCY = 11
M = 5
SIZE = 1 << M


def reverse_bits(value: int, width: int) -> int:
    """Reverse a paper-style MSB-first column into our LSB-row encoding."""
    return sum(((value >> bit) & 1) << (width - 1 - bit)
               for bit in range(width))


def ok2_columns() -> list[int]:
    """Return H_OK2=[I_11 M_OK2] with row 1 encoded in bit zero."""
    columns = [1 << row for row in range(OK2_REDUNDANCY)]
    columns.extend(reverse_bits(value, OK2_REDUNDANCY) for value in OK2_HEX)
    assert len(columns) == 19
    assert len(set(columns)) == len(columns) and all(columns)
    assert binary_rank(columns) == OK2_REDUNDANCY
    # Paper columns h_9, h_10, h_14 (one-based) are dependent.
    assert columns[8] ^ columns[9] ^ columns[13] == 0
    return columns


def covering_representatives(columns: list[int]) -> tuple[list[tuple[int, ...]], list[int]]:
    """Find the lexicographically first shortest OK2 representation."""
    representatives: list[tuple[int, ...] | None] = [None] * (1 << OK2_REDUNDANCY)
    representatives[0] = ()
    cumulative: list[int] = []
    for weight in range(1, 5):
        for chosen in combinations(range(len(columns)), weight):
            syndrome = 0
            for index in chosen:
                syndrome ^= columns[index]
            if representatives[syndrome] is None:
                representatives[syndrome] = chosen
        cumulative.append(sum(value is not None for value in representatives))
    assert cumulative == [20, 183, 981, 2048]
    assert all(value is not None for value in representatives)

    # A (4,1)-partition requires a nonempty representation also for zero.
    representatives[0] = (8, 9, 13)
    result = [value for value in representatives if value is not None]
    assert len(result) == 1 << OK2_REDUNDANCY
    assert all(1 <= len(value) <= 4 for value in result)
    return result, cumulative


def radius2_cover_count(columns: list[int], redundancy: int) -> int:
    covered = bytearray(1 << redundancy)
    covered[0] = 1
    for column in columns:
        covered[column] = 1
    for left, column in enumerate(columns):
        for right in range(left):
            covered[column ^ columns[right]] = 1
    return sum(covered)


def build_qm44(
    seed_columns: list[int], radius2_columns: list[int]
) -> tuple[int, list[int], list[int]]:
    """Return the QM_4^4 matrix with m=5 and D=D_5."""
    gf_selftest(M)
    indicators = list(range(1, len(seed_columns) + 1))
    assert len(seed_columns) == 19 <= SIZE - 1
    assert len(set(indicators)) == len(indicators) and all(indicators)

    shift_u1 = OK2_REDUNDANCY
    shift_u2 = OK2_REDUNDANCY + M
    shift_u3 = OK2_REDUNDANCY + 2 * M
    shift_u4 = OK2_REDUNDANCY + 3 * M
    columns: list[int] = []

    # D_5 = [(0,0,H_{2m},0) | (0,0,0,W_m)].  The ten rows of
    # H_{2m} occupy the u2,u3 row blocks.
    for column in radius2_columns:
        columns.append(column << shift_u2)
    for value in range(1, SIZE):
        columns.append(value << shift_u4)

    # A(h,beta) for R=4 is (h,xi,beta*xi,beta^2*xi,beta^3*xi).
    for column, beta in zip(seed_columns, indicators):
        beta_squared = gf_mul(beta, beta, M)
        beta_cubed = gf_mul(beta_squared, beta, M)
        for xi in range(SIZE):
            columns.append(
                column
                | (xi << shift_u1)
                | (gf_mul(beta, xi, M) << shift_u2)
                | (gf_mul(beta_squared, xi, M) << shift_u3)
                | (gf_mul(beta_cubed, xi, M) << shift_u4)
            )

    redundancy = OK2_REDUNDANCY + 4 * M
    expected_length = SIZE * (len(seed_columns) + 1) + len(radius2_columns) - 1
    assert redundancy == 31 and expected_length == 689
    assert len(columns) == expected_length
    assert all(0 < column < (1 << redundancy) for column in columns)
    assert len(set(columns)) == expected_length
    assert binary_rank(columns) == redundancy
    # The xi=0 lifts of the dependent OK2 triple remain dependent.
    d_offset = len(radius2_columns) + SIZE - 1
    assert (columns[d_offset + 8 * SIZE]
            ^ columns[d_offset + 9 * SIZE]
            ^ columns[d_offset + 13 * SIZE]) == 0
    return redundancy, columns, indicators


def write_top_certificate(
    path: Path, columns: list[int], representatives: list[tuple[int, ...]]
) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# QM_4^4 top-syndrome certificate\n")
        handle.write("# syndrome_decimal weight one_based_OK2_column_indices\n")
        handle.write("# Every row is a nonempty sum of 1..4 distinct columns.\n")
        for syndrome, chosen in enumerate(representatives):
            check = 0
            for index in chosen:
                check ^= columns[index]
            assert check == syndrome
            handle.write("%d %d %s\n" % (
                syndrome,
                len(chosen),
                " ".join(str(index + 1) for index in chosen),
            ))


def density(length: int, redundancy: int) -> Fraction:
    return Fraction(
        sum(math.comb(length, weight) for weight in range(5)),
        1 << redundancy,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--radius2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    radius2_r, radius2_n, radius2_columns = read_matrix(args.radius2)
    assert (radius2_r, radius2_n) == (10, 50), (
        "radius-2 input is %d x %d, expected 10 x 50" %
        (radius2_r, radius2_n)
    )
    assert binary_rank(radius2_columns) == radius2_r
    assert len(set(radius2_columns)) == radius2_n and all(radius2_columns)
    covered_radius2 = radius2_cover_count(radius2_columns, radius2_r)
    assert covered_radius2 == 1 << radius2_r
    assert has_dependent_triple(radius2_columns)

    seed_columns = ok2_columns()
    representatives, cumulative = covering_representatives(seed_columns)
    redundancy, columns, indicators = build_qm44(seed_columns, radius2_columns)
    length = len(columns)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.certificate.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    write_matrix(
        args.output,
        redundancy,
        columns,
        [
            "Construction QM_4^4 (arXiv:2511.02542 Theorem 9.1),",
            "with m=5 and D=D_5.",
            "C0 is the Oestergaard--Kaikkonen [19,8]_2 radius-4 code",
            "H_OK2=[I_11 M_OK2] from Theorem 8.3; V_10 is H_r10_n50.",
            "The 19 singleton seed blocks use GF(32) indicators 1..19;",
            "GF(32) modulus 0x%X." % MODULUS[M],
            "r=11+4*5=31; n=32*(19+1)+50-1=689.",
            "LSB-first: bit i of a column integer is row i+1.",
            "31 rows, 689 columns; generated by compute/build_qm44.py.",
        ],
    )
    write_top_certificate(args.certificate, seed_columns, representatives)

    histogram = Counter(len(value) for value in representatives)
    mu = density(length, redundancy)
    manifest = {
        "format": "covering-qm44-build-manifest-v1",
        "construction": "QM_4^4, arXiv:2511.02542 Theorem 9.1",
        "radius2_input": str(args.radius2),
        "radius2_covered_at_most_2": covered_radius2,
        "ok2_columns_decimal_lsb_first": seed_columns,
        "ok2_matrix_hex_msb_first": ["0x%03X" % value for value in OK2_HEX],
        "ok2_cumulative_covered_weights_1_to_4": cumulative,
        "ok2_dependent_triple_one_based": [9, 10, 14],
        "top_certificate": str(args.certificate),
        "top_certificate_weight_histogram": {
            str(weight): histogram[weight] for weight in range(1, 5)
        },
        "field_modulus_hex": "0x%X" % MODULUS[M],
        "indicators_decimal": indicators,
        "matrix": str(args.output),
        "redundancy": redundancy,
        "length": length,
        "rank": binary_rank(columns),
        "distinct_nonzero_columns": len(set(columns)),
        "minimum_distance": 3,
        "covering_radius": 4,
        "published_length_arxiv_2511_02542": 690,
        "improvement": 1,
        "density_numerator": mu.numerator,
        "density_denominator": mu.denominator,
        "warning": (
            "Builder checks are not the certificate; run run_qm44_checks.sh."
        ),
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built %s: r=%d n=%d rank=%d OK2<=4=%d/%d improvement=1" %
        (args.output, redundancy, length, redundancy, cumulative[-1],
         1 << OK2_REDUNDANCY)
    )


if __name__ == "__main__":
    main()
