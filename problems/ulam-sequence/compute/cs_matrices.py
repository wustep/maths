"""Clément–Steinerberger 2025 majorant matrices for the Ulam recurrence.

Type I  (T1): a_{n+1} = a_n + a_{n-3}
Type II (T2): a_{n+1} = a_{n-1} + a_{n-2}
Eggleton(T3): a_{n+1} = a_n + a_{n-2}

State vector is (a_n, a_{n-1}, a_{n-2}, a_{n-3})^T.
Admissible words: alphabet {1,2,3} with no two consecutive 3s.
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

T1 = np.array(
    [[1, 0, 0, 1],
     [1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 1, 0]],
    dtype=np.int64,
)
T2 = np.array(
    [[0, 1, 1, 0],
     [1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 1, 0]],
    dtype=np.int64,
)
T3 = np.array(
    [[1, 0, 1, 0],
     [1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 1, 0]],
    dtype=np.int64,
)

MATS = {1: T1, 2: T2, 3: T3}
NAMES = {1: "T1", 2: "T2", 3: "T3"}


def product(word: Iterable[int]) -> np.ndarray:
    acc = np.eye(4, dtype=np.int64)
    for k in word:
        acc = MATS[k] @ acc
    return acc


def opnorm2(A: np.ndarray) -> float:
    """Spectral (2-)norm via SVD of a float copy."""
    return float(np.linalg.norm(np.asarray(A, dtype=np.float64), ord=2))


def opnorm1(A: np.ndarray) -> int:
    return int(np.abs(A).sum(axis=0).max())


def opnorminf(A: np.ndarray) -> int:
    return int(np.abs(A).sum(axis=1).max())


def frobenius(A: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(A, dtype=np.float64), ord="fro"))


def spectral_radius(A: np.ndarray) -> float:
    ev = np.linalg.eigvals(np.asarray(A, dtype=np.float64))
    return float(np.max(np.abs(ev)))


def word_str(word: Iterable[int]) -> str:
    return "".join(NAMES[k][-1] for k in word)


def count_admissible(L: int) -> int:
    """Number of length-L words over {1,2,3} with no consecutive 3s."""
    if L <= 0:
        return 0
    # total_n = 2*total_{n-1} + 2*total_{n-2}, with t1=3, t2=8
    if L == 1:
        return 3
    if L == 2:
        return 8
    a, b = 3, 8
    for _ in range(3, L + 1):
        a, b = b, 2 * b + 2 * a
    return b


def eggleton_root() -> float:
    """Real root of x^3 - x^2 - 1 = 0."""
    # Cardano or numpy
    roots = np.roots([1, -1, 0, -1])
    real = [float(r.real) for r in roots if abs(r.imag) < 1e-12]
    return max(real)


def t3t1sq_root() -> float:
    """rho(T3 T1^2)^{1/3}, CS lower barrier for this method."""
    W = T3 @ T1 @ T1
    return spectral_radius(W) ** (1 / 3)
