#!/usr/bin/env python3
"""DIMACS SAT for (s,t)-Ramsey graphs on n=2m+1 vertices with a fixed involution.

Vertices: 0 (fixed) and pairs P_i = {2*i+1, 2*i+2} for i=0..m-1.
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path


class Enc:
    def __init__(self, npairs: int):
        self.npairs = npairs
        self.na = npairs
        self.nb = npairs
        self.np = npairs * (npairs - 1) // 2
        self.nc = self.np
        self.clauses: list[list[int]] = []
        self.next = 1 + self.na + self.nb + self.np + self.nc
        self.pair_index = {}
        k = 0
        for i in range(npairs):
            for j in range(i + 1, npairs):
                self.pair_index[(i, j)] = k
                k += 1

    def a(self, i: int) -> int:
        return 1 + i

    def b(self, i: int) -> int:
        return 1 + self.na + i

    def p(self, i: int, j: int) -> int:
        if i > j:
            i, j = j, i
        return 1 + self.na + self.nb + self.pair_index[(i, j)]

    def c(self, i: int, j: int) -> int:
        if i > j:
            i, j = j, i
        return 1 + self.na + self.nb + self.np + self.pair_index[(i, j)]

    def new(self) -> int:
        v = self.next
        self.next += 1
        return v

    def add(self, lits: list[int]) -> None:
        if lits:
            self.clauses.append(lits)

    def card_between(self, lits: list[int], lo: int, hi: int) -> None:
        """Sequential counter: lo <= sum(lits) <= hi."""
        m = len(lits)
        if m == 0:
            if lo > 0:
                self.add([])  # unsat
            return
        hi = min(hi, m)
        lo = max(lo, 0)
        if lo > hi:
            self.add([1])
            self.add([-1])
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


def edge_var(enc: Enc, u: int, v: int) -> int:
    if u > v:
        u, v = v, u
    if u == 0:
        return enc.a((v - 1) // 2)
    iu = (u - 1) // 2
    iv = (v - 1) // 2
    if iu == iv:
        return enc.b(iu)
    u_side = (u - 1) % 2
    v_side = (v - 1) % 2
    if u_side == v_side:
        return enc.p(iu, iv)
    return enc.c(iu, iv)


def build(n: int, s: int, t: int, use_card: bool = True) -> Enc:
    if n % 2 == 0:
        raise ValueError("need odd n for an involution with one fixed point")
    npairs = (n - 1) // 2
    enc = Enc(npairs)
    # R(s-1,t)=? we use the classical (5,5) window when s=t=5
    if s == 5 and t == 5:
        deg_lo = max(0, n - 25)
        deg_hi = min(n - 1, 24)
    else:
        deg_lo = 0
        deg_hi = n - 1
    # deg(0) = 2 * #a_i
    if use_card:
        a_lo = (deg_lo + 1) // 2
        a_hi = deg_hi // 2
        enc.card_between([enc.a(i) for i in range(npairs)], a_lo, a_hi)
        for i in range(npairs):
            lits = [enc.a(i), enc.b(i)]
            for j in range(npairs):
                if j == i:
                    continue
                lits.append(enc.p(i, j))
                lits.append(enc.c(i, j))
            enc.card_between(lits, deg_lo, deg_hi)

    k5 = a5 = 0
    for comb in itertools.combinations(range(n), s):
        evars = [edge_var(enc, x, y) for x, y in itertools.combinations(comb, 2)]
        enc.add([-v for v in evars])
        k5 += 1
    if t != s:
        for comb in itertools.combinations(range(n), t):
            evars = [edge_var(enc, x, y) for x, y in itertools.combinations(comb, 2)]
            enc.add(list(evars))
            a5 += 1
    else:
        for comb in itertools.combinations(range(n), t):
            evars = [edge_var(enc, x, y) for x, y in itertools.combinations(comb, 2)]
            enc.add(list(evars))
            a5 += 1
    enc.n_k = k5
    enc.n_a = a5
    enc.nvars = enc.next - 1
    enc.n = n
    enc.s = s
    enc.t = t
    return enc


def write_dimacs(enc: Enc, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"c involution-symmetric R({enc.s},{enc.t},{enc.n})\n")
        f.write(f"c k_clauses={enc.n_k} a_clauses={enc.n_a}\n")
        f.write(f"p cnf {enc.nvars} {len(enc.clauses)}\n")
        for cl in enc.clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=43)
    ap.add_argument("--s", type=int, default=5)
    ap.add_argument("--t", type=int, default=5)
    ap.add_argument("--no-card", action="store_true")
    args = ap.parse_args()
    print(f"building n={args.n} s={args.s} t={args.t} card={not args.no_card}", flush=True)
    enc = build(args.n, args.s, args.t, use_card=not args.no_card)
    dest = Path(args.out)
    write_dimacs(enc, dest)
    print(f"vars={enc.nvars} clauses={len(enc.clauses)} wrote {dest} "
          f"bytes={dest.stat().st_size}", flush=True)


if __name__ == "__main__":
    main()
