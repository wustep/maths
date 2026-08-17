#!/usr/bin/env python3
"""Replace one original vertex by unused lattice points that share its neighbours.

For each low-degree v, collect unused disk/ρ points adjacent (exact unit
distance) to at least --min-share neighbours of v.  Test whether
(G - {v}) ∪ those extras is still non-4-colorable, then trim extras.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

from pysat.solvers import Cadical195

from lattice import generate_disk, rotate_rho
from udg import F, coloring_cnf, find_triangle, load_vtx, sqdist, unit_edges, write_vtx


def solve_graph(pts):
    edges = unit_edges(pts)
    n = len(pts)
    tri = find_triangle(n, edges)
    _, clauses, _ = coloring_cnf(n, edges, triangle=tri)
    t0 = time.perf_counter()
    with Cadical195() as s:
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve()
    return ("SAT" if sat else "UNSAT"), len(edges), time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--r-max", type=float, default=2.55)
    ap.add_argument("--min-share", type=int, default=3)
    ap.add_argument("--max-v", type=int, default=80)
    ap.add_argument("--log", type=Path, default=Path("targeted_swap.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("targeted_reduced.vtx"))
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    n0 = len(pts)
    edges = unit_edges(pts)
    nbr = [set() for _ in range(n0)]
    for a, b in edges:
        nbr[a].add(b)
        nbr[b].add(a)
    floats = [(p[0].to_float(), p[1].to_float()) for p in pts]
    have = set(pts)
    one = F.from_int(1)

    disk = [p for _, p in generate_disk(args.r_max)]
    extras = []
    seen = set(have)
    for p in disk:
        if p not in seen:
            seen.add(p)
            extras.append(p)
    for p in disk:
        q = rotate_rho(p)
        if q not in seen:
            seen.add(q)
            extras.append(q)
    print(f"extras {len(extras)}", flush=True)

    # For each extra, exact neighbours in G (float prefilter)
    extra_nbrs = []
    for p in extras:
        xf, yf = p[0].to_float(), p[1].to_float()
        ns = []
        for i, (xi, yi) in enumerate(floats):
            dx, dy = xf - xi, yf - yi
            if abs(dx * dx + dy * dy - 1.0) < 1e-8 and sqdist(p, pts[i]) == one:
                ns.append(i)
        extra_nbrs.append(set(ns))

    # invert: neighbour-set -> extras that hit them
    by_vertex = defaultdict(list)
    for j, ns in enumerate(extra_nbrs):
        for i in ns:
            by_vertex[i].append(j)

    order = sorted(range(n0), key=lambda v: (len(nbr[v]), v))[: args.max_v]
    best = None
    with args.log.open("w", encoding="utf-8") as logf:
        for v in order:
            Nv = nbr[v]
            chosen = []
            for j, ns in enumerate(extra_nbrs):
                share = len(ns & Nv)
                if share >= args.min_share:
                    chosen.append((share, j))
            chosen.sort(reverse=True)
            extra_pts = [extras[j] for _, j in chosen]
            trial = [p for i, p in enumerate(pts) if i != v] + extra_pts
            if not extra_pts:
                rec = {"phase": "skip", "v": v, "deg": len(Nv), "n_extra": 0}
                logf.write(json.dumps(rec) + "\n")
                continue
            status, m, dt = solve_graph(trial)
            rec = {
                "phase": "swap",
                "v": v,
                "deg": len(Nv),
                "n_extra": len(extra_pts),
                "shares": [s for s, _ in chosen[:8]],
                "n": len(trial),
                "m": m,
                "status": status,
                "seconds": dt,
            }
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            print(rec, flush=True)
            if status == "UNSAT":
                # trim extras
                original_set = set(trial[: n0 - 1])
                current = trial
                progress = True
                while progress:
                    progress = False
                    for i, p in list(enumerate(current)):
                        if p in original_set:
                            continue
                        t2 = current[:i] + current[i + 1 :]
                        st, _, dt2 = solve_graph(t2)
                        if st == "UNSAT":
                            current = t2
                            progress = True
                            print(f"  trim extra -> {len(current)} {dt2:.2f}s", flush=True)
                            break
                rec2 = {"phase": "unsat_swap", "v": v, "n": len(current)}
                logf.write(json.dumps(rec2) + "\n")
                print(rec2, flush=True)
                if best is None or len(current) < best[0]:
                    best = (len(current), current, v)
                    write_vtx(args.out, current)
                    if len(current) < n0:
                        print(f"DENT n={len(current)}", flush=True)
                        break
        if best:
            print(f"best n={best[0]}", flush=True)
        else:
            print("no targeted swap stayed 5-chromatic", flush=True)


if __name__ == "__main__":
    main()
