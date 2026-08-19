#!/usr/bin/env python3
"""Independently verify a theorem-only QM_5^3 / QM_3^5 certificate.

The r=38 and r=41 syndrome spaces are intentionally not enumerated.  This
checker instead verifies every hypothesis of arXiv:2511.02542, Theorem 7.3,
then checks every emitted matrix column against the construction identity.
It shares no imports with the builder.
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path


MODULUS = {
    5: 0x25,   # x^5 + x^2 + 1
    9: 0x211,  # x^9 + x^4 + 1
    10: 0x409,  # x^10 + x^3 + 1
}

# A parity-check matrix for the perfect binary Golay [23,12,7] code.  These
# are LSB-first column integers.  Their perfect-code property is rederived
# below rather than trusted from this label.
GOLAY_COLUMNS = (
    739,
    1478,
    367,
    734,
    1468,
    411,
    822,
    1644,
    1595,
    1685,
    1993,
    1393,
    1,
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
)

EXPECTED = {
    5: (10, 50, 26, 817),
    9: (18, 815, 38, 13102),
    10: (20, 1631, 41, 26206),
}


def read_matrix(path: Path) -> tuple[int, int, list[int]]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    assert rows, "%s: no matrix rows" % path
    length = len(rows[0])
    assert length > 0
    assert all(len(row) == length for row in rows), "%s: ragged matrix" % path
    assert all(bit in ("0", "1") for row in rows for bit in row), (
        "%s: nonbinary matrix token" % path)
    columns = [0] * length
    for row_index, row in enumerate(rows):
        for column_index, bit in enumerate(row):
            if bit == "1":
                columns[column_index] |= 1 << row_index
    return len(rows), length, columns


def binary_rank(columns: list[int] | tuple[int, ...]) -> int:
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
    divisor_degree = polynomial_degree(divisor)
    while polynomial_degree(dividend) >= divisor_degree:
        dividend ^= divisor << (polynomial_degree(dividend) - divisor_degree)
    return dividend


def verify_irreducible(modulus: int, degree: int) -> None:
    """Exhaust all possible monic odd factors through degree floor(m/2)."""
    assert polynomial_degree(modulus) == degree
    assert modulus & 1
    for factor_degree in range(1, degree // 2 + 1):
        for factor in range(
            (1 << factor_degree) | 1,
            1 << (factor_degree + 1),
            2,
        ):
            if polynomial_degree(factor) == factor_degree:
                assert polynomial_remainder(modulus, factor) != 0, (
                    "field modulus 0x%X is divisible by 0x%X" %
                    (modulus, factor)
                )


def gf_multiply(left: int, right: int, degree: int, modulus: int) -> int:
    """Carry-less multiplication, implemented independently of the builder."""
    product = 0
    while right:
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
    while polynomial_degree(product) >= degree:
        product ^= modulus << (polynomial_degree(product) - degree)
    return product


def verify_field(degree: int) -> int:
    modulus = MODULUS[degree]
    verify_irreducible(modulus, degree)
    size = 1 << degree
    for value in range(size):
        assert gf_multiply(value, 0, degree, modulus) == 0
        assert gf_multiply(value, 1, degree, modulus) == value
    # Irreducibility already proves this is a field.  Checking every inverse
    # also catches an implementation mismatch in the multiplication routine.
    inverses = [0] * size
    for left in range(1, size):
        for right in range(1, size):
            if gf_multiply(left, right, degree, modulus) == 1:
                inverses[left] += 1
        assert inverses[left] == 1, (
            "field element %d has %d inverses" % (left, inverses[left]))
    return modulus


def verify_golay_partition() -> None:
    """Certify the perfect Golay seed and its singleton (3,0)-partition."""
    columns = GOLAY_COLUMNS
    assert len(columns) == 23
    assert len(set(columns)) == 23 and all(0 < value < (1 << 11) for value in columns)
    assert binary_rank(columns) == 11

    seen = bytearray(1 << 11)
    pattern_count = 0
    for weight in range(4):
        for positions in itertools.combinations(range(23), weight):
            syndrome = 0
            for position in positions:
                syndrome ^= columns[position]
            assert not seen[syndrome], (
                "Golay weight<=3 error patterns collide at syndrome %d" % syndrome)
            seen[syndrome] = 1
            pattern_count += 1
    assert pattern_count == 1 << 11
    assert sum(seen) == 1 << 11

    # Assigning each column its own block makes every weight-at-most-three
    # representation use distinct blocks; in particular this is a (3,0)
    # partition with p=23.
    assert len(set(range(len(columns)))) == 23


def verify_radius2(columns: list[int], redundancy: int) -> int:
    """Exhaustively certify V_{2m} without relying on its provenance."""
    space = 1 << redundancy
    assert binary_rank(columns) == redundancy
    assert len(set(columns)) == len(columns)
    assert all(0 < column < space for column in columns)
    covered = bytearray(space)
    covered[0] = 1
    for left, column in enumerate(columns):
        covered[column] = 1
        for right in range(left):
            covered[column ^ columns[right]] = 1
    count = sum(covered)
    assert count == space, "V_%d covers only %d/%d syndromes" % (
        redundancy, count, space)
    return count


def check_equal(
    actual: list[int], index: int, expected: int, description: str
) -> int:
    assert index < len(actual), "matrix ended before %s" % description
    assert actual[index] == expected, (
        "column %d fails %s identity: got %d, expected %d" %
        (index, description, actual[index], expected)
    )
    return index + 1


def verify_construction_identity(
    output: list[int],
    radius2_columns: list[int],
    m: int,
    modulus: int,
) -> None:
    """Compare all columns with D_4 and A(h,beta), in documented order."""
    size = 1 << m
    shift_u1 = 11
    shift_u2 = 11 + m
    shift_u3 = 11 + 2 * m
    index = 0

    # D_4 = [(0,W_m,0,0) | (0,0,H_{2m})].
    for value in range(1, size):
        index = check_equal(
            output, index, value << shift_u1, "D_4 Hamming block")
    for column in radius2_columns:
        index = check_equal(
            output, index, column << shift_u2, "D_4 V_2m block")

    # The singleton Golay blocks use beta=1,...,23.  Check all 23*2^m
    # columns, including xi=0 in each A block.
    for beta, golay_column in enumerate(GOLAY_COLUMNS, start=1):
        beta_squared = gf_multiply(beta, beta, m, modulus)
        for xi in range(size):
            expected = (
                golay_column
                | (xi << shift_u1)
                | (gf_multiply(beta, xi, m, modulus) << shift_u2)
                | (gf_multiply(beta_squared, xi, m, modulus) << shift_u3)
            )
            index = check_equal(output, index, expected, "A(h,beta)")
    assert index == len(output), (
        "matrix has %d trailing columns after construction identity" %
        (len(output) - index))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--radius2", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--m", type=int, choices=sorted(EXPECTED), required=True)
    parser.add_argument("--published", type=int, required=True)
    args = parser.parse_args()

    expected_v_r, expected_v_n, expected_r, expected_n = EXPECTED[args.m]
    radius2_r, radius2_n, radius2_columns = read_matrix(args.radius2)
    assert (radius2_r, radius2_n) == (expected_v_r, expected_v_n), (
        "V_2m shape is %d x %d, expected %d x %d" %
        (radius2_r, radius2_n, expected_v_r, expected_v_n))
    radius2_covered = verify_radius2(radius2_columns, radius2_r)

    verify_golay_partition()
    assert 23 <= (1 << args.m) - 1
    indicators = tuple(range(1, 24))
    assert len(set(indicators)) == 23 and 0 not in indicators
    modulus = verify_field(args.m)

    output_r, output_n, output_columns = read_matrix(args.matrix)
    assert (output_r, output_n) == (expected_r, expected_n), (
        "output shape is %d x %d, expected %d x %d" %
        (output_r, output_n, expected_r, expected_n))
    assert output_n == (1 << args.m) * 24 + radius2_n - 1
    assert len(set(output_columns)) == output_n
    assert all(0 < column < (1 << output_r) for column in output_columns)
    output_rank = binary_rank(output_columns)
    assert output_rank == output_r
    verify_construction_identity(
        output_columns, radius2_columns, args.m, modulus)

    assert expected_n < args.published
    print(
        "PASS theorem=7.3 m=%d V_%d=%s V_covered=%d/%d "
        "golay_partition_blocks=23 field_modulus=0x%X "
        "matrix=%s r=%d n=%d rank=%d distinct_nonzero=%d "
        "identity_columns=%d published=%d improvement=%d "
        "coverage=THEOREM_7_3" %
        (
            args.m,
            2 * args.m,
            args.radius2,
            radius2_covered,
            1 << radius2_r,
            modulus,
            args.matrix,
            output_r,
            output_n,
            output_rank,
            len(set(output_columns)),
            output_n,
            args.published,
            args.published - output_n,
        )
    )


if __name__ == "__main__":
    main()
