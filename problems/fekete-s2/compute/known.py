#!/usr/bin/env python3
"""Exact / closed-form configurations for N=2–7 and N=12."""

from __future__ import annotations

import math

import numpy as np

from energy import log_energy, project_to_sphere


def antipodes():
    return np.array([[0.0, 0.0, 1.0], [0.0, 0.0, -1.0]])


def triangle():
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [-0.5, math.sqrt(3.0) / 2.0, 0.0],
            [-0.5, -math.sqrt(3.0) / 2.0, 0.0],
        ]
    )


def tetrahedron():
    # Regular simplex, then project (already equal norm).
    return project_to_sphere(
        [
            [1.0, 1.0, 1.0],
            [1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, -1.0, 1.0],
        ]
    )


def triangular_bipyramid():
    # N=5: poles plus equatorial equilateral triangle. Dragnev–Legg–Townsend.
    return np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
            [1.0, 0.0, 0.0],
            [-0.5, math.sqrt(3.0) / 2.0, 0.0],
            [-0.5, -math.sqrt(3.0) / 2.0, 0.0],
        ]
    )


def octahedron():
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ]
    )


def pentagonal_bipyramid():
    # N=7 1:5:1. Conjectured global; proven among dipole configs
    # (Beltrán–Lizarte arXiv:2502.10152v3).
    pts = [[0.0, 0.0, 1.0], [0.0, 0.0, -1.0]]
    for k in range(5):
        ang = 2.0 * math.pi * k / 5.0
        pts.append([math.cos(ang), math.sin(ang), 0.0])
    return np.asarray(pts)


def icosahedron():
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    pts = []
    for a in (1.0, -1.0):
        for b in (phi, -phi):
            pts.append([0.0, a, b])
            pts.append([a, b, 0.0])
            pts.append([b, 0.0, a])
    return project_to_sphere(pts)


KNOWN = {
    2: ("antipodes", antipodes, -math.log(2.0)),
    3: ("equilateral", triangle, -1.5 * math.log(3.0)),
    4: ("tetrahedron", tetrahedron, 3.0 * math.log(3.0 / 8.0)),
    5: ("triangular_bipyramid", triangular_bipyramid, -4.0 * math.log(2.0) - 1.5 * math.log(3.0)),
    6: ("octahedron", octahedron, -9.0 * math.log(2.0)),
    7: ("pentagonal_bipyramid", pentagonal_bipyramid, None),
    12: ("icosahedron", icosahedron, None),
}


def closed_form_energy(n: int) -> float:
    name, builder, exact = KNOWN[n]
    pts = builder()
    e = log_energy(pts)
    if exact is not None:
        return exact
    return e


def main() -> None:
    print(f"{'N':>3}  {'name':<22}  {'E_numeric':>18}  {'E_closed':>18}  {'|diff|':>10}")
    for n, (name, builder, exact) in KNOWN.items():
        pts = builder()
        e = log_energy(pts)
        closed = exact if exact is not None else float("nan")
        diff = abs(e - exact) if exact is not None else float("nan")
        print(f"{n:3d}  {name:<22}  {e:18.12f}  {closed:18.12f}  {diff:10.2e}")
        assert abs(np.linalg.norm(pts, axis=1) - 1.0).max() < 1e-14
        if exact is not None:
            assert abs(e - exact) < 1e-13, (n, e, exact)


if __name__ == "__main__":
    main()
