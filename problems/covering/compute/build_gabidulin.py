#!/usr/bin/env python3
"""Build the Gabidulin–Davydov–Tombak odd-r covering (GUAVA GabidulinCode).

Reimplements Theorem 1 of Gabidulin–Davydov–Tombak, IEEE TIT 37 (1991),
as transcribed in GUAVA lib/codecstr.gi.  For m >= 4 this is an
[5*2^{m-2}-1, 5*2^{m-2}-2m, 3]_2 code of covering radius 2 and
redundancy r = 2m-1.  That is the paper's f(r) family:

    r=11 (m=6) -> n=79
    r=13 (m=7) -> n=159

Integer columns are LSB-first.  This is a seed factory; the C/Python
verifiers are the certificate.
"""

from __future__ import annotations

import argparse
from pathlib import Path


# Conway polynomials used by GAP for these degrees.
CONWAY = {
    2: 0x7,    # x^2 + x + 1
    3: 0xB,    # x^3 + x + 1
    4: 0x13,   # x^4 + x + 1
    5: 0x25,   # x^5 + x^2 + 1
}


def gf_mul(left: int, right: int, degree: int) -> int:
    modulus = CONWAY[degree]
    top = 1 << degree
    product = 0
    while right:
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
        if left & top:
            left ^= modulus
    return product


def gf_pow(base: int, exponent: int, degree: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = gf_mul(result, base, degree)
        base = gf_mul(base, base, degree)
        exponent >>= 1
    return result


def primitive_root(degree: int) -> int:
    """GAP PrimitiveRoot(GF(2^d)) is the Conway root x."""
    return 2 if degree > 1 else 1


def field_tables(degree: int) -> tuple[list[int], dict[int, int], list[int]]:
    """Return (sorted field elements, dlog, inverses) matching GUAVA."""
    size = 1 << degree
    alpha = primitive_root(degree)
    elements = [0]
    dlog = {0: None}
    for k in range(size - 1):
        value = gf_pow(alpha, k, degree)
        elements.append(value)
        dlog[value] = k
    inverses = [0] * size
    for value in range(1, size):
        inverses[value] = gf_pow(value, size - 2, degree)
    return elements, dlog, inverses


def binary_representation(element: int, degree: int, dlog: dict[int, int]) -> list[int]:
    """F_2-coordinates of a field element in the Conway polynomial basis.

    GUAVA's log-plus-one BinaryRepresentation coincides with this basis on
    GF(4) (m=4) but not on GF(8) or GF(16).  The polynomial basis is the one
    that actually yields a radius-2 covering for m=5,6,7.
    """
    del dlog
    return [(element >> index) & 1 for index in range(degree)]


def gabidulin_columns(m: int, w1: int, w2: int) -> list[int]:
    if m < 4:
        raise ValueError("GabidulinCode requires m >= 4")
    degree = m - 2
    size = 1 << degree
    redundancy = 2 * m - 1
    elements, dlog, inverses = field_tables(degree)
    if not (0 < w1 < size and 0 < w2 < size):
        raise ValueError("w1 and w2 must be nonzero field elements")
    w3 = w1 ^ w2
    binels = [binary_representation(value, degree, dlog) for value in elements]
    n = 5 * size - 1
    columns = [0] * n

    def set_bit(column: int, row: int) -> None:
        columns[column] |= 1 << row

    # Matrix N: nonzero field elements in bits 1..degree.
    for i in range(size - 1):
        bits = binels[i + 1]
        for j, bit in enumerate(bits):
            if bit:
                set_bit(i, j + 1)

    def write_block(start: int, extra_rows: list[int], scale: int) -> None:
        for i in range(size):
            column = start + i
            set_bit(column, 0)
            for row in extra_rows:
                set_bit(column, row)
            for j, bit in enumerate(binels[i]):
                if bit:
                    set_bit(column, j + 1)
            quotient = 0 if i == 0 else gf_mul(scale, inverses[elements[i]], degree)
            qbits = binary_representation(quotient, degree, dlog)
            for j, bit in enumerate(qbits):
                if bit:
                    set_bit(column, j + (m - 1))

    # D, Q, M
    write_block(size - 1, [], w1)
    write_block(2 * size - 1, [redundancy - 1], w2)
    write_block(3 * size - 1, [redundancy - 2], w3)

    # Matrix G
    for i in range(size):
        column = 4 * size - 1 + i
        set_bit(column, 0)
        set_bit(column, redundancy - 2)
        set_bit(column, redundancy - 1)
        for j, bit in enumerate(binels[i]):
            if bit:
                set_bit(column, (m - 1) + j)

    if any(column == 0 for column in columns):
        raise RuntimeError("Gabidulin construction produced a zero column")
    if len(set(columns)) != n:
        raise RuntimeError("Gabidulin construction produced a repeated column")
    return columns


def covered_count(columns: list[int], redundancy: int) -> int:
    space = 1 << redundancy
    seen = bytearray(space)
    seen[0] = 1
    for left, a in enumerate(columns):
        seen[a] = 1
        for b in columns[:left]:
            seen[a ^ b] = 1
    return sum(seen)


def write_columns(path: Path, columns: list[int]) -> None:
    path.write_text(" ".join(str(value) for value in columns) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, default=6)
    parser.add_argument("--w1", type=int, default=1)
    parser.add_argument("--w2", type=int, default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    columns = gabidulin_columns(args.m, args.w1, args.w2)
    redundancy = 2 * args.m - 1
    covered = covered_count(columns, redundancy)
    space = 1 << redundancy
    print(
        f"Gabidulin m={args.m} r={redundancy} n={len(columns)} "
        f"w1={args.w1} w2={args.w2} covered={covered}/{space}"
    )
    if args.output is not None:
        write_columns(args.output, columns)
        print(f"wrote {args.output}")
    if covered != space:
        raise SystemExit("Gabidulin seed failed the pair-XOR cover")


if __name__ == "__main__":
    main()
