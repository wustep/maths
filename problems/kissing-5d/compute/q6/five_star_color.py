#!/usr/bin/env python3
"""Greedy extras colouring of every 5-star leftover pool."""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "q5"))

from n1_leftover_sat import stars_of  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402


def welsh_powell(adj):
    n = len(adj)
    deg = [adj[i].bit_count() for i in range(n)]
    order = sorted(range(n), key=lambda i: -deg[i])
    col = [-1] * n
    chi = 0
    for v in order:
        used = set()
        nb = adj[v]
        while nb:
            u = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            if col[u] >= 0:
                used.add(col[u])
        c = 0
        while c in used:
            c += 1
        col[v] = c
        if c + 1 > chi:
            chi = c + 1
    return chi


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    masks = G["masks"]
    thresh = G["thresh"]
    groups = G["groups"]
    seed_index = {m: i for i, m in enumerate(groups)}
    stars = stars_of(G["D"])

    rows = []
    for comb in combinations(range(10), 5):
        U5 = 0
        for s in comb:
            U5 |= stars[s]
        local, local_g = [], []
        for i, m in enumerate(masks):
            if m & ~U5 == 0:
                local.append(i)
                local_g.append(seed_index[m])
        nL = len(local)
        adj = [0] * nL
        for a in range(nL):
            ia = local[a]
            for b in range(a + 1, nL):
                if local_g[a] != local_g[b] and ip(extras[ia], extras[local[b]]) <= thresh:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        chi = welsh_powell(adj)
        rows.append({
            "stars": list(comb),
            "k": U5.bit_count(),
            "n_extras": nL,
            "n_seeds": len(set(local_g)),
            "chi_welsh_powell": chi,
        })
        print(f"stars={list(comb)} k={U5.bit_count()} nE={nL} chi={chi}",
              flush=True)

    chis = [r["chi_welsh_powell"] for r in rows]
    by_k = {}
    for r in rows:
        rec = by_k.setdefault(r["k"], {
            "k": r["k"], "n_pools": 0, "n_extras": r["n_extras"],
            "n_seeds": r["n_seeds"], "chi_min": r["chi_welsh_powell"],
            "chi_max": r["chi_welsh_powell"], "n_chi_le_19": 0,
        })
        rec["n_pools"] += 1
        rec["chi_min"] = min(rec["chi_min"], r["chi_welsh_powell"])
        rec["chi_max"] = max(rec["chi_max"], r["chi_welsh_powell"])
        if r["chi_welsh_powell"] <= 19:
            rec["n_chi_le_19"] += 1

    report = {
        "n_pools": len(rows),
        "n_colouring_le_19": sum(1 for c in chis if c <= 19),
        "min_chi": min(chis),
        "max_chi": max(chis),
        "chi_hist": dict(sorted(Counter(chis).items())),
        "by_k": [by_k[k] for k in sorted(by_k)],
        "found_41": False,
        "comment": (
            "Greedy extras colouring of 5-star pools.  chi<=19 would "
            "empty leftovers in that pool.  A larger chi does not give "
            "a 41-set."
        ),
        "pools": rows,
    }
    (HERE / "five_star_color.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n_pools": report["n_pools"],
        "n_colouring_le_19": report["n_colouring_le_19"],
        "min_chi": report["min_chi"],
        "max_chi": report["max_chi"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
