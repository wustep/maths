#!/usr/bin/env python3
"""Prescribed-automorphism setup for l_2(10,2) <= 49.

Builds an order-7 sigma in GL(10,2) with a 1-dimensional fixed space, lists its
orbits on F_2^10, finds the partner pairs (the only way the fixed vector f can
be covered), and reduces those pairs modulo an explicit subgroup of the
centraliser of sigma in GL(10,2).

Module types (F_2[C_7] has two 3-dimensional irreducibles M1, M2 and the
trivial one).  With a 1-dimensional fixed space, V = M1^a (+) M2^b (+) triv,
a+b = 3; up to the outer automorphism of C_7 that is (3,0) and (2,1).

Usage: setup.py <30|21> <outfile>
"""
import json
import random
import sys

R = 10
N = 1 << R

# companion matrices for the two irreducible cubics over F_2, acting on
# (a0,a1,a2) <-> a0 + a1 y + a2 y^2, as multiplication by y.
def mul_M1(a):            # y^3 = y + 1
    a0, a1, a2 = a & 1, (a >> 1) & 1, (a >> 2) & 1
    return a2 | ((a0 ^ a2) << 1) | (a1 << 2)

def mul_M2(a):            # y^3 = y^2 + 1
    a0, a1, a2 = a & 1, (a >> 1) & 1, (a >> 2) & 1
    return a2 | (a0 << 1) | ((a1 ^ a2) << 2)


def build_sigma(kind):
    """kind '30' -> M1+M1+M1+triv, kind '21' -> M1+M1+M2+triv."""
    blocks = [mul_M1, mul_M1, mul_M1 if kind == '30' else mul_M2]
    sig = [0] * N
    for v in range(N):
        out = 0
        for b, f in enumerate(blocks):
            out |= f((v >> (3 * b)) & 7) << (3 * b)
        out |= v & (1 << 9)          # trivial summand on bit 9
        sig[v] = out
    return sig


def matrix_of(sig):
    """sigma as a list of 10 column images (sigma is F_2-linear)."""
    return [sig[1 << i] for i in range(R)]


def apply_cols(cols, v):
    out = 0
    for i in range(R):
        if (v >> i) & 1:
            out ^= cols[i]
    return out


def commutant_basis(scols):
    """F_2-basis of {M in End(V) : M sigma = sigma M}, M given by 10 columns.

    Unknown m[i][j] (bit i of column j) is indexed 10*j + i.
    """
    rows = []
    for j in range(R):
        sj = scols[j]
        for i in range(R):
            eq = 0
            # bit i of M(sigma e_j) = XOR of bit i of column k of M, k in sj
            for k in range(R):
                if (sj >> k) & 1:
                    eq ^= 1 << (10 * k + i)
            # bit i of sigma(M e_j) = XOR of m[k][j] over k with sigma_{ik} = 1
            for k in range(R):
                if (scols[k] >> i) & 1:
                    eq ^= 1 << (10 * j + k)
            rows.append(eq)

    piv = {}                                    # pivot column -> row, leading bit = key
    for r in rows:
        cur = r
        while cur:
            h = cur.bit_length() - 1
            if h in piv:
                cur ^= piv[h]
            else:
                piv[h] = cur
                break
    for h in sorted(piv):                       # reduce, low pivots first
        for h2 in sorted(piv):
            if h2 < h and (piv[h] >> h2) & 1:
                piv[h] ^= piv[h2]

    basis = []
    for fcol in (c for c in range(100) if c not in piv):
        vec = 1 << fcol
        for h in piv:
            if (piv[h] >> fcol) & 1:
                vec |= 1 << h
        cols = [0] * R
        for bit in range(100):
            if (vec >> bit) & 1:
                cols[bit // 10] |= 1 << (bit % 10)
        basis.append(cols)
    return basis


def compose(a, b):
    """columns of a o b."""
    return [apply_cols(a, b[i]) for i in range(R)]


def rank(cols):
    piv = []
    for c in cols:
        cur = c
        for p in piv:
            if cur >> (p.bit_length() - 1) & 1:
                cur ^= p
        if cur:
            piv.append(cur)
    return len(piv)


def main():
    kind, out = sys.argv[1], sys.argv[2]
    sig = build_sigma(kind)
    scols = matrix_of(sig)
    assert all(sig[v] == apply_cols(scols, v) for v in range(N)), "sigma not linear"

    # order 7, fixed space dimension 1
    p = list(range(N))
    for _ in range(7):
        p = [sig[x] for x in p]
    assert p == list(range(N)), "sigma^7 != 1"
    fixed = [v for v in range(N) if sig[v] == v]
    assert len(fixed) == 2, f"fixed space size {len(fixed)}"
    f = [v for v in fixed if v][0]

    # orbits
    oid = [-1] * N
    reps = []
    for v in range(1, N):
        if v == f or oid[v] >= 0:
            continue
        k = len(reps)
        u = v
        for _ in range(7):
            assert oid[u] == -1
            oid[u] = k
            u = sig[u]
        assert u == v
        reps.append(v)
    assert len(reps) == 146, len(reps)

    # partner pairs: f = a + b forces b = a + f, so the two orbits O and O + f
    pairs = sorted({tuple(sorted((i, oid[reps[i] ^ f]))) for i in range(146)})
    assert len(pairs) == 73 and all(i != j for i, j in pairs)

    # explicit subgroup of the centraliser, from the commutant algebra
    basis = commutant_basis(scols)
    gens = []
    seen = set()
    rng = random.Random(20260821)
    tries = 0
    while len(gens) < 40 and tries < 50000:
        tries += 1
        cols = [0] * R
        for b in basis:
            if rng.getrandbits(1):
                cols = [cols[i] ^ b[i] for i in range(R)]
        if rank(cols) != R:
            continue
        key = tuple(cols)
        if key in seen:
            continue
        seen.add(key)
        assert compose(cols, scols) == compose(scols, cols), "generator does not commute"
        gens.append(cols)

    # orbits of <gens> on the 73 partner pairs
    idx = {pr: k for k, pr in enumerate(pairs)}
    def pair_of(orb):
        return idx[tuple(sorted((orb, oid[reps[orb] ^ f])))]
    lab = [-1] * 73
    classes = []
    for s in range(73):
        if lab[s] >= 0:
            continue
        c = len(classes)
        stack, members = [s], []
        lab[s] = c
        while stack:
            cur = stack.pop()
            members.append(cur)
            i0 = pairs[cur][0]
            for g in gens:
                t = pair_of(oid[apply_cols(g, reps[i0])])
                if lab[t] < 0:
                    lab[t] = c
                    stack.append(t)
        classes.append(sorted(members))

    info = {
        "kind": kind,
        "commutant_dim": len(basis),
        "n_centraliser_gens": len(gens),
        "f": f,
        "n_orbits": len(reps),
        "n_partner_pairs": len(pairs),
        "classes": [[list(pairs[m]) for m in cls] for cls in classes],
        "class_sizes": [len(c) for c in classes],
        # forced pair representatives, as raw vectors so the C side can map them
        # through its own orbit indexing
        "forced_pairs": [[reps[pairs[cls[0]][0]], reps[pairs[cls[0]][1]]] for cls in classes],
    }
    with open(out, "w") as fh:
        json.dump(info, fh, indent=1)
    print(f"kind={kind} commutant_dim={len(basis)} gens={len(gens)} "
          f"partner-pair classes={info['class_sizes']}")


if __name__ == "__main__":
    main()
