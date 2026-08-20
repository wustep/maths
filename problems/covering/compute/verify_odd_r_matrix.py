#!/usr/bin/env python3
"""Independent Python check of a radius-2 matrix (no shared code with the C searcher)."""

from __future__ import annotations

import argparse
from pathlib import Path


def read_matrix(path: Path) -> list[int]:
    rows: list[list[str]] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    if not rows:
        raise SystemExit(f"{path}: empty matrix")
    n = len(rows[0])
    if any(len(row) != n for row in rows):
        raise SystemExit(f"{path}: ragged matrix")
    columns = [0] * n
    for row_index, row in enumerate(rows):
        for column_index, bit in enumerate(row):
            if bit not in ("0", "1"):
                raise SystemExit(f"{path}: non-binary entry")
            columns[column_index] |= (bit == "1") << row_index
    return columns


def binary_rank(columns: list[int]) -> int:
    basis: dict[int, int] = {}
    rank = 0
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix")
    parser.add_argument("r", type=int)
    parser.add_argument("n", type=int)
    args = parser.parse_args()
    columns = read_matrix(Path(args.matrix))
    space = 1 << args.r
    if len(columns) != args.n:
        raise SystemExit(f"length {len(columns)} != {args.n}")
    if any(column <= 0 or column >= space for column in columns):
        raise SystemExit("zero or out-of-range column")
    if len(set(columns)) != args.n:
        raise SystemExit("repeated columns")
    rank = binary_rank(columns)
    if rank != args.r:
        raise SystemExit(f"rank {rank} != {args.r}")
    covered = {0, *columns}
    pairs = 0
    for left in range(args.n):
        for right in range(left):
            covered.add(columns[left] ^ columns[right])
            pairs += 1
    if len(covered) != space:
        raise SystemExit(f"covered {len(covered)}/{space} missing={space - len(covered)}")
    print(
        f"PASS matrix={args.matrix} r={args.r} n={args.n} rank={rank} "
        f"distinct_nonzero={args.n} pairs={pairs} covered={len(covered)}/{space}"
    )


if __name__ == "__main__":
    main()
