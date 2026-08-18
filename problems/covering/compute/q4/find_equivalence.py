#!/usr/bin/env python3
"""Search for an explicit GL(10,2) equivalence between two 49-column
configurations (as column sets).  Backtracking on images of a column
basis, guided by combinatorial colors (representation-multiplicity
profiles), verifying the full set map at the end.

Usage: find_equivalence.py A.cols B.cols
Prints the matrix (10 basis images) if found.  Deterministic.
"""

import sys
from collections import Counter


def load(path):
    cols = []
    for line in open(path):
        if line.lstrip().startswith("#"):
            continue
        cols += [int(t) for t in line.split()]
    assert len(cols) == len(set(cols))
    return sorted(cols)


def counts_of(cols):
    cnt = Counter()
    cnt[0] += 1
    for i, a in enumerate(cols):
        cnt[a] += 1
        for b in cols[:i]:
            cnt[a ^ b] += 1
    return cnt


def color(cols, cnt):
    # per-column color: (own multiplicity, sorted multiset of pair-sum
    # multiplicities with every other column)
    out = {}
    for a in cols:
        prof = sorted(cnt[a ^ b] for b in cols if b != a)
        out[a] = (cnt[a], tuple(prof))
    return out


def solve(A, B):
    cntA, cntB = counts_of(A), counts_of(B)
    colA, colB = color(A, cntA), color(B, cntB)
    # candidate images: same color
    cand = {a: [b for b in B if colB[b] == colA[a]] for a in A}
    # choose a basis of A greedily from columns with fewest candidates
    orderA = sorted(A, key=lambda a: len(cand[a]))
    basis = []
    for a in orderA:
        v = a
        for bb in basis:
            v = min(v, v ^ bb[0]) if False else v
        # rank check against current basis (over the raw vectors)
        vv = a
        red = a
        for (bvec, _) in basis:
            pass
        # simple independence test
        vecs = [x for (x, _) in basis] + [a]
        if rank(vecs) == len(vecs):
            basis.append((a, None))
        if len(basis) == 10:
            break
    basis_vecs = [x for (x, _) in basis]
    assert rank(basis_vecs) == 10

    setB = set(B)

    def extend(idx, images):
        if idx == 10:
            return images
        a = basis_vecs[idx]
        for b in cand[a]:
            if b in images.values():
                continue
            trial = dict(images)
            trial[a] = b
            # partial consistency: any element of A in the span of
            # basis[:idx+1] must map into setB
            ok = True
            # enumerate span combos incrementally: check all A-columns
            # expressible over chosen basis prefix
            chosen = basis_vecs[: idx + 1]
            img = [trial[x] for x in chosen]
            n = idx + 1
            for mask in range(1, 1 << n):
                va = 0
                vb = 0
                for t in range(n):
                    if mask >> t & 1:
                        va ^= chosen[t]
                        vb ^= img[t]
                in_a = va in cand  # va is an A-column
                if in_a and vb not in setB:
                    ok = False
                    break
                if in_a and colB.get(vb) != colA[va]:
                    ok = False
                    break
                if not in_a and vb in setB:
                    ok = False
                    break
            if not ok:
                continue
            res = extend(idx + 1, trial)
            if res:
                return res
        return None

    res = extend(0, {})
    if res is None:
        return None
    return basis_vecs, [res[x] for x in basis_vecs]


def rank(vecs):
    basis = {}
    r = 0
    for c in vecs:
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


def apply_map(basis_vecs, images, v):
    # solve v over basis_vecs, apply to images
    rows = list(zip(basis_vecs, images))
    out = 0
    vv = v
    # gaussian: reduce v over basis, tracking image combination
    work = [(bv, im) for bv, im in rows]
    # triangularize
    pivots = {}
    for bv, im in work:
        cur, curim = bv, im
        while cur:
            p = cur.bit_length() - 1
            if p in pivots:
                pb, pim = pivots[p]
                cur ^= pb
                curim ^= pim
            else:
                pivots[p] = (cur, curim)
                break
    while vv:
        p = vv.bit_length() - 1
        pb, pim = pivots[p]
        vv ^= pb
        out ^= pim
    return out


def main():
    A = load(sys.argv[1])
    B = load(sys.argv[2])
    res = solve(A, B)
    if res is None:
        print("no equivalence found (colors/backtracking exhausted)")
        return 1
    basis_vecs, images = res
    # verify: map every A column, compare sets
    mapped = sorted(apply_map(basis_vecs, images, a) for a in A)
    if mapped == B:
        print("EQUIVALENT: linear map sends A onto B")
        print("basis:", basis_vecs)
        print("images:", images)
        return 0
    print("map found on basis but full sets differ - not equivalent this way")
    return 1


if __name__ == "__main__":
    sys.exit(main())
