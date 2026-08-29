#!/usr/bin/env python3
"""Global leftover SAT |U|=19 (q8 encoding, type-(2,1)/(1,3) forbids)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q8 = HERE.parent / "q8"
sys.path.insert(0, str(Q8))
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent / "q5"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import global_leftover_cnf, load_graph  # noqa: E402
from n1_leftover_sat import decode_model, write_code41  # noqa: E402
from native_sat import run_cadical, run_drat, run_kissat  # noqa: E402

import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("q9_write_cnf", HERE / "write_cnf.py")
q9cnf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q9cnf)
GLOBAL_SHA = q9cnf.GLOBAL_SHA
write_global = q9cnf.write_global

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
    meta = write_global(G)
    inst = global_leftover_cnf(
        G, k=args.k, min_star_cover=5, forbid_five_types=EMPTY_FIVE,
    )
    cnf = inst["cnf"]
    cnf_path = HERE / "certs" / f"{STEM}.cnf"

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
        "same_as_q8": meta["sha256"] == GLOBAL_SHA,
        "found_41": False,
        "complete": False,
        "comment": (
            f"Global leftover SAT k={args.k} with 4-star and type-(2,1)/"
            "(1,3) five-star forbids. Encoder is q8/cnfutil.py. A model "
            "is a 41-set. UNSAT without a stored verified DRAT is residue. "
            "Did not claim tau5=40."
        ),
    }

    if args.solver in ("cadical", "both"):
        proof = None if args.no_proof else HERE / "certs" / f"{STEM}.native.drat"
        crec = run_cadical(cnf_path, proof, HERE / "certs" / f"{STEM}.cadical.log")
        report["cadical"] = crec
        report["sat"] = crec["sat"]
        if proof is not None and proof.exists():
            report["drat"] = proof.name
            report["drat_bytes"] = proof.stat().st_size
            if crec["sat"] is False and not args.no_trim:
                report["drat_trim"] = run_drat(
                    cnf_path, proof, HERE / "certs" / f"{STEM}.native.drat-trim.log",
                )
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
        krec = run_kissat(cnf_path, HERE / "certs" / f"{STEM}.kissat.log")
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
