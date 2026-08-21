#!/usr/bin/env python3
"""Centraliser classes of m-subsets of the nonzero fixed vectors of sigma.

Conjugating a sigma-invariant set by an element of the centraliser of sigma
gives another sigma-invariant set of the same size, and carries its fixed part
to another m-subset of the fixed space.  So an exhaustive search only has to
run one m-subset per centraliser class, with the orbit part left completely
free.  Using a subgroup of the centraliser only refines the classes, so the
reduction stays sound.

Usage: fixed_classes.py <kind> <m>
"""
import random
import sys
from itertools import combinations

import sigma_setup as S


def main():
    kind, m = sys.argv[1], int(sys.argv[2])
    r, scols = S.build(kind)
    n = 1 << r
    sig = [S.apply_cols(scols, v, r) for v in range(n)]
    fixed = tuple(v for v in range(1, n) if sig[v] == v)

    basis = S.commutant_basis(scols, r)
    gens, seen, rng, tries = [], set(), random.Random(20260821), 0
    while len(gens) < 40 and tries < 50000:
        tries += 1
        cols = [0] * r
        for b in basis:
            if rng.getrandbits(1):
                cols = [cols[i] ^ b[i] for i in range(r)]
        if S.rank(cols) != r or tuple(cols) in seen:
            continue
        seen.add(tuple(cols))
        gens.append(cols)

    fset = set(fixed)
    acts = []
    for g in gens:
        img = {v: S.apply_cols(g, v, r) for v in fixed}
        assert set(img.values()) == fset, "centraliser does not preserve the fixed space"
        acts.append(img)

    lab, classes = {}, []
    for sub in combinations(fixed, m):
        key = frozenset(sub)
        if key in lab:
            continue
        c = len(classes)
        lab[key], stack, members = c, [key], 0
        while stack:
            cur = stack.pop()
            members += 1
            for img in acts:
                t = frozenset(img[v] for v in cur)
                if t not in lab:
                    lab[t] = c
                    stack.append(t)
        classes.append((sorted(key), members))
    total = sum(sz for _, sz in classes)
    print(f"# {kind}: {len(fixed)} fixed vectors, C({len(fixed)},{m}) = {total} "
          f"subsets in {len(classes)} centraliser classes", file=sys.stderr)
    for rep, sz in classes:
        print(" ".join(map(str, rep)), f"# class size {sz}")


if __name__ == "__main__":
    main()
