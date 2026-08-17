#!/usr/bin/env python3
"""Sanity check of the Si-sum majorant 12(1+log K̃) on random partitions.

Not a proof. Samples increasing n_j and x∈(0,π], compares the left-hand
side of Bedert (16) to 12(1+log K). Exit 0 if every sample stays under.
"""

from __future__ import annotations

import math
import sys

import numpy as np


def si_piece(a: float, b: float) -> float:
    # ∫_a^b sin t / t dt  via scipy-free quadrature
    if b == a:
        return 0.0
    lo, hi = (a, b) if a < b else (b, a)
    # avoid 0
    lo = max(lo, 1e-12)
    t = np.linspace(lo, hi, 64)
    val = np.trapezoid(np.sin(t) / t, t)
    return float(val if a < b else -val)


def one_sample(K: int, rng: np.random.Generator) -> float:
    n = np.cumsum(rng.integers(1, 8, size=K))
    x = float(rng.uniform(0.05, math.pi - 0.05))
    s = 0.0
    njm = 0
    for nj in n:
        s += si_piece(njm * x, nj * x)
        njm = int(nj)
    return abs(s)


def main() -> int:
    rng = np.random.default_rng(0)
    worst = 0.0
    for K in (5, 10, 20, 40, 80):
        bound = 12 * (1 + math.log(K))
        local = 0.0
        for _ in range(80):
            val = one_sample(K, rng)
            local = max(local, val)
            if val > bound:
                print(f"FAIL K={K} val={val} bound={bound}")
                return 1
        worst = max(worst, local / bound)
        print(f"K={K:3d}  max|sum|={local:.3f}  12(1+log K)={bound:.3f}  ratio={local/bound:.3f}")
    print(f"si-group sanity: OK (worst ratio {worst:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
