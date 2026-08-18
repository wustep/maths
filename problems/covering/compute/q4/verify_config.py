#!/usr/bin/env python3
"""Independent verifier / residue reporter for a column configuration.

Usage: verify_config.py FILE [FILE...]

Each FILE lists integer columns in 1..1023 (whitespace separated, '#'
comments allowed).  For each file this recomputes, from scratch:
  - column count, distinctness, F_2-rank;
  - the exact set of syndromes not expressible as a sum of at most two
    columns (the holes), by full pair enumeration.
Zero holes with 49 distinct rank-10 columns would certify l_2(10,2)<=49.
Nonzero holes are a search residue, not a bound.
"""

import sys


def rank2(cols):
    basis = {}  # pivot bit -> row
    r = 0
    for c in cols:
        v = c
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                r += 1
                break
    return r


def main(argv):
    status = 0
    for path in argv[1:]:
        cols = []
        with open(path) as f:
            for line in f:
                if line.lstrip().startswith("#"):
                    continue
                cols.extend(int(t, 0) for t in line.split())
        n = len(cols)
        distinct = len(set(cols)) == n
        in_range = all(1 <= c <= 1023 for c in cols)
        r = rank2(sorted(cols, reverse=True))
        covered = bytearray(1024)
        covered[0] = 1
        for i, a in enumerate(cols):
            covered[a] = 1
            for b in cols[:i]:
                covered[a ^ b] = 1
        holes = [v for v in range(1024) if not covered[v]]
        verdict = ("COVERING" if not holes and n == 49 and distinct
                   and in_range and r == 10 else "residue")
        print("%s: n=%d distinct=%s in_range=%s rank=%d holes=%d %s -> %s" %
              (path, n, distinct, in_range, r, len(holes),
               holes if len(holes) <= 24 else holes[:24] + ["..."], verdict))
        if verdict != "COVERING":
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
