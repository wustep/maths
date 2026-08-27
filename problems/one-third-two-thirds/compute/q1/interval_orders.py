#!/usr/bin/env python3
"""Naturally labelled interval orders (2+2-free), exact δ.

A poset is an interval order iff its principal down-sets are totally
ordered by inclusion. Semiorders (also 3+1-free) are already proved.
This census keeps every naturally labelled interval order that is not a
chain, records whether it contains 3+1, and reports min δ.

Complete through n=8. Isolated samples at larger n are not a bound.
"""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))

from posetlib import Poset, balance, pair_counts_fb  # noqa: E402


def contains_three_plus_one(P: Poset) -> bool:
    n = P.n
    # 3+1: a chain a<b<c and an element d incomparable to all three.
    for a in range(n):
        above_a = P.succ[a]
        m = above_a
        while m:
            bbit = m & -m
            b = bbit.bit_length() - 1
            above_b = P.succ[b]
            t = above_b
            while t:
                cbit = t & -t
                c = cbit.bit_length() - 1
                blocked = (1 << a) | (1 << b) | (1 << c) | P.comp[a] | P.comp[b] | P.comp[c]
                if ((1 << n) - 1) & ~blocked:
                    return True
                t ^= cbit
            m ^= bbit
    return False


def generate(n: int):
    """Naturally labelled interval orders: identity is a linear extension
    and down-sets form a chain under inclusion."""
    down = [0] * n

    def rec(k: int, prev_sets: list[int]):
        if k == n:
            yield list(down)
            return
        # down[k] ⊆ {0..k-1}, and {down[0],...,down[k]} is a chain.
        # Also transitivity: if j ∈ down[k] then down[j] ⊆ down[k].
        full = (1 << k) - 1

        def ok(mask: int) -> bool:
            m = mask
            while m:
                lsb = m & -m
                j = lsb.bit_length() - 1
                if down[j] & ~mask:
                    return False
                m ^= lsb
            for prev in prev_sets:
                if not (mask & prev == prev or prev & mask == mask):
                    return False
            return True

        for mask in range(full + 1):
            if ok(mask):
                down[k] = mask
                yield from rec(k + 1, prev_sets + [mask])
                down[k] = 0

    yield from rec(0, [])


def census(nmax: int):
    rows = []
    for n in range(3, nmax + 1):
        n_all = 0
        n_nonchain = 0
        n_not_semi = 0
        n_below13 = 0
        best = None
        best_down = None
        for down in generate(n):
            n_all += 1
            P = Poset(n, down)
            if all(P.succ[i] or P.down[i] for i in range(n)) and all(
                (P.down[i] | P.succ[i] | (1 << i)) == (1 << n) - 1 for i in range(n)
            ):
                # might still be a chain
                pass
            incomp = sum(P.incomp[i].bit_count() for i in range(n))
            if incomp == 0:
                continue
            n_nonchain += 1
            e, C = pair_counts_fb(P)
            num, den, e2, pair, _ = balance(P, C, e)
            g = gcd(num, den)
            num, den = num // g, den // g
            if num * 3 < den:
                n_below13 += 1
            not_semi = contains_three_plus_one(P)
            if not_semi:
                n_not_semi += 1
            if best is None or num * best[1] < best[0] * den:
                best = (num, den, e2, pair, not_semi)
                best_down = down
        row = {
            "n": n,
            "n_natural_interval": n_all,
            "n_nonchain": n_nonchain,
            "n_not_semiorder": n_not_semi,
            "n_below_1_3": n_below13,
            "min_delta": [best[0], best[1]],
            "min_e": best[2],
            "min_is_not_semiorder": best[4],
            "min_down": best_down,
            "complete": True,
        }
        rows.append(row)
        print(
            f"n={n} interval={n_all} nonchain={n_nonchain} "
            f"not_semi={n_not_semi} min {best[0]}/{best[1]} "
            f"below 1/3={n_below13}",
            flush=True,
        )
        if n_below13:
            raise AssertionError(f"interval order below 1/3 at n={n}")
    return rows


def main():
    rows = census(8)
    path = HERE / "interval_orders.json"
    path.write_text(json.dumps({"census": rows}, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
