#!/usr/bin/env python3
"""Show that none of the 656 known (5,5,42)-graphs extend by one vertex.

A new vertex v with neighbourhood S subset V(G) yields a (5,5,43)-graph iff
  * 18 <= |S| <= 24
  * S contains no K4 of G          (else v+K4 is a K5)
  * V\\S contains no independent 4-set of G  (else that set plus v is an alpha-5)

This is a 42-variable SAT instance per graph. We solve it by DPLL with the
K4 / independent-4 unit-propagation rules, and write a compact per-graph
trace (decision count, conflict count, runtime). Replay is: run this file.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from r55lib import complement, dump_json, list_k_cliques, parse_graph6

ROOT = Path(__file__).resolve().parent
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = ROOT / "certs" / "mckay42_nonextend.json"

# For n=43: deg in [43-25, 24] = [18, 24]
DEG_LO, DEG_HI = 18, 24


class DPLL:
    """3-state SAT on bits 0..n-1. 0=false, 1=true, -1=undef."""

    def __init__(self, n: int, forbid_all: list[int], hit_any: list[int], lo: int, hi: int):
        self.n = n
        self.forbid_all = forbid_all  # bitmasks that cannot be contained in S
        self.hit_any = hit_any  # bitmasks that must meet S
        self.lo = lo
        self.hi = hi
        self.assign = [-1] * n
        self.decisions = 0
        self.conflicts = 0
        self.nodes = 0
        self.sat = False
        self.model = None

    def _propagate(self) -> bool:
        """Unit-propagate. Return False on conflict."""
        changed = True
        while changed:
            changed = False
            ones = 0
            zeros = 0
            undefs = []
            for i, a in enumerate(self.assign):
                if a == 1:
                    ones += 1
                elif a == 0:
                    zeros += 1
                else:
                    undefs.append(i)
            if ones > self.hi:
                return False
            if zeros > self.n - self.lo:
                return False
            # cardinality units
            if ones == self.hi:
                for i in undefs:
                    self.assign[i] = 0
                    changed = True
                if changed:
                    continue
            if zeros == self.n - self.lo:
                for i in undefs:
                    self.assign[i] = 1
                    changed = True
                if changed:
                    continue
            # K4: if 3 verts already in S, 4th must be out
            for mask in self.forbid_all:
                in_s = 0
                last_undef = -1
                n_undef = 0
                m = mask
                conflict = False
                while m:
                    b = m & -m
                    v = b.bit_length() - 1
                    a = self.assign[v]
                    if a == 1:
                        in_s += 1
                    elif a == -1:
                        n_undef += 1
                        last_undef = v
                    m ^= b
                if in_s == 4:
                    return False
                if in_s == 3 and n_undef == 1:
                    if self.assign[last_undef] == 1:
                        return False
                    if self.assign[last_undef] == -1:
                        self.assign[last_undef] = 0
                        changed = True
            # independent 4: if 3 verts already out, 4th must be in
            for mask in self.hit_any:
                out_s = 0
                last_undef = -1
                n_undef = 0
                m = mask
                while m:
                    b = m & -m
                    v = b.bit_length() - 1
                    a = self.assign[v]
                    if a == 0:
                        out_s += 1
                    elif a == -1:
                        n_undef += 1
                        last_undef = v
                    m ^= b
                if out_s == 4:
                    return False
                if out_s == 3 and n_undef == 1:
                    if self.assign[last_undef] == 0:
                        return False
                    if self.assign[last_undef] == -1:
                        self.assign[last_undef] = 1
                        changed = True
        return True

    def solve(self) -> bool:
        def rec() -> bool:
            self.nodes += 1
            if not self._propagate():
                self.conflicts += 1
                return False
            undefs = [i for i, a in enumerate(self.assign) if a == -1]
            if not undefs:
                ones = sum(1 for a in self.assign if a == 1)
                if self.lo <= ones <= self.hi:
                    self.sat = True
                    self.model = list(self.assign)
                    return True
                self.conflicts += 1
                return False
            # branch on a vertex appearing in the most unfinished constraints
            v = max(undefs, key=lambda i: self._score(i))
            for val in (1, 0):
                snap = list(self.assign)
                self.decisions += 1
                self.assign[v] = val
                if rec():
                    return True
                self.assign = snap
            return False

        return rec()

    def _score(self, v: int) -> int:
        bit = 1 << v
        s = 0
        for mask in self.forbid_all:
            if mask & bit:
                s += 1
        for mask in self.hit_any:
            if mask & bit:
                s += 1
        return s


def check_one(nbr: list[int]) -> dict:
    t0 = time.time()
    k4s = list_k_cliques(nbr, 4)
    i4s = list_k_cliques(complement(nbr), 4)
    solver = DPLL(len(nbr), k4s, i4s, DEG_LO, DEG_HI)
    sat = solver.solve()
    return {
        "n_k4": len(k4s),
        "n_ind4": len(i4s),
        "sat": sat,
        "decisions": solver.decisions,
        "conflicts": solver.conflicts,
        "nodes": solver.nodes,
        "seconds": round(time.time() - t0, 4),
        "model_ones": None if not sat else solver.model.count(1),
    }


def main() -> int:
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    results = []
    any_sat = False
    t0 = time.time()
    # Check each stored graph and its complement (656 graphs).
    for side, mapper in (("stored", lambda n: n), ("complement", complement)):
        for i, line in enumerate(lines):
            n, nbr = parse_graph6(line)
            nbr = mapper(nbr)
            rec = check_one(nbr)
            rec["i"] = i
            rec["side"] = side
            results.append(rec)
            if rec["sat"]:
                any_sat = True
                print("SAT", rec, flush=True)
            if (len(results) % 20) == 0:
                print(
                    f"progress {len(results)}/656 last_k4={rec['n_k4']} "
                    f"ind4={rec['n_ind4']} dec={rec['decisions']} "
                    f"sec={rec['seconds']}",
                    flush=True,
                )
    summary = {
        "n_graphs": len(results),
        "any_extension": any_sat,
        "total_seconds": round(time.time() - t0, 3),
        "k4_range": [min(r["n_k4"] for r in results), max(r["n_k4"] for r in results)],
        "ind4_range": [min(r["n_ind4"] for r in results), max(r["n_ind4"] for r in results)],
        "results": results,
    }
    dump_json(str(OUT), summary)
    print(
        f"graphs={len(results)} any_extension={any_sat} "
        f"sec={summary['total_seconds']} wrote {OUT}"
    )
    return 1 if any_sat else 0


if __name__ == "__main__":
    sys.exit(main())
