#!/usr/bin/env python3
"""QP-only lifts: same Hou–Zhao kernels, no outer optimization."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_kernels import evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parent


def load_r8():
    ns: dict = {}
    exec((ROOT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    ker, lam = ns["stored_candidates"]()[8]
    return np.asarray(ker, dtype=float), np.asarray(lam, dtype=float)


def refine_m(kernels: np.ndarray, factor: int) -> np.ndarray:
    return np.repeat(kernels / factor, factor, axis=1)


def main():
    ker, lam = load_r8()
    for L in range(4, 13):
        evaluate(ker, lam, L, tag=f"fast-r8-m32-L{L}")
    for fac in (2, 3, 4):
        kf = refine_m(ker, fac)
        for L in (4, 5, 6, 8):
            evaluate(kf, lam, L, tag=f"fast-r8-m{kf.shape[1]}-L{L}")
    # also replay R=1 and R=3 at larger L
    ns: dict = {}
    exec((ROOT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    cands = ns["stored_candidates"]()
    for R in (1, 3, 6):
        k, l = cands[R]
        for L in (4, 6, 8):
            evaluate(k, l, L, tag=f"fast-R{R}-m32-L{L}")
    print("done")


if __name__ == "__main__":
    main()
