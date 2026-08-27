#!/usr/bin/env python3
"""SAT for a 41-set in the 1480-graph with n1 <= 21.

Same-missed extras are independent, so the extras part of a clique
picks at most one vertex per seed.  Let U be the union of the missed
D5-root sets of the selected extras.  Then

    n1 = 40 - |U|,    |E| + n1 >= 41  <=>  |E| >= |U| + 1.

q4 emptied |U| <= 18.  The leftover is |U| >= 19.

A SAT model is written to certs/code41.json.  UNSAT without a stored
DRAT is residue, not an emptiness proof.  Slice by k = |U|.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

F = Fraction

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
ROOT = HERE.parent
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(ROOT))

from sphere import extras_and_groups, ip  # noqa: E402


def build_instance(k: int):
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    groups = G["groups"]
    masks = G["masks"]
    thresh = G["thresh"]
    nE = len(extras)
    nD = len(D)
    seeds = list(groups)
    seed_index = {m: i for i, m in enumerate(seeds)}
    g_of = [seed_index[m] for m in masks]
    miss_bits = masks

    def vx(i):
        return i + 1

    def vy(r):
        return nE + r + 1

    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF

    cnf = CNF()
    # at most one extra per seed
    by_g = {}
    for i, g in enumerate(g_of):
        by_g.setdefault(g, []).append(i)
    for vs in by_g.values():
        for a, b in combinations(vs, 2):
            cnf.append([-vx(a), -vx(b)])

    for i in range(nE):
        for j in range(i + 1, nE):
            if ip(extras[i], extras[j]) > thresh:
                cnf.append([-vx(i), -vx(j)])

    # x_i -> y_r for r in miss(e_i); y_r -> some such x
    support = [[] for _ in range(nD)]
    for i, m in enumerate(miss_bits):
        mm = m
        while mm:
            r = (mm & -mm).bit_length() - 1
            mm &= mm - 1
            cnf.append([-vx(i), vy(r)])
            support[r].append(i)
    for r in range(nD):
        cnf.append([-vy(r)] + [vx(i) for i in support[r]])

    top = nE + nD
    card_y = CardEnc.equals(
        lits=[vy(r) for r in range(nD)], bound=k,
        top_id=top, encoding=EncType.seqcounter,
    )
    cnf.extend(card_y.clauses)
    top = card_y.nv
    card_x = CardEnc.atleast(
        lits=[vx(i) for i in range(nE)], bound=k + 1,
        top_id=top, encoding=EncType.seqcounter,
    )
    cnf.extend(card_x.clauses)
    return {
        "cnf": cnf,
        "nE": nE,
        "nD": nD,
        "extras": extras,
        "D": D,
        "miss_bits": miss_bits,
        "k": k,
    }


def decode_model(inst, model):
    true = {x for x in model if x > 0}
    E = [i for i in range(inst["nE"]) if (i + 1) in true]
    U = [r for r in range(inst["nD"]) if (inst["nE"] + r + 1) in true]
    return E, U


def write_code41(inst, E, U, path: Path):
    extras = inst["extras"]
    D = inst["D"]
    Uset = set(U)
    def scale(p):
        return [str(F(x, 4)) for x in p]

    pts = [scale(extras[i]) for i in E]
    for r, p in enumerate(D):
        if r not in Uset:
            pts.append(scale(p))
    path.write_text(json.dumps({
        "n": len(pts),
        "source": "q5 n1 leftover SAT",
        "k": inst["k"],
        "n_extras": len(E),
        "n1": 40 - len(U),
        "points": pts,
    }, indent=2) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=19, help="|U| slice; n1=40-k")
    ap.add_argument("--kmax", type=int, default=None,
                    help="run k..kmax inclusive")
    ap.add_argument("--solver", default="cadical195",
                    choices=("cadical195", "kissat404", "glucose4"))
    ap.add_argument("--write-cnf", action="store_true")
    args = ap.parse_args()
    kmax = args.kmax if args.kmax is not None else args.k
    (HERE / "certs").mkdir(exist_ok=True)

    slices = []
    found = False
    for k in range(args.k, kmax + 1):
        print(f"==== k={k} n1={40 - k} |E|>={k + 1} ====", flush=True)
        inst = build_instance(k)
        cnf = inst["cnf"]
        print(f"  vars={cnf.nv} clauses={len(cnf.clauses)}", flush=True)
        if args.write_cnf:
            cnf.to_file(str(HERE / "certs" / f"n1_k{k}.cnf"))

        if args.solver == "cadical195":
            from pysat.solvers import Cadical195
            slv = Cadical195(bootstrap_with=cnf, with_proof=True)
        elif args.solver == "kissat404":
            from pysat.solvers import Kissat404
            slv = Kissat404(bootstrap_with=cnf)
        else:
            from pysat.solvers import Glucose4
            slv = Glucose4(bootstrap_with=cnf)

        sat = slv.solve()
        model = slv.get_model() if sat else None
        proof = None
        if (not sat) and args.solver == "cadical195":
            proof = slv.get_proof()
        slv.delete()
        rec = {
            "k": k,
            "n1": 40 - k,
            "need_extras": k + 1,
            "sat": bool(sat),
            "cnf_vars": cnf.nv,
            "cnf_clauses": len(cnf.clauses),
            "solver": args.solver,
            "proof_lines": len(proof) if proof else 0,
        }
        if sat and model:
            E, U = decode_model(inst, model)
            rec["n_extras"] = len(E)
            rec["n_U"] = len(U)
            write_code41(inst, E, U, HERE / "certs" / "code41.json")
            rec["wrote"] = "certs/code41.json"
            found = True
            slices.append(rec)
            print(f"  SAT extras={len(E)} U={len(U)}", flush=True)
            break
        if proof:
            drat = HERE / "certs" / f"n1_k{k}.drat"
            drat.write_text("\n".join(proof) + "\n")
            rec["drat"] = drat.name
        print(f"  sat={sat} proof_lines={rec['proof_lines']}", flush=True)
        slices.append(rec)

    report = {
        "solver": args.solver,
        "k_lo": args.k,
        "k_hi": kmax,
        "found_41": found,
        "slices": slices,
        "comment": (
            "Leftover n1<=21 is |U|>=19.  A model is a 41-set.  UNSAT "
            "without a stored DRAT is residue."
        ),
    }
    out = HERE / f"n1_leftover_sat_k{args.k}.json"
    if args.kmax is not None:
        out = HERE / f"n1_leftover_sat_k{args.k}_{kmax}.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out, "found_41=", found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
