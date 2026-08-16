#!/usr/bin/env python3
"""Shared geometry for the canonical odd-order rct4 model.

For n = 2m + 1, the canonical orientation used by Prellberg fixes the
anti-diagonal empty.  A representative (i, j) in

    H_n = {0, ..., m} x {0, ..., m - 1}

has a four-cycle under quarter-turn rotation when i != j.  A representative
(i, i) has only its half-turn mate; the missing quarter-turn images lie on
the fixed-empty anti-diagonal.

This module deliberately contains no solver code.  It is also not imported by
the independent witness checker.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import gcd
from typing import Iterator


Point = tuple[int, int]
Signature = tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class Rct4Geometry:
    n: int
    orbits: tuple[tuple[Point, ...], ...]
    representatives: tuple[Point, ...]
    point_to_orbit: dict[Point, int]
    diagonal_orbits: tuple[int, ...]
    off_diagonal_orbits: tuple[int, ...]
    fixed_empty: frozenset[Point]


@dataclass(frozen=True)
class LineStatistics:
    primitive_directions: int
    maximal_lines: int
    nonhorizontal_nonvertical_lines: int
    tautologies_after_reduction: int
    duplicate_signatures: int
    retained_signatures: int
    retained_weighted_terms: int
    retained_max_arity: int


def quarter_turn(point: Point, n: int) -> Point:
    """Rotate clockwise by 90 degrees about the centre of the n by n grid."""

    x, y = point
    return y, n - 1 - x


def half_turn(point: Point, n: int) -> Point:
    x, y = point
    return n - 1 - x, n - 1 - y


def build_rct4_geometry(n: int) -> Rct4Geometry:
    if n < 3 or n % 2 == 0:
        raise ValueError("canonical rct4 is defined here only for odd n >= 3")

    m = (n - 1) // 2
    fixed_empty = frozenset((x, n - 1 - x) for x in range(n))
    orbits: list[tuple[Point, ...]] = []
    representatives: list[Point] = []
    point_to_orbit: dict[Point, int] = {}
    diagonal_orbits: list[int] = []
    off_diagonal_orbits: list[int] = []

    for i in range(m + 1):
        for j in range(m):
            representative = (i, j)
            if i == j:
                members = (representative, half_turn(representative, n))
            else:
                orbit_set: set[Point] = set()
                current = representative
                for _ in range(4):
                    orbit_set.add(current)
                    current = quarter_turn(current, n)
                members = tuple(sorted(orbit_set))

            if any(point in fixed_empty for point in members):
                raise AssertionError(f"variable orbit intersects fixed anti-diagonal: {members}")
            if any(point in point_to_orbit for point in members):
                raise AssertionError(f"overlapping rct4 orbit: {members}")

            orbit_id = len(orbits)
            orbits.append(tuple(sorted(members)))
            representatives.append(representative)
            for point in members:
                point_to_orbit[point] = orbit_id

            if i == j:
                if len(members) != 2:
                    raise AssertionError("diagonal rct4 orbit must have size two")
                diagonal_orbits.append(orbit_id)
            else:
                if len(members) != 4:
                    raise AssertionError("off-diagonal rct4 orbit must have size four")
                off_diagonal_orbits.append(orbit_id)

    all_points = {(x, y) for x in range(n) for y in range(n)}
    variable_points = set(point_to_orbit)
    if variable_points & fixed_empty:
        raise AssertionError("fixed and variable cells overlap")
    if variable_points | set(fixed_empty) != all_points:
        missing = sorted(all_points - variable_points - set(fixed_empty))
        raise AssertionError(f"rct4 cells do not partition the grid; missing {missing[:5]}")
    if len(orbits) != (n * n - 1) // 4:
        raise AssertionError("unexpected number of rct4 orbit variables")

    return Rct4Geometry(
        n=n,
        orbits=tuple(orbits),
        representatives=tuple(representatives),
        point_to_orbit=point_to_orbit,
        diagonal_orbits=tuple(diagonal_orbits),
        off_diagonal_orbits=tuple(off_diagonal_orbits),
        fixed_empty=fixed_empty,
    )


def primitive_directions(n: int) -> Iterator[tuple[int, int]]:
    """Yield one orientation of every primitive direction supporting 3 cells."""

    radius = (n - 1) // 2
    yield 0, 1  # vertical
    for dx in range(1, radius + 1):
        for dy in range(-radius, radius + 1):
            if gcd(dx, abs(dy)) == 1:
                yield dx, dy


def maximal_grid_lines(n: int) -> Iterator[tuple[Point, ...]]:
    """Yield every maximal grid line containing at least three lattice cells."""

    for dx, dy in primitive_directions(n):
        for x in range(n):
            for y in range(n):
                previous = (x - dx, y - dy)
                if 0 <= previous[0] < n and 0 <= previous[1] < n:
                    continue

                points: list[Point] = []
                xx, yy = x, y
                while 0 <= xx < n and 0 <= yy < n:
                    points.append((xx, yy))
                    xx += dx
                    yy += dy
                if len(points) >= 3:
                    yield tuple(points)


def reduced_line_signatures(
    geometry: Rct4Geometry,
    *,
    omit_horizontal: bool = True,
    omit_vertical: bool = True,
) -> tuple[tuple[Signature, ...], LineStatistics]:
    """Return unique non-tautological weighted at-most-two constraints.

    A signature records (orbit_id, multiplicity_on_line).  Cells on the fixed
    anti-diagonal disappear.  Horizontal and vertical constraints may be
    omitted when the caller replaces them with exact row/column equalities.
    """

    n = geometry.n
    signatures: set[Signature] = set()
    direction_count = sum(1 for _ in primitive_directions(n))
    maximal_count = 0
    non_axis_count = 0
    tautology_count = 0
    duplicate_count = 0

    for points in maximal_grid_lines(n):
        maximal_count += 1
        if omit_horizontal and all(y == points[0][1] for _, y in points):
            continue
        if omit_vertical and all(x == points[0][0] for x, _ in points):
            continue
        non_axis_count += 1

        incidence = Counter(
            geometry.point_to_orbit[point]
            for point in points
            if point in geometry.point_to_orbit
        )
        # With binary variables, sum of all positive coefficients <= 2 makes
        # the inequality automatic.
        if sum(incidence.values()) <= 2:
            tautology_count += 1
            continue
        signature = tuple(sorted(incidence.items()))
        if signature in signatures:
            duplicate_count += 1
        else:
            signatures.add(signature)

    ordered = tuple(sorted(signatures))
    stats = LineStatistics(
        primitive_directions=direction_count,
        maximal_lines=maximal_count,
        nonhorizontal_nonvertical_lines=non_axis_count,
        tautologies_after_reduction=tautology_count,
        duplicate_signatures=duplicate_count,
        retained_signatures=len(ordered),
        retained_weighted_terms=sum(len(signature) for signature in ordered),
        retained_max_arity=max((len(signature) for signature in ordered), default=0),
    )
    return ordered, stats


def row_signature(geometry: Rct4Geometry, row: int) -> Signature:
    counts = Counter(
        geometry.point_to_orbit[(x, row)]
        for x in range(geometry.n)
        if (x, row) in geometry.point_to_orbit
    )
    return tuple(sorted(counts.items()))


def column_signature(geometry: Rct4Geometry, column: int) -> Signature:
    counts = Counter(
        geometry.point_to_orbit[(column, y)]
        for y in range(geometry.n)
        if (column, y) in geometry.point_to_orbit
    )
    return tuple(sorted(counts.items()))


def selected_points(geometry: Rct4Geometry, selected_orbits: set[int]) -> list[Point]:
    return sorted(
        point
        for orbit_id in selected_orbits
        for point in geometry.orbits[orbit_id]
    )
