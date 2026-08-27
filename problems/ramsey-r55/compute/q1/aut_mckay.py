#!/usr/bin/env python3
"""Automorphism-group sizes of the 656 published (5,5,42)-graphs.

Colour refinement, then backtrack. Records |Aut| and whether any graph
has a 7-cycle or a nontrivial involution. Independent of nauty.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import complement, dump_json, parse_graph6

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = Path(__file__).resolve().parent / "certs" / "aut_mckay.json"


def refine(nbr: list[int]) -> list[int]:
    n = len(nbr)
    color = [nbr[i].bit_count() for i in range(n)]
    for _ in range(n + 2):
        keys = []
        for i in range(n):
            cols = []
            m = nbr[i]
            while m:
                b = m & -m
                cols.append(color[b.bit_length() - 1])
                m ^= b
            keys.append((color[i], tuple(sorted(cols))))
        ranks = {k: i for i, k in enumerate(sorted(set(keys)))}
        nxt = [ranks[k] for k in keys]
        if nxt == color:
            return color
        color = nxt
    return color


def aut_group(nbr: list[int], limit: int = 10000) -> dict:
    n = len(nbr)
    col = refine(nbr)
    cells: dict[int, list[int]] = {}
    for i, c in enumerate(col):
        cells.setdefault(c, []).append(i)
    # map image of vertex i; -1 unset
    count = 0
    orders = Counter()
    has_inv = False
    has_7 = False

    def apply_ok(f: list[int], a: int, b: int) -> bool:
        # f[a] = b tentatively: edges among assigned vertices
        for i in range(n):
            if f[i] < 0:
                continue
            e = (nbr[a] >> i) & 1
            ee = (nbr[b] >> f[i]) & 1
            if e != ee:
                return False
        return True

    def rec(f: list[int], used: list[int]) -> None:
        nonlocal count, has_inv, has_7
        if count >= limit:
            return
        # pick unassigned vertex in the smallest cell among remaining
        best_v = -1
        best_opts = None
        remaining_cells = {}
        for i in range(n):
            if f[i] >= 0:
                continue
            remaining_cells.setdefault(col[i], []).append(i)
        if not remaining_cells:
            count += 1
            # cycle type of f
            seen = [False] * n
            lens = []
            for i in range(n):
                if seen[i]:
                    continue
                j = i
                L = 0
                while not seen[j]:
                    seen[j] = True
                    j = f[j]
                    L += 1
                lens.append(L)
            g = 1
            for L in lens:
                g = _lcm(g, L)
            orders[g] += 1
            if any(L == 2 for L in lens):
                has_inv = True
            if any(L == 7 for L in lens):
                has_7 = True
            return
        cell = min(remaining_cells, key=lambda c: len(remaining_cells[c]))
        v = remaining_cells[cell][0]
        # candidates: unused vertices of the same colour
        for w in range(n):
            if used[w] or col[w] != col[v]:
                continue
            if not apply_ok(f, v, w):
                continue
            f[v] = w
            used[w] = 1
            rec(f, used)
            used[w] = 0
            f[v] = -1
            if count >= limit:
                return

    def _lcm(a, b):
        x, y = a, b
        while y:
            x, y = y, x % y
        return a * b // x

    f = [-1] * n
    used = [0] * n
    rec(f, used)
    return {
        "aut": count,
        "capped": count >= limit,
        "n_colors": len(set(col)),
        "has_involution": has_inv and count > 1,
        "has_7cycle": has_7 and count > 1,
        "aut_orders": dict(orders),
    }


def main() -> int:
    t0 = time.time()
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    recs = []
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        for side, g in (("stored", nbr), ("comp", complement(nbr))):
            info = aut_group(g)
            recs.append({"i": i, "side": side, **info})
        if (i + 1) % 40 == 0:
            print(f"progress {i+1}/328", flush=True)
    auts = Counter(r["aut"] for r in recs)
    summary = {
        "n_graphs": len(recs),
        "aut_histogram": {str(k): v for k, v in sorted(auts.items())},
        "n_trivial": sum(1 for r in recs if r["aut"] == 1),
        "n_nontrivial": sum(1 for r in recs if r["aut"] > 1),
        "n_has_involution": sum(1 for r in recs if r["has_involution"]),
        "n_has_7cycle": sum(1 for r in recs if r["has_7cycle"]),
        "n_capped": sum(1 for r in recs if r["capped"]),
        "seconds": round(time.time() - t0, 3),
        "records": recs,
    }
    dump_json(str(OUT), summary)
    print(
        f"graphs={len(recs)} trivial={summary['n_trivial']} "
        f"nontrivial={summary['n_nontrivial']} invol={summary['n_has_involution']} "
        f"c7={summary['n_has_7cycle']} hist={summary['aut_histogram']} "
        f"sec={summary['seconds']}"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
