"""Cyclic sum covers: A + A = Z/nZ.

Counting: n <= |A|(|A|+1)/2, so |A| >= (-1 + sqrt(1+8n))/2.
"""

from __future__ import annotations

import math
from typing import Iterable


def counting_lower(n: int) -> int:
    # smallest m with m(m+1)/2 >= n
    return math.ceil((-1 + math.sqrt(1 + 8 * n)) / 2)


def ratio(m: int, n: int) -> float:
    return m / math.sqrt(n)


def sumset_size(A: Iterable[int], n: int) -> int:
    S = [0] * n
    A = list({int(a) % n for a in A})
    for i, a in enumerate(A):
        S[(a + a) % n] = 1
        for b in A[i + 1 :]:
            S[(a + b) % n] = 1
    return sum(S)


def is_sum_cover(A: Iterable[int], n: int) -> bool:
    return sumset_size(A, n) == n


def uncovered(A: Iterable[int], n: int) -> list[int]:
    seen = [False] * n
    A = list({int(a) % n for a in A})
    for i, a in enumerate(A):
        seen[(2 * a) % n] = True
        for b in A[i + 1 :]:
            seen[(a + b) % n] = True
    return [x for x, ok in enumerate(seen) if not ok]


def cover_stats(A: Iterable[int], n: int) -> dict:
    A = sorted({int(a) % n for a in A})
    m = len(A)
    cov = sumset_size(A, n)
    return {
        "n": n,
        "m": m,
        "covered": cov,
        "missed": n - cov,
        "ratio": m / math.sqrt(n) if n else float("inf"),
        "counting": counting_lower(n),
        "slack": m - counting_lower(n),
        "ok": cov == n,
    }
