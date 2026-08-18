#!/usr/bin/env python3
"""SAT encoding of the n=49 radius-2 covering problem for r=10.

Variables x_v for v in 1..1023 (column v selected).  For each unordered
pair {v, w} an auxiliary y_{v,w} with y -> x_v and y -> x_w; for each
syndrome s != 0 a coverage clause  x_s  OR  OR_{v<w, v^w=s} y_{v,w}.
Cardinality: sum x_v <= 49 (sequential counter).

WLOG reduction: a rank-10 covering contains 10 linearly independent
columns; some element of GL(10,2) maps them to the unit vectors.  So we
assert x_{2^i} = 1 for i = 0..9 and search for the other 39 columns.
This is sound for existence: a 49-covering exists iff one containing
the unit vectors exists.

Output: prints SAT + a verified column list, or UNSAT (which would
prove no 49-covering exists - do not expect this to terminate), or
runs until the caller's timeout.  Deterministic given the solver.
"""

import sys
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195

V = 1024
N_TARGET = 49


def main():
    pool = IDPool()
    x = {v: pool.id(("x", v)) for v in range(1, V)}
    clauses = []

    # pair auxiliaries and coverage clauses
    for s in range(1, V):
        cover = [x[s]]
        for v in range(1, V):
            w = v ^ s
            if v < w:
                y = pool.id(("y", v, w))
                cover.append(y)
        clauses.append(cover)
    # y -> x_v, y -> x_w (only for created ys)
    for key, ident in list(pool.obj2id.items()):
        if key[0] == "y":
            _, v, w = key
            clauses.append([-ident, x[v]])
            clauses.append([-ident, x[w]])

    # unit vectors forced in (WLOG via GL(10,2))
    for i in range(10):
        clauses.append([x[1 << i]])

    card = CardEnc.atmost(lits=[x[v] for v in range(1, V)], bound=N_TARGET,
                          vpool=pool, encoding=EncType.seqcounter)
    clauses.extend(card.clauses)

    print("clauses=%d vars=%d" % (len(clauses), pool.top), flush=True)
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        if not sat:
            print("UNSAT: no 49-covering containing the unit frame "
                  "(hence none at all)")
            return 1
        model = set(l for l in solver.get_model() if l > 0)
        cols = [v for v in range(1, V) if x[v] in model]
        print("SAT columns(%d): %s" % (len(cols), " ".join(map(str, cols))))
        # independent flat verification
        covered = bytearray(V)
        covered[0] = 1
        for i, a in enumerate(cols):
            covered[a] = 1
            for b in cols[:i]:
                covered[a ^ b] = 1
        holes = [v for v in range(V) if not covered[v]]
        print("verified holes=%d %s" % (len(holes), holes[:20]))
        return 0


if __name__ == "__main__":
    sys.exit(main())
