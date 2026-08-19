#!/usr/bin/env python3
"""Build the QM_3^2 descendants of the certified r=10, n=50 seed.

This implements Construction QM_3^2 from Davydov--Marcugini--Pambianco,
arXiv:2511.02542, Theorem 5.1, equations (5.1)--(5.2).  The construction is
used with m = 6, 7, 8, giving redundancies 22, 24, 26.  It is discovery and
construction code, not the exhaustive certificate: verify the emitted matrix
texts independently with verify_radius2_matrix.c.

Run from problems/covering/:

  python3 compute/build_qm3.py \
      --seed compute/H_r10_n50.txt \
      --partition result/data/partition_p10.json \
      --outdir compute \
      --manifest compute/qm3_build_manifest.json

All integer columns are LSB-first: bit i is matrix row i+1.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


MODULUS = {
    4: 0x13,   # x^4 + x + 1
    5: 0x25,   # x^5 + x^2 + 1
    6: 0x43,   # x^6 + x + 1
    7: 0x83,   # x^7 + x + 1
    8: 0x11B,  # x^8 + x^4 + x^3 + x + 1
}


def polynomial_degree(value: int) -> int:
    return value.bit_length() - 1


def polynomial_remainder(dividend: int, divisor: int) -> int:
    divisor_degree = polynomial_degree(divisor)
    while polynomial_degree(dividend) >= divisor_degree:
        dividend ^= divisor << (polynomial_degree(dividend) - divisor_degree)
    return dividend


def assert_irreducible(modulus: int, degree: int) -> None:
    """Brute-force all possible factor degrees (degree <= 8 here)."""
    assert polynomial_degree(modulus) == degree
    for factor_degree in range(1, degree // 2 + 1):
        first = (1 << factor_degree) | 1
        stop = 1 << (factor_degree + 1)
        for factor in range(first, stop, 2):
            if polynomial_degree(factor) != factor_degree:
                continue
            assert polynomial_remainder(modulus, factor) != 0, (
                "0x%X is reducible by 0x%X" % (modulus, factor))


def gf_mul(left: int, right: int, m: int) -> int:
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


def gf_selftest(m: int) -> None:
    """Check the field definition without trusting a lookup table."""
    size = 1 << m
    assert_irreducible(MODULUS[m], m)
    for value in range(size):
        assert gf_mul(value, 0, m) == 0
        assert gf_mul(value, 1, m) == value
        assert 0 <= gf_mul(value, value, m) < size
    for value in range(1, size):
        inverse_count = sum(
            gf_mul(value, candidate, m) == 1
            for candidate in range(1, size)
        )
        assert inverse_count == 1, (
            "GF(2^%d) element %d has %d inverses" %
            (m, value, inverse_count))


def read_matrix(path: Path) -> tuple[int, int, list[int]]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    assert rows, "%s: no matrix rows" % path
    n = len(rows[0])
    assert n > 0
    assert all(len(row) == n for row in rows), "%s: ragged matrix" % path
    assert all(bit in ("0", "1") for row in rows for bit in row), (
        "%s: matrix entries must be 0 or 1" % path)
    columns = [0] * n
    for row_index, row in enumerate(rows):
        for column_index, bit in enumerate(row):
            columns[column_index] |= (bit == "1") << row_index
    return len(rows), n, columns


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


def has_dependent_triple(columns: list[int]) -> bool:
    members = set(columns)
    for left in range(len(columns)):
        for right in range(left):
            if columns[left] ^ columns[right] in members:
                return True
    return False


def verify_seed_partition(
    columns: list[int], block_of_column: list[int], redundancy: int
) -> None:
    """Recheck the (2,0)-partition instead of trusting its JSON label."""
    assert len(block_of_column) == len(columns)
    labels = sorted(set(block_of_column))
    assert labels == list(range(len(labels))), "block labels must be 0..p-1"
    covered = bytearray(1 << redundancy)
    covered[0] = 1
    for column in columns:
        covered[column] = 1
    for left in range(len(columns)):
        for right in range(left):
            if block_of_column[left] != block_of_column[right]:
                covered[columns[left] ^ columns[right]] = 1
    failures = [value for value, hit in enumerate(covered) if not hit]
    assert not failures, (
        "partition is not a (2,0)-partition; first failures: %s" % failures[:10])


def allocate_qm3_indicators(
    block_of_column: list[int], m: int
) -> list[int | None]:
    """One allowed indicator per block; None denotes the paper's star."""
    blocks = sorted(set(block_of_column))
    size = 1 << m
    assert len(blocks) <= size, (
        "QM_3^2 condition violated: p(H_0)=%d > 2^m=%d" %
        (len(blocks), size))

    # Theorem 5.1 permits B subset {star} union (F_{2^m} minus {1}).
    allowed: list[int | None] = [None, 0]
    allowed.extend(value for value in range(2, size))
    chosen = allowed[:len(blocks)]
    assert len(chosen) == len(blocks)
    assert len(set(chosen)) == len(chosen)
    assert 1 not in chosen
    return [chosen[block] for block in block_of_column]


def build_qm3(
    r0: int, columns0: list[int], block_of_column: list[int], m: int
) -> tuple[int, list[int], list[int | None]]:
    """Return the r=r0+2m columns of Construction QM_3^2."""
    size = 1 << m
    gf_selftest(m)
    indicators = allocate_qm3_indicators(block_of_column, m)
    shift_first = r0
    shift_second = r0 + m
    columns: list[int] = []

    # D_6 from equation (3.8), with w=1 chosen from W_m:
    #   [ W_m\w   w      0_m   ]
    #   [   0_m   w    W_m\w   ].
    w = 1
    for value in range(1, size):
        if value != w:
            columns.append(value << shift_first)
    columns.append((w << shift_first) | (w << shift_second))
    for value in range(1, size):
        if value != w:
            columns.append(value << shift_second)

    # A(h_j,beta_j), equations (3.3)--(3.5), specialized to R=2.
    for column, indicator in zip(columns0, indicators):
        for xi in range(size):
            if indicator is None:  # beta_j = star: (h_j, 0_m, xi)
                lifted = column | (xi << shift_second)
            else:
                lifted = (
                    column
                    | (xi << shift_first)
                    | (gf_mul(indicator, xi, m) << shift_second)
                )
            columns.append(lifted)

    r = r0 + 2 * m
    expected_n = size * (len(columns0) + 2) - 3
    assert len(columns) == expected_n, (
        "QM_3^2 length mismatch: got %d, expected %d" %
        (len(columns), expected_n))
    assert len(set(columns)) == expected_n, "QM_3^2 emitted duplicate columns"
    assert all(0 < value < (1 << r) for value in columns)
    assert binary_rank(columns) == r, "QM_3^2 matrix is not full rank"
    return r, columns, indicators


def write_matrix(
    path: Path, r: int, columns: list[int], header_lines: list[str]
) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for line in header_lines:
            handle.write("# %s\n" % line if line else "#\n")
        for row in range(r):
            handle.write(" ".join(
                "1" if (column >> row) & 1 else "0"
                for column in columns
            ))
            handle.write("\n")


def density(n: int, r: int) -> Fraction:
    return Fraction(1 + n + n * (n - 1) // 2, 1 << r)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--partition", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--m", type=int, nargs="+", default=[6, 7, 8])
    args = parser.parse_args()

    assert args.m and all(value in MODULUS for value in args.m), (
        "supported m values are %s" % sorted(MODULUS))
    r0, n0, columns0 = read_matrix(args.seed)
    assert (r0, n0) == (10, 50), (
        "seed is %d x %d, expected 10 x 50" % (r0, n0))
    assert len(set(columns0)) == n0 and all(columns0)
    assert binary_rank(columns0) == r0
    # Distinct nonzero columns give d >= 3; a dependent triple gives d <= 3.
    # The exact d=3 hypothesis in Theorem 5.1 is therefore rechecked here.
    assert has_dependent_triple(columns0), "seed does not have minimum distance 3"

    with args.partition.open("r", encoding="utf-8") as handle:
        partition = json.load(handle)
    assert partition["columns"] == columns0, (
        "partition JSON columns disagree with seed matrix")
    block_of_column = list(partition["block_of_column"])
    verify_seed_partition(columns0, block_of_column, r0)
    p_h0 = len(set(block_of_column))
    assert p_h0 == 10

    args.outdir.mkdir(parents=True, exist_ok=True)
    records = []
    for m in args.m:
        r, columns, indicators = build_qm3(
            r0, columns0, block_of_column, m)
        n = len(columns)
        published_n = 53 * (1 << m) - 3
        assert n == 52 * (1 << m) - 3
        path = args.outdir / ("H_r%d_n%d.txt" % (r, n))
        write_matrix(
            path,
            r,
            columns,
            [
                "Construction QM_3^2 (arXiv:2511.02542 Theorem 5.1,",
                "equations (5.1)--(5.2)) applied to H_r10_n50 with m=%d." % m,
                "B is a %d-element subset of {star} union (GF(2^%d) minus {1});" %
                (p_h0, m),
                "columns in each of the 10 seed-partition blocks share one",
                "indicator, and distinct blocks have distinct indicators.",
                "D=D_6 from equation (3.8), with w=1.",
                "GF(2^%d) modulus 0x%X." % (m, MODULUS[m]),
                "r=10+2*%d=%d; n=2^%d*(50+2)-3=%d." % (m, r, m, n),
                "LSB-first: bit i of a column integer is row i+1.",
                "%d rows, %d columns; generated by compute/build_qm3.py." %
                (r, n),
            ],
        )
        mu = density(n, r)
        records.append({
            "m": m,
            "redundancy": r,
            "length": n,
            "matrix": str(path),
            "rank": binary_rank(columns),
            "distinct_nonzero_columns": len(set(columns)),
            "seed_partition_blocks": p_h0,
            "distinct_indicators": len(set(indicators)),
            "field_modulus_hex": "0x%X" % MODULUS[m],
            "published_length_arxiv_2511_02542": published_n,
            "improvement": published_n - n,
            "density_numerator": mu.numerator,
            "density_denominator": mu.denominator,
            "warning": "constructed only; certify with verify_radius2_matrix",
        })
        print(
            "built %s: r=%d n=%d rank=%d improvement=%d" %
            (path, r, n, r, published_n - n)
        )

    manifest = {
        "format": "covering-qm3-build-manifest-v1",
        "construction": "QM_3^2, arXiv:2511.02542 Theorem 5.1",
        "seed": str(args.seed),
        "partition": str(args.partition),
        "seed_partition_reverified": True,
        "records": records,
        "warning": "Matrix-only exhaustive verification is separate.",
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
