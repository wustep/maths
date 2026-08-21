#!/usr/bin/env python3
"""Structured r=11 seeds from the certified r=10, n=50 covering.

Identify F_2^11 = F_2^10 x F_2.  Place the 50-set in the last-bit-0 slice,
the extra column (0,1), and a hitting set T in the last-bit-1 slice so that
every pair-only 10-bit syndrome is in T or in S+T.  That is a constructive
radius-2 covering of F_2^11 of length 51+|T|.  A later compiled search can
shorten it.

This is a seed factory, not a certificate.
"""

from __future__ import annotations

import argparse
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_matrix(path: Path) -> list[int]:
    rows: list[list[str]] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    columns = [0] * len(rows[0])
    for row_index, row in enumerate(rows):
        for column_index, bit in enumerate(row):
            columns[column_index] |= (bit == "1") << row_index
    return columns


def covered(columns: list[int], redundancy: int) -> set[int]:
    seen = {0, *columns}
    for left in range(len(columns)):
        for right in range(left):
            seen.add(columns[left] ^ columns[right])
    return seen


def greedy_hitting_set(seed: list[int]) -> list[int]:
    seed_set = set(seed)
    pair_only = [value for value in range(1024) if value not in seed_set and value != 0]
    remaining = set(pair_only)
    chosen: list[int] = []
    # t may be any 10-bit word, including seed columns; 0 is reserved for (0,1).
    candidates = list(range(1, 1024))
    while remaining:
        best_t = None
        best_hit = -1
        for t in candidates:
            hit = 0
            if t in remaining:
                hit += 1
            hit += sum(1 for s in seed if (s ^ t) in remaining)
            if hit > best_hit:
                best_hit = hit
                best_t = t
        assert best_t is not None and best_hit > 0
        chosen.append(best_t)
        remaining.discard(best_t)
        for s in seed:
            remaining.discard(s ^ best_t)
        candidates.remove(best_t)
    return chosen


def lift_columns(seed: list[int], top: list[int]) -> list[int]:
    columns = [value for value in seed]  # last bit 0
    columns.append(1 << 10)  # (0, 1)
    columns.extend(value | (1 << 10) for value in top)
    return columns


def write_columns(path: Path, columns: list[int]) -> None:
    path.write_text(" ".join(str(value) for value in columns) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=HERE / "H_r10_n50.txt")
    parser.add_argument("--output", type=Path, default=HERE / "odd_r11_twolevel.cols")
    args = parser.parse_args()

    seed = read_matrix(args.seed)
    assert len(seed) == 50
    assert len(covered(seed, 10)) == 1024
    top = greedy_hitting_set(seed)
    columns = lift_columns(seed, top)
    space = covered(columns, 11)
    print(f"seed=50 hitting_set={len(top)} lifted_n={len(columns)} covered={len(space)}/2048")
    print("T=" + " ".join(str(value) for value in top))
    write_columns(args.output, columns)
    if len(space) != 2048:
        raise SystemExit("two-level lift failed to cover F_2^11")
    if len(columns) >= 79:
        print("NOTE: lifted length does not beat the paper 79; still a seed")
    else:
        print(f"SEED BEATS PAPER: n={len(columns)} < 79")


if __name__ == "__main__":
    main()
