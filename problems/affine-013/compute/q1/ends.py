"""Second count of T: hooks from every point, not fibres at z.

For each a in S and d>0:
  N2(a): a+d and a+3d both in S   ({0,1,3} starting at a)
  N1(a): a+2d and a+3d both in S   ({0,2,3} starting at a)

Then T(S) = n + sum_a (N1(a)+N2(a)). Each nontrivial ordered triple
is counted once, at its left-most point among {x,y}.
"""

from __future__ import annotations

from typing import Iterable


def n1_n2(pts: Iterable[int]) -> dict[int, tuple[int, int]]:
    s = set(pts)
    out: dict[int, tuple[int, int]] = {}
    for a in s:
        n1 = n2 = 0
        # 3d = p-a > 0 with p in S
        for p in s:
            if p <= a or (p - a) % 3:
                continue
            d = (p - a) // 3
            if a + d in s:
                n2 += 1
            if a + 2 * d in s:
                n1 += 1
        out[a] = (n1, n2)
    return out


def t_from_hooks(pts: Iterable[int]) -> int:
    s = list(pts)
    return len(s) + sum(n1 + n2 for n1, n2 in n1_n2(s).values())


def end_scores(pts: Iterable[int]) -> tuple[int, int]:
    """(N1+N2 at min, N1+N2 at max)."""
    s = list(pts)
    hooks = n1_n2(s)
    lo, hi = min(s), max(s)
    return sum(hooks[lo]), sum(hooks[hi])
