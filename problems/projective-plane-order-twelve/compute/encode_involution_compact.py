#!/usr/bin/env python3
"""t-MOLS + involution with pairwise orthogonality (no orbit aux vars).

Same primary variables and Latin/involution/normalization constraints
as encode_involution_mols.py.  Orthogonality is encoded as: every two
free cells lie in different +6-orbits of symbol pairs.
"""

from __future__ import annotations

import argparse
import sys

from encode_involution_mols import Cnf, HALF, N, n_primary, var_id


def encode(t: int, normalize: bool = True) -> Cnf:
    cnf = Cnf()
    cnf._next = n_primary(t) + 1
    cnf.n_orig = n_primary(t)

    def X(k, r, c, s):
        return var_id(t, k, r, c, s)

    for k in range(t):
        for r in range(HALF):
            for c in range(N):
                cnf.eo_pairwise([X(k, r, c, s) for s in range(N)])
        for r in range(HALF):
            for s in range(N):
                cnf.eo_pairwise([X(k, r, c, s) for c in range(N)])
        for c in range(N):
            for u in range(HALF):
                lits = []
                for r in range(HALF):
                    lits.append(X(k, r, c, u))
                    lits.append(X(k, r, c, u + HALF))
                cnf.eo_sequential(lits)

    cells = [(r, c) for r in range(HALF) for c in range(N)]
    for k in range(t):
        for kp in range(k + 1, t):
            for i, (r1, c1) in enumerate(cells):
                for r2, c2 in cells[i + 1 :]:
                    for s in range(N):
                        for sp in range(N):
                            # forbid same pair
                            cnf.add(
                                [
                                    -X(k, r1, c1, s),
                                    -X(kp, r1, c1, sp),
                                    -X(k, r2, c2, s),
                                    -X(kp, r2, c2, sp),
                                ]
                            )
                            # forbid complementary pair
                            cnf.add(
                                [
                                    -X(k, r1, c1, s),
                                    -X(kp, r1, c1, sp),
                                    -X(k, r2, c2, (s + HALF) % N),
                                    -X(kp, r2, c2, (sp + HALF) % N),
                                ]
                            )

    if normalize:
        for c in range(N):
            cnf.add([X(0, 0, c, c)])
        for r in range(1, HALF):
            allowed = []
            for u in range(r, HALF):
                allowed.append(X(0, r, 0, u))
                allowed.append(X(0, r, 0, u + HALF))
            cnf.add(allowed)
        for k in range(1, t):
            cnf.add([X(k, 0, 0, 0)])
        if t >= 3:
            for a in range(N):
                for b in range(a):
                    cnf.add([-X(1, 0, 1, a), -X(2, 0, 1, b)])
    return cnf


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("t", type=int)
    ap.add_argument("-o", "--output", default="-")
    args = ap.parse_args()
    cnf = encode(args.t)
    comments = [f"compact pairwise t={args.t} involution MOLS"]
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
