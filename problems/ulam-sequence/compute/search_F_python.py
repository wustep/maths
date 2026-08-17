#!/usr/bin/env python3
"""Independent Python enumeration of max ||W||_F^2 over admissible words."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from cs_matrices import MATS, count_admissible

HERE = Path(__file__).resolve().parent


def enumerate_F(L: int) -> dict:
    t0 = time.perf_counter()
    I = np.eye(4, dtype=np.int64)
    best = 0
    best_w = None
    nwords = 0

    def dfs(depth, last, word, A):
        nonlocal best, best_w, nwords
        if depth == L:
            nwords += 1
            f2 = int(np.square(A).sum())
            if f2 > best:
                best = f2
                best_w = "".join(str(k) for k in word)
            return
        for k in (1, 2, 3):
            if k == 3 and last == 3:
                continue
            word.append(k)
            dfs(depth + 1, k, word, MATS[k] @ A)
            word.pop()

    dfs(0, 0, [], I)
    assert nwords == count_admissible(L)
    return {
        "L": L,
        "nwords": nwords,
        "seconds": time.perf_counter() - t0,
        "max_F2": best,
        "CF": best ** (0.5 / L),
        "wordF": best_w,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=12)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rec = enumerate_F(args.L)
    out = args.out or HERE / f"cs_F_py_L{args.L}.json"
    out.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
