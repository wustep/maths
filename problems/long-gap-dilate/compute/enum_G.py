#!/usr/bin/env python3
"""Exact G(p,n) by enumerating n-sets containing {0,1}. Feasible for small n."""

from __future__ import annotations

import argparse
import itertools
import json
import time

from gaplib import max_gap_dilates, primes_upto, shakan_lower


def G_enum(p: int, n: int) -> dict:
    t0 = time.time()
    if n < 2:
        raise ValueError
    if n == 2:
        g, d = max_gap_dilates([0, 1], p)
        sh = shakan_lower(p, n)
        return {
            "p": p,
            "n": n,
            "G": g,
            "witness": [0, 1],
            "shakan": sh,
            "extra": g - sh,
            "ratio": g * n / p,
            "sec": round(time.time() - t0, 4),
        }
    best = p
    best_A = None
    rest = range(2, p)
    for extra in itertools.combinations(rest, n - 2):
        A = [0, 1, *extra]
        g, _ = max_gap_dilates(A, p)
        if g < best:
            best = g
            best_A = A
            if best <= shakan_lower(p, n) + 1e-9:
                break
    sh = shakan_lower(p, n)
    return {
        "p": p,
        "n": n,
        "G": best,
        "witness": best_A,
        "shakan": sh,
        "extra": best - sh,
        "ratio": best * n / p,
        "sec": round(time.time() - t0, 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--pmax", type=int, default=80)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    out = args.out or f"compute/certs/G_n{args.n}.jsonl"
    with open(out, "w") as f:
        for p in primes_upto(args.pmax):
            if p < args.n + 2:
                continue
            rec = G_enum(p, args.n)
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(
                f"p={p:3d} n={args.n} G={rec['G']:4d} sh={rec['shakan']:7.3f} "
                f"extra={rec['extra']:7.3f} ratio={rec['ratio']:.3f} sec={rec['sec']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
