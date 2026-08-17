#!/usr/bin/env python3
"""Closed-form sanity checks for the 0/1 census.

- |P_n| = 2^{n-1}
- # {f in P_n : (x+1)|f } = # {f : f(-1)=0}
- I_2(n) = (1/n) sum_{d|n} mu(d) 2^{n/d}  is a lower bound on #irreducible
  (every F2-irreducible is Z-irreducible)
"""

from __future__ import annotations

import math


def mu(n: int) -> int:
    if n == 1:
        return 1
    n0 = n
    p = 2
    primes = 0
    while p * p <= n:
        if n % p == 0:
            n //= p
            primes += 1
            if n % p == 0:
                return 0
        p += 1 if p == 2 else 2
    if n > 1:
        primes += 1
    return -1 if primes % 2 else 1


def I2(n: int) -> int:
    s = 0
    d = 1
    while d * d <= n:
        if n % d == 0:
            s += mu(d) * (1 << (n // d))
            if d * d != n:
                s += mu(n // d) * (1 << d)
        d += 1
    return s // n


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def xplus1_count(n: int) -> int:
    """Number of f in P_n with f(-1)=0.

    Ends a0=an=1. Even-position free bits and odd-position free bits
    must balance the two forced +1's at the even ends when n is even,
    or one forced +1 at 0 and one forced -1 at n when n is odd.
    """
    if n < 1:
        return 0
    if n == 1:
        # 1+x, f(-1)=0
        return 1
    # positions 0..n
    # contribution of x^i is (+1) if i even, (-1) if i odd
    # forced: pos 0 contributes +1, pos n contributes (+1) if n even else -1
    if n % 2 == 0:
        # free even positions: 2,4,...,n-2 : n/2 - 1 of them
        # free odd positions: 1,3,...,n-1 : n/2 of them
        # 1 + E + 1 - O = 0 => O = E+2
        ev = n // 2 - 1
        od = n // 2
        return sum(binom(ev, k) * binom(od, k + 2) for k in range(ev + 1))
    else:
        # n odd: forced 1 at 0 (+), 1 at n (-)
        # free even: 2,4,...,n-1 : (n-1)/2 - 0 wait 2..n-1 step 2: (n-1)/2 - 0 = (n-1)/2
        # positions even in 1..n-1: 2,4,...,n-1. n-1 is even, so 2..n-1 even: (n-1)/2
        # odd free: 1,3,...,n-2: (n-1)/2
        # 1 + E - (O + 1) = 0 => E = O
        ev = (n - 1) // 2
        od = (n - 1) // 2
        return sum(binom(ev, k) * binom(od, k) for k in range(ev + 1))


def main() -> None:
    print("n  |P|  x+1  I2  I2/|P|")
    for n in range(1, 31):
        tot = 1 << (n - 1)
        xp = xplus1_count(n)
        i2 = I2(n)
        print(f"{n:2d}  {tot:10d}  {xp:10d}  {i2:10d}  {i2/tot:.6f}")


if __name__ == "__main__":
    main()
