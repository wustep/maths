#!/usr/bin/env python3
"""Build r=18, n=151 via QM_4^3 from a 9-block (3,0)-partition of H_OK.

arXiv:2511.02542 Theorem 6.1 / Construction QM_4^3 (6.4), (6.8):
n0 >= 2^m+1 >= p(H0, ell0). With p=9 and m=3: n=8*(18+1)-1=151, r=9+9=18.

The seed partition is (3,0), not (3,1). QM_4^3 allows any ell0.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

from build_qm3 import (
    MODULUS,
    binary_rank,
    gf_mul,
    gf_selftest,
    has_dependent_triple,
    write_matrix,
)

# x^3 + x + 1; needed for m=3 QM_4^3 (not in build_qm3's R=2 table).
MODULUS[3] = 0xB
from recover_mok import (
    OK_HEX_PREFIX,
    covering_counts,
    ok_columns,
)

M = 3
SIZE = 1 << M
STAR = None
R0 = 9
LAST_HEX = 0x1CE
P9_LABELS = [2, 5, 6, 5, 1, 7, 8, 4, 7, 5, 1, 3, 1, 0, 8, 7, 7, 0]


def is_partition_30(columns: list[int], labels: list[int], redundancy: int) -> bool:
    space = 1 << redundancy
    covered = bytearray(space)
    covered[0] = 1
    for column in columns:
        covered[column] = 1
    for left, a in enumerate(columns):
        for right in range(left):
            if labels[left] == labels[right]:
                continue
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


def allocate_indicators(labels: list[int]) -> list[int | None]:
    """One distinct indicator from F_8 union {*} per block; reuse within block."""
    blocks = sorted(set(labels))
    assert blocks == list(range(9))
    pool: list[int | None] = [STAR]
    pool.extend(range(SIZE))
    assert len(pool) == SIZE + 1 == 9
    block_indicator = {block: pool[block] for block in blocks}
    indicators = [block_indicator[label] for label in labels]
    assert len(set(indicators)) == 9
    for left in range(len(labels)):
        for right in range(left):
            if labels[left] != labels[right]:
                assert indicators[left] != indicators[right]
    return indicators


def build_qm43_p9(
    seed_columns: list[int], labels: list[int]
) -> tuple[int, list[int], list[int | None]]:
    gf_selftest(M)
    indicators = allocate_indicators(labels)
    shift_u1 = R0
    shift_u2 = R0 + M
    shift_u3 = R0 + 2 * M
    columns: list[int] = []

    for value in range(1, SIZE):
        columns.append(value << shift_u2)

    for column, indicator in zip(seed_columns, indicators):
        for xi in range(SIZE):
            if indicator is STAR:
                lifted = column | (xi << shift_u3)
            else:
                beta_xi = gf_mul(indicator, xi, M)
                beta_sq_xi = gf_mul(gf_mul(indicator, indicator, M), xi, M)
                lifted = (
                    column
                    | (xi << shift_u1)
                    | (beta_xi << shift_u2)
                    | (beta_sq_xi << shift_u3)
                )
            columns.append(lifted)

    redundancy = R0 + 3 * M
    expected = SIZE * (len(seed_columns) + 1) - 1
    assert redundancy == 18 and expected == 151
    assert len(columns) == expected
    assert all(0 < column < (1 << redundancy) for column in columns)
    assert len(set(columns)) == expected
    assert binary_rank(columns) == redundancy
    assert has_dependent_triple(columns)
    return redundancy, columns, indicators


def density(length: int, redundancy: int) -> Fraction:
    return Fraction(
        sum(math.comb(length, weight) for weight in range(4)),
        1 << redundancy,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--partition",
        type=Path,
        default=Path("compute/partition_H_OK_p9_ell0.txt"),
    )
    args = parser.parse_args()

    labels = P9_LABELS
    file_labels = [
        int(tok)
        for line in args.partition.read_text().splitlines()
        if line and not line.startswith("#")
        for tok in line.split()
    ]
    assert file_labels == labels

    seed_columns = ok_columns(LAST_HEX)
    assert len(set(seed_columns)) == 18
    le1, le2, le3 = covering_counts(seed_columns, R0)
    assert (le1, le2, le3) == (19, 163, 512)
    assert is_partition_30(seed_columns, labels, R0)

    redundancy, columns, indicators = build_qm43_p9(seed_columns, labels)
    length = len(columns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_matrix(
        args.output,
        redundancy,
        columns,
        [
            "Construction QM_4^3 (arXiv:2511.02542 Theorem 6.1 / (6.4),(6.8)),",
            "with m=3 and D=D_3.",
            "C0 is the Ostergard--Kaikkonen [18,9]_2 radius-3 code;",
            "M_OK last word recovered as 1CE (paper OCR: ICE).",
            "P_OK9 is a 9-block (3,0)-partition (not (3,1)).",
            "B = GF(8) union {*}; GF(8) modulus 0x%X." % MODULUS[M],
            "r=9+3*3=18; n=8*(18+1)-1=151.",
            "LSB-first: bit i of a column integer is row i+1.",
            "18 rows, 151 columns; generated by compute/build_qm43_p9.py.",
        ],
    )

    histogram = Counter("star" if value is STAR else "field" for value in indicators)
    mu = density(length, redundancy)
    blocks = [[] for _ in range(9)]
    for index, label in enumerate(labels):
        blocks[label].append(index + 1)
    manifest = {
        "format": "covering-qm43-p9-build-manifest-v1",
        "construction": "QM_4^3, arXiv:2511.02542 Theorem 6.1",
        "ok_hex_msb_first": [
            "0x%03X" % value for value in OK_HEX_PREFIX + (LAST_HEX,)
        ],
        "ok_partition_one_based": blocks,
        "ok_partition_labels": labels,
        "ok_partition_ell": 0,
        "ok_covered_le1": le1,
        "ok_covered_le2": le2,
        "ok_covered_le3": le3,
        "field_modulus_hex": "0x%X" % MODULUS[M],
        "indicator_kinds": dict(histogram),
        "matrix": str(args.output),
        "redundancy": redundancy,
        "length": length,
        "rank": binary_rank(columns),
        "previous_table_length_r18": 153,
        "improvement_vs_table": 2,
        "density_numerator": mu.numerator,
        "density_denominator": mu.denominator,
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built %s: r=%d n=%d vs_table=153 delta=2" %
        (args.output, redundancy, length)
    )


if __name__ == "__main__":
    main()
