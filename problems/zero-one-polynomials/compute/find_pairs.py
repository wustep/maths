#!/usr/bin/env python3
"""
List all extra homometric pairs for small n:
subsets A,B of {0,...,n} containing 0, with the same difference
multiset, B not equal to A or to max(A)-A.

Also record a coarse factorization type of the associated 0-1
polynomials (via sympy) so we can see Filaseta Lemma 2 in action.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict


def popcount(x: int) -> int:
    return x.bit_count()


def histogram(bits: int, n: int) -> tuple:
    return tuple(popcount(bits & (bits >> k)) for k in range(1, n + 1))


def bit_reverse(bits: int, width: int) -> int:
    r = 0
    for i in range(width):
        if bits >> i & 1:
            r |= 1 << (width - 1 - i)
    return r


def support(bits: int) -> list[int]:
    return [i for i in range(bits.bit_length()) if bits >> i & 1]


def reflect(bits: int) -> int:
    if bits == 0:
        return 0
    m = bits.bit_length() - 1
    return bit_reverse(bits, m + 1)


def collect(n: int):
    groups = defaultdict(list)
    nA = 1 << n
    for free in range(nA):
        bits = 1 | (free << 1)
        groups[histogram(bits, n)].append(bits)

    extras = []
    for hist, members in groups.items():
        # expand each member by its reflection; unique
        orbit = set()
        for b in members:
            orbit.add(b)
            orbit.add(reflect(b))
        # reflections of sets with max < n still live in the same n-box
        # (support inside 0..n)
        if len(orbit) <= 2 and len(members) <= 2:
            # typical {A} or {A, A'}
            continue
        extras.append(
            {
                "hist": hist,
                "members": [support(b) for b in sorted(set(members))],
                "orbit_size": len(orbit),
                "class_size": len(set(members)),
            }
        )
    return extras


def try_factor_types(extras, n):
    """Optional sympy factorisation of the 0-1 polynomials in extra classes."""
    try:
        from sympy import Poly, ZZ, symbols

        x = symbols("x")
    except Exception:
        return extras
    for ex in extras:
        types = []
        for supp in ex["members"]:
            coeffs = [0] * (n + 1)
            for i in supp:
                if i <= n:
                    coeffs[i] = 1
            # Poly.from_list wants highest degree first
            p = Poly.from_list(list(reversed(coeffs)), x, domain=ZZ)
            fac = p.factor_list()[1]
            types.append([(str(f.as_expr()), int(e)) for f, e in fac])
        ex["factorizations"] = types
    return extras


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    summary = []
    all_extras = {}
    for n in range(1, 19):
        extras = collect(n)
        extras = try_factor_types(extras, n)
        all_extras[str(n)] = extras
        print(f"n={n:2d}  extra_classes={len(extras):4d}", flush=True)
        if n <= 14:
            for ex in extras:
                print(f"    class {ex['members']}", flush=True)
                if "factorizations" in ex:
                    print(f"      factors {ex['factorizations']}", flush=True)
        summary.append({"n": n, "extra_classes": len(extras)})

    path = os.path.join(out_dir, "homometric_pairs.json")
    with open(path, "w") as f:
        json.dump({"summary": summary, "extras": all_extras}, f, indent=2)
        f.write("\n")
    print(f"wrote {path}", flush=True)


if __name__ == "__main__":
    main()
