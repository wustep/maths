#!/usr/bin/env python3
"""Build the QM_5^2 r=28 descendant and its explicit partitions.

The chain follows arXiv:2511.02542, Theorem 5.4, with the certified 50-column
seed substituted for the paper's 51-column KR seed:

1. Refine the seed's verified 10-block (2,0)-partition to 16 blocks, making
   the three columns of its cross-block dependent triple singleton blocks.
2. Apply QM_2^2 with m=4 and B=GF(16), obtaining r=18, n=815 together with
   the explicit 33-block partition described in the proof of Theorem 5.4(i).
3. Apply QM_5^2 with m=5, B=GF(32) union {star}, assigning star to one of the
   singleton triple columns.  This gives r=28, n=26111 and an explicit
   66-block partition as in Theorem 5.4(ii).

The separate C verifier checks the emitted matrix texts and cross-block pair
coverage.  This builder does not certify its own output.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from build_qm3 import (
    MODULUS,
    binary_rank,
    gf_mul,
    gf_selftest,
    has_dependent_triple,
    read_matrix,
    verify_seed_partition,
    write_matrix,
)


def cross_block_triples(
    columns: list[int], block_of_column: list[int]
) -> list[tuple[int, int, int]]:
    location = {column: index for index, column in enumerate(columns)}
    triples: set[tuple[int, int, int]] = set()
    for left in range(len(columns)):
        for right in range(left):
            third = location.get(columns[left] ^ columns[right])
            if third is None or third in (left, right):
                continue
            triple = tuple(sorted((left, right, third)))
            if len({block_of_column[index] for index in triple}) == 3:
                triples.add(triple)
    return sorted(triples)


def refine_to_sixteen_blocks(
    block_of_column: list[int], triple: tuple[int, int, int]
) -> tuple[list[int], list[list[int]]]:
    """Refine blocks only, so validity of the old partition is preserved."""
    triple_set = set(triple)
    groups: list[list[int]] = []
    for old_block in sorted(set(block_of_column)):
        members = [
            index for index, label in enumerate(block_of_column)
            if label == old_block
        ]
        special = [index for index in members if index in triple_set]
        ordinary = [index for index in members if index not in triple_set]
        assert len(special) <= 1, "triple was not cross-block"
        if special:
            groups.append(special)
        if ordinary:
            groups.append(ordinary)

    # Isolating the three triple columns takes 10 blocks to 13.  Peel three
    # further deterministic singletons to reach all 16 field indicators.
    while len(groups) < 16:
        position = next(
            index for index, group in enumerate(groups)
            if len(group) > 1 and not (set(group) & triple_set)
        )
        group = groups[position]
        groups[position:position + 1] = [[group[0]], group[1:]]
    assert len(groups) == 16
    assert sorted(index for group in groups for index in group) == list(
        range(len(block_of_column)))
    assert all(
        any(group == [index] for group in groups) for index in triple)

    labels = [-1] * len(block_of_column)
    for block, group in enumerate(groups):
        for index in group:
            labels[index] = block
    assert all(label >= 0 for label in labels)
    return labels, groups


def build_refined_qm2(
    columns0: list[int], refined_blocks: list[int]
) -> tuple[list[int], list[int]]:
    """QM_2^2 at m=4 plus the proof's explicit 33-block partition."""
    m = 4
    size = 1 << m
    r0 = 10
    gf_selftest(m)
    assert sorted(set(refined_blocks)) == list(range(size))
    shift_first = r0
    shift_second = r0 + m
    columns: list[int] = []
    partition: list[int] = []

    # D_1(2), one final partition block.
    for value in range(1, size):
        columns.append(value << shift_second)
        partition.append(2 * size)

    # One field indicator per refined seed block.  Split each interim A block
    # into xi=0 and xi!=0, exactly as in Theorem 5.4(i).
    for column, block in zip(columns0, refined_blocks):
        beta = block
        for xi in range(size):
            columns.append(
                column
                | (xi << shift_first)
                | (gf_mul(beta, xi, m) << shift_second)
            )
            partition.append(2 * block + (xi != 0))

    assert len(columns) == size * (len(columns0) + 1) - 1 == 815
    assert len(set(columns)) == len(columns)
    assert binary_rank(columns) == 18
    assert sorted(set(partition)) == list(range(33))
    return columns, partition


def build_qm5(
    columns0: list[int], partition0: list[int], star_block: int
) -> tuple[list[int], list[int], dict[int, int | None]]:
    """Theorem 5.4(ii): QM_5^2 with one star block and all GF(32)."""
    m = 5
    size = 1 << m
    r0 = 18
    gf_selftest(m)
    blocks = sorted(set(partition0))
    assert blocks == list(range(33))
    assert star_block in blocks
    finite_blocks = [block for block in blocks if block != star_block]
    assert len(finite_blocks) == size
    indicator = {star_block: None}
    indicator.update({block: value for value, block in enumerate(finite_blocks)})
    assert set(value for value in indicator.values() if value is not None) == set(
        range(size))

    shift_first = r0
    shift_second = r0 + m
    columns: list[int] = []
    partition: list[int] = []

    # D_1(2), the 66th output block.
    for value in range(1, size):
        columns.append(value << shift_second)
        partition.append(65)

    finite_position = {block: index for index, block in enumerate(finite_blocks)}
    for column, block in zip(columns0, partition0):
        beta = indicator[block]
        for xi in range(size):
            if beta is None:
                lifted = column | (xi << shift_second)
                output_block = 64
            else:
                lifted = (
                    column
                    | (xi << shift_first)
                    | (gf_mul(beta, xi, m) << shift_second)
                )
                output_block = 2 * finite_position[block] + (xi != 0)
            columns.append(lifted)
            partition.append(output_block)

    assert len(columns) == size * len(columns0) + size - 1 == 26111
    assert len(set(columns)) == len(columns)
    assert binary_rank(columns) == 28
    assert sorted(set(partition)) == list(range(66))
    return columns, partition, indicator


def write_partition(path: Path, labels: list[int], description: list[str]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for line in description:
            handle.write("# %s\n" % line if line else "#\n")
        handle.write(" ".join(str(label) for label in labels) + "\n")


def density(n: int, r: int) -> Fraction:
    return Fraction(1 + n + n * (n - 1) // 2, 1 << r)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--partition", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    r0, n0, columns0 = read_matrix(args.seed)
    assert (r0, n0) == (10, 50)
    assert len(set(columns0)) == n0 and all(columns0)
    assert binary_rank(columns0) == r0
    assert has_dependent_triple(columns0)
    with args.partition.open("r", encoding="utf-8") as handle:
        blob = json.load(handle)
    assert blob["columns"] == columns0
    partition0 = list(blob["block_of_column"])
    verify_seed_partition(columns0, partition0, r0)

    triples = cross_block_triples(columns0, partition0)
    assert len(triples) == 1, (
        "expected one cross-block dependent triple, got %d" % len(triples))
    triple = triples[0]
    triple_values = [columns0[index] for index in triple]
    assert triple_values[0] ^ triple_values[1] ^ triple_values[2] == 0

    refined, refined_groups = refine_to_sixteen_blocks(partition0, triple)
    verify_seed_partition(columns0, refined, r0)
    columns18, partition18 = build_refined_qm2(columns0, refined)
    verify_seed_partition(columns18, partition18, 18)

    # The xi=0 lift of each singleton seed-triple block is itself a singleton
    # partition block, retaining the dependent triple required by QM_5^2.
    d_columns = (1 << 4) - 1
    lifted_triple = [d_columns + index * (1 << 4) for index in triple]
    assert [columns18[index] for index in lifted_triple] == triple_values
    assert columns18[lifted_triple[0]] ^ columns18[lifted_triple[1]] ^ \
        columns18[lifted_triple[2]] == 0
    for index in lifted_triple:
        assert partition18.count(partition18[index]) == 1
    star_block = partition18[lifted_triple[0]]

    columns28, partition28, indicators = build_qm5(
        columns18, partition18, star_block)

    matrix18 = args.outdir / "H_r18_n815_qm5_seed.txt"
    labels18 = args.outdir / "partition_r18_n815_qm5.txt"
    matrix28 = args.outdir / "H_r28_n26111.txt"
    labels28 = args.outdir / "partition_r28_n26111.txt"
    write_matrix(
        matrix18,
        18,
        columns18,
        [
            "QM_2^2 m=4 lift of H_r10_n50 using a refined 16-block",
            "seed partition with the cross-block dependent triple isolated.",
            "This is the starting matrix for QM_5^2; n=16*51-1=815.",
            "LSB-first; generated by compute/build_qm5.py.",
        ],
    )
    write_partition(
        labels18,
        partition18,
        [
            "Block label for each column of H_r18_n815_qm5_seed.txt.",
            "33 blocks: each of 16 A-blocks split by xi=0/nonzero, plus D.",
        ],
    )
    write_matrix(
        matrix28,
        28,
        columns28,
        [
            "Construction QM_5^2 (arXiv:2511.02542 Theorem 5.4(ii))",
            "applied with m=5 to H_r18_n815_qm5_seed.txt.",
            "B=GF(32) union {star}; D=D_1(2); GF(32) modulus 0x25.",
            "r=18+2*5=28; n=32*815+31=26111.",
            "LSB-first; generated by compute/build_qm5.py.",
        ],
    )
    write_partition(
        labels28,
        partition28,
        [
            "Block label for each column of H_r28_n26111.txt.",
            "66 blocks: 32 finite-indicator A-blocks split by xi=0/nonzero,",
            "one unsplit star A-block, and one D block.",
        ],
    )

    published28 = 26623
    records = []
    for r, columns, matrix, labels, blocks, published in (
        (18, columns18, matrix18, labels18, 33, 831),
        (28, columns28, matrix28, labels28, 66, published28),
    ):
        mu = density(len(columns), r)
        records.append({
            "redundancy": r,
            "length": len(columns),
            "rank": binary_rank(columns),
            "matrix": str(matrix),
            "partition": str(labels),
            "partition_blocks": blocks,
            "published_length_arxiv_2511_02542": published,
            "improvement": published - len(columns),
            "density_numerator": mu.numerator,
            "density_denominator": mu.denominator,
            "warning": "certify matrix and partition with verify_radius2_matrix",
        })

    continuations = []
    for m in (7, 8):
        assert len(columns28) >= (1 << m) >= 66
        r = 28 + 2 * m
        n = (1 << m) * (len(columns28) + 1) - 1
        expected = 51 * (1 << (r // 2 - 5)) - 1
        assert n == expected
        published = 52 * (1 << (r // 2 - 5)) - 1
        continuations.append({
            "construction": "QM_2^2",
            "from_redundancy": 28,
            "m": m,
            "redundancy": r,
            "length": n,
            "published_length_arxiv_2511_02542": published,
            "improvement": published - n,
            "hypothesis": "%d >= 2^%d >= 66" % (len(columns28), m),
        })

    manifest = {
        "format": "covering-qm5-build-manifest-v1",
        "seed": str(args.seed),
        "seed_partition": str(args.partition),
        "cross_block_triple_decimal": triple_values,
        "refined_seed_block_sizes": [len(group) for group in refined_groups],
        "r18_star_block": star_block,
        "qm5_distinct_indicators": len(set(indicators.values())),
        "records": records,
        "qm2_continuations": continuations,
        "warning": "Matrix-only exhaustive verification is separate.",
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built %s and 33-block partition; built %s and 66-block partition" %
        (matrix18, matrix28)
    )
    print(
        "r=28 n=26111 improves 26623 by 512; certified partition would "
        "enable r=42,44 QM_2^2 continuations"
    )


if __name__ == "__main__":
    main()
