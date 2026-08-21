#!/usr/bin/env python3
"""Independent flat verifier for a q11 graph-family solution.

Reads a SOLUTION line of graph_search.c (A as hex bitmask over V, g as a list
indexed by u=1..2^M-1), rebuilds the column set

    S = { (v,0) : v in A }  u  { (g(u),u) : u in W\\{0} }   subset F_2^F x F_2^M

with the column integer v | (u << F), and checks, by a flat sweep over all 2^r
syndromes and all pairs of columns, that {0} u S u (S+S) = F_2^r.  Shares no
code with the DFS constraint encoding.
"""
import sys


def rank2(cols, r):
    basis = []
    for c in cols:
        for b in basis:
            c = min(c, c ^ b)
        if c:
            basis.append(c)
            basis.sort(reverse=True)
    return len(basis)


def build(F, M, Amask, g):
    cols = []
    for v in range(1, 1 << F):
        if Amask >> v & 1:
            cols.append(v)
    for u in range(1, 1 << M):
        cols.append(g[u - 1] | (u << F))
    return cols


def check(F, M, Amask, g):
    r = F + M
    cols = build(F, M, Amask, g)
    n = len(cols)
    assert len(set(cols)) == n, "repeated column"
    assert 0 not in cols, "zero column"
    cov = bytearray(1 << r)
    cov[0] = 1
    for c in cols:
        cov[c] = 1
    for i in range(n):
        for j in range(i + 1, n):
            cov[cols[i] ^ cols[j]] = 1
    return n, rank2(cols, r), sum(cov), 1 << r, cols


def parse(line):
    a = line.split("A=")[1].split()[0]
    g = [int(x) for x in line.split("g=")[1].strip().split(",")]
    return int(a, 16), g


if __name__ == "__main__":
    F, M = int(sys.argv[1]), int(sys.argv[2])
    for line in sys.stdin:
        if not line.startswith("SOLUTION"):
            continue
        Amask, g = parse(line)
        n, rk, got, tot, cols = check(F, M, Amask, g)
        ok = "OK" if got == tot and rk == F + M else "FAIL"
        print(f"n={n} rank={rk}/{F+M} covered={got}/{tot} {ok}")
        if ok == "OK":
            print("cols=" + " ".join(f"{c:0{(F+M+3)//4}x}" for c in sorted(cols)))
