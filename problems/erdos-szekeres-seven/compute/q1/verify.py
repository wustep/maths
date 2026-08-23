#!/usr/bin/env python3
"""Exact verifier using non-convex 4-subsets as blocking certificates."""

from __future__ import annotations

import csv
import itertools
from math import comb
from pathlib import Path


Point = tuple[int, int]


def orient(a: Point, b: Point, c: Point) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def inside_triangle(p: Point, a: Point, b: Point, c: Point) -> bool:
    signs = (orient(a, b, p), orient(b, c, p), orient(c, a, p))
    return all(value > 0 for value in signs) or all(value < 0 for value in signs)


def nonconvex_four(points: list[Point], indices: tuple[int, ...]) -> bool:
    for pos, index in enumerate(indices):
        triangle = [points[indices[j]] for j in range(4) if j != pos]
        if inside_triangle(points[index], *triangle):
            return True
    return False


def mask(indices: tuple[int, ...]) -> int:
    return sum(1 << index for index in indices)


def load_points() -> list[Point]:
    path = Path(__file__).with_name("points.csv")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [int(row["id"]) for row in rows] == list(range(32))
    return [(int(row["x"]), int(row["y"])) for row in rows]


def main() -> None:
    points = load_points()
    assert len(points) == len(set(points)) == 32

    triples = 0
    for indices in itertools.combinations(range(32), 3):
        triples += 1
        assert orient(*(points[index] for index in indices)) != 0, indices

    blockers = {
        mask(indices)
        for indices in itertools.combinations(range(32), 4)
        if nonconvex_four(points, indices)
    }
    assert len(blockers) == 12_740

    seven_sets = 0
    for indices in itertools.combinations(range(32), 7):
        seven_sets += 1
        assert any(
            mask(four) in blockers for four in itertools.combinations(indices, 4)
        ), indices

    assert triples == comb(32, 3) == 4_960
    assert seven_sets == comb(32, 7) == 3_365_856
    print(
        "python verifier: 4960 noncollinear triples; "
        "3365856 seven-sets blocked by 12740 non-convex four-sets"
    )


if __name__ == "__main__":
    main()
