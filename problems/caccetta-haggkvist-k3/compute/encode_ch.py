#!/usr/bin/env python3
"""CNF for a C3-free oriented n-vertex graph with min out-degree d.

Variables x_{i,j} (i≠j): arc i→j.  At most one of x_ij, x_ji.
Each out-neighbourhood has size at least d (exactly d after unit-propagation
if we also cap at d; we force exactly d).
No directed 3-cycle.

Symmetry: N⁺(0) = {1,…,d}.

Usage:
    python3 encode_ch.py --n 9 --d 3 > /tmp/ch9-3.cnf
    ./kissat /tmp/ch9-3.cnf
"""

from __future__ import annotations

import argparse
import itertools
import sys


def var_id(n: int, i: int, j: int) -> int:
    # 1-based DIMACS.  n*n grid, skip diagonals but keep the numbering simple:
    # id = i*n + j + 1, unused on the diagonal.
    return i * n + j + 1


def binomial_atleast(vars_list, k):
    """Every subset of size m-k+1 contains a true var.  No auxiliaries."""
    xs = list(vars_list)
    m = len(xs)
    if k <= 0:
        return []
    if k > m:
        return [[]]
    need = m - k + 1
    return [list(comb) for comb in itertools.combinations(xs, need)]


def binomial_atmost(vars_list, k):
    """Every subset of size k+1 contains a false var."""
    xs = list(vars_list)
    m = len(xs)
    if k >= m:
        return []
    if k < 0:
        return [[]]
    return [[-v for v in comb] for comb in itertools.combinations(xs, k + 1)]


def lex_leq(xs, ys):
    """Clauses: bitstring xs <= ys in lexicographic order (1 > 0)."""
    # aux e_k: first k bits equal
    clauses = []
    # we'll encode without aux: for each prefix
    # (¬x0 ∨ y0)  and for k>0: (x0∨¬y0 ∨ x1∨¬y1 ∨ ... ∨ x_{k-1}∨¬y_{k-1} ∨ ¬x_k ∨ y_k)
    # i.e. if prefix equal and x_k=1 then y_k=1
    m = len(xs)
    # equality-prefix auxiliaries p_0=True, p_{k+1} = p_k ∧ (x_k ↔ y_k)
    # Keep it aux-free: for each k, (eq-prefix ⇒ ¬x_k ∨ y_k)
    # eq-prefix = ∧_{j<k} (x_j↔y_j) encoded as:
    # ∨_{j<k} (x_j ⊕ y_j) ∨ ¬x_k ∨ y_k
    # x⊕y = (x∨y) ∧ (¬x∨¬y) is two lits... CNF of
    # (∧_j (x_j↔y_j)) → (¬x_k ∨ y_k)
    # ≡ ∨_j ¬(x_j↔y_j) ∨ ¬x_k ∨ y_k
    # ¬(x↔y) = (x∨y) ∧ (¬x∨¬y), so we need a Tseitin xor or just
    # the two-clause expansion:
    # For a small m we introduce xor vars.
    return clauses  # filled below with aux in encode()


def encode(n: int, d: int, exact: bool = True, sb: bool = True):
    clauses = []
    # unused diagonal variables stay false
    for i in range(n):
        clauses.append([-var_id(n, i, i)])
    # oriented: at most one direction
    for i in range(n):
        for j in range(i + 1, n):
            clauses.append([-var_id(n, i, j), -var_id(n, j, i)])
    # no directed triangle
    for i, j, k in itertools.combinations(range(n), 3):
        clauses.append([-var_id(n, i, j), -var_id(n, j, k), -var_id(n, k, i)])
        clauses.append([-var_id(n, i, k), -var_id(n, k, j), -var_id(n, j, i)])
    # symmetry: N⁺(0) = {1,…,d}
    for j in range(1, d + 1):
        clauses.append([var_id(n, 0, j)])
        clauses.append([-var_id(n, j, 0)])
    for j in range(d + 1, n):
        clauses.append([-var_id(n, 0, j)])
    for i in range(n):
        outs = [var_id(n, i, j) for j in range(n) if j != i]
        if exact:
            clauses.extend(binomial_atleast(outs, d))
            clauses.extend(binomial_atmost(outs, d))
        else:
            clauses.extend(binomial_atleast(outs, d))
    nvars = n * n
    next_id = nvars + 1

    def fresh():
        nonlocal next_id
        v = next_id
        next_id += 1
        return v

    def add_lex(xs, ys):
        """xs <= ys lexicographically, with 1 > 0."""
        # p_k: first k bits equal. p_0 true.
        # p_{k+1} ↔ p_k ∧ (x_k ↔ y_k)
        # p_k → (¬x_k ∨ y_k)
        m = len(xs)
        p_prev = None
        for k in range(m):
            x, y = xs[k], ys[k]
            if p_prev is None:
                clauses.append([-x, y])
                # p1 ↔ (x↔y)
                p = fresh()
                # x↔y = (¬x∨y)∧(¬y∨x)
                # p → (x↔y): (¬p∨¬x∨y) (¬p∨¬y∨x)
                clauses.append([-p, -x, y])
                clauses.append([-p, -y, x])
                # (x↔y) → p: (x∨y∨p) (¬x∨¬y∨p)
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
                # p ↔ p_prev ∧ eq
                clauses.append([-p, p_prev])
                clauses.append([-p, eq])
                clauses.append([p, -p_prev, -eq])
                p_prev = p

    if sb and d >= 1:
        # order N⁺(0) = {1..d} by out-neighbourhood bitstrings
        def outbits(v):
            return [var_id(n, v, j) for j in range(n) if j != v]

        for a, b in zip(range(1, d), range(2, d + 1)):
            add_lex(outbits(a), outbits(b))
        # order the rest
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
    ap.add_argument("--atleast", action="store_true", help="δ⁺ ≥ d instead of = d")
    ap.add_argument("--no-sb", action="store_true", help="disable lex symmetry breaking")
    args = ap.parse_args()
    clauses, nvars = encode(args.n, args.d, exact=not args.atleast, sb=not args.no_sb)
    write_cnf(clauses, nvars, sys.stdout)


if __name__ == "__main__":
    main()
