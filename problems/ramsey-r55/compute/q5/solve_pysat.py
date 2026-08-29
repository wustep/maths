#!/usr/bin/env python3
"""Run one PySAT backend on a DIMACS instance and optionally save a proof/model."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Cadical195, Glucose4, Lingeling, MapleChrono


SOLVERS = {
    "cadical195": Cadical195,
    "glucose4": Glucose4,
    "lingeling": Lingeling,
    "maplechrono": MapleChrono,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--solver", choices=sorted(SOLVERS), required=True)
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()

    started = time.monotonic()
    formula = CNF(from_file=args.cnf)
    loaded = time.monotonic()
    solver_type = SOLVERS[args.solver]
    with solver_type(
        bootstrap_with=formula.clauses,
        use_timer=True,
        with_proof=args.proof is not None,
    ) as solver:
        status = solver.solve()
        solved = time.monotonic()
        record = {
            "cnf": str(args.cnf),
            "clauses": len(formula.clauses),
            "load_sec": round(loaded - started, 3),
            "solve_sec": round(solved - loaded, 3),
            "solver": args.solver,
            "status": "SAT" if status else "UNSAT",
            "stats": solver.accum_stats(),
            "variables": formula.nv,
        }
        if status and args.model:
            args.model.parent.mkdir(parents=True, exist_ok=True)
            args.model.write_text(" ".join(map(str, solver.get_model())) + " 0\n")
            record["model"] = str(args.model)
        if not status and args.proof:
            proof = solver.get_proof()
            if proof is None:
                raise RuntimeError(f"{args.solver} did not return a proof")
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text("\n".join(proof) + "\n")
            record["proof"] = str(args.proof)
            record["proof_lines"] = len(proof)
        print(json.dumps(record, sort_keys=True), flush=True)
    return 10 if status else 20


if __name__ == "__main__":
    raise SystemExit(main())
