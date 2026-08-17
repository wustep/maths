#!/usr/bin/env python3
"""Check a kissat model against the CH-triangle encoding."""

from __future__ import annotations

import sys
from encode_ch import var_id


def parse_model(text: str) -> set[int]:
    pos = set()
    for line in text.splitlines():
        if not line.startswith("v "):
            continue
        for tok in line.split()[1:]:
            if tok == "0":
                continue
            lit = int(tok)
            if lit > 0:
                pos.add(lit)
    return pos


def check(n: int, d: int, pos: set[int]) -> dict:
    arcs = []
    outdeg = [0] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if var_id(n, i, j) in pos:
                arcs.append((i, j))
                outdeg[i] += 1
    two = [(i, j) for i, j in arcs if (j, i) in set(arcs)]
    tris = []
    for i, j, k in (
        (a, b, c) for a in range(n) for b in range(n) for c in range(n) if len({a, b, c}) == 3
    ):
        if (i, j) in set(arcs) and (j, k) in set(arcs) and (k, i) in set(arcs):
            if (i, j, k) <= (j, k, i) and (i, j, k) <= (k, i, j):
                tris.append((i, j, k))
    return {
        "n": n,
        "d": d,
        "narcs": len(arcs),
        "outdeg": outdeg,
        "min_out": min(outdeg) if outdeg else None,
        "two_cycles": two,
        "triangles": tris,
        "ok": min(outdeg) >= d and not two and not tris,
        "arcs": arcs,
    }


def main():
    n = int(sys.argv[1])
    d = int(sys.argv[2])
    text = sys.stdin.read()
    if "s UNSATISFIABLE" in text:
        print("UNSAT")
        return
    if "s SATISFIABLE" not in text:
        print("NO-RESULT")
        print(text[-400:])
        return
    pos = parse_model(text)
    info = check(n, d, pos)
    print(info)


if __name__ == "__main__":
    main()
