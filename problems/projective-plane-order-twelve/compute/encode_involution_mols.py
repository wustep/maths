#!/usr/bin/env python3
"""DIMACS CNF for t MOLS of order 12 with the involutory-elation symmetry.

A Latin square L of order 12 satisfies the involution constraint if
    L[r+6][c] == (L[r][c] + 6) % 12
for all r,c.  After the standard coordinatization of an affine plane of
order 12 with a translation τ(x,y)=(x+6,y), every square in the
associated MOLS family can be symbol-relabelled to this form.

Only the top half r=0..5 is encoded.  The bottom half is determined.
"""

from __future__ import annotations

import argparse
import sys


N = 12
HALF = 6


class Cnf:
    def __init__(self) -> None:
        self.clauses: list[list[int]] = []
        self._next = 1
        self.n_orig = 0

    def fresh(self, n: int = 1) -> int:
        v = self._next
        self._next += n
        return v

    def add(self, lits: list[int]) -> None:
        self.clauses.append(lits)

    def amo_pairwise(self, xs: list[int]) -> None:
        for i, a in enumerate(xs):
            for b in xs[i + 1 :]:
                self.add([-a, -b])

    def eo_pairwise(self, xs: list[int]) -> None:
        self.add(list(xs))
        self.amo_pairwise(xs)

    def amo_sequential(self, xs: list[int]) -> None:
        """Sinz sequential counter: at most one of xs."""
        m = len(xs)
        if m <= 6:
            self.amo_pairwise(xs)
            return
        s = [self.fresh() for _ in range(m - 1)]
        self.add([-xs[0], s[0]])
        self.add([-xs[m - 1], -s[m - 2]])
        for i in range(1, m - 1):
            self.add([-xs[i], s[i]])
            self.add([-s[i - 1], s[i]])
            self.add([-xs[i], -s[i - 1]])

    def eo_sequential(self, xs: list[int]) -> None:
        self.add(list(xs))
        self.amo_sequential(xs)

    def dump(self, out, comments: list[str] | None = None) -> None:
        if comments:
            for line in comments:
                out.write(f"c {line}\n")
        nvars = self._next - 1
        out.write(f"p cnf {nvars} {len(self.clauses)}\n")
        for cl in self.clauses:
            out.write(" ".join(str(x) for x in cl) + " 0\n")


def var_id(t: int, k: int, r: int, c: int, s: int) -> int:
    """1-based variable: square k, row r<6, col c, symbol s."""
    return 1 + (((k * HALF + r) * N + c) * N + s)


def n_primary(t: int) -> int:
    return t * HALF * N * N


def encode(t: int, normalize: bool = True) -> Cnf:
    if t < 1:
        raise ValueError("t >= 1")
    cnf = Cnf()
    cnf._next = n_primary(t) + 1
    cnf.n_orig = n_primary(t)

    def X(k: int, r: int, c: int, s: int) -> int:
        return var_id(t, k, r, c, s)

    # Each free cell has exactly one symbol.
    for k in range(t):
        for r in range(HALF):
            for c in range(N):
                cnf.eo_pairwise([X(k, r, c, s) for s in range(N)])

    # Each free row is a permutation of Z_12.
    for k in range(t):
        for r in range(HALF):
            for s in range(N):
                cnf.eo_pairwise([X(k, r, c, s) for c in range(N)])

    # Each column of the free half is a transversal of the pairs {u,u+6}.
    for k in range(t):
        for c in range(N):
            for u in range(HALF):
                lits = []
                for r in range(HALF):
                    lits.append(X(k, r, c, u))
                    lits.append(X(k, r, c, u + HALF))
                cnf.eo_sequential(lits)

    # Orthogonality of each pair of squares: the 72 free cells hit 72
    # distinct orbits of symbol-pairs under (s,s') |-> (s+6,s'+6).
    # Orbit representatives: (s, s') with s in 0..5.
    for k in range(t):
        for kp in range(k + 1, t):
            for s in range(HALF):
                for sp in range(N):
                    # literals "cell (r,c) realises this orbit"
                    orbit_lits: list[int] = []
                    for r in range(HALF):
                        for c in range(N):
                            # aux <-> (X(k,r,c,s) & X(kp,r,c,sp))
                            #    or  (X(k,r,c,s+6) & X(kp,r,c,(sp+6)%12))
                            a = cnf.fresh()
                            b = cnf.fresh()
                            o = cnf.fresh()
                            # a <-> X(k,s) & X(kp,sp)
                            cnf.add([-a, X(k, r, c, s)])
                            cnf.add([-a, X(kp, r, c, sp)])
                            cnf.add([-X(k, r, c, s), -X(kp, r, c, sp), a])
                            # b <-> X(k,s+6) & X(kp,sp+6)
                            cnf.add([-b, X(k, r, c, s + HALF)])
                            cnf.add([-b, X(kp, r, c, (sp + HALF) % N)])
                            cnf.add(
                                [
                                    -X(k, r, c, s + HALF),
                                    -X(kp, r, c, (sp + HALF) % N),
                                    b,
                                ]
                            )
                            # o <-> a or b
                            cnf.add([-o, a, b])
                            cnf.add([-a, o])
                            cnf.add([-b, o])
                            orbit_lits.append(o)
                    cnf.amo_sequential(orbit_lits)

    if normalize:
        # Column permutation can make the first row of square 0 the
        # identity and preserves L[r+6][c] = L[r][c]+6.  The same
        # column permutation is shared by every square, so we cannot
        # also force the first row of L_k, k>=1, to be the identity:
        # the leftover symbol relabelling of L_k has to commute with
        # +6, and that is not always possible.  First-column identity
        # on square 0 is likewise unsafe (the free half of a column is
        # only a transversal of the pairs {u,u+6}).
        for c in range(N):
            cnf.add([X(0, 0, c, c)])
        # Permute free rows 1..5 (and their +6 partners) so the pair
        # index of L_0[r][0] is strictly increasing.  Each free entry
        # of column 0 uses a different pair {u,u+6}.
        for r in range(1, HALF):
            allowed = []
            for u in range(r, HALF):
                allowed.append(X(0, r, 0, u))
                allowed.append(X(0, r, 0, u + HALF))
            cnf.add(allowed)
        # Independent +6-commuting symbol relabel of square k>=1 can
        # send the pair of L_k[0][0] to {0,6} and unflip it to 0.
        for k in range(1, t):
            cnf.add([X(k, 0, 0, 0)])
        # Swap of squares 1 and 2 can sort L_1[0][1] <= L_2[0][1].
        if t >= 3:
            for a in range(N):
                for b in range(a):
                    cnf.add([-X(1, 0, 1, a), -X(2, 0, 1, b)])

    return cnf


def parse_model_lits(path: str) -> list[int]:
    lits: list[int] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] == "c":
                continue
            if line[0] == "s":
                continue
            if line[0] == "v" or line[0].isdigit() or line[0] == "-":
                parts = line[1:].split() if line[0] == "v" else line.split()
                for p in parts:
                    if p == "0":
                        continue
                    lits.append(int(p))
    return lits


def model_to_squares(t: int, lits: list[int]) -> list[list[list[int]]]:
    truth = {abs(x): x > 0 for x in lits}
    squares: list[list[list[int]]] = []
    for k in range(t):
        L = [[-1] * N for _ in range(N)]
        for r in range(HALF):
            for c in range(N):
                found = None
                for s in range(N):
                    v = var_id(t, k, r, c, s)
                    if truth.get(v, False):
                        if found is not None:
                            raise ValueError(f"two symbols at ({k},{r},{c})")
                        found = s
                if found is None:
                    raise ValueError(f"no symbol at ({k},{r},{c})")
                L[r][c] = found
                L[r + HALF][c] = (found + HALF) % N
        squares.append(L)
    return squares


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("t", type=int, help="number of MOLS")
    ap.add_argument("-o", "--output", default="-")
    ap.add_argument("--no-normalize", action="store_true")
    args = ap.parse_args()
    cnf = encode(args.t, normalize=not args.no_normalize)
    comments = [
        f"t={args.t} MOLS of order 12 with involution L(r+6,c)=L(r,c)+6",
        f"primary vars 1..{cnf.n_orig} = X[k][r][c][s], k<t, r<6, c<12, s<12",
        f"normalize={not args.no_normalize}",
    ]
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
