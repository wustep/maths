#!/usr/bin/env python3
"""Rank symmetry-preserving embeddings of Heule's n=73 rct4 witness."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from rct4_model import build_rct4_geometry  # noqa: E402


ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,."


def decode(path: Path, n: int) -> list[tuple[int, int]]:
    code = path.read_text(encoding="ascii").strip()
    if code[:1] != "c" or len(code) != 1 + 2 * n:
        raise ValueError("expected one canonical rct4 database code")
    points = []
    for row in range(n):
        for character in code[1 + 2 * row : 3 + 2 * row]:
            column = ALPHABET.index(character)
            if column >= n:
                raise ValueError(f"row {row}: column {column} is outside the grid")
            points.append((column, row))
    return points


def normalized_line(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int, int]:
    dx = right[0] - left[0]
    dy = right[1] - left[1]
    a, b = dy, -dx
    c = dx * left[1] - dy * left[0]
    divisor = gcd(gcd(abs(a), abs(b)), abs(c))
    a, b, c = a // divisor, b // divisor, c // divisor
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return a, b, c


def conflict_metrics(points: list[tuple[int, int]]) -> tuple[int, int]:
    lines: dict[tuple[int, int, int], set[int]] = defaultdict(set)
    for left in range(len(points)):
        for right in range(left + 1, len(points)):
            line = normalized_line(points[left], points[right])
            lines[line].update((left, right))
    bad = [indices for indices in lines.values() if len(indices) >= 3]
    return len(bad), len(set().union(*bad)) if bad else 0


def embed(points: list[tuple[int, int]], omitted_low: int) -> list[tuple[int, int]]:
    omitted = {omitted_low, 74 - omitted_low}
    image = [coordinate for coordinate in range(75) if coordinate not in omitted]
    if len(image) != 73:
        raise AssertionError("embedding must omit two distinct symmetric coordinates")
    return sorted((image[x], image[y]) for x, y in points)


def selected_orbits(points: list[tuple[int, int]]) -> int:
    geometry = build_rct4_geometry(75)
    selected = set()
    for point in points:
        if point not in geometry.point_to_orbit:
            raise AssertionError(f"embedded point {point} lies on the fixed anti-diagonal")
        selected.add(geometry.point_to_orbit[point])
    if sum(len(geometry.orbits[orbit_id]) for orbit_id in selected) != len(points):
        raise AssertionError("embedding is not a union of complete rct4 orbits")
    return len(selected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, default=HERE / "n73-rct4.code")
    parser.add_argument("--output", type=Path, default=HERE / "n73-best-embedding.txt")
    parser.add_argument("--json", type=Path, default=HERE / "n73-embedding-audit.json")
    args = parser.parse_args()

    source = decode(args.code, 73)
    rows = []
    images = {}
    for omitted_low in range(37):
        image = embed(source, omitted_low)
        bad_lines, conflicted_points = conflict_metrics(image)
        orbit_count = selected_orbits(image)
        row = {
            "omitted_coordinates": [omitted_low, 74 - omitted_low],
            "bad_lines": bad_lines,
            "conflicted_points": conflicted_points,
            "selected_orbits": orbit_count,
        }
        rows.append(row)
        images[omitted_low] = image

    rows.sort(key=lambda row: (row["bad_lines"], row["conflicted_points"], row["omitted_coordinates"]))
    best = rows[0]
    best_low = best["omitted_coordinates"][0]
    payload = "".join(f"{x} {y}\n" for x, y in images[best_low])
    args.output.write_text(payload, encoding="ascii")
    args.json.write_text(json.dumps({"source_n": 73, "target_n": 75, "best": best, "embeddings": rows}, indent=2) + "\n")
    print(json.dumps(best, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
