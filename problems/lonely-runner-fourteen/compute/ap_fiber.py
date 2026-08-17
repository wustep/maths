"""Independent exact checker for the ST26 (s,r)-fiber statement.

A vector v in (Z/mZ)^k, m=k+1, is saved if some s,r satisfy
    (s*v[i] + r*(i+1)) % m  not in {0, m-1}  for all i.
N_k = {v : v != 0 and some coordinate is 0}.

This file brute-forces small k and verifies any obstruction emitted by
ap_fiber.c. It is the independently readable witness checker.
"""

from __future__ import annotations

import argparse
import math
import random


def is_unit(a: int, m: int) -> bool:
    return math.gcd(a, m) == 1


def saved(v: list[int], m: int, units: bool = False) -> tuple[int, int] | None:
    k = len(v)
    srange = [s for s in range(m) if (not units or is_unit(s, m))]
    rrange = [r for r in range(m) if (not units or is_unit(r, m))]
    for s in srange:
        for r in rrange:
            ok = True
            for i, val in enumerate(v):
                x = (s * val + r * (i + 1)) % m
                if x == 0 or x == m - 1:
                    ok = False
                    break
            if ok:
                return s, r
    return None


def in_Nk(v: list[int]) -> bool:
    z = v.count(0)
    return 0 < z < len(v)


def brute(k: int, units: bool = False) -> list[int] | None:
    m = k + 1
    # iterate in mixed-radix; skip vectors outside N_k
    n = m**k
    obstruction = None
    n_nk = 0
    n_saved = 0
    v = [0] * k
    for idx in range(n):
        x = idx
        for i in range(k):
            v[i] = x % m
            x //= m
        if not in_Nk(v):
            continue
        n_nk += 1
        w = saved(v, m, units=units)
        if w is None:
            obstruction = v.copy()
            break
        n_saved += 1
    return obstruction, n_nk, n_saved


def sample_check(k: int, n: int, units: bool = False, seed: int = 1) -> int:
    m = k + 1
    rng = random.Random(seed)
    ok = 0
    for _ in range(n):
        while True:
            v = [rng.randrange(m) for _ in range(k)]
            if in_Nk(v):
                break
        if saved(v, m, units=units) is None:
            raise SystemExit(f"UNSAVED {v}")
        ok += 1
    return ok


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--units", action="store_true")
    ap.add_argument("--brute", action="store_true")
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--check", type=str, default="", help="comma vector to test")
    args = ap.parse_args()
    m = args.k + 1
    if args.check:
        v = [int(x) for x in args.check.split(",")]
        assert len(v) == args.k
        w = saved(v, m, units=args.units)
        print(f"v={v} in_Nk={in_Nk(v)} witness={w}")
        raise SystemExit(0 if w else 1)
    if args.samples:
        ok = sample_check(args.k, args.samples, units=args.units)
        print(f"samples {ok}/{args.samples} saved")
    if args.brute:
        est = m**args.k
        if est > 12_000_000:
            raise SystemExit(f"brute refused m^k={est}")
        obst, n_nk, n_saved = brute(args.k, units=args.units)
        if obst is None:
            print(f"NO_OBSTRUCTION brute N_k={n_nk} saved={n_saved}")
        else:
            print(f"OBSTRUCTION {obst}")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
