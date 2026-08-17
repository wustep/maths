"""Exact coordinates for the four known 40-point kissing codes in R^5.

All returned points have squared Euclidean norm 2.  Distinct points of a
kissing configuration then satisfy <x,y> <= 1.

Sources: Korkine–Zolotareff 1873 (D5); Leech 1967 (L5); Szöllősi 2023 /
Cohn–Rajagopal arXiv:2412.00937v3 (Q5, R5).
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from typing import Iterable, List, Sequence, Tuple

Vec = Tuple[Fraction, ...]
F = Fraction


def _f(*coords) -> Vec:
    return tuple(F(c) for c in coords)


def _dot(a: Sequence[F], b: Sequence[F]) -> F:
    return sum(x * y for x, y in zip(a, b))


def _norm2(a: Sequence[F]) -> F:
    return _dot(a, a)


def _unique(pts: Iterable[Vec]) -> List[Vec]:
    seen = set()
    out: List[Vec] = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def d5() -> List[Vec]:
    """40 roots: all permutations of (±1, ±1, 0, 0, 0)."""
    pts: List[Vec] = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [F(0)] * 5
            v[i] = F(si)
            v[j] = F(sj)
            pts.append(tuple(v))
    return _unique(pts)


def _signed_half(odd: bool, last: F) -> List[Vec]:
    """8 points (±1/2, ±1/2, ±1/2, ±1/2, last) with prescribed parity of minuses."""
    pts: List[Vec] = []
    for signs in product((-1, 1), repeat=4):
        nneg = sum(1 for s in signs if s < 0)
        if (nneg % 2 == 1) == odd:
            pts.append(_f(signs[0] * F(1, 2), signs[1] * F(1, 2),
                          signs[2] * F(1, 2), signs[3] * F(1, 2), last))
    return pts


def l5() -> List[Vec]:
    """Leech's L5: D5 with the x5 = +1 layer replaced by the odd-sign half-spinor."""
    pts: List[Vec] = []
    # keep D5 except the eight points with last coordinate +1
    for p in d5():
        if p[4] != F(1):
            pts.append(p)
    pts.extend(_signed_half(odd=True, last=F(1)))
    return _unique(pts)


def _reflect_coord_sum(v: Vec) -> Vec:
    """Orthogonal reflection across the hyperplane sum_i x_i = 0.

    A vector of coordinate-sum s is sent to v - (2s/5) * (1,1,1,1,1).
    """
    s = sum(v)
    shift = 2 * s / 5
    return tuple(x - shift for x in v)


def _coord_sum(v: Vec) -> F:
    return sum(v)


def q5() -> List[Vec]:
    """Szöllősi Q5: D5 with the coord-sum = +2 layer replaced by the
    reflection of the coord-sum = -2 layer."""
    base = d5()
    keep = [p for p in base if _coord_sum(p) != F(2)]
    minus = [p for p in base if _coord_sum(p) == F(-2)]
    replaced = [_reflect_coord_sum(p) for p in minus]
    return _unique(keep + replaced)


def r5() -> List[Vec]:
    """Cohn–Rajagopal R5: the same layer swap applied to L5."""
    base = l5()
    keep = [p for p in base if _coord_sum(p) != F(2)]
    minus = [p for p in base if _coord_sum(p) == F(-2)]
    replaced = [_reflect_coord_sum(p) for p in minus]
    return _unique(keep + replaced)


CONFIGS = {
    "D5": d5,
    "L5": l5,
    "Q5": q5,
    "R5": r5,
}


def pairwise_ips(pts: Sequence[Vec]) -> List[F]:
    """Normalized inner products of distinct pairs (points have norm^2 = 2)."""
    ips: List[F] = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            ips.append(_dot(pts[i], pts[j]) / 2)
    return ips


def ip_histogram(pts: Sequence[Vec]) -> dict:
    hist: dict = {}
    for t in pairwise_ips(pts):
        hist[t] = hist.get(t, 0) + 1
    return dict(sorted(hist.items(), key=lambda kv: kv[0]))


def max_normalized_ip(pts: Sequence[Vec]) -> F:
    return max(pairwise_ips(pts)) if len(pts) >= 2 else F(0)


def is_kissing(pts: Sequence[Vec]) -> bool:
    if any(_norm2(p) != F(2) for p in pts):
        return False
    if len(set(pts)) != len(pts):
        return False
    return max_normalized_ip(pts) <= F(1, 2)
