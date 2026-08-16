#!/usr/bin/env python3
"""CP-SAT search for a canonical rct4 no-three-in-line configuration.

The mathematical model follows Prellberg's odd-order symmetry reduction and
adds redundant exact column and orbit-count equations for propagation.  Every
geometric line is generated exactly from a primitive step, rewritten in orbit
variables, stripped of the fixed-empty anti-diagonal, and deduplicated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import ortools
from ortools.sat.python import cp_model

from rct4_model import (
    Rct4Geometry,
    build_rct4_geometry,
    column_signature,
    reduced_line_signatures,
    row_signature,
    selected_points,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def weighted_sum(variables: list[cp_model.IntVar], signature: tuple[tuple[int, int], ...]):
    return sum(coefficient * variables[orbit_id] for orbit_id, coefficient in signature)


def build_model(n: int) -> tuple[cp_model.CpModel, list[cp_model.IntVar], Rct4Geometry, dict]:
    geometry = build_rct4_geometry(n)
    signatures, line_stats = reduced_line_signatures(geometry)

    model = cp_model.CpModel()
    variables = [
        model.new_bool_var(f"o_{orbit_id}_{i}_{j}")
        for orbit_id, (i, j) in enumerate(geometry.representatives)
    ]

    for signature in signatures:
        model.add(weighted_sum(variables, signature) <= 2)

    # A 2n-point configuration has exactly two points in every row and column.
    # Column equalities are logically redundant with the vertical at-most-two
    # constraints and total cardinality, but materially improve propagation.
    for row in range(n):
        model.add(weighted_sum(variables, row_signature(geometry, row)) == 2)
    for column in range(n):
        model.add(weighted_sum(variables, column_signature(geometry, column)) == 2)

    # These equations are consequences of the canonical rct4 orbit sizes and
    # total cardinality; stating them explicitly avoids asking presolve to
    # rediscover the parity argument.
    model.add(sum(variables[i] for i in geometry.diagonal_orbits) == 1)
    model.add(sum(variables[i] for i in geometry.off_diagonal_orbits) == (n - 1) // 2)

    metadata = {
        "n": n,
        "target_points": 2 * n,
        "symmetry": "canonical-rct4",
        "fixed_empty": "anti-diagonal",
        "orbit_variables": len(variables),
        "diagonal_orbits": len(geometry.diagonal_orbits),
        "off_diagonal_orbits": len(geometry.off_diagonal_orbits),
        "line_statistics": line_stats.__dict__,
        "row_equalities": n,
        "column_equalities": n,
        "orbit_count_equalities": 2,
    }
    return model, variables, geometry, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=71)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("n71-142.txt"))
    parser.add_argument("--run-json", type=Path, default=Path("cpsat-run.json"))
    parser.add_argument("--export-model", type=Path)
    parser.add_argument("--log-progress", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = utc_now()
    process_start = time.monotonic()
    model, variables, geometry, metadata = build_model(args.n)
    build_seconds = time.monotonic() - process_start

    if args.export_model is not None:
        args.export_model.parent.mkdir(parents=True, exist_ok=True)
        model.export_to_file(str(args.export_model))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.randomize_search = True
    solver.parameters.log_search_progress = args.log_progress
    solver.parameters.cp_model_presolve = True

    print(json.dumps({"event": "model-built", "build_seconds": build_seconds, **metadata}, sort_keys=True))
    sys.stdout.flush()
    solve_start = time.monotonic()
    status_code = solver.solve(model)
    solve_seconds = time.monotonic() - solve_start
    status = solver.status_name(status_code)

    result: dict = {
        **metadata,
        "started_utc": started,
        "finished_utc": utc_now(),
        "python": platform.python_version(),
        "ortools": ortools.__version__,
        "pid": os.getpid(),
        "seed": args.seed,
        "workers": args.workers,
        "time_limit_seconds": args.seconds,
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "status": status,
        "conflicts": solver.num_conflicts,
        "branches": solver.num_branches,
        "wall_time_reported": solver.wall_time,
        "response_stats": solver.response_stats(),
    }

    if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        selected = {i for i, variable in enumerate(variables) if solver.value(variable)}
        points = selected_points(geometry, selected)
        if len(points) != 2 * args.n:
            raise AssertionError(f"solver model decoded to {len(points)} points")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = "".join(f"{x} {y}\n" for x, y in points)
        args.output.write_text(payload, encoding="utf-8")
        result["witness"] = str(args.output)
        result["witness_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
        result["selected_orbits"] = len(selected)

    args.run_json.parent.mkdir(parents=True, exist_ok=True)
    args.run_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "build_seconds", "solve_seconds", "conflicts", "branches"
    )}, sort_keys=True))
    if "witness" in result:
        print(f"witness: {result['witness']} sha256={result['witness_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
