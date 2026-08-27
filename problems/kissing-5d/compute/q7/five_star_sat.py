#!/usr/bin/env python3
"""Leftover-tight SAT on 5-star leftover hosts, with native DRAT.

q6 leftover-tight SAT on the four k=32 C-cutoff pools was unsat
without a stored DRAT.  This file writes those CNFs plus one
representative of each Aut(D5) orbit, runs native CaDiCaL 3.0.1,
and stores a binary DRAT.  Replay with write_cnf.py and
native_sat.py --proof --trim.

A model is a leftover 41-set (written to certs/code41.json).
UNSAT without a stored verified DRAT is residue for that CNF.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import (  # noqa: E402
    leftover_tight_cnf,
    load_graph,
    pool_for_stars,
    star_type,
    write_dimacs,
)
from native_sat import run_cadical, run_drat  # noqa: E402
from orbits import Q6_CUTOFF, REPS  # noqa: E402
from sphere import extras_and_groups  # noqa: E402

F = Fraction


def write_code41(extras, D, E, U, source, path: Path):
    Uset = set(U)
    pts = [[str(F(x, 4)) for x in extras[i]] for i in E]
    for r, p in enumerate(D):
        if r not in Uset:
            pts.append([str(F(x, 4)) for x in p])
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({
        "n": len(pts),
        "source": source,
        "n_extras": len(E),
        "n1": 40 - len(U),
        "points": pts,
    }, indent=2) + "\n")


def jobs_for(args):
    jobs = []
    if args.reps or args.all:
        for name, comb in REPS.items():
            jobs.append((name, comb))
    if args.q6 or args.all:
        for comb in Q6_CUTOFF:
            name = "q6_" + "".join(str(x) for x in comb)
            if any(tuple(comb) == tuple(c) for c in REPS.values()):
                name = [n for n, c in REPS.items() if tuple(c) == tuple(comb)][0]
            if (name, comb) not in jobs:
                jobs.append((name, comb))
    if args.stars:
        comb = tuple(int(x) for x in args.stars.split(","))
        name = args.name or "s" + "".join(str(x) for x in comb)
        jobs.append((name, comb))
    if not jobs:
        jobs = [(n, c) for n, c in REPS.items()]
        for comb in Q6_CUTOFF:
            if tuple(comb) not in REPS.values():
                jobs.append(("q6_" + "".join(str(x) for x in comb), comb))
    # unique by comb
    seen = set()
    out = []
    for name, comb in jobs:
        key = tuple(comb)
        if key in seen:
            continue
        seen.add(key)
        out.append((name, comb))
    return out


def decode_if_sat(G, comb, cnf_path: Path):
    """If cadical wrote a model, native_sat logs it; we re-solve with pysat
    only when sat so we can write code41.  Unsat path never needs this."""
    from pysat.solvers import Cadical195
    from pysat.formula import CNF
    U, local, local_g, local_miss = pool_for_stars(G, comb)
    cnf, _, _ = leftover_tight_cnf(G, local, local_g, local_miss, U)
    slv = Cadical195(bootstrap_with=cnf)
    sat = slv.solve()
    model = slv.get_model() if sat else None
    slv.delete()
    if not sat or model is None:
        return None
    true = {x for x in model if x > 0}
    E_local = [i for i in range(len(local)) if (i + 1) in true]
    E = [local[t] for t in E_local]
    Ubits = 0
    for i in E:
        Ubits |= G["masks"][i]
    Ulist = [r for r in range(40) if (Ubits >> r) & 1]
    return E, Ulist


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", action="store_true")
    ap.add_argument("--q6", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--stars", default="")
    ap.add_argument("--name", default="")
    ap.add_argument("--no-proof", action="store_true")
    ap.add_argument("--no-trim", action="store_true")
    args = ap.parse_args()

    G = load_graph()
    extras = G["extras"]
    D = G["D"]
    (HERE / "certs").mkdir(exist_ok=True)
    pools = []
    found = False
    for name, comb in jobs_for(args):
        U, local, local_g, local_miss = pool_for_stars(G, comb)
        cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
        cnf_path = HERE / "certs" / f"five_{name}.cnf"
        meta = write_dimacs(cnf, cnf_path)
        print(f"==== {name} stars={list(comb)} k={U.bit_count()} "
              f"nE={nL} vars={meta['vars']} =====", flush=True)
        proof = None if args.no_proof else HERE / "certs" / f"five_{name}.native.drat"
        clog = HERE / "certs" / f"five_{name}.cadical.log"
        crec = run_cadical(cnf_path, proof, clog)
        rec = {
            "name": name,
            "stars": list(comb),
            "type": list(star_type(comb)),
            "k": U.bit_count(),
            "n_extras": nL,
            "n_roots": nY,
            "cnf_vars": meta["vars"],
            "cnf_clauses": meta["clauses"],
            "cnf_sha256": meta["sha256"],
            "sat": crec["sat"],
            "cadical": crec,
            "found_41": False,
        }
        if proof is not None and proof.exists():
            rec["drat"] = proof.name
            rec["drat_bytes"] = proof.stat().st_size
            if crec["sat"] is False and not args.no_trim:
                tlog = HERE / "certs" / f"five_{name}.native.drat-trim.log"
                rec["drat_trim"] = run_drat(cnf_path, proof, tlog)
        if crec["sat"] is True:
            decoded = decode_if_sat(G, comb, cnf_path)
            if decoded:
                E, Ulist = decoded
                rec["n_sel"] = len(E)
                rec["n_U"] = len(Ulist)
                if len(E) >= len(Ulist) + 1 and len(Ulist) >= 19:
                    write_code41(extras, D, E, Ulist,
                                 f"q7 5-star SAT stars={list(comb)}",
                                 HERE / "certs" / "code41.json")
                    rec["found_41"] = True
                    found = True
        pools.append(rec)
        print(f"  sat={rec['sat']} trim={rec.get('drat_trim', {}).get('status')} "
              f"found_41={rec['found_41']}", flush=True)
        if found:
            break

    n_unsat = sum(1 for p in pools if p.get("sat") is False)
    n_verified = sum(1 for p in pools
                     if p.get("drat_trim", {}).get("status") == "VERIFIED")
    report = {
        "n_pools": len(pools),
        "found_41": found,
        "n_sat_unsat": n_unsat,
        "n_drat_verified": n_verified,
        "pools": pools,
        "comment": (
            "Leftover-tight SAT on 5-star hosts.  Native CaDiCaL 3.0.1 "
            "binary DRAT; Heule drat-trim.  UNSAT without a stored "
            "verified DRAT is residue.  Did not claim tau5=40."
        ),
    }
    (HERE / "five_star_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote five_star_sat.json found_41=", found,
          "unsat=", n_unsat, "verified=", n_verified)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
