#!/usr/bin/env python3
"""Decode one current Flammenkamp no-three-in-line database entry."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,."
assert len(ALPHABET) == 90
SYMMETRY = {
    ".": "iden",
    ":": "rot2",
    "/": "dia1",
    "-": "ort1",
    "o": "rot4",
    "c": "rct4",
    "x": "dia2",
    "+": "ort2",
    "*": "full",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--n", type=int, default=71)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lines = [line.strip() for line in args.code.read_text(encoding="ascii").splitlines() if line.strip()]
    if len(lines) != 1:
        raise ValueError(f"expected one encoded configuration, found {len(lines)}")
    code = lines[0]
    if not code or code[0] not in SYMMETRY:
        raise ValueError("missing or unknown symmetry character")

    columns = code[1:]
    if len(columns) != 2 * args.n:
        raise ValueError(f"encoded payload has {len(columns)} columns, expected {2 * args.n}")

    points: list[tuple[int, int]] = []
    for row in range(args.n):
        pair = columns[2 * row : 2 * row + 2]
        try:
            selected = [ALPHABET.index(character) for character in pair]
        except ValueError as error:
            raise ValueError(f"row {row}: character outside the database alphabet") from error
        if any(column >= args.n for column in selected):
            raise ValueError(f"row {row}: column outside the {args.n}-grid: {selected}")
        if selected[0] == selected[1]:
            raise ValueError(f"row {row}: duplicate column {selected[0]}")
        points.extend((column, row) for column in selected)

    points.sort()
    payload = "".join(f"{x} {y}\n" for x, y in points)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="ascii")
    print(f"DECODED symmetry={SYMMETRY[code[0]]} n={args.n} points={len(points)}")
    print(f"code_sha256={hashlib.sha256((code + chr(10)).encode('ascii')).hexdigest()}")
    print(f"witness_sha256={hashlib.sha256(payload.encode('ascii')).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
