"""Count solutions of x + 2y = 3z in a finite integer set.

T(S) is Aaronson's count: all ordered triples in S^3, including the
|S| trivials x = y = z. Affine copies of {0,1,3} are the T(S) - |S|
nontrivial triples (d = z - y ≠ 0).
"""

from __future__ import annotations

from typing import Iterable


def t_count(s: Iterable[int]) -> int:
    pts = list(s)
    present = set(pts)
    t = 0
    for x in pts:
        for y in pts:
            tot = x + 2 * y
            if tot % 3 == 0 and tot // 3 in present:
                t += 1
    return t


def t_count_sorted(pts: list[int]) -> int:
    present = set(pts)
    t = 0
    for x in pts:
        for y in pts:
            tot = x + 2 * y
            if tot % 3 == 0 and tot // 3 in present:
                t += 1
    return t


def residue_bound(s: Iterable[int]) -> int:
    """T(S) <= A0^2 + A1^2 + A2^2."""
    a = [0, 0, 0]
    for x in s:
        a[x % 3] += 1
    return a[0] * a[0] + a[1] * a[1] + a[2] * a[2]


def interval_t(n: int) -> int:
    """Exact T({0,1,...,n-1}).

    z = (x+2y)/3 lands in the interval automatically, so this is
    #{(x,y) : x ≡ y (mod 3)}.
    """
    if n <= 0:
        return 0
    # sizes of residue classes 0,1,2 in [0, n)
    a0 = (n + 2) // 3
    a1 = (n + 1) // 3
    a2 = n // 3
    return a0 * a0 + a1 * a1 + a2 * a2


def interval_formula_check(n: int) -> int:
    r = n % 3
    m = n // 3
    if r == 0:
        return 3 * m * m
    if r == 1:
        return 3 * m * m + 2 * m + 1
    return 3 * m * m + 4 * m + 2


def hl_upper(n: int) -> int:
    """Hardy–Littlewood / Aaronson Lemma 2.6: T <= (3 n^2 + 1)/4."""
    return (3 * n * n + 1) // 4


def affine_normalise(s: Iterable[int]) -> tuple[int, ...]:
    pts = sorted(set(s))
    if not pts:
        return tuple()
    lo = pts[0]
    pts = [p - lo for p in pts]
    g = 0
    for p in pts:
        g = _gcd(g, p)
    if g > 1:
        pts = [p // g for p in pts]
    return tuple(pts)


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)
