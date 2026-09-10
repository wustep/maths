#!/usr/bin/env python3
"""OK37 [37,25]_2 R=3 seed from Ostergard--Kaikkonen DM 178 Table 2."""
from __future__ import annotations
from itertools import combinations

M_HEX = (
    0xBFF, 0x727, 0x977, 0x93B, 0x6B9, 0x51D, 0xAAE, 0x9B8, 0x85B,
    0xA2D, 0xB16, 0x9C5, 0xAE2, 0x6E2, 0x371, 0x5B8, 0x2DC, 0x16E,
    0x0B7, 0x45B, 0x62D, 0x716, 0x38B, 0x5C5, 0x7FF,
)
R = 12
N = 37


def reverse_bits(value: int, width: int = R) -> int:
    out = 0
    for i in range(width):
        if (value >> i) & 1:
            out |= 1 << (width - 1 - i)
    return out


def ok37_columns() -> list[int]:
    cols = [1 << i for i in range(R)]
    cols.extend(reverse_bits(h) for h in M_HEX)
    assert len(cols) == N and len(set(cols)) == N and 0 not in cols
    return cols


def covering_counts(columns: list[int], redundancy: int = R) -> tuple[int, int, int]:
    space = 1 << redundancy
    covered = bytearray(space)
    covered[0] = 1
    for c in columns:
        covered[c] = 1
    le1 = sum(covered)
    for a, b in combinations(columns, 2):
        covered[a ^ b] = 1
    le2 = sum(covered)
    for a, b, c in combinations(columns, 3):
        covered[a ^ b ^ c] = 1
    return le1, le2, sum(covered)


def is_partition_3ell(
    columns: list[int], labels: list[int], ell: int, redundancy: int = R
) -> bool:
    """Every vector is a sum of k in [ell,3] columns from distinct blocks."""
    assert len(columns) == len(labels) == N
    space = 1 << redundancy
    covered = bytearray(space)
    if ell == 0:
        covered[0] = 1
    if ell <= 1:
        for c in columns:
            covered[c] = 1
    for left, a in enumerate(columns):
        for right in range(left):
            if labels[left] == labels[right]:
                continue
            if ell <= 2:
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
    return sum(covered) == space


def main() -> None:
    cols = ok37_columns()
    le1, le2, le3 = covering_counts(cols)
    assert le3 == (1 << R)
    print(f"PASS OK37 n={N} r={R} le1={le1} le2={le2} le3={le3}")


if __name__ == "__main__":
    main()
