#!/usr/bin/env python3
"""Classify the colour sets that block r=9, n=38 in the q11 family.

Reads the FULLSET lines emitted by sa_graph.c when a cost-0 configuration at
k=8 has no 1-saturating complement, and reports how many of the recorded
8-colour sets are affine hyperplanes of F_2^4 -- for those, A = V\\(B u {0}) is
a hyperplane minus 0, so A+A stays inside the hyperplane and fibre 0 can never
be covered.
"""
import sys
from collections import Counter


def is_affine_hyperplane(mask, F=4):
    pts = [v for v in range(1, 1 << F) if mask >> v & 1]
    if len(pts) != 1 << (F - 1):
        return False
    d = {p ^ pts[0] for p in pts}
    return all((a ^ b) in d for a in d for b in d)


masks = [int(line.split()[1], 16) for line in open(sys.argv[1]) if line.startswith("FULLSET")]
c = Counter(is_affine_hyperplane(m) for m in masks)
print(f"{len(masks)} recorded 8-colour sets, {len(set(masks))} distinct")
print(f"affine hyperplanes: {c[True]}   other: {c[False]}")
