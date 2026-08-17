#!/usr/bin/env python3
"""Decode a kissat SAT model of involution_sat.py into a graph and verify it."""

from __future__ import annotations

import sys
from pathlib import Path

from r55lib import dump_json, is_ramsey, n_edges, to_graph6


def parse_model(text: str) -> set[int]:
    pos = set()
    for line in text.splitlines():
        if not line or line[0] == "c":
            continue
        if line.startswith("s "):
            continue
        if line[0] == "v" or line[0].isdigit() or line[0] == "-":
            toks = line.split()
            if toks and toks[0] == "v":
                toks = toks[1:]
            for t in toks:
                if t == "0":
                    continue
                v = int(t)
                if v > 0:
                    pos.add(v)
    return pos


def rebuild(n: int, pos: set[int]) -> list[int]:
    npairs = (n - 1) // 2
    na, nb = npairs, npairs
    np_ = npairs * (npairs - 1) // 2
    pair_index = {}
    k = 0
    for i in range(npairs):
        for j in range(i + 1, npairs):
            pair_index[(i, j)] = k
            k += 1

    def a(i):
        return 1 + i

    def b(i):
        return 1 + na + i

    def p(i, j):
        if i > j:
            i, j = j, i
        return 1 + na + nb + pair_index[(i, j)]

    def c(i, j):
        if i > j:
            i, j = j, i
        return 1 + na + nb + np_ + pair_index[(i, j)]

    nbr = [0] * n
    def add(u, v):
        nbr[u] |= 1 << v
        nbr[v] |= 1 << u

    for i in range(npairs):
        if a(i) in pos:
            add(0, 2 * i + 1)
            add(0, 2 * i + 2)
        if b(i) in pos:
            add(2 * i + 1, 2 * i + 2)
    for i in range(npairs):
        for j in range(i + 1, npairs):
            if p(i, j) in pos:
                add(2 * i + 1, 2 * j + 1)
                add(2 * i + 2, 2 * j + 2)
            if c(i, j) in pos:
                add(2 * i + 1, 2 * j + 2)
                add(2 * i + 2, 2 * j + 1)
    return nbr


def main() -> int:
    n = int(sys.argv[1])
    model_path = Path(sys.argv[2])
    pos = parse_model(model_path.read_text())
    nbr = rebuild(n, pos)
    ok = is_ramsey(nbr)
    rec = {
        "n": n,
        "edges": n_edges(nbr),
        "is_55": ok,
        "g6": to_graph6(nbr),
    }
    print(rec)
    dest = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("certs/involution_model.json")
    dump_json(str(dest), rec)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
