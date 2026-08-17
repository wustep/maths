"""Exact helpers for sums of two squares. Integers only; no density claims."""

from __future__ import annotations

import math
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple


def isqrt(n: int) -> int:
    return math.isqrt(n)


def is_square(n: int) -> bool:
    if n < 0:
        return False
    r = isqrt(n)
    return r * r == n


def is_sum_of_two_squares(n: int) -> bool:
    """Fermat: every p=3 (mod 4) has even exponent."""
    if n < 0:
        return False
    while n % 4 == 0:
        n //= 4
    while n % 2 == 0:
        n //= 2
    p = 3
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            if p % 4 == 3 and e % 2 == 1:
                return False
        p += 2
    return n % 4 != 3


def bc_point(n: int) -> Tuple[int, int, int]:
    """Bambah–Chowla point: u=floor(sqrt(n)), v=ceil(sqrt(n-u^2)).

    Returns (u, v, u^2+v^2) with n <= u^2+v^2.
    """
    if n <= 0:
        return (0, 0, 0)
    u = isqrt(n)
    rem = n - u * u
    if rem == 0:
        return (u, 0, n)
    s = isqrt(rem)
    v = s if s * s == rem else s + 1
    return (u, v, u * u + v * v)


def phi_bc(n: int) -> float:
    """The Bambah–Chowla comparison function 2*sqrt(2)*n^{1/4}."""
    return 2.0 * math.sqrt(2.0) * n ** 0.25


def next_two_square_scan(n: int, limit: int) -> Optional[int]:
    """Small-range exact scan: first two-square in [n, limit]."""
    for x in range(n, limit + 1):
        if is_sum_of_two_squares(x):
            return x
    return None


def nearby_two_squares(n: int, window: int) -> List[Tuple[int, int, int]]:
    """Lattice points with n <= u^2+v^2 < n+window, u,v >= 0.

    Search u from 0 to floor(sqrt(n+window-1)). For each u, v is the
    unique ceil(sqrt(n-u^2)) if that lands in range, plus a few extra
    v that still stay below n+window.
    """
    out: List[Tuple[int, int, int]] = []
    umax = isqrt(n + window - 1)
    for u in range(umax + 1):
        need = n - u * u
        if need <= 0:
            vmin = 0
        else:
            s = isqrt(need)
            vmin = s if s * s == need else s + 1
        vmax_sq = n + window - 1 - u * u
        if vmax_sq < 0:
            continue
        vmax = isqrt(vmax_sq)
        for v in range(vmin, vmax + 1):
            s = u * u + v * v
            if n <= s < n + window:
                out.append((u, v, s))
    out.sort(key=lambda t: (t[2], t[0], t[1]))
    return out


def first_two_square_ge(n: int, extra: int) -> Optional[Tuple[int, int, int]]:
    """First two-square s >= n found among lattice points with s < n+extra."""
    pts = nearby_two_squares(n, extra)
    return pts[0] if pts else None


def shiu_family_n(m: int) -> Tuple[int, int, int]:
    """Shiu's even-m family: 2u+1 = (m+1)^2, n = u^2 + m^2 + 1.

    Returns (u, n, 2*m) with the BC / (u+1)^2 gap equal to 2m.
    Requires m even so that u is an integer.
    """
    if m % 2 != 0:
        raise ValueError("Shiu family needs even m")
    u = m * (m + 2) // 2
    n = u * u + m * m + 1
    return u, n, 2 * m


def generate_two_squares_upto(N: int) -> List[int]:
    """All a^2+b^2 in [0, N], sorted unique. Includes 0."""
    seen = bytearray(N + 1)
    rmax = isqrt(N)
    for a in range(rmax + 1):
        a2 = a * a
        bmax = isqrt(N - a2)
        for b in range(bmax + 1):
            seen[a2 + b * b] = 1
    return [i for i, v in enumerate(seen) if v]
