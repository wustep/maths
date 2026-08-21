#!/usr/bin/env python3
"""Build or byte-check the exhaustive certificate for the q1 witness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WITNESS_PATH = HERE / "witness_r10_n50.json"
CERTIFICATE_PATH = HERE / "covering_certificate_r10_n50.json"
MATRIX_PATH = HERE / "H_r10_n50.txt"


def load_columns() -> tuple[int, list[int]]:
    data = json.loads(WITNESS_PATH.read_text())
    return int(data["redundancy"]), [int(value) for value in data["columns_decimal"]]


def make_representations(redundancy: int, columns: list[int]) -> list[list[int]]:
    representations: list[list[int] | None] = [None] * (1 << redundancy)
    representations[0] = []

    for index, column in enumerate(columns, start=1):
        if representations[column] is None:
            representations[column] = [index]

    for left in range(len(columns)):
        for right in range(left + 1, len(columns)):
            syndrome = columns[left] ^ columns[right]
            if representations[syndrome] is None:
                representations[syndrome] = [left + 1, right + 1]

    missing = [index for index, representation in enumerate(representations) if representation is None]
    if missing:
        raise RuntimeError(f"witness leaves {len(missing)} syndromes uncovered: {missing}")
    return [representation for representation in representations if representation is not None]


def render_certificate(redundancy: int, columns: list[int]) -> str:
    payload = {
        "format": "binary-radius-two-syndrome-certificate-v1",
        "redundancy": redundancy,
        "length": len(columns),
        "column_indexing": "1-based indices into witness_r10_n50.json",
        "syndrome_indexing": "representations[s] represents integer syndrome s",
        "representations": make_representations(redundancy, columns),
    }
    return json.dumps(payload, indent=2) + "\n"


def render_matrix(redundancy: int, columns: list[int]) -> str:
    lines = [
        "# H for the binary [50,40] code found in quest q1",
        "# 10 rows, 50 columns; entries are separated by one space",
        "# row 1 is the least-significant bit of the integer column encoding",
    ]
    for row in range(redundancy):
        lines.append(" ".join(str((column >> row) & 1) for column in columns))
    return "\n".join(lines) + "\n"


def check_exact(path: Path, expected: str) -> None:
    if not path.exists():
        raise SystemExit(f"missing generated artifact: {path}")
    actual = path.read_text()
    if actual != expected:
        raise SystemExit(f"generated artifact is stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="write H and the JSON certificate")
    action.add_argument("--check", action="store_true", help="byte-check committed generated files")
    args = parser.parse_args()

    redundancy, columns = load_columns()
    certificate = render_certificate(redundancy, columns)
    matrix = render_matrix(redundancy, columns)
    if args.write:
        CERTIFICATE_PATH.write_text(certificate)
        MATRIX_PATH.write_text(matrix)
        print(f"wrote {MATRIX_PATH.name} and {CERTIFICATE_PATH.name}")
    else:
        check_exact(CERTIFICATE_PATH, certificate)
        check_exact(MATRIX_PATH, matrix)
        print("PASS: generated matrix and certificate are byte-for-byte current")


if __name__ == "__main__":
    main()
