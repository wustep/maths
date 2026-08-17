#!/usr/bin/env python3
"""Local search for thin cyclic sum covers.

State: a set A of exact size m. Score = number of covered residues.
Swap one element for an outsider, accept improvements and rare sideways moves.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, counting_lower
from constructions import two_ap
from singer import singer_difference_set, is_prime

BEL = math.sqrt(8 / 3)


def covered_count(A, n):
    seen = bytearray(n)
    Al = list(A)
    for i, a in enumerate(Al):
        seen[(a + a) % n] = 1
        for b in Al[i + 1 :]:
            seen[(a + b) % n] = 1
    return int(sum(seen)), seen


def search(n, m, seed=0, steps=20000):
    rng = random.Random(seed)
    # start: two_ap truncated / padded
    base = two_ap(n)
    if len(base) >= m:
        A = set(base[:m])
        # prefer 0
        A.add(0)
        while len(A) > m:
            A.remove(max(A))
    else:
        A = set(base)
        while len(A) < m:
            A.add(rng.randrange(n))
    cov, seen = covered_count(A, n)
    best = cov
    best_A = set(A)
    universe = list(range(n))
    for t in range(steps):
        if cov == n:
            break
        out = rng.choice(tuple(A))
        inn = rng.randrange(n)
        if inn in A:
            continue
        A.remove(out)
        A.add(inn)
        new, seen2 = covered_count(A, n)
        if new >= cov or rng.random() < 0.02:
            cov = new
            seen = seen2
            if cov > best:
                best = cov
                best_A = set(A)
        else:
            A.remove(inn)
            A.add(out)
    st = cover_stats(best_A, n)
    st.update(target_m=m, steps=steps, seed=seed)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="31,57,72,91,133,156,183")
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--out", default="compute/local_search.json")
    args = ap.parse_args()
    rows = []
    for n in [int(x) for x in args.ns.split(",")]:
        c0 = counting_lower(n)
        # try a few sizes from counting up to just below BEL
        bel_m = math.floor(BEL * math.sqrt(n) - 1e-9)
        sizes = sorted(set([c0, c0 + 1, (c0 + bel_m) // 2, bel_m]))
        sizes = [m for m in sizes if m >= c0]
        for m in sizes:
            best = None
            for sd in range(3):
                st = search(n, m, seed=sd, steps=args.steps)
                if best is None or (st["covered"], -st["m"]) > (
                    best["covered"],
                    -best["m"],
                ):
                    best = st
                if st["ok"]:
                    break
            print(
                f"n={n} m={m} covered={best['covered']} ok={best['ok']} "
                f"ratio={best['ratio']:.4f} count={c0} bel_m={bel_m}",
                flush=True,
            )
            rows.append(
                {k: best[k] for k in ("n", "m", "covered", "ok", "ratio", "counting")}
            )
            if best["ok"]:
                # no need to try larger m
                break
    Path(args.out).write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
