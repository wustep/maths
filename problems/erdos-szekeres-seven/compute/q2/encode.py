#!/usr/bin/env python3
"""Stream a signotope relaxation of the Erdős--Szekeres SAT instance."""

from __future__ import annotations

import argparse
import itertools
import math
from collections.abc import Iterable
from pathlib import Path


Clause = list[int]


def forbidding_clause(variables: list[int], assignment: tuple[int, ...]) -> Clause:
    """Return the clause falsified by exactly this 0/1 assignment."""
    return [-var if bit else var for var, bit in zip(variables, assignment)]


def signotope_clauses(variables: list[int]) -> Iterable[Clause]:
    """Forbid sign sequences having more than one change."""
    assert len(variables) == 4
    for bits in itertools.product((0, 1), repeat=4):
        changes = sum(bits[i] != bits[i + 1] for i in range(3))
        if changes > 1:
            yield forbidding_clause(variables, bits)


def parity_clauses(variables: list[int], parity_variable: int) -> Iterable[Clause]:
    """Encode parity_variable iff XOR(variables), by its 16 forbidden rows."""
    assert len(variables) == 4
    for bits in itertools.product((0, 1), repeat=4):
        parity = sum(bits) & 1
        wrong = 1 - parity
        yield forbidding_clause(variables + [parity_variable], bits + (wrong,))


def counts(n: int, k: int) -> tuple[int, int]:
    four_sets = math.comb(n, 4)
    variables = math.comb(n, 3) + four_sets
    clauses = 24 * four_sets + math.comb(n, k)
    return variables, clauses


def write_instance(n: int, k: int, path: Path) -> None:
    triples = list(itertools.combinations(range(n), 3))
    triple_variable = {triple: i + 1 for i, triple in enumerate(triples)}
    four_sets = list(itertools.combinations(range(n), 4))
    first_parity = len(triples) + 1
    parity_variable = {
        four: first_parity + i for i, four in enumerate(four_sets)
    }
    variable_count, clause_count = counts(n, k)

    written = 0
    with path.open("w", encoding="ascii", buffering=1 << 20) as output:
        output.write("c rank-3 signotope relaxation for Erdos-Szekeres\n")
        output.write(f"c n={n} k={k}\n")
        output.write(f"p cnf {variable_count} {clause_count}\n")

        for a, b, c, d in four_sets:
            sequence = [
                triple_variable[(a, b, c)],
                triple_variable[(a, b, d)],
                triple_variable[(a, c, d)],
                triple_variable[(b, c, d)],
            ]
            for clause in signotope_clauses(sequence):
                output.write(" ".join(map(str, clause)) + " 0\n")
                written += 1
            for clause in parity_clauses(sequence, parity_variable[(a, b, c, d)]):
                output.write(" ".join(map(str, clause)) + " 0\n")
                written += 1

        for subset in itertools.combinations(range(n), k):
            clause = [
                parity_variable[four]
                for four in itertools.combinations(subset, 4)
            ]
            output.write(" ".join(map(str, clause)) + " 0\n")
            written += 1

    if written != clause_count:
        raise RuntimeError(f"wrote {written} clauses, expected {clause_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=33)
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--count-only", action="store_true")
    args = parser.parse_args()

    if not 4 <= args.k <= args.n:
        parser.error("require 4 <= k <= n")
    variable_count, clause_count = counts(args.n, args.k)
    print(f"signotope n={args.n} k={args.k}: {variable_count} variables, {clause_count} clauses")
    if args.count_only:
        return
    if args.out is None:
        parser.error("--out is required unless --count-only is used")
    write_instance(args.n, args.k, args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
