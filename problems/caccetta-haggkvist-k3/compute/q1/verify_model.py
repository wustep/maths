#!/usr/bin/env python3
"""Check a SAT model against the exact CH-triangle statement."""

from __future__ import annotations

import sys

from encode import var_id


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
    indeg = [0] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if var_id(n, i, j) in pos:
                arcs.append((i, j))
                outdeg[i] += 1
                indeg[j] += 1
    arcset = set(arcs)
    two = [(i, j) for i, j in arcs if (j, i) in arcset]
    tris = []
    for i, j, k in (
        (a, b, c)
        for a in range(n)
        for b in range(n)
        for c in range(n)
        if len({a, b, c}) == 3
    ):
        if (i, j) in arcset and (j, k) in arcset and (k, i) in arcset:
            if (i, j, k) <= (j, k, i) and (i, j, k) <= (k, i, j):
                tris.append((i, j, k))
    return {
        "n": n,
        "d": d,
        "narcs": len(arcs),
        "outdeg": outdeg,
        "indeg": indeg,
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
    info = check(n, d, parse_model(text))
    print(info)


if __name__ == "__main__":
    main()
