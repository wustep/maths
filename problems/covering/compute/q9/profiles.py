#!/usr/bin/env python3
"""Quotient-block profiles of a radius-2 column set at r=10.

Every S subset F_2^r decomposes, relative to each 2-dimensional quotient
q : F_2^r -> F_2^2, into four blocks (A;B,C,D), where A = S cap ker q and
B,C,D are the fibres over the three nonzero labels.  Radius-2 covering is then
equivalent to four conditions inside F_2^{r-2} = ker q:

    (00)  {0} u A u (A+A) u (B+B) u (C+C) u (D+D) = ker q
    (01)  B u (A+B) u (C+D)                       = ker q
    (10)  C u (A+C) u (B+D)                       = ker q
    (11)  D u (A+D) u (B+C)                       = ker q

so the profile (|A|;|B|,|C|,|D|) is the structural fingerprint of a covering
with respect to the labelled-lift family.  This script tabulates the profile
over all 174251 two-dimensional quotients of F_2^10, and reports whether any
block A is by itself a radius-2 covering of its own 8-dimensional kernel
(which is what a "lift of the r=8 record" would look like).

Usage: profiles.py <matrix-or-cols-file> [...]
"""
import sys
from collections import Counter

R = 10
RM2 = R - 2


def load(path):
    lines = []
    for ln in open(path):
        ln = ln.split("#")[0].strip()
        if ln:
            lines.append(ln)
    if len(lines) == R and all(set(ln) <= {"0", "1", " "} for ln in lines):
        rows = [ln.replace(" ", "") for ln in lines]
        n = len(rows[0])
        return [sum(1 << row for row in range(R) if rows[row][i] == "1")
                for i in range(n)]
    return [int(t, 0) for t in " ".join(lines).split()]


def parity_mask(f, cols):
    m = 0
    for i, c in enumerate(cols):
        if bin(f & c).count("1") & 1:
            m |= 1 << i
    return m


def analyse(path):
    cols = load(path)
    n = len(cols)
    full = (1 << n) - 1
    masks = [parity_mask(f, cols) if f else 0 for f in range(1024)]
    prof = Counter()
    nq = 0
    big = []                       # quotients with a big kernel block
    for f in range(1, 1024):
        mf = masks[f]
        for g in range(f + 1, 1024):
            h = f ^ g
            if h < g:              # canonical rep: f < g < f^g
                continue
            mg = masks[g]
            b3 = bin(mf & mg).count("1")
            b2 = bin(mf & ~mg & full).count("1")
            b1 = bin(~mf & mg & full).count("1")
            a = n - b1 - b2 - b3
            nq += 1
            prof[(a,) + tuple(sorted((b1, b2, b3)))] += 1
            if a >= 25:
                big.append((a, f, g))
    print(f"== {path}   n={n}   quotients={nq}")
    print("   most common profiles (|A|; |B|,|C|,|D|):")
    for p, k in prof.most_common(6):
        print(f"      {p[0]:3d}; {p[1]:2d},{p[2]:2d},{p[3]:2d}   x{k}")
    print(f"   |A| range {min(p[0] for p in prof)}..{max(p[0] for p in prof)}"
          f"   distinct profiles {len(prof)}")
    bal = sum(k for p, k in prof.items() if p[1] == p[2] == p[3])
    print(f"   quotients with |B|=|C|=|D|: {bal}")
    # near-balanced small blocks: max-min <= 1
    nb = sum(k for p, k in prof.items() if p[3] - p[1] <= 1)
    print(f"   quotients with |B|,|C|,|D| within 1 of each other: {nb}")
    hits, sizes = 0, []
    for a, f, g in big:
        ker = [c for c in cols
               if bin(f & c).count("1") % 2 == 0 and bin(g & c).count("1") % 2 == 0]
        seen = {0} | set(ker)
        for x in range(len(ker)):
            for y in range(x + 1, len(ker)):
                seen.add(ker[x] ^ ker[y])
        if len(seen) == (1 << RM2):
            hits += 1
            sizes.append(a)
    print(f"   quotients with |A|>=25: {len(big)}; of those A covers its own F_2^8:"
          f" {hits}" + (f"  (|A| = {sorted(set(sizes))})" if sizes else ""))
    sys.stdout.flush()
    return prof


if __name__ == "__main__":
    for p in sys.argv[1:]:
        analyse(p)
