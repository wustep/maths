#!/usr/bin/env python3
"""Exact-union U of missed D5-root seeds, and extras-cliques in those pools.

A missed-union that can arise from extras is a union of actual seeds (no
dummy roots).  A 41-set needs some such U with at least |U|+1 extras
that pairwise kiss and whose missed sets sit in U.

This file rebuilds the 1480-point integer graph, walks every seed-union
with |U| <= maxk, and searches each promising pool with an independent
bitset clique (no C B&B).  It is the replay of n1_le32's U list.
"""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path

from sphere import extras_and_groups, ip

HERE = Path(__file__).resolve().parent


def clique_search(adj, n, target):
    """Return (hit or None, best).  Complete; n is small."""
    best = 0
    found = None

    def expand(P, stack):
        nonlocal best, found
        if found is not None:
            return
        rsz = len(stack)
        psz = P.bit_count()
        if rsz + psz <= best:
            return
        if P == 0:
            if rsz > best:
                best = rsz
            return
        rem = P
        ord_v, col = [], []
        c = 0
        while rem:
            c += 1
            avail = rem
            while avail:
                v = (avail & -avail).bit_length() - 1
                ord_v.append(v)
                col.append(c)
                avail &= ~adj[v]
                avail &= ~(1 << v)
                rem &= ~(1 << v)
        Q = P
        for i in range(len(ord_v) - 1, -1, -1):
            if found is not None:
                return
            if rsz + col[i] <= best:
                return
            v = ord_v[i]
            stack.append(v)
            if rsz + 1 >= target:
                found = list(stack)
                best = rsz + 1
                return
            expand(Q & adj[v], stack)
            stack.pop()
            Q &= ~(1 << v)

    expand((1 << n) - 1, [])
    return found, best


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxk", type=int, default=16)
    args = ap.parse_args()
    maxk = args.maxk

    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    thresh = G["thresh"]
    groups = G["groups"]
    seeds = list(groups)
    nG = len(seeds)
    seed_of = {m: i for i, m in enumerate(seeds)}

    through = [0] * 40
    for i, m in enumerate(seeds):
        x = m
        while x:
            b = (x & -x).bit_length() - 1
            through[b] |= 1 << i
            x &= x - 1
    all_seeds = (1 << nG) - 1

    def contained(U):
        dead = 0
        for r in range(40):
            if not ((U >> r) & 1):
                dead |= through[r]
        return all_seeds & ~dead

    def union_of(bits):
        U = 0
        x = bits
        while x:
            i = (x & -x).bit_length() - 1
            U |= seeds[i]
            x &= x - 1
        return U

    # Inter-group bipartite type.
    g_extras = [groups[m] for m in seeds]
    pair_type = Counter()
    for i in range(nG):
        for j in range(i + 1, nG):
            a, b = g_extras[i], g_extras[j]
            e = 0
            tot = len(a) * len(b)
            for p in a:
                for q in b:
                    if ip(p, q) <= thresh:
                        e += 1
            if e == 0:
                pair_type["empty"] += 1
            elif e == tot:
                pair_type["complete"] += 1
            else:
                pair_type["mixed"] += 1

    types = Counter(type_key(p) for p in extras)
    pop_hist = Counter(m.bit_count() for m in seeds)

    # BFS of seed-unions.
    seen = set()
    q = deque()
    for m in seeds:
        seen.add(m)
        q.append(m)
    promising = []
    max_seeds = Counter()
    n_unions = Counter()
    while q:
        U = q.popleft()
        k = U.bit_count()
        bits = contained(U)
        ns = bits.bit_count()
        n_unions[k] += 1
        if ns > max_seeds[k]:
            max_seeds[k] = ns
        if k >= 4 and ns >= k + 1 and union_of(bits) == U:
            promising.append((k, ns, U, bits))
        if k >= maxk:
            continue
        for s in seeds:
            U2 = U | s
            k2 = U2.bit_count()
            if k2 <= maxk and U2 not in seen:
                seen.add(U2)
                q.append(U2)

    promising.sort()
    print(f"unions={len(seen)} promising={len(promising)} maxk={maxk}",
          flush=True)
    print(f"max_seeds_by_k={dict(sorted(max_seeds.items()))}", flush=True)
    print(f"n_unions_by_k={dict(sorted(n_unions.items()))}", flush=True)
    print(f"pair_type={dict(pair_type)} types={dict(types)} "
          f"seed_pops={dict(pop_hist)}", flush=True)

    # Extras adjacency as Python ints, indexed in extras list.
    extra_index = {p: i for i, p in enumerate(extras)}
    nE = len(extras)
    adjE = [0] * nE
    for i in range(nE):
        for j in range(i + 1, nE):
            if ip(extras[i], extras[j]) <= thresh:
                adjE[i] |= 1 << j
                adjE[j] |= 1 << i

    slices = {}
    constructions = []
    for k, ns, U, bits in promising:
        pool = []
        gsel = []
        x = bits
        while x:
            gi = (x & -x).bit_length() - 1
            gsel.append(gi)
            pool.extend(g_extras[gi])
            x &= x - 1
        idx = [extra_index[p] for p in pool]
        m = len(pool)
        adj = [0] * m
        for a in range(m):
            ia = idx[a]
            for b in range(a + 1, m):
                if (adjE[ia] >> idx[b]) & 1:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        # drop intra-group: already independent, but keep the search honest
        target = k + 1
        hit, best = clique_search(adj, m, target)
        rec = slices.setdefault(str(k), {
            "k": k,
            "n1": 40 - k,
            "n_U": 0,
            "tried": 0,
            "found": False,
            "complete": True,
            "best_extras": 0,
            "best_total": 0,
            "max_seeds": 0,
        })
        rec["n_U"] += 1
        rec["tried"] += 1
        rec["max_seeds"] = max(rec["max_seeds"], ns)
        if best > rec["best_extras"]:
            rec["best_extras"] = best
            rec["best_total"] = best + (40 - k)
        if hit is not None:
            rec["found"] = True
            extra = [pool[i] for i in hit]
            common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
            constructions.append({
                "n1": len(common),
                "n_extras": len(extra),
                "total": len(common) + len(extra),
                "extras": [list(p) for p in extra],
                "d5": [list(r) for r in common],
            })

    for k in range(4, maxk + 1):
        slices.setdefault(str(k), {
            "k": k,
            "n1": 40 - k,
            "n_U": 0,
            "tried": 0,
            "found": False,
            "complete": True,
            "best_extras": 0,
            "best_total": 0,
            "max_seeds": max_seeds.get(k, 0),
        })
        slices[str(k)]["empty_by_part_count"] = max_seeds.get(k, 0) < k + 1
        slices[str(k)]["max_seeds_any_union"] = max_seeds.get(k, 0)
        slices[str(k)]["n_unions"] = n_unions.get(k, 0)

    report = {
        "d": 4,
        "n": len(G["pts"]),
        "n_extras": nE,
        "n_groups": nG,
        "group_pair_type": dict(pair_type),
        "type_hist": {str(a): b for a, b in sorted(types.items())},
        "maxk": maxk,
        "n_unions_visited": len(seen),
        "n_promising": len(promising),
        "slices": slices,
        "constructed_ge41": constructions,
        "found_41": bool(constructions),
        "comment": (
            "Exact seed-unions only.  Dummy roots that complete no extra "
            "seed cannot arise as a missed-union.  Clique search is an "
            "independent Python bitset replay of each promising pool."
        ),
    }
    path = HERE / "dense_U.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path, "found_41=", report["found_41"])
    for k, rec in sorted(slices.items(), key=lambda kv: int(kv[0])):
        print(f"  k={k} n1={rec['n1']} n_U={rec['n_U']} "
              f"max_seeds={rec.get('max_seeds_any_union')} "
              f"best_ex={rec['best_extras']} found={rec['found']} "
              f"part_empty={rec.get('empty_by_part_count')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
