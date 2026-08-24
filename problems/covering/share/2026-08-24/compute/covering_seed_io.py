"""Shared I/O for the 16 August discovery programs.

This file lives in the 24 August pin compute snapshot. The matrix and
witness are siblings. The certified partition is in ../result/ (the
16 August result symlink on this pin).
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATRIX_PATH = HERE / "H_r10_n50.txt"
WITNESS_PATH = HERE / "witness_r10_n50.json"
PARTITION_PATH = HERE.parent / "result" / "data" / "partition_p10.json"

KR_HEX = (
    "1B6 193 1CC 187 1F6 F7 16E 140 3C 296 22F 303 381 365 "
    "11D 1A3 274 2F2 254 56 F 41 357 208 34 329 28D 31D 3D5 129 3D7 "
    "B7 3EC 2E2 23C AD 34E 155 2E6 371 D4"
).split()

MODULUS = {
    4: 0x13,  # x^4 + x + 1
    5: 0x25,  # x^5 + x^2 + 1
}


def read_matrix(path: Path = MATRIX_PATH):
    """Read an r x n 0/1 text matrix. Bit i of a column is row i+1."""
    rows = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            rows.append([int(tok) for tok in line.split()])
    if not rows:
        raise ValueError("%s: no data rows" % path)
    width = len(rows[0])
    for idx, row in enumerate(rows):
        if len(row) != width:
            raise ValueError("%s: ragged row %d" % (path, idx + 1))
        for tok in row:
            if tok not in (0, 1):
                raise ValueError("%s: token %r is not 0 or 1" % (path, tok))
    r = len(rows)
    n = width
    columns = [0] * n
    for i, row in enumerate(rows):
        bit = 1 << i
        for j, val in enumerate(row):
            if val:
                columns[j] |= bit
    return r, n, columns


def read_witness(path: Path = WITNESS_PATH):
    blob = json.loads(path.read_text(encoding="utf-8"))
    return [int(value) for value in blob["columns_decimal"]]


def read_partition(path: Path = PARTITION_PATH):
    blob = json.loads(path.read_text(encoding="utf-8"))
    return blob


def f2_rank(columns):
    """Rank over F_2, pivoting on the lowest set bit."""
    pivots = {}
    rank = 0
    for col in columns:
        cur = col
        while cur:
            low = cur & -cur
            if low not in pivots:
                pivots[low] = cur
                rank += 1
                break
            cur ^= pivots[low]
    return rank


def cover_mult(columns, r):
    """Multiplicity of each syndrome as a sum of at most two columns."""
    total = 1 << r
    mult = [0] * total
    mult[0] += 1
    for col in columns:
        mult[col] += 1
    n = len(columns)
    for i in range(n):
        ci = columns[i]
        for j in range(i + 1, n):
            mult[ci ^ columns[j]] += 1
    return mult


def pair_lists(columns, r):
    """For each syndrome, the unordered pairs of columns that sum to it."""
    lists = defaultdict(list)
    n = len(columns)
    for i in range(n):
        ci = columns[i]
        for j in range(i + 1, n):
            lists[ci ^ columns[j]].append((i, j))
    return lists


def gf_mul(a, b, m):
    """Carry-less multiply in GF(2^m), reduced by MODULUS[m]."""
    mod = MODULUS[m]
    top = 1 << m
    product = 0
    while b:
        if b & 1:
            product ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= mod
    return product


def allocate_indicators(block_of_column, m):
    """Deterministic QM indicators: one per block, then fill F_{2^m}."""
    size = 1 << m
    blocks = sorted(set(block_of_column))
    assert blocks == list(range(len(blocks)))
    p = len(blocks)
    members = {b: [j for j, bb in enumerate(block_of_column) if bb == b]
               for b in blocks}
    capacities = [len(members[b]) for b in blocks]
    assert p <= size <= sum(capacities)
    counts = [1] * p
    remaining = size - p
    for b in range(p):
        if remaining <= 0:
            break
        extra = min(capacities[b] - 1, remaining)
        counts[b] += extra
        remaining -= extra
    assert remaining == 0
    indicator_sets = {}
    nxt = 0
    for b in range(p):
        indicator_sets[b] = list(range(nxt, nxt + counts[b]))
        nxt += counts[b]
    betas = [None] * len(block_of_column)
    for b in range(p):
        pool = indicator_sets[b]
        for pos, j in enumerate(members[b]):
            betas[j] = pool[pos % len(pool)]
    assert set(betas) == set(range(size))
    return betas


def qm2_squared(r0, columns0, block_of_column, m):
    """Construction QM_2^2 from (4.2) and (4.4) of arXiv:2511.02542."""
    n0 = len(columns0)
    size = 1 << m
    p0 = len(set(block_of_column))
    assert n0 >= size >= p0
    betas = allocate_indicators(block_of_column, m)
    shift_xi = r0
    shift_bx = r0 + m
    columns = []
    for w in range(1, size):
        columns.append(w << shift_bx)
    for j in range(n0):
        hj = columns0[j]
        bj = betas[j]
        for xi in range(size):
            columns.append(
                hj | (xi << shift_xi) | (gf_mul(bj, xi, m) << shift_bx)
            )
    r = r0 + 2 * m
    n = size * (n0 + 1) - 1
    assert len(columns) == n
    return r, columns


def density(n, r):
    return (1 + n + n * (n - 1) // 2) / (1 << r)
