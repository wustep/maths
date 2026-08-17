#!/usr/bin/env python3
"""Search for a Seymour-counterexample in the Brukhman equality layer.

At n = 2*delta + 3, Brukhman's n = 2*delta + 2 argument no longer
contradicts.  The extremal Eulerian case is: every out/in-degree equals
delta, so the missing graph is 2-regular (a 2-factor).

We ask CP-SAT whether there is an oriented graph with
    n = 2*delta + 3,
    d^+(v) = d^-(v) = delta for all v,     (or just d^+ = delta)
    |N2^+(v)| <= delta - 1 for all v.
UNSAT is a machine-checked proof that every such graph has a Seymour
vertex.  A SAT model is a counterexample certificate.

Independently rechecked by seymour.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seymour import all_margins, encode_ternary, graph_signature, outdegrees


def solve(delta: int, eulerian: bool = True, time_limit: float = 120.0,
          workers: int = 8, seed: int = 17):
    n = 2 * delta + 3
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

    outdeg = []
    indeg = []
    for v in range(n):
        od = model.NewIntVar(0, n - 1, f"od_{v}")
        idg = model.NewIntVar(0, n - 1, f"id_{v}")
        model.Add(od == sum(arc(v, w) for w in range(n) if w != v))
        model.Add(idg == sum(arc(w, v) for w in range(n) if w != v))
        model.Add(od == delta)
        if eulerian:
            model.Add(idg == delta)
        outdeg.append(od)
        indeg.append(idg)

    # N2 indicators and |N2| <= delta-1
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
        model.Add(sum(secs) <= delta - 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    status = solver.Solve(model)
    rec = {
        "delta": delta,
        "n": n,
        "eulerian": eulerian,
        "status": solver.StatusName(status),
        "solve_time": solver.WallTime(),
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        out = [0] * n
        for i, j in pairs:
            if solver.Value(fwd[i, j]):
                out[i] |= 1 << j
            elif solver.Value(bwd[i, j]):
                out[j] |= 1 << i
        sig = graph_signature(out)
        rec["witness"] = sig
        rec["code"] = encode_ternary(out)
        rec["margins"] = all_margins(out)
        rec["outdegrees"] = outdegrees(out)
        if max(all_margins(out)) >= 0:
            rec["error"] = "model claimed counterexample but verifier found a Seymour vertex"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=int, required=True)
    ap.add_argument("--not-eulerian", action="store_true")
    ap.add_argument("--time", type=float, default=180.0)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    rec = solve(args.delta, eulerian=not args.not_eulerian, time_limit=args.time)
    text = json.dumps(rec, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n")


if __name__ == "__main__":
    main()
