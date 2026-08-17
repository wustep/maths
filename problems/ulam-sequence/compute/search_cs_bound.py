#!/usr/bin/env python3
"""Enumerate admissible CS majorant words and record operator-norm bounds.

A length-L admissible word W gives the valid majorant
    a_n <= K_L * C_L^n,   C_L = max ||W||^{1/L},
so for large n one has a_n <= (C_L + eps)^n.  CS used L=15 and the 2-norm
and published 1.454.  This script recomputes small L in Python; larger L
is handled by search_cs_bound.c.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

from cs_matrices import (
    MATS,
    T1,
    T3,
    count_admissible,
    eggleton_root,
    opnorm1,
    opnorm2,
    opnorminf,
    product,
    spectral_radius,
    t3t1sq_root,
    word_str,
)


def enumerate_level(L: int) -> dict:
    """DFS over admissible words; track max 2-norm, 1-norm, inf-norm, geom."""
    t0 = time.perf_counter()
    I = np.eye(4, dtype=np.int64)
    best = {
        "n2": 0.0,
        "n1": 0,
        "ninf": 0,
        "n1inf": 0.0,
        "word2": None,
        "word1": None,
        "wordinf": None,
        "word1inf": None,
    }
    nwords = 0

    def consider(word, A):
        nonlocal nwords
        nwords += 1
        n2 = opnorm2(A)
        n1 = opnorm1(A)
        ninf = opnorminf(A)
        g = math.sqrt(n1 * ninf)
        if n2 > best["n2"]:
            best["n2"] = n2
            best["word2"] = word.copy()
        if n1 > best["n1"]:
            best["n1"] = n1
            best["word1"] = word.copy()
        if ninf > best["ninf"]:
            best["ninf"] = ninf
            best["wordinf"] = word.copy()
        if g > best["n1inf"]:
            best["n1inf"] = g
            best["word1inf"] = word.copy()

    def dfs(depth, last, word, A):
        if depth == L:
            consider(word, A)
            return
        for k in (1, 2, 3):
            if k == 3 and last == 3:
                continue
            word.append(k)
            dfs(depth + 1, k, word, MATS[k] @ A)
            word.pop()

    dfs(0, 0, [], I)
    elapsed = time.perf_counter() - t0
    assert nwords == count_admissible(L), (nwords, count_admissible(L))
    out = {
        "L": L,
        "nwords": nwords,
        "seconds": elapsed,
        "C2": best["n2"] ** (1 / L),
        "C1": best["n1"] ** (1 / L),
        "Cinf": best["ninf"] ** (1 / L),
        "C1inf": best["n1inf"] ** (1 / L),
        "max_n2": best["n2"],
        "max_n1": best["n1"],
        "max_ninf": best["ninf"],
        "max_n1inf": best["n1inf"],
        "word2": word_str(best["word2"]),
        "word1": word_str(best["word1"]),
        "wordinf": word_str(best["wordinf"]),
        "word1inf": word_str(best["word1inf"]),
    }
    return out


def check_cs_extremal_word() -> dict:
    """CS write-up: extremal word W = (T3 T1)^3 (T1 T3)^3 T2 (length 13).

    They quote L=15 in the surrounding sentence; we evaluate the printed
    word on its actual length and also scan nearby paddings.
    """
    w = [3, 1] * 3 + [1, 3] * 3 + [2]
    A = product(w)
    L = len(w)
    out = {
        "word": word_str(w),
        "length": L,
        "n2": opnorm2(A),
        "C2": opnorm2(A) ** (1 / L),
        "n1": opnorm1(A),
        "C1": opnorm1(A) ** (1 / L),
        "rho": spectral_radius(A),
        "rho_root": spectral_radius(A) ** (1 / L),
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--Lmin", type=int, default=1)
    ap.add_argument("--Lmax", type=int, default=12)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "cs_bound_small.json",
    )
    args = ap.parse_args()

    rows = []
    for L in range(args.Lmin, args.Lmax + 1):
        row = enumerate_level(L)
        rows.append(row)
        print(
            f"L={L:2d}  words={row['nwords']:8d}  "
            f"C2={row['C2']:.10f}  C1={row['C1']:.10f}  "
            f"Cinf={row['Cinf']:.10f}  C1inf={row['C1inf']:.10f}  "
            f"w2={row['word2']}  ({row['seconds']:.2f}s)",
            flush=True,
        )

    summary = {
        "eggleton_root": eggleton_root(),
        "t3t1sq_root": t3t1sq_root(),
        "cs_extremal_L15": check_cs_extremal_word(),
        "rows": rows,
    }
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print("wrote", args.out)
    print("Eggleton root", summary["eggleton_root"])
    print("rho(T3 T1^2)^{1/3}", summary["t3t1sq_root"])
    print("CS claimed L=15 word", summary["cs_extremal_L15"])


if __name__ == "__main__":
    main()
