#!/usr/bin/env python3
"""Two further involution-Latin squares, pairwise orthogonal and orthogonal to L0.

This is t=3 with square 0 hard-wired.  Primary vars are two free halves.
"""

from __future__ import annotations

import argparse
import json
import sys

from encode_involution_mols import Cnf, HALF, N


def var_id(k: int, r: int, c: int, s: int) -> int:
    """k in {0,1} indexes the two new squares."""
    return 1 + (((k * HALF + r) * N + c) * N + s)


def n_primary() -> int:
    return 2 * HALF * N * N


def encode_two_mates(L0: list[list[int]], normalize: bool = True) -> Cnf:
    cnf = Cnf()
    cnf._next = n_primary() + 1
    cnf.n_orig = n_primary()

    def X(k, r, c, s):
        return var_id(k, r, c, s)

    for k in range(2):
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

    def amo_orbits_var_var():
        for s in range(HALF):
            for sp in range(N):
                ol = []
                for r in range(HALF):
                    for c in range(N):
                        a = cnf.fresh()
                        b = cnf.fresh()
                        o = cnf.fresh()
                        cnf.add([-a, X(0, r, c, s)])
                        cnf.add([-a, X(1, r, c, sp)])
                        cnf.add([-X(0, r, c, s), -X(1, r, c, sp), a])
                        cnf.add([-b, X(0, r, c, s + HALF)])
                        cnf.add([-b, X(1, r, c, (sp + HALF) % N)])
                        cnf.add(
                            [
                                -X(0, r, c, s + HALF),
                                -X(1, r, c, (sp + HALF) % N),
                                b,
                            ]
                        )
                        cnf.add([-o, a, b])
                        cnf.add([-a, o])
                        cnf.add([-b, o])
                        ol.append(o)
                cnf.amo_sequential(ol)

    def amo_orbits_fixed(k: int, A: list[list[int]]):
        for s in range(HALF):
            for a in range(N):
                ol = []
                for r in range(HALF):
                    for c in range(N):
                        a_rc = A[r][c]
                        if a_rc == a:
                            ol.append(X(k, r, c, s))
                        if a_rc == (a + HALF) % N:
                            ol.append(X(k, r, c, s + HALF))
                if ol:
                    cnf.amo_sequential(ol)

    amo_orbits_fixed(0, L0)
    amo_orbits_fixed(1, L0)
    amo_orbits_var_var()

    if normalize:
        # symbol relabel of each new square: L_k[0][0] = 0
        cnf.add([X(0, 0, 0, 0)])
        cnf.add([X(1, 0, 0, 0)])
        # order the two new squares by L[0][1]
        for a in range(N):
            for b in range(a):
                cnf.add([-X(0, 0, 1, a), -X(1, 0, 1, b)])
    return cnf


def model_to_two(lits: list[int]) -> list[list[list[int]]]:
    truth = {abs(x): x > 0 for x in lits}
    squares = []
    for k in range(2):
        L = [[-1] * N for _ in range(N)]
        for r in range(HALF):
            for c in range(N):
                found = None
                for s in range(N):
                    if truth.get(var_id(k, r, c, s), False):
                        found = s
                        break
                if found is None:
                    raise ValueError(f"no symbol {k},{r},{c}")
                L[r][c] = found
                L[r + HALF][c] = (found + HALF) % N
        squares.append(L)
    return squares


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("l0_json")
    ap.add_argument("-o", "--output", default="-")
    ap.add_argument("--index", type=int, default=0)
    args = ap.parse_args()
    with open(args.l0_json) as f:
        payload = json.load(f)
    if "squares" in payload and payload["squares"] and isinstance(payload["squares"][0][0][0], int):
        # either a family or an enum of families
        first = payload["squares"][0]
        if isinstance(first[0][0], int) and not isinstance(first[0][0], list):
            L0 = payload["squares"][args.index] if isinstance(payload["squares"][args.index][0][0], int) else payload["squares"][args.index][0]
        else:
            L0 = payload["squares"][args.index][0]
    else:
        L0 = payload[args.index][0] if isinstance(payload[0][0][0], list) else payload[0]
    # simpler:
    data = payload["squares"] if isinstance(payload, dict) else payload
    item = data[args.index]
    L0 = item[0] if isinstance(item[0][0], list) else item
    cnf = encode_two_mates(L0)
    comments = ["two involution mates of a fixed L0, pairwise orthogonal"]
    if args.output == "-":
        cnf.dump(sys.stdout, comments)
    else:
        with open(args.output, "w") as f:
            cnf.dump(f, comments)
        print(f"wrote {args.output}: {cnf._next-1} vars, {len(cnf.clauses)} clauses", file=sys.stderr)


if __name__ == "__main__":
    main()
