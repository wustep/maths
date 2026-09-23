#!/usr/bin/env python3
"""Cross-check the 3-to-2 hole reduction against flat syndrome sweeps."""
from pathlib import Path
from random import Random

matrix = Path(__file__).resolve().parents[1] / "H_r10_n50.txt"
rows = [
    [int(v) for v in line.split()]
    for line in matrix.read_text().splitlines()
    if line and not line.startswith("#")
]
assert len(rows) == 10 and all(len(row) == 50 for row in rows)
source = [sum(rows[i][j] << i for i in range(10)) for j in range(50)]
assert len(set(source)) == 50

random = Random(14)
for _ in range(256):
    deleted = set(random.sample(range(50), 3))
    base = [v for i, v in enumerate(source) if i not in deleted]
    outside = [v for v in range(1, 1024) if v not in base]
    x, y = random.sample(outside, 2)
    base_cover = {0, *base}
    base_cover.update(v ^ w for i, v in enumerate(base) for w in base[:i])
    direct_columns = base + [x, y]
    direct = {0, *direct_columns}
    direct.update(v ^ w for i, v in enumerate(direct_columns) for w in direct_columns[:i])
    predicted = base_cover | {x, y, x ^ y}
    predicted.update(x ^ v for v in base)
    predicted.update(y ^ v for v in base)
    assert predicted == direct
print("audit: 256 deterministic 3-to-2 cases agree with flat 1024-syndrome sweeps")
