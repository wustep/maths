#!/usr/bin/env python3
"""Evaluate constructions: upper bounds on G(p,n) / (p/n). Residue unless ~2."""

from __future__ import annotations

import argparse
import json
import random
import time

from constructions import (
    equally_spaced,
    geometric,
    jittered_grid,
    nearest_subgroup,
    random_set,
    small_squares,
    subgroup,
)
from gaplib import max_gap_dilates, primes_upto, shakan_lower


def eval_one(p, n, A, tag):
    g, d = max_gap_dilates(A, p)
    return {
        "tag": tag,
        "p": p,
        "n": n,
        "g": g,
        "d": d,
        "shakan": shakan_lower(p, n),
        "ratio": g * n / p,
        "ratio_sqrt": g / (p**0.5),
        "A": A,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmax", type=int, default=200)
    ap.add_argument("--out", type=str, default="compute/certs/constructions.jsonl")
    args = ap.parse_args()
    rng = random.Random(1)
    t0 = time.time()
    rows = []
    for p in primes_upto(args.pmax):
        if p < 5:
            continue
        n = max(2, int(round(p**0.5)))
        cands = [
            ("equal", equally_spaced(p, n)),
            ("squares", small_squares(p, n)),
            ("geom", geometric(p, n)),
            ("sub", nearest_subgroup(p, n)[0]),
            ("jitter", jittered_grid(p, n, rng)),
        ]
        # several random
        for i in range(3):
            cands.append((f"rand{i}", random_set(p, n, rng)))
        # exact subgroup if available near n
        for k in (n - 1, n, n + 1):
            if k >= 2:
                H = subgroup(p, k)
                if H is not None:
                    cands.append((f"H{k}", H))
        best = None
        for tag, A in cands:
            rec = eval_one(p, len(A), A, tag)
            rows.append({k: rec[k] for k in rec if k != "A"})
            if best is None or rec["g"] < best["g"]:
                best = rec
        print(
            f"p={p:4d} n={n:3d} sh={shakan_lower(p,n):7.2f} "
            f"best={best['tag']:8s} g={best['g']:4d} ratio={best['ratio']:.3f}",
            flush=True,
        )
    with open(args.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {args.out} ({len(rows)} rows) in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
