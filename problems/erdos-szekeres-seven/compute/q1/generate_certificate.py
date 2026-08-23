#!/usr/bin/env python3
"""Generate the exact 32-point Erdős–Szekeres witness from paper recurrences."""

from __future__ import annotations

import csv
import sys
from functools import cache
from pathlib import Path


Point = tuple[int, int]


@cache
def cup_cap_set(k: int, ell: int) -> tuple[Point, ...]:
    """Return S_{k,ell} from arXiv:1602.03075v2, Sections 2.1--2.2."""
    if k <= 2 or ell <= 2:
        return ((0, 0),)
    r = k + ell - 1
    delta_x = 3 * 4 ** (r - 1)
    delta_y = (3 * r + 1) * 4 ** (r - 1)
    left = cup_cap_set(k - 1, ell)
    right = tuple(
        (x + delta_x, y + delta_y) for x, y in cup_cap_set(k, ell - 1)
    )
    return left + right


def erdos_szekeres_set(t: int) -> list[Point]:
    """Return S_t from arXiv:1602.03075v2, Section 2.3."""
    scale = (t + 1) * 4 ** (t + 1)
    wx = wy = 0
    points: list[Point] = []
    for i in range(t - 1):
        points.extend(
            (x + scale * wx, y + scale * wy)
            for x, y in cup_cap_set(t - i, i + 2)
        )
        if i < t - 2:
            wx += 3 * (t - i)
            wy -= 3 * i
    return points


def read_certificate(path: Path) -> list[Point]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [int(row["id"]) for row in rows] == list(range(len(rows)))
    return [(int(row["x"]), int(row["y"])) for row in rows]


def main() -> None:
    expected = erdos_szekeres_set(7)
    assert len(expected) == 32
    path = Path(__file__).with_name("points.csv")
    actual = read_certificate(path)
    if actual != expected:
        sys.exit(f"certificate differs from the Section 2 recurrence: {path}")
    print("generator: points.csv matches the t=7 recurrence (32 points)")


if __name__ == "__main__":
    main()
