#!/usr/bin/env python3
"""SAT hunt for a 41-clique in the 1480-point (1/4)Z^5 kissing graph.

D5 is a 40-clique.  Same-missed extras are independent, so a clique
takes at most one extra per seed.  The CNF is: select 41 vertices,
forbid every non-edge, at most one extra per group.

A model is an explicit 41-set (written to certs/code41.json).
UNSAT without a DRAT file is not an emptiness proof.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from sphere import extras_and_groups, ip

HERE = Path(__file__).resolve().parent


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    pts = list(D) + extras
    thresh = G["thresh"]
    nD = len(D)
    nE = len(extras)
    n = nD + nE
    groups = G["groups"]
    masks = G["masks"]
    seed_index = {m: i for i, m in enumerate(groups)}
    g_of = [seed_index[m] for m in masks]

    # vars: 1..n  (0..nD-1 are D5, then extras)
    def vid(i):
        return i + 1

    from pysat.card import CardEnc, EncType
    from pysat.solvers import Cadical195, Glucose4

    clauses = []
    # at most one extra per group
    by_g = {}
    for i, g in enumerate(g_of):
        by_g.setdefault(g, []).append(nD + i)
    for vs in by_g.values():
        for a, b in combinations(vs, 2):
            clauses.append([-vid(a), -vid(b)])

    nonedges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ip(pts[i], pts[j]) > thresh:
                clauses.append([-vid(i), -vid(j)])
                nonedges += 1

    topid = n
    card = CardEnc.equals(lits=[vid(i) for i in range(n)], bound=41,
                          top_id=topid, encoding=EncType.seqcounter)
    clauses.extend(card.clauses)
    print(f"n={n} nonedges={nonedges} extra_clauses={len(clauses)} "
          f"card_vars={card.nv}", flush=True)

    colour = None
    used = None
    for name, Solver in (("cadical195", Cadical195), ("glucose4", Glucose4)):
        print(f"41-clique SAT with {name} ...", flush=True)
        slv = Solver()
        for c in clauses:
            slv.add_clause(c)
        sat = slv.solve()
        model = slv.get_model() if sat else None
        slv.delete()
        print(f"  {name} sat={sat}", flush=True)
        if sat and model:
            true = set(x for x in model if x > 0)
            sel = [i for i in range(n) if vid(i) in true]
            if len(sel) != 41:
                print("  bad model size", len(sel), flush=True)
                continue
            ok = True
            for a, b in combinations(sel, 2):
                if ip(pts[a], pts[b]) > thresh:
                    ok = False
                    break
            if not ok:
                print("  model failed pair check", flush=True)
                continue
            used = name
            colour = sel
            break

    report = {
        "n": n,
        "n_d5": nD,
        "n_extras": nE,
        "n_nonedges": nonedges,
        "found_41": colour is not None,
        "solver": used,
        "comment": (
            "Exact 41-clique CNF on the rebuilt 1480-graph.  A model is a "
            "41-set.  UNSAT is not an emptiness proof without DRAT."
        ),
    }
    if colour is not None:
        chosen = [list(pts[i]) for i in colour]
        report["points"] = chosen
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / "code41.json").write_text(json.dumps({
            "n": 41,
            "model": "integer a in Z^5, a.a=32, edge iff a.b<=16",
            "method": f"sat:{used}",
            "points": chosen,
        }, indent=2) + "\n")
    (HERE / "clique41_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote clique41_sat.json found_41=", report["found_41"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
