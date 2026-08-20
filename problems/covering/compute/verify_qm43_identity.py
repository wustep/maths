#!/usr/bin/env python3
"""Independently verify the QM_4^3 seed and construction identity.

This checker shares no imports with build_qm43.py.  It reconstructs
H_OK from the recovered 1CE last word, rechecks covering radius 3 and
the Theorem 7.1 (3,1)-partition, then matches every emitted column
against D_3 or A(h,beta).  Covering of F_2^21 is left to
verify_radius3_matrix.c.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MODULUS = 0x13  # x^4 + x + 1
STAR = None
R0 = 9
M = 4
SIZE = 1 << M
LAST_HEX = 0x1CE
OK_HEX = (0x1A0, 0x174, 0x0A5, 0x173, 0x017, 0x0E8, 0x009, 0x18D, LAST_HEX)
P_OK_ONE_BASED = (
    (1, 2, 4),
    (3,),
    (5, 8),
    (6, 17),
    (7, 10),
    (11, 14),
    (12,),
    (13, 18),
    (15,),
    (9,),
    (16,),
)
EXPECTED_R = 21
EXPECTED_N = 303


def reverse_bits(value: int, width: int) -> int:
    return sum(((value >> bit) & 1) << (width - 1 - bit) for bit in range(width))


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


def ok_columns() -> list[int]:
    columns = [1 << row for row in range(R0)]
    columns.extend(reverse_bits(value, R0) for value in OK_HEX)
    assert len(columns) == 18
    assert len(set(columns)) == 18 and all(columns)
    assert binary_rank(columns) == R0
    assert columns[5] ^ columns[8] ^ columns[15] == 0
    return columns


def block_of_column() -> list[int]:
    labels = [-1] * 18
    for block, members in enumerate(P_OK_ONE_BASED):
        for one_based in members:
            labels[one_based - 1] = block
    assert all(label >= 0 for label in labels)
    return labels


def covering_counts(columns: list[int]) -> tuple[int, int, int]:
    covered = bytearray(1 << R0)
    covered[0] = 1
    for column in columns:
        covered[column] = 1
    le1 = sum(covered)
    for left, column in enumerate(columns):
        for right in range(left):
            covered[column ^ columns[right]] = 1
    le2 = sum(covered)
    for left, a in enumerate(columns):
        for middle in range(left):
            ab = a ^ columns[middle]
            for right in range(middle):
                covered[ab ^ columns[right]] = 1
    return le1, le2, sum(covered)


def is_partition_31(columns: list[int], labels: list[int]) -> bool:
    covered = bytearray(1 << R0)
    for column in columns:
        covered[column] = 1
    for left, a in enumerate(columns):
        for right in range(left):
            if labels[left] != labels[right]:
                covered[a ^ columns[right]] = 1
    for left, a in enumerate(columns):
        for middle in range(left):
            if labels[left] == labels[middle]:
                continue
            ab = a ^ columns[middle]
            used = {labels[left], labels[middle]}
            for right in range(middle):
                if labels[right] in used:
                    continue
                covered[ab ^ columns[right]] = 1
    return sum(covered) == (1 << R0)


def allocate_indicators(labels: list[int]) -> list[int | None]:
    blocks = sorted(set(labels))
    pool: list[int | None] = [STAR]
    pool.extend(range(SIZE))
    block_indicator = {block: pool[block] for block in blocks}
    used = set(block_indicator.values())
    leftover = [value for value in pool if value not in used]
    indicators: list[int | None] = [block_indicator[label] for label in labels]
    extra_slots = [
        index for index, label in enumerate(labels)
        if labels[:index].count(label) > 0
    ]
    for slot, indicator in zip(extra_slots, leftover):
        indicators[slot] = indicator
    assert len(set(indicators)) == SIZE + 1
    return indicators


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
    parser.add_argument("--matrix", type=Path, required=True)
    args = parser.parse_args()

    verify_irreducible(MODULUS, M)
    for value in range(SIZE):
        assert gf_multiply(value, 0) == 0
        assert gf_multiply(value, 1) == value

    seed = ok_columns()
    labels = block_of_column()
    le1, le2, le3 = covering_counts(seed)
    assert (le1, le2, le3) == (19, 163, 512)
    assert is_partition_31(seed, labels)
    assert len({labels[5], labels[8], labels[15]}) == 3
    assert 18 >= SIZE + 1 >= 11

    indicators = allocate_indicators(labels)
    output_r, output_n, output = read_matrix(args.matrix)
    assert (output_r, output_n) == (EXPECTED_R, EXPECTED_N)
    assert output_n == SIZE * (18 + 1) - 1
    assert binary_rank(output) == output_r
    assert len(set(output)) == output_n
    assert all(0 < column < (1 << output_r) for column in output)

    shift_u1 = R0
    shift_u2 = R0 + M
    shift_u3 = R0 + 2 * M
    index = 0
    for value in range(1, SIZE):
        index = check_equal(output, index, value << shift_u2, "D_3 Hamming")
    for column, indicator in zip(seed, indicators):
        for xi in range(SIZE):
            if indicator is STAR:
                expected = column | (xi << shift_u3)
            else:
                expected = (
                    column
                    | (xi << shift_u1)
                    | (gf_multiply(indicator, xi) << shift_u2)
                    | (gf_multiply(gf_multiply(indicator, indicator), xi)
                       << shift_u3)
                )
            index = check_equal(output, index, expected, "A(h,beta)")
    assert index == len(output)

    print(
        "PASS theorem=7.2 QM_4^3 m=%d M_OK_last=0x1CE seed_le3=%d/512 "
        "p_OK=11 field_modulus=0x%X matrix=%s r=%d n=%d rank=%d "
        "distinct_nonzero=%d identity_columns=%d published=303 "
        "pre_paper=308 improvement=5 coverage=VERIFY_RADIUS3_MATRIX" %
        (
            M,
            le3,
            MODULUS,
            args.matrix,
            output_r,
            output_n,
            output_r,
            output_n,
            output_n,
        )
    )


if __name__ == "__main__":
    main()
