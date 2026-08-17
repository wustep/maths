"""Additive energy E(S, 2S) = sum_d r_{S-S}(d) r_{S-S}(2d).

T^2 <= n E(S,2S) (Aaronson Lemma 2.3). If E is maximised by an
interval then T <= sqrt(n E(I,2I)) ~ n^2 / sqrt(6), which would
move 3/4 -> 0.408. This file checks the small-n energy picture
and records the exact interval energy.
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import t_count  # noqa: E402


def diff_rep(s: list[int]) -> dict[int, int]:
    r: dict[int, int] = {}
    for x in s:
        for y in s:
            d = x - y
            r[d] = r.get(d, 0) + 1
    return r


def energy_2(s: list[int]) -> int:
    r = diff_rep(s)
    return sum(c * r.get(2 * d, 0) for d, c in r.items())


def interval_energy(n: int) -> int:
    # r(d) = n-|d| for |d|<n
    e = 0
    for d in range(-(n - 1), n):
        rd = n - abs(d)
        r2 = n - abs(2 * d) if abs(2 * d) < n else 0
        e += rd * r2
    return e


def scan(n: int, dmax: int) -> tuple[int, list[int], int]:
    best_e = interval_energy(n)
    best_s = list(range(n))
    best_t = t_count(best_s)
    for comb in itertools.combinations(range(1, dmax + 1), n - 1):
        s = [0] + list(comb)
        e = energy_2(s)
        if e > best_e:
            best_e = e
            best_s = s
            best_t = t_count(s)
    return best_e, best_s, best_t


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=8)
    ap.add_argument("--dmult", type=int, default=3)
    args = ap.parse_args()
    print("n E_I E_max_found T_at_Emax T_I E_I/n^3 sqrt(n E_I)/n^2")
    for n in range(1, args.nmax + 1):
        ei = interval_energy(n)
        dmax = n if n <= 2 else min(n * args.dmult, 22)
        em, sm, tm = scan(n, dmax)
        print(
            f"{n} {ei} {em} {tm} {t_count(range(n))} "
            f"{ei/(n**3):.5f} {(n*ei)**0.5/(n*n):.5f} set={sm}",
            flush=True,
        )


if __name__ == "__main__":
    main()
