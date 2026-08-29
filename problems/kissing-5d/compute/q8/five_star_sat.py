#!/usr/bin/env python3
"""Leftover-tight SAT on the type-(0,5) five-star orbit representative.

q7 emptied types (2,1) and (1,3).  Remaining 5-star leftover hosts are
the 32 type-(0,5) pools (k=30, 625 extras).  Aut(D5) is transitive on
that type (q7 orbits.json).  Native CaDiCaL binary DRAT + Heule
drat-trim, or a Kissat probe without a proof.

A model is a leftover 41-set (certs/code41.json).  UNSAT without a
stored verified DRAT is residue.
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

from cnfutil import leftover_tight_cnf, load_graph, pool_for_stars, write_dimacs  # noqa: E402
from native_sat import run_cadical, run_drat, run_kissat  # noqa: E402
from orbits import REPS  # noqa: E402

F = Fraction
K30 = REPS["k30_n0_5"]


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


def decode_if_sat(G):
    from pysat.solvers import Cadical195
    U, local, local_g, local_miss = pool_for_stars(G, K30)
    cnf, _, _ = leftover_tight_cnf(G, local, local_g, local_miss, U)
    slv = Cadical195(bootstrap_with=cnf)
    sat = slv.solve()
    model = slv.get_model() if sat else None
    slv.delete()
    if not sat or model is None:
        return None
    true = {x for x in model if x > 0}
    E = [local[i] for i in range(len(local)) if (i + 1) in true]
    Ubits = 0
    for i in E:
        Ubits |= G["masks"][i]
    Ulist = [r for r in range(40) if (Ubits >> r) & 1]
    return E, Ulist


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", default="cadical", choices=("cadical", "kissat"))
    ap.add_argument("--no-proof", action="store_true")
    ap.add_argument("--no-trim", action="store_true")
    args = ap.parse_args()

    G = load_graph()
    U, local, local_g, local_miss = pool_for_stars(G, K30)
    cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
    (HERE / "certs").mkdir(exist_ok=True)
    cnf_path = HERE / "certs" / "five_k30_n0_5.cnf"
    meta = write_dimacs(cnf, cnf_path)
    print(f"==== k30_n0_5 k={U.bit_count()} nE={nL} vars={meta['vars']} ====",
          flush=True)

    rec = {
        "name": "k30_n0_5",
        "stars": list(K30),
        "type": [0, 5],
        "k": U.bit_count(),
        "n_extras": nL,
        "n_roots": nY,
        "cnf_vars": meta["vars"],
        "cnf_clauses": meta["clauses"],
        "cnf_sha256": meta["sha256"],
        "found_41": False,
        "complete": False,
    }
    if args.solver == "kissat":
        klog = HERE / "certs" / "five_k30_n0_5.kissat.log"
        krec = run_kissat(cnf_path, klog)
        rec["kissat"] = krec
        rec["sat"] = krec["sat"]
    else:
        proof = None if args.no_proof else HERE / "certs" / "five_k30_n0_5.native.drat"
        clog = HERE / "certs" / "five_k30_n0_5.cadical.log"
        crec = run_cadical(cnf_path, proof, clog)
        rec["cadical"] = crec
        rec["sat"] = crec["sat"]
        if proof is not None and proof.exists():
            rec["drat"] = proof.name
            rec["drat_bytes"] = proof.stat().st_size
            if crec["sat"] is False and not args.no_trim:
                tlog = HERE / "certs" / "five_k30_n0_5.native.drat-trim.log"
                rec["drat_trim"] = run_drat(cnf_path, proof, tlog)
                rec["complete"] = rec["drat_trim"].get("status") == "VERIFIED"
    if rec.get("sat") is True:
        decoded = decode_if_sat(G)
        if decoded:
            E, Ulist = decoded
            rec["n_sel"] = len(E)
            rec["n_U"] = len(Ulist)
            if len(E) >= len(Ulist) + 1 and len(Ulist) >= 19:
                write_code41(G["extras"], G["D"], E, Ulist,
                             "q8 type-(0,5) leftover SAT",
                             HERE / "certs" / "code41.json")
                rec["found_41"] = True

    report = {
        "n_pools": 1,
        "orbit_size": 32,
        "found_41": rec["found_41"],
        "n_sat_unsat": 1 if rec.get("sat") is False else 0,
        "n_drat_verified": 1 if rec.get("complete") else 0,
        "complete": bool(rec.get("complete")),
        "pools": [rec],
        "comment": (
            "Leftover-tight SAT on the type-(0,5) orbit representative. "
            " Native CaDiCaL 3.0.1 binary DRAT; Heule drat-trim. "
            " Aut transitivity empties all 32 hosts if verified unsat. "
            " Did not claim tau5=40."
        ),
    }
    (HERE / "five_star_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    (HERE / "certs" / "five_k30_n0_5.sat.json").write_text(
        json.dumps(rec, indent=2) + "\n"
    )
    print("wrote five_star_sat.json sat=", rec.get("sat"),
          "found_41=", rec["found_41"], "complete=", rec.get("complete"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
