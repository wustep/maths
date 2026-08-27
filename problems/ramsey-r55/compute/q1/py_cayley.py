#!/usr/bin/env python3
"""Independent Python replay of the smaller q1 Cayley groups (c11c4, c3c15)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

Q1 = Path(__file__).resolve().parent
sys.path.insert(0, str(Q1.parent))
sys.path.insert(0, str(Q1))
from r55lib import dump_json, is_ramsey

from check_groups import mul_c11c4, mul_c3c15
from verify_cayley import cayley_nbr, inv_table

GROUPS = {
    "c11c4": (mul_c11c4, 44),
    "c3c15": (mul_c3c15, 45),
}


def classify(mul, n):
    inv = inv_table(mul, n)
    seen = [False] * n
    pairs, invols = [], []
    for g in range(1, n):
        if seen[g]:
            continue
        h = inv[g]
        if h == g:
            invols.append(g)
            seen[g] = True
        else:
            pairs.append((g, h))
            seen[g] = seen[h] = True
    return pairs, invols, inv


def has_k4(mul, inv, S):
    sl = list(S)
    m = len(sl)
    for a in range(m):
        ga = sl[a]
        for b in range(a + 1, m):
            gb = sl[b]
            if mul(inv[ga], gb) not in S:
                continue
            for c in range(b + 1, m):
                gc = sl[c]
                if mul(inv[ga], gc) not in S or mul(inv[gb], gc) not in S:
                    continue
                for d in range(c + 1, m):
                    gd = sl[d]
                    if (
                        mul(inv[ga], gd) in S
                        and mul(inv[gb], gd) in S
                        and mul(inv[gc], gd) in S
                    ):
                        return True
    return False


def census(name: str) -> dict:
    mul, n = GROUPS[name]
    deg_lo, deg_hi = n - 25, 24
    pairs, invols, inv = classify(mul, n)
    scanned = pruned = hits = 0
    t0 = time.time()
    ch_p = [0] * len(pairs)
    ch_i = [0] * len(invols)

    def S_of():
        S = set()
        for i, bit in enumerate(ch_p):
            if bit:
                S.add(pairs[i][0])
                S.add(pairs[i][1])
        for i, bit in enumerate(ch_i):
            if bit:
                S.add(invols[i])
        return S

    def rec_inv(k, deg):
        nonlocal scanned, pruned, hits
        if deg > deg_hi:
            return
        if k == len(invols):
            if deg < deg_lo:
                return
            scanned += 1
            S = S_of()
            if has_k4(mul, inv, S):
                return
            Sc = set(range(1, n)) - S
            if has_k4(mul, inv, Sc):
                return
            nbr = cayley_nbr(mul, n, S)
            if is_ramsey(nbr):
                hits += 1
                print("HIT", name, "deg", deg, "S", sorted(S), flush=True)
            return
        rem = len(invols) - k
        if deg + rem < deg_lo:
            return
        ch_i[k] = 0
        rec_inv(k + 1, deg)
        ch_i[k] = 1
        S = S_of()
        if has_k4(mul, inv, S):
            pruned += 1
            ch_i[k] = 0
            return
        rec_inv(k + 1, deg + 1)
        ch_i[k] = 0

    def rec_pair(k, deg):
        nonlocal pruned
        if deg > deg_hi:
            return
        if k == len(pairs):
            rec_inv(0, deg)
            return
        rem = len(pairs) - k
        if deg + 2 * rem + len(invols) < deg_lo:
            return
        ch_p[k] = 0
        rec_pair(k + 1, deg)
        ch_p[k] = 1
        S = S_of()
        if has_k4(mul, inv, S):
            pruned += 1
            ch_p[k] = 0
            return
        rec_pair(k + 1, deg + 2)
        ch_p[k] = 0

    rec_pair(0, 0)
    return {
        "group": name,
        "n": n,
        "npairs": len(pairs),
        "ninv": len(invols),
        "scanned": scanned,
        "pruned": pruned,
        "hits": hits,
        "seconds": round(time.time() - t0, 3),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("group", choices=sorted(GROUPS))
    args = ap.parse_args()
    rec = census(args.group)
    out = Path(__file__).resolve().parent / "certs" / f"py_{args.group}.json"
    dump_json(str(out), rec)
    print(rec)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
