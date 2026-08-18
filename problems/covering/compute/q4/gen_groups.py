#!/usr/bin/env python3
"""Generate group files for the q4 orbit DFS engine.

Each group file lists generator matrices of a subgroup of GL(10,2), one
generator per line, as the 10 images of the basis vectors e_0..e_9
encoded as 10-bit integers (bit i = coordinate i).

Cyclic cases: every block-diagonal order-L map, L in {3,5,7,9,15,21,35,45,105},
built from companion blocks of the irreducible divisors of x^L - 1 over F_2,
deduped up to subgroup equality (M and M^k generate the same subgroup for
gcd(k, L) = 1, and the block of exponent e becomes exponent k*e; blocks are
labeled by cyclotomic cosets so this is a cheap canonical form).

Non-cyclic: C7 x C7 subgroups acting by two commuting order-7 maps on
3+3+3+1 or 3+3+4 splittings, third-block characters (lam, mu) swept.

Deterministic: no randomness anywhere.
"""

import itertools
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "groups")


def poly_mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out


def poly_mod(a, m):
    dm = m.bit_length() - 1
    while a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def minpoly_of_power(n, e):
    """Minimal polynomial over F_2 of zeta^e where zeta has order n.

    Work in F_2[y]/(f) for a primitive-enough modulus: use the splitting
    field F_{2^d} with d = ord_n(2), realized inside F_2[y]/(f) where f is
    found by brute force as an irreducible of degree d for which y has
    order divisible by n... simpler: represent conjugates as exponent
    coset and multiply linear factors symbolically over the field.
    """
    d = 1
    while pow(2, d, n) != 1:
        d += 1
    # find an irreducible degree-d poly with primitive root y
    size = (1 << d) - 1
    for f in range(1 << d, 1 << (d + 1)):
        if f % 2 == 0:
            continue
        # check y has order size mod f (implies irreducible + primitive)
        ok = True
        x = 2  # y
        # compute order of y by checking y^size == 1 and y^(size/p) != 1
        def ppow(base, exp, mod):
            r = 1
            while exp:
                if exp & 1:
                    r = poly_mod(poly_mul(r, base), mod)
                exp >>= 1
                base = poly_mod(poly_mul(base, base), mod)
            return r
        if ppow(x, size, f) != 1:
            continue
        pf = size
        primes = set()
        t = pf
        p = 2
        while p * p <= t:
            while t % p == 0:
                primes.add(p)
                t //= p
            p += 1
        if t > 1:
            primes.add(t)
        for p in primes:
            if ppow(x, size // p, f) == 1:
                ok = False
                break
        if ok:
            modulus = f
            break
    else:
        raise RuntimeError("no field found")

    def fmul(a, b):
        return poly_mod(poly_mul(a, b), modulus)

    def fpow(a, k):
        r = 1
        while k:
            if k & 1:
                r = fmul(r, a)
            k >>= 1
            a = fmul(a, a)
        return r

    zeta = fpow(2, size // n)
    # conjugates zeta^(e*2^i)
    exps = set()
    cur = e % n
    while cur not in exps:
        exps.add(cur)
        cur = (cur * 2) % n
    # poly = prod (x - zeta^j): coefficients in the field, must land in F_2
    coeffs = [1]  # constant polynomial 1 (in x), coeffs[i] ~ x^i
    for j in sorted(exps):
        root = fpow(zeta, j)
        new = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new[i + 1] ^= c
            new[i] ^= fmul(c, root)
        coeffs = new
    out = 0
    for i, c in enumerate(coeffs):
        if c not in (0, 1):
            raise RuntimeError("minpoly not over F_2")
        if c:
            out |= 1 << i
    return out


def companion(poly):
    """Companion matrix of monic poly (int encoding), as column images."""
    deg = poly.bit_length() - 1
    low = poly & ((1 << deg) - 1)
    cols = []
    for i in range(deg - 1):
        cols.append(1 << (i + 1))
    cols.append(low)
    return cols  # cols[i] = image of e_i, dim = deg


def block_diag(blocks, total_dim=10):
    """blocks: list of column-image lists; pad with identity to total_dim."""
    cols = []
    offset = 0
    for b in blocks:
        d = len(b)
        for img in b:
            cols.append(img << offset)
        offset += d
    while offset < total_dim:
        cols.append(1 << offset)
        offset += 1
    assert len(cols) == total_dim
    return cols


def mat_mul(a, b):
    """Column-image composition: (a*b)(v) = a(b(v))."""
    def apply(m, v):
        out = 0
        i = 0
        while v:
            if v & 1:
                out ^= m[i]
            v >>= 1
            i += 1
        return out
    return [apply(a, bi) for bi in b]


def mat_pow(m, k):
    r = [1 << i for i in range(len(m))]
    while k:
        if k & 1:
            r = mat_mul(r, m)
        k >>= 1
        m = mat_mul(m, m)
    return r


def coset_label(n, e):
    e %= n
    best = e
    cur = (e * 2) % n
    while cur != e:
        best = min(best, cur)
        cur = (cur * 2) % n
    return best


def lcm(a, b):
    import math
    return a * b // math.gcd(a, b)


def cyclic_cases():
    """Enumerate block multisets, dedupe by subgroup canonical key."""
    # available nontrivial blocks: (n, coset_label, dim)
    blocks = []
    for n in (3, 5, 7, 9, 15, 21):
        d = 1
        while pow(2, d, n) != 1:
            d += 1
        seen = set()
        for e in range(1, n):
            # element of order exactly n
            import math
            if math.gcd(e, n) != 1:
                continue
            lab = coset_label(n, e)
            if lab in seen:
                continue
            seen.add(lab)
            blocks.append((n, lab, d))
    # multisets of blocks with total nontrivial dim <= 10
    cases = {}
    def rec(start, dims_left, chosen):
        if chosen:
            L = 1
            for (n, _lab, _d) in chosen:
                L = lcm(L, n)
            if L > 2:
                # canonical key over k coprime to L
                import math
                keys = []
                for k in range(1, L):
                    if math.gcd(k, L) != 1:
                        continue
                    key = tuple(sorted((n, coset_label(n, k * lab if lab else k))
                                       for (n, lab, _d) in chosen))
                    keys.append(key)
                canon = (10 - sum(d for (_n, _l, d) in chosen), min(keys), L)
                if canon not in cases:
                    cases[canon] = list(chosen)
        for i in range(start, len(blocks)):
            n, lab, d = blocks[i]
            if d <= dims_left:
                rec(i, dims_left - d, chosen + [(n, lab, d)])
    rec(0, 10, [])
    return cases


def write_group(name, gen_list, comment):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".grp")
    with open(path, "w") as f:
        f.write("# %s\n" % comment)
        for gen in gen_list:
            f.write(" ".join(str(c) for c in gen) + "\n")
    return path


def main():
    minpoly_cache = {}

    def block_matrix(n, lab):
        if (n, lab) not in minpoly_cache:
            minpoly_cache[(n, lab)] = minpoly_of_power(n, lab if lab else 1)
        return companion(minpoly_cache[(n, lab)])

    written = []
    for (t, key, L), chosen in sorted(cyclic_cases().items()):
        blocks = [block_matrix(n, lab) for (n, lab, _d) in chosen]
        gen = block_diag(blocks)
        desc = "+".join("%d.%d" % (n, lab) for (n, lab, _d) in chosen)
        name = "cyc_L%d_t%d_%s" % (L, t, desc.replace(".", "_").replace("+", "__"))
        comment = ("cyclic order %d, trivial dim %d, blocks %s "
                   "(n.cosetlabel), minpolys %s" %
                   (L, t, desc,
                    ",".join(hex(minpoly_cache[(n, lab)])
                             for (n, lab, _d) in chosen)))
        written.append(write_group(name, [gen], comment))

    # C7 x C7 groups
    C1 = companion(minpoly_of_power(7, 1))
    # 3+3+4: two independent blocks
    g1 = block_diag([C1, [1 << i for i in range(3)]])
    g2 = block_diag([[1 << i for i in range(3)], C1])
    written.append(write_group(
        "c7c7_t4", [g1, g2], "C7xC7 on 3+3+4, characters (1,0),(0,1)"))
    # 3+3+3+1: third block character (lam, mu)
    I3 = [1, 2, 4]
    for lam in range(7):
        for mu in range(7):
            if lam == 0 and mu == 0:
                continue
            b3a = mat_pow(C1, lam) if lam else I3
            b3b = mat_pow(C1, mu) if mu else I3
            # g1 acts C1 on block1, C1^lam on block3; g2 acts C1 on block2,
            # C1^mu on block3
            g1 = block_diag([C1, I3, b3a])
            g2 = block_diag([I3, C1, b3b])
            written.append(write_group(
                "c7c7_t1_l%d_m%d" % (lam, mu), [g1, g2],
                "C7xC7 on 3+3+3+1, third-block character (%d,%d)" % (lam, mu)))

    print("wrote %d group files under %s" % (len(written), OUT))
    for p in written:
        print(os.path.basename(p))


if __name__ == "__main__":
    sys.exit(main())
