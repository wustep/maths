#!/usr/bin/env python3
"""Streaming structural audit for a DIMACS CNF file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cnf", type=Path, nargs="?", default=Path("n71-rct4.cnf"))
    parser.add_argument("--json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    digest = hashlib.sha256()
    clauses = 0
    literals = 0
    max_variable = 0
    declared_variables = None
    declared_clauses = None

    with args.cnf.open("rb") as raw:
        for chunk in iter(lambda: raw.read(1024 * 1024), b""):
            digest.update(chunk)

    with args.cnf.open("r", encoding="ascii") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            line = raw_line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                fields = line.split()
                if fields[:2] != ["p", "cnf"] or len(fields) != 4:
                    raise ValueError(f"line {line_number}: malformed DIMACS header")
                if declared_variables is not None:
                    raise ValueError("multiple DIMACS headers")
                declared_variables = int(fields[2])
                declared_clauses = int(fields[3])
                continue
            if declared_variables is None:
                raise ValueError("clause appears before DIMACS header")
            fields = [int(field) for field in line.split()]
            if not fields or fields[-1] != 0 or 0 in fields[:-1]:
                raise ValueError(f"line {line_number}: malformed clause terminator")
            clause = fields[:-1]
            if not clause:
                raise ValueError(f"line {line_number}: unexpected empty clause")
            clauses += 1
            literals += len(clause)
            max_variable = max(max_variable, *(abs(literal) for literal in clause))

    if declared_variables is None or declared_clauses is None:
        raise ValueError("missing DIMACS header")
    if clauses != declared_clauses:
        raise ValueError(f"read {clauses} clauses, header declares {declared_clauses}")
    if max_variable > declared_variables:
        raise ValueError(
            f"maximum variable {max_variable} exceeds declared {declared_variables}"
        )

    result = {
        "path": str(args.cnf),
        "bytes": args.cnf.stat().st_size,
        "sha256": digest.hexdigest(),
        "declared_variables": declared_variables,
        "declared_clauses": declared_clauses,
        "actual_clauses": clauses,
        "actual_literals": literals,
        "maximum_variable_seen": max_variable,
        "status": "VALID_DIMACS",
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
