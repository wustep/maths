#!/usr/bin/env python3
"""Random cyclic generators t*(1,a,b,c,d) in Z/n, n around 368.

Same min-max circular distance test as the geometric family.
"""

from __future__ import annotations

import random
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def k_of_gen(n: int, gen: tuple[int, ...]) -> int:
    best = n
    for t in range(1, n):
        mx = 0
        for g in gen:
            x = (t * g) % n
            d = x if x <= n - x else n - x
            if d > mx:
                mx = d
                if mx >= best:
                    break
        if mx < best:
            best = mx
    return best


def main() -> None:
    rng = random.Random(2)
    t0 = time.time()
    hits = []
    best_rows = []
    for n in range(368, 401):
        need = (2 * n + 6) // 7
        best = (-1, None)
        # geometric already searched; try random 5-tuples with first coord 1
        for _ in range(80):
            gen = (1, rng.randrange(n), rng.randrange(n), rng.randrange(n), rng.randrange(n))
            k = k_of_gen(n, gen)
            if k > best[0]:
                best = (k, gen)
            if k >= need:
                hits.append((n, gen, k, need))
                print(f"HIT n={n} gen={gen} k={k}", flush=True)
        best_rows.append((n, best[0], best[1], need, n / best[0] if best[0] else None))
        print(f"n={n} best_k={best[0]} need={need} gen={best[1]}", flush=True)
    (HERE / "random_gen.txt").write_text(
        f"hits {len(hits)}\nseconds {time.time()-t0:.1f}\n"
        + "\n".join(str(h) for h in hits)
        + "\n# best\n"
        + "\n".join(str(r) for r in best_rows)
        + "\n"
    )
    print(f"hits={len(hits)} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
