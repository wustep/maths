#!/usr/bin/env python3
"""Neighbourhood census for T^5 36-cliques of share 23.

q4 emptied share 24 through 30.  A remaining 36-clique K satisfies
|K ∩ C| <= 23 for every published 35-clique C.

Share 23 is C(35,12)*4 neighbourhoods if enumerated raw.  This file
does not enumerate those subsets.  For each published 35 it counts
outsiders with d_C >= 23, 22, 21, records clique / independence hints
on the d_C >= 23 outsider graph, and samples 10k random 23-subsets of
C.  A sample whose common neighbourhood N (minus C) has |N| >= 13 is
large enough to host the 13 extra vertices of a share-23 36-clique;
those N are searched for a 13-clique.  A hit lifts through the five
universal basis vectors.  A full emptiness proof still lives in
t5_share.c.  Incomplete search is residue.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))
sys.path.insert(0, str(ROOT / "q4"))

from cliqueutil import clique_search  # noqa: E402
from t5_36 import bits_list, build_pool, is_clique  # noqa: E402

SHARE = 23
NEED = 36 - SHARE
N_SAMPLES = 10_000
NODE_LIMIT = 2_000_000
SEED = 20260827


def common_n(adj, verts, n):
    bits = (1 << n) - 1
    for v in verts:
        bits &= adj[v]
    for v in verts:
        bits &= ~(1 << v)
    return bits


def induced_adj(adj, verts):
    remap = {v: i for i, v in enumerate(verts)}
    m = len(verts)
    hadj = [0] * m
    for i, a in enumerate(verts):
        bits = 0
        x = adj[a]
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            j = remap.get(b)
            if j is not None:
                bits |= 1 << j
        hadj[i] = bits
    return hadj


def complement_adj(hadj, m):
    mask = (1 << m) - 1
    return [mask ^ (1 << i) ^ hadj[i] for i in range(m)]


def hint_search(hadj, m, target, seed_best=0):
    if m == 0:
        return {
            "best": 0,
            "nodes": 0,
            "complete": True,
            "found_target": False,
        }
    hit, best, nodes, complete = clique_search(
        hadj, m, target=target, node_limit=NODE_LIMIT, seed_best=seed_best
    )
    return {
        "best": best,
        "nodes": nodes,
        "complete": complete,
        "found_target": hit is not None,
        "seed_best": seed_best,
    }


def write_code41(G, clique36, source):
    univ = G["univ"]
    keep = G["keep"]
    pool = G["pool"]
    idx = [keep[i] for i in clique36] + list(univ)
    (HERE / "certs").mkdir(exist_ok=True)
    (HERE / "certs" / "code41.json").write_text(json.dumps({
        "n": 41,
        "source": source,
        "remainder_clique": list(clique36),
        "points": [list(map(str, pool[i])) for i in idx],
    }, indent=2) + "\n")


def census_code(name, C, G, adj, n, published_sets, rng):
    assert len(C) == 35 and is_clique(adj, C)
    Cset = set(C)
    Cbits = 0
    for v in C:
        Cbits |= 1 << v

    deg_hist = {}
    n_ge = {21: 0, 22: 0, 23: 0}
    outsiders_23 = []
    max_dC = 0
    for v in range(n):
        if v in Cset:
            continue
        dC = (adj[v] & Cbits).bit_count()
        deg_hist[dC] = deg_hist.get(dC, 0) + 1
        if dC > max_dC:
            max_dC = dC
        if dC >= 21:
            n_ge[21] += 1
        if dC >= 22:
            n_ge[22] += 1
        if dC >= 23:
            n_ge[23] += 1
            outsiders_23.append(v)

    N_all = common_n(adj, C, n)
    N_all_out = N_all & ~Cbits

    seed_omega = 0
    other_outside = {}
    for other, S in published_sets.items():
        if other == name:
            continue
        outside = len(S - Cset)
        other_outside[other] = outside
        if outside > seed_omega:
            seed_omega = outside

    hadj = induced_adj(adj, outsiders_23)
    m = len(outsiders_23)
    clique_hint = hint_search(hadj, m, target=36, seed_best=seed_omega)
    indep_hint = hint_search(complement_adj(hadj, m), m, target=m, seed_best=0)
    print(
        f"{name} out>=23/22/21={n_ge[23]}/{n_ge[22]}/{n_ge[21]} "
        f"max_dC={max_dC} omega~{clique_hint['best']}"
        f"{'' if clique_hint['complete'] else '*'} "
        f"alpha~{indep_hint['best']}"
        f"{'' if indep_hint['complete'] else '*'}",
        flush=True,
    )

    hist = {}
    n_ge_13 = 0
    n_searched = 0
    n_search_complete = 0
    n_search_incomplete = 0
    best_in_N = 0
    found_13 = False
    clique36 = None
    mask = (1 << n) - 1
    outside_mask = mask & ~Cbits

    for _ in range(N_SAMPLES):
        S = rng.sample(C, SHARE)
        bits = outside_mask
        for v in S:
            bits &= adj[v]
        nsz = bits.bit_count()
        key = str(nsz)
        hist[key] = hist.get(key, 0) + 1
        if nsz < NEED:
            continue
        n_ge_13 += 1
        if found_13:
            continue
        pool = bits_list(bits)
        padj = induced_adj(adj, pool)
        n_searched += 1
        hit, best, nodes, ok = clique_search(
            padj, len(pool), target=NEED, node_limit=NODE_LIMIT, seed_best=0
        )
        if best > best_in_N:
            best_in_N = best
        if ok:
            n_search_complete += 1
        else:
            n_search_incomplete += 1
        if hit is not None:
            K = list(S) + [pool[i] for i in hit]
            if len(K) == 36 and is_clique(adj, K):
                found_13 = True
                clique36 = K
                print(f"  {name} 13-clique in N (size {nsz}): 36-clique",
                      flush=True)

    hist = {k: hist[k] for k in sorted(hist, key=int)}
    sizes = [int(k) for k in hist]
    print(
        f"  {name} samples={N_SAMPLES} |N|>=13: {n_ge_13} "
        f"N in [{min(sizes, default=0)}, {max(sizes, default=0)}] "
        f"searched={n_searched} found_13={found_13}",
        flush=True,
    )
    return {
        "n_outsiders_deg_ge_23": n_ge[23],
        "n_outsiders_deg_ge_22": n_ge[22],
        "n_outsiders_deg_ge_21": n_ge[21],
        "max_dC": max_dC,
        "degC_hist": {str(a): b for a, b in sorted(deg_hist.items())},
        "common_N_of_C": N_all.bit_count(),
        "common_N_in_outsiders": N_all_out.bit_count(),
        "other_published_outside_C": other_outside,
        "outsider_clique": clique_hint,
        "outsider_independence": indep_hint,
        "sample_N_hist": hist,
        "n_N_ge_13": n_ge_13,
        "n_N_ge_13_rate": n_ge_13 / N_SAMPLES,
        "n_searched_13": n_searched,
        "n_search_complete": n_search_complete,
        "n_search_incomplete": n_search_incomplete,
        "best_clique_in_N": best_in_N,
        "found_13_clique": found_13,
        "need": NEED,
        "clique36": clique36,
    }


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    published_sets = {
        name: set(rec["remainder_clique"])
        for name, rec in G["published"].items()
    }
    rng = random.Random(SEED)
    by_code = {}
    found_36 = False
    clique36 = None
    found_from = None
    for name, rec in G["published"].items():
        C = rec["remainder_clique"]
        out = census_code(name, C, G, adj, n, published_sets, rng)
        clique = out.pop("clique36")
        by_code[name] = out
        if clique is not None and not found_36:
            found_36 = True
            clique36 = clique
            found_from = name

    report = {
        "n": n,
        "share": SHARE,
        "need": NEED,
        "n_samples": N_SAMPLES,
        "node_limit": NODE_LIMIT,
        "seed": SEED,
        "found_36": found_36,
        "found_41": found_36,
        "found_from": found_from,
        "by_code": by_code,
        "comment": (
            "Census of share-23 neighbourhoods, not an emptiness proof.  "
            "C(35,12) is not enumerated.  Outsider clique / independence "
            "figures are hints at node_limit "
            f"{NODE_LIMIT}.  Incomplete search is residue.  "
            "A 36-clique, if one exists, shares at most 23 with each "
            "published 35.  This does not move 40 <= tau_5 <= 44."
        ),
    }
    (HERE / "t5_share_pruned.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    if found_36:
        write_code41(
            G,
            clique36,
            "T5 share-23 sample 13-clique plus 5 universal basis vectors",
        )
        print("wrote certs/code41.json", flush=True)
    print(json.dumps({
        "found_36": found_36,
        "found_from": found_from,
        "by_code": {
            name: {
                "n_outsiders_deg_ge_23": rec["n_outsiders_deg_ge_23"],
                "n_outsiders_deg_ge_22": rec["n_outsiders_deg_ge_22"],
                "n_outsiders_deg_ge_21": rec["n_outsiders_deg_ge_21"],
                "n_N_ge_13": rec["n_N_ge_13"],
                "found_13_clique": rec["found_13_clique"],
                "outsider_clique_best": rec["outsider_clique"]["best"],
                "outsider_independence_best": rec["outsider_independence"]["best"],
            }
            for name, rec in by_code.items()
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
