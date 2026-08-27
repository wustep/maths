#!/usr/bin/env python3
"""Independent replay of exact seed-unions up to a given maxk.

Rebuilds the 1480-graph, walks every union of missed-set seeds with
|U| <= maxk, and bitset-searches each U that contains at least |U|+1
seeds.  Must agree with n1_complete.c on n_unions, n_promising, and
emptiness of each slice.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from sphere import extras_and_groups, ip

HERE = Path(__file__).resolve().parent


def clique_search(adj, n, target):
    best = 0
    found = None

    def expand(P, stack):
        nonlocal best, found
        if found is not None:
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


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxk", type=int, default=12)
    args = ap.parse_args()
    maxk = args.maxk

    G = extras_and_groups(4)
    extras, groups, D, thresh = G["extras"], G["groups"], G["D"], G["thresh"]
    seeds = list(groups)
    nG = len(seeds)
    through = [0] * 40
    for i, m in enumerate(seeds):
        x = m
        while x:
            b = (x & -x).bit_length() - 1
            through[b] |= 1 << i
            x &= x - 1
    allm = (1 << nG) - 1

    def contained_bits(U):
        dead = 0
        for r in range(40):
            if not ((U >> r) & 1):
                dead |= through[r]
        return allm & ~dead

    extra_index = {p: i for i, p in enumerate(extras)}
    nE = len(extras)
    adjE = [0] * nE
    for i in range(nE):
        for j in range(i + 1, nE):
            if ip(extras[i], extras[j]) <= thresh:
                adjE[i] |= 1 << j
                adjE[j] |= 1 << i

    g_extras = [groups[m] for m in seeds]

    seen = set()
    q = deque()
    for m in seeds:
        seen.add(m)
        q.append(m)
    slices = {str(k): {
        "k": k, "n1": 40 - k, "n_unions": 0, "n_promising": 0, "tried": 0,
        "max_seeds": 0, "best_extras": 0, "found": False, "complete": True,
    } for k in range(4, maxk + 1)}
    constructions = []
    n_seen = 0
    while q:
        U = q.popleft()
        n_seen += 1
        k = U.bit_count()
        bits = contained_bits(U)
        ns = bits.bit_count()
        if 4 <= k <= maxk:
            rec = slices[str(k)]
            rec["n_unions"] += 1
            if ns > rec["max_seeds"]:
                rec["max_seeds"] = ns
            if ns >= k + 1:
                rec["n_promising"] += 1
                rec["tried"] += 1
                # build pool
                pool = []
                x = bits
                while x:
                    gi = (x & -x).bit_length() - 1
                    pool.extend(g_extras[gi])
                    x &= x - 1
                idx = [extra_index[p] for p in pool]
                m = len(pool)
                adj = [0] * m
                for a in range(m):
                    ia = idx[a]
                    row = adjE[ia]
                    for b in range(a + 1, m):
                        if (row >> idx[b]) & 1:
                            adj[a] |= 1 << b
                            adj[b] |= 1 << a
                hit, best = clique_search(adj, m, k + 1)
                if best > rec["best_extras"]:
                    rec["best_extras"] = best
                if hit is not None:
                    rec["found"] = True
                    extra_pts = [pool[i] for i in hit]
                    common = [r for r in D
                              if all(ip(p, r) <= thresh for p in extra_pts)]
                    constructions.append({
                        "k": k,
                        "n1": len(common),
                        "n_extras": len(extra_pts),
                        "total": len(common) + len(extra_pts),
                        "extras": [list(p) for p in extra_pts],
                        "d5": [list(r) for r in common],
                    })
        if k >= maxk:
            continue
        for s in seeds:
            U2 = U | s
            if U2.bit_count() <= maxk and U2 not in seen:
                seen.add(U2)
                q.append(U2)
        if n_seen % 200000 == 0:
            print(f"bfs {n_seen} q={len(q)}", flush=True)

    for rec in slices.values():
        rec["empty_by_part_count"] = rec["max_seeds"] < rec["k"] + 1
        rec["best_total"] = rec["best_extras"] + rec["n1"] if rec["best_extras"] else rec["n1"]

    report = {
        "d": 4,
        "n": 1480,
        "n_extras": nE,
        "n_groups": nG,
        "maxk": maxk,
        "n_unions_visited": len(seen),
        "slices": slices,
        "constructed_ge41": constructions,
        "found_41": bool(constructions),
        "complete": all(not r["found"] and r["complete"] for r in slices.values()),
        "comment": "Independent Python BFS of exact seed-unions.",
    }
    path = HERE / f"replay_unions_k{maxk}.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path, "unions=", len(seen), "found_41=", report["found_41"])
    for k, rec in sorted(slices.items(), key=lambda kv: int(kv[0])):
        print(f"  k={k} unions={rec['n_unions']} prom={rec['n_promising']} "
              f"max_seeds={rec['max_seeds']} best={rec['best_extras']} "
              f"found={rec['found']} part_empty={rec['empty_by_part_count']}",
              flush=True)

    # compare to C if present
    for cand in (HERE / f"n1_dfs_k{maxk}.json", HERE / f"n1_complete_k{maxk}.json",
                 HERE / "n1_dfs_k16.json", HERE / "n1_complete.json"):
        if cand.exists():
            C = json.loads(cand.read_text())
            ok = True
            for k, rec in slices.items():
                cr = C["slices"].get(k)
                if cr is None:
                    continue
                if cr["n_unions"] != rec["n_unions"] or cr["n_promising"] != rec["n_promising"] or cr["found"] != rec["found"]:
                    print("MISMATCH", k, cr, rec)
                    ok = False
            print("agree_with_c", ok, "file", cand.name)
            report["agree_with_c"] = ok
            path.write_text(json.dumps(report, indent=2) + "\n")
            return 0 if ok and not report["found_41"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
