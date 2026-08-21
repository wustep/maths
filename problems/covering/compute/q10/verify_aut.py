#!/usr/bin/env python3
"""Independent check of an automorphism group listed by aut_group.c.

Reads the "basis", "set" and "g ..." lines, rebuilds each g as a matrix over
F_2, and verifies, without reusing any of the search logic:
  * every g is invertible,
  * every g maps S onto S,
  * the listed elements are pairwise distinct,
  * the set is closed under composition and inverses and contains the identity,
so the listed elements really do form a group of the stated order.

Usage: verify_aut.py <listing> [...]
"""
import sys


def main():
    for path in sys.argv[1:]:
        basis = S = None
        gens = []
        for line in open(path):
            t = line.split()
            if not t:
                continue
            if t[0] == "basis":
                basis = [int(x) for x in t[1:]]
            elif t[0] == "set":
                S = [int(x) for x in t[1:]]
            elif t[0] == "g":
                gens.append([int(x) for x in t[1:]])
        r = len(basis)
        Sset = set(S)

        # g is given by the images of `basis`; convert to images of e_0..e_{r-1}
        def to_cols(img):
            # solve for the matrix M with M(basis[j]) = img[j]
            rowsL = [(basis[j], img[j]) for j in range(r)]
            piv = []
            for src, dst in rowsL:
                cur_s, cur_d = src, dst
                for ps, pd in piv:
                    if (cur_s >> (ps.bit_length() - 1)) & 1:
                        cur_s ^= ps
                        cur_d ^= pd
                if cur_s:
                    piv.append((cur_s, cur_d))
            piv.sort(key=lambda x: -x[0].bit_length())
            cols = []
            for i in range(r):
                v, out = 1 << i, 0
                for ps, pd in piv:
                    if (v >> (ps.bit_length() - 1)) & 1:
                        v ^= ps
                        out ^= pd
                assert v == 0, "basis images do not determine a linear map"
                cols.append(out)
            return tuple(cols)

        def apply(cols, v):
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

        G = set()
        for img in gens:
            cols = to_cols(img)
            assert rank(cols) == r, "not invertible"
            assert {apply(cols, s) for s in S} == Sset, "does not preserve S"
            G.add(cols)
        assert len(G) == len(gens), f"duplicates: {len(gens)} listed, {len(G)} distinct"
        ident = tuple(1 << i for i in range(r))
        assert ident in G, "identity missing"
        for a in G:
            for b in G:
                comp = tuple(apply(a, b[i]) for i in range(r))
                assert comp in G, "not closed under composition"
        for a in G:
            inv = None
            for b in G:
                if tuple(apply(a, b[i]) for i in range(r)) == ident:
                    inv = b
                    break
            assert inv is not None, "element without an inverse"
        print(f"{path}: |G| = {len(G)}  invertible, S-preserving, distinct, "
              f"closed under composition and inverses, contains the identity")


if __name__ == "__main__":
    main()
