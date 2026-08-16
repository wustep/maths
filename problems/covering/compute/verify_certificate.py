#!/usr/bin/env python3
"""Dependency-free, independent verification of the q1 radius-two witness."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def fail(message: str) -> None:
    raise AssertionError(message)


def binary_rank(vectors: list[int], width: int) -> int:
    """Rank over GF(2), implemented independently of the search code."""
    basis = [0] * width
    rank = 0
    for original in vectors:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def read_matrix(path: Path) -> list[list[int]]:
    rows: list[list[int]] = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            row = [int(entry) for entry in line.split()]
            if any(entry not in (0, 1) for entry in row):
                fail("H contains an entry outside GF(2)")
            rows.append(row)
    return rows


def main() -> None:
    witness_bytes = (HERE / "witness_r10_n50.json").read_bytes()
    witness = json.loads(witness_bytes)
    certificate_bytes = (HERE / "covering_certificate_r10_n50.json").read_bytes()
    certificate = json.loads(certificate_bytes)
    rows = read_matrix(HERE / "H_r10_n50.txt")

    redundancy = int(witness["redundancy"])
    length = int(witness["length"])
    columns = [int(value) for value in witness["columns_decimal"]]
    if redundancy != 10 or length != 50 or len(columns) != length:
        fail("unexpected witness parameters")
    if len(set(columns)) != length:
        fail("H has repeated columns")
    if any(column <= 0 or column >= (1 << redundancy) for column in columns):
        fail("H has a zero or out-of-range column")

    if len(rows) != redundancy or any(len(row) != length for row in rows):
        fail("text matrix does not have shape 10 x 50")
    matrix_columns = [
        sum(rows[row][column] << row for row in range(redundancy))
        for column in range(length)
    ]
    if matrix_columns != columns:
        fail("text matrix and JSON column encodings disagree")

    rank = binary_rank(columns, redundancy)
    if rank != redundancy:
        fail(f"H has rank {rank}, not {redundancy}")

    representations = certificate.get("representations")
    if not isinstance(representations, list) or len(representations) != (1 << redundancy):
        fail("certificate does not contain exactly 2^r representations")
    if certificate.get("redundancy") != redundancy or certificate.get("length") != length:
        fail("certificate metadata disagrees with witness metadata")

    represented = set()
    certificate_weights = Counter()
    for syndrome, indices in enumerate(representations):
        if not isinstance(indices, list) or len(indices) > 2:
            fail(f"syndrome {syndrome} has a malformed representation")
        if syndrome == 0 and indices != []:
            fail("the zero syndrome must use the empty representation")
        if syndrome != 0 and not indices:
            fail(f"nonzero syndrome {syndrome} has an empty representation")
        if len(indices) == 2 and indices[0] == indices[1]:
            fail(f"syndrome {syndrome} repeats a column index")
        value = 0
        for index in indices:
            if not isinstance(index, int) or not 1 <= index <= length:
                fail(f"syndrome {syndrome} uses an invalid column index")
            value ^= columns[index - 1]
        if value != syndrome:
            fail(f"certificate entry {syndrome} evaluates to {value}")
        represented.add(value)
        certificate_weights[len(indices)] += 1
    if represented != set(range(1 << redundancy)):
        fail("certificate does not represent every syndrome")

    # A second exhaustive route ignores the supplied representations entirely.
    multiplicity = [0] * (1 << redundancy)
    multiplicity[0] += 1
    for column in columns:
        multiplicity[column] += 1
    for left in range(length):
        for right in range(left + 1, length):
            multiplicity[columns[left] ^ columns[right]] += 1
    missing = [syndrome for syndrome, count in enumerate(multiplicity) if count == 0]
    if missing:
        fail(f"independent enumeration leaves {len(missing)} syndromes uncovered")
    if max(len(indices) for indices in representations) != 2:
        fail("certificate establishes radius at most one, not exactly two")

    density = Fraction(1 + length + length * (length - 1) // 2, 1 << redundancy)
    if density != Fraction(319, 256):
        fail(f"unexpected density {density}")
    histogram = dict(sorted(Counter(multiplicity).items()))
    digest = hashlib.sha256(witness_bytes + certificate_bytes).hexdigest()

    print("PASS: independent exhaustive radius-two verification")
    print(f"code parameters: [{length},{length - rank}]_2, rank(H)={rank}, |C|=2^{length-rank}")
    print(f"syndromes covered: {len(multiplicity)}/{1 << redundancy}; radius exactly 2")
    print(f"certificate weights: {dict(sorted(certificate_weights.items()))}")
    print(f"representation multiplicities: {histogram}")
    print(f"covering density: {density} = {float(density):.8f}")
    print(f"witness+certificate sha256: {digest}")


if __name__ == "__main__":
    main()
