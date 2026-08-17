#!/usr/bin/env python3
"""Shared arithmetic for n^2+1 primes and Iwaniec P2s.

Deterministic Miller–Rabin is the 64-bit Jaeschke/Sinclair witness set
(2,3,5,7,11,13,23), sufficient for every n^2+1 with n < 2^32.
"""
from __future__ import annotations

import math
from array import array

# Wolf / OEIS A199401 / Hardy–Littlewood conjecture E.
C_Q = 1.372813462818246009112192696727
EULER = 0.57721566490153286060651209008240243

# Wolf Table I / OEIS A083844: number of primes q = m^2+1 with q < 10^k.
WOLF_PI_Q = {
    6: 112,
    7: 316,
    8: 841,
    9: 2378,
    10: 6656,
    11: 18822,
    12: 54110,
    13: 156081,
    14: 456362,
    15: 1339875,
    16: 3954181,
}


def primes_upto(limit: int) -> list[int]:
    if limit < 2:
        return []
    n = limit + 1
    sieve = bytearray(b"\x01") * n
    sieve[0:2] = b"\x00\x00"
    r = int(limit**0.5)
    for p in range(2, r + 1):
        if sieve[p]:
            sieve[p * p :: p] = b"\x00" * (((n - 1 - p * p) // p) + 1)
    return [i for i in range(2, n) if sieve[i]]


def miller_rabin(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    if n in small:
        return True
    if any(n % p == 0 for p in small):
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 23):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def sqrt_minus_one(p: int) -> int:
    """r with r^2 ≡ -1 (mod p). Requires odd prime p ≡ 1 (mod 4)."""
    if p % 4 != 1:
        raise ValueError(f"sqrt(-1) does not exist mod {p}")
    exp = (p - 1) // 4
    a = 2
    while a < p:
        r = pow(a, exp, p)
        if (r * r + 1) % p == 0:
            return r
        a += 1
    raise RuntimeError(f"failed to find sqrt(-1) mod {p}")


def pollard_rho(n: int) -> int:
    """Deterministic Brent–Pollard factor of a composite n > 1."""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    for c in range(1, 96):
        y = 2
        d = 1
        r = 1
        q = 1
        ys = y
        while d == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and d == 1:
                ys = y
                mstep = min(128, r - k)
                for _ in range(mstep):
                    y = (y * y + c) % n
                    q = (q * abs(x - y)) % n
                d = math.gcd(q, n)
                k += mstep
            r *= 2
        if d != n:
            return d
        y = ys
        while True:
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
            if d > 1:
                if d != n:
                    return d
                break
    raise RuntimeError(f"pollard rho failed on {n}")


def factor_int(m: int, small_primes: list[int] | None = None) -> list[int]:
    """Prime factors of m with multiplicity, sorted. m >= 1."""
    if m < 1:
        raise ValueError(m)
    if m == 1:
        return []
    fs: list[int] = []
    if small_primes is None:
        bound = min(100_003, int(m**0.5) + 1)
        small_primes = primes_upto(bound)
    for p in small_primes:
        if p * p > m:
            break
        while m % p == 0:
            fs.append(p)
            m //= p
    if m == 1:
        return fs
    stack = [m]
    while stack:
        t = stack.pop()
        if t == 1:
            continue
        if miller_rabin(t):
            fs.append(t)
            continue
        d = pollard_rho(t)
        stack.append(d)
        stack.append(t // d)
    return sorted(fs)


def omega_big_omega(factors: list[int]) -> tuple[int, int]:
    if not factors:
        return 0, 0
    return len(set(factors)), len(factors)


def li(x: float) -> float:
    """Soldner li(x) = γ + log log x + sum_{n>=1} (log x)^n / (n·n!), x>1."""
    if x <= 1.0:
        raise ValueError(x)
    L = math.log(x)
    s = EULER + math.log(L)
    term = L
    n = 1
    while n < 250:
        s += term / n
        n += 1
        term *= L / n
        if term / n < 1e-18 * (1.0 + abs(s)):
            break
    return s


def bateman_horn_integral(n_max: int, npts: int = 400_000) -> float:
    """∫_2^{n_max} dt / log(t^2+1) by the trapezoid rule."""
    if n_max <= 2:
        return 0.0
    npts = max(npts, 2000)
    h = (n_max - 2.0) / (npts - 1)
    acc = 0.0
    for i in range(npts):
        t = 2.0 + i * h
        y = 1.0 / math.log(t * t + 1.0)
        if i == 0 or i == npts - 1:
            acc += 0.5 * y
        else:
            acc += y
    return acc * h


def landau_shanks_product(primes: list[int]) -> float:
    """Truncated Euler product for C_q. Converges slowly; a check, not the working value."""
    logc = 0.0
    for p in primes:
        if p == 2:
            continue
        chi = 1 if (p % 4 == 1) else -1
        logc += math.log1p(-chi / (p - 1))
    return math.exp(logc)


def wolf_prediction_li(n_max: int) -> float:
    """(C_q/2)(li(N) - li(√2)), Wolf's recasting of Hardy–Littlewood E at x=N^2."""
    return 0.5 * C_Q * (li(float(n_max)) - li(math.sqrt(2.0)))


def even_index(n: int) -> int:
    return n // 2 - 1


def n_from_index(i: int) -> int:
    return 2 * (i + 1)
