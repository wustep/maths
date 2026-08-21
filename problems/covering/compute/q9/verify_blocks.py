#!/usr/bin/env python3
"""Check the block reduction that compute/q9/block_solve.c is built on.

Claim.  Fix a 2-dimensional quotient q : F_2^r -> F_2^2 with kernel V, and coset
representatives t00=0, t01, t10, t11 = t01+t10.  Write a column set S as
A = (S cap V), B = (S cap (V+t01)) + t01, and likewise C, D, all inside V.
Then S has covering radius <= 2 in F_2^r if and only if, inside V,

  (00)  {0} u A u D(A) u D(B) u D(C) u D(D) = V     with D(X) = {x+x' : x != x'}
  (01)  (A u {0}) + B  u  C + D = V
  (10)  (A u {0}) + C  u  B + D = V
  (11)  (A u {0}) + D  u  B + C = V

This script tests both directions on real data: the certified 50-set (a
covering, all four conditions must hold for every quotient tried) and the
q4 7-hole residues (not a covering, so some condition must fail), and it
cross-checks the count of uncovered syndromes computed the two ways.

Usage: verify_blocks.py <file> [ntrials]
"""
import random
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from profiles import load                                    # noqa: E402

R = 10


def par(a, b):
    return bin(a & b).count("1") & 1


def direct_holes(cols):
    hit = bytearray(1 << R)
    hit[0] = 1
    for c in cols:
        hit[c] = 1
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            hit[cols[i] ^ cols[j]] = 1
    return {s for s in range(1 << R) if not hit[s]}


def block_holes(cols, f, g):
    V = [x for x in range(1 << R) if not par(f, x) and not par(g, x)]
    t01 = next(x for x in range(1, 1 << R) if not par(f, x) and par(g, x))
    t10 = next(x for x in range(1, 1 << R) if par(f, x) and not par(g, x))
    trep = {0: 0, 1: t01, 2: t10, 3: t01 ^ t10}
    blocks = {0: [], 1: [], 2: [], 3: []}
    for c in cols:
        lab = par(f, c) * 2 + par(g, c)
        idx = {0: 0, 1: 1, 2: 2, 3: 3}[lab]
        blocks[idx].append(c ^ trep[idx])
    A, B, C, D = (blocks[i] for i in range(4))
    Ap = [0] + A

    def delta(X):
        return {X[i] ^ X[j] for i in range(len(X)) for j in range(i + 1, len(X))}

    def msum(X, Y):
        return {x ^ y for x in X for y in Y}

    cov = {
        0: {0} | set(A) | delta(A) | delta(B) | delta(C) | delta(D),
        1: msum(Ap, B) | msum(C, D),
        2: msum(Ap, C) | msum(B, D),
        3: msum(Ap, D) | msum(B, C),
    }
    holes = set()
    for lab in range(4):
        for v in V:
            if v not in cov[lab]:
                holes.add(v ^ trep[lab])
    return holes, tuple(len(blocks[i]) for i in range(4))


def main():
    path = sys.argv[1]
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    cols = load(path)
    want = direct_holes(cols)
    rng = random.Random(20260821)
    quots = []
    while len(quots) < trials:
        f, g = rng.randrange(1, 1 << R), rng.randrange(1, 1 << R)
        if f == g:
            continue
        a, b, c = sorted((f, g, f ^ g))
        if (a, b) not in quots:
            quots.append((a, b))
    bad = 0
    for f, g in quots:
        got, prof = block_holes(cols, f, g)
        if got != want:
            bad += 1
            print(f"  MISMATCH f={f} g={g} profile={prof} "
                  f"direct={len(want)} blockwise={len(got)}")
    print(f"{path}: n={len(cols)} direct holes={len(want)}; "
          f"blockwise agrees on {trials - bad}/{trials} quotients")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
