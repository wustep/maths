#!/usr/bin/env python3
"""Max |det| of n×n Hankel matrices with small integer entries.

Erdélyi Lemma 3.5 uses a general Hadamard bound  M^{n-1} n^{n/2}  on an
invertible window matrix. Consecutive b-windows of a bounded integer
sequence form a Hankel matrix. If max|det Hankel| is only C^n, the
(2d)^{d} factor in log q becomes exp(O(d)) and Bedert's d log d upgrades
to d, i.e. Z(N) ≥ c log log N.

This script enumerates small n and reports the growth. Residue unless a
proof appears.
"""

from __future__ import annotations

import itertools
import math
import sys

import numpy as np


def max_hankel_det(n: int, alphabet: tuple[int, ...], cap: int | None = None) -> tuple[int, int]:
    """Return (max_abs_det, n_checked). Exhaustive if alphabet^{2n-1} is small."""
    width = 2 * n - 1
    space = len(alphabet) ** width
    if cap is not None and space > cap:
        return -1, space
    best = 0
    for seq in itertools.product(alphabet, repeat=width):
        H = np.empty((n, n), dtype=np.int64)
        for i in range(n):
            for j in range(n):
                H[i, j] = seq[i + j]
        d = int(round(np.linalg.det(H.astype(float))))
        # exact integer det for tiny n via numpy is ok up to n~7 for |a|<=2
        if abs(d) > best:
            best = abs(d)
    return best, space


def sample_hankel_det(n: int, alphabet: tuple[int, ...], trials: int, rng: np.random.Generator) -> int:
    best = 0
    alpha = np.array(alphabet, dtype=np.int64)
    width = 2 * n - 1
    for _ in range(trials):
        seq = rng.choice(alpha, size=width)
        H = np.empty((n, n), dtype=np.float64)
        for i in range(n):
            H[i, :] = seq[i : i + n]
        d = abs(float(np.linalg.det(H)))
        if d > best:
            best = d
    return int(round(best))


def main() -> int:
    rng = np.random.default_rng(1)
    print("alphabet {0,1}")
    print(f"{'n':>3} {'max|det|':>12} {'Hadamard n^{n/2}':>18} {'ratio':>10} {'method':>10}")
    for n in range(1, 8):
        cap = 3_000_000
        best, space = max_hankel_det(n, (0, 1), cap=cap)
        method = "exact" if best >= 0 else "sample"
        if best < 0:
            best = sample_hankel_det(n, (0, 1), trials=80_000, rng=rng)
        had = n ** (n / 2)
        print(f"{n:3d} {best:12d} {had:18.3e} {best / max(had,1):10.4f} {method:>10}")

    print("\nalphabet {-2,-1,0,1,2}  (S^{**} scale for S={0,1})")
    print(f"{'n':>3} {'max|det|':>14} {'Hadamard (2√n)^n':>20} {'method':>10}")
    for n in range(1, 6):
        cap = 2_000_000
        best, space = max_hankel_det(n, (-2, -1, 0, 1, 2), cap=cap)
        method = "exact" if best >= 0 else "sample"
        if best < 0:
            best = sample_hankel_det(n, (-2, -1, 0, 1, 2), trials=40_000, rng=rng)
        had = (2 * math.sqrt(n)) ** n
        print(f"{n:3d} {best:14d} {had:20.3e} {method:>10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
