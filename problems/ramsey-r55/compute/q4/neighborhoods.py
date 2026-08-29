#!/usr/bin/env python3
"""Enumerate the invariant neighbourhood of a leftover fixed-prefix instance.

The selected p-cycles adjacent to fixed vertex 0 induce a neighbourhood with
no K4 and no independent 5-set.  After the existing cycle/phase symmetry
breaking, the SAT models of that local formula are the cubes for a later
conquer pass.  This does not change q2's encoding of the full instance.
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


def local_formula(p: int, cycles: int, selected: int, p5_symbreak: bool):
    obj = OrbitEncoding(43, p, cycles)
    obj.add_base_clauses()
    obj.add_degrees()
    obj.add_fixed_cycle_prefix(selected)
    if p5_symbreak:
        obj.add_p5_symmetry_breaking()
    else:
        obj.add_anchor_symmetry_breaking(selected)

    vertices = [obj.cyc_vertex(cycle, r) for cycle in range(selected) for r in range(p)]
    projected = sorted(
        {obj.edge_var(u, v) for u, v in itertools.combinations(vertices, 2)}
    )

    base: set[tuple[int, ...]] = set()
    for subset in itertools.combinations(vertices, 4):
        base.add(
            tuple(sorted({-obj.edge_var(u, v) for u, v in itertools.combinations(subset, 2)}))
        )
    for subset in itertools.combinations(vertices, 5):
        base.add(
            tuple(sorted({obj.edge_var(u, v) for u, v in itertools.combinations(subset, 2)}))
        )

    local_vars = set(projected)
    selected_symmetry = [
        clause
        for clause in obj.enc.clauses
        if clause and all(abs(lit) in local_vars or abs(lit) > len(obj.enc.names) for lit in clause)
        and any(abs(lit) in local_vars for lit in clause)
    ]
    # Keep only the projected clique/independent-set constraints for a
    # self-contained local formula; symmetry is already baked into the full CNF
    # cubes via the original instance.
    clauses = [list(clause) for clause in sorted(base)]
    return obj, projected, clauses, selected_symmetry


def enumerate_rows(projected: list[int], clauses: list[list[int]], limit: int | None = None) -> list[str]:
    rows: list[str] = []
    with Cadical195(bootstrap_with=clauses) as solver:
        while solver.solve():
            positive = {lit for lit in solver.get_model() if lit > 0}
            bits = "".join("1" if var in positive else "0" for var in projected)
            rows.append(bits)
            solver.add_clause([-var if var in positive else var for var in projected])
            if limit is not None and len(rows) >= limit:
                break
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
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--cycles", type=int, required=True)
    parser.add_argument("--fixed-cycle-count", type=int, required=True)
    parser.add_argument("--p5-symbreak", action="store_true")
    parser.add_argument("--cert", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    started = time.monotonic()
    _, projected, clauses, _ = local_formula(
        args.p, args.cycles, args.fixed_cycle_count, args.p5_symbreak
    )
    rows = enumerate_rows(projected, clauses, args.limit)
    record = {
        "cycles": args.cycles,
        "fixed_cycle_count": args.fixed_cycle_count,
        "local_clauses": len(clauses),
        "p": args.p,
        "projected_variables": projected,
        "rows_sha256": hashlib.sha256("\n".join(rows).encode()).hexdigest(),
        "status": "EXHAUSTED" if args.limit is None else "PARTIAL",
        "total": len(rows),
        "enumeration_sec": round(time.monotonic() - started, 3),
    }
    if args.limit is None:
        record["rows"] = rows
    if args.cert:
        args.cert.parent.mkdir(parents=True, exist_ok=True)
        args.cert.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k != "rows"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
