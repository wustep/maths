#!/usr/bin/env python3
"""Build the r=26, n=13070 radius-2 descendant via Construction QM_2^1.

This implements Davydov--Marcugini--Pambianco, arXiv:2511.02542,
Theorem 4.1 / (4.1), (4.3).  It lifts the certified r=18, n=815 matrix
through D=D_2(2), using the certified 17-block 2-partition so that
2^4+1 = p(H_18).  The output is shorter than the already-certified
QM_3^2 matrix at the same redundancy, and the theorem preserves p(H).

The builder checks inputs and construction identities only.  The
certificate is the independent C sweep of all 2^26 syndromes.

Run from problems/covering/:

  python3 compute/build_qm21.py \
      --seed result/data/H_r18_n815.txt \
      --partition compute/partition_r18_n815_p17.txt \
      --output compute/H_r26_n13070.txt \
      --labels compute/partition_r26_n13070_p19.txt \
      --manifest compute/qm21_build_manifest.json

All integer columns are LSB-first: bit i is matrix row i+1.
"""

from __future__ import annotations

import argparse
import json
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


M = 4
SIZE = 1 << M
STAR = None


def read_labels(path: Path, length: int) -> list[int]:
    labels: list[int] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0]
            labels.extend(int(token) for token in line.split())
    assert len(labels) == length, "%s: expected %d labels, got %d" % (
        path, length, len(labels))
    assert sorted(set(labels)) == list(range(max(labels) + 1))
    return labels


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
    assert count == space, "seed partition covers only %d/%d" % (count, space)
    return count


def allocate_indicators(labels: list[int]) -> list[int | None]:
    """One indicator per block, using all of F_{16} union {* }."""
    blocks = sorted(set(labels))
    assert blocks == list(range(SIZE + 1))
    pool: list[int | None] = [STAR]
    pool.extend(range(SIZE))
    assert len(pool) == len(blocks)
    chosen = {block: pool[block] for block in blocks}
    assert len(set(chosen.values())) == len(blocks)
    return [chosen[label] for label in labels]


def build_qm21(
    seed_columns: list[int], labels: list[int]
) -> tuple[int, list[int], list[int | None], list[int]]:
    """Return the QM_2^1 matrix, indicators, and a 19-block lift-partition."""
    gf_selftest(M)
    indicators = allocate_indicators(labels)
    r0 = 18
    shift_xi = r0
    shift_beta_xi = r0 + M
    columns: list[int] = []
    out_labels: list[int] = []

    # D_2(2) = [(0, W_m, 0) | (0, 0, W_m)].  Putting both Hamming blocks
    # into the star seed-block misses syndromes.  Giving each Hamming
    # copy its own block yields an explicit 19-block 2-partition, which
    # is enough for QM_2^2 at m=5 (2^5=32 >= 19).
    d1_block = SIZE + 1
    d2_block = SIZE + 2
    for value in range(1, SIZE):
        columns.append(value << shift_xi)
        out_labels.append(d1_block)
    for value in range(1, SIZE):
        columns.append(value << shift_beta_xi)
        out_labels.append(d2_block)

    for column, indicator, label in zip(seed_columns, indicators, labels):
        for xi in range(SIZE):
            if indicator is STAR:
                lifted = column | (xi << shift_beta_xi)
            else:
                lifted = (
                    column
                    | (xi << shift_xi)
                    | (gf_mul(indicator, xi, M) << shift_beta_xi)
                )
            columns.append(lifted)
            out_labels.append(label)

    redundancy = r0 + 2 * M
    expected = SIZE * (len(seed_columns) + 2) - 2
    assert redundancy == 26 and expected == 13070
    assert len(columns) == expected
    assert len(out_labels) == expected
    assert all(0 < column < (1 << redundancy) for column in columns)
    assert len(set(columns)) == expected
    assert binary_rank(columns) == redundancy
    return redundancy, columns, indicators, out_labels


def write_labels(path: Path, labels: list[int], source: str) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# QM_2^1 lift-partition of %s.\n" % source)
        handle.write(
            "# %d blocks: 17 seed blocks copied through A(h,beta), plus "
            "one block for each D_2(2) Hamming copy.\n" % len(set(labels))
        )
        handle.write(
            "# Certify with compute/verify_radius2_matrix.c.\n")
        handle.write(" ".join(str(label) for label in labels) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--partition", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    seed_r, seed_n, seed_columns = read_matrix(args.seed)
    assert (seed_r, seed_n) == (18, 815), (
        "seed is %d x %d, expected 18 x 815" % (seed_r, seed_n))
    assert binary_rank(seed_columns) == seed_r
    assert len(set(seed_columns)) == seed_n and all(seed_columns)
    assert has_dependent_triple(seed_columns)

    labels = read_labels(args.partition, seed_n)
    covered = verify_seed_partition(seed_columns, labels, seed_r)
    assert len(set(labels)) == SIZE + 1

    redundancy, columns, indicators, out_labels = build_qm21(
        seed_columns, labels)
    length = len(columns)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.labels.parent.mkdir(parents=True, exist_ok=True)
    write_matrix(
        args.output,
        redundancy,
        columns,
        [
            "Construction QM_2^1 (arXiv:2511.02542 Theorem 4.1,",
            "equations (4.1), (4.3)), with m=4 and D=D_2(2).",
            "C0 is the certified r=18, n=815 radius-2 code;",
            "its 17-block 2-partition uses all of GF(16) union {*}.",
            "GF(16) modulus 0x%X." % MODULUS[M],
            "r=18+2*4=26; n=16*(815+2)-2=13070.",
            "LSB-first: bit i of a column integer is row i+1.",
            "26 rows, 13070 columns; generated by compute/build_qm21.py.",
        ],
    )
    write_labels(args.labels, out_labels, str(args.output))

    manifest = {
        "format": "covering-qm21-build-manifest-v1",
        "construction": "QM_2^1, arXiv:2511.02542 Theorem 4.1 (4.1)/(4.3)",
        "seed": str(args.seed),
        "seed_partition": str(args.partition),
        "seed_partition_blocks": 17,
        "seed_partition_cross_block_covered": covered,
        "field_modulus_hex": "0x%X" % MODULUS[M],
        "block_indicators": [
            "star" if value is STAR else value
            for value in [STAR] + list(range(SIZE))
        ],
        "matrix": str(args.output),
        "partition": str(args.labels),
        "partition_blocks": len(set(out_labels)),
        "redundancy": redundancy,
        "length": length,
        "rank": binary_rank(columns),
        "distinct_nonzero_columns": len(set(columns)),
        "published_length_arxiv_2511_02542": 13565,
        "previous_certified_length": 13309,
        "improvement_vs_paper": 13565 - length,
        "improvement_vs_certified": 13309 - length,
        "warning": (
            "Builder checks are not the certificate; run run_qm21_checks.sh."
        ),
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built %s: r=%d n=%d rank=%d vs_paper=%d vs_certified=%d" %
        (args.output, redundancy, length, redundancy,
         13565 - length, 13309 - length)
    )


if __name__ == "__main__":
    main()
