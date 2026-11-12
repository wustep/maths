#!/usr/bin/env python3
"""Exact search inside the 12-fiber family exposed by a seven-hole set.

For a seed whose seven holes span a 5-space W, adjoining zero partitions the
50 points into twelve W-cosets of sizes 6,4,...,4.  This program preserves
those cosets and sizes but chooses every point anew.  Translation, GL(W), and
linear shears from F_2^10/W to W normalize zero, the rank of its four-point
fiber, and one point in each of five quotient-basis fibers.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195, Kissat404


V = 1 << 10


def read_columns(path: Path) -> list[int]:
    columns: list[int] = []
    for line in path.read_text().splitlines():
        if not line.lstrip().startswith("#"):
            columns.extend(int(token, 0) for token in line.split())
    if len(columns) != 49 or len(set(columns)) != 49:
        raise ValueError(f"{path} is not a 49-column set")
    return columns


def rank(values: list[int] | set[int]) -> int:
    basis = [0] * 10
    result = 0
    for original in values:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                result += 1
                break
    return result


def flat_coverage(points: list[int] | set[int]) -> set[int]:
    ordered = sorted(points)
    covered = {0}
    for index, left in enumerate(ordered):
        for right in ordered[:index]:
            covered.add(left ^ right)
    return covered


def linear_basis(values: set[int]) -> list[int]:
    basis: list[int] = []
    for value in sorted(values - {0}):
        if rank(basis + [value]) > len(basis):
            basis.append(value)
    return basis


def basis_map(domain: list[int], images: list[int]) -> list[int]:
    if len(domain) != 10 or rank(domain) != 10 or rank(images) != 10:
        raise ValueError("basis_map needs two bases")
    result = [0] * V
    for mask in range(V):
        source = 0
        target = 0
        for index in range(10):
            if mask & (1 << index):
                source ^= domain[index]
                target ^= images[index]
        result[source] = target
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-columns", type=Path, required=True)
    parser.add_argument("--zero-fiber-rank", type=int, choices=(2, 3),
                        required=True)
    parser.add_argument("--solver", choices=("cadical", "kissat"),
                        default="cadical")
    parser.add_argument("--random-seed", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    seed = read_columns(args.seed_columns)
    seed_points = {0, *seed}
    holes = sorted(set(range(V)) - flat_coverage(seed_points))
    hole_space = {0}
    for hole in holes:
        hole_space |= {value ^ hole for value in list(hole_space)}
    if len(holes) != 7 or len(hole_space) != 32:
        raise ValueError("the seed must have seven holes spanning a 5-space")
    w_basis = linear_basis(hole_space)
    assert len(w_basis) == 5

    def representative(value: int) -> int:
        return min(value ^ shift for shift in hole_space)

    seed_fibers: dict[int, set[int]] = defaultdict(set)
    for value in seed_points:
        seed_fibers[representative(value)].add(value)
    target_sizes = {key: len(values) for key, values in seed_fibers.items()}
    if Counter(target_sizes.values()) != Counter({4: 11, 6: 1}):
        raise ValueError("unexpected fiber-size pattern")
    allowed = sorted({key ^ shift for key in target_sizes for shift in hole_space})

    # Five supported quotient cosets form a basis modulo W.  A shear fixing W
    # can move one chosen point in each of these fibers to its representative.
    quotient_basis: list[int] = []
    for key in sorted(target_sizes):
        if rank(w_basis + quotient_basis + [key]) > 5 + len(quotient_basis):
            quotient_basis.append(key)
    assert len(quotient_basis) == 5

    if args.zero_fiber_rank == 2:
        zero_anchor = {0, w_basis[0], w_basis[1], w_basis[0] ^ w_basis[1]}
    else:
        zero_anchor = {0, w_basis[0], w_basis[1], w_basis[2]}
    anchors = zero_anchor | set(quotient_basis)

    # Put the known seven-hole seed into the same canonical coordinates for
    # SAT phasing whenever its zero fiber belongs to this rank branch.
    phase_points: set[int] | None = None
    seed_zero = seed_fibers[0]
    seed_zero_rank = rank(seed_zero)
    if seed_zero_rank == args.zero_fiber_rank:
        domain_w: list[int] = []
        for value in sorted(seed_zero - {0}):
            if rank(domain_w + [value]) > len(domain_w):
                domain_w.append(value)
        for value in sorted(hole_space - {0}):
            if rank(domain_w + [value]) > len(domain_w):
                domain_w.append(value)
        first_map = basis_map(
            domain_w + quotient_basis,
            w_basis + quotient_basis,
        )
        transformed = {first_map[value] for value in seed_points}
        transformed_fibers: dict[int, set[int]] = defaultdict(set)
        for value in transformed:
            transformed_fibers[representative(value)].add(value)
        shifts = [min(transformed_fibers[key]) ^ key for key in quotient_basis]
        shear = basis_map(
            w_basis + quotient_basis,
            w_basis + [key ^ shift for key, shift in zip(quotient_basis, shifts)],
        )
        phase_points = {shear[value] for value in transformed}
        assert anchors <= phase_points
        assert len(phase_points) == 50
        assert len(flat_coverage(phase_points)) == 1017

    pool = IDPool()
    selected = {value: pool.id(("x", value)) for value in allowed}
    clauses: list[list[int]] = [[selected[value]] for value in anchors]
    for key, size in sorted(target_sizes.items()):
        clauses.extend(CardEnc.equals(
            [selected[key ^ shift] for shift in hole_space], size,
            vpool=pool, encoding=EncType.seqcounter,
        ).clauses)

    coverage: list[list[int]] = [[] for _ in range(V)]
    for index, left in enumerate(allowed):
        for right in allowed[index + 1:]:
            pair = pool.id(("pair", left, right))
            coverage[left ^ right].append(pair)
            clauses.extend([
                [-pair, selected[left]],
                [-pair, selected[right]],
                [-selected[left], -selected[right], pair],
            ])

    # The number of selected pairs in each quotient class is fixed by the
    # fiber cardinalities.  In the twenty classes with budget 32, coverage of
    # all 32 syndromes therefore implies exactly one representation each.
    pair_budget: Counter[int] = Counter()
    keys = sorted(target_sizes)
    for index, left in enumerate(keys):
        size = target_sizes[left]
        pair_budget[0] += size * (size - 1) // 2
        for right in keys[index + 1:]:
            pair_budget[representative(left ^ right)] += (
                size * target_sizes[right]
            )
    for syndrome in range(1, V):
        if not coverage[syndrome]:
            raise RuntimeError(f"empty coverage clause for {syndrome}")
        clauses.append(coverage[syndrome])
        if pair_budget[representative(syndrome)] == 32:
            clauses.extend(CardEnc.atmost(
                coverage[syndrome], 1, vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses)

    print(
        f"branch=rank{args.zero_fiber_rank} holes={holes} W={len(hole_space)} "
        f"allowed={len(allowed)} anchors={sorted(anchors)} "
        f"pair_budgets={dict(sorted(Counter(pair_budget.values()).items()))} "
        f"vars={pool.top} clauses={len(clauses)}",
        flush=True,
    )
    solver_class = Cadical195 if args.solver == "cadical" else Kissat404
    with solver_class(bootstrap_with=clauses) as solver:
        if args.solver == "cadical":
            solver.configure({"seed": args.random_seed})
        if phase_points is not None:
            solver.set_phases([
                selected[value] if value in phase_points else -selected[value]
                for value in allowed
            ])
        satisfiable = solver.solve()
        print("SAT" if satisfiable else "UNSAT", solver.accum_stats(), flush=True)
        if not satisfiable:
            return 1
        model = {literal for literal in solver.get_model() if literal > 0}

    points = sorted(value for value in allowed if selected[value] in model)
    columns = [value for value in points if value]
    if (len(points) != 50 or points[0] != 0 or len(columns) != 49 or
            rank(columns) != 10 or len(flat_coverage(points)) != V):
        raise RuntimeError("SAT model failed the flat independent recount")
    print("columns " + " ".join(map(str, columns)), flush=True)
    if args.output:
        args.output.write_text(" ".join(map(str, columns)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
