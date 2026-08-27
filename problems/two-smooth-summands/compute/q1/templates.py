"""Closed-form covering templates and exact n^{p/q} tests.

A template is a function n |-> (a, n-a) with 1 <= a < n. It lifts at
the rational exponent p/q only if max(P+(a), P+(n-a))^q <= n^p for
every large n. Isolated holes on a prefix are residue.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from smooth_lib import largest_prime_factor


def floor_n_pow(n: int, p: int, q: int) -> int:
    """Largest k >= 1 with k^q <= n^p. This is floor(n^{p/q}) for n>=1."""
    if n <= 1:
        return 1
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if pow(mid, q) <= pow(n, p):
            lo = mid
        else:
            hi = mid - 1
    return lo


def exceeds_pow(val: int, n: int, p: int, q: int) -> bool:
    """val > n^{p/q}, via val^q > n^p."""
    return pow(val, q) > pow(n, p)


def template_fails(a: int, n: int, p: int, q: int) -> bool:
    if a < 1 or a >= n:
        return True
    b = n - a
    f = max(largest_prime_factor(a), largest_prime_factor(b))
    return exceeds_pow(f, n, p, q)


def square_plus_remainder(n: int) -> int:
    m = int(math.isqrt(n))
    r = n - m * m
    if r == 0:
        return (m - 1) * (m - 1) if m > 1 else 1
    return m * m


def largest_pow2(n: int) -> int:
    return 1 << (n - 1).bit_length() - 1


def triangular(n: int) -> int:
    # Largest k(k+1)/2 < n.
    k = int((math.isqrt(8 * n - 7) - 1) // 2)
    k = max(1, k)
    t = k * (k + 1) // 2
    while t >= n:
        k -= 1
        t = k * (k + 1) // 2
    return max(1, t)


def cube(n: int) -> int:
    k = int(round(n ** (1.0 / 3.0)))
    while k * k * k >= n:
        k -= 1
    while (k + 1) ** 3 < n:
        k += 1
    return max(1, k * k * k)


def floor_divisor(n: int, p: int, q: int) -> int:
    """a = n - (n mod u), u = floor(n^{p/q}), or n-u if u divides n.

    Remainder is < u <= n^{p/q}, so it is automatically n^{p/q}-smooth
    by size. The first summand is u * floor(n/u), and fails exactly when
    floor(n/u) is n^{p/q}-rough (or u itself is).
    """
    u = max(1, floor_n_pow(n, p, q))
    if u >= n:
        u = n - 1
    r = n % u
    if r == 0:
        return n - u if u < n else 1
    return n - r


CLOSED_FORMS: dict[str, Callable[[int], int]] = {
    "square_plus_remainder": square_plus_remainder,
    "largest_pow2": largest_pow2,
    "triangular": triangular,
    "cube": cube,
}


def closed_form_holes(
    name: str,
    fn: Callable[[int], int],
    p: int,
    q: int,
    limit: int,
    max_holes: int = 40,
) -> dict:
    holes: list[int] = []
    first = None
    last = None
    count = 0
    for n in range(2, limit + 1):
        if template_fails(fn(n), n, p, q):
            count += 1
            last = n
            if first is None:
                first = n
            if len(holes) < max_holes:
                holes.append(n)
    return {
        "template": name,
        "exponent": f"{p}/{q}",
        "limit": limit,
        "first_hole": first,
        "last_hole": last,
        "n_holes": count,
        "n_holes_recorded": len(holes),
        "first_holes": holes,
        "covers_the_range": first is None,
        "holes_persist_to_limit": last is not None and last > limit - 100,
        "is_dent": False,
    }


def floor_divisor_holes(p: int, q: int, limit: int, max_holes: int = 40) -> dict:
    holes: list[int] = []
    first = None
    last = None
    count = 0
    for n in range(2, limit + 1):
        if template_fails(floor_divisor(n, p, q), n, p, q):
            count += 1
            last = n
            if first is None:
                first = n
            if len(holes) < max_holes:
                holes.append(n)
    return {
        "template": "floor_divisor",
        "exponent": f"{p}/{q}",
        "limit": limit,
        "first_hole": first,
        "last_hole": last,
        "n_holes": count,
        "n_holes_recorded": len(holes),
        "first_holes": holes,
        "covers_the_range": first is None,
        "holes_persist_to_limit": last is not None and last > limit - 100,
        "is_dent": False,
    }
