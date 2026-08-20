#!/usr/bin/env python3
"""Independently verify the QM_2^1 construction identity at r=26.

This checker shares no imports with build_qm21.py.  It reparses the
certified r=18 seed and 17-block partition, checks every QM_2^1
hypothesis of arXiv:2511.02542 Theorem 4.1, and matches every emitted
column against D_2(2) or A(h,beta).  Covering of F_2^26 is left to
verify_radius2_matrix.c.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MODULUS = 0x13  # x^4 + x + 1
STAR = None
R0 = 18
M = 4
SIZE = 1 << M
EXPECTED_N0 = 815
EXPECTED_R = 26
EXPECTED_N = 13070


def read_matrix(path: Path) -> tuple[int, int, list[int]]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    assert rows, "%s: no matrix rows" % path
    length = len(rows[0])
    assert all(len(row) == length for row in rows)
    assert all(bit in ("0", "1") for row in rows for bit in row)
    columns = [0] * length
    for row_index, row in enumerate(rows):
        for column_index, bit in enumerate(row):
            if bit == "1":
                columns[column_index] |= 1 << row_index
    return len(rows), length, columns


def read_labels(path: Path, length: int) -> list[int]:
    labels: list[int] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0]
            labels.extend(int(token) for token in line.split())
    assert len(labels) == length
    assert sorted(set(labels)) == list(range(max(labels) + 1))
    return labels


def binary_rank(columns: list[int]) -> int:
    basis: dict[int, int] = {}
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def polynomial_degree(value: int) -> int:
    return value.bit_length() - 1


def polynomial_remainder(dividend: int, divisor: int) -> int:
    degree = polynomial_degree(divisor)
    while polynomial_degree(dividend) >= degree:
        dividend ^= divisor << (polynomial_degree(dividend) - degree)
    return dividend


def verify_irreducible(modulus: int, degree: int) -> None:
    assert polynomial_degree(modulus) == degree
    for factor_degree in range(1, degree // 2 + 1):
        for factor in range((1 << factor_degree) | 1, 1 << (factor_degree + 1), 2):
            if polynomial_degree(factor) == factor_degree:
                assert polynomial_remainder(modulus, factor) != 0


def gf_multiply(left: int, right: int) -> int:
    product = 0
    while right:
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
    while polynomial_degree(product) >= M:
        product ^= MODULUS << (polynomial_degree(product) - M)
    return product


def verify_field() -> None:
    verify_irreducible(MODULUS, M)
    for value in range(SIZE):
        assert gf_multiply(value, 0) == 0
        assert gf_multiply(value, 1) == value
    for left in range(1, SIZE):
        inverses = sum(
            gf_multiply(left, right) == 1 for right in range(1, SIZE)
        )
        assert inverses == 1


def verify_seed_partition(
    columns: list[int], labels: list[int], redundancy: int
) -> int:
    space = 1 << redundancy
    covered = bytearray(space)
    covered[0] = 1
    for column in columns:
        covered[column] = 1
    for left, column in enumerate(columns):
        for right in range(left):
            if labels[left] != labels[right]:
                covered[column ^ columns[right]] = 1
    count = sum(covered)
    assert count == space
    return count


def check_equal(
    actual: list[int], index: int, expected: int, description: str
) -> int:
    assert index < len(actual), "matrix ended before %s" % description
    assert actual[index] == expected, (
        "column %d fails %s: got %d, expected %d" %
        (index, description, actual[index], expected)
    )
    return index + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--seed-partition", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    args = parser.parse_args()

    verify_field()
    seed_r, seed_n, seed_columns = read_matrix(args.seed)
    assert (seed_r, seed_n) == (R0, EXPECTED_N0)
    assert binary_rank(seed_columns) == R0
    assert len(set(seed_columns)) == seed_n and all(seed_columns)
    labels = read_labels(args.seed_partition, seed_n)
    blocks = len(set(labels))
    assert blocks == SIZE + 1
    covered = verify_seed_partition(seed_columns, labels, seed_r)
    assert SIZE + 1 >= blocks

    indicators: list[int | None] = [STAR]
    indicators.extend(range(SIZE))
    column_indicators = [indicators[label] for label in labels]
    assert len(set(column_indicators)) == blocks

    output_r, output_n, output = read_matrix(args.matrix)
    assert (output_r, output_n) == (EXPECTED_R, EXPECTED_N)
    assert output_n == SIZE * (seed_n + 2) - 2
    assert binary_rank(output) == output_r
    assert len(set(output)) == output_n
    assert all(0 < column < (1 << output_r) for column in output)

    shift_xi = R0
    shift_beta_xi = R0 + M
    index = 0
    for value in range(1, SIZE):
        index = check_equal(
            output, index, value << shift_xi, "D_2(2) first Hamming")
    for value in range(1, SIZE):
        index = check_equal(
            output, index, value << shift_beta_xi, "D_2(2) second Hamming")
    for column, indicator in zip(seed_columns, column_indicators):
        for xi in range(SIZE):
            if indicator is STAR:
                expected = column | (xi << shift_beta_xi)
            else:
                expected = (
                    column
                    | (xi << shift_xi)
                    | (gf_multiply(indicator, xi) << shift_beta_xi)
                )
            index = check_equal(output, index, expected, "A(h,beta)")
    assert index == len(output)

    print(
        "PASS theorem=4.1 QM_2^1 m=%d seed=%s seed_blocks=%d "
        "seed_cross_block=%d/%d field_modulus=0x%X matrix=%s "
        "r=%d n=%d rank=%d distinct_nonzero=%d identity_columns=%d "
        "published=13565 previous_certified=13309 improvement=%d "
        "coverage=VERIFY_RADIUS2_MATRIX" %
        (
            M,
            args.seed,
            blocks,
            covered,
            1 << seed_r,
            MODULUS,
            args.matrix,
            output_r,
            output_n,
            output_r,
            output_n,
            output_n,
            13565 - output_n,
        )
    )


if __name__ == "__main__":
    main()
