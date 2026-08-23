#!/usr/bin/env python3
"""Characterise which Haas split collections give depth-3 nests.

Prints, for the empty collection and every singleton, the scheme of
C(S); then re-evaluates the 38 published 22-oval certificates from
their recorded split collections (certs/mcert_collections.json) and
reports the laminar depth of their Z+ zone forests against the nesting
depth of their schemes.
"""

import json
from collections import Counter, defaultdict

import haas
import deepnest as dn
from notation import parse as parse_scheme


def nest_depth(scheme):
    forest, _ = parse_scheme(scheme)

    def d(t):
        return 1 + max((d(x) for x in t), default=0)

    return max((d(t) for t in forest), default=0)


def shape(scheme):
    """(a,b,c,junk) for <a u 1<b u 1<c>>>."""
    forest, _ = parse_scheme(scheme)

    def size(t):
        return sum(1 + size(x) for x in t)

    a = sum(1 for t in forest if t == ())
    nests = [t for t in forest if t != ()]
    if not nests:
        return a, 0, 0, 0
    big = max(nests, key=size)
    junk = sum(size(t) + 1 for t in nests if t is not big)
    b = sum(1 for x in big if x == ())
    inner = [x for x in big if x != ()]
    if not inner:
        return a, b, 0, junk
    ibig = max(inner, key=size)
    junk += sum(size(x) + 1 for x in inner if x is not ibig)
    c = sum(1 for y in ibig if y == ())
    junk += sum(size(y) + 1 for y in ibig if y != ())
    return a, b, c, junk


def main():
    sp = dn.splits()
    print(f"{len(sp)} splits")
    nc, s, _ = dn.evaluate([])
    print(f"empty collection (Harnack): {nc} components, {s}")

    by_scheme = defaultdict(list)
    for i, x in enumerate(sp):
        nc, s, _ = dn.evaluate([x])
        by_scheme[s].append(i)
    print(f"\nsingletons: {len(by_scheme)} distinct schemes")
    for s, ids in sorted(by_scheme.items(), key=lambda kv: -len(kv[1])):
        d = nest_depth(s)
        print(f"  {len(ids):5d}  depth {d}  {s}")

    # census depth-3 M-certificates, replayed from their collections
    print("\n38 published 22-oval certificates, from their collections:")
    coll = json.load(open("certs/mcert_collections.json"))
    key = {x.key: x for x in sp}
    rows = []
    for claimed, rec in sorted(coll.items()):
        paths = [tuple(tuple(v) for v in p) for p in rec["collection"]]
        cs = []
        ok = True
        for p in paths:
            k = p if p[0] < p[-1] else p[::-1]
            if k not in key:
                ok = False
                break
            cs.append(key[k])
        if not ok:
            print(f"  {claimed}: split not found")
            continue
        try:
            nc, s, _ = dn.evaluate(cs)
        except ValueError as e:
            print(f"  {claimed}: {e}")
            continue
        items, par, kids, roots, dep = dn.zone_tree(cs)
        rows.append((nest_depth(s) if s else -1, claimed, s, nc,
                     len(cs), dep, shape(s) if s else None))
    for d, claimed, s, nc, n, zd, sh in sorted(rows, reverse=True):
        print(f"  nest-depth {d}  zone-depth {zd}  |S|={n:2d}  "
              f"ncomp={nc}  {s}   (claimed {claimed}) shape={sh}")
    print("\nzone-depth vs nest-depth:",
          Counter((r[5], r[0]) for r in rows))


if __name__ == "__main__":
    main()
