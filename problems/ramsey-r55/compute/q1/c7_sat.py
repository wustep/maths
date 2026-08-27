#!/usr/bin/env python3
"""C7-symmetric (5,5)-graphs.

n=42: six orbits of 7 (no fixed point). A model would be a new (5,5,42)-graph
outside the published 656 if Aut has a 7-cycle; those 656 are checked separately.

n=43: one fixed vertex plus six orbits. deg(0) must be 21 (a multiple of 7
inside [18,24]), so the fixed vertex meets exactly three orbits.

Self-test: n=7 (one orbit, 3 distance bits) exhausts 8 circulants and checks
the encoder against r55lib.is_ramsey.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import dump_json, is_ramsey, n_edges


class Enc:
    def __init__(self):
        self.clauses: list[list[int]] = []
        self.next = 1
        self.names: dict = {}

    def var(self, *key) -> int:
        if key not in self.names:
            self.names[key] = self.next
            self.next += 1
        return self.names[key]

    def add(self, lits):
        self.clauses.append(list(lits))

    def new(self) -> int:
        v = self.next
        self.next += 1
        return v

    def card_eq(self, lits, k):
        self.card_between(lits, k, k)

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


def vertices_42():
    # (orbit, r) -> 7*orbit + r
    return 42, 6, 0


def vertices_43():
    return 43, 6, 1


def vid(offset, orbit, r):
    return offset + 7 * orbit + (r % 7)


def edge_var(enc: Enc, n: int, offset: int, norb: int, u: int, v: int) -> int:
    if u > v:
        u, v = v, u
    if offset and u == 0:
        orbit = (v - 1) // 7
        return enc.var("a", orbit)
    uu = u - offset
    vv = v - offset
    iu, ru = divmod(uu, 7)
    iv, rv = divmod(vv, 7)
    if iu == iv:
        d = (rv - ru) % 7
        d = min(d, 7 - d)
        return enc.var("w", iu, d)
    if iu > iv:
        iu, iv = iv, iu
        ru, rv = rv, ru
    d = (rv - ru) % 7
    return enc.var("b", iu, iv, d)


def build(n: int, use_card: bool = True) -> Enc:
    if n == 42:
        offset, norb = 0, 6
        deg_lo, deg_hi = 17, 24
    elif n == 43:
        offset, norb = 1, 6
        deg_lo, deg_hi = 18, 24
    elif n == 7:
        offset, norb = 0, 1
        deg_lo, deg_hi = 0, 6
    elif n == 14:
        offset, norb = 0, 2
        deg_lo, deg_hi = 0, 13
    else:
        raise ValueError(n)
    enc = Enc()
    if use_card and n == 43:
        # deg(0) = 7 * #a_i in [18,24] => exactly 3
        enc.card_eq([enc.var("a", i) for i in range(norb)], 3)
    if use_card and n in (42, 43):
        for i in range(norb):
            v0 = vid(offset, i, 0)
            others = [x for x in range(n) if x != v0]
            lits = [edge_var(enc, n, offset, norb, v0, w) for w in others]
            enc.card_between(lits, deg_lo, deg_hi)
    for comb in itertools.combinations(range(n), 5):
        evars = [edge_var(enc, n, offset, norb, x, y) for x, y in itertools.combinations(comb, 2)]
        enc.add([-v for v in evars])
        enc.add(list(evars))
    enc.n = n
    enc.offset = offset
    enc.norb = norb
    enc.nvars = enc.next - 1
    return enc


def decode(enc: Enc, model: list[int]) -> list[int]:
    pos = set(x for x in model if x > 0)
    n = enc.n
    nbr = [0] * n
    for u, v in itertools.combinations(range(n), 2):
        var = edge_var(enc, n, enc.offset, enc.norb, u, v)
        if var in pos:
            nbr[u] |= 1 << v
            nbr[v] |= 1 << u
    return nbr


def write_dimacs(enc: Enc, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"c C7-symmetric (5,5,{enc.n})\n")
        f.write(f"p cnf {enc.nvars} {len(enc.clauses)}\n")
        for cl in enc.clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")


def selftest() -> dict:
    """n=7: 3 distance bits, 8 circulants, encoder vs is_ramsey."""
    enc = build(7, use_card=False)
    from pysat.solvers import Cadical195

    sat_ok = []
    brute = []
    # brute the 8 assignments of w(0,1), w(0,2), w(0,3)
    keys = [("w", 0, 1), ("w", 0, 2), ("w", 0, 3)]
    ids = [enc.var(*k) for k in keys]
    for mask in range(8):
        assume = []
        for b, vid_ in enumerate(ids):
            assume.append(vid_ if (mask >> b) & 1 else -vid_)
        with Cadical195(bootstrap_with=enc.clauses) as s:
            sat = s.solve(assumptions=assume)
        # build graph from mask
        nbr = [0] * 7
        for u, v in itertools.combinations(range(7), 2):
            d = min((v - u) % 7, (u - v) % 7)
            if (mask >> (d - 1)) & 1:
                nbr[u] |= 1 << v
                nbr[v] |= 1 << u
        brute.append(is_ramsey(nbr))
        sat_ok.append(bool(sat))
    agree = sat_ok == brute
    return {
        "n": 7,
        "sat": sat_ok,
        "brute_55": brute,
        "agree": agree,
        "n_55": sum(brute),
    }


def solve(n: int, use_card: bool, tlim: int) -> dict:
    t0 = time.time()
    print(f"building n={n} card={use_card}", flush=True)
    enc = build(n, use_card=use_card)
    print(f"vars={enc.nvars} clauses={len(enc.clauses)} build_sec={time.time()-t0:.2f}", flush=True)
    from pysat.solvers import Cadical195

    s = Cadical195(bootstrap_with=enc.clauses)
    # Cadical has no portable time limit in this pysat; wrap with a budget of conflicts
    # and also a wall clock check via solving in one shot (caller uses `timeout`).
    t1 = time.time()
    sat = s.solve()
    model = s.get_model() if sat else None
    s.delete()
    rec = {
        "n": n,
        "use_card": use_card,
        "nvars": enc.nvars,
        "nclauses": len(enc.clauses),
        "status": "SAT" if sat else "UNSAT",
        "solve_sec": round(time.time() - t1, 3),
        "total_sec": round(time.time() - t0, 3),
        "time_limit_hint": tlim,
    }
    if sat and model:
        nbr = decode(enc, model)
        rec["ok_55"] = is_ramsey(nbr)
        rec["edges"] = n_edges(nbr)
        rec["nbr"] = nbr
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--no-card", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--cnf", type=str, default="")
    ap.add_argument("--time", type=int, default=180)
    args = ap.parse_args()
    outdir = Path(__file__).resolve().parent / "certs"
    outdir.mkdir(parents=True, exist_ok=True)
    if args.selftest:
        rec = selftest()
        dump_json(str(outdir / "c7_selftest.json"), rec)
        print(rec)
        return 0 if rec["agree"] else 1
    enc = build(args.n, use_card=not args.no_card)
    if args.cnf:
        dest = Path(args.cnf)
        write_dimacs(enc, dest)
        print(f"vars={enc.nvars} clauses={len(enc.clauses)} wrote {dest}")
    if args.solve:
        rec = solve(args.n, use_card=not args.no_card, tlim=args.time)
        # drop bitsets from json if present
        rec.pop("nbr", None)
        path = outdir / f"c7_n{args.n}.json"
        dump_json(str(path), rec)
        print(rec)
        print("wrote", path)
        return 0
    if not args.cnf:
        print(f"vars={enc.nvars} clauses={len(enc.clauses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
