#!/usr/bin/env python3
"""Enumerate and split on the C7-invariant 21-vertex neighbourhood.

The q2 maximum-cycle order-7 instance has one fixed vertex adjacent to three
7-cycles.  Its neighbourhood contains no K4 and no independent 5-set.  After
q2's cycle/phase symmetry breaking there are only 787 possible assignments
to the 30 edge-orbit variables inside that neighbourhood.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Cadical195

Q2 = Path(__file__).resolve().parents[1] / "q2"
sys.path.insert(0, str(Q2))
from orbit_sat import OrbitEncoding  # noqa: E402


def local_formula() -> tuple[OrbitEncoding, list[int], list[list[int]]]:
    obj = OrbitEncoding(43, 7, 6)
    obj.add_base_clauses()
    obj.add_degrees()
    obj.add_fixed_cycle_prefix(3)
    vertices = [obj.cyc_vertex(cycle, r) for cycle in range(3) for r in range(7)]
    projected = sorted(
        {
            obj.edge_var(u, v)
            for u, v in itertools.combinations(vertices, 2)
        }
    )

    base: set[tuple[int, ...]] = set()
    for subset in itertools.combinations(vertices, 4):
        base.add(
            tuple(
                sorted(
                    {
                        -obj.edge_var(u, v)
                        for u, v in itertools.combinations(subset, 2)
                    }
                )
            )
        )
    for subset in itertools.combinations(vertices, 5):
        base.add(
            tuple(
                sorted(
                    {
                        obj.edge_var(u, v)
                        for u, v in itertools.combinations(subset, 2)
                    }
                )
            )
        )

    # Build q2's symmetry constraints in their original order and retain the
    # clauses supported on the three selected cycles.  This preserves the
    # auxiliary-variable numbers used by the full CNF, so the local completion
    # proof can be appended directly to a proof of the full instance.
    selected_symmetry: list[list[int]] = []
    for block in ((0, 1, 2), (3, 4, 5)):
        for left, right in zip(block, block[1:]):
            begin = len(obj.enc.clauses)
            obj.enc.lex_leq(
                [obj.enc.var("cc", left, d) for d in range(1, 4)],
                [obj.enc.var("cc", right, d) for d in range(1, 4)],
            )
            if left < 3:
                selected_symmetry.extend(obj.enc.clauses[begin:])
    for cycle in range(1, 6):
        bits = [obj.enc.var("cb", 0, cycle, d) for d in range(7)]
        begin = len(obj.enc.clauses)
        for shift in range(1, 7):
            obj.enc.lex_leq(bits, [bits[(d + shift) % 7] for d in range(7)])
        if cycle < 3:
            selected_symmetry.extend(obj.enc.clauses[begin:])

    clauses = [list(clause) for clause in sorted(base)] + selected_symmetry
    return obj, projected, clauses


def enumerate_rows(projected: list[int], clauses: list[list[int]]) -> list[str]:
    rows: list[str] = []
    with Cadical195(bootstrap_with=clauses) as solver:
        while solver.solve():
            positive = {lit for lit in solver.get_model() if lit > 0}
            bits = "".join("1" if var in positive else "0" for var in projected)
            rows.append(bits)
            solver.add_clause([-var if var in positive else var for var in projected])
    return sorted(rows)


def literals(row: str, projected: list[int]) -> list[int]:
    return [var if bit == "1" else -var for bit, var in zip(row, projected)]


def write_dimacs(path: Path, nvars: int, clauses: list[list[int]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        stream.write(f"p cnf {nvars} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_cube(base: Path, target: Path, units: list[int]) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    with base.open() as source, target.open("w") as output:
        for line in source:
            if line.startswith("p cnf "):
                _, _, nvars, nclauses = line.split()
                output.write(f"p cnf {nvars} {int(nclauses) + len(units)}\n")
            else:
                output.write(line)
        for unit in units:
            output.write(f"{unit} 0\n")
    return hashlib.sha256(target.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert", type=Path)
    parser.add_argument("--completion-cnf", type=Path)
    parser.add_argument("--base-cnf", type=Path)
    parser.add_argument("--cube-cnf", type=Path)
    parser.add_argument("--cube-index", type=int)
    parser.add_argument("--solve-shard", type=int)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()

    started = time.monotonic()
    _, projected, clauses = local_formula()
    rows = enumerate_rows(projected, clauses)
    row_hash = hashlib.sha256("\n".join(rows).encode()).hexdigest()
    record: dict[str, object] = {
        "local_clauses": len(clauses),
        "projected_variables": projected,
        "rows": rows,
        "rows_sha256": row_hash,
        "status": "EXHAUSTED",
        "total": len(rows),
    }

    if args.completion_cnf:
        blockers = [[-lit for lit in literals(row, projected)] for row in rows]
        nvars = max(abs(lit) for clause in clauses for lit in clause)
        record["completion_cnf"] = str(args.completion_cnf)
        record["completion_cnf_sha256"] = write_dimacs(
            args.completion_cnf, nvars, clauses + blockers
        )

    if args.cube_index is not None:
        if args.base_cnf is None or args.cube_cnf is None:
            parser.error("--cube-index requires --base-cnf and --cube-cnf")
        if not 0 <= args.cube_index < len(rows):
            parser.error("cube index out of range")
        units = literals(rows[args.cube_index], projected)
        record["cube_index"] = args.cube_index
        record["cube_cnf"] = str(args.cube_cnf)
        record["cube_cnf_sha256"] = write_cube(args.base_cnf, args.cube_cnf, units)

    if args.solve_shard is not None:
        if args.base_cnf is None or args.results is None:
            parser.error("--solve-shard requires --base-cnf and --results")
        if not 0 <= args.solve_shard < args.shards:
            parser.error("shard index out of range")
        formula = CNF(from_file=args.base_cnf)
        results = []
        with Cadical195(bootstrap_with=formula.clauses) as solver:
            for index in range(args.solve_shard, len(rows), args.shards):
                before = solver.accum_stats().copy()
                t0 = time.monotonic()
                sat = solver.solve(assumptions=literals(rows[index], projected))
                elapsed = time.monotonic() - t0
                after = solver.accum_stats()
                delta = {key: after[key] - before.get(key, 0) for key in after}
                results.append(
                    {
                        "index": index,
                        "sec": round(elapsed, 3),
                        "stats": delta,
                        "status": "SAT" if sat else "UNSAT",
                    }
                )
                print(json.dumps(results[-1], sort_keys=True), flush=True)
                if sat:
                    break
        args.results.parent.mkdir(parents=True, exist_ok=True)
        args.results.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    record["enumeration_sec"] = round(time.monotonic() - started, 3)
    if args.cert:
        args.cert.parent.mkdir(parents=True, exist_ok=True)
        args.cert.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {key: value for key, value in record.items() if key != "rows"},
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
