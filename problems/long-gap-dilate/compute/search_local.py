#!/usr/bin/env python3
"""Local search: minimise max_d g(dA) for |A|=n.

Used as an upper bound on G(p,n). Not a lower bound, not a dent.
"""

from __future__ import annotations

import argparse
import json
import random
import time

from constructions import equally_spaced, jittered_grid, nearest_subgroup, random_set, small_squares
from gaplib import gap, max_gap_dilates, shakan_lower, uniq_mod


def score(A, p):
    g, d = max_gap_dilates(A, p)
    return g, d


def local_search(p: int, n: int, seed: int = 0, steps: int = 2000, restarts: int = 4) -> dict:
    rng = random.Random(seed)
    t0 = time.time()
    starts = [
        equally_spaced(p, n),
        small_squares(p, n),
        nearest_subgroup(p, n)[0],
        jittered_grid(p, n, rng, width=max(1, int((p / n) ** 0.5))),
    ]
    for _ in range(max(0, restarts - 4)):
        starts.append(random_set(p, n, rng))

    best_A = None
    best_g = p
    best_d = 1
    history = []
    for si, A0 in enumerate(starts):
        A = uniq_mod(A0, p)[:n]
        if len(A) < n:
            extra = [x for x in range(p) if x not in A]
            A = A + extra[: n - len(A)]
        cur_g, cur_d = score(A, p)
        Aset = set(A)
        idle = 0
        for st in range(steps):
            if cur_g <= shakan_lower(p, n) + 1e-9:
                break
            # propose: replace a random element by a random outsider
            out_el = rng.choice(A)
            ins_el = rng.randrange(p)
            if ins_el in Aset:
                idle += 1
                continue
            Aset.remove(out_el)
            Aset.add(ins_el)
            trial = list(Aset)
            tg, td = score(trial, p)
            if tg <= cur_g:
                A = trial
                cur_g, cur_d = tg, td
                idle = 0
            else:
                Aset.remove(ins_el)
                Aset.add(out_el)
                idle += 1
            if idle > 80:
                # random kick
                out_el = rng.choice(A)
                ins_el = rng.randrange(p)
                if ins_el not in Aset:
                    Aset.remove(out_el)
                    Aset.add(ins_el)
                    A = list(Aset)
                    cur_g, cur_d = score(A, p)
                idle = 0
        if cur_g < best_g:
            best_g, best_d, best_A = cur_g, cur_d, sorted(A)
        history.append({"start": si, "g": cur_g, "A": sorted(A)})
    return {
        "p": p,
        "n": n,
        "g_upper": best_g,
        "d": best_d,
        "A": best_A,
        "shakan": shakan_lower(p, n),
        "ratio_over_mean": best_g / (p / n),
        "sec": round(time.time() - t0, 4),
        "history_best": min(h["g"] for h in history),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--steps", type=int, default=800)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    n = args.n if args.n is not None else max(2, int(round(args.p**0.5)))
    rec = local_search(args.p, n, seed=args.seed, steps=args.steps)
    print(json.dumps({k: rec[k] for k in rec if k != "history"}))


if __name__ == "__main__":
    main()
