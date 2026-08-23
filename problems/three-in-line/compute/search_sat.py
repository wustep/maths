#!/usr/bin/env python3
"""PySAT CNF search for a canonical odd-order rct4 instance.

The original 1-indexed SAT variables are the rct4 orbit variables from
``rct4_model.py``.  Auxiliary variables are introduced only by sequential
cardinality counters.  Weighted line inequalities have coefficients at most
two and are reduced exactly to:

* at-most-one among coefficient-two literals;
* incompatibility between coefficient-two and coefficient-one literals; and
* at-most-two among coefficient-one literals.

The emitted DIMACS file is a complete, independently reusable encoding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pysat
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from rct4_model import (
    Rct4Geometry,
    build_rct4_geometry,
    column_signature,
    reduced_line_signatures,
    row_signature,
    selected_points,
)


HEADER_WIDTH = 80


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ClauseSink:
    """Send clauses to a solver and, optionally, a seekable DIMACS file."""

    def __init__(self, solver: Solver, path: Path | None):
        self.solver = solver
        self.path = path
        self.handle = None
        self.clauses = 0
        self.literals = 0
        self.max_var = 0
        self.lengths: Counter[int] = Counter()
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.handle = path.open("w+", encoding="ascii")
            self.handle.write("c placeholder".ljust(HEADER_WIDTH - 1) + "\n")

    def add(self, clause: Iterable[int]) -> None:
        materialized = list(clause)
        if not materialized:
            raise ValueError("refusing to emit an empty clause unexpectedly")
        self.solver.add_clause(materialized)
        self.clauses += 1
        self.literals += len(materialized)
        self.lengths[len(materialized)] += 1
        self.max_var = max(self.max_var, *(abs(literal) for literal in materialized))
        if self.handle is not None:
            self.handle.write(" ".join(map(str, materialized)) + " 0\n")

    def add_encoding(self, encoding) -> None:
        for clause in encoding.clauses:
            self.add(clause)

    def finish(self, number_of_variables: int) -> None:
        self.max_var = max(self.max_var, number_of_variables)
        if self.handle is None:
            return
        header = f"p cnf {number_of_variables} {self.clauses}"
        if len(header) >= HEADER_WIDTH:
            raise AssertionError("DIMACS header overflow")
        self.handle.seek(0)
        self.handle.write(header.ljust(HEADER_WIDTH - 1) + "\n")
        self.handle.close()
        self.handle = None


class CnfBuilder:
    def __init__(self, sink: ClauseSink, original_variables: int):
        self.sink = sink
        self.top_id = original_variables

    def add_at_most(self, literals: list[int], bound: int) -> None:
        if len(literals) <= bound:
            return
        if bound == 1 and len(literals) <= 6:
            for i, left in enumerate(literals):
                for right in literals[i + 1 :]:
                    self.sink.add((-left, -right))
            return
        if bound == 2 and len(literals) == 3:
            self.sink.add(tuple(-literal for literal in literals))
            return
        encoding = CardEnc.atmost(
            lits=literals,
            bound=bound,
            top_id=self.top_id,
            encoding=EncType.seqcounter,
        )
        self.top_id = encoding.nv
        self.sink.add_encoding(encoding)

    def add_equals(self, literals: list[int], bound: int) -> None:
        encoding = CardEnc.equals(
            lits=literals,
            bound=bound,
            top_id=self.top_id,
            encoding=EncType.seqcounter,
        )
        self.top_id = encoding.nv
        self.sink.add_encoding(encoding)

    def add_weighted_at_most_two(self, signature: tuple[tuple[int, int], ...]) -> None:
        singles: list[int] = []
        doubles: list[int] = []
        for orbit_id, coefficient in signature:
            literal = orbit_id + 1
            if coefficient == 1:
                singles.append(literal)
            elif coefficient == 2:
                doubles.append(literal)
            else:
                # Such an orbit alone would place at least three points on the
                # line, so it must be false.
                self.sink.add((-literal,))

        self.add_at_most(doubles, 1)
        for double in doubles:
            for single in singles:
                self.sink.add((-double, -single))
        self.add_at_most(singles, 2)


def literals_from_signature(signature: tuple[tuple[int, int], ...]) -> list[int]:
    # Cardinality encoders operate on literal occurrences. Repeating a
    # literal exactly preserves an orbit's incidence multiplicity; this is
    # needed for centre rows/columns, which can meet one rct4 orbit twice.
    return [
        orbit_id + 1
        for orbit_id, coefficient in signature
        for _ in range(coefficient)
    ]


def build_cnf(
    n: int,
    solver: Solver,
    dimacs_path: Path | None,
) -> tuple[ClauseSink, CnfBuilder, Rct4Geometry, dict]:
    geometry = build_rct4_geometry(n)
    signatures, line_stats = reduced_line_signatures(geometry)
    sink = ClauseSink(solver, dimacs_path)
    builder = CnfBuilder(sink, len(geometry.orbits))

    for signature in signatures:
        builder.add_weighted_at_most_two(signature)

    for row in range(n):
        builder.add_equals(literals_from_signature(row_signature(geometry, row)), 2)
    for column in range(n):
        builder.add_equals(literals_from_signature(column_signature(geometry, column)), 2)

    builder.add_equals([orbit_id + 1 for orbit_id in geometry.diagonal_orbits], 1)
    builder.add_equals(
        [orbit_id + 1 for orbit_id in geometry.off_diagonal_orbits],
        (n - 1) // 2,
    )
    sink.finish(builder.top_id)

    metadata = {
        "n": n,
        "target_points": 2 * n,
        "symmetry": "canonical-rct4",
        "fixed_empty": "anti-diagonal",
        "original_variables": len(geometry.orbits),
        "auxiliary_variables": builder.top_id - len(geometry.orbits),
        "cnf_variables": builder.top_id,
        "cnf_clauses": sink.clauses,
        "cnf_literals": sink.literals,
        "clause_length_histogram": dict(sorted(sink.lengths.items())),
        "line_statistics": line_stats.__dict__,
    }
    return sink, builder, geometry, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=71)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--solver", default="kissat404")
    parser.add_argument("--output", type=Path, default=Path("n71-142.txt"))
    parser.add_argument("--run-json", type=Path, default=Path("kissat-run.json"))
    parser.add_argument("--write-cnf", type=Path)
    parser.add_argument("--random-phases", action="store_true")
    parser.add_argument(
        "--phase-witness",
        type=Path,
        help="phase every orbit wholly present in this partial point set true",
    )
    return parser.parse_args()


def phased_orbits(geometry: Rct4Geometry, path: Path) -> set[int]:
    points: set[tuple[int, int]] = set()
    for line_number, raw_line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        fields = raw_line.split()
        if not fields:
            continue
        if len(fields) != 2:
            raise ValueError(f"{path}:{line_number}: expected two coordinates")
        points.add((int(fields[0]), int(fields[1])))

    selected: set[int] = set()
    for orbit_id, orbit in enumerate(geometry.orbits):
        incidence = sum(point in points for point in orbit)
        if incidence == len(orbit):
            selected.add(orbit_id)
        elif incidence:
            raise ValueError(f"{path}: partial incidence with rct4 orbit {orbit_id}")
    if sum(len(geometry.orbits[orbit_id]) for orbit_id in selected) != len(points):
        raise ValueError(f"{path}: contains fixed-empty or out-of-grid points")
    return selected


def main() -> int:
    args = parse_args()
    started = utc_now()
    process_start = time.monotonic()

    with Solver(name=args.solver, use_timer=True) as solver:
        solver.configure({"seed": args.seed})
        sink, builder, geometry, metadata = build_cnf(args.n, solver, args.write_cnf)
        build_seconds = time.monotonic() - process_start

        positive_phases = (
            phased_orbits(geometry, args.phase_witness)
            if args.phase_witness is not None
            else set()
        )
        if args.random_phases or positive_phases:
            rng = random.Random(args.seed)
            phases = [
                orbit_id + 1
                if orbit_id in positive_phases or (args.random_phases and rng.getrandbits(1))
                else -(orbit_id + 1)
                for orbit_id in range(len(geometry.orbits))
            ]
            solver.set_phases(phases)

        print(json.dumps({"event": "cnf-built", "build_seconds": build_seconds, **metadata}, sort_keys=True))
        solve_start = time.monotonic()
        timer = threading.Timer(args.seconds, solver.interrupt)
        timer.daemon = True
        timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
        solve_seconds = time.monotonic() - solve_start
        stats = solver.accum_stats()

        if answer is True:
            status = "SAT"
        elif answer is False:
            status = "UNSAT"
        else:
            status = "UNKNOWN"

        result: dict = {
            **metadata,
            "started_utc": started,
            "finished_utc": utc_now(),
            "python": platform.python_version(),
            "pysat": pysat.__version__,
            "solver": f"{args.solver} via PySAT",
            "seed": args.seed,
            "random_phases": args.random_phases,
            "phase_witness": str(args.phase_witness) if args.phase_witness is not None else None,
            "positive_phase_orbits": len(positive_phases),
            "time_limit_seconds": args.seconds,
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "status": status,
            "solver_stats": stats,
            "dimacs": str(args.write_cnf) if args.write_cnf is not None else None,
        }

        if answer is True:
            model = set(solver.get_model())
            selected = {
                orbit_id
                for orbit_id in range(len(geometry.orbits))
                if orbit_id + 1 in model
            }
            points = selected_points(geometry, selected)
            if len(points) != 2 * args.n:
                raise AssertionError(f"SAT model decoded to {len(points)} points")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            payload = "".join(f"{x} {y}\n" for x, y in points)
            args.output.write_text(payload, encoding="utf-8")
            result["witness"] = str(args.output)
            result["witness_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
            result["selected_orbits"] = len(selected)

    args.run_json.parent.mkdir(parents=True, exist_ok=True)
    args.run_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "build_seconds": result["build_seconds"],
        "solve_seconds": result["solve_seconds"],
        **result["solver_stats"],
    }, sort_keys=True))
    if "witness" in result:
        print(f"witness: {result['witness']} sha256={result['witness_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
