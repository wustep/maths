#!/usr/bin/env python3
"""SAT searches for a 49-column radius-two covering of F_2^10.

The selected nonzero columns are S.  The implicit zero point turns
A = {0} union S into a 50-point difference basis, so a syndrome s is
covered by x_s or by a selected pair x_v, x_(v xor s).

This is discovery code.  Every SAT model is rechecked here, but any model
must also pass verify_n49.c before it is treated as a certificate.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


SPACE = 1 << 10
TARGET = 49


def read_columns(path: Path) -> list[int]:
    columns: list[int] = []
    for line in path.read_text().splitlines():
        if line.lstrip().startswith("#"):
            continue
        columns.extend(int(token, 0) for token in line.split())
    if any(column <= 0 or column >= SPACE for column in columns):
        raise ValueError(f"{path}: columns must lie in 1..1023")
    if len(columns) != len(set(columns)):
        raise ValueError(f"{path}: repeated columns")
    return columns


def gf32_multiply(left: int, right: int) -> int:
    """Multiply in GF(32), represented modulo x^5+x^2+1."""
    product = 0
    while right:
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
        if left & 0x20:
            left ^= 0x25
    return product & 0x1F


def apn_graph() -> list[int]:
    """The 32-point Sidon graph {(u,u^3): u in GF(32)}."""
    graph = []
    for value in range(32):
        square = gf32_multiply(value, value)
        cube = gf32_multiply(square, value)
        graph.append(value | (cube << 5))
    assert len(set(graph)) == 32 and 0 in graph
    pair_sums = {
        left ^ right
        for index, left in enumerate(graph)
        for right in graph[:index]
    }
    assert len(pair_sums) == 32 * 31 // 2
    return graph


def rank2(columns: list[int]) -> int:
    basis = [0] * 10
    rank = 0
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def verify(columns: list[int]) -> list[int]:
    covered = bytearray(SPACE)
    covered[0] = 1
    for index, left in enumerate(columns):
        covered[left] = 1
        for right in columns[:index]:
            covered[left ^ right] = 1
    return [syndrome for syndrome in range(SPACE) if not covered[syndrome]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", action="store_true",
                        help="force the ten unit columns (sound WLOG globally)")
    parser.add_argument("--apn", action="store_true",
                        help="force the 31 nonzero points of an APN graph")
    parser.add_argument("--force", type=Path,
                        help="force every column listed in this file")
    parser.add_argument("--seed", type=Path,
                        help="use a column set as the initial SAT phase")
    parser.add_argument("--distance", type=int,
                        help="retain all but at most K columns of --seed")
    parser.add_argument("--cross-only", action="store_true",
                        help="with fixed columns, require their cross-pairs alone "
                             "to finish coverage (a stricter geometric search)")
    parser.add_argument("--random-seed", type=int, default=1)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.distance is not None and args.seed is None:
        raise SystemExit("--distance requires --seed")
    if args.distance is not None and not 0 <= args.distance <= TARGET:
        raise SystemExit("--distance must lie in 0..49")

    forced: set[int] = set()
    if args.frame:
        forced.update(1 << bit for bit in range(10))
    if args.apn:
        forced.update(apn_graph())
        forced.discard(0)
    if args.force:
        forced.update(read_columns(args.force))
    if len(forced) > TARGET:
        raise SystemExit(f"too many forced columns: {len(forced)}")
    if args.cross_only and not forced:
        raise SystemExit("--cross-only requires --apn or --force")

    seed = read_columns(args.seed) if args.seed else []
    if seed and len(seed) != TARGET:
        raise SystemExit(f"--seed must contain exactly {TARGET} columns")

    pool = IDPool()
    selected = {value: pool.id(("x", value)) for value in range(1, SPACE)}
    clauses: list[list[int]] = []
    coverage: list[list[int] | None] = [
        None if syndrome == 0 else [selected[syndrome]]
        for syndrome in range(SPACE)
    ]

    for value in sorted(forced):
        clauses.append([selected[value]])

    # A fixed singleton or a fixed-fixed pair already covers its syndrome.
    for value in forced:
        coverage[value] = None
    forced_list = sorted(forced)
    for index, left in enumerate(forced_list):
        for right in forced_list[:index]:
            coverage[left ^ right] = None

    for left in range(1, SPACE):
        for right in range(left + 1, SPACE):
            syndrome = left ^ right
            if coverage[syndrome] is None:
                continue
            left_fixed = left in forced
            right_fixed = right in forced
            if left_fixed or right_fixed:
                coverage[syndrome].append(
                    selected[right if left_fixed else left]
                )
            elif not args.cross_only:
                pair = pool.id(("y", left, right))
                coverage[syndrome].append(pair)
                clauses.append([-pair, selected[left]])
                clauses.append([-pair, selected[right]])

    for syndrome in range(1, SPACE):
        if coverage[syndrome] is not None:
            clauses.append(coverage[syndrome])

    cardinality = CardEnc.atmost(
        lits=[selected[value] for value in range(1, SPACE)],
        bound=TARGET,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    clauses.extend(cardinality.clauses)

    if args.distance is not None:
        retain = CardEnc.atleast(
            lits=[selected[value] for value in seed],
            bound=TARGET - args.distance,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        clauses.extend(retain.clauses)

    print(
        f"clauses={len(clauses)} vars={pool.top} forced={len(forced)} "
        f"cross_only={args.cross_only} distance={args.distance}",
        flush=True,
    )
    with Cadical195(bootstrap_with=clauses) as solver:
        solver.configure({"seed": args.random_seed})
        if seed:
            seed_set = set(seed)
            solver.set_phases([
                selected[value] if value in seed_set else -selected[value]
                for value in range(1, SPACE)
            ])
        satisfiable = solver.solve()
        if not satisfiable:
            print("UNSAT in this restricted search")
            return 1
        model = {literal for literal in solver.get_model() if literal > 0}

    columns = [
        value for value in range(1, SPACE) if selected[value] in model
    ]
    # At-most 49 is enough for existence; pad a shorter covering harmlessly.
    for value in range(1, SPACE):
        if len(columns) == TARGET:
            break
        if value not in columns:
            columns.append(value)
    columns.sort()
    holes = verify(columns)
    distinct = len(columns) == len(set(columns))
    rank = rank2(columns)
    print(
        f"SAT columns={len(columns)} distinct={distinct} rank={rank} "
        f"covered={SPACE - len(holes)}/{SPACE} holes={holes}",
        flush=True,
    )
    if len(columns) != TARGET or not distinct or rank != 10 or holes:
        print("INTERNAL VERIFICATION FAILURE", file=sys.stderr)
        return 2
    print("CANDIDATE ONLY: run the independent C verifier", flush=True)
    if args.output:
        args.output.write_text(
            "# SAT candidate; independently verify before claiming\n"
            + " ".join(map(str, columns))
            + "\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
