#!/usr/bin/env python3
"""Backtrack all involution-mates of a given involution Latin square.

Fills the free half M[r][c], r<6, c<12.  Much faster than blocking SAT
for complete mate lists of one square.
"""

from __future__ import annotations

import argparse
import json
import sys

from verify_involution_mols import has_involution, is_latin, is_orthogonal


N = 12
HALF = 6


def orbit_id(s: int, a: int) -> int:
    """Orbit of (s,a) under (s,a) |-> (s+6,a+6). Representative s in 0..5."""
    if s >= HALF:
        return (s - HALF) * N + ((a - HALF) % N)
    return s * N + a


def reconstruct(half: list[list[int]]) -> list[list[int]]:
    M = [row[:] for row in half]
    for r in range(HALF):
        M.append([(half[r][c] + HALF) % N for c in range(N)])
    return M


def enumerate_mates(L: list[list[int]], limit: int = 0) -> list[list[list[int]]]:
    assert is_latin(L)[0] and has_involution(L)[0]
    half = [[-1] * N for _ in range(HALF)]
    row_used = [0] * HALF
    col_pair = [0] * N  # bit u if pair {u,u+6} already used
    orbit = 0  # 72-bit, via python int
    mates: list[list[list[int]]] = []
    cells = [(r, c) for r in range(HALF) for c in range(N)]

    def rec(k: int) -> None:
        if limit and len(mates) >= limit:
            return
        if k == len(cells):
            mates.append(reconstruct(half))
            return
        r, c = cells[k]
        a = L[r][c]
        ru = row_used[r]
        cp = col_pair[c]
        # try symbols 0..11
        # skip those used in the row or whose pair is used in the column
        for s in range(N):
            if ru & (1 << s):
                continue
            u = s % HALF
            if cp & (1 << u):
                continue
            oid = orbit_id(s, a)
            if orbit & (1 << oid):
                continue
            half[r][c] = s
            row_used[r] = ru | (1 << s)
            col_pair[c] = cp | (1 << u)
            # set orbit
            nonlocal_orbit = oid
            # use outer orbit via closure
            rec.__defaults__  # keep linter quiet
            rec_go(k, r, c, s, u, ru, cp, oid)

    # rewrite with explicit orbit in enclosing scope
    def rec_go(k, r, c, s, u, ru, cp, oid):
        nonlocal orbit
        old = orbit
        orbit |= 1 << oid
        rec(k + 1)
        orbit = old
        row_used[r] = ru
        col_pair[c] = cp
        half[r][c] = -1

    # actually just call a clean recursive function
    mates.clear()

    def search(k: int) -> None:
        nonlocal orbit
        if limit and len(mates) >= limit:
            return
        if k == 72:
            mates.append(reconstruct(half))
            return
        r, c = cells[k]
        a = L[r][c]
        ru = row_used[r]
        cp = col_pair[c]
        for s in range(N):
            if ru & (1 << s):
                continue
            u = s % HALF
            if cp & (1 << u):
                continue
            oid = orbit_id(s, a)
            if orbit & (1 << oid):
                continue
            half[r][c] = s
            row_used[r] |= 1 << s
            col_pair[c] |= 1 << u
            orbit |= 1 << oid
            search(k + 1)
            orbit ^= 1 << oid
            col_pair[c] = cp
            row_used[r] = ru
            half[r][c] = -1

    search(0)
    return mates


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("family_json")
    ap.add_argument("--index", type=int, default=0, help="which square to mate")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    with open(args.family_json) as f:
        payload = json.load(f)
    family = payload["squares"] if isinstance(payload, dict) else payload
    L = family[args.index]
    mates = enumerate_mates(L, limit=args.limit)
    # verify a sample
    bad = 0
    for M in mates[:5]:
        if not (is_latin(M)[0] and has_involution(M)[0] and is_orthogonal(L, M)[0]):
            bad += 1
    print(f"mates={len(mates)} sample_bad={bad}")
    if args.output:
        with open(args.output, "w") as f:
            json.dump({"n_mates": len(mates), "mates": mates}, f)
            f.write("\n")


if __name__ == "__main__":
    main()
