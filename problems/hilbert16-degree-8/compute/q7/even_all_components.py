#!/usr/bin/env python3
"""Count fixed-odd even-split components of every published M-collection.

q7/even_components.py only seeds the five published (19,3) collections.
The hole-map M-scheme <5 u 1<6> u 1<9>> sits on the (7,15) row, next to
two published T-curves.  Even twists keep (p,n), so those two components
are the next place to look for that hole.
"""
from __future__ import annotations

import json
import os
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import even_walk as ew


def count_mask(mask, adj):
    @lru_cache(maxsize=None)
    def count(m):
        if not m:
            return 1
        bit = m & -m
        v = bit.bit_length() - 1
        rest = m ^ bit
        return count(rest) + count(rest & adj[v])
    return count(mask), count.cache_info().currsize


def main():
    sys.setrecursionlimit(10000)
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = ew.even_mask(sp)
    key = {x.key: i for i, x in enumerate(sp)}
    rows = []
    for claimed, rec in sorted(json.load(
            open("certs/mcert_collections.json")).items()):
        ids = []
        ok = True
        for p in rec["collection"]:
            t = tuple(tuple(v) for v in p)
            k = t if t[0] < t[-1] else t[::-1]
            if k not in key:
                ok = False
                break
            ids.append(key[k])
        if not ok:
            rows.append({"scheme": claimed, "ok": False})
            continue
        ids = sorted(set(ids))
        odd = tuple(i for i in ids if not sp[i].even)
        candidates = emask
        for i in odd:
            candidates &= adj[i]
        n_even = candidates.bit_count()
        if not odd:
            ncoll, memo = None, None
            complete = False
            why = "all-even component not counted"
        else:
            ncoll, memo = count_mask(candidates, adj)
            complete = True
            why = None
        rows.append({
            "scheme": claimed,
            "cert": rec.get("cert"),
            "odd_splits": list(odd),
            "compatible_even_splits": n_even,
            "collections": ncoll,
            "memo_states": memo,
            "complete": complete,
            "why_incomplete": why,
        })
    payload = {
        "what": ("Fixed-odd even-split component sizes for all 38 published "
                 "M-collections. Components with more than 40 even candidates "
                 "are sized only by candidate count."),
        "components": rows,
        "enumerable": [r for r in rows if r.get("complete")
                       and r.get("collections")
                       and r["collections"] <= 30_000_000],
    }
    dest = HERE / "certs" / "even_all_components.json"
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    enum = payload["enumerable"]
    print(f"wrote {dest.relative_to(ROOT)}: {len(rows)} collections, "
          f"{len(enum)} enumerable")
    for r in enum:
        print(f"  {r['scheme']} even={r['compatible_even_splits']} "
              f"coll={r['collections']}")


if __name__ == "__main__":
    main()
