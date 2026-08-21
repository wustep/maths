#!/usr/bin/env python3
"""Emit a parity-check matrix for a q11 fibered-family solution.

Usage: emit_H.py F M "<SOLUTION line>" <outfile> "<header comment>"
Rebuilds S from (A, g) exactly as verify_graph.py does, re-runs the flat
radius-2 sweep, and only then writes H (row i = bit i of the column integer).
"""
import sys
from verify_graph import check, parse

F, M = int(sys.argv[1]), int(sys.argv[2])
Amask, g = parse(sys.argv[3])
n, rk, got, tot, cols = check(F, M, Amask, g)
assert got == tot and rk == F + M, f"not a covering: rank {rk}, {got}/{tot}"
cols = sorted(cols)
with open(sys.argv[4], "w") as f:
    f.write(f"# {sys.argv[5]}\n")
    f.write(f"# {F+M} rows, {n} columns; entries are separated by one space\n")
    f.write("# row 1 is the least-significant bit of the integer column encoding\n")
    for i in range(F + M):
        f.write(" ".join(str(c >> i & 1) for c in cols) + "\n")
print(f"wrote {sys.argv[4]}: r={F+M} n={n} rank={rk} covered={got}/{tot}")
