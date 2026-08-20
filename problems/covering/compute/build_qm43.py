#!/usr/bin/env python3
"""Build the r=21, n=303 radius-3 descendant via Construction QM_4^3.

This implements Davydov--Marcugini--Pambianco, arXiv:2511.02542,
Theorems 6.4, 7.1, 7.2 / Construction QM_4^3 (6.4), (6.8).  The
Ostergard--Kaikkonen [18,9]_2 seed is reconstructed after independently
recovering the last M_OK word as 1CE (the paper's ICE is invalid hex).

The builder checks the seed hypotheses and construction identities.
The certificate is the independent C sweep of all 2^21 syndromes.

Run from problems/covering/:

  python3 compute/build_qm43.py \
      --output compute/H_R3_r21_n303.txt \
      --manifest compute/qm43_build_manifest.json

All integer columns are LSB-first: bit i is matrix row i+1.
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
from recover_mok import (
    OK_HEX_PREFIX,
    P_OK_ONE_BASED,
    block_of_column,
    candidate_ok,
    covering_counts,
    is_partition_31,
    ok_columns,
)


M = 4
SIZE = 1 << M
STAR = None
R0 = 9
LAST_HEX = 0x1CE


def allocate_indicators(labels: list[int]) -> list[int | None]:
    """Use every element of F_16 union {*} on the 18 seed columns."""
    blocks = sorted(set(labels))
    assert blocks == list(range(11))
    pool: list[int | None] = [STAR]
    pool.extend(range(SIZE))
    assert len(pool) == SIZE + 1

    # One distinct indicator per block; leftover field elements go to the
    # extra columns of the larger blocks.  One extra column reuses its
    # block indicator so that 18 assignments consume exactly 17 values.
    block_indicator = {block: pool[block] for block in blocks}
    used = set(block_indicator.values())
    leftover = [value for value in pool if value not in used]
    indicators: list[int | None] = [block_indicator[label] for label in labels]
    extra_slots = [
        index for index, label in enumerate(labels)
        if labels[:index].count(label) > 0
    ]
    assert len(extra_slots) == 7
    assert len(leftover) == 6
    for slot, indicator in zip(extra_slots, leftover):
        indicators[slot] = indicator
    assert len(set(indicators)) == SIZE + 1
    for left in range(len(labels)):
        for right in range(left):
            if labels[left] != labels[right]:
                assert indicators[left] != indicators[right]
    return indicators


def build_qm43(
    seed_columns: list[int], labels: list[int]
) -> tuple[int, list[int], list[int | None]]:
    gf_selftest(M)
    indicators = allocate_indicators(labels)
    shift_u1 = R0
    shift_u2 = R0 + M
    shift_u3 = R0 + 2 * M
    columns: list[int] = []

    # D_3 = (0_{r0+m}, W_m, 0_m).
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
    assert redundancy == 21 and expected == 303
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
    args = parser.parse_args()

    labels = block_of_column()
    recovered = candidate_ok(LAST_HEX, labels)
    assert recovered is not None, "1CE failed the independently checked seed test"
    seed_columns = list(recovered["columns"])
    assert seed_columns == ok_columns(LAST_HEX)
    assert is_partition_31(seed_columns, labels, R0)
    le1, le2, le3 = covering_counts(seed_columns, R0)
    assert (le1, le2, le3) == (19, 163, 512)

    redundancy, columns, indicators = build_qm43(seed_columns, labels)
    length = len(columns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_matrix(
        args.output,
        redundancy,
        columns,
        [
            "Construction QM_4^3 (arXiv:2511.02542 Theorems 6.4, 7.1, 7.2),",
            "with m=4 and D=D_3.",
            "C0 is the Ostergard--Kaikkonen [18,9]_2 radius-3 code;",
            "M_OK last word recovered as 1CE (paper OCR: ICE).",
            "P_OK is the 11-block (3,1)-partition of Theorem 7.1.",
            "B = GF(16) union {*}; GF(16) modulus 0x%X." % MODULUS[M],
            "r=9+3*4=21; n=16*(18+1)-1=303.",
            "LSB-first: bit i of a column integer is row i+1.",
            "21 rows, 303 columns; generated by compute/build_qm43.py.",
        ],
    )

    histogram = Counter("star" if value is STAR else "field" for value in indicators)
    mu = density(length, redundancy)
    manifest = {
        "format": "covering-qm43-build-manifest-v1",
        "construction": "QM_4^3, arXiv:2511.02542 Theorems 6.4, 7.1, 7.2",
        "ok_hex_msb_first": [
            "0x%03X" % value for value in OK_HEX_PREFIX + (LAST_HEX,)
        ],
        "ok_last_word_recovered": "0x1CE",
        "ok_last_word_paper_ocr": "ICE",
        "ok_columns_decimal_lsb_first": seed_columns,
        "ok_partition_one_based": [list(block) for block in P_OK_ONE_BASED],
        "ok_covered_le1": le1,
        "ok_covered_le2": le2,
        "ok_covered_le3": le3,
        "ok_dependent_triple_one_based": [6, 9, 16],
        "field_modulus_hex": "0x%X" % MODULUS[M],
        "indicator_kinds": dict(histogram),
        "matrix": str(args.output),
        "redundancy": redundancy,
        "length": length,
        "rank": binary_rank(columns),
        "distinct_nonzero_columns": len(set(columns)),
        "published_length_arxiv_2511_02542": 303,
        "previous_table_length_theorem_6_3": 308,
        "improvement_vs_pre_paper": 5,
        "density_numerator": mu.numerator,
        "density_denominator": mu.denominator,
        "warning": (
            "Builder checks are not the certificate; run run_qm43_checks.sh."
        ),
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built %s: r=%d n=%d rank=%d seed_le3=%d/512 vs_pre_paper=5" %
        (args.output, redundancy, length, redundancy, le3)
    )


if __name__ == "__main__":
    main()
