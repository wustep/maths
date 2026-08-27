#!/usr/bin/env python3
"""Extras clique in each leftover-tight 3-star pool.

seed_graph.json: every 3-star union is leftover-tight — 80 pools with
a seed-clique of size 22 and union 21, 40 with (23, 22).  A seed-clique
is only a compatibility pool.  A 41-set hosted by the pool is an extras
clique E with miss(E)subseteq Ustar and |E| >= |U|+1, |U|>=19.

q4 emptied |U|<=18, so it is enough to hunt |E| >= |Ustar|+1 inside
each pool (then |U| <= |Ustar| gives |E| >= |U|+1 automatically).

A SAT model is written to certs/code41.json.  UNSAT without a stored
DRAT is residue for that pool, not an emptiness proof of the whole
leftover n1<=21 slice.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from cliqueutil import clique_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402

F = Fraction


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            assert bits.bit_count() == 8
            out.append(bits)
    return out


def scale(p):
    return [str(F(x, 4)) for x in p]


def write_code41(extras, D, E, U, source, path: Path):
    Uset = set(U)
    pts = [scale(extras[i]) for i in E]
    for r, p in enumerate(D):
        if r not in Uset:
            pts.append(scale(p))
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({
        "n": len(pts),
        "source": source,
        "n_extras": len(E),
        "n1": 40 - len(U),
        "points": pts,
    }, indent=2) + "\n")


def extras_sat(n, adj_ok, by_g, need, with_proof=False):
    """SAT: pick >= need extras, at most one per seed, pairwise kissing."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF
    from pysat.solvers import Cadical195

    cnf = CNF()
    for vs in by_g.values():
        for a, b in combinations(vs, 2):
            cnf.append([-(a + 1), -(b + 1)])
    for i in range(n):
        for j in range(i + 1, n):
            if not adj_ok[i][j]:
                cnf.append([-(i + 1), -(j + 1)])
    card = CardEnc.atleast(
        lits=list(range(1, n + 1)), bound=need,
        encoding=EncType.seqcounter,
    )
    cnf.extend(card.clauses)
    slv = Cadical195(bootstrap_with=cnf, with_proof=with_proof)
    sat = slv.solve()
    model = slv.get_model() if sat else None
    proof = slv.get_proof() if (with_proof and not sat) else None
    slv.delete()
    E = None
    if sat and model:
        true = {x for x in model if x > 0}
        E = [i for i in range(n) if (i + 1) in true]
    return {
        "sat": bool(sat),
        "n_vars": cnf.nv,
        "n_clauses": len(cnf.clauses),
        "extras_local": E,
        "proof_lines": len(proof) if proof else 0,
        "proof": proof,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat", action="store_true",
                    help="Cadical on each pool (default: B&B then SAT if incomplete)")
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--node-limit", type=int, default=400_000)
    ap.add_argument("--max-pools", type=int, default=0,
                    help="0 = all 120")
    args = ap.parse_args()

    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    groups = G["groups"]
    masks = G["masks"]
    thresh = G["thresh"]
    seed_list = list(groups)
    assert len(seed_list) == 240
    seed_index = {m: i for i, m in enumerate(seed_list)}
    stars = stars_of(D)

    witness = json.loads((HERE / "seed_graph.json").read_text())
    w = witness["triple_star_leftover"]["witness"]
    w_seeds = w["seed_clique"]

    # --- witness 22-seed extras SAT (one extra per seed, need 22) ---
    w_pool = []
    w_g = []
    for gi in w_seeds:
        m = seed_list[gi]
        for p in groups[m]:
            w_pool.append(p)
            w_g.append(gi)
    nW = len(w_pool)
    by_g = {}
    for i, g in enumerate(w_g):
        by_g.setdefault(g, []).append(i)
    adj_ok = [[False] * nW for _ in range(nW)]
    for i in range(nW):
        adj_ok[i][i] = True
        for j in range(i + 1, nW):
            if w_g[i] != w_g[j] and ip(w_pool[i], w_pool[j]) <= thresh:
                adj_ok[i][j] = adj_ok[j][i] = True
    wsat = extras_sat(nW, adj_ok, by_g, need=22, with_proof=args.proof)
    witness_rec = {
        "n_seeds": 22,
        "n_extras": nW,
        "need": 22,
        "sat": wsat["sat"],
        "cnf_vars": wsat["n_vars"],
        "cnf_clauses": wsat["n_clauses"],
        "proof_lines": wsat["proof_lines"],
        "found_41": False,
    }
    found = False
    if wsat["sat"] and wsat["extras_local"]:
        Epts = [w_pool[i] for i in wsat["extras_local"]]
        Ubits = 0
        for p in Epts:
            for r, root in enumerate(D):
                if ip(p, root) > thresh:
                    Ubits |= 1 << r
        U = [r for r in range(40) if (Ubits >> r) & 1]
        if len(Epts) >= len(U) + 1 and len(U) >= 19:
            eidx = [extras.index(p) for p in Epts]
            write_code41(extras, D, eidx, U,
                         "q5 triple-star witness extras SAT",
                         HERE / "certs" / "code41.json")
            witness_rec["found_41"] = True
            witness_rec["n_extras_sel"] = len(Epts)
            witness_rec["n_U"] = len(U)
            found = True

    print(f"witness sat={wsat['sat']} found_41={witness_rec['found_41']}",
          flush=True)

    pools = []
    triples = list(combinations(range(10), 3))
    if args.max_pools:
        triples = triples[:args.max_pools]

    for comb in triples:
        if found:
            break
        Ustar = stars[comb[0]] | stars[comb[1]] | stars[comb[2]]
        k = Ustar.bit_count()
        need = k + 1
        local = []
        local_g = []
        local_miss = []
        for i, p in enumerate(extras):
            m = masks[i]
            if m & ~Ustar == 0:
                local.append(i)
                local_g.append(seed_index[m])
                local_miss.append(m)
        nL = len(local)
        by = {}
        for t, g in enumerate(local_g):
            by.setdefault(g, []).append(t)
        # B&B on extras
        adj = [0] * nL
        for a in range(nL):
            ia = local[a]
            for b in range(a + 1, nL):
                if local_g[a] != local_g[b] and ip(extras[ia], extras[local[b]]) <= thresh:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        hit, best, nodes, complete = clique_search(
            adj, nL, target=need, node_limit=args.node_limit,
            seed_best=max(0, need - 4),
        )
        rec = {
            "stars": list(comb),
            "k": k,
            "need": need,
            "n_extras": nL,
            "n_seeds": len(by),
            "bb_best": best,
            "bb_nodes": nodes,
            "bb_complete": complete,
            "bb_hit": bool(hit),
            "sat": None,
            "found_41": False,
        }
        E_local = hit
        if hit is None and (args.sat or not complete):
            adj_ok = [[False] * nL for _ in range(nL)]
            for a in range(nL):
                adj_ok[a][a] = True
                for b in range(a + 1, nL):
                    if (adj[a] >> b) & 1:
                        adj_ok[a][b] = adj_ok[b][a] = True
            srec = extras_sat(nL, adj_ok, by, need=need,
                              with_proof=args.proof)
            rec["sat"] = srec["sat"]
            rec["cnf_vars"] = srec["n_vars"]
            rec["cnf_clauses"] = srec["n_clauses"]
            rec["proof_lines"] = srec["proof_lines"]
            E_local = srec["extras_local"]
        if E_local:
            E = [local[t] for t in E_local]
            Ubits = 0
            for i in E:
                Ubits |= masks[i]
            U = [r for r in range(40) if (Ubits >> r) & 1]
            rec["n_sel"] = len(E)
            rec["n_U"] = len(U)
            if len(E) >= len(U) + 1 and len(U) >= 19:
                write_code41(extras, D, E, U,
                             f"q5 triple-star extras stars={list(comb)}",
                             HERE / "certs" / "code41.json")
                rec["found_41"] = True
                found = True
        pools.append(rec)
        print(
            f"stars={list(comb)} k={k} nE={nL} best={best} "
            f"complete={complete} sat={rec['sat']} found_41={rec['found_41']}",
            flush=True,
        )

    n_complete = sum(1 for p in pools if p["bb_complete"] or p["sat"] is False
                     or p["found_41"])
    n_sat_unsat = sum(1 for p in pools if p["sat"] is False)
    n_bb_empty = sum(1 for p in pools if p["bb_complete"] and not p["bb_hit"])
    report = {
        "n_pools": len(pools),
        "n_expected": 120 if not args.max_pools else args.max_pools,
        "witness": witness_rec,
        "found_41": found,
        "n_bb_complete_empty": n_bb_empty,
        "n_sat_unsat": n_sat_unsat,
        "n_decided": n_complete,
        "pools": pools,
        "comment": (
            "3-star hosted leftover extras.  A seed-clique is not a 41-code. "
            "bb_complete empty or SAT-unsat-without-DRAT is residue for that "
            "pool unless a DRAT is stored.  This does not empty the whole "
            "n1<=21 leftover and does not claim tau5=40."
        ),
    }
    (HERE / "triple_star_extras.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print("wrote triple_star_extras.json found_41=", found,
          "decided=", n_complete, "/", len(pools))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
