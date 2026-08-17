#!/usr/bin/env python3
"""Apply the same safe symmetry breaking the SAT encoder uses."""

from __future__ import annotations

import json
import sys


N = 12
HALF = 6


def normalize(squares: list[list[list[int]]]) -> list[list[list[int]]]:
    squares = [ [row[:] for row in L] for L in squares ]
    L0 = squares[0]
    # Column perm so L0[0] is the identity.
    # L0[0][sigma[c]] = c  => sigma[c] = index of c in L0[0].
    sigma = [L0[0].index(c) for c in range(N)]
    squares = [
        [[L[r][sigma[c]] for c in range(N)] for r in range(N)]
        for L in squares
    ]
    # Permute free rows 1..5 so pair-index of L0[r][0] is r.
    L0 = squares[0]
    # remaining rows
    used = {0}
    row_of_pair = {}
    for r in range(1, HALF):
        p = L0[r][0] % HALF
        row_of_pair[p] = r
    # new row order: 0, then the row currently holding pair 1, pair 2, ...
    row_perm = [0]
    for p in range(1, HALF):
        row_perm.append(row_of_pair[p])
    # extend by +6
    row_perm.extend([r + HALF for r in row_perm])
    squares = [
        [L[row_perm[r]] for r in range(N)]
        for L in squares
    ]
    # Send the pair of L_k[0][0] to {0,6} and unflip so L_k[0][0]=0.
    for k in range(1, len(squares)):
        s0 = squares[k][0][0]
        p = s0 % HALF
        flip0 = s0 >= HALF

        def phi(s: int, p: int = p, flip0: bool = flip0) -> int:
            q = s % HALF
            bit = s >= HALF
            if q == p:
                q2 = 0
                bit2 = bit ^ flip0
            elif q == 0:
                q2 = p
                bit2 = bit
            else:
                q2 = q
                bit2 = bit
            return q2 + (HALF if bit2 else 0)

        squares[k] = [[phi(s) for s in row] for row in squares[k]]
    return squares


def main() -> None:
    with open(sys.argv[1]) as f:
        payload = json.load(f)
    squares = payload["squares"] if isinstance(payload, dict) else payload
    out = normalize(squares)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
