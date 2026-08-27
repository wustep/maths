#!/usr/bin/env python3
"""Greedy colouring of extras in each 4-star pool.

Leftover 41-sets need |E| >= 20.  If a greedy colouring of pool(U4)
uses at most 19 colours, then omega <= 19 and that 4-star hosts no
leftover 41-set.  Census only: a colouring bound is an emptiness
proof for that pool; a bound >= 20 is not a 41-code.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from sphere import extras_and_groups, ip  # noqa: E402


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            out.append(bits)
    return out


def greedy_chi(adj, n):
    """Welsh–Powell greedy colouring; return n_colours."""
    deg = [adj[i].bit_count() for i in range(n)]
    order = sorted(range(n), key=lambda i: -deg[i])
    col = [-1] * n
    used = 0
    for v in order:
        forbidden = set()
        bits = adj[v]
        while bits:
            u = (bits & -bits).bit_length() - 1
            bits &= bits - 1
            if col[u] >= 0:
                forbidden.add(col[u])
        c = 0
        while c in forbidden:
            c += 1
        col[v] = c
        if c + 1 > used:
            used = c + 1
    return used


def cliqueutil_colour_bound(adj, n):
    """Same greedy independent-set colouring as cliqueutil.clique_search."""
    rem = (1 << n) - 1
    c = 0
    while rem:
        c += 1
        avail = rem
        while avail:
            v = (avail & -avail).bit_length() - 1
            avail &= ~adj[v]
            avail &= ~(1 << v)
            rem &= ~(1 << v)
    return c


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    masks = G["masks"]
    groups = G["groups"]
    thresh = G["thresh"]
    seeds = list(groups)
    stars = stars_of(D)

    hist = Counter()
    rows = []
    n_le19 = 0
    max_chi = 0
    max_n = 0
    for comb in combinations(range(10), 4):
        U = stars[comb[0]] | stars[comb[1]] | stars[comb[2]] | stars[comb[3]]
        k = U.bit_count()
        local = [i for i, m in enumerate(masks) if m & ~U == 0]
        nL = len(local)
        ns = sum(1 for m in seeds if m & ~U == 0)
        adj = [0] * nL
        for a in range(nL):
            ia = local[a]
            for b in range(a + 1, nL):
                if ip(extras[ia], extras[local[b]]) <= thresh:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        chi_wp = greedy_chi(adj, nL)
        chi_cu = cliqueutil_colour_bound(adj, nL)
        chi = min(chi_wp, chi_cu)
        hist[(k, nL, ns, chi_wp, chi_cu)] += 1
        if chi <= 19:
            n_le19 += 1
        if chi > max_chi:
            max_chi = chi
        if nL > max_n:
            max_n = nL
        rows.append({
            "stars": list(comb),
            "k": k,
            "n_extras": nL,
            "n_seeds": ns,
            "chi_welsh_powell": chi_wp,
            "chi_cliqueutil": chi_cu,
            "omega_le_19": chi <= 19,
        })
        print(
            f"stars={list(comb)} k={k} nE={nL} ns={ns} "
            f"chi_wp={chi_wp} chi_cu={chi_cu}",
            flush=True,
        )

    pairs = [
        {
            "k": k, "n_extras": nL, "n_seeds": ns,
            "chi_welsh_powell": cwp, "chi_cliqueutil": ccu, "n_pools": c,
        }
        for (k, nL, ns, cwp, ccu), c in sorted(hist.items())
    ]
    report = {
        "n_pools": 210,
        "n_colouring_le_19": n_le19,
        "max_chi": max_chi,
        "max_n_extras": max_n,
        "pairs": pairs,
        "found_41": False,
        "all_omega_le_19": n_le19 == 210,
        "comment": (
            "Greedy colouring of extras in each 4-star pool.  "
            "chi <= 19 implies no leftover 41-set hosted by that union.  "
            "A larger colouring is not a 41-code.  Did not claim tau5=40."
        ),
        "rows": rows,
    }
    (HERE / "four_star_color.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n_pools": 210,
        "n_colouring_le_19": n_le19,
        "max_chi": max_chi,
        "max_n_extras": max_n,
        "pairs": pairs,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
