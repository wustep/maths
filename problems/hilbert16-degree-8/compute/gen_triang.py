#!/usr/bin/env python3
"""Random convex (regular) primitive triangulations of T_d.

Strategy: heights = M * Q(i,j) + r(i,j) where Q is a random
positive-definite integer quadratic form and r is integer noise.
The float lower hull of the lifted points is computed by brute force
(every triple of points whose lifted plane lies strictly below all
other lifted points is a face).  The result is then validated
combinatorially (validate_triangulation: primitive, all lattice
points used) and certified EXACTLY (check_convexity with Fraction
heights).  Anything that fails is rejected, so no unverified
triangulation ever reaches the search.

Noise scale sweeps from tiny (Delaunay-like triangulations of the
form Q with random tie-breaks) to comparable with M (skewed, skinny
triangles), giving a varied sample of the regular primitive
triangulation space.  This is a SAMPLE, not an enumeration.
"""

from fractions import Fraction
import random

from tcurve import (lattice_points, validate_triangulation,
                    check_convexity)


def float_lower_hull_triangles(pts, h):
    """All triples whose lifted plane is strictly below the other
    lifted points (float arithmetic; exactness comes later)."""
    n = len(pts)
    tris = []
    for a in range(n):
        xa, ya = pts[a]
        ha = h[a]
        for b in range(a + 1, n):
            xb, yb = pts[b]
            hb = h[b]
            for c in range(b + 1, n):
                xc, yc = pts[c]
                det = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
                if det == 0:
                    continue
                hc = h[c]
                # plane z = A x + B y + C
                A = ((hb - ha) * (yc - ya) - (hc - ha) * (yb - ya)) / det
                B = ((xb - xa) * (hc - ha) - (xc - xa) * (hb - ha)) / det
                C = ha - A * xa - B * ya
                ok = True
                for k in range(n):
                    if k == a or k == b or k == c:
                        continue
                    if h[k] <= A * pts[k][0] + B * pts[k][1] + C + 1e-9:
                        ok = False
                        break
                if ok:
                    tris.append((pts[a], pts[b], pts[c]))
    return tris


def random_certified_triangulation(d, rng, noise_num=1, noise_den=50):
    """One certified (triangulation, heights) pair, or None.

    Heights are integers M*Q + r with M = 10^6 and r uniform in
    [0, M*noise_num/noise_den).
    """
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
    hf = [float(hts[p]) for p in pts]
    tris = float_lower_hull_triangles(pts, hf)
    if validate_triangulation(d, tris):
        return None
    frac = {p: Fraction(hts[p]) for p in pts}
    if check_convexity(d, tris, frac):
        return None
    return tris, frac


def triangulation_signature(tris):
    return tuple(sorted(tuple(sorted(t)) for t in tris))
