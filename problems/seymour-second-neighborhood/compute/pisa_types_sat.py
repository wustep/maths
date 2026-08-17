#!/usr/bin/env python3
"""SAT search for Pisa graphs with prescribed missing-degree type.

Existence (not enumeration) of a strongly connected oriented graph with
Delta == 0 and a given missing-degree sequence.  Used to classify which
complement types occur at n = 8, the first order Halkiewicz left open.

A witness is dumped as JSON and rechecked by seymour.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seymour import decode_ternary, encode_ternary, graph_signature, is_pisa


def pair_index(n: int, i: int, j: int) -> int:
    if i > j:
        i, j = j, i
    # lex pairs
    return i * n - i * (i + 1) // 2 + (j - i - 1)


def build_model(n: int, miss_deg: list[int] | None, require_not_matching: bool,
                require_min_out: int, force_irregular_missing: bool):
    """Boolean vars:
    fwd[i][j] = 1 means i->j for i<j;  bwd[i][j] = 1 means j->i.
    missing = 1 - fwd - bwd.
    """
    model = cp_model.CpModel()
    pairs = list(combinations(range(n), 2))
    fwd = {}
    bwd = {}
    miss = {}
    for i, j in pairs:
        f = model.NewBoolVar(f"f_{i}_{j}")
        b = model.NewBoolVar(f"b_{i}_{j}")
        m = model.NewBoolVar(f"m_{i}_{j}")
        model.Add(f + b + m == 1)
        fwd[i, j] = f
        bwd[i, j] = b
        miss[i, j] = m

    def arc(u, v):
        if u < v:
            return fwd[u, v]
        return bwd[v, u]

    def missing(u, v):
        if u > v:
            u, v = v, u
        return miss[u, v]

    # out/in degrees
    outdeg = []
    indeg = []
    for v in range(n):
        od = model.NewIntVar(0, n - 1, f"od_{v}")
        idg = model.NewIntVar(0, n - 1, f"id_{v}")
        model.Add(od == sum(arc(v, w) for w in range(n) if w != v))
        model.Add(idg == sum(arc(w, v) for w in range(n) if w != v))
        model.Add(od >= require_min_out)
        model.Add(idg >= 1)  # necessary for strong
        outdeg.append(od)
        indeg.append(idg)

    # missing degrees
    mdeg = []
    for v in range(n):
        md = model.NewIntVar(0, n - 1, f"md_{v}")
        model.Add(md == sum(missing(v, w) for w in range(n) if w != v))
        mdeg.append(md)
    if miss_deg is not None:
        # miss_deg is a multiset; assign via sorting network / bools
        # Use a permutation of the prescribed sequence.
        # Easier: force the sorted tuple by counting how many vertices have each degree.
        from collections import Counter
        c = Counter(miss_deg)
        for d, cnt in c.items():
            flags = []
            for v in range(n):
                eq = model.NewBoolVar(f"md_{v}_eq_{d}")
                model.Add(mdeg[v] == d).OnlyEnforceIf(eq)
                model.Add(mdeg[v] != d).OnlyEnforceIf(eq.Not())
                flags.append(eq)
            model.Add(sum(flags) == cnt)
        # no other degrees
        for v in range(n):
            model.AddAllowedAssignments([mdeg[v]], [[d] for d in c])

    if require_not_matching:
        # some missing-degree >= 2
        big = []
        for v in range(n):
            ge2 = model.NewBoolVar(f"mdge2_{v}")
            model.Add(mdeg[v] >= 2).OnlyEnforceIf(ge2)
            model.Add(mdeg[v] < 2).OnlyEnforceIf(ge2.Not())
            big.append(ge2)
        model.Add(sum(big) >= 1)
        # not the directed n-cycle (that has missing-deg all n-3, underlying 2-regular)
        # we still allow it; the caller can filter.

    if force_irregular_missing:
        # missing degree sequence not constant
        for v in range(1, n):
            # at least one differs from vertex 0 — not sufficient; use min != max
            pass
        mn = model.NewIntVar(0, n - 1, "mdmin")
        mx = model.NewIntVar(0, n - 1, "mdmax")
        model.AddMinEquality(mn, mdeg)
        model.AddMaxEquality(mx, mdeg)
        model.Add(mn < mx)

    # second-neighborhood indicators
    # sec[v][w] = 1 if w in N2+(v)
    sec = [[None] * n for _ in range(n)]
    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            s = model.NewBoolVar(f"s_{v}_{w}")
            sec[v][w] = s
            # cannot be a first-neighbour
            model.Add(s + arc(v, w) <= 1)
            # witnesses u
            wit = []
            for u in range(n):
                if u == v or u == w:
                    continue
                b = model.NewBoolVar(f"wit_{v}_{u}_{w}")
                # b <=> arc(v,u) & arc(u,w)
                model.Add(b <= arc(v, u))
                model.Add(b <= arc(u, w))
                model.Add(b >= arc(v, u) + arc(u, w) - 1)
                wit.append(b)
            # s <=> (not arc(v,w)) and (or wit)
            # If any wit and not first, s must be 1
            for b in wit:
                model.Add(s >= b - arc(v, w))
            # s <= or wit  (and already s <= 1-arc)
            if wit:
                model.Add(s <= sum(wit))
            else:
                model.Add(s == 0)

    # margins <= 0: sum_w sec[v][w] <= outdeg[v]
    for v in range(n):
        model.Add(sum(sec[v][w] for w in range(n) if w != v) <= outdeg[v])

    # Strong connectivity via reachability bools r[k][v][w] = reach in <=k steps
    # k up to n-1.  A bit heavy (n^3) but n=8 is 512.
    r = [[[None] * n for _ in range(n)] for _ in range(n)]
    for v in range(n):
        for w in range(n):
            r0 = model.NewBoolVar(f"r0_{v}_{w}")
            if v == w:
                model.Add(r0 == 1)
            else:
                model.Add(r0 == arc(v, w))
            r[0][v][w] = r0
    for k in range(1, n):
        for v in range(n):
            for w in range(n):
                rk = model.NewBoolVar(f"r{k}_{v}_{w}")
                # rk <=> r[k-1][v][w] or exists u: r[k-1][v][u] & arc(u,w)
                opts = [r[k - 1][v][w]]
                for u in range(n):
                    if u == v:
                        continue
                    b = model.NewBoolVar(f"rp_{k}_{v}_{u}_{w}")
                    model.Add(b <= r[k - 1][v][u])
                    model.Add(b <= arc(u, w))
                    model.Add(b >= r[k - 1][v][u] + arc(u, w) - 1)
                    opts.append(b)
                model.Add(rk <= sum(opts))
                for o in opts:
                    model.Add(rk >= o)
                r[k][v][w] = rk
    for v in range(n):
        for w in range(n):
            model.Add(r[n - 1][v][w] == 1)

    return model, fwd, bwd, miss, pairs


def extract(n, solver, fwd, bwd) -> list[int]:
    out = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if solver.Value(fwd[i, j]):
                out[i] |= 1 << j
            elif solver.Value(bwd[i, j]):
                out[j] |= 1 << i
    return out


def solve_one(n: int, miss_deg=None, require_not_matching=False,
              require_min_out=1, force_irregular_missing=False,
              time_limit=60.0, workers=8):
    model, fwd, bwd, miss, pairs = build_model(
        n, miss_deg, require_not_matching, require_min_out, force_irregular_missing
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 17
    status = solver.Solve(model)
    name = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": name, "n": n, "miss_deg": miss_deg}
    out = extract(n, solver, fwd, bwd)
    sig = graph_signature(out)
    if not is_pisa(out):
        raise RuntimeError(f"solver returned non-Pisa graph: {sig}")
    return {
        "status": name,
        "n": n,
        "miss_deg": miss_deg,
        "witness": sig,
        "code": encode_ternary(out),
        "solve_time": solver.WallTime(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--miss-deg", type=str, default=None,
                    help="comma-separated missing degrees, e.g. 3,3,3,3,3,3,3,3")
    ap.add_argument("--not-matching", action="store_true")
    ap.add_argument("--irregular-missing", action="store_true")
    ap.add_argument("--min-out", type=int, default=1)
    ap.add_argument("--time", type=float, default=60.0)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    miss = None
    if args.miss_deg:
        miss = [int(x) for x in args.miss_deg.split(",")]
        if len(miss) != args.n:
            raise SystemExit("miss-deg length must equal n")
    result = solve_one(
        args.n, miss, args.not_matching, args.min_out,
        args.irregular_missing, args.time,
    )
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n")


if __name__ == "__main__":
    main()
