#!/usr/bin/env python3
"""Global leftover SAT |U|=19 with 4-star and empty-five-star forbids.

q6 emptied 4-star hosts.  q7 emptied type-(2,1) and type-(1,3) five-star
hosts.  This CNF forbids those unions.  A remaining model is a leftover
41-set hosted by a type-(0,5) five-star or with star-cover at least 6.

A model is a 41-set (certs/code41.json).  UNSAT without a stored
verified DRAT is residue.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent / "q5"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import global_leftover_cnf, load_graph, write_dimacs  # noqa: E402
from n1_leftover_sat import decode_model, write_code41  # noqa: E402
from native_sat import run_cadical, run_drat, run_kissat  # noqa: E402

EMPTY_FIVE = ((2, 1), (1, 3))
STEM = "n1_k19_star5_no21_no13"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=19)
    ap.add_argument("--solver", default="cadical",
                    choices=("cadical", "kissat", "both"))
    ap.add_argument("--no-proof", action="store_true")
    ap.add_argument("--no-trim", action="store_true")
    args = ap.parse_args()

    G = load_graph()
    inst = global_leftover_cnf(
        G, k=args.k, min_star_cover=5, forbid_five_types=EMPTY_FIVE,
    )
    cnf = inst["cnf"]
    (HERE / "certs").mkdir(exist_ok=True)
    cnf_path = HERE / "certs" / f"{STEM}.cnf"
    meta = write_dimacs(cnf, cnf_path)
    print(f"==== k={args.k} forbid (2,1)+(1,3) "
          f"vars={meta['vars']} clauses={meta['clauses']} "
          f"five_forbids={inst['n_five_forbids']} ====", flush=True)

    found = False
    report = {
        "k": args.k,
        "n1": 40 - args.k,
        "need_extras": args.k + 1,
        "min_star_cover": 5,
        "forbid_five_types": inst["forbid_five_types"],
        "n_five_forbids": inst["n_five_forbids"],
        "cnf_vars": meta["vars"],
        "cnf_clauses": meta["clauses"],
        "cnf_sha256": meta["sha256"],
        "found_41": False,
        "complete": False,
        "comment": (
            f"Global leftover SAT k={args.k} with 4-star and type-(2,1)/"
            "(1,3) five-star forbids.  A model is a 41-set.  UNSAT "
            "without a stored verified DRAT is residue.  Did not claim "
            "tau5=40."
        ),
    }

    if args.solver in ("cadical", "both"):
        proof = None if args.no_proof else HERE / "certs" / f"{STEM}.native.drat"
        clog = HERE / "certs" / f"{STEM}.cadical.log"
        crec = run_cadical(cnf_path, proof, clog)
        report["cadical"] = crec
        report["sat"] = crec["sat"]
        if proof is not None and proof.exists():
            report["drat"] = proof.name
            report["drat_bytes"] = proof.stat().st_size
            if crec["sat"] is False and not args.no_trim:
                tlog = HERE / "certs" / f"{STEM}.native.drat-trim.log"
                report["drat_trim"] = run_drat(cnf_path, proof, tlog)
                report["complete"] = (
                    report["drat_trim"].get("status") == "VERIFIED"
                )
        if crec["sat"] is True:
            from pysat.solvers import Cadical195
            slv = Cadical195(bootstrap_with=cnf)
            sat = slv.solve()
            model = slv.get_model() if sat else None
            slv.delete()
            if sat and model:
                E, U = decode_model(inst, model)
                write_code41(inst, E, U, HERE / "certs" / "code41.json")
                report["n_extras"] = len(E)
                report["n_U"] = len(U)
                report["found_41"] = True
                found = True

    if args.solver in ("kissat", "both") and not found:
        klog = HERE / "certs" / f"{STEM}.kissat.log"
        krec = run_kissat(cnf_path, klog)
        report["kissat"] = krec
        if args.solver == "kissat":
            report["sat"] = krec["sat"]
        if krec["sat"] is True:
            from pysat.solvers import Cadical195
            slv = Cadical195(bootstrap_with=cnf)
            sat = slv.solve()
            model = slv.get_model() if sat else None
            slv.delete()
            if sat and model:
                E, U = decode_model(inst, model)
                write_code41(inst, E, U, HERE / "certs" / "code41.json")
                report["n_extras"] = len(E)
                report["n_U"] = len(U)
                report["found_41"] = True
                found = True

    report["found_41"] = found
    (HERE / "leftover_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    (HERE / "leftover_sat_status.json").write_text(json.dumps({
        "k": args.k,
        "n1": 40 - args.k,
        "min_star_cover": 5,
        "forbid_five_types": report["forbid_five_types"],
        "cnf_vars": meta["vars"],
        "cnf_clauses": meta["clauses"],
        "found_41": found,
        "sat": report.get("sat"),
        "complete": report.get("complete"),
        "drat_trim": (report.get("drat_trim") or {}).get("status"),
        "comment": report["comment"],
    }, indent=2) + "\n")
    print("wrote leftover_sat.json sat=", report.get("sat"),
          "found_41=", found, "complete=", report.get("complete"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
