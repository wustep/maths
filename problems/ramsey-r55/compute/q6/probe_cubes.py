#!/usr/bin/env python3
"""Incremental Cadical probe of neighbourhood cubes (search only)."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Cadical195

from neighborhoods import literals


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-cnf", type=Path, required=True)
    parser.add_argument("--neighborhoods", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()

    data = json.loads(args.neighborhoods.read_text())
    rows = data["rows"]
    projected = data["projected_variables"]
    formula = CNF(from_file=args.base_cnf)
    results = []
    started = time.monotonic()
    with Cadical195(bootstrap_with=formula.clauses) as solver:
        load = time.monotonic()
        print(json.dumps({"loaded_sec": round(load - started, 3), "clauses": len(formula.clauses)}), flush=True)
        for index, row in enumerate(rows):
            if index >= args.limit:
                break
            t0 = time.monotonic()
            sat = solver.solve(assumptions=literals(row, projected))
            rec = {
                "index": index,
                "sec": round(time.monotonic() - t0, 3),
                "status": "SAT" if sat else "UNSAT",
            }
            results.append(rec)
            print(json.dumps(rec, sort_keys=True), flush=True)
            if sat:
                break
    if args.results:
        args.results.parent.mkdir(parents=True, exist_ok=True)
        args.results.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
