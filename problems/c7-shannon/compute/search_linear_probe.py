#!/usr/bin/env python3
"""Sample random 3-dimensional F7-codes and measure residual extension."""

from __future__ import annotations

import itertools
import random
import time
from pathlib import Path

from c7_common import N, encode, format_word, greedy_mis_fast, residual_of
from search_linear import is_good, subspace
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent


def random_rows(rng: random.Random):
    while True:
        rows = tuple(tuple(rng.randrange(N) for _ in range(5)) for _ in range(3))
        # crude rank check: not all rows in a 2-dim space
        if rows[0] == (0, 0, 0, 0, 0):
            continue
        return rows


def main() -> None:
    rng = random.Random(3)
    t0 = time.time()
    n_good = 0
    best = 0
    lines = []
    tried = 0
    while n_good < 30 and tried < 4000:
        tried += 1
        rows = random_rows(rng)
        if not is_good(rows):
            continue
        pts = subspace(rows)
        if len(set(pts)) != 343:
            continue
        n_good += 1
        residual = residual_of(pts)
        ext = greedy_mis_fast(residual)
        total = 343 + len(ext)
        print(f"good={n_good} res={len(residual)} ext={len(ext)} total={total}", flush=True)
        lines.append(f"{rows} res={len(residual)} ext={len(ext)} total={total}")
        if total > best:
            best = total
            if total >= 368:
                R = sorted(set(pts) | set(ext))
                if first_conflict(R) is None:
                    out = HERE / f"R{len(R)}_linear.txt"
                    out.write_text("\n".join(format_word(v) for v in R) + "\n")
                    print(f"WROTE {out}")
    (HERE / "linear_probe.txt").write_text(
        f"tried {tried}\ngood {n_good}\nbest {best}\nseconds {time.time()-t0:.1f}\n"
        + "\n".join(lines)
        + "\n"
    )
    print(f"done tried={tried} good={n_good} best={best} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
