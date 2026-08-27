#!/usr/bin/env python3
"""Leftover 41-set hosted by a two-axis 4-star (k=28).

The ten 4-star unions of size 28 are the pairs of fully covered
coordinate-axes: both signs on two of the five axes.  Each pool is
64 four-seeds and 320 extras (no type-C).  A leftover 41-set in the
pool needs |E| >= 20 and |U| <= |E| - 1.

SAT is leftover-tight.  A model is written to certs/code41.json.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from four_star_extras import leftover_sat, stars_of, write_code41  # noqa: E402
from cliqueutil import clique_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    groups = G["groups"]
    masks = G["masks"]
    thresh = G["thresh"]
    leftover_sat.extras = extras
    leftover_sat.thresh = thresh
    seed_list = list(groups)
    seed_index = {m: i for i, m in enumerate(seed_list)}
    stars = stars_of(D)

    # opposite pair of stars: indices 2i, 2i+1 are axis i ±
    pools = []
    found = False
    for a, b in combinations(range(5), 2):
        comb = (2 * a, 2 * a + 1, 2 * b, 2 * b + 1)
        U4 = stars[comb[0]] | stars[comb[1]] | stars[comb[2]] | stars[comb[3]]
        k = U4.bit_count()
        assert k == 28
        local, local_g, local_miss = [], [], []
        nA = 0
        for i, m in enumerate(masks):
            if m & ~U4 == 0:
                local.append(i)
                local_g.append(seed_index[m])
                local_miss.append(m)
                if tuple(sorted(abs(x) for x in extras[i])) == (2, 2, 2, 2, 4):
                    nA += 1
        nL = len(local)
        adj = [0] * nL
        for p in range(nL):
            ip_ = extras[local[p]]
            for q in range(p + 1, nL):
                if local_g[p] != local_g[q] and ip(ip_, extras[local[q]]) <= thresh:
                    adj[p] |= 1 << q
                    adj[q] |= 1 << p
        hit, best, nodes, complete = clique_search(
            adj, nL, target=20, node_limit=400_000, seed_best=19,
        )
        rec = {
            "axes": [a, b],
            "stars": list(comb),
            "k": k,
            "n_extras": nL,
            "n_type_A": nA,
            "n_seeds": len(set(local_g)),
            "bb_best": best,
            "bb_nodes": nodes,
            "bb_complete": complete,
            "bb_hit": bool(hit),
            "found_41": False,
        }
        if hit:
            E = [local[t] for t in hit]
            Ubits = 0
            for i in E:
                Ubits |= masks[i]
            U = [r for r in range(40) if (Ubits >> r) & 1]
            rec["n_sel"] = len(E)
            rec["n_U"] = len(U)
            if len(E) >= len(U) + 1 and len(U) >= 19:
                write_code41(extras, D, E, U,
                             f"q6 two-axis B&B axes={a,b}",
                             HERE / "certs" / "code41.json")
                rec["found_41"] = True
                found = True
        if not rec["found_41"]:
            srec = leftover_sat(local, local_g, local_miss, U4, need=20)
            rec["sat"] = srec["sat"]
            rec["cnf_vars"] = srec["n_vars"]
            rec["cnf_clauses"] = srec["n_clauses"]
            if srec["sat"] and srec["extras_local"] is not None:
                E = [local[t] for t in srec["extras_local"]]
                Ubits = 0
                for i in E:
                    Ubits |= masks[i]
                U = [r for r in range(40) if (Ubits >> r) & 1]
                rec["n_sel"] = len(E)
                rec["n_U"] = len(U)
                if len(E) >= len(U) + 1 and len(U) >= 19:
                    write_code41(extras, D, E, U,
                                 f"q6 two-axis SAT axes={a,b}",
                                 HERE / "certs" / "code41.json")
                    rec["found_41"] = True
                    found = True
        pools.append(rec)
        print(
            f"axes={a,b} nE={nL} best={best} complete={complete} "
            f"sat={rec.get('sat')} found_41={rec['found_41']}",
            flush=True,
        )
        if found:
            break

    report = {
        "n_pools": len(pools),
        "n_expected": 10,
        "found_41": found,
        "n_sat_unsat": sum(1 for p in pools if p.get("sat") is False),
        "n_bb_complete_empty": sum(
            1 for p in pools if p["bb_complete"] and not p["bb_hit"]
        ),
        "pools": pools,
        "comment": (
            "Two-axis 4-star leftover.  Pure four-seeds.  SAT-unsat "
            "without DRAT is residue.  Did not claim tau5=40."
        ),
    }
    (HERE / "two_axis_extras.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote two_axis_extras.json found_41=", found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
