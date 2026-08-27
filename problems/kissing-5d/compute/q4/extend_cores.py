#!/usr/bin/env python3
"""The 10 dense 8-cores and every promising superset.

k=8 has exactly 10 missed-unions with >= 9 seeds, each with 16 seeds
(replayed by n1_check.py).  k=9 tried exactly 10*32 = 320 unions, so
those 8-cores plus one dummy root are the only promising 9-sets.

This file extracts the cores, then for each k=8..20 searches every
k-superset of a core that still has >= k+1 seeds.  A second BFS of
seed-unions looks for any other U with n_seeds >= |U|+1 that is not a
superset of one of the ten cores.  Together that is a complete hunt
for a 41-set in n1 <= 32.
"""

from __future__ import annotations

import json
from collections import Counter, deque
from itertools import combinations
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

    def n_in(U):
        dead = 0
        for r in range(40):
            if not ((U >> r) & 1):
                dead |= through[r]
        return (allm & ~dead).bit_count()

    def contained_list(U):
        return [s for s in seeds if (s & ~U) == 0]

    # All 8-supersets of seeds: the 10 cores.
    cores = []
    seen8 = set()
    for m in seeds:
        if m.bit_count() > 8:
            continue
        rest = [i for i in range(40) if not ((m >> i) & 1)]
        for extra in combinations(rest, 8 - m.bit_count()):
            U = m
            for i in extra:
                U |= 1 << i
            if U in seen8:
                continue
            seen8.add(U)
            ns = n_in(U)
            if ns >= 9:
                cores.append((U, ns))
    cores.sort()
    print(f"cores={len(cores)} n8={len(seen8)} pops={[c[1] for c in cores]}",
          flush=True)
    core_U = [U for U, _ in cores]
    extra_index = {p: i for i, p in enumerate(extras)}
    nE = len(extras)
    adjE = [0] * nE
    for i in range(nE):
        for j in range(i + 1, nE):
            if ip(extras[i], extras[j]) <= thresh:
                adjE[i] |= 1 << j
                adjE[j] |= 1 << i

    def search_U(U, target):
        contained = contained_list(U)
        pool = []
        for s in contained:
            pool.extend(groups[s])
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
        return clique_search(adj, m, target), pool, contained

    constructions = []
    slices = {}
    for k in range(8, 21):
        need = k - 8
        seen = set()
        rec = {
            "k": k,
            "n1": 40 - k,
            "n_U": 0,
            "tried": 0,
            "max_seeds": 0,
            "best_extras": 0,
            "best_total": 0,
            "found": False,
            "complete": True,
        }
        for core, _ in cores:
            rest = [i for i in range(40) if not ((core >> i) & 1)]
            for extra in combinations(rest, need):
                U = core
                for i in extra:
                    U |= 1 << i
                if U in seen:
                    continue
                seen.add(U)
                ns = n_in(U)
                rec["n_U"] += 1
                if ns > rec["max_seeds"]:
                    rec["max_seeds"] = ns
                if ns < k + 1:
                    continue
                rec["tried"] += 1
                (hit, best), pool, contained = search_U(U, k + 1)
                if best > rec["best_extras"]:
                    rec["best_extras"] = best
                    rec["best_total"] = best + (40 - k)
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
                    break
            if rec["found"]:
                break
        slices[str(k)] = rec
        print(f"core-superset k={k} n_U={rec['n_U']} tried={rec['tried']} "
              f"max_seeds={rec['max_seeds']} best={rec['best_extras']} "
              f"found={rec['found']}", flush=True)
        if rec["found"]:
            break

    # BFS of seed-unions: any other promising U not a superset of a core?
    maxk = 20
    seen = set()
    q = deque()
    for m in seeds:
        seen.add(m)
        q.append(m)
    other = []
    n_unions = 0
    max_other = Counter()
    while q:
        U = q.popleft()
        n_unions += 1
        k = U.bit_count()
        ns = n_in(U)
        is_core_sup = any((U & C) == C for C in core_U)
        if not is_core_sup:
            if ns > max_other[k]:
                max_other[k] = ns
            if k >= 4 and ns >= k + 1:
                other.append((k, ns, U))
        if k >= maxk:
            continue
        for s in seeds:
            U2 = U | s
            if U2.bit_count() <= maxk and U2 not in seen:
                seen.add(U2)
                q.append(U2)
        if n_unions % 200000 == 0:
            print(f"  bfs unions={n_unions} q={len(q)} other={len(other)}",
                  flush=True)

    print(f"bfs unions={n_unions} other_promising={len(other)} "
          f"max_other={dict(sorted(max_other.items()))}", flush=True)

    for k, ns, U in other:
        (hit, best), pool, contained = search_U(U, k + 1)
        rec = slices.setdefault(str(k), {
            "k": k, "n1": 40 - k, "n_U": 0, "tried": 0,
            "max_seeds": 0, "best_extras": 0, "best_total": 0,
            "found": False, "complete": True,
        })
        rec["tried"] += 1
        rec["n_U"] += 1
        rec["max_seeds"] = max(rec.get("max_seeds", 0), ns)
        if best > rec["best_extras"]:
            rec["best_extras"] = best
            rec["best_total"] = best + (40 - k)
        if hit is not None:
            rec["found"] = True
            extra_pts = [pool[i] for i in hit]
            common = [r for r in D if all(ip(p, r) <= thresh for p in extra_pts)]
            constructions.append({
                "k": k,
                "n1": len(common),
                "n_extras": len(extra_pts),
                "total": len(common) + len(extra_pts),
                "extras": [list(p) for p in extra_pts],
                "d5": [list(r) for r in common],
            })

    report = {
        "d": 4,
        "n_cores": len(cores),
        "core_seed_counts": [ns for _, ns in cores],
        "cores": [U for U, _ in cores],
        "n_seed_unions": n_unions,
        "n_other_promising": len(other),
        "max_seeds_outside_cores": {str(a): b for a, b in sorted(max_other.items())},
        "slices": slices,
        "constructed_ge41": constructions,
        "found_41": bool(constructions),
        "complete": all(slices[str(k)]["complete"] and not slices[str(k)]["found"]
                        for k in slices) and len(other) == 0 or (
            not constructions and all(rec["complete"] for rec in slices.values())
        ),
        "comment": (
            "Ten 8-cores with 16 seeds each; every promising superset "
            "searched; BFS of seed-unions for any other U with "
            "n_seeds>=|U|+1."
        ),
    }
    # dump cores as bit lists for the verifier
    report["cores_bits"] = [
        [i for i in range(40) if (U >> i) & 1] for U, _ in cores
    ]
    path = HERE / "extend_cores.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path, "found_41=", report["found_41"],
          "n_other=", len(other))
    if constructions:
        (HERE / "certs").mkdir(exist_ok=True)
        c0 = constructions[0]
        (HERE / "certs" / "code41.json").write_text(json.dumps({
            "n": 41,
            "model": "integer a in Z^5, a.a=32, edge iff a.b<=16",
            "points": c0["extras"] + c0["d5"],
        }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
