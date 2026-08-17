"""Shared exact helpers for y-smooth numbers and F / G."""

from __future__ import annotations

import math
from functools import lru_cache


def primes_upto(n: int) -> list[int]:
    if n < 2:
        return []
    s = bytearray(b"\x01") * (n + 1)
    s[0:2] = b"\x00\x00"
    for p in range(2, int(n**0.5) + 1):
        if s[p]:
            s[p * p : n + 1 : p] = b"\x00" * (((n - p * p) // p) + 1)
    return [i for i in range(2, n + 1) if s[i]]


@lru_cache(maxsize=None)
def primes_upto_cached(n: int) -> tuple[int, ...]:
    return tuple(primes_upto(n))


def largest_prime_factor(n: int) -> int:
    if n <= 1:
        return 1
    x = n
    last = 1
    while x % 2 == 0:
        last = 2
        x //= 2
    f = 3
    while f * f <= x:
        while x % f == 0:
            last = f
            x //= f
        f += 2
    if x > 1:
        last = x
    return last


def is_y_smooth(n: int, y: int) -> bool:
    return n >= 1 and largest_prime_factor(n) <= y


def smooth_upto(limit: int, y: int) -> list[int]:
    """All y-smooth positive integers <= limit, increasing, including 1."""
    if limit < 1:
        return []
    out = [1]
    for p in primes_upto(y):
        ext = []
        for s in out:
            v = s * p
            while v <= limit:
                ext.append(v)
                if v > limit // p:
                    break
                v *= p
        out.extend(ext)
    out.sort()
    return out


def jacobi(a: int, n: int) -> int:
    """Jacobi symbol (a/n), n odd positive."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("jacobi modulus must be odd positive")
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            n8 = n % 8
            if n8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def F_one(n: int) -> tuple[int, int, int]:
    """Return (F(n), a, n-a) for a minimising max(P+(a), P+(n-a))."""
    best = n
    best_a = 1
    for a in range(1, n):
        val = max(largest_prime_factor(a), largest_prime_factor(n - a))
        if val < best:
            best = val
            best_a = a
            if best <= 2:
                break
    return best, best_a, n - best_a


def F_via_smooth(n: int) -> tuple[int, int, int]:
    """F(n) by testing increasing smoothness bounds against S_y + S_y."""
    # Upper bound from the square covering.
    m = int(math.isqrt(n))
    r = n - m * m
    if r == 0:
        upper = largest_prime_factor(2 * m - 1) if m > 1 else 1
        if m > 1:
            upper = max(largest_prime_factor(m - 1), upper)
    else:
        upper = max(largest_prime_factor(m), largest_prime_factor(r))
    # Binary search the least y with n in S_y+S_y.
    lo, hi = 1, upper
    best_a = 1
    while lo < hi:
        mid = (lo + hi) // 2
        a = representation(n, mid)
        if a is not None:
            hi = mid
            best_a = a
        else:
            lo = mid + 1
    return lo, best_a, n - best_a


def representation(n: int, y: int) -> int | None:
    """Smallest a in 1..n//2 with a and n-a both y-smooth, or None."""
    S = set(smooth_upto(n - 1, y))
    for a in range(1, n // 2 + 1):
        if a in S and (n - a) in S:
            return a
    return None
