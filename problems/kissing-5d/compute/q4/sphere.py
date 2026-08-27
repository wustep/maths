"""Integer model of (1/d)Z^5 on |x|^2 = 2.

Points a in Z^5 with a·a = 2 d^2; kissing iff a·b <= d^2.
d = 4 is the leftover 1480-point graph.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product


def d5_pts(d: int):
    pts = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [0] * 5
            v[i] = si * d
            v[j] = sj * d
            pts.append(tuple(v))
    return pts


def ip(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] + a[4] * b[4]


def enumerate_sphere(d: int):
    target = 2 * d * d
    lim = 0
    while (lim + 1) * (lim + 1) <= target:
        lim += 1
    squares = {i * i: i for i in range(lim + 1)}
    pts = []
    for a in range(-lim, lim + 1):
        r2 = target - a * a
        for b in range(-lim, lim + 1):
            r3 = r2 - b * b
            if r3 < 0:
                continue
            for c in range(-lim, lim + 1):
                r4 = r3 - c * c
                if r4 < 0:
                    continue
                for e in range(-lim, lim + 1):
                    rem = r4 - e * e
                    if rem not in squares:
                        continue
                    f = squares[rem]
                    for s in ((f,) if f == 0 else (f, -f)):
                        pts.append((a, b, c, e, s))
    return pts


def extras_and_groups(d: int):
    thresh = d * d
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    extras = [p for p in pts if p not in Dset]
    groups = defaultdict(list)
    masks = []
    for p in extras:
        m = 0
        for i, r in enumerate(D):
            if ip(p, r) > thresh:
                m |= 1 << i
        groups[m].append(p)
        masks.append(m)
    return {
        "d": d,
        "thresh": thresh,
        "pts": pts,
        "D": D,
        "extras": extras,
        "groups": groups,
        "masks": masks,
    }
