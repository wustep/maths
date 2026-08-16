#!/usr/bin/env python3
"""Independent exact checker for a 142-point witness on the 71 by 71 grid.

This checker intentionally does not import the search model.  It parses plain
integer coordinates and tests every one of the C(142, 3) determinants.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from itertools import combinations
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("witness", type=Path, nargs="?", default=Path("n71-142.txt"))
    parser.add_argument("--n", type=int, default=71)
    return parser.parse_args()


def read_points(path: Path) -> tuple[list[tuple[int, int]], bytes]:
    payload = path.read_bytes()
    points: list[tuple[int, int]] = []
    for line_number, raw_line in enumerate(payload.decode("utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 2:
            raise ValueError(f"{path}:{line_number}: expected exactly two integers")
        try:
            point = int(fields[0]), int(fields[1])
        except ValueError as error:
            raise ValueError(f"{path}:{line_number}: invalid integer coordinate") from error
        points.append(point)
    return points, payload


def main() -> int:
    args = parse_args()
    points, payload = read_points(args.witness)
    expected = 2 * args.n
    errors: list[str] = []

    if len(points) != expected:
        errors.append(f"point count is {len(points)}, expected {expected}")
    duplicates = [point for point, count in Counter(points).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate points: {duplicates[:5]}")
    outside = [point for point in points if not (0 <= point[0] < args.n and 0 <= point[1] < args.n)]
    if outside:
        errors.append(f"out-of-grid points: {outside[:5]}")

    bad_triple = None
    determinants_checked = 0
    for a, b, c in combinations(points, 3):
        determinants_checked += 1
        determinant = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if determinant == 0:
            bad_triple = a, b, c
            break
    if bad_triple is not None:
        errors.append(f"collinear triple: {bad_triple}")

    row_counts = Counter(y for _, y in points)
    column_counts = Counter(x for x, _ in points)
    if len(points) == expected and not outside and any(row_counts[y] != 2 for y in range(args.n)):
        errors.append("not every row contains exactly two points")
    if len(points) == expected and not outside and any(column_counts[x] != 2 for x in range(args.n)):
        errors.append("not every column contains exactly two points")

    digest = hashlib.sha256(payload).hexdigest()
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        print(f"sha256={digest}")
        print(f"determinants_checked={determinants_checked}")
        return 1

    total_triples = expected * (expected - 1) * (expected - 2) // 6
    if determinants_checked != total_triples:
        raise AssertionError("checker did not exhaust all triples")
    print("VALID")
    print(f"n={args.n} points={len(points)}")
    print(f"determinants_checked={determinants_checked}")
    print("rows=2-each columns=2-each")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
