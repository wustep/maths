#!/usr/bin/env python3
"""Isotopy of involution-compatible MOLS that preserves L[r+6][c]=L[r][c]+6.

Allowed moves:
  - permute free rows {0..5} and copy to {6..11}
  - arbitrary column permutation
  - independently, for each square, a symbol permutation commuting with +6
    (permute the 6 pairs, and flip within pairs)
  - permute the squares among themselves
"""

from __future__ import annotations

import itertools
import json
import sys


N = 12
HALF = 6


def apply_row_col(L, row_perm, col_perm):
    """row_perm is a perm of 0..5; col_perm of 0..11."""
    full_row = list(row_perm) + [r + HALF for r in row_perm]
    return [[L[full_row[r]][col_perm[c]] for c in range(N)] for r in range(N)]


def symbol_perms():
    """All 6! * 2^6 = 46080 perms of Z_12 commuting with +6."""
    pairs = list(range(HALF))
    for p in itertools.permutations(pairs):
        for flips in range(1 << HALF):
            phi = [0] * N
            for i, dest in enumerate(p):
                if flips & (1 << i):
                    phi[i] = dest + HALF
                    phi[i + HALF] = dest
                else:
                    phi[i] = dest
                    phi[i + HALF] = dest + HALF
            yield phi


def apply_symbol(L, phi):
    return [[phi[L[r][c]] for c in range(N)] for r in range(N)]


def invariants(squares):
    """Cheap isotopy invariants (preserving the involution type)."""
    out = []
    for L in squares:
        # symbol-pair pattern of first rows after sorting columns by L[0]
        # better: the 2x2 intercalate counts, or the identity of the
        # associated quasigroup up to the allowed autotopism.
        # Use the multiset of 2x2 determinants of free-half symbols mod 2
        # and the column-transversal flip pattern.
        flips = []
        for c in range(N):
            top = [L[r][c] for r in range(HALF)]
            flips.append(tuple(sorted(x % HALF for x in top)))
        out.append(tuple(sorted(flips)))
    return tuple(sorted(out))


def same_invariants(A, B):
    return invariants(A) == invariants(B)


def main() -> None:
    paths = sys.argv[1:]
    fams = []
    for p in paths:
        with open(p) as f:
            payload = json.load(f)
        fams.append(payload["squares"] if isinstance(payload, dict) else payload)
    for i, A in enumerate(fams):
        print(f"family {i} t={len(A)} inv={invariants(A)}")
    if len(fams) == 2:
        print("same cheap invariants", same_invariants(fams[0], fams[1]))


if __name__ == "__main__":
    main()
