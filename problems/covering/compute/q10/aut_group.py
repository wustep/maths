#!/usr/bin/env python3
"""Automorphism group of a column set S in F_2^r, as a subgroup of GL(r,2).

Aut(S) = { g in GL(r,2) : g(S) = S }.  This is what q10 prescribes, so it is
worth knowing whether the coverings people actually have carry any of it.

Method: colour the columns by refinable invariants (the pair-count w(x) =
#{ {a,b} in S : a+b = x } and its refinement through the "sum lands in S"
graph), then backtrack over the images of a basis drawn from S, pruning as soon
as some element of S already inside the span maps outside S.

Usage: aut_group.py <matrix-or-cols-file> [...]
"""
import sys
from collections import defaultdict


def read_set(path):
    """Accept either the H-matrix format (rows of bits) or one column per line."""
    rows, cols = [], []
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        tok = line.split()
        if all(t in ("0", "1") for t in tok) and len(tok) > 12:
            rows.append([int(t) for t in tok])
        else:
            cols += [int(t) for t in tok]
    if rows:
        r = len(rows)
        n = len(rows[0])
        cols = [sum((rows[i][j] & 1) << i for i in range(r)) for j in range(n)]
    r = max(c.bit_length() for c in cols)
    return r, sorted(set(cols))


def colours(r, S):
    N = 1 << r
    inS = bytearray(N)
    for s in S:
        inS[s] = 1
    w = [0] * N
    for i, a in enumerate(S):
        for b in S[i + 1:]:
            w[a ^ b] += 1
    col = {s: w[s] for s in S}
    for _ in range(6):
        new = {}
        for s in S:
            sig = sorted((col[t], w[s ^ t]) for t in S if t != s)
            new[s] = (col[s], tuple(sig))
        ranks = {k: i for i, k in enumerate(sorted(set(new.values())))}
        nxt = {s: ranks[new[s]] for s in S}
        if len(set(nxt.values())) == len(set(col.values())):
            col = nxt
            break
        col = nxt
    return w, inS, col


def aut(r, S, cap=200_000_000):
    w, inS, col = colours(r, S)
    by_col = defaultdict(list)
    for s in S:
        by_col[col[s]].append(s)

    # basis drawn from S, greedily, so the growing span swallows S early
    basis, span = [], {0}
    for s in S:
        if s not in span:
            basis.append(s)
            span |= {x ^ s for x in span}
        if len(basis) == r:
            break
    if len(basis) != r:
        raise SystemExit("S does not span")

    # coordinate of every s in S with respect to that basis
    pos = {}
    for mask in range(1 << r):
        val = 0
        for j in range(r):
            if (mask >> j) & 1:
                val ^= basis[j]
        pos[val] = mask
    # S elements first covered at level i+1: top bit of the coordinate is i
    fresh = [[] for _ in range(r)]
    for s in S:
        m = pos[s]
        fresh[m.bit_length() - 1].append(m)

    found = nodes = 0

    def rec(i, spanv, spanset):
        nonlocal found, nodes
        nodes += 1
        if nodes > cap:
            return
        if i == r:
            found += 1
            return
        for c in by_col[col[basis[i]]]:
            if c in spanset:
                continue                        # the image must stay independent
            half = [x ^ c for x in spanv]
            ok = True
            for mask in fresh[i]:
                if not inS[half[mask ^ (1 << i)]]:
                    ok = False
                    break
            if ok:
                rec(i + 1, spanv + half, spanset | set(half))
            if nodes > cap:
                return

    rec(0, [0], {0})
    return found, nodes, len(set(col.values()))


def main():
    for path in sys.argv[1:]:
        r, S = read_set(path)
        n, nodes, ncol = aut(r, S)
        print(f"{path}: r={r} |S|={len(S)}  colour classes={ncol}  "
              f"|Aut(S)|={n}  (backtrack nodes {nodes})")


if __name__ == "__main__":
    main()
