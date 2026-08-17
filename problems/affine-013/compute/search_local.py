"""Hill-climb / random mutation around the interval and {0,1,3}-seeds."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import affine_normalise, interval_t, t_count  # noqa: E402


def mutate(pts: list[int], dcap: int, rng: random.Random) -> list[int]:
    s = set(pts)
    n = len(s)
    kind = rng.randrange(3)
    if kind == 0 and n >= 2:
        # move a non-zero point
        victims = [p for p in s if p != min(s)]
        v = rng.choice(victims)
        s.remove(v)
        for _ in range(20):
            nxt = rng.randrange(0, dcap + 1)
            if nxt not in s:
                s.add(nxt)
                break
        else:
            s.add(v)
    elif kind == 1:
        # swap a point for a neighbour hole
        holes = [i for i in range(0, dcap + 1) if i not in s]
        if holes and s:
            s.remove(rng.choice(tuple(s)))
            s.add(rng.choice(holes))
    else:
        # translate one point by ±1, ±2, ±3
        if s:
            v = rng.choice(tuple(s))
            delta = rng.choice([-3, -2, -1, 1, 2, 3])
            w = v + delta
            if 0 <= w <= dcap and w not in s:
                s.remove(v)
                s.add(w)
    if len(s) != n:
        return pts
    return sorted(s)


def climb(n: int, dcap: int, restarts: int, steps: int, seed: int) -> dict:
    rng = random.Random(seed)
    interval = list(range(n))
    best_t = interval_t(n)
    best_s = interval
    history = []

    seeds = [interval]
    # {0,1,3} union an interval
    if n >= 3:
        seeds.append(sorted(set(range(n - 3)) | {0, 1, 3}))
        seeds.append(list(range(n - 1)) + [n])
        seeds.append(list(range(n - 1)) + [n + 1])
        seeds.append(list(range(n - 1)) + [2 * n])
        # two equal blocks
        a = n // 2
        seeds.append(list(range(a)) + list(range(a + 2, a + 2 + n - a)))
        seeds.append(list(range(a)) + list(range(3 * a, 3 * a + n - a)))

    for r in range(restarts):
        if r < len(seeds):
            cur = [p for p in seeds[r] if 0 <= p <= dcap]
            # pad / trim
            x = 0
            while len(cur) < n:
                if x not in cur:
                    cur.append(x)
                x += 1
            cur = sorted(cur)[:n]
        else:
            cur = sorted(rng.sample(range(dcap + 1), n))
        ct = t_count(cur)
        for _ in range(steps):
            nxt = mutate(cur, dcap, rng)
            nt = t_count(nxt)
            if nt >= ct:
                cur, ct = nxt, nt
                if ct > best_t:
                    best_t = ct
                    best_s = list(affine_normalise(cur))
                    history.append({"T": best_t, "S": best_s})
    return {
        "n": n,
        "dcap": dcap,
        "T_best": best_t,
        "T_interval": interval_t(n),
        "ratio": best_t / (n * n),
        "S": list(affine_normalise(best_s)),
        "improvements": history,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=3)
    ap.add_argument("--nmax", type=int, default=40)
    ap.add_argument("--dmult", type=int, default=5)
    ap.add_argument("--restarts", type=int, default=30)
    ap.add_argument("--steps", type=int, default=800)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    rows = []
    for n in range(args.nmin, args.nmax + 1):
        rec = climb(n, max(n * args.dmult, n + 8), args.restarts, args.steps, args.seed + n)
        rows.append(rec)
        print(
            f"n={n:2d} T={rec['T_best']:5d} I={rec['T_interval']:5d} "
            f"ratio={rec['ratio']:.5f} beat={rec['T_best']>rec['T_interval']} "
            f"S={rec['S'][:20]}{'...' if len(rec['S'])>20 else ''}",
            flush=True,
        )
    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
