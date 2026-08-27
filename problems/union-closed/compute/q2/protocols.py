"""Named 2-sample bit protocols for the q2 hunt.

Each returns h(P(X∨Y=1)) for a coupling of Bern(s) and Bern(t).
None of them can beat the {b,1} product-coupling ceiling: h ≤ 1.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entropy import (  # noqa: E402
    a_example4,
    h,
    h_or_example4,
    h_or_example5,
    h_or_indep,
    h_or_maxent,
    pi_example4,
    pi_example5,
)


def pi_half_target(s: float, t: float) -> float:
    """Fréchet-feasible Π(0,0) closest to 1/2 (max binary entropy of OR)."""
    lo = max(0.0, 1.0 - s - t)
    hi = min(1.0 - s, 1.0 - t)
    if hi < lo:
        return max(lo, 0.0)
    target = 0.5
    return min(hi, max(lo, target))


def h_or_half_target(s: float, t: float) -> float:
    return h(1.0 - pi_half_target(s, t))


def a_scaled(t: float, alpha: float) -> float:
    """Scale Example 4's a(t) toward iid (alpha=0) or past it (clip)."""
    return min(1.0, max(0.0, alpha * a_example4(t)))


def pi_scaled_ex4(s: float, t: float, alpha: float) -> float:
    sb, tb = 1.0 - s, 1.0 - t
    aa = a_scaled(s, alpha) * a_scaled(t, alpha)
    return sb * tb + aa * (min(sb, tb) - sb * tb)


def h_or_scaled_ex4(s: float, t: float, alpha: float) -> float:
    return h(1.0 - pi_scaled_ex4(s, t, alpha))


def h_or_named(name: str, s: float, t: float, **kw) -> float:
    if name == "iid":
        return h_or_indep(s, t)
    if name == "ex4":
        return h_or_example4(s, t)
    if name == "ex5":
        return h_or_example5(s, t, kw.get("ell", 1.0))
    if name == "maxent":
        return h_or_maxent(s, t)
    if name == "half":
        return h_or_half_target(s, t)
    if name == "scaled_ex4":
        return h_or_scaled_ex4(s, t, kw.get("alpha", 1.0))
    raise KeyError(name)


def mix_h_or(s: float, t: float, weights: dict[str, float], **kw) -> float:
    """Convex combination of named protocols.  Weights need not be normalized."""
    acc = 0.0
    wsum = 0.0
    for name, w in weights.items():
        if w <= 0.0:
            continue
        acc += w * h_or_named(name, s, t, **kw)
        wsum += w
    if wsum <= 0.0:
        return 0.0
    return acc / wsum
