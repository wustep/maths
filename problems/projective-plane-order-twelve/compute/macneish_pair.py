#!/usr/bin/env python3
"""MacNeish 2-MOLS of order 12 with the involutory-elation symmetry.

Product of the unique (up to iso) 2-MOLS of order 3 with two MOLS of
order 4 coming from AG(2,4).  The characteristic-2 translation on the
F_4 factor is an involution; after row and symbol relabelling it becomes
L[r+6][c] = (L[r][c] + 6) % 12.

This is a concrete SAT witness that the t=2 instance is faithful, and a
lower bound: the involution constraint does not already kill 2 MOLS.
"""

from __future__ import annotations

import json
import sys

from verify_involution_mols import verify


# F_4 = {0,1,2,3} with XOR addition and multiplication
# 0=00, 1=10, 2=01, 3=11;  2 is a primitive element, 2*2=3, 2*3=1, 3*3=2.
F4_ADD = [
    [0, 1, 2, 3],
    [1, 0, 3, 2],
    [2, 3, 0, 1],
    [3, 2, 1, 0],
]
F4_MUL = [
    [0, 0, 0, 0],
    [0, 1, 2, 3],
    [0, 2, 3, 1],
    [0, 3, 1, 2],
]


def f3_mols() -> list[list[list[int]]]:
    """Two MOLS of order 3: L_m[i][j] = i + m*j  (m=1,2) over F_3."""
    out = []
    for m in (1, 2):
        L = [[(i + m * j) % 3 for j in range(3)] for i in range(3)]
        out.append(L)
    return out


def f4_mols() -> list[list[list[int]]]:
    """Two MOLS of order 4: L_m[k][l] = k + m*l  (m=1,2) over F_4."""
    out = []
    for m in (1, 2):
        L = [
            [F4_ADD[k][F4_MUL[m][l]] for l in range(4)]
            for k in range(4)
        ]
        out.append(L)
    return out


def product(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """Kronecker-style product: P[(i,k)][(j,l)] = (A[i][j], B[k][l])."""
    n, m = len(A), len(B)
    P = [[0] * (n * m) for _ in range(n * m)]
    for i in range(n):
        for k in range(m):
            for j in range(n):
                for l in range(m):
                    # flatten (i,k) as 4*i + k
                    P[4 * i + k][4 * j + l] = A[i][j] * 4 + B[k][l]
    return P


def relabel_involution(squares: list[list[list[int]]]) -> list[list[list[int]]]:
    """Send the F_4 translation k |-> k XOR 1 to the standard +6 action.

    Old row/col indices are 4*i+k.  Translation acts as k |-> k XOR 1
    on rows only (points (x,y) |-> (τx, y)).  Old pairs:
        {4i+0, 4i+1} and {4i+2, 4i+3}.
    New row labels: pair p=0..5 goes to {p, p+6}, in the order
        (0,1)->(0,6), (2,3)->(1,7), (4,5)->(2,8),
        (6,7)->(3,9), (8,9)->(4,10), (10,11)->(5,11).
    Columns are not moved.  Symbols are remapped by the same pairing
    so that the induced symbol involution (a,b) |-> (a, b XOR 1)
    becomes s |-> s+6.
    """
    row_of = [0] * 12
    pairs = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)]
    for p, (a, b) in enumerate(pairs):
        row_of[a] = p
        row_of[b] = p + 6

    # Symbol involution on the un-relabelled product: (a,b) |-> (a, b XOR 1)
    # i.e. s = 4*a + b  |->  4*a + (b XOR 1), the same pairing as rows.
    # So the same map row_of sends the symbol involution to +6.
    sym_of = row_of

    out = []
    for L in squares:
        Lp = [[0] * 12 for _ in range(12)]
        for r in range(12):
            for c in range(12):
                Lp[row_of[r]][c] = sym_of[L[r][c]]
        out.append(Lp)
    return out


def normalize(squares: list[list[list[int]]]) -> list[list[list[int]]]:
    """Permute columns and independently relabel symbols so that
    every first row is the identity and square 0's first column is
    the identity, preserving L[r+6][c] = L[r][c]+6.
    """
    L0 = squares[0]
    # Permute columns so that L0[0] becomes the identity.
    col_perm = [L0[0].index(s) for s in range(12)]
    squares = [
        [[L[r][col_perm[c]] for c in range(12)] for r in range(12)]
        for L in squares
    ]
    # Symbol relabel each square so that first row is identity.
    # First row of L after col perm is some permutation π; send π(c) |-> c.
    # The involution sends row 0 to row 6 with symbols +6, so the same
    # map automatically sends row 6 to identity+6 iff π(c)+6 maps to c+6,
    # i.e. the relabelling commutes with +6.  First-row identity plus
    # the involution forces row 6 = identity+6, so the relabelling of
    # s and of s+6 is determined consistently: φ(π(c))=c and
    # φ(π(c)+6)=c+6.
    out = []
    for L in squares:
        phi = [-1] * 12
        for c in range(12):
            phi[L[0][c]] = c
            phi[(L[0][c] + 6) % 12] = (c + 6) % 12
        if any(x < 0 for x in phi):
            raise RuntimeError("symbol relabel failed to commute with +6")
        out.append([[phi[L[r][c]] for c in range(12)] for r in range(12)])
    # Now L0[0] is identity.  If L0[:,0] is not identity, compose a
    # row permutation that commutes with +6 (i.e. a permutation of
    # {0..5} copied to {6..11}) together with a matching symbol perm.
    # For the SAT sanity check we only need the involution and
    # orthogonality; normalization is optional.  Leave as is if the
    # first column is not yet identity.
    return out


def build() -> list[list[list[int]]]:
    A1, A2 = f3_mols()
    B1, B2 = f4_mols()
    P1 = product(A1, B1)
    P2 = product(A2, B2)
    return relabel_involution([P1, P2])


def main() -> None:
    squares = build()
    report = verify(squares)
    if not report["ok"]:
        print(json.dumps(report, indent=2))
        sys.exit(1)
    # also try a normalized form
    norm = normalize(squares)
    report_n = verify(norm, normalized=False)
    inv_ok = all(item["ok"] for item in report_n["involution"])
    lat_ok = all(item["ok"] for item in report_n["latin"])
    ort_ok = all(item["ok"] for item in report_n["orthogonal"])
    out = {
        "raw_ok": report["ok"],
        "normalized_latin": lat_ok,
        "normalized_orthogonal": ort_ok,
        "normalized_involution": inv_ok,
        "normalized_first_rows": [norm[k][0] for k in range(2)],
        "squares": norm,
    }
    path = sys.argv[1] if len(sys.argv) > 1 else "certs/macneish_involution_2mols.json"
    with open(path, "w") as f:
        json.dump(out, f)
        f.write("\n")
    print(
        f"wrote {path}: latin={lat_ok} orthogonal={ort_ok} involution={inv_ok}"
    )
    sys.exit(0 if (lat_ok and ort_ok and inv_ok) else 1)


if __name__ == "__main__":
    main()
