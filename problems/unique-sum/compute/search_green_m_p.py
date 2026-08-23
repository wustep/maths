#!/usr/bin/env python3
"""Exact cardinality-SAT search for Green's no-unique-sum function m(p).

This file deliberately does not import or reuse ``search_m_p.py``.  That q1
program encoded only the weaker midpoint condition.

For every residue ``a`` there is one Boolean x[a].  For every off-diagonal
unordered pair ``{a,b}`` there is a Boolean y[a,b] constrained by

    y[a,b] <-> (x[a] and x[b]).

The diagonal pair ``{a,a}`` is represented directly by x[a].  For each sum s,
the p unordered pairs with a+b=s collapse to (p+1)/2 candidates (one diagonal
and (p-1)/2 off-diagonal pairs).  If their literals are q_1,...,q_t, the
clauses

    not q_i or q_1 or ... or q_(i-1) or q_(i+1) or ... or q_t

say that no selected representation is the only selected representation.
Thus the number of unordered representations is never one, equivalently the
ordered representation count is never 1 or 2.

Every admissible non-singleton set in an odd prime cyclic group contains a
nontrivial three-term progression: the diagonal representation {a,a} needs a
second pair {b,c}.  Translation by -a and scaling by (b-a)^(-1) therefore
justify the affine normalization x[0] = x[1] = x[p-1] = true.

Cardinalities are tested in increasing order.  Every UNSAT result is an
exhaustive lower-bound check; the first SAT result supplies the witness.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from time import monotonic
from typing import Any

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "green_m_p.csv"
DEFAULT_CERTIFICATES = HERE / "green_m_p_certificates.json"

OEIS_PREFIX: dict[int, int] = {
    3: 3,
    5: 4,
    7: 5,
    11: 7,
    13: 7,
    17: 8,
    19: 9,
    23: 10,
    29: 11,
    31: 11,
    37: 12,
    41: 13,
    43: 13,
    47: 13,
    53: 14,
}

OEIS_BOUND = max(OEIS_PREFIX)


def primes_up_to(bound: int) -> list[int]:
    return [
        candidate
        for candidate in range(3, bound + 1, 2)
        if all(candidate % divisor for divisor in range(2, math.isqrt(candidate) + 1))
    ]


def ordered_representation_counts(p: int, values: list[int]) -> list[int]:
    counts = [0] * p
    for left in values:
        for right in values:
            counts[(left + right) % p] += 1
    return counts


def unordered_representation_counts(p: int, values: list[int]) -> list[int]:
    counts = [0] * p
    for left_index, left in enumerate(values):
        for right in values[left_index:]:
            counts[(left + right) % p] += 1
    return counts


def assert_admissible(p: int, values: list[int]) -> None:
    if len(values) < 2 or values != sorted(set(values)):
        raise AssertionError(f"malformed set modulo {p}: {values}")
    if any(value < 0 or value >= p for value in values):
        raise AssertionError(f"residue outside Z/{p}Z: {values}")
    ordered = ordered_representation_counts(p, values)
    forbidden = [residue for residue, count in enumerate(ordered) if count in (1, 2)]
    if forbidden:
        raise AssertionError(
            f"p={p}, A={values} has ordered multiplicity 1 or 2 at sums {forbidden}"
        )


def cyclic_arithmetic_progression(p: int, values: list[int]) -> bool:
    target = set(values)
    return any(
        {(start + index * step) % p for index in range(len(values))} == target
        for start in values
        for step in range(1, p)
    )


def affine_stabilizer_size(p: int, values: list[int]) -> int:
    target = set(values)
    if len(values) == 1:
        return p - 1
    first, second = values[:2]
    inverse = pow(second - first, -1, p)
    stabilizer: set[tuple[int, int]] = set()
    for image_first in values:
        for image_second in values:
            if image_first == image_second:
                continue
            multiplier = (image_second - image_first) * inverse % p
            translation = (image_first - multiplier * first) % p
            if {(multiplier * value + translation) % p for value in values} == target:
                stabilizer.add((multiplier, translation))
    return len(stabilizer)


def shape_label(p: int, values: list[int]) -> str:
    if len(values) == p:
        return "whole group"
    if cyclic_arithmetic_progression(p, values):
        return "cyclic arithmetic progression"
    if affine_stabilizer_size(p, values) > 1:
        return "non-AP, affine-symmetric"
    return "non-AP, trivial affine stabilizer"


def build_exact_cnf(p: int, cardinality: int) -> tuple[CNF, list[int], IDPool]:
    """Build the normalized exact-cardinality CNF for odd p."""

    if p < 3 or p % 2 == 0 or not 3 <= cardinality <= p:
        raise ValueError("requires odd p >= 3 and 3 <= cardinality <= p")

    pool = IDPool()
    selected = [pool.id(("selected", residue)) for residue in range(p)]
    cnf = CNF()
    representations: list[list[int]] = [[] for _ in range(p)]

    for left in range(p):
        # The diagonal pair is active exactly when its single endpoint is.
        representations[2 * left % p].append(selected[left])
        for right in range(left + 1, p):
            pair = pool.id(("pair", left, right))
            representations[(left + right) % p].append(pair)
            # pair <-> selected[left] AND selected[right]
            cnf.append([-pair, selected[left]])
            cnf.append([-pair, selected[right]])
            cnf.append([pair, -selected[left], -selected[right]])

    expected_representations = (p + 1) // 2
    for residue, candidates in enumerate(representations):
        if len(candidates) != expected_representations:
            raise AssertionError(
                f"sum {residue} has {len(candidates)} pair variables, "
                f"expected {expected_representations}"
            )
        for index, candidate in enumerate(candidates):
            cnf.append([-candidate, *candidates[:index], *candidates[index + 1 :]])

    cnf.extend(
        CardEnc.equals(
            lits=selected,
            bound=cardinality,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    cnf.append([selected[0]])
    cnf.append([selected[1]])
    cnf.append([selected[p - 1]])
    return cnf, selected, pool


def solve_cardinality(
    p: int,
    cardinality: int,
    solver_name: str,
) -> tuple[bool, list[int] | None, dict[str, Any]]:
    built_at = monotonic()
    cnf, selected, pool = build_exact_cnf(p, cardinality)
    build_seconds = monotonic() - built_at
    solved_at = monotonic()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        satisfiable = solver.solve()
        solve_seconds = monotonic() - solved_at
        statistics = solver.accum_stats()
        model = solver.get_model() if satisfiable else None

    witness = None
    if model is not None:
        positive = {literal for literal in model if literal > 0}
        witness = [residue for residue, literal in enumerate(selected) if literal in positive]
        if len(witness) != cardinality:
            raise AssertionError(
                f"SAT model has {len(witness)} selected residues, expected {cardinality}"
            )
        assert_admissible(p, witness)

    result: dict[str, Any] = {
        "cardinality": cardinality,
        "status": "SAT" if satisfiable else "UNSAT",
        "solver": solver_name,
        "variables": pool.top,
        "clauses": len(cnf.clauses),
        "build_seconds": round(build_seconds, 6),
        "solve_seconds": round(solve_seconds, 6),
        "statistics": statistics,
    }
    return satisfiable, witness, result


def compute_prime(
    p: int,
    solver_name: str,
    start_cardinality: int = 3,
    stop_cardinality: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    stop = p if stop_cardinality is None else min(stop_cardinality, p)
    checks: list[dict[str, Any]] = []
    witness: list[int] | None = None
    for cardinality in range(start_cardinality, stop + 1):
        satisfiable, candidate, result = solve_cardinality(p, cardinality, solver_name)
        checks.append(result)
        print(
            f"p={p:3d} k={cardinality:2d} {result['status']:5s} "
            f"build={result['build_seconds']:.3f}s solve={result['solve_seconds']:.3f}s",
            flush=True,
        )
        if satisfiable:
            witness = candidate
            break
    if witness is None:
        raise RuntimeError(f"no witness found for p={p} through cardinality {stop}")

    ordered = ordered_representation_counts(p, witness)
    unordered = unordered_representation_counts(p, witness)
    row: dict[str, Any] = {
        "p": p,
        "m": len(witness),
        "witness": json.dumps(witness, separators=(",", ":")),
        "sumset_size": sum(count > 0 for count in unordered),
        "max_ordered_multiplicity": max(ordered),
        "affine_stabilizer": affine_stabilizer_size(p, witness),
        "shape": shape_label(p, witness),
    }
    certificate: dict[str, Any] = {
        "p": p,
        "m": len(witness),
        "witness": witness,
        "ordered_representation_counts": ordered,
        "unordered_representation_counts": unordered,
        "cardinality_checks": checks,
    }
    return row, certificate


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "p",
                "m",
                "witness",
                "sumset_size",
                "max_ordered_multiplicity",
                "affine_stabilizer",
                "shape",
            ),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound", type=int, default=OEIS_BOUND)
    parser.add_argument("--prime", type=int, help="solve just one odd prime")
    parser.add_argument("--start-cardinality", type=int, default=3)
    parser.add_argument("--stop-cardinality", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--certificates", type=Path, default=DEFAULT_CERTIFICATES)
    parser.add_argument(
        "--skip-oeis-gate",
        action="store_true",
        help=(
            f"allow a bound above {OEIS_BOUND} without first running the published prefix"
        ),
    )
    args = parser.parse_args()

    if args.prime is not None:
        primes = [args.prime]
    else:
        primes = primes_up_to(args.bound)
    if not primes or any(p < 3 or p % 2 == 0 for p in primes):
        parser.error("all requested moduli must be odd primes at least 3")
    if args.bound > OEIS_BOUND and args.prime is None and not args.skip_oeis_gate:
        parser.error(
            f"run and save the complete p <= {OEIS_BOUND} OEIS gate before extending"
        )

    started = monotonic()
    rows: list[dict[str, Any]] = []
    certificates: list[dict[str, Any]] = []
    for p in primes:
        row, certificate = compute_prime(
            p,
            solver_name=args.solver,
            start_cardinality=args.start_cardinality,
            stop_cardinality=args.stop_cardinality,
        )
        rows.append(row)
        certificates.append(certificate)

    if args.prime is None and args.bound >= OEIS_BOUND:
        observed = {
            int(row["p"]): int(row["m"])
            for row in rows
            if int(row["p"]) <= OEIS_BOUND
        }
        if observed != OEIS_PREFIX:
            raise AssertionError(f"A398173 gate failed: expected {OEIS_PREFIX}, got {observed}")
        print(
            f"A398173_GATE_MATCHED: {len(OEIS_PREFIX)}/{len(OEIS_PREFIX)} "
            f"terms through p={OEIS_BOUND}",
            flush=True,
        )

    write_csv(args.csv, rows)
    payload = {
        "schema_version": 1,
        "claim": "exact Green m(p), not the q1 midpoint function",
        "predicate": "all ordered representation counts avoid 1 and 2",
        "normalization": "0, 1, and p-1 selected (affine WLOG)",
        "solver": args.solver,
        "elapsed_seconds": round(monotonic() - started, 6),
        "oeis_a398173_gate": (
            f"matched {len(OEIS_PREFIX)}/{len(OEIS_PREFIX)} through p={OEIS_BOUND}"
            if args.prime is None and args.bound >= OEIS_BOUND
            else "not run in this partial invocation"
        ),
        "records": certificates,
    }
    args.certificates.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.csv}")
    print(f"wrote {args.certificates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
