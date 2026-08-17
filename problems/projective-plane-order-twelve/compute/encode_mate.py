#!/usr/bin/env python3
"""Encode one more involution-Latin square orthogonal to a given family.

Primary variables X[r][c][s] for r<6, same as encode_involution_mols
with t=1.  Orthogonality against each given square is a family of
at-most-one constraints on orbits, with the given symbols hard-wired.
"""

from __future__ import annotations

import argparse
import json
import sys

from encode_involution_mols import Cnf, HALF, N


def var_id(r: int, c: int, s: int) -> int:
    return 1 + (r * N + c) * N + s


def encode_mate(family: list[list[list[int]]]) -> Cnf:
    cnf = Cnf()
    cnf._next = HALF * N * N + 1
    cnf.n_orig = HALF * N * N

    def X(r: int, c: int, s: int) -> int:
        return var_id(r, c, s)

    for r in range(HALF):
        for c in range(N):
            cnf.eo_pairwise([X(r, c, s) for s in range(N)])
    for r in range(HALF):
        for s in range(N):
            cnf.eo_pairwise([X(r, c, s) for c in range(N)])
    for c in range(N):
        for u in range(HALF):
            lits = []
            for r in range(HALF):
                lits.append(X(r, c, u))
                lits.append(X(r, c, u + HALF))
            cnf.eo_sequential(lits)

    # Orthogonal to each given square A: free cells hit distinct
    # orbits of (new, A) pairs under +6.
    for A in family:
        for s in range(HALF):  # representative first-component
            for a in range(N):  # A-symbol
                orbit_lits = []
                for r in range(HALF):
                    for c in range(N):
                        a_rc = A[r][c]
                        # free cell (r,c) realises orbit {(s,a),(s+6,a+6)} iff
                        #   (new=s and A=a) or (new=s+6 and A=a+6)
                        if a_rc == a:
                            orbit_lits.append(X(r, c, s))
                        if a_rc == (a + HALF) % N:
                            orbit_lits.append(X(r, c, s + HALF))
                if orbit_lits:
                    cnf.amo_sequential(orbit_lits)
    return cnf


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("family_json")
    ap.add_argument("-o", "--output", default="-")
    args = ap.parse_args()
    with open(args.family_json) as f:
        payload = json.load(f)
    family = payload["squares"] if isinstance(payload, dict) else payload
    cnf = encode_mate(family)
    comments = [
        f"one involution-Latin mate of a {len(family)}-MOLS family of order 12",
        f"primary vars 1..{cnf.n_orig}",
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
