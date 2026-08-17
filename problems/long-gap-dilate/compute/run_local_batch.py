#!/usr/bin/env python3
"""Local-search upper bounds on G(p, round sqrt p)."""

from __future__ import annotations

import json

from gaplib import primes_upto
from search_local import local_search


def main():
    out = "compute/certs/local_upper.jsonl"
    with open(out, "w") as f:
        for p in primes_upto(120):
            if p < 11:
                continue
            n = max(2, int(round(p**0.5)))
            rec = local_search(p, n, seed=0, steps=400, restarts=6)
            slim = {k: rec[k] for k in rec if k != "history"}
            f.write(json.dumps(slim) + "\n")
            f.flush()
            print(
                f"p={p:3d} n={n:2d} g_up={rec['g_upper']:4d} sh={rec['shakan']:7.2f} "
                f"ratio={rec['ratio_over_mean']:.3f} sec={rec['sec']}",
                flush=True,
            )
    print("wrote", out)


if __name__ == "__main__":
    main()
