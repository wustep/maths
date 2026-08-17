#!/usr/bin/env python3
"""Naturally labelled posets of width >= 3, orders 5..10.

Every unlabelled poset appears as a naturally labelled one (relabel by a
linear extension), so the minimum δ among naturally labelled width-3
posets is the unlabelled minimum.

Generation: start from the empty poset; add a new *maximal* element whose
down-set is an order ideal. Width stays <= 3 iff the open complement of
that ideal has width <= 2.

Pair probabilities use the bitmask forward-backward counter, independently
rechecked on every record-tying or record-breaking poset by the mins
recursion.
"""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from posetlib import (
    Poset,
    balance,
    count_le_mins,
    pair_counts_by_adding,
    pair_counts_fb,
)


def ideals(down: list[int]) -> list[int]:
    n = len(down)
    out = [0]
    for mask in range(1, 1 << n):
        ok = True
        m = mask
        while m:
            lsb = m & -m
            i = lsb.bit_length() - 1
            if down[i] & ~mask:
                ok = False
                break
            m ^= lsb
        if ok:
            out.append(mask)
    return out


def width_of_set(down: list[int], mask: int) -> int:
    """Exact width of the induced subposet on ``mask`` (n<=10)."""
    if mask == 0:
        return 0
    # largest antichain inside mask
    n = len(down)
    # comparability inside mask
    best = 1
    sub = mask
    # iterate submasks of mask
    s = sub
    while True:
        if s:
            ok = True
            m = s
            while m:
                lsb = m & -m
                i = lsb.bit_length() - 1
                # any comparable partner in s?
                # partners of i that are < i:
                if down[i] & s:
                    ok = False
                    break
                # partners > i: someone j in s with i in down[j]
                # check while scanning
                m ^= lsb
            if ok:
                # still need i < j comparabilities: if i in down[j] for j in s
                m = s
                while m and ok:
                    lsb = m & -m
                    j = lsb.bit_length() - 1
                    if down[j] & s:
                        ok = False
                    m ^= lsb
            if ok:
                c = s.bit_count()
                if c > best:
                    best = c
        if s == 0:
            break
        s = (s - 1) & sub
    return best


def width_of_set_fast(down: list[int], mask: int) -> int:
    """Width of the induced subposet on ``mask``. n<=12, so O(|S|^3) is fine.

    We only need the exact width to cap at 3, so we stop at 3.
    """
    if mask == 0:
        return 0
    els = []
    m = mask
    while m:
        lsb = m & -m
        els.append(lsb.bit_length() - 1)
        m ^= lsb
    k = len(els)
    if k == 1:
        return 1
    # pairwise incomparable?
    inc = [[False] * k for _ in range(k)]
    has_inc = False
    for a in range(k):
        ia = els[a]
        for b in range(a + 1, k):
            ib = els[b]
            if ((down[ia] >> ib) & 1) == 0 and ((down[ib] >> ia) & 1) == 0:
                inc[a][b] = inc[b][a] = True
                has_inc = True
    if not has_inc:
        return 1
    for a in range(k):
        for b in range(a + 1, k):
            if not inc[a][b]:
                continue
            for c in range(b + 1, k):
                if inc[a][c] and inc[b][c]:
                    return 3
    return 2


def census(max_n: int, min_n: int = 5):
    # each node: (down, width)
    # we only keep width <= 3
    level = [([], 0)]
    summary = []
    records = []

    for n in range(1, max_n + 1):
        nxt = []
        for down, w in level:
            full = (1 << len(down)) - 1
            for I in ideals(down):
                # new antichains involving n: {n} ∪ A, A antichain in complement
                comp = full ^ I
                wc = width_of_set_fast(down, comp)
                nw = max(w, 1 + wc)
                if nw <= 3:
                    nxt.append((down + [I], nw))
        level = nxt
        n_nat = len(level)
        n_w3 = sum(1 for _, w in level if w == 3)
        print(f"n={n}: naturally labelled {n_nat}  width=3 {n_w3}", flush=True)
        if n < min_n:
            continue

        min_num, min_den = 1, 2  # track min δ among width=3
        min_examples = []
        n_checked = 0
        n_below_1439 = 0
        n_below_13 = 0
        worst = []

        for down, w in level:
            if w < 3:
                continue
            P = Poset(n, down)
            e, C = pair_counts_fb(P)
            num, den, _, pair, _ = balance(P, C, e)
            n_checked += 1
            # compare num/den vs min_num/min_den
            if num * min_den < min_num * den:
                min_num, min_den = num, den
                min_examples = [(down, e, pair, num, den)]
            elif num * min_den == min_num * den:
                if len(min_examples) < 5:
                    min_examples.append((down, e, pair, num, den))
            if num * 39 < den * 14:
                n_below_1439 += 1
                worst.append((num, den, e, pair, down))
            if num * 3 < den:
                n_below_13 += 1

        g = gcd(min_num, min_den)
        rec = {
            "n": n,
            "n_natural": n_nat,
            "n_width3": n_w3,
            "n_checked": n_checked,
            "min_delta": [min_num // g, min_den // g],
            "n_below_14_39": n_below_1439,
            "n_below_1_3": n_below_13,
            "min_examples_e_pair": [
                {"e": e, "pair": list(pair) if pair else None, "covers": _covers(down)}
                for down, e, pair, _, _ in min_examples[:3]
            ],
        }
        print(
            f"    width3 checked={n_checked} min δ={rec['min_delta'][0]}/{rec['min_delta'][1]}"
            f"  <14/39: {n_below_1439}  <1/3: {n_below_13}",
            flush=True,
        )
        if worst:
            print("    *** beat 14/39 ***", worst[0][:4], flush=True)
        summary.append(rec)
        records.append(rec)

    return summary


def _covers(down):
    n = len(down)
    P = Poset(n, down)
    cov = []
    for i in range(n):
        for j in range(n):
            if ((P.succ[i] >> j) & 1) == 0:
                continue
            is_c = True
            for k in range(n):
                if ((P.succ[i] >> k) & 1) and ((P.succ[k] >> j) & 1):
                    is_c = False
                    break
            if is_c:
                cov.append((i, j))
    return cov


def main():
    max_n = 10
    if len(sys.argv) > 1:
        max_n = int(sys.argv[1])
    summary = census(max_n)
    path = Path(__file__).resolve().parent / "width3_census.json"
    path.write_text(json.dumps({"census": summary}, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
