#!/usr/bin/env python3
"""Check the signotope/parity interpretation on an exact coordinate grid."""

from __future__ import annotations

import itertools


Point = tuple[int, int]


def orient(a: Point, b: Point, c: Point) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def inside_triangle(p: Point, a: Point, b: Point, c: Point) -> bool:
    signs = (orient(a, b, p), orient(b, c, p), orient(c, a, p))
    return all(value > 0 for value in signs) or all(value < 0 for value in signs)


def main() -> None:
    patterns: set[tuple[bool, ...]] = set()
    examined = 0
    nonconvex = 0
    for xs in itertools.combinations(range(-2, 3), 4):
        for ys in itertools.product(range(-2, 3), repeat=4):
            points = list(zip(xs, ys))
            a, b, c, d = points
            determinants = (
                orient(a, b, c),
                orient(a, b, d),
                orient(a, c, d),
                orient(b, c, d),
            )
            if not all(determinants):
                continue

            signs = tuple(value > 0 for value in determinants)
            changes = sum(signs[i] != signs[i + 1] for i in range(3))
            is_nonconvex = any(
                inside_triangle(
                    points[i], *(points[j] for j in range(4) if j != i)
                )
                for i in range(4)
            )
            assert changes <= 1
            assert is_nonconvex == (sum(signs) % 2 == 1)
            patterns.add(signs)
            examined += 1
            nonconvex += is_nonconvex

    assert len(patterns) == 8
    assert examined == 2_222
    assert nonconvex == 472
    print(
        "geometry audit: 2222 exact x-ordered four-tuples; "
        "8 signotope patterns; odd parity iff non-convex"
    )


if __name__ == "__main__":
    main()
