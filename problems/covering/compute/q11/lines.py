#!/usr/bin/env python3
"""Control for the q11 line-colouring reformulation.

For a solution (A, g) of the fibered family this checks, independently of the
search code, that

    radius 2  <=>  A is 1-saturating in V  and  B = V\\(A u {0}) is contained
                   in C_u = { tau(l) : l a line of PG(M-1,2) through u }
                   for every point u,

where tau({a,b,a+b}) = g(a)+g(b)+g(a+b).  It also reports whether tau is
bilinear (g quadratic), which Lemma A of the README forbids for M odd.

Usage: lines.py F M "<SOLUTION line>"
"""
import sys
from verify_graph import check, parse


def lines_of(M):
    out = []
    for a in range(1, 1 << M):
        for b in range(a + 1, 1 << M):
            c = a ^ b
            if c > b:
                out.append((a, b, c))
    return out


def main():
    F, M = int(sys.argv[1]), int(sys.argv[2])
    Amask, gl = parse(sys.argv[3])
    g = [0] + gl
    A = {v for v in range(1, 1 << F) if Amask >> v & 1}
    B = set(range(1, 1 << F)) - A
    tau = {}
    C = {u: set() for u in range(1, 1 << M)}
    for (a, b, c) in lines_of(M):
        t = g[a] ^ g[b] ^ g[c]
        tau[(a, b, c)] = t
        for p in (a, b, c):
            C[p].add(t)
    colour_ok = all(B <= C[u] for u in C)
    sat = {0} | A | {x ^ y for x in A for y in A if x != y}
    sat_ok = sat == set(range(1 << F))
    n, rk, got, tot, _ = check(F, M, Amask, gl)
    flat_ok = got == tot
    # bilinearity of tau, i.e. g quadratic
    T = {}
    for (a, b, c) in tau:
        for (x, y) in ((a, b), (a, c), (b, c)):
            T[(x, y)] = T[(y, x)] = tau[(a, b, c)]
    quad = all(T.get((w, u), 0) ^ T.get((w, v), 0) == T.get((w, u ^ v), 0)
               for w in range(1, 1 << M) for u in range(1, 1 << M)
               for v in range(1, 1 << M) if u != v and u ^ v != w and w != u and w != v)
    ncol = len({tau[l] for l in tau})
    print(f"F={F} M={M} n={n} |B|={len(B)} "
          f"colour-condition={colour_ok} fibre-0={sat_ok} flat-sweep={got}/{tot} "
          f"agree={(colour_ok and sat_ok) == flat_ok} tau-bilinear={quad} distinct-colours={ncol}")


main()
