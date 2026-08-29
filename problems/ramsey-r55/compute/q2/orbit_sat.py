#!/usr/bin/env python3
"""SAT for (5,5,n)-graphs invariant under a prime-order permutation.

The permutation has ``cycles`` p-cycles and ``fixed`` fixed vertices.  Clique
clauses are emitted once per orbit of 5-subsets, not once per labelled
5-subset.  This is logically equivalent to the raw encoding because all edge
variables are constant on permutation orbits.

For n=43 and p in {2,3,5,7}, ``--fixed-cycle-count k`` uses the freedom to
permute the p-cycles and makes fixed vertex 0 adjacent to the first k cycles.
The caller must run every degree-feasible k unless the degree window forces k.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import fingerprint, is_ramsey, to_graph6


class Enc:
    def __init__(self) -> None:
        self.clauses: list[list[int]] = []
        self.names: dict[tuple, int] = {}
        self.next_var = 1

    def var(self, *key: object) -> int:
        k = tuple(key)
        if k not in self.names:
            self.names[k] = self.next_var
            self.next_var += 1
        return self.names[k]

    def new(self) -> int:
        v = self.next_var
        self.next_var += 1
        return v

    def add(self, lits: list[int] | tuple[int, ...]) -> None:
        vals = set(lits)
        if any(-v in vals for v in vals):
            return
        self.clauses.append(sorted(vals, key=lambda x: (abs(x), x < 0)))

    def card_between(self, lits: list[int], lo: int, hi: int) -> None:
        """Sequential counter for lo <= sum(lits) <= hi.

        A literal may occur more than once; this gives it its integer weight.
        """
        m = len(lits)
        lo = max(0, lo)
        hi = min(m, hi)
        if lo > hi:
            self.add([])
            return
        if m == 0:
            return
        if hi == 0:
            for lit in lits:
                self.add([-lit])
            return
        # s[i][j] iff at least j+1 of inputs 0..i are true.  Column hi-1,
        # together with the next input, forbids a total of hi+1.  The earlier
        # q2 draft accidentally allocated one extra column and only enforced
        # an upper bound of hi+1; verify_encoder.py guards this boundary.
        s = [[self.new() for _ in range(hi)] for _ in range(m)]
        self.add([-lits[0], s[0][0]])
        self.add([lits[0], -s[0][0]])
        for j in range(1, hi):
            self.add([-s[0][j]])
        for i in range(1, m):
            self.add([-lits[i], s[i][0]])
            self.add([-s[i - 1][0], s[i][0]])
            self.add([lits[i], s[i - 1][0], -s[i][0]])
            for j in range(1, hi):
                self.add([-s[i - 1][j], s[i][j]])
                self.add([-lits[i], -s[i - 1][j - 1], s[i][j]])
                self.add([s[i - 1][j], lits[i], -s[i][j]])
                self.add([s[i - 1][j], s[i - 1][j - 1], -s[i][j]])
            self.add([-lits[i], -s[i - 1][hi - 1]])
        if lo:
            self.add([s[m - 1][lo - 1]])

    def lex_leq(self, left: list[int], right: list[int]) -> None:
        """Add a binary lexicographic left <= right constraint (0 < 1)."""
        if len(left) != len(right):
            raise ValueError("lex vectors have different lengths")
        prefix = self.new()
        self.add([prefix])
        for x, y in zip(left, right):
            # Equal prefix forbids the first difference 1 > 0.
            self.add([-prefix, -x, y])
            nxt = self.new()
            # nxt iff prefix and x == y.
            self.add([-nxt, prefix])
            self.add([-nxt, -x, y])
            self.add([-nxt, x, -y])
            self.add([-prefix, x, y, nxt])
            self.add([-prefix, -x, -y, nxt])
            prefix = nxt


class OrbitEncoding:
    def __init__(self, n: int, p: int, cycles: int | None = None) -> None:
        if p < 2 or n < p:
            raise ValueError((n, p))
        self.n = n
        self.p = p
        self.cycles = n // p if cycles is None else cycles
        if not 1 <= self.cycles <= n // p:
            raise ValueError((n, p, self.cycles))
        self.fixed = n - self.cycles * p
        self.enc = Enc()
        self.base_clause_keys: set[tuple[int, ...]] = set()
        self.subset_orbits = 0

    def cyc_vertex(self, orbit: int, r: int) -> int:
        return self.fixed + orbit * self.p + (r % self.p)

    def split_vertex(self, v: int) -> tuple[str, int, int]:
        if v < self.fixed:
            return ("f", v, 0)
        orbit, r = divmod(v - self.fixed, self.p)
        return ("c", orbit, r)

    def shift_vertex(self, v: int, t: int) -> int:
        kind, i, r = self.split_vertex(v)
        return v if kind == "f" else self.cyc_vertex(i, r + t)

    def edge_var(self, u: int, v: int) -> int:
        if u > v:
            u, v = v, u
        ku, iu, ru = self.split_vertex(u)
        kv, iv, rv = self.split_vertex(v)
        if ku == kv == "f":
            return self.enc.var("ff", iu, iv)
        if ku == "f" and kv == "c":
            return self.enc.var("fc", iu, iv)
        if ku == kv == "c" and iu == iv:
            d = (rv - ru) % self.p
            d = min(d, self.p - d)
            return self.enc.var("cc", iu, d)
        if ku == "c" and kv == "c":
            if iu > iv:
                iu, iv = iv, iu
                ru, rv = rv, ru
            d = (rv - ru) % self.p
            return self.enc.var("cb", iu, iv, d)
        raise AssertionError((u, v))

    def degree_lits(self, v: int) -> list[int]:
        # Listing all incident labelled edges automatically repeats an orbit
        # variable according to its contribution to the degree.
        return [self.edge_var(v, w) for w in range(self.n) if w != v]

    def add_base_clauses(self) -> None:
        for comb in itertools.combinations(range(self.n), 5):
            shifted = [
                tuple(sorted(self.shift_vertex(v, t) for v in comb))
                for t in range(self.p)
            ]
            if comb != min(shifted):
                continue
            self.subset_orbits += 1
            key = tuple(
                sorted(
                    {
                        self.edge_var(u, v)
                        for u, v in itertools.combinations(comb, 2)
                    }
                )
            )
            self.base_clause_keys.add(key)
        for key in sorted(self.base_clause_keys):
            self.enc.add([-v for v in key])
            self.enc.add(list(key))

    def add_degrees(self) -> None:
        lo, hi = max(0, self.n - 25), min(self.n - 1, 24)
        # One representative per vertex orbit is enough.
        for v in range(self.fixed):
            self.enc.card_between(self.degree_lits(v), lo, hi)
        for orbit in range(self.cycles):
            self.enc.card_between(self.degree_lits(self.cyc_vertex(orbit, 0)), lo, hi)

    def add_fixed_cycle_prefix(self, k: int) -> None:
        if self.fixed == 0:
            raise ValueError("no fixed vertex")
        if not 0 <= k <= self.cycles:
            raise ValueError(k)
        for orbit in range(self.cycles):
            lit = self.enc.var("fc", 0, orbit)
            self.enc.add([lit if orbit < k else -lit])

    def add_c7_symmetry_breaking(self) -> None:
        """Break cycle permutations and independent cycle phases for 1+6*7.

        The fixed vertex has already selected cycles 0,1,2.  The three selected
        cycles and three unselected cycles can each be permuted.  After choosing
        cycle 0 as a phase anchor, every other cycle can be rotated independently,
        so its seven cross-edge bits to cycle 0 may be made rotation-minimal.
        """
        if (self.n, self.p, self.fixed, self.cycles) != (43, 7, 1, 6):
            raise ValueError("C7 symmetry breaking is only for n=43")
        for block in ((0, 1, 2), (3, 4, 5)):
            for a, b in zip(block, block[1:]):
                wa = [self.enc.var("cc", a, d) for d in range(1, 4)]
                wb = [self.enc.var("cc", b, d) for d in range(1, 4)]
                self.enc.lex_leq(wa, wb)
        for j in range(1, 6):
            bits = [self.enc.var("cb", 0, j, d) for d in range(7)]
            for shift in range(1, 7):
                rotated = [bits[(d + shift) % 7] for d in range(7)]
                self.enc.lex_leq(bits, rotated)

    def add_p5_symmetry_breaking(self) -> None:
        """Break cycle permutations and phases for 3+8*5, after k=4."""
        if (self.n, self.p, self.fixed, self.cycles) != (43, 5, 3, 8):
            raise ValueError("C5 symmetry breaking is only for n=43")
        for block in ((0, 1, 2, 3), (4, 5, 6, 7)):
            for a, b in zip(block, block[1:]):
                wa = [self.enc.var("cc", a, d) for d in range(1, 3)]
                wb = [self.enc.var("cc", b, d) for d in range(1, 3)]
                self.enc.lex_leq(wa, wb)
        for j in range(1, 8):
            bits = [self.enc.var("cb", 0, j, d) for d in range(5)]
            for shift in range(1, 5):
                rotated = [bits[(d + shift) % 5] for d in range(5)]
                self.enc.lex_leq(bits, rotated)

    def add_anchor_symmetry_breaking(self, selected: int) -> None:
        """Generic cycle-permutation/phase breaking after a fixed prefix.

        Cycle 0 lies in the selected block.  Choose it to have minimum internal
        signature there, sort both blocks by that signature, and rotate every
        other cycle so its cross-edge word to cycle 0 is rotation-minimal.
        """
        if self.fixed == 0 or not 1 <= selected <= self.cycles:
            raise ValueError("anchor symmetry breaking needs a nonempty prefix")
        blocks = (tuple(range(selected)), tuple(range(selected, self.cycles)))
        ndist = self.p // 2
        for block in blocks:
            for a, b in zip(block, block[1:]):
                wa = [self.enc.var("cc", a, d) for d in range(1, ndist + 1)]
                wb = [self.enc.var("cc", b, d) for d in range(1, ndist + 1)]
                self.enc.lex_leq(wa, wb)
        for j in range(1, self.cycles):
            bits = [self.enc.var("cb", 0, j, d) for d in range(self.p)]
            for shift in range(1, self.p):
                rotated = [bits[(d + shift) % self.p] for d in range(self.p)]
                self.enc.lex_leq(bits, rotated)

    def build(
        self,
        use_degrees: bool,
        fixed_cycle_count: int | None,
        c7_symbreak: bool = False,
        p5_symbreak: bool = False,
        anchor_symbreak: bool = False,
    ) -> None:
        self.add_base_clauses()
        if use_degrees:
            self.add_degrees()
        if fixed_cycle_count is not None:
            self.add_fixed_cycle_prefix(fixed_cycle_count)
        if c7_symbreak:
            if fixed_cycle_count != 3:
                raise ValueError("C7 symmetry breaking requires --fixed-cycle-count 3")
            self.add_c7_symmetry_breaking()
        if p5_symbreak:
            if fixed_cycle_count != 4:
                raise ValueError("C5 symmetry breaking requires --fixed-cycle-count 4")
            self.add_p5_symmetry_breaking()
        if anchor_symbreak:
            if fixed_cycle_count is None:
                raise ValueError("anchor symmetry breaking needs --fixed-cycle-count")
            self.add_anchor_symmetry_breaking(fixed_cycle_count)

    def decode(self, model: list[int]) -> list[int]:
        positive = {v for v in model if v > 0}
        nbr = [0] * self.n
        for u, v in itertools.combinations(range(self.n), 2):
            if self.edge_var(u, v) in positive:
                nbr[u] |= 1 << v
                nbr[v] |= 1 << u
        return nbr


def write_dimacs(obj: OrbitEncoding, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(
            f"c R(5,5,{obj.n}), automorphism order {obj.p}, "
            f"cycles={obj.cycles}, fixed={obj.fixed}\n"
        )
        f.write(f"p cnf {obj.enc.next_var - 1} {len(obj.enc.clauses)}\n")
        for clause in obj.enc.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solve_with_pysat(obj: OrbitEncoding) -> tuple[str, list[int] | None, float]:
    from pysat.solvers import Cadical195

    t0 = time.time()
    with Cadical195(bootstrap_with=obj.enc.clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    return ("SAT" if sat else "UNSAT", model, time.time() - t0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=43)
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--cycles", type=int)
    ap.add_argument("--no-degrees", action="store_true")
    ap.add_argument("--fixed-cycle-count", type=int)
    ap.add_argument("--c7-symbreak", action="store_true")
    ap.add_argument("--p5-symbreak", action="store_true")
    ap.add_argument("--anchor-symbreak", action="store_true")
    ap.add_argument("--cnf", type=Path)
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--cert", type=Path)
    args = ap.parse_args()

    t0 = time.time()
    obj = OrbitEncoding(args.n, args.p, args.cycles)
    obj.build(
        not args.no_degrees,
        args.fixed_cycle_count,
        args.c7_symbreak,
        args.p5_symbreak,
        args.anchor_symbreak,
    )
    build_sec = time.time() - t0
    cnf_sha256 = None
    if args.cnf:
        cnf_sha256 = write_dimacs(obj, args.cnf)

    rec: dict[str, object] = {
        "n": args.n,
        "p": args.p,
        "cycles": obj.cycles,
        "fixed": obj.fixed,
        "fixed_cycle_count": args.fixed_cycle_count,
        "c7_symbreak": args.c7_symbreak,
        "p5_symbreak": args.p5_symbreak,
        "anchor_symbreak": args.anchor_symbreak,
        "degree_constraints": not args.no_degrees,
        "edge_orbit_vars": len(obj.enc.names),
        "nvars": obj.enc.next_var - 1,
        "nclauses": len(obj.enc.clauses),
        "five_subset_orbits": obj.subset_orbits,
        "distinct_base_clause_keys": len(obj.base_clause_keys),
        "build_sec": round(build_sec, 3),
    }
    if cnf_sha256:
        rec["cnf_sha256"] = cnf_sha256
    if args.solve:
        status, model, sec = solve_with_pysat(obj)
        rec["status"] = status
        rec["solve_sec"] = round(sec, 3)
        rec["solver"] = "PySAT Cadical195"
        if model:
            nbr = obj.decode(model)
            rec["verified_55"] = is_ramsey(nbr)
            rec["graph6"] = to_graph6(nbr)
            rec["fingerprint"] = fingerprint(nbr)
    if args.cert:
        args.cert.parent.mkdir(parents=True, exist_ok=True)
        args.cert.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, sort_keys=True), flush=True)
    if rec.get("status") == "SAT" and not rec.get("verified_55"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
