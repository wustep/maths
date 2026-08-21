#!/usr/bin/env python3
"""Emit a sigma column table and its centraliser class representatives.

sigma is an element of prime order in GL(r,2) with a 1-dimensional fixed
space.  The centraliser of sigma acts on the sigma-orbits and on the partner
pairs {O, O+f}; a subgroup of it is enough to reduce the forced starting
object of orbit_search_g, since using a subgroup only refines the classes.

Kinds:
  r10-30  r = 10, order 7,  M1+M1+M1+trivial
  r10-21  r = 10, order 7,  M1+M1+M2+trivial
  r11-11  r = 11, order 11, F_1024 (mult by an element of order 11) + trivial
  r11-23  r = 11, order 23, F_2048 (mult by an element of order 23), no fixed
          vector at all -- so an invariant set is a union of full orbits and
          its size is a multiple of 23

Usage: sigma_setup.py <kind> <sigma-out> <json-out>
"""
import json
import random
import sys


def mul_M1(a):                                   # F_2[y]/(y^3+y+1), times y
    a0, a1, a2 = a & 1, (a >> 1) & 1, (a >> 2) & 1
    return a2 | ((a0 ^ a2) << 1) | (a1 << 2)


def mul_M2(a):                                   # F_2[y]/(y^3+y^2+1), times y
    a0, a1, a2 = a & 1, (a >> 1) & 1, (a >> 2) & 1
    return a2 | (a0 << 1) | ((a1 ^ a2) << 2)


def gf1024_mul(a, b):                            # F_2[x]/(x^10+x^3+1)
    res = 0
    for i in range(10):
        if (b >> i) & 1:
            res ^= a << i
    for i in range(19, 9, -1):
        if (res >> i) & 1:
            res ^= (1 << i) ^ (1 << (i - 10)) ^ (1 << (i - 7))
    return res


def field_mul(poly, deg):
    """multiplication in F_2[x]/(poly), poly given as an int bitmask."""
    def mul(a, b):
        res = 0
        for i in range(deg):
            if (b >> i) & 1:
                res ^= a << i
        for i in range(2 * deg - 2, deg - 1, -1):
            if (res >> i) & 1:
                res ^= poly << (i - deg)
        return res
    return mul


def field_order_cols(poly, deg, want):
    """columns of multiplication by an element of order `want` in F_2^deg."""
    mul = field_mul(poly, deg)
    step = ((1 << deg) - 1) // want
    assert step * want == (1 << deg) - 1, f"{want} does not divide 2^{deg}-1"
    beta = 1
    for _ in range(step):
        beta = mul(beta, 2)
    chk, k = beta, 1
    while chk != 1:
        chk, k = mul(chk, beta), k + 1
    assert k == want, f"element has order {k}, not {want}"
    return [mul(beta, 1 << i) for i in range(deg)]


def gf2048_mul(a, b):                            # F_2[x]/(x^11+x^2+1)
    res = 0
    for i in range(11):
        if (b >> i) & 1:
            res ^= a << i
    for i in range(21, 10, -1):
        if (res >> i) & 1:
            res ^= (1 << i) ^ (1 << (i - 11)) ^ (1 << (i - 9))
    return res


def build(kind):
    if kind in ("r10-30", "r10-21"):
        third = mul_M2 if kind.endswith("21") else mul_M1
        r = 10
        def sig(v):
            return (mul_M1(v & 7) | (mul_M1((v >> 3) & 7) << 3)
                    | (third((v >> 6) & 7) << 6) | (v & (1 << 9)))
        return r, [sig(1 << i) for i in range(r)]
    if kind == "r11-11":
        r = 11
        beta = 1                                  # x^93, x primitive of order 1023
        for _ in range(93):
            beta = gf1024_mul(beta, 2)
        chk, k = beta, 1
        while chk != 1:
            chk, k = gf1024_mul(chk, beta), k + 1
        assert k == 11, f"beta has order {k}, not 11"
        cols = [gf1024_mul(beta, 1 << i) for i in range(10)] + [1 << 10]
        return r, cols
    if kind == "r11-23":
        r = 11
        beta = 1                                  # x^89, x primitive of order 2047
        for _ in range(89):
            beta = gf2048_mul(beta, 2)
        chk, k = beta, 1
        while chk != 1:
            chk, k = gf2048_mul(chk, beta), k + 1
        assert k == 23, f"beta has order {k}, not 23"
        return r, [gf2048_mul(beta, 1 << i) for i in range(11)]
    GENERIC = {
        # kind: (r, [(field-poly, deg, order) blocks], c)
        "r11-17-c3":  (11, [(0x11d, 8, 17)], 3),
        "r11-31-c6":  (11, [(0x25, 5, 31)], 6),
        "r10-7-c4a":  (10, [(0xb, 3, 7), (0xb, 3, 7)], 4),
        "r10-7-c4b":  (10, [(0xb, 3, 7), (0xd, 3, 7)], 4),
        "r10-7-c7":   (10, [(0xb, 3, 7)], 7),
    }
    if kind in GENERIC:
        r, blocks, c = GENERIC[kind]
        cols, off = [], 0
        for poly, deg, order in blocks:
            bc = field_order_cols(poly, deg, order)
            cols += [x << off for x in bc]
            off += deg
        assert off + c == r, f"{kind}: blocks {off} + c {c} != r {r}"
        cols += [1 << (off + i) for i in range(c)]
        return r, cols
    raise SystemExit(f"unknown kind {kind}")


def apply_cols(cols, v, r):
    out = 0
    for i in range(r):
        if (v >> i) & 1:
            out ^= cols[i]
    return out


def rank(cols):
    piv = []
    for c in cols:
        cur = c
        for p in piv:
            if (cur >> (p.bit_length() - 1)) & 1:
                cur ^= p
        if cur:
            piv.append(cur)
    return len(piv)


def commutant_basis(scols, r):
    rows = []
    for j in range(r):
        sj = scols[j]
        for i in range(r):
            eq = 0
            for k in range(r):
                if (sj >> k) & 1:
                    eq ^= 1 << (r * k + i)
            for k in range(r):
                if (scols[k] >> i) & 1:
                    eq ^= 1 << (r * j + k)
            rows.append(eq)
    piv = {}
    for row in rows:
        cur = row
        while cur:
            h = cur.bit_length() - 1
            if h in piv:
                cur ^= piv[h]
            else:
                piv[h] = cur
                break
    for h in sorted(piv):
        for h2 in sorted(piv):
            if h2 < h and (piv[h] >> h2) & 1:
                piv[h] ^= piv[h2]
    basis = []
    for fcol in (c for c in range(r * r) if c not in piv):
        vec = 1 << fcol
        for h in piv:
            if (piv[h] >> fcol) & 1:
                vec |= 1 << h
        cols = [0] * r
        for bit in range(r * r):
            if (vec >> bit) & 1:
                cols[bit // r] |= 1 << (bit % r)
        basis.append(cols)
    return basis


def main():
    kind, sig_out, json_out = sys.argv[1], sys.argv[2], sys.argv[3]
    r, scols = build(kind)
    n = 1 << r
    sig = [apply_cols(scols, v, r) for v in range(n)]

    fixed = [v for v in range(1, n) if sig[v] == v]
    f = fixed[0] if len(fixed) == 1 else 0
    order = 1
    fset = set(fixed)
    v = next(x for x in range(1, n) if x not in fset)
    u = sig[v]
    while u != v:
        u, order = sig[u], order + 1
    order += 0

    oid = [-1] * n
    reps = []
    for v in range(1, n):
        if v in fset or oid[v] >= 0:
            continue
        k = len(reps)
        u = v
        for _ in range(order):
            assert oid[u] == -1
            oid[u] = k
            u = sig[u]
        assert u == v
        reps.append(v)
    assert (n - 1 - len(fixed)) == len(reps) * order

    basis = commutant_basis(scols, r)
    for b in basis:
        assert [apply_cols(scols, b[i], r) for i in range(r)] == \
               [apply_cols(b, scols[i], r) for i in range(r)], "basis fails to commute"

    gens, seen, rng, tries = [], set(), random.Random(20260821), 0
    while len(gens) < 40 and tries < 50000:
        tries += 1
        cols = [0] * r
        for b in basis:
            if rng.getrandbits(1):
                cols = [cols[i] ^ b[i] for i in range(r)]
        if rank(cols) != r or tuple(cols) in seen:
            continue
        seen.add(tuple(cols))
        gens.append(cols)

    def orbit_classes(act):
        lab, classes = {}, []
        for s in act():
            if s in lab:
                continue
            c = len(classes)
            lab[s], stack, members = c, [s], []
            while stack:
                cur = stack.pop()
                members.append(cur)
                for g in gens:
                    t = step(cur, g)
                    if t not in lab:
                        lab[t] = c
                        stack.append(t)
            classes.append(members)
        return classes

    # classes of single orbits
    step = lambda o, g: oid[apply_cols(g, reps[o], r)]
    orb_classes = orbit_classes(lambda: range(len(reps)))
    # classes of partner pairs {O, O+f}
    if len(fixed) == 1:
        pairs = sorted({tuple(sorted((i, oid[reps[i] ^ f]))) for i in range(len(reps))})
        assert all(i != j for i, j in pairs)
    else:
        pairs = []
    pmap = {}
    for pr in pairs:
        pmap[pr[0]] = pr
        pmap[pr[1]] = pr
    step_pair = lambda pr, g: pmap[oid[apply_cols(g, reps[pr[0]], r)]]
    step = step_pair
    pair_classes = orbit_classes(lambda: pairs) if pairs else []

    with open(sig_out, "w") as fh:
        fh.write(f"{r}\n" + " ".join(map(str, scols)) + "\n")
    info = {
        "kind": kind, "r": r, "order": order, "f": f, "n_fixed": len(fixed),
        "n_orbits": len(reps), "commutant_dim": len(basis), "n_gens": len(gens),
        "orbit_class_sizes": [len(c) for c in orb_classes],
        "orbit_class_reps": [reps[sorted(c)[0]] for c in orb_classes],
        "pair_class_sizes": [len(c) for c in pair_classes],
        "pair_class_reps": [[reps[i] for i in sorted(c)[0]] for c in pair_classes],
    }
    with open(json_out, "w") as fh:
        json.dump(info, fh, indent=1)
    print(f"{kind}: r={r} order={order} orbits={len(reps)} commutant_dim={len(basis)} "
          f"orbit-classes={info['orbit_class_sizes']} pair-classes={info['pair_class_sizes']}")


if __name__ == "__main__":
    main()
