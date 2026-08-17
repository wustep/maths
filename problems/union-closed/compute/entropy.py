"""Binary-entropy primitives for Gilmer / Sawin / Yu–Cambie / Liu couplings.

All logs are base 2.  Entropy of the zero/one Bernoullis is 0.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

LN2 = math.log(2)


def h(p: float) -> float:
    """Binary entropy in bits.  Continuous at {0,1}."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    q = 1.0 - p
    return -(p * math.log(p) + q * math.log(q)) / LN2


def h_or_indep(s: float, t: float) -> float:
    """h(s ∨ t) under independent Bernoullis:  P(s∨t=0) = (1-s)(1-t)."""
    return h(1.0 - (1.0 - s) * (1.0 - t))


def h_or_maxent(s: float, t: float) -> float:
    """Sawin max-entropy OR: P(s∨t=1) = s ∨ t ∨ min(s+t, 1/2)."""
    return h(max(s, t, min(s + t, 0.5)))


def a_example4(t: float) -> float:
    """Liu Example 4: a(t) maximising h(Π_{t,t}(0,0))."""
    if t <= 0.0:
        return 0.0
    if t >= 0.5:
        return 1.0
    thresh = 1.0 - 1.0 / math.sqrt(2.0)
    if t <= thresh:
        return 0.0
    tbar = 1.0 - t
    num = 1.0 - 2.0 * tbar * tbar
    den = 2.0 * t * tbar
    if num <= 0.0:
        return 0.0
    return math.sqrt(num / den)


def pi_example4(s: float, t: float) -> float:
    """Π_{s,t}(0,0) for Liu Example 4."""
    sb, tb = 1.0 - s, 1.0 - t
    return sb * tb + a_example4(s) * a_example4(t) * (min(sb, tb) - sb * tb)


def h_or_example4(s: float, t: float) -> float:
    return h(1.0 - pi_example4(s, t))


def pi_example5(s: float, t: float, l: float = 1.0) -> float:
    """Example 5 with f(x) = l x (1-x).  Π(0,0) = s̄ t̄ + f(s̄) f(t̄)."""
    sb, tb = 1.0 - s, 1.0 - t
    fs = l * sb * (1.0 - sb)
    ft = l * tb * (1.0 - tb)
    # Feasibility: 0 ≤ f(s̄) ≤ s ∧ s̄
    return sb * tb + fs * ft


def h_or_example5(s: float, t: float, l: float = 1.0) -> float:
    return h(1.0 - pi_example5(s, t, l))


def mean_atoms(values: Sequence[float], weights: Sequence[float]) -> float:
    return sum(v * w for v, w in zip(values, weights))


def entropy_atoms(values: Sequence[float], weights: Sequence[float]) -> float:
    return sum(w * h(v) for v, w in zip(values, weights))


def pairwise_expectation(
    values: Sequence[float],
    weights: Sequence[float],
    fn,
) -> float:
    """E[fn(S,T)] for an atomic law, S,T iid."""
    acc = 0.0
    n = len(values)
    for i in range(n):
        for j in range(n):
            acc += weights[i] * weights[j] * fn(values[i], values[j])
    return acc


def mixture_pairwise(
    atoms0: Sequence[float],
    w0: Sequence[float],
    atoms1: Sequence[float],
    w1: Sequence[float],
    q: float,
    fn,
) -> float:
    """E[fn(S,R)] under the 2-mixture of iid laws q P1⊗P1 + (1-q) P0⊗P0."""
    return (1.0 - q) * pairwise_expectation(atoms0, w0, fn) + q * pairwise_expectation(
        atoms1, w1, fn
    )


def mixture_mean(
    atoms0: Sequence[float],
    w0: Sequence[float],
    atoms1: Sequence[float],
    w1: Sequence[float],
    q: float,
) -> float:
    return (1.0 - q) * mean_atoms(atoms0, w0) + q * mean_atoms(atoms1, w1)


def mixture_entropy(
    atoms0: Sequence[float],
    w0: Sequence[float],
    atoms1: Sequence[float],
    w1: Sequence[float],
    q: float,
) -> float:
    return (1.0 - q) * entropy_atoms(atoms0, w0) + q * entropy_atoms(atoms1, w1)
