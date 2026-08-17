"""Core predicates for Green #32 / Shakan 2020.

g(A) is the longest run of consecutive misses of A in Z/pZ.
max_d g(dA) is the length of the longest AP in the complement of A.
Shakan: max_d g(dA) >= 2*p/|A| - 2  for |A| > 1.
"""

from __future__ import annotations

import math
from typing import Iterable


def uniq_mod(A: Iterable[int], p: int) -> list[int]:
    return sorted({int(a) % p for a in A})


def gap(A: Iterable[int], p: int) -> int:
    """Longest number of consecutive residues missed by A. Empty set -> p."""
    S = uniq_mod(A, p)
    if not S:
        return p
    if len(S) == p:
        return 0
    best = (S[0] + p) - S[-1] - 1
    for i in range(1, len(S)):
        d = S[i] - S[i - 1] - 1
        if d > best:
            best = d
    return best


def max_gap_dilates(A: Iterable[int], p: int) -> tuple[int, int]:
    """Return (max_d g(dA), a witnessing d in 1..p-1)."""
    S = uniq_mod(A, p)
    if not S:
        return p, 1
    best_g, best_d = -1, 1
    for d in range(1, p):
        gd = gap(((d * a) % p for a in S), p)
        if gd > best_g:
            best_g, best_d = gd, d
            if best_g >= p - 1:
                break
    return best_g, best_d


def L_of(A: Iterable[int], p: int) -> float:
    S = uniq_mod(A, p)
    if not S:
        return float("inf")
    g, _ = max_gap_dilates(S, p)
    return (len(S) / p) * g


def shakan_lower(p: int, n: int) -> float:
    if n <= 1:
        return float("inf")
    return 2 * p / n - 2


def longest_ap_in_complement(A: Iterable[int], p: int) -> tuple[int, int, int]:
    """Longest AP in F_p \\ A. Returns (length, start, difference)."""
    S = set(uniq_mod(A, p))
    if len(S) == p:
        return 0, 0, 1
    best = (1, 0, 1)
    for d in range(1, p):
        # walk cycles of +d; there is one cycle of length p
        seen = [False] * p
        for s in range(p):
            if seen[s]:
                continue
            run = 0
            start_of_run = s
            x = s
            first_miss_start = None
            first_miss_len = 0
            wrapping = True
            for _ in range(p):
                seen[x] = True
                if x not in S:
                    if run == 0:
                        start_of_run = x
                    run += 1
                    if wrapping:
                        first_miss_len += 1
                else:
                    wrapping = False
                    if run > best[0]:
                        best = (run, start_of_run, d)
                    run = 0
                x = (x + d) % p
            total = run + (first_miss_len if not wrapping else 0)
            # if the whole cycle missed, total = p and start is anything
            if wrapping:
                total = p
                start_of_run = s
            elif run > 0:
                # wrap: suffix run joins prefix first_miss
                start_of_run = (s - run * d) % p
            if total > best[0]:
                best = (total, start_of_run, d)
    return best


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    r = int(n**0.5)
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True


def primes_upto(n: int) -> list[int]:
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i * i : n + 1 : i] = b"\x00" * (((n - i * i) // i) + 1)
    return [i for i in range(n + 1) if sieve[i]]


def primitive_root(p: int) -> int:
    """Least primitive root mod p. p prime."""
    if p == 2:
        return 1
    phi = p - 1
    facts = []
    m = phi
    f = 2
    while f * f <= m:
        if m % f == 0:
            facts.append(f)
            while m % f == 0:
                m //= f
        f += 1 if f == 2 else 2
    if m > 1:
        facts.append(m)
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in facts):
            return g
    raise RuntimeError(f"no primitive root mod {p}")
