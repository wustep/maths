#!/usr/bin/env python3
"""Leftover-tight SAT on a few 5-star pools.

C B&B hit the node cutoff on k=32.  SAT is leftover-tight.
A model is written to certs/code41.json.  UNSAT without DRAT is residue.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent / "q5"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from four_star_extras import leftover_sat, write_code41  # noqa: E402
from n1_leftover_sat import stars_of  # noqa: E402
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
    seed_index = {m: i for i, m in enumerate(groups)}
    stars = stars_of(D)

    # four k=32 pools that C left incomplete, plus two more
    wanted = [
        (0, 1, 2, 3, 4),
        (0, 1, 2, 3, 5),
        (0, 1, 2, 3, 6),
        (0, 1, 2, 3, 7),
        (0, 1, 4, 5, 6),
        (0, 1, 4, 5, 7),
    ]
    wanted_set = {tuple(c) for c in wanted}

    pools = []
    found = False
    for comb in combinations(range(10), 5):
        if comb not in wanted_set:
            continue
        U5 = 0
        for s in comb:
            U5 |= stars[s]
        local, local_g, local_miss = [], [], []
        for i, m in enumerate(masks):
            if m & ~U5 == 0:
                local.append(i)
                local_g.append(seed_index[m])
                local_miss.append(m)
        print(f"stars={list(comb)} k={U5.bit_count()} nE={len(local)}",
              flush=True)
        srec = leftover_sat(local, local_g, local_miss, U5, need=20)
        rec = {
            "stars": list(comb),
            "k": U5.bit_count(),
            "n_extras": len(local),
            "sat": srec["sat"],
            "cnf_vars": srec["n_vars"],
            "cnf_clauses": srec["n_clauses"],
            "found_41": False,
        }
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
                             f"q6 5-star SAT stars={list(comb)}",
                             HERE / "certs" / "code41.json")
                rec["found_41"] = True
                found = True
        pools.append(rec)
        print(f"  sat={rec['sat']} found_41={rec['found_41']}", flush=True)
        if found:
            break

    report = {
        "n_pools": len(pools),
        "found_41": found,
        "n_sat_unsat": sum(1 for p in pools if p.get("sat") is False),
        "pools": pools,
        "comment": (
            "Leftover-tight SAT on a sample of 5-star pools.  "
            "UNSAT without DRAT is residue.  Did not claim tau5=40."
        ),
    }
    (HERE / "five_star_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote five_star_sat.json found_41=", found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
