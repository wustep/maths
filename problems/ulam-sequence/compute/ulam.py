"""Exact generation of the classical Ulam sequence U(1,2)."""

from __future__ import annotations


def ulam_upto_value(limit: int) -> list[int]:
    """All Ulam numbers in {1, ..., limit}.

    Incremental sieve: when u is added, increment representation counts of
    u + v for every previously found Ulam number v.
    """
    if limit < 1:
        return []
    if limit == 1:
        return [1]
    counts = [0] * (limit + 1)
    ulam = [1, 2]
    if 1 + 2 <= limit:
        counts[3] = 1
    n = 3
    while n <= limit:
        if counts[n] == 1:
            for u in ulam:
                s = u + n
                if s > limit:
                    break
                counts[s] += 1
            ulam.append(n)
        n += 1
    return ulam


def ulam_first(k: int) -> list[int]:
    """First k Ulam numbers. Grows the value-limit as needed."""
    if k <= 0:
        return []
    if k == 1:
        return [1]
    # Empirical a_n ~ 13.52 n; start generously and expand.
    limit = max(32, int(20 * k) + 64)
    while True:
        seq = ulam_upto_value(limit)
        if len(seq) >= k:
            return seq[:k]
        limit *= 2
