#!/usr/bin/env python3
"""Exact G(p, n=round sqrt p) for small primes."""

from __future__ import annotations

import argparse
import json
import time

from gaplib import primes_upto
from sat_exact import exact_G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmax", type=int, default=47)
    ap.add_argument("--out", type=str, default="compute/certs/sat_G.jsonl")
    args = ap.parse_args()
    t0 = time.time()
    with open(args.out, "w") as f:
        for p in primes_upto(args.pmax):
            if p < 5:
                continue
            n = max(2, int(round(p**0.5)))
            rec = exact_G(p, n)
            slim = {k: rec[k] for k in rec if k != "log"}
            f.write(json.dumps(slim) + "\n")
            f.flush()
            print(
                f"p={p:3d} n={n:2d} G={rec['G']:4} shakan={rec['shakan']:7.3f} "
                f"ratio={rec['ratio_over_mean']} sec={rec['sec']}",
                flush=True,
            )
    print(f"done in {time.time()-t0:.1f}s -> {args.out}")


if __name__ == "__main__":
    main()
