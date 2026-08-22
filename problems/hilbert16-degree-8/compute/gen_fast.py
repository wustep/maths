#!/usr/bin/env python3
"""Vectorised twin of gen_triang.random_certified_triangulation.

Same heights, same brute-force lower-hull rule, same exact acceptance tests
(validate_triangulation + Fraction check_convexity); only the O(n^3 * n)
"is this lifted plane below every other lifted point" scan is moved into
numpy.  gen_fast_check.py asserts the two agree triangulation-for-
triangulation on the same rng stream.
"""
from fractions import Fraction
from itertools import combinations

import numpy as np

from tcurve import lattice_points, validate_triangulation, check_convexity

_CACHE = {}


def _combos(n):
    if n not in _CACHE:
        idx = np.array(list(combinations(range(n), 3)), dtype=np.int64)
        mask = np.ones((len(idx), n), dtype=bool)
        rows = np.arange(len(idx))[:, None]
        mask[rows, idx] = False
        _CACHE[n] = (idx, mask)
    return _CACHE[n]


def lower_hull_triangles(pts, h):
    P = np.asarray(pts, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    n = len(pts)
    idx, mask = _combos(n)
    a, b, c = idx[:, 0], idx[:, 1], idx[:, 2]
    xa, ya, ha = P[a, 0], P[a, 1], h[a]
    xb, yb, hb = P[b, 0], P[b, 1], h[b]
    xc, yc, hc = P[c, 0], P[c, 1], h[c]
    det = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
    good = det != 0
    A = np.where(good, ((hb - ha) * (yc - ya) - (hc - ha) * (yb - ya)) / np.where(good, det, 1), 0.0)
    B = np.where(good, ((xb - xa) * (hc - ha) - (xc - xa) * (hb - ha)) / np.where(good, det, 1), 0.0)
    C = ha - A * xa - B * ya
    plane = A[:, None] * P[None, :, 0] + B[:, None] * P[None, :, 1] + C[:, None]
    below = (h[None, :] <= plane + 1e-9) & mask
    keep = good & ~below.any(axis=1)
    return [(pts[a[i]], pts[b[i]], pts[c[i]]) for i in np.nonzero(keep)[0]]


def random_certified_triangulation(d, rng, noise_num=1, noise_den=50):
    pts = lattice_points(d)
    M = 10 ** 6
    while True:
        a = rng.randint(1, 6)
        c = rng.randint(1, 6)
        bmax = int((4 * a * c) ** 0.5) - 1
        b = rng.randint(-bmax, bmax) if bmax > 0 else 0
        if 4 * a * c - b * b > 0:
            break
    R = max(1, (M * noise_num) // noise_den)
    hts = {}
    for (i, j) in pts:
        q = a * i * i + b * i * j + c * j * j
        hts[(i, j)] = M * q + rng.randrange(R)
    tris = lower_hull_triangles(pts, [float(hts[p]) for p in pts])
    if validate_triangulation(d, tris):
        return None
    frac = {p: Fraction(hts[p]) for p in pts}
    if check_convexity(d, tris, frac):
        return None
    return tris, frac
