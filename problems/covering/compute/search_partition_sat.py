#!/usr/bin/env python3
"""Search for a valid coarsening of a certified radius-2 partition.

This is discovery code, not the certificate.  It represents each original
partition block by log2(TARGET) color bits.  For every nontrivial syndrome,
at least one of its original block-pair representations must retain different
colors.  The emitted labels must be checked independently with
verify_radius2_matrix.c.

Requires the optional ``python-sat`` package.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from pysat.solvers import Solver
except ImportError as error:
    raise SystemExit(
        "python-sat is required for this optional search; "
        "install the latest release with `python3 -m pip install python-sat`"
    ) from error


def read_matrix(path: Path) -> tuple[int, int, list[int]]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                rows.append(line.split())
    assert rows, "%s: no matrix rows" % path
    length = len(rows[0])
    assert all(len(row) == length for row in rows), "%s: ragged matrix" % path
    assert all(bit in ("0", "1") for row in rows for bit in row)
    columns = [0] * length
    for row_index, row in enumerate(rows):
        for column_index, bit in enumerate(row):
            if bit == "1":
                columns[column_index] |= 1 << row_index
    return len(rows), length, columns


def read_partition(path: Path, length: int) -> list[int]:
    labels: list[int] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0]
            labels.extend(int(token) for token in line.split())
    assert len(labels) == length
    assert sorted(set(labels)) == list(range(max(labels) + 1))
    return labels


def binary_rank(columns: list[int]) -> int:
    basis: dict[int, int] = {}
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def collect_constraints(
    columns: list[int], labels: list[int], redundancy: int, blocks: int
) -> tuple[
    set[tuple[int, ...]],
    list[tuple[int, int]],
    int,
]:
    """Return distinct syndrome constraints over original block-pair edges."""
    edge_id = [[-1] * blocks for _ in range(blocks)]
    edges: list[tuple[int, int]] = []
    for left in range(blocks):
        for right in range(left):
            identifier = len(edges)
            edge_id[left][right] = identifier
            edge_id[right][left] = identifier
            edges.append((right, left))

    space = 1 << redundancy
    protected = bytearray(space)
    protected[0] = 1
    for column in columns:
        protected[column] = 1
    representations: list[list[int] | None] = [None] * space
    cross_pairs = 0
    for left, left_column in enumerate(columns):
        left_block = labels[left]
        for right in range(left):
            right_block = labels[right]
            if left_block == right_block:
                continue
            identifier = edge_id[left_block][right_block]
            syndrome = left_column ^ columns[right]
            current = representations[syndrome]
            if current is None:
                representations[syndrome] = [identifier]
            elif identifier not in current:
                current.append(identifier)
            cross_pairs += 1

    constraints: set[tuple[int, ...]] = set()
    for syndrome in range(space):
        if protected[syndrome]:
            continue
        current = representations[syndrome]
        assert current is not None, (
            "input partition misses syndrome %d" % syndrome)
        constraints.add(tuple(sorted(current)))
    return constraints, edges, cross_pairs


class Variables:
    def __init__(self) -> None:
        self.next_variable = 1

    def take(self) -> int:
        variable = self.next_variable
        self.next_variable += 1
        return variable


def solve_colors(
    constraints: set[tuple[int, ...]],
    edges: list[tuple[int, int]],
    blocks: int,
    target: int,
    solver_name: str,
) -> tuple[list[int], int, int]:
    bits = math.ceil(math.log2(target))
    assert bits > 0
    variables = Variables()
    block_bits = [
        [variables.take() for _ in range(bits)] for _ in range(blocks)
    ]
    relevant_edges = sorted({
        edge for constraint in constraints for edge in constraint
    })
    difference: dict[int, int] = {}
    clause_count = 0

    with Solver(name=solver_name) as solver:
        # A color permutation can always send block zero's color to zero.
        for variable in block_bits[0]:
            solver.add_clause([-variable])
            clause_count += 1

        # Exclude unused bit patterns when target is not a power of two.
        for block in range(blocks):
            for color in range(target, 1 << bits):
                solver.add_clause([
                    -variable if (color >> bit) & 1 else variable
                    for bit, variable in enumerate(block_bits[block])
                ])
                clause_count += 1

        for edge_identifier in relevant_edges:
            left, right = edges[edge_identifier]
            xor_bits: list[int] = []
            for bit in range(bits):
                left_bit = block_bits[left][bit]
                right_bit = block_bits[right][bit]
                xor_bit = variables.take()
                xor_bits.append(xor_bit)
                # xor_bit <=> left_bit XOR right_bit.
                solver.add_clause([-left_bit, -right_bit, -xor_bit])
                solver.add_clause([left_bit, right_bit, -xor_bit])
                solver.add_clause([left_bit, -right_bit, xor_bit])
                solver.add_clause([-left_bit, right_bit, xor_bit])
                clause_count += 4
            different = variables.take()
            difference[edge_identifier] = different
            for xor_bit in xor_bits:
                solver.add_clause([-xor_bit, different])
                clause_count += 1
            solver.add_clause([-different, *xor_bits])
            clause_count += 1

        for constraint in sorted(constraints):
            solver.add_clause([
                difference[edge_identifier]
                for edge_identifier in constraint
            ])
            clause_count += 1

        satisfiable = solver.solve()
        assert satisfiable, "no coarsening with at most %d blocks exists" % target
        positive = {
            literal for literal in solver.get_model() if literal > 0
        }

    colors = [
        sum(
            (1 << bit) if variable in positive else 0
            for bit, variable in enumerate(block_bits[block])
        )
        for block in range(blocks)
    ]
    assert all(0 <= color < target for color in colors)
    return colors, variables.next_variable - 1, clause_count


def verify_output(
    columns: list[int], labels: list[int], redundancy: int
) -> int:
    space = 1 << redundancy
    covered = bytearray(space)
    covered[0] = 1
    for left, column in enumerate(columns):
        covered[column] = 1
        for right in range(left):
            if labels[left] != labels[right]:
                covered[column ^ columns[right]] = 1
    count = sum(covered)
    assert count == space
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("matrix", type=Path)
    parser.add_argument("expected_r", type=int)
    parser.add_argument("expected_n", type=int)
    parser.add_argument("partition", type=Path)
    parser.add_argument("expected_blocks", type=int)
    parser.add_argument("target", type=int)
    parser.add_argument("output", type=Path)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()

    assert args.target > 1
    redundancy, length, columns = read_matrix(args.matrix)
    assert (redundancy, length) == (args.expected_r, args.expected_n)
    assert len(set(columns)) == length and all(columns)
    assert binary_rank(columns) == redundancy
    old_labels = read_partition(args.partition, length)
    blocks = len(set(old_labels))
    assert blocks == args.expected_blocks

    constraints, edges, cross_pairs = collect_constraints(
        columns, old_labels, redundancy, blocks)
    colors, variable_count, clause_count = solve_colors(
        constraints,
        edges,
        blocks,
        args.target,
        args.solver,
    )
    used_colors = sorted(set(colors))
    color_label = {
        color: label for label, color in enumerate(used_colors)
    }
    block_labels = [color_label[color] for color in colors]
    labels = [block_labels[old_label] for old_label in old_labels]
    output_blocks = len(used_colors)
    assert output_blocks <= args.target
    covered = verify_output(columns, labels, redundancy)

    with args.output.open("w", encoding="utf-8") as handle:
        handle.write("# SAT-found coarsening of %s.\n" % args.partition)
        handle.write(
            "# %d original blocks colored into %d blocks (target <= %d).\n" %
            (blocks, output_blocks, args.target))
        handle.write(
            "# Discovery only; certify with compute/verify_radius2_matrix.c.\n")
        handle.write(" ".join(str(label) for label in labels) + "\n")

    print(
        "PASS matrix=%s r=%d n=%d input_blocks=%d output_blocks=%d "
        "target=%d constraints=%d variables=%d clauses=%d cross_pairs=%d "
        "cross_block_covered=%d/%d output=%s" %
        (
            args.matrix,
            redundancy,
            length,
            blocks,
            output_blocks,
            args.target,
            len(constraints),
            variable_count,
            clause_count,
            cross_pairs,
            covered,
            1 << redundancy,
            args.output,
        )
    )


if __name__ == "__main__":
    main()
