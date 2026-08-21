#!/usr/bin/env python3
"""Standard triangulation of T_d and classical sign distributions.

The standard triangulation cuts each unit cell along the antidiagonal
(i+1,j)-(i,j+1).  It is convex: the quadratic lifting h(i,j) =
i^2 + i*j + j^2 picks exactly these diagonals (the mixed coefficient
is positive, so the lower hull prefers the antidiagonal pair), and
sanity.py certifies this exactly via tcurve.check_convexity.

The Harnack sign distribution eps(i,j) = -1 iff i and j are both odd
(else +1) yields Harnack's M-curve in every degree (Itenberg).
"""

from fractions import Fraction

from tcurve import lattice_points


def standard_triangulation(d):
    tris = []
    for i in range(d):
        for j in range(d - i):
            tris.append(((i, j), (i + 1, j), (i, j + 1)))
            if i + j <= d - 2:
                tris.append(((i + 1, j), (i, j + 1), (i + 1, j + 1)))
    return tris


def standard_heights(d):
    return {(i, j): Fraction(i * i + i * j + j * j)
            for (i, j) in lattice_points(d)}


def harnack_signs(d):
    return {(i, j): -1 if (i % 2 == 1 and j % 2 == 1) else 1
            for (i, j) in lattice_points(d)}


def all_plus_signs(d):
    return {(i, j): 1 for (i, j) in lattice_points(d)}
