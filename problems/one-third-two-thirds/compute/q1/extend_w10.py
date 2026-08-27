#!/usr/bin/env python3
"""One-point extensions of W10 that stay width ≤ 3.

Gupta v2's order-14 tail has no width-3 value below 6/17, so a one-point
extension of W10 (n=11) cannot beat 6/17. The search is still run, then
iterated: keep every non-sum extension whose δ is at most 6/17 and grow
to n=15, the first order the published census does not cover.

A conservative one-point extension picks a down-set D and an up-set U
with D ∩ U = ∅ and every d already < every u; the new element sits
above D and below U. Width stays ≤ 3 iff the leftover set has width ≤ 2.
Ordinal-sum extensions (D empty and U empty, or D everything, or U
everything in the dual sense) inherit δ and are recorded separately.
"""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(HERE))

from posetlib import (  # noqa: E402
    Poset,
    W10,
    balance,
    list_ideals,
    pair_counts_fb,
)
from ladders import n_ordinal_summands  # noqa: E402


def up_sets(P: Poset) -> list[int]:
    """Up-sets are complements of ideals of the dual, i.e. filters."""
    n = P.n
    full = (1 << n) - 1
    # A set U is an up-set iff its complement is an ideal.
    return [full ^ I for I in list_ideals(P)]


def width_of(P: Poset, mask: int) -> int:
    if mask == 0:
        return 0
    best = 0
    s = mask
    # iterate submasks
    sub = s
    while True:
        if sub:
            ok = True
            m = sub
            while m:
                lsb = m & -m
                i = lsb.bit_length() - 1
                if P.comp[i] & sub:
                    ok = False
                    break
                m ^= lsb
            if ok:
                c = sub.bit_count()
                if c > best:
                    best = c
        if sub == 0:
            break
        sub = (sub - 1) & s
    return best


def already_below(P: Poset, D: int, U: int) -> bool:
    if D == 0 or U == 0:
        return True
    m = D
    while m:
        lsb = m & -m
        d = lsb.bit_length() - 1
        if (P.succ[d] & U) != U:
            return False
        m ^= lsb
    return True


def add_point(P: Poset, D: int, U: int) -> Poset:
    n = P.n
    down = list(P.down)
    # new element n is above D; everyone in U is above n
    down.append(D)
    u = U
    while u:
        lsb = u & -u
        j = lsb.bit_length() - 1
        down[j] |= (1 << n) | D
        u ^= lsb
    # transitivity: anyone already above someone in U is above n
    for j in range(n):
        if P.down[j] & U:
            down[j] |= (1 << n) | D
    return Poset(n + 1, down)


def delta_of(P: Poset):
    e, C = pair_counts_fb(P)
    num, den, e2, pair, _ = balance(P, C, e)
    g = gcd(num, den)
    return num // g, den // g, e2, pair


def extensions(P: Poset):
    n = P.n
    full = (1 << n) - 1
    ideals = list_ideals(P)
    filters = up_sets(P)
    out = []
    for D in ideals:
        for U in filters:
            if D & U:
                continue
            if not already_below(P, D, U):
                continue
            V = full ^ D ^ U
            if width_of(P, V) > 2:
                continue
            Q = add_point(P, D, U)
            out.append((D, U, Q))
    return out


def classify_sum(P: Poset, D: int, U: int) -> bool:
    """True if the extension is an ordinal sum with a singleton."""
    n = P.n
    full = (1 << n) - 1
    return D == full or U == full or (D == 0 and U == 0)


def search_from_W10(max_n: int = 15, keep_le: tuple[int, int] = (6, 17)):
    start = W10()
    frontier = [(start, "W10")]
    rows = []
    seen_down = {tuple(start.down)}
    kn, kd = keep_le
    n_below = 0
    best = (6, 17, 10, None)

    for n_target in range(11, max_n + 1):
        nxt = []
        n_ext = 0
        n_keep = 0
        n_sum = 0
        local_best = None
        for P, tag in frontier:
            for D, U, Q in extensions(P):
                key = tuple(Q.down)
                if key in seen_down:
                    continue
                seen_down.add(key)
                n_ext += 1
                num, den, e, pair = delta_of(Q)
                is_sum = classify_sum(P, D, U) or n_ordinal_summands(Q) != 1
                if is_sum:
                    n_sum += 1
                rec = {
                    "n": Q.n,
                    "from": tag,
                    "D": D,
                    "U": U,
                    "delta": [num, den],
                    "e": e,
                    "pair": list(pair) if pair else None,
                    "sum": is_sum,
                    "down": Q.down,
                }
                if num * 17 < den * 6:
                    n_below += 1
                    rec["beats_6_17"] = True
                if local_best is None or num * local_best[1] < local_best[0] * den:
                    local_best = (num, den, Q.n, rec)
                if num * best[1] < best[0] * den:
                    best = (num, den, Q.n, rec)
                # keep non-sum extensions with δ ≤ 6/17, and every
                # extension that strictly beats 6/17
                if (not is_sum and num * kd <= den * kn) or num * 17 < den * 6:
                    nxt.append((Q, f"{tag}+({D},{U})"))
                    n_keep += 1
                    rows.append(rec)
        print(
            f"n={n_target} extensions={n_ext} kept={n_keep} sums={n_sum} "
            f"local_best={local_best[0]}/{local_best[1] if local_best else None} "
            f"frontier={len(nxt)}",
            flush=True,
        )
        frontier = nxt
        if not frontier:
            break
    return rows, best, n_below


def main():
    print("one-point extensions of W10, width ≤ 3")
    # First just n=11, complete.
    P = W10()
    ext = extensions(P)
    n11 = []
    best11 = None
    n_below = 0
    for D, U, Q in ext:
        num, den, e, pair = delta_of(Q)
        is_sum = classify_sum(P, D, U)
        rec = {
            "D": D,
            "U": U,
            "delta": [num, den],
            "e": e,
            "sum": is_sum,
            "n_summands": n_ordinal_summands(Q),
            "down": Q.down,
        }
        n11.append(rec)
        if best11 is None or num * best11[1] < best11[0] * den:
            best11 = (num, den, rec)
        if num * 17 < den * 6:
            n_below += 1
    print(
        f"n=11 complete: {len(n11)} width-≤3 extensions, "
        f"best {best11[0]}/{best11[1]}, below 6/17: {n_below}"
    )
    if n_below:
        raise AssertionError("n=11 width-3 below 6/17 contradicts Gupta v2 tail")

    nonsum = [r for r in n11 if not r["sum"]]
    nonsum.sort(key=lambda r: r["delta"][0] / r["delta"][1])
    best_nonsum = nonsum[0] if nonsum else None
    print(
        f"n=11 best non-sum "
        f"{best_nonsum['delta'][0]}/{best_nonsum['delta'][1] if best_nonsum else None}"
    )

    print("iterate non-sum δ≤6/17 extensions toward n=15")
    grown, best, n_below_grown = search_from_W10(15)
    out = {
        "n11_count": len(n11),
        "n11_best": [best11[0], best11[1]],
        "n11_below_6_17": n_below,
        "grown_count": len(grown),
        "grown_best": [best[0], best[1]],
        "grown_best_n": best[2],
        "grown_below_6_17": n_below_grown,
        "n11": [
            {k: v for k, v in r.items() if k != "down"}
            for r in n11
            if (not r["sum"]) or r["delta"] == [6, 17]
        ],
        "grown": [{k: v for k, v in r.items() if k != "down"} for r in grown],
    }
    if best[3] is not None:
        out["grown_best_down"] = best[3]["down"]
        out["grown_best_record"] = {k: v for k, v in best[3].items() if k != "down"}
    path = HERE / "extend_w10.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path}")
    print(
        f"grown best {best[0]}/{best[1]} at n={best[2]}; "
        f"below 6/17: {n_below_grown}"
    )


if __name__ == "__main__":
    main()
