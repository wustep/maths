#!/usr/bin/env python3
"""DIMACS SAT for (5,5,43)-graphs with a fixed 3-cycle automorphism.

Vertices: 0 fixed, triples T_i = {3i+1, 3i+2, 3i+3} ~ Z/3, σ cycles each triple.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

NTR = 14
N = 43


class Enc:
    def __init__(self):
        self.clauses: list[list[int]] = []
        self.next = 1
        self.names = {}

    def var(self, *key) -> int:
        if key not in self.names:
            self.names[key] = self.next
            self.next += 1
        return self.names[key]

    def add(self, lits):
        if lits:
            self.clauses.append(lits)

    def new(self) -> int:
        v = self.next
        self.next += 1
        return v

    def card_between(self, lits, lo, hi):
        m = len(lits)
        hi = min(hi, m)
        lo = max(lo, 0)
        if lo > hi:
            self.add([1])
            self.add([-1])
            return
        if m == 0:
            return
        s = [[self.new() for _ in range(hi + 1)] for _ in range(m)]
        self.add([-lits[0], s[0][0]])
        self.add([lits[0], -s[0][0]])
        for j in range(1, hi + 1):
            self.add([-s[0][j]])
        for i in range(1, m):
            self.add([-lits[i], s[i][0]])
            self.add([-s[i - 1][0], s[i][0]])
            self.add([lits[i], s[i - 1][0], -s[i][0]])
            for j in range(1, hi + 1):
                self.add([-s[i - 1][j], s[i][j]])
                self.add([-lits[i], -s[i - 1][j - 1], s[i][j]])
                self.add([s[i - 1][j], lits[i], -s[i][j]])
                self.add([s[i - 1][j], s[i - 1][j - 1], -s[i][j]])
            self.add([-lits[i], -s[i - 1][hi]])
        if lo >= 1:
            self.add([s[m - 1][lo - 1]])


def triple_vert(i, r):
    return 3 * i + 1 + r


def edge_var(enc: Enc, u: int, v: int) -> int:
    if u > v:
        u, v = v, u
    if u == 0:
        i = (v - 1) // 3
        return enc.var("a", i)  # 0 adjacent to whole triple
    iu, ru = divmod(u - 1, 3)
    iv, rv = divmod(v - 1, 3)
    if iu == iv:
        return enc.var("b", iu)  # empty vs K3
    # between triples: class d = (rv - ru) mod 3
    d = (rv - ru) % 3
    return enc.var("c", min(iu, iv), max(iu, iv), d)


def build() -> Enc:
    enc = Enc()
    use_card = "--no-card" not in sys.argv
    if use_card:
        # deg(0) = 3 * #a_i in [18,24] => #a in [6,8]
        enc.card_between([enc.var("a", i) for i in range(NTR)], 6, 8)
        # deg of 3i+1:
        # a_i + 2*b_i + sum_{j!=i} (c(i,j,0)+c(i,j,1)+c(i,j,2))
        for i in range(NTR):
            lits = [enc.var("a", i), enc.var("b", i), enc.var("b", i)]
            for j in range(NTR):
                if j == i:
                    continue
                lo, hi = (i, j) if i < j else (j, i)
                for d in range(3):
                    lits.append(enc.var("c", lo, hi, d))
            enc.card_between(lits, 18, 24)

    nk = na = 0
    for comb in itertools.combinations(range(N), 5):
        evars = [edge_var(enc, x, y) for x, y in itertools.combinations(comb, 2)]
        enc.add([-v for v in evars])
        enc.add(list(evars))
        nk += 1
        na += 1
    enc.n_k = nk
    enc.n_a = na
    enc.nvars = enc.next - 1
    return enc


def main() -> None:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("cnf/order3_43.cnf")
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("building order-3", flush=True)
    enc = build()
    with dest.open("w") as f:
        f.write(f"c order-3-symmetric (5,5,43)\n")
        f.write(f"c k={enc.n_k}\n")
        f.write(f"p cnf {enc.nvars} {len(enc.clauses)}\n")
        for cl in enc.clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")
    print(f"vars={enc.nvars} clauses={len(enc.clauses)} wrote {dest} "
          f"bytes={dest.stat().st_size}")


if __name__ == "__main__":
    main()
