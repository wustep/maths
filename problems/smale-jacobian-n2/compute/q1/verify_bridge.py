#!/usr/bin/env python3
"""Independently check the published-polygon-to-certificate bridge."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def lattice_points(vertices: list[list[int]]) -> list[tuple[int, int]]:
    """Return all lattice points in a convex polygon, boundary included."""
    xmax = max(point[0] for point in vertices)
    ymax = max(point[1] for point in vertices)
    points = []
    edges = list(zip(vertices, vertices[1:] + vertices[:1]))
    for x in range(xmax + 1):
        for y in range(ymax + 1):
            crosses = [
                (b[0] - a[0]) * (y - a[1])
                - (b[1] - a[1]) * (x - a[0])
                for a, b in edges
            ]
            if all(value >= 0 for value in crosses) or all(
                value <= 0 for value in crosses
            ):
                points.append((x, y))
    return points


def bands(points: list[tuple[int, int]]) -> dict[int, tuple[int, int, int]]:
    by_band: dict[int, list[int]] = defaultdict(list)
    for x, y in points:
        by_band[2 * x - y].append(x)
    return {
        band: (min(xs), max(xs), len(xs))
        for band, xs in sorted(by_band.items())
    }


Monomial = tuple[str, ...]
Expression = dict[Monomial, int]


def add_term(expression: Expression, coefficient: int, *atoms: str) -> None:
    monomial = tuple(sorted(atoms))
    expression[monomial] = expression.get(monomial, 0) + coefficient
    if expression[monomial] == 0:
        del expression[monomial]


def coefficient_identities() -> dict[int, Expression]:
    """Expand P_z Q_t - P_t Q_z as a differential polynomial."""
    p_terms = [(2, "A", "Ap"), (1, "B", "Bp"), (0, "C", "Cp")]
    q_terms = [
        (3, "D", "Dp"),
        (2, "E", "Ep"),
        (1, "F", "Fp"),
        (0, "G", "Gp"),
    ]
    answer: dict[int, Expression] = defaultdict(dict)
    for p_power, p_atom, p_derivative in p_terms:
        for q_power, q_atom, q_derivative in q_terms:
            z_power = p_power + q_power - 1
            if p_power:
                add_term(answer[z_power], p_power, p_atom, q_derivative)
            if q_power:
                add_term(answer[z_power], -q_power, p_derivative, q_atom)
    return dict(answer)


def expected_identities() -> dict[int, Expression]:
    expected: dict[int, Expression] = {power: {} for power in range(5)}
    for power, terms in {
        4: [(2, "A", "Dp"), (-3, "Ap", "D")],
        3: [(2, "A", "Ep"), (-2, "Ap", "E"), (1, "B", "Dp"), (-3, "Bp", "D")],
        2: [(2, "A", "Fp"), (-1, "Ap", "F"), (1, "B", "Ep"), (-2, "Bp", "E"), (-3, "Cp", "D")],
        1: [(2, "A", "Gp"), (1, "B", "Fp"), (-1, "Bp", "F"), (-2, "Cp", "E")],
        0: [(1, "B", "Gp"), (-1, "Cp", "F")],
    }.items():
        for coefficient, left, right in terms:
            add_term(expected[power], coefficient, left, right)
    return expected


def determinant_3(matrix: list[list[int]]) -> int:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} certificate.json")
    certificate = json.loads(Path(sys.argv[1]).read_text())

    record = certificate["record"]
    assert record["threshold"] == 125
    assert record["exceptional_degree_pairs"] == [[72, 108], [108, 72]]

    summaries = []
    for case_number in (1, 2):
        case = certificate["proposition_4_3"][f"case_{case_number}"]
        p_points = lattice_points(case["P_vertices"])
        q_points = lattice_points(case["Q_vertices"])
        assert [len(p_points), len(q_points)] == case["lattice_points"]
        p_bands = bands(p_points)
        q_bands = bands(q_points)
        assert [min(p_bands), max(p_bands)] == case["band_ranges"][0]
        assert [min(q_bands), max(q_bands)] == case["band_ranges"][1]
        summaries.append(
            (case_number, len(p_points), len(q_points), min(p_bands), max(p_bands), min(q_bands), max(q_bands))
        )

    # t=x*y^2 and z=y^-1: det d(t,z)/d(x,y) = -1, and x=t*z^2.
    coordinate_jacobian = 1 * -1 - 2 * 0
    assert coordinate_jacobian == certificate["laurent_change"]["coordinate_jacobian"]
    assert certificate["laurent_change"]["x_squared"] == "t^2*z^4"
    assert coefficient_identities() == expected_identities()
    assert len(certificate["laurent_change"]["coefficient_identities"]) == 5

    vertices = certificate["normalization"]["vertices"]
    exponent_matrix = [[x, y, 1] for x, y in vertices]
    normalization_determinant = determinant_3(exponent_matrix)
    assert normalization_determinant == certificate["normalization"]["exponent_matrix_determinant"]
    assert normalization_determinant != 0

    print("BRIDGE_THEOREM threshold=125 exceptions=72,108;108,72")
    for case, p_count, q_count, p_min, p_max, q_min, q_max in summaries:
        print(
            f"BRIDGE_CASE case={case} P_points={p_count} Q_points={q_count} "
            f"P_bands={p_min}..{p_max} Q_bands={q_min}..{q_max}"
        )
    print("BRIDGE_COORDINATES jacobian=-1 x2=t^2*z^4")
    print("BRIDGE_IDENTITIES count=5")
    print(f"BRIDGE_NORMALIZATION determinant={normalization_determinant}")
    print("BRIDGE_PASS")


if __name__ == "__main__":
    main()

