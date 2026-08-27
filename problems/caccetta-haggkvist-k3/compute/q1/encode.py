#!/usr/bin/env python3
"""CNF for a C3-free oriented n-vertex graph with out-degree exactly d.

Same statement as ../encode_ch.py, with two encoding changes:

1. Sinz sequential counters (linear size) instead of binomial subsets.
   The parent encoder's at-most-6 on 17 literals is C(17,7) = 19448
   clauses per vertex; here it is O(n d).
2. Optional in-neighbourhood symmetry: fix N-(0) = {d+1,...,d+k}.
   Always legal by relabelling the vertices outside {0} ∪ N+(0).
   Each k is a separate cube.  For n=18, d=6 the range is k=0..11,
   and k=11 is immediately empty (each v in N+(0) would need 6
   out-neighbours from 5 legal candidates).

Usage:
    python3 encode.py --n 9 --d 3 > /tmp/ch9-3.cnf
    python3 encode.py --n 18 --d 6 --indeg0 6 > /tmp/ch18-6-k6.cnf
"""

from __future__ import annotations

import argparse
import itertools
import sys


def var_id(n: int, i: int, j: int) -> int:
    return i * n + j + 1


def sinz_atmost(xs, k, fresh):
    """Sinz sequential counter: at most k of xs are true.

    Auxiliary s[i][j] (i=0..n-2, j=0..k-1): at least j+1 of xs[0..i]
    are true.  See Sinz, SAT 2005, encoding (1).
    """
    clauses = []
    n = len(xs)
    if k >= n:
        return clauses
    if k < 0:
        return [[]]
    if k == 0:
        return [[-x] for x in xs]
    s = [[fresh() for _ in range(k)] for _ in range(n - 1)]
    clauses.append([-xs[0], s[0][0]])
    for j in range(1, k):
        clauses.append([-s[0][j]])
    for i in range(1, n - 1):
        clauses.append([-xs[i], s[i][0]])
        clauses.append([-s[i - 1][0], s[i][0]])
        for j in range(1, k):
            clauses.append([-xs[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-xs[i], -s[i - 1][k - 1]])
    clauses.append([-xs[-1], -s[n - 2][k - 1]])
    return clauses


def sinz_atleast(xs, k, fresh):
    """At least k of xs: at most (n-k) of the negated literals."""
    return sinz_atmost([-x for x in xs], len(xs) - k, fresh)


def sinz_exactly(xs, k, fresh):
    return sinz_atleast(xs, k, fresh) + sinz_atmost(xs, k, fresh)


def encode(
    n: int,
    d: int,
    exact: bool = True,
    sb: bool = True,
    indeg0: int | None = None,
    exact_in: bool = False,
):
    """Return (clauses, nvars).

    indeg0: if set, force N-(0) = {d+1, ..., d+indeg0} and no edge
    between 0 and the leftover vertices.  Vertices in N-(0) already
    have the out-arc to 0, so they need d-1 further out-neighbours.
    """
    clauses = []
    for i in range(n):
        clauses.append([-var_id(n, i, i)])
    for i in range(n):
        for j in range(i + 1, n):
            clauses.append([-var_id(n, i, j), -var_id(n, j, i)])
    for i, j, k in itertools.combinations(range(n), 3):
        clauses.append([-var_id(n, i, j), -var_id(n, j, k), -var_id(n, k, i)])
        clauses.append([-var_id(n, i, k), -var_id(n, k, j), -var_id(n, j, i)])

    # N+(0) = {1,...,d}
    for j in range(1, d + 1):
        clauses.append([var_id(n, 0, j)])
        clauses.append([-var_id(n, j, 0)])
    for j in range(d + 1, n):
        clauses.append([-var_id(n, 0, j)])

    if indeg0 is not None:
        if indeg0 < 0 or d + indeg0 > n - 1:
            return [[]], 1
        # N-(0) = {d+1,...,d+indeg0}; leftover nonadjacent to 0
        for j in range(d + 1, d + indeg0 + 1):
            clauses.append([var_id(n, j, 0)])
        for j in range(d + indeg0 + 1, n):
            clauses.append([-var_id(n, j, 0)])
        # triangle 0 → a → b → 0 with a in N+(0), b in N-(0):
        # already a unit from N+(0) not pointing to 0, and
        # a → b is forbidden because b → 0.
        for a in range(1, d + 1):
            for b in range(d + 1, d + indeg0 + 1):
                clauses.append([-var_id(n, a, b)])

    nvars = n * n
    next_id = nvars + 1

    def fresh():
        nonlocal next_id
        v = next_id
        next_id += 1
        return v

    for i in range(n):
        outs = [var_id(n, i, j) for j in range(n) if j != i]
        need = d
        if indeg0 is not None and d + 1 <= i <= d + indeg0:
            # already has i → 0
            need = d - 1
            outs = [var_id(n, i, j) for j in range(n) if j != i and j != 0]
        if i == 0:
            continue  # out-neighbourhood of 0 is fixed
        if exact:
            clauses.extend(sinz_exactly(outs, need, fresh))
        else:
            clauses.extend(sinz_atleast(outs, need, fresh))

    if exact_in:
        for i in range(n):
            ins = [var_id(n, j, i) for j in range(n) if j != i]
            if i == 0 and indeg0 is not None:
                continue
            clauses.extend(sinz_exactly(ins, d, fresh))

    def add_lex(xs, ys):
        """xs <= ys lexicographically, with 1 > 0.  Prefix-equality aux."""
        p_prev = None
        for x, y in zip(xs, ys):
            if p_prev is None:
                clauses.append([-x, y])
                p = fresh()
                clauses.append([-p, -x, y])
                clauses.append([-p, -y, x])
                clauses.append([x, y, p])
                clauses.append([-x, -y, p])
                p_prev = p
            else:
                clauses.append([-p_prev, -x, y])
                p = fresh()
                eq = fresh()
                clauses.append([-eq, -x, y])
                clauses.append([-eq, -y, x])
                clauses.append([x, y, eq])
                clauses.append([-x, -y, eq])
                clauses.append([-p, p_prev])
                clauses.append([-p, eq])
                clauses.append([p, -p_prev, -eq])
                p_prev = p

    if sb and d >= 1:

        def outbits(v):
            return [var_id(n, v, j) for j in range(n) if j != v]

        for a, b in zip(range(1, d), range(2, d + 1)):
            add_lex(outbits(a), outbits(b))
        if indeg0 is not None:
            # lex inside N-(0) and inside the non-neighbours of 0
            inn = range(d + 1, d + indeg0 + 1)
            rest = range(d + indeg0 + 1, n)
            for group in (inn, rest):
                gl = list(group)
                for a, b in zip(gl, gl[1:]):
                    add_lex(outbits(a), outbits(b))
        else:
            for a, b in zip(range(d + 1, n - 1), range(d + 2, n)):
                add_lex(outbits(a), outbits(b))

    nvars = next_id - 1
    clean = []
    for c in clauses:
        if not c:
            clean.append([])
            continue
        s = set(c)
        if any(-l in s for l in s):
            continue
        clean.append(sorted(s, key=lambda x: (abs(x), x)))
    return clean, nvars


def write_cnf(clauses, nvars, out):
    out.write(f"p cnf {nvars} {len(clauses)}\n")
    for c in clauses:
        out.write(" ".join(str(x) for x in c) + " 0\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--d", type=int, required=True)
    ap.add_argument("--atleast", action="store_true")
    ap.add_argument("--no-sb", action="store_true")
    ap.add_argument("--indeg0", type=int, default=None, help="fix |N-(0)|=k and the labels")
    ap.add_argument("--exact-in", action="store_true", help="force every in-degree = d")
    args = ap.parse_args()
    clauses, nvars = encode(
        args.n,
        args.d,
        exact=not args.atleast,
        sb=not args.no_sb,
        indeg0=args.indeg0,
        exact_in=args.exact_in,
    )
    write_cnf(clauses, nvars, sys.stdout)


if __name__ == "__main__":
    main()
