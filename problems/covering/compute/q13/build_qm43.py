#!/usr/bin/env python3
"""Build the q13 QM_4^3 descendant at r=44, n=52351.

The starting matrix is the notebook's certified r=26, n=817 QM_5^3
construction.  Theorem 7.3, equation (7.4), gives it a 34-block (3,0)
partition: 23 Golay A-blocks, 10 blocks from the embedded r=10 radius-2
matrix, and one W_5 block.  We refine that partition to all 65 indicators
of GF(64) union {star}, then apply Theorem 6.1, equations (6.4), (6.8),
with m=6.

This is the constructor, not the certificate.  verify_q13.c independently
checks the two seed partitions and every emitted construction identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
COMPUTE = HERE.parent
sys.path.insert(0, str(COMPUTE))

from build_qm3 import (  # noqa: E402
    MODULUS,
    binary_rank,
    gf_mul,
    gf_selftest,
    read_matrix,
    verify_seed_partition,
    write_matrix,
)
from build_qm35 import (  # noqa: E402
    build_qm35,
    exact_three_sum_count,
    golay_parity_check,
)


M = 6
SIZE = 1 << M
STAR = None
SEED_R = 26
SEED_N = 817
OUTPUT_R = 44
OUTPUT_N = 52351
PUBLISHED_N = 52415


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_radius2_partition(path: Path, columns: list[int]) -> list[int]:
    with path.open("r", encoding="utf-8") as handle:
        blob = json.load(handle)
    labels = list(blob["block_of_column"])
    assert list(blob["columns"]) == columns
    assert len(labels) == len(columns) == 50
    assert sorted(set(labels)) == list(range(10))
    return labels


def inherited_partition(radius2_labels: list[int]) -> list[int]:
    """The 34 blocks in the proof of QM_5^3, equation (7.4)."""
    labels: list[int] = []

    # build_qm35.py emits D_4 first.  Its W_5 part is one block, and its
    # embedded H_10 part keeps the certified ten-block radius-2 partition.
    labels.extend([33] * 31)
    labels.extend(23 + label for label in radius2_labels)

    # Each Golay seed column is a singleton starting block.  Its complete
    # 32-column A(h,beta) submatrix stays one output partition block.
    for golay_block in range(23):
        labels.extend([golay_block] * 32)

    assert len(labels) == SEED_N
    assert sorted(set(labels)) == list(range(34))
    return labels


def refine_to_all_indicators(coarse: list[int]) -> list[int]:
    """Refine 34 blocks to 65 without merging any coarse blocks.

    The first Golay A-block is split into a singleton and its remaining
    columns.  The 31-column W_5 block is split into singletons.  All other
    coarse blocks are unchanged, giving 2 + 32 + 31 = 65 blocks.
    """
    groups = [
        [index for index, label in enumerate(coarse) if label == block]
        for block in range(34)
    ]
    assert all(groups)

    refined_groups: list[list[int]] = []
    for block, members in enumerate(groups):
        if block == 0:
            assert len(members) == 32
            refined_groups.extend((members[:1], members[1:]))
        elif block == 33:
            assert len(members) == 31
            refined_groups.extend([index] for index in members)
        else:
            refined_groups.append(members)

    assert len(refined_groups) == SIZE + 1
    refined = [-1] * len(coarse)
    for label, members in enumerate(refined_groups):
        for index in members:
            assert refined[index] == -1
            refined[index] = label
    assert all(label >= 0 for label in refined)
    assert sorted(set(refined)) == list(range(SIZE + 1))

    containing_coarse: dict[int, int] = {}
    for old, new in zip(coarse, refined):
        containing_coarse.setdefault(new, old)
        assert containing_coarse[new] == old
    return refined


def write_partition(path: Path, labels: list[int], header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for line in header:
            handle.write("# %s\n" % line)
        handle.write(" ".join(str(label) for label in labels))
        handle.write("\n")


def allocate_indicators(refined: list[int]) -> list[int | None]:
    """Map block 0 to star and blocks 1..64 to field elements 0..63."""
    assert sorted(set(refined)) == list(range(SIZE + 1))
    indicators = [STAR if label == 0 else label - 1 for label in refined]
    assert set(indicators) == {STAR, *range(SIZE)}
    return indicators


def build_qm43(
    seed_columns: list[int], refined: list[int]
) -> tuple[list[int], list[int | None]]:
    gf_selftest(M)
    indicators = allocate_indicators(refined)
    shift_u1 = SEED_R
    shift_u2 = SEED_R + M
    shift_u3 = SEED_R + 2 * M
    columns: list[int] = []

    # D_3 = (0_{r0+m}, W_m, 0_m).
    for value in range(1, SIZE):
        columns.append(value << shift_u2)

    for seed_column, indicator in zip(seed_columns, indicators):
        if indicator is STAR:
            for xi in range(SIZE):
                columns.append(seed_column | (xi << shift_u3))
            continue

        indicator_squared = gf_mul(indicator, indicator, M)
        for xi in range(SIZE):
            columns.append(
                seed_column
                | (xi << shift_u1)
                | (gf_mul(indicator, xi, M) << shift_u2)
                | (gf_mul(indicator_squared, xi, M) << shift_u3)
            )

    assert len(columns) == SIZE * (SEED_N + 1) - 1 == OUTPUT_N
    assert all(0 < column < (1 << OUTPUT_R) for column in columns)
    assert len(set(columns)) == OUTPUT_N
    assert binary_rank(columns) == OUTPUT_R
    return columns, indicators


def density(length: int, redundancy: int) -> Fraction:
    return Fraction(
        sum(math.comb(length, weight) for weight in range(4)),
        1 << redundancy,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--radius2", type=Path, required=True)
    parser.add_argument("--radius2-partition", type=Path, required=True)
    parser.add_argument("--coarse-partition", type=Path, required=True)
    parser.add_argument("--refined-partition", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    radius2_r, radius2_n, radius2_columns = read_matrix(args.radius2)
    assert (radius2_r, radius2_n) == (10, 50)
    assert binary_rank(radius2_columns) == radius2_r
    assert len(set(radius2_columns)) == radius2_n and all(radius2_columns)
    radius2_labels = read_radius2_partition(
        args.radius2_partition, radius2_columns)
    verify_seed_partition(radius2_columns, radius2_labels, radius2_r)
    assert exact_three_sum_count(radius2_columns, radius2_r) == 1 << radius2_r

    seed_r, seed_n, seed_columns = read_matrix(args.seed)
    assert (seed_r, seed_n) == (SEED_R, SEED_N)
    assert binary_rank(seed_columns) == seed_r
    assert len(set(seed_columns)) == seed_n and all(seed_columns)

    # Rebuild the parent construction instead of trusting its filename or
    # column ordering.  This also fixes the exact inherited partition ranges.
    golay_columns, _ = golay_parity_check()
    rebuilt_r, rebuilt_seed, _ = build_qm35(golay_columns, radius2_columns)
    assert rebuilt_r == seed_r and rebuilt_seed == seed_columns

    coarse = inherited_partition(radius2_labels)
    refined = refine_to_all_indicators(coarse)
    write_partition(
        args.coarse_partition,
        coarse,
        [
            "q13 inherited 34-block (3,0)-partition of H_R3_r26_n817.txt.",
            "Blocks 0..22: Golay A-blocks; 23..32: embedded H_10 blocks;",
            "block 33: W_5. Theorem 7.3, equation (7.4).",
            "Labels correspond to columns 0..816; independently swept by verify_q13.c.",
        ],
    )
    write_partition(
        args.refined_partition,
        refined,
        [
            "q13 refinement of the inherited 34-block partition to 65 blocks.",
            "Refined block 0 uses star; block k=1..64 uses GF(64) element k-1.",
            "The first Golay A-block is split in two and W_5 into 31 singletons.",
            "Labels correspond to columns 0..816; independently swept by verify_q13.c.",
        ],
    )

    output_columns, indicators = build_qm43(seed_columns, refined)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_matrix(
        args.output,
        OUTPUT_R,
        output_columns,
        [
            "Construction QM_4^3 (arXiv:2511.02542 Theorem 6.1, (6.4), (6.8)),",
            "with m=6 and D=D_3, from the certified r=26, n=817 seed.",
            "The seed has an inherited 34-block (3,0)-partition, refined to 65.",
            "Indicators are GF(64) union {star}; GF(64) modulus 0x%X." % MODULUS[M],
            "r=26+3*6=44; n=64*(817+1)-1=52351.",
            "LSB-first: bit i of a column integer is row i+1.",
            "44 rows, 52351 columns; generated by compute/q13/build_qm43.py.",
        ],
    )

    mu = density(OUTPUT_N, OUTPUT_R)
    assert OUTPUT_N == SIZE * (SEED_N + 1) - 1
    assert SEED_N >= SIZE + 1 >= len(set(refined))
    assert PUBLISHED_N - OUTPUT_N == 64
    assert 1 + OUTPUT_N + math.comb(OUTPUT_N, 2) < (1 << OUTPUT_R)
    manifest = {
        "format": "covering-q13-qm43-manifest-v1",
        "claim": "ell_2(44,3) <= 52351",
        "construction": "QM_4^3, Theorem 6.1, equations (6.4), (6.8)",
        "field_degree": M,
        "field_modulus_hex": "0x%X" % MODULUS[M],
        "seed": str(args.seed),
        "seed_sha256": sha256_file(args.seed),
        "seed_redundancy": SEED_R,
        "seed_length": SEED_N,
        "coarse_partition": str(args.coarse_partition),
        "coarse_partition_sha256": sha256_file(args.coarse_partition),
        "coarse_partition_blocks": len(set(coarse)),
        "coarse_block_sizes": [coarse.count(block) for block in range(34)],
        "refined_partition": str(args.refined_partition),
        "refined_partition_sha256": sha256_file(args.refined_partition),
        "refined_partition_blocks": len(set(refined)),
        "refined_block_sizes": [
            refined.count(block) for block in range(SIZE + 1)
        ],
        "indicator_values": "star,0,...,63",
        "star_seed_columns": sum(indicator is STAR for indicator in indicators),
        "output": str(args.output),
        "output_sha256": sha256_file(args.output),
        "redundancy": OUTPUT_R,
        "length": OUTPUT_N,
        "rank": binary_rank(output_columns),
        "distinct_nonzero_columns": len(set(output_columns)),
        "published_length_arxiv_2511_02542_table_7_2": PUBLISHED_N,
        "improvement": PUBLISHED_N - OUTPUT_N,
        "density_numerator": mu.numerator,
        "density_denominator": mu.denominator,
        "certificate": "compute/q13/verify_q13.c and compute/q13/run_all.sh",
        "warning": "The builder is not the certificate; run run_all.sh.",
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built %s: seed_p=34 refined_p=65 GF(64)=0x%X "
        "r=%d n=%d rank=%d published=%d improvement=%d" %
        (
            args.output,
            MODULUS[M],
            OUTPUT_R,
            OUTPUT_N,
            OUTPUT_R,
            PUBLISHED_N,
            PUBLISHED_N - OUTPUT_N,
        )
    )


if __name__ == "__main__":
    main()
