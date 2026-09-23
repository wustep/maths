#!/usr/bin/env python3
"""Independent full syndrome sweep of the best two-delete/one-add miss."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = [
    [int(value) for value in line.split()]
    for line in (root / "H_r10_n50.txt").read_text().splitlines()
    if line and not line.startswith("#")
]
assert len(rows) == 10 and all(len(row) == 50 for row in rows)
columns = [sum(rows[i][j] << i for i in range(10)) for j in range(50)]
candidate = [v for j, v in enumerate(columns) if j not in (0, 21)] + [1]
assert len(candidate) == len(set(candidate)) == 49
basis = {}
for value in candidate:
    while value:
        pivot = value.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            break
assert len(basis) == 10
covered = {0, *candidate}
covered.update(a ^ b for i, a in enumerate(candidate) for b in candidate[:i])
holes = [s for s in range(1024) if s not in covered]
assert holes == [8, 40, 349, 381, 584, 616, 797, 829, 931]
print(f"best local candidate: rank 10, {len(covered)}/1024 covered, holes={holes}")
