#!/usr/bin/env python3
"""Complete high-n1 slices of (1/3)Z^5 and (1/6)Z^5.

Same-missed extras are independent (same_missed.py).  A 41-set with
n1 = 40-k therefore needs k+1 extras whose missed-root sets sit inside
one k-set U.  For small k the maximum pool is smaller than k+1 (empty
by counting).  Larger k are enumerated from actual missed sets.
"""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from cliqueutil import clique_search
from sphere import d5_pts, enumerate_sphere, ip

HERE = Path(__file__).resolve().parent


def prepare(d):
    pts = enumerate_sphere(d)
    D = d5_pts(d)
    Dset = set(D)
    thresh = d * d
    extras = [p for p in pts if p not in Dset]
    masks = []
    by_mask = defaultdict(list)
    for p in extras:
        m = 0
        for i, r in enumerate(D):
            if ip(p, r) > thresh:
                m |= 1 << i
        masks.append(m)
        by_mask[m].append(p)
    miss_sizes = sorted({m.bit_count() for m in by_mask})
    return {
        "d": d, "pts": pts, "D": D, "thresh": thresh,
        "extras": extras, "by_mask": by_mask, "miss_sizes": miss_sizes,
        "n": len(pts),
    }


def pool_for(U, by_mask):
    pool = []
    s = U
    # all submasks of U, including U
    sub = s
    while True:
        if sub in by_mask:
            pool.extend(by_mask[sub])
        if sub == 0:
            break
        sub = (sub - 1) & s
    return pool


def max_pool_bound(k, miss_sizes, by_mask):
    """Upper bound on |{extras : missed ⊆ U}| for |U|=k."""
    max_g = max((len(v) for v in by_mask.values()), default=0)
    tot = 0
    from math import comb
    for ms in miss_sizes:
        if ms <= k:
            tot += comb(k, ms) * max_g
    return tot


def slice_k(G, k, node_limit=200_000):
    by_mask = G["by_mask"]
    thresh = G["thresh"]
    target = k + 1
    n1 = 40 - k
    bound = max_pool_bound(k, G["miss_sizes"], by_mask)
    rec = {
        "k": k, "n1": n1, "target_extras": target,
        "pool_bound": bound,
        "n_U": 0, "tried": 0, "found": False, "complete": True,
        "best_extras": 0, "best_total": n1,
        "empty_by_count": bound < target,
    }
    if bound < target:
        rec["complete"] = True
        return rec, None
    seeds = [m for m in by_mask if m.bit_count() <= k]
    seen = set()
    hit = None
    for M in seeds:
        popM = M.bit_count()
        rest = [i for i in range(40) if not ((M >> i) & 1)]
        need = k - popM
        for extra_idx in combinations(rest, need):
            U = M
            for i in extra_idx:
                U |= 1 << i
            if U in seen:
                continue
            seen.add(U)
            rec["n_U"] += 1
            pool = pool_for(U, by_mask)
            if len(pool) < target:
                continue
            rec["tried"] += 1
            n = len(pool)
            adj = [0] * n
            for i in range(n):
                for j in range(i + 1, n):
                    if ip(pool[i], pool[j]) <= thresh:
                        adj[i] |= 1 << j
                        adj[j] |= 1 << i
            found, best, nodes, complete = clique_search(
                adj, n, target, node_limit=node_limit
            )
            rec["complete"] = rec["complete"] and complete
            if best > rec["best_extras"]:
                rec["best_extras"] = best
                rec["best_total"] = best + n1
            if found is not None:
                extra = [pool[i] for i in found]
                common = [r for r in G["D"]
                          if all(ip(p, r) <= thresh for p in extra)]
                hit = extra + common
                rec["found"] = True
                return rec, hit
    return rec, None


def hunt(d, ks, node_limit=200_000):
    G = prepare(d)
    slices = {}
    hit = None
    print(f"d={d} n={G['n']} extras={len(G['extras'])} "
          f"miss_sizes={G['miss_sizes']}", flush=True)
    for k in ks:
        rec, h = slice_k(G, k, node_limit=node_limit)
        slices[str(k)] = rec
        print(f"  k={k} bound={rec['pool_bound']} n_U={rec['n_U']} "
              f"tried={rec['tried']} best_ex={rec['best_extras']} "
              f"empty_count={rec['empty_by_count']} found={rec['found']}",
              flush=True)
        if h is not None:
            hit = h
            break
    return {
        "d": d,
        "n": G["n"],
        "n_extras": len(G["extras"]),
        "miss_sizes": G["miss_sizes"],
        "slices": slices,
        "found_41": hit is not None,
        "complete": all(s["complete"] and not s["found"] for s in slices.values()),
        "hit_int": hit,
    }


def main():
    report = {}
    # d=3: k=4,5 empty by count; k=6,7 enumerated.  k>=8 is residue if unfinished.
    # d=6: k=4 empty by same-missed independence + count; k=5,6,7 attempted.
    # d=5 included: max miss 8, some extras miss only 3.
    for d, ks in ((3, (4, 5, 6, 7)), (5, (3, 4, 5, 6)), (6, (4, 5, 6))):
        rec = hunt(d, ks)
        report[str(d)] = {k: v for k, v in rec.items() if k != "hit_int"}
        if rec["hit_int"]:
            from fractions import Fraction
            (HERE / "certs").mkdir(exist_ok=True)
            pts = [tuple(Fraction(a, d) for a in p) for p in rec["hit_int"][:41]]
            (HERE / "certs" / "code41.json").write_text(json.dumps({
                "n": 41,
                "source": f"mixed_slices.py d={d}",
                "points": [[str(x) for x in p] for p in pts],
            }, indent=2) + "\n")
            report["found_41"] = True
            break
    else:
        report["found_41"] = False
    (HERE / "mixed_slices.json").write_text(json.dumps(report, indent=2) + "\n")
    print("found_41", report["found_41"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
