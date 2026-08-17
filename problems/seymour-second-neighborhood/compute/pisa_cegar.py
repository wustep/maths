#!/usr/bin/env python3
"""CEGAR SAT for Pisa-type existence.

The SAT model encodes an oriented graph with all margins <= 0 and
optional missing-degree constraints.  Strong connectivity is checked
outside the solver; a non-strong model is blocked by a nogood on the
pair-orientation bits and we iterate.

This is the right encoding for n=8 type-hunting: reachability inside
CP-SAT is n^4 and slow, while a BFS filter is free.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seymour import (
    encode_ternary,
    graph_signature,
    is_pisa,
    is_strongly_connected,
)


def _source_sccs(out: list[int]) -> list[set[int]]:
    """Tarjan SCCs that have no incoming arc from outside."""
    n = len(out)
    index = 0
    stack = []
    on = [False] * n
    idx = [-1] * n
    low = [0] * n
    comps = []

    def strongconnect(v):
        nonlocal index
        idx[v] = low[v] = index
        index += 1
        stack.append(v)
        on[v] = True
        m = out[v]
        while m:
            w = (m & -m).bit_length() - 1
            if idx[w] < 0:
                strongconnect(w)
                low[v] = min(low[v], low[w])
            elif on[w]:
                low[v] = min(low[v], idx[w])
            m &= m - 1
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stack.pop()
                on[w] = False
                comp.append(w)
                if w == v:
                    break
            comps.append(comp)

    for v in range(n):
        if idx[v] < 0:
            strongconnect(v)

    sources = []
    for comp in comps:
        S = set(comp)
        incoming = False
        for u in range(n):
            if u in S:
                continue
            if out[u] & sum(1 << v for v in S):
                incoming = True
                break
        if not incoming and len(S) < n:
            sources.append(S)
    return sources


def solve_pisa(
    n: int,
    miss_deg=None,
    require_not_matching: bool = False,
    irregular_missing: bool = False,
    min_out: int = 1,
    time_limit: float = 120.0,
    workers: int = 8,
    max_rounds: int = 200,
):
    model = cp_model.CpModel()
    pairs = list(combinations(range(n), 2))
    fwd, bwd, miss = {}, {}, {}
    for i, j in pairs:
        f = model.NewBoolVar(f"f_{i}_{j}")
        b = model.NewBoolVar(f"b_{i}_{j}")
        m = model.NewBoolVar(f"m_{i}_{j}")
        model.Add(f + b + m == 1)
        fwd[i, j], bwd[i, j], miss[i, j] = f, b, m

    def arc(u, v):
        return fwd[u, v] if u < v else bwd[v, u]

    def missing(u, v):
        return miss[min(u, v), max(u, v)]

    outdeg, mdeg = [], []
    for v in range(n):
        od = model.NewIntVar(0, n - 1, f"od_{v}")
        idg = model.NewIntVar(0, n - 1, f"id_{v}")
        md = model.NewIntVar(0, n - 1, f"md_{v}")
        model.Add(od == sum(arc(v, w) for w in range(n) if w != v))
        model.Add(idg == sum(arc(w, v) for w in range(n) if w != v))
        model.Add(md == sum(missing(v, w) for w in range(n) if w != v))
        model.Add(od >= min_out)
        model.Add(idg >= 1)
        outdeg.append(od)
        mdeg.append(md)

    if miss_deg is not None:
        c = Counter(miss_deg)
        for d, cnt in c.items():
            flags = []
            for v in range(n):
                eq = model.NewBoolVar(f"eq_{v}_{d}")
                model.Add(mdeg[v] == d).OnlyEnforceIf(eq)
                model.Add(mdeg[v] != d).OnlyEnforceIf(eq.Not())
                flags.append(eq)
            model.Add(sum(flags) == cnt)
        for v in range(n):
            model.AddAllowedAssignments([mdeg[v]], [[d] for d in c])

    if require_not_matching:
        flags = []
        for v in range(n):
            ge = model.NewBoolVar(f"ge2_{v}")
            model.Add(mdeg[v] >= 2).OnlyEnforceIf(ge)
            model.Add(mdeg[v] <= 1).OnlyEnforceIf(ge.Not())
            flags.append(ge)
        model.Add(sum(flags) >= 1)

    if irregular_missing:
        mn = model.NewIntVar(0, n - 1, "mdmin")
        mx = model.NewIntVar(0, n - 1, "mdmax")
        model.AddMinEquality(mn, mdeg)
        model.AddMaxEquality(mx, mdeg)
        model.Add(mn < mx)

    for v in range(n):
        secs = []
        for w in range(n):
            if w == v:
                continue
            s = model.NewBoolVar(f"s_{v}_{w}")
            model.Add(s + arc(v, w) <= 1)
            wits = []
            for u in range(n):
                if u == v or u == w:
                    continue
                b = model.NewBoolVar(f"w_{v}_{u}_{w}")
                model.Add(b <= arc(v, u))
                model.Add(b <= arc(u, w))
                model.Add(b >= arc(v, u) + arc(u, w) - 1)
                wits.append(b)
            if wits:
                model.Add(s <= sum(wits))
                for b in wits:
                    model.Add(s >= b - arc(v, w))
            else:
                model.Add(s == 0)
            secs.append(s)
        model.Add(sum(secs) <= outdeg[v])

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 17

    leftover = time_limit
    rounds = []
    for rnd in range(max_rounds):
        if leftover <= 0.05:
            return {"status": "UNKNOWN", "reason": "time", "rounds": rounds, "n": n}
        solver.parameters.max_time_in_seconds = leftover
        status = solver.Solve(model)
        used = solver.WallTime()
        leftover -= used
        name = solver.StatusName(status)
        rounds.append({"round": rnd, "status": name, "time": used,
                       "conflicts": solver.NumConflicts()})
        if status == cp_model.INFEASIBLE:
            return {
                "status": "INFEASIBLE",
                "n": n,
                "miss_deg": miss_deg,
                "require_not_matching": require_not_matching,
                "irregular_missing": irregular_missing,
                "rounds": rounds,
                "total_time": time_limit - leftover,
            }
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {"status": name, "n": n, "rounds": rounds}

        out = [0] * n
        lits_true = []
        lits_false = []
        for i, j in pairs:
            if solver.Value(fwd[i, j]):
                out[i] |= 1 << j
                lits_true.append(fwd[i, j])
            else:
                lits_false.append(fwd[i, j])
            if solver.Value(bwd[i, j]):
                out[j] |= 1 << i
                lits_true.append(bwd[i, j])
            else:
                lits_false.append(bwd[i, j])

        if is_strongly_connected(out):
            sig = graph_signature(out)
            if not is_pisa(out):
                raise RuntimeError(f"non-Pisa SAT model: {sig}")
            return {
                "status": "FEASIBLE",
                "n": n,
                "miss_deg": miss_deg,
                "witness": sig,
                "code": encode_ternary(out),
                "rounds": rounds,
                "total_time": time_limit - leftover,
            }

        # Source-component cut: some SCC has no incoming arcs from outside.
        # Force at least one such incoming arc (or an internal change that
        # merges the component).  This is much stronger than blocking the
        # whole orientation.
        sccs = _source_sccs(out)
        if not sccs:
            model.Add(sum(lits_false) + sum(1 - x for x in lits_true) >= 1)
        else:
            for S in sccs:
                incoming = []
                for u in range(n):
                    if u in S:
                        continue
                    for v in S:
                        incoming.append(arc(u, v))
                if incoming:
                    model.Add(sum(incoming) >= 1)
                else:
                    model.Add(sum(lits_false) + sum(1 - x for x in lits_true) >= 1)

    return {"status": "UNKNOWN", "reason": "max_rounds", "rounds": rounds, "n": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--miss-deg", type=str, default=None)
    ap.add_argument("--not-matching", action="store_true")
    ap.add_argument("--irregular-missing", action="store_true")
    ap.add_argument("--min-out", type=int, default=1)
    ap.add_argument("--time", type=float, default=90.0)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    miss = [int(x) for x in args.miss_deg.split(",")] if args.miss_deg else None
    rec = solve_pisa(
        args.n, miss, args.not_matching, args.irregular_missing,
        args.min_out, args.time,
    )
    text = json.dumps(rec, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n")


if __name__ == "__main__":
    main()
