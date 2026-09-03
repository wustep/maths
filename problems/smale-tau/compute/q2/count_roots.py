#!/usr/bin/env python3
"""Exact distinct-integer-root counts for the candidate polynomials written by
poly_search (lines "CAND depth [coeffs] program" and "WIDE depth [f] [g]").

For each depth d prints the largest Z among candidates first seen at depth <= d
with one witness program, and the per-depth maxima.  Exact arithmetic only:
integer roots are found from the divisors of the trailing coefficient of the
primitive part after removing the power of x (rational root theorem), which
is always feasible here because sympy factors the (small) trailing
coefficients; a polynomial whose trailing coefficient resists factoring is
reported instead of guessed.
"""
import sys, json
from sympy import factorint, divisors
from functools import reduce
from math import gcd

def integer_roots(coeffs):
    """coeffs low to high; returns the set of distinct integer roots"""
    c = list(coeffs)
    while c and c[-1] == 0: c.pop()
    if not c: raise ValueError("zero polynomial")
    roots = set()
    m = 0
    while c[m] == 0: m += 1
    if m > 0: roots.add(0)
    c = c[m:]
    g = reduce(gcd, c); c = [x // g for x in c]
    if len(c) == 1: return roots
    a0 = abs(c[0])
    # any integer root divides a0
    if a0.bit_length() > 200:
        raise ValueError("trailing coefficient too large to factor")
    for d in divisors(a0):
        for r in (d, -d):
            # Horner
            v = 0
            for k in reversed(c): v = v * r + k
            if v == 0: roots.add(r)
    return roots

def main():
    best_at = {}       # depth -> (Z, coeffs, program)
    seen = {}
    unresolved = []
    for line in sys.stdin:
        parts = line.split()
        if not parts: continue
        if parts[0] == "CAND":
            depth = int(parts[1]); coeffs = json.loads(parts[2]); prog = parts[3]
            key = tuple(coeffs)
            if key in seen and seen[key][0] <= depth: continue
            try:
                z = len(integer_roots(coeffs))
            except ValueError as e:
                unresolved.append((depth, coeffs, str(e))); continue
            seen[key] = (depth, z)
            if depth not in best_at or z > best_at[depth][0]:
                best_at[depth] = (z, coeffs, prog)
        elif parts[0] == "WIDE":
            depth = int(parts[1]); f = json.loads(parts[2]); g = json.loads(parts[3])
            prod = [0] * (len(f) + len(g) - 1)
            for i, a in enumerate(f):
                for j, b in enumerate(g): prod[i + j] += a * b
            try:
                z = len(integer_roots(prod))
            except ValueError as e:
                unresolved.append((depth, prod, str(e))); continue
            if depth not in best_at or z > best_at[depth][0]:
                best_at[depth] = (z, prod, "WIDE " + parts[2] + " * " + parts[3])
    out = {"per_depth_max": {d: {"Z": v[0], "poly": v[1], "program": v[2]} for d, v in sorted(best_at.items())}, "unresolved": unresolved[:20], "unresolved_count": len(unresolved)}
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
