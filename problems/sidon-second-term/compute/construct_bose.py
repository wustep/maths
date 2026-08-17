#!/usr/bin/env python3
"""Bose–Chowla Sidon sets and greedy extra points.

For prime p, Bose–Chowla gives a Sidon subset of [p^2-1] of size p, hence
F(p^2-1) >= p = sqrt(N+1). The second term is o(1). This script:

  * builds the set (finite field F_{p^2} via a Conway-style modulus search)
  * verifies it is Sidon
  * greedily tries to add integers in a slightly larger interval
  * records how many extra points appear

A bounded number of extra points is still O(1), not a dent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def find_moduli(p: int):
    """Irreducible x^2 - t x - n over F_p, and a generator of F_{p^2}^*."""
    for t in range(p):
        for n in range(p):
            # x^2 - t x - n irreducible iff disc t^2+4n is nonsquare
            disc = (t * t + 4 * n) % p
            if pow(disc, (p - 1) // 2, p) == 1:
                continue
            if disc == 0:
                continue
            # try to find a generator θ = (a,b) meaning a + b x
            order = p * p - 1
            # factor order coarsely
            factors = []
            m = order
            f = 2
            while f * f <= m:
                if m % f == 0:
                    factors.append(f)
                    while m % f == 0:
                        m //= f
                f += 1 if f == 2 else 2
            if m > 1:
                factors.append(m)

            def mul(u, v):
                # (u0 + u1 x)(v0 + v1 x) = u0 v0 + (u0 v1+u1 v0) x + u1 v1 x^2
                # x^2 = t x + n
                a = (u[0] * v[0] + u[1] * v[1] * n) % p
                b = (u[0] * v[1] + u[1] * v[0] + u[1] * v[1] * t) % p
                return (a, b)

            def pow_el(g, e):
                r = (1, 0)
                while e:
                    if e & 1:
                        r = mul(r, g)
                    g = mul(g, g)
                    e >>= 1
                return r

            for a in range(p):
                for b in range(1, p):
                    g = (a, b)
                    if all(pow_el(g, order // q) != (1, 0) for q in factors):
                        return t, n, g
    raise RuntimeError(f"no generator for p={p}")


def bose_chowla(p: int) -> list[int]:
    t, n, theta = find_moduli(p)
    # powers of theta: θ^i = (c0, c1). θ^i - θ ∈ F_p iff the x-coeff of θ^i equals that of θ.
    # θ = (a,b) stored. Element of F_p is (k, 0).
    # We want θ^i ∈ θ + F_p, i.e. θ^i - θ has x-coeff 0.

    def mul(u, v, t=t, n=n, p=p):
        a = (u[0] * v[0] + u[1] * v[1] * n) % p
        b = (u[0] * v[1] + u[1] * v[0] + u[1] * v[1] * t) % p
        return (a, b)

    # Standard Bose: A = { i : 0 ≤ i ≤ p^2-2, θ^i + θ ∈ F_p } or θ^i - θ.
    # Use θ^i ∈ F_p + θ, i.e. θ^i - θ has vanishing x-coefficient.
    cur = (1, 0)  # θ^0
    out = []
    for i in range(p * p - 1):
        # cur - theta
        dx = (cur[1] - theta[1]) % p
        if dx == 0:
            out.append(i)
        cur = mul(cur, theta)
    return out


def is_sidon(xs: list[int]) -> bool:
    seen = set()
    n = len(xs)
    for i in range(n):
        for j in range(i, n):
            s = xs[i] + xs[j]
            if s in seen:
                return False
            seen.add(s)
    return True


def greedy_extend(base: list[int], N: int) -> list[int]:
    sums = set()
    xs = list(base)
    for i, a in enumerate(xs):
        for b in xs[i:]:
            sums.add(a + b)
    for y in range(N + 1):
        if y in xs:
            continue
        doubles = {y + y}
        crosses = {y + x for x in xs}
        if doubles & sums or crosses & sums or (y + y) in crosses:
            continue
        if len(crosses) < len(xs):  # collision among crosses
            continue
        xs.append(y)
        sums |= doubles
        sums |= crosses
    xs.sort()
    return xs


def main():
    primes = [p for p in range(3, 80) if is_prime(p)]
    rows = []
    for p in primes:
        A = bose_chowla(p)
        N0 = p * p - 1
        # Bose lives in {0,...,p^2-2} typically
        A = sorted(set(A))
        ok = is_sidon(A) and max(A) <= N0 - 1 and len(A) == p
        # try to add points in [0, N0-1] and a bit beyond
        extra_in = greedy_extend(A, N0 - 1)
        extra_wide = greedy_extend(A, N0 + 4 * p)
        rec = {
            "p": p,
            "N0": N0,
            "size": len(A),
            "max": max(A) if A else None,
            "sidon": ok,
            "sqrtN": N0**0.5,
            "second_term": len(A) - N0**0.5,
            "greedy_in_interval": len(extra_in),
            "extra_in_interval": len(extra_in) - len(A),
            "greedy_wide": len(extra_wide),
            "extra_wide": len(extra_wide) - len(A),
            "wide_N": N0 + 4 * p,
            "wide_second": len(extra_wide) - (N0 + 4 * p) ** 0.5,
        }
        rows.append(rec)
        print(json.dumps(rec), flush=True)
        if not ok:
            print("WARN construction failed", p, "size", len(A), "max", max(A) if A else None, flush=True)

    out = Path(__file__).resolve().parent / "bose_greedy.json"
    out.write_text(json.dumps(rows, indent=2))
    extras = [r["extra_in_interval"] for r in rows if r["sidon"]]
    print("primes_ok", sum(1 for r in rows if r["sidon"]), "/", len(rows))
    print("extra_in_interval_values", extras)
    print("max_extra_in_interval", max(extras) if extras else None)


if __name__ == "__main__":
    main()
