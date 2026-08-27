"""Shared adjacency dump format for clique41.c.

Text file:

    n
    hex0
    hex1
    ...

Each hex line is the little-endian bitset of neighbours of that vertex
(bit j set iff {i,j} is an edge; loops are absent).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


def write_adj(path: Path, adj: Sequence[int], n: int) -> None:
    words = (n + 63) // 64
    lines = [str(n)]
    for bits in adj:
        hex_words = []
        x = bits
        for _ in range(words):
            hex_words.append(f"{x & ((1 << 64) - 1):016x}")
            x >>= 64
        lines.append(" ".join(hex_words))
    path.write_text("\n".join(lines) + "\n")


def read_adj(path: Path) -> List[int]:
    raw = path.read_text().split()
    n = int(raw[0])
    words = (n + 63) // 64
    vals = raw[1:]
    if len(vals) != n * words:
        raise ValueError(f"expected {n * words} words, got {len(vals)}")
    adj = []
    for i in range(n):
        bits = 0
        for w, h in enumerate(vals[i * words:(i + 1) * words]):
            bits |= int(h, 16) << (64 * w)
        adj.append(bits)
    return adj
