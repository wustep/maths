#!/usr/bin/env python3
"""Enumerate n with n^2+1 prime or P2, independently of OEIS.

Odd n>1 make n^2+1 even and composite. Only even n are searched.
Primality is deterministic Miller-Rabin for 64-bit integers.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def primes_upto(limit: int) -> list[int]:
    if limit < 2:
        return []
    n = limit + 1
    sieve = bytearray(b"\x01") * n
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            sieve[p * p :: p] = b"\x00" * (((n - 1 - p * p) // p) + 1)
    return [i for i in range(2, n) if sieve[i]]


def modpow(a: int, e: int, m: int) -> int:
    return pow(a, e, m)


def miller_rabin(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    if n in small:
        return True
    if any(n % p == 0 for p in small):
        return False
    # Deterministic for n < 2^64 (Jaeschke / Sinclair).
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


def tonelli_neg1(q: int) -> int | None:
    """Square root of -1 mod q, or None if q != 1 mod 4."""
    if q % 4 != 1:
        return None
    return pow(q - 1, (q + 1) // 4, q) if pow(q - 1, (q - 1) // 2, q) == 1 else pow(2, (q - 1) // 4, q)


def sqrt_minus_one(q: int) -> int:
    # For q = 1 mod 4, i^{(q+1)/4} works when i is a quadratic nonresidue? Standard:
    # find z with z^{(q-1)/2} == -1, then ...
    # Simpler: since -1 is a residue, a^{(q+1)/4} is a sqrt of a for residue a.
    return pow(q - 1, (q + 1) // 4, q)


def trial_omega(m: int, bound: int) -> tuple[int, int]:
    """Return (omega, remaining). remaining==1 means fully factored."""
    omega = 0
    if m % 2 == 0:
        omega += 1
        while m % 2 == 0:
            m //= 2
    p = 3
    while p * p <= m and p <= bound:
        if m % p == 0:
            omega += 1
            while m % p == 0:
                m //= p
        p += 2
    if m > 1:
        if miller_rabin(m):
            omega += 1
            m = 1
        # else leftover composite
    return omega, m


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-max", type=int, default=200_000)
    parser.add_argument("--out", type=Path, default=HERE / "n2p1.json")
    args = parser.parse_args()
    n_max = args.n_max

    primes = primes_upto(min(1_000_003, max(1000, int(n_max**0.5) * 20)))
    marked = bytearray(n_max + 1)
    for q in primes:
        if q == 2 or q % 4 != 1:
            continue
        r = sqrt_minus_one(q)
        if (r * r + 1) % q != 0:
            # fallback search
            r = next((x for x in range(1, q) if (x * x + 1) % q == 0), None)
            if r is None:
                continue
        for residue in (r, q - r):
            start = residue
            if start == 0:
                start = q
            for n in range(start, n_max + 1, q):
                if n * n + 1 != q:
                    marked[n] = 1

    prime_n: list[int] = []
    p2_n: list[dict[str, int]] = []
    for n in range(0, n_max + 1, 2):
        if n == 0:
            continue
        m = n * n + 1
        if m == 2:
            prime_n.append(n)
            continue
        if not marked[n] and miller_rabin(m):
            prime_n.append(n)
            continue
        # P2 hunt: fully factor small leftovers
        omega, rem = trial_omega(m, 2_000_000)
        if rem == 1 and 1 <= omega <= 2 and not miller_rabin(m):
            p2_n.append({"n": n, "m": m, "omega": omega})
        elif rem == 1 and omega == 1:
            # should have been caught as prime
            if n not in prime_n:
                prime_n.append(n)

    prime_n = sorted(set(prime_n))
    payload = {
        "n_max": n_max,
        "count_prime": len(prime_n),
        "count_p2_omega_le_2_composite": len(p2_n),
        "prime_n": prime_n,
        "prime_values": [n * n + 1 for n in prime_n],
        "note": "prime_n are even n (plus n=1 if in range) with n^2+1 prime by deterministic 64-bit MR. P2 list is incomplete if trial bound misses a factor.",
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"n_max={n_max} primes={len(prime_n)} p2={len(p2_n)} wrote {args.out}")
    print("first primes", payload["prime_values"][:20])
    print("last primes", payload["prime_values"][-5:])


if __name__ == "__main__":
    main()
