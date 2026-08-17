#!/usr/bin/env python3
"""Involution t-MOLS in (σ,δ) coordinates.

A[r][c] = σ[r][c] + 6*δ[r][c] for r<6, with
A[r+6][c] = σ[r][c] + 6*(1-δ[r][c]).

σ[r][c] ∈ {0..5}, δ[r][c] ∈ {0,1}.

Primary variables:
  S[k][r][c][u]  u=0..5     1 + ((k*6+r)*12+c)*6 + u
  D[k][r][c]               after all S vars
"""

from __future__ import annotations

import argparse
import json
import sys

from encode_involution_mols import Cnf, HALF, N


def s_id(t: int, k: int, r: int, c: int, u: int) -> int:
    return 1 + (((k * HALF + r) * N + c) * HALF + u)


def n_sigma(t: int) -> int:
    return t * HALF * N * HALF


def d_id(t: int, k: int, r: int, c: int) -> int:
    return n_sigma(t) + 1 + ((k * HALF + r) * N + c)


def encode(t: int, normalize: bool = True) -> Cnf:
    cnf = Cnf()
    cnf._next = n_sigma(t) + t * HALF * N + 1
    cnf.n_orig = n_sigma(t) + t * HALF * N

    def S(k, r, c, u):
        return s_id(t, k, r, c, u)

    def D(k, r, c):
        return d_id(t, k, r, c)

    # each cell has one σ
    for k in range(t):
        for r in range(HALF):
            for c in range(N):
                cnf.eo_pairwise([S(k, r, c, u) for u in range(HALF)])

    # each column of σ is a permutation of {0..5}
    for k in range(t):
        for c in range(N):
            for u in range(HALF):
                cnf.eo_pairwise([S(k, r, c, u) for r in range(HALF)])

    # each row of σ contains each symbol twice, once at each δ
    for k in range(t):
        for r in range(HALF):
            for u in range(HALF):
                pos = [c for c in range(N)]
                # exactly two c with σ=u
                # exactly one of those has δ=0, one has δ=1
                # encode via: for the cells with σ=u, their D's are different
                # and there are exactly two such cells.
                # Use exactly-two sequential + link to D.
                lits = [S(k, r, c, u) for c in pos]
                # exactly two of lits
                _exactly_two(cnf, lits)
                # the two cells with σ=u have opposite δ:
                # for every pair c1<c2, S(c1,u) & S(c2,u) => D(c1) XOR D(c2)
                for i, c1 in enumerate(pos):
                    for c2 in pos[i + 1 :]:
                        # S1 & S2 => D1 != D2
                        cnf.add([-S(k, r, c1, u), -S(k, r, c2, u), D(k, r, c1), D(k, r, c2)])
                        cnf.add([-S(k, r, c1, u), -S(k, r, c2, u), -D(k, r, c1), -D(k, r, c2)])

    # Orthogonality of each pair of squares.
    # Cells must realize distinct +6-orbits of (A,B).
    # Orbit of (σA+6δA, σB+6δB) = orbit of same σ's and flipped δ's.
    # Two cells clash if (σA,σB) match AND (δA,δB) are equal or complementary.
    cells = [(r, c) for r in range(HALF) for c in range(N)]
    for k in range(t):
        for kp in range(k + 1, t):
            for i, (r1, c1) in enumerate(cells):
                for r2, c2 in cells[i + 1 :]:
                    for u in range(HALF):
                        for w in range(HALF):
                            # both cells have (σA,σB)=(u,w)
                            # then (D_k, D_kp) at the two cells must be
                            # neither equal nor complementary:
                            # i.e. they must differ in exactly one of the two
                            # δ-bits? Wait:
                            # equal: (d1,e1)=(d2,e2)
                            # complementary: (d1,e1)=(1-d2,1-e2)
                            # allowed: the other two relations,
                            # (d1,e1)=(d2,1-e2) or (1-d2,e2)
                            # i.e. the two δ-pairs differ in exactly one coordinate.
                            #
                            # Forbid equal:
                            # S's => not (D1=D2 and E1=E2)
                            # S's => not (D1!=D2 and E1!=E2)  [complementary]
                            # equivalently S's => (D1 XOR D2) XOR (E1 XOR E2) = 1
                            # i.e. they differ in exactly one δ.
                            base = [
                                -S(k, r1, c1, u),
                                -S(kp, r1, c1, w),
                                -S(k, r2, c2, u),
                                -S(kp, r2, c2, w),
                            ]
                            D1, E1 = D(k, r1, c1), D(kp, r1, c1)
                            D2, E2 = D(k, r2, c2), D(kp, r2, c2)
                            # forbid D1=D2 and E1=E2
                            cnf.add(base + [D1, D2, E1, E2])          # not all false
                            cnf.add(base + [D1, D2, -E1, -E2])
                            cnf.add(base + [-D1, -D2, E1, E2])
                            cnf.add(base + [-D1, -D2, -E1, -E2])
                            # forbid D1!=D2 and E1!=E2
                            cnf.add(base + [D1, -D2, E1, -E2])
                            cnf.add(base + [D1, -D2, -E1, E2])
                            cnf.add(base + [-D1, D2, E1, -E2])
                            cnf.add(base + [-D1, D2, -E1, E2])

    if normalize:
        # L0[0][c]=c means σ=c%6, δ=0 for c<6 and δ=1 for c>=6
        for c in range(N):
            cnf.add([S(0, 0, c, c % HALF)])
            if c < HALF:
                cnf.add([-D(0, 0, c)])
            else:
                cnf.add([D(0, 0, c)])
        # pair-index of L0[r][0] is r for r=1..5: σ[r][0] ∈ {r,...,5}
        for r in range(1, HALF):
            cnf.add([S(0, r, 0, u) for u in range(r, HALF)])
        # L_k[0][0]=0 => σ=0, δ=0
        for k in range(1, t):
            cnf.add([S(k, 0, 0, 0)])
            cnf.add([-D(k, 0, 0)])
        if t >= 3:
            # L1[0][1] <= L2[0][1] as 12-ary symbols σ+6δ
            # symbol = σ + 6δ. Compare as integers.
            # For all a>b, forbid L1=a and L2=b.
            def sym_lits(k, c, val):
                u, dbit = val % HALF, val // HALF
                # S(k,0,c,u) and D iff dbit
                return S(k, 0, c, u), D(k, 0, c), dbit

            for a in range(N):
                for b in range(a):
                    s1, d1, bit1 = sym_lits(1, 1, a)
                    s2, d2, bit2 = sym_lits(2, 1, b)
                    cl = [-s1, -s2]
                    cl.append(d1 if bit1 == 0 else -d1)
                    cl.append(d2 if bit2 == 0 else -d2)
                    cnf.add(cl)
    return cnf


def _exactly_two(cnf: Cnf, xs: list[int]) -> None:
    """Exactly two of xs are true.  |xs|=12, pairwise is fine enough."""
    m = len(xs)
    # at most two: for every triple, not all three
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                cnf.add([-xs[i], -xs[j], -xs[k]])
    # at least two: for every 11-set (i.e. omit one), at least two in the
    # whole set <=> not at most one.  Equiv: sum >= 2.
    # For every set of m-1=11 lits?  Simpler: the complement of "at most 1".
    # at least two <=> not (all false or exactly one).
    # all-false already killed by "each symbol twice" together with 6
    # symbols * 2 = 12, if we also have the row-σ covering...
    # Safer: sequential at-least-two.
    # For every set of 11 variables (leave one out), at least one is true
    # would be at least 2? No that is at least 1 after removing one = at least 2? 
    # If every 11-subset has a true, then at most one false, i.e. at least 11 true.
    # Wrong.
    # at least two: for every pair of positions being the only candidates...
    # Use: OR over all pairs (xi & xj).  CNF: for every set of m-1 zeros...
    # Standard: negate at-most-one of the complement.
    # I'll add: sum_{i<j} (xi & xj) >= 1 via aux.
    pair_aux = []
    for i in range(m):
        for j in range(i + 1, m):
            a = cnf.fresh()
            cnf.add([-a, xs[i]])
            cnf.add([-a, xs[j]])
            cnf.add([-xs[i], -xs[j], a])
            pair_aux.append(a)
    cnf.add(pair_aux)


def squares_from_model(t: int, lits: list[int]) -> list[list[list[int]]]:
    truth = {abs(x): x > 0 for x in lits}
    out = []
    for k in range(t):
        L = [[-1] * N for _ in range(N)]
        for r in range(HALF):
            for c in range(N):
                u = None
                for uu in range(HALF):
                    if truth.get(s_id(t, k, r, c, uu), False):
                        u = uu
                        break
                if u is None:
                    raise ValueError(f"no sigma {k},{r},{c}")
                d = 1 if truth.get(d_id(t, k, r, c), False) else 0
                L[r][c] = u + HALF * d
                L[r + HALF][c] = u + HALF * (1 - d)
        out.append(L)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("t", type=int)
    ap.add_argument("-o", "--output", default="-")
    args = ap.parse_args()
    cnf = encode(args.t)
    comments = [f"sigma-delta t={args.t} involution MOLS"]
    if args.output == "-":
        cnf.dump(sys.stdout, comments)
    else:
        with open(args.output, "w") as f:
            cnf.dump(f, comments)
        print(
            f"wrote {args.output}: {cnf._next-1} vars, {len(cnf.clauses)} clauses",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
