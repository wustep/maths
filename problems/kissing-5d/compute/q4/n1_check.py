#!/usr/bin/env python3
"""Independent replay of the n1=32 slice.

Rebuilds extras and missed-set groups over Z, checks that each group is
edgeless, enumerates every 8-superset of an actual seed, and searches a
9-clique in every pool that contains at least 9 groups.  Must agree with
n1_le32.c: n_U = 7407770, tried = 10, best_extras = 8, found = false.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from sphere import extras_and_groups, ip

HERE = Path(__file__).resolve().parent


def clique_search(adj, n, target, node_limit=2_000_000):
    best = 0
    found = None
    nodes = 0

    def expand(P, stack):
        nonlocal best, found, nodes
        if found is not None:
            return
        nodes += 1
        if nodes > node_limit:
            return
        rsz = len(stack)
        if rsz + P.bit_count() <= best:
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
            if found is not None or nodes > node_limit:
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
    return found, best, nodes, found is not None or nodes <= node_limit


def main() -> int:
    G = extras_and_groups(4)
    extras, groups, thresh = G["extras"], G["groups"], G["thresh"]
    seeds = list(groups)
    # groups edgeless
    intra = 0
    for g in groups.values():
        for a, b in combinations(g, 2):
            if ip(a, b) <= thresh:
                intra += 1
    print(f"extras={len(extras)} groups={len(seeds)} intra={intra}", flush=True)

    seen = set()
    nU = 0
    interesting = []
    max_seeds = 0
    for m in seeds:
        pop = m.bit_count()
        if pop > 8:
            continue
        rest = [i for i in range(40) if not ((m >> i) & 1)]
        need = 8 - pop
        for extra in combinations(rest, need):
            U = m
            for i in extra:
                U |= 1 << i
            if U in seen:
                continue
            seen.add(U)
            nU += 1
            contained = [s for s in seeds if (s & ~U) == 0]
            if len(contained) > max_seeds:
                max_seeds = len(contained)
            if len(contained) >= 9:
                interesting.append((U, contained))
    print(f"n_U={nU} interesting={len(interesting)} max_seeds={max_seeds}",
          flush=True)

    best_ex = 0
    found = False
    complete = True
    constructions = []
    for U, contained in interesting:
        pool = []
        for s in contained:
            pool.extend(groups[s])
        k = len(pool)
        adj = [0] * k
        for i in range(k):
            for j in range(i + 1, k):
                if ip(pool[i], pool[j]) <= thresh:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
        hit, best, nodes, ok = clique_search(adj, k, 9)
        complete = complete and ok
        if best > best_ex:
            best_ex = best
        print(f"  U pop={U.bit_count()} groups={len(contained)} pool={k} "
              f"best={best} found={hit is not None} nodes={nodes}", flush=True)
        if hit is not None:
            found = True
            extra = [pool[i] for i in hit]
            common = [r for r in G["D"] if all(ip(p, r) <= thresh for p in extra)]
            constructions.append({
                "n1": len(common),
                "n_extras": len(extra),
                "total": len(common) + len(extra),
            })
            break

    report = {
        "d": 4,
        "n_extras": len(extras),
        "n_groups": len(seeds),
        "groups_edgeless": intra == 0,
        "k": 8,
        "n1": 32,
        "n_U": nU,
        "tried": len(interesting),
        "max_seeds_in_U": max_seeds,
        "best_extras": best_ex,
        "best_total": best_ex + 32,
        "found_41": found,
        "complete": complete and not found,
        "constructed_ge41": constructions,
        "comment": (
            "Independent Python replay of the k=8 slice.  Must match "
            "n1_le32.c: n_U=7407770, tried=10, best_extras=8, empty."
        ),
    }
    (HERE / "n1_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote n1_check.json", report)
    # agree with C
    cpath = HERE / "n1_le32.json"
    ok = True
    if cpath.exists():
        C = json.loads(cpath.read_text())
        sl = C["slices"]["8"]
        ok = (
            sl["n_U"] == nU and sl["tried"] == len(interesting)
            and sl["found"] == found and sl["best_extras"] == best_ex
            and C["groups_edgeless"] and intra == 0
        )
        print("agree_with_c", ok)
    report["agree_with_c"] = ok
    (HERE / "n1_check.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok and not found and complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
