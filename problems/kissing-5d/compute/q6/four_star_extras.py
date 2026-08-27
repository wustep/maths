#!/usr/bin/env python3
"""Leftover 41-set hosted by a 4-star union.

q5 emptied every 3-star host (extras ω ≤ 19).  A remaining 41-set in
the 1480-graph has star-cover at least 4, so its missed-union U sits
in some 4-star union U4.  This file searches each of the 210 pools:

    |E| >= 20,  |U| >= 19,  |E| >= |U| + 1,  U ⊆ U4.

B&B first (cliqueutil, leftover-aware only via the target).  SAT is
the leftover-tight model (y_r = union of selected missed roots).
A SAT model is written to certs/code41.json.  UNSAT without a stored
DRAT is residue for that pool.
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
Q5 = HERE.parent / "q5"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(Q5))

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


def leftover_sat(local, local_g, local_miss, U4, need=20, with_proof=False):
    """SAT: leftover-tight extras clique inside a 4-star pool."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF
    from pysat.solvers import Cadical195

    nL = len(local)
    roots = [r for r in range(40) if (U4 >> r) & 1]
    def vx(i):
        return i + 1

    def vy(t):
        return nL + t + 1

    cnf = CNF()
    by_g = {}
    for i, g in enumerate(local_g):
        by_g.setdefault(g, []).append(i)
    for vs in by_g.values():
        for a, b in combinations(vs, 2):
            cnf.append([-vx(a), -vx(b)])

    extras = leftover_sat.extras
    thresh = leftover_sat.thresh
    for i in range(nL):
        for j in range(i + 1, nL):
            if ip(extras[local[i]], extras[local[j]]) > thresh:
                cnf.append([-vx(i), -vx(j)])

    support = [[] for _ in roots]
    rpos = {r: t for t, r in enumerate(roots)}
    for i, m in enumerate(local_miss):
        mm = m
        while mm:
            r = (mm & -mm).bit_length() - 1
            mm &= mm - 1
            if r in rpos:
                cnf.append([-vx(i), vy(rpos[r])])
                support[rpos[r]].append(i)
    for t, vs in enumerate(support):
        cnf.append([-vy(t)] + [vx(i) for i in vs])

    top = nL + len(roots)
    card_y = CardEnc.atleast(
        lits=[vy(t) for t in range(len(roots))], bound=19,
        top_id=top, encoding=EncType.seqcounter,
    )
    cnf.extend(card_y.clauses)
    top = card_y.nv
    card_x = CardEnc.atleast(
        lits=[vx(i) for i in range(nL)], bound=need,
        top_id=top, encoding=EncType.seqcounter,
    )
    cnf.extend(card_x.clauses)
    # |E| >= |U| + 1: for each possible |U|=k in 19..|roots|,
    # if |U| >= k then |E| >= k+1.  Encoded as: not (|Y|>=k and |X|<=k).
    # Cheaper sequential: y-sum <= |X|-1.  Use pairwise
    # "if exactly the y's of size k then at least k+1 x".
    # Conservative cut already: |X| >= 20 and |Y| >= 19.
    # Add: for each r, cannot have all 20+ extras while avoiding a
    # small U — handled after decode.  Extra card: |X| - |Y| >= 1
    # via |X| + (nY - |Y|) >= nY + 1.
    nY = len(roots)
    card_diff = CardEnc.atleast(
        lits=[vx(i) for i in range(nL)] + [-vy(t) for t in range(nY)],
        bound=nY + 1,
        top_id=card_x.nv, encoding=EncType.seqcounter,
    )
    cnf.extend(card_diff.clauses)

    slv = Cadical195(bootstrap_with=cnf, with_proof=with_proof)
    sat = slv.solve()
    model = slv.get_model() if sat else None
    proof = slv.get_proof() if (with_proof and not sat) else None
    slv.delete()
    E_local = None
    U = None
    if sat and model:
        true = {x for x in model if x > 0}
        E_local = [i for i in range(nL) if vx(i) in true]
        U = [roots[t] for t in range(nY) if vy(t) in true]
    return {
        "sat": bool(sat),
        "n_vars": cnf.nv,
        "n_clauses": len(cnf.clauses),
        "extras_local": E_local,
        "U": U,
        "proof_lines": len(proof) if proof else 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat", action="store_true")
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--node-limit", type=int, default=200_000)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--k-filter", type=int, default=0,
                    help="0 = all; else only 4-star unions of this size")
    ap.add_argument("--max-pools", type=int, default=0)
    args = ap.parse_args()

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

    combs = list(combinations(range(10), 4))
    combs = [c for i, c in enumerate(combs) if i % args.nshards == args.shard]
    if args.max_pools:
        combs = combs[:args.max_pools]

    pools = []
    found = False
    for comb in combs:
        if found:
            break
        U4 = stars[comb[0]] | stars[comb[1]] | stars[comb[2]] | stars[comb[3]]
        k = U4.bit_count()
        if args.k_filter and k != args.k_filter:
            continue
        local = []
        local_g = []
        local_miss = []
        for i, m in enumerate(masks):
            if m & ~U4 == 0:
                local.append(i)
                local_g.append(seed_index[m])
                local_miss.append(m)
        nL = len(local)
        adj = [0] * nL
        for a in range(nL):
            ia = local[a]
            for b in range(a + 1, nL):
                if local_g[a] != local_g[b] and ip(extras[ia], extras[local[b]]) <= thresh:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        hit, best, nodes, complete = clique_search(
            adj, nL, target=20, node_limit=args.node_limit, seed_best=19,
        )
        rec = {
            "stars": list(comb),
            "k": k,
            "n_extras": nL,
            "n_seeds": len(set(local_g)),
            "bb_best": best,
            "bb_nodes": nodes,
            "bb_complete": complete,
            "bb_hit": bool(hit),
            "sat": None,
            "found_41": False,
        }
        E = None
        U = None
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
                             f"q6 4-star B&B stars={list(comb)}",
                             HERE / "certs" / "code41.json")
                rec["found_41"] = True
                found = True
        if (not rec["found_41"]) and (args.sat or not complete or hit):
            srec = leftover_sat(local, local_g, local_miss, U4,
                                need=20, with_proof=args.proof)
            rec["sat"] = srec["sat"]
            rec["cnf_vars"] = srec["n_vars"]
            rec["cnf_clauses"] = srec["n_clauses"]
            rec["proof_lines"] = srec["proof_lines"]
            if srec["sat"] and srec["extras_local"] is not None:
                E = [local[t] for t in srec["extras_local"]]
                U = srec["U"] or []
                Ubits = 0
                for i in E:
                    Ubits |= masks[i]
                U = [r for r in range(40) if (Ubits >> r) & 1]
                rec["n_sel"] = len(E)
                rec["n_U"] = len(U)
                if len(E) >= len(U) + 1 and len(U) >= 19:
                    write_code41(extras, D, E, U,
                                 f"q6 4-star SAT stars={list(comb)}",
                                 HERE / "certs" / "code41.json")
                    rec["found_41"] = True
                    found = True
        pools.append(rec)
        print(
            f"stars={list(comb)} k={k} nE={nL} best={best} "
            f"complete={complete} sat={rec['sat']} found_41={rec['found_41']}",
            flush=True,
        )

    n_bb_empty = sum(1 for p in pools if p["bb_complete"] and not p["bb_hit"])
    n_sat_unsat = sum(1 for p in pools if p["sat"] is False)
    n_decided = sum(1 for p in pools if p["found_41"] or p["bb_complete"]
                    or p["sat"] is False)
    suffix = ""
    if args.nshards > 1:
        suffix = f"_s{args.shard}"
    if args.k_filter:
        suffix += f"_k{args.k_filter}"
    report = {
        "n_pools": len(pools),
        "shard": args.shard,
        "nshards": args.nshards,
        "k_filter": args.k_filter,
        "found_41": found,
        "n_bb_complete_empty": n_bb_empty,
        "n_sat_unsat": n_sat_unsat,
        "n_decided": n_decided,
        "pools": pools,
        "comment": (
            "4-star hosted leftover extras.  A 20-clique with large U "
            "is not a 41-set.  SAT-unsat without DRAT is residue for "
            "that pool.  Did not claim tau5=40."
        ),
    }
    out = HERE / f"four_star_extras{suffix}.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out, "found_41=", found, "decided=", n_decided, "/",
          len(pools))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
