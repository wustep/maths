#!/usr/bin/env python3
"""Build explicit and certified coarsened partitions of the r=18,20 lifts.

For each QM_2^2 output, the proof's interim blocks are indexed by the field
indicator beta.  Each interim block is split into xi=0 and xi!=0, and D is
the final block.  The result has 2^(m+1)+1 blocks.  Static maps coarsen those
partitions to 17 and 14 blocks.  This script reconstructs the complete lift
identity and exhausts both parent and coarsened partitions before writing them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


MODULUS = {
    4: 0x13,
    5: 0x25,
}

# Static coarsenings found by SAT from the proof-constructed partitions below.
# Entry i is the new label of constructive block i.  These maps are discovery
# data, not trusted certificates: both the Python builder and the independent C
# verifier exhaust the cross-block syndrome coverage of the emitted labels.
COARSENING = {
    4: [
        0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0,
        2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 9, 12, 11, 13, 14, 15, 16,
    ],
    5: [
        0, 1, 0, 1, 2, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0,
        1, 0, 3, 4, 5, 6, 5, 6, 7, 8, 7, 1, 8, 7, 7, 8,
        8, 7, 7, 8, 8, 7, 8, 7, 7, 8, 9, 8, 10, 11, 10, 11,
        5, 6, 11, 10, 11, 10, 10, 11, 4, 3, 10, 11, 3, 2, 12, 13,
        9,
    ],
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
    assert all(len(row) == length for row in rows), "%s: ragged matrix" % path
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
        for factor in range(
            (1 << factor_degree) | 1,
            1 << (factor_degree + 1),
            2,
        ):
            if polynomial_degree(factor) == factor_degree:
                assert polynomial_remainder(modulus, factor) != 0


def gf_multiply(left: int, right: int, m: int) -> int:
    modulus = MODULUS[m]
    top = 1 << m
    product = 0
    while right:
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
        if left & top:
            left ^= modulus
    return product


def verify_partition(
    columns: list[int], labels: list[int], redundancy: int
) -> int:
    assert len(columns) == len(labels)
    blocks = sorted(set(labels))
    assert blocks == list(range(len(blocks)))
    space = 1 << redundancy
    covered = bytearray(space)
    covered[0] = 1
    for left, column in enumerate(columns):
        covered[column] = 1
        for right in range(left):
            if labels[left] != labels[right]:
                covered[column ^ columns[right]] = 1
    count = sum(covered)
    assert count == space, "partition covers only %d/%d syndromes" % (
        count, space)
    return count


def allocate_indicators(
    block_of_column: list[int], m: int
) -> tuple[list[int], dict[int, list[int]]]:
    """Reproduce the deterministic allocation used by build_propagation.py."""
    size = 1 << m
    blocks = sorted(set(block_of_column))
    assert blocks == list(range(len(blocks)))
    members = {
        block: [
            index for index, label in enumerate(block_of_column)
            if label == block
        ]
        for block in blocks
    }
    assert len(blocks) <= size <= len(block_of_column)

    counts = [1] * len(blocks)
    remaining = size - len(blocks)
    for block in blocks:
        extra = min(len(members[block]) - 1, remaining)
        counts[block] += extra
        remaining -= extra
    assert remaining == 0

    indicator_sets: dict[int, list[int]] = {}
    next_indicator = 0
    for block, count in zip(blocks, counts):
        indicator_sets[block] = list(
            range(next_indicator, next_indicator + count))
        next_indicator += count
    assert next_indicator == size

    indicators = [-1] * len(block_of_column)
    for block in blocks:
        pool = indicator_sets[block]
        for position, index in enumerate(members[block]):
            indicators[index] = pool[position % len(pool)]
    assert set(indicators) == set(range(size))
    for left in range(len(indicators)):
        for right in range(left):
            if block_of_column[left] != block_of_column[right]:
                assert indicators[left] != indicators[right]
    return indicators, indicator_sets


def build_case(
    seed_columns: list[int],
    seed_partition: list[int],
    matrix_path: Path,
    constructive_path: Path,
    coarsened_path: Path,
    m: int,
) -> dict[str, object]:
    size = 1 << m
    expected_r = 10 + 2 * m
    expected_n = size * (len(seed_columns) + 1) - 1
    verify_irreducible(MODULUS[m], m)
    indicators, indicator_sets = allocate_indicators(seed_partition, m)

    expected_columns: list[int] = []
    labels: list[int] = []
    shift_xi = 10
    shift_beta_xi = 10 + m

    # The D_1(2) columns form their own final block.
    for value in range(1, size):
        expected_columns.append(value << shift_beta_xi)
        labels.append(2 * size)

    # The interim block indexed by beta is split according to xi=0/nonzero.
    for seed_column, beta in zip(seed_columns, indicators):
        for xi in range(size):
            expected_columns.append(
                seed_column
                | (xi << shift_xi)
                | (gf_multiply(beta, xi, m) << shift_beta_xi)
            )
            labels.append(2 * beta + int(xi != 0))

    matrix_r, matrix_n, matrix_columns = read_matrix(matrix_path)
    assert (matrix_r, matrix_n) == (expected_r, expected_n)
    assert matrix_columns == expected_columns, (
        "%s does not match the complete QM_2^2 construction identity" %
        matrix_path)
    assert binary_rank(matrix_columns) == matrix_r
    assert len(set(matrix_columns)) == matrix_n and all(matrix_columns)
    assert sorted(set(labels)) == list(range(2 * size + 1))
    cross_covered = verify_partition(matrix_columns, labels, matrix_r)

    with constructive_path.open("w", encoding="utf-8") as handle:
        handle.write(
            "# Theorem 5.4 constructive partition of %s.\n" % matrix_path)
        handle.write(
            "# %d blocks: %d beta-blocks split by xi=0/nonzero, plus D.\n" %
            (2 * size + 1, size))
        handle.write("# Generated by compute/build_lift_partitions.py.\n")
        handle.write(" ".join(str(label) for label in labels) + "\n")

    coarsening = COARSENING[m]
    assert len(coarsening) == 2 * size + 1
    coarsened_labels = [coarsening[label] for label in labels]
    coarsened_blocks = sorted(set(coarsened_labels))
    assert coarsened_blocks == list(range(len(coarsened_blocks)))
    coarsened_covered = verify_partition(
        matrix_columns, coarsened_labels, matrix_r)
    with coarsened_path.open("w", encoding="utf-8") as handle:
        handle.write(
            "# Certified coarsening of %s.\n" % constructive_path)
        handle.write(
            "# %d constructive blocks mapped to %d blocks; no minimality "
            "claim.\n" % (2 * size + 1, len(coarsened_blocks)))
        handle.write("# Generated by compute/build_lift_partitions.py.\n")
        handle.write(" ".join(str(label) for label in coarsened_labels) + "\n")

    return {
        "m": m,
        "matrix": str(matrix_path),
        "matrix_sha256": hashlib.sha256(matrix_path.read_bytes()).hexdigest(),
        "constructive_partition": str(constructive_path),
        "constructive_partition_sha256": hashlib.sha256(
            constructive_path.read_bytes()).hexdigest(),
        "constructive_partition_blocks": 2 * size + 1,
        "partition": str(coarsened_path),
        "partition_sha256": hashlib.sha256(
            coarsened_path.read_bytes()).hexdigest(),
        "redundancy": matrix_r,
        "length": matrix_n,
        "partition_blocks": len(coarsened_blocks),
        "coarsening_map": coarsening,
        "indicator_sets_by_seed_block": {
            str(block): values for block, values in indicator_sets.items()
        },
        "field_modulus_hex": "0x%X" % MODULUS[m],
        "constructive_cross_block_covered": cross_covered,
        "cross_block_covered": coarsened_covered,
        "syndrome_space": 1 << matrix_r,
        "minimality_claimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--seed-partition", type=Path, required=True)
    parser.add_argument("--matrix18", type=Path, required=True)
    parser.add_argument("--matrix20", type=Path, required=True)
    parser.add_argument("--partition18", type=Path, required=True)
    parser.add_argument("--partition20", type=Path, required=True)
    parser.add_argument("--coarsened18", type=Path, required=True)
    parser.add_argument("--coarsened20", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    seed_r, seed_n, seed_columns = read_matrix(args.seed)
    assert (seed_r, seed_n) == (10, 50)
    assert binary_rank(seed_columns) == seed_r
    with args.seed_partition.open("r", encoding="utf-8") as handle:
        seed_blob = json.load(handle)
    assert seed_blob["columns"] == seed_columns
    seed_partition = list(seed_blob["block_of_column"])
    assert len(set(seed_partition)) == 10
    assert verify_partition(seed_columns, seed_partition, seed_r) == 1 << seed_r

    records = [
        build_case(
            seed_columns,
            seed_partition,
            args.matrix18,
            args.partition18,
            args.coarsened18,
            4,
        ),
        build_case(
            seed_columns,
            seed_partition,
            args.matrix20,
            args.partition20,
            args.coarsened20,
            5,
        ),
    ]
    manifest = {
        "format": "covering-lift-partitions-v2",
        "construction": (
            "Theorem 5.4 proof: beta interim blocks, xi split, D last; "
            "then a statically recorded certified coarsening"
        ),
        "seed": str(args.seed),
        "seed_partition": str(args.seed_partition),
        "seed_partition_blocks": 10,
        "records": records,
        "warning": "No partition minimality is claimed.",
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for record in records:
        print(
            "built %(partition)s: r=%(redundancy)d n=%(length)d "
            "blocks=%(partition_blocks)d (constructive "
            "%(constructive_partition_blocks)d) cross_block_covered="
            "%(cross_block_covered)d/%(syndrome_space)d" % record
        )


if __name__ == "__main__":
    main()
