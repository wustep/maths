#!/usr/bin/env python3
"""Test whether the full deg>=4 reserve can replace one original vertex.

For each listed original v, build (G - {v}) ∪ {all unused disk/ρ points of
unit-degree >= min_deg into G} and SAT-check 4-colorability.  If UNSAT,
some extras substitute for v and we then greedily drop extras.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

from lattice import generate_disk, rotate_rho
from udg import F, coloring_cnf, degrees, find_triangle, load_vtx, sqdist, unit_edges, write_vtx


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
    ap.add_argument("--min-deg", type=int, default=4)
    ap.add_argument("--which", type=int, nargs="*", default=None, help="original indices to drop")
    ap.add_argument("--first", type=int, default=6, help="if --which omitted, first k low-degree verts")
    ap.add_argument("--log", type=Path, default=Path("max_extras.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("max_extras_reduced.vtx"))
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    n0 = len(pts)
    edges = unit_edges(pts)
    deg = degrees(n0, edges)
    floats = [(p[0].to_float(), p[1].to_float()) for p in pts]
    have = set(pts)
    one = F.from_int(1)
    disk = [p for _, p in generate_disk(args.r_max)]
    seen = set(have)
    extras = []
    for p in disk:
        if p not in seen:
            seen.add(p)
            extras.append(p)
    for p in disk:
        q = rotate_rho(p)
        if q not in seen:
            seen.add(q)
            extras.append(q)
    kept = []
    for p in extras:
        xf, yf = p[0].to_float(), p[1].to_float()
        d = 0
        for i, (xi, yi) in enumerate(floats):
            dx, dy = xf - xi, yf - yi
            if abs(dx * dx + dy * dy - 1.0) < 1e-8 and sqdist(p, pts[i]) == one:
                d += 1
        if d >= args.min_deg:
            kept.append(p)
    print(f"reserve extras deg>={args.min_deg}: {len(kept)}", flush=True)

    if args.which is not None:
        targets = args.which
    else:
        targets = sorted(range(n0), key=lambda v: (deg[v], v))[: args.first]

    with args.log.open("w", encoding="utf-8") as logf:
        logf.write(json.dumps({"phase": "start", "n_extra": len(kept), "targets": targets}) + "\n")
        for v in targets:
            trial = [p for i, p in enumerate(pts) if i != v] + kept
            status, m, dt = solve_graph(trial)
            rec = {
                "phase": "max_swap",
                "v": v,
                "deg": deg[v],
                "n": len(trial),
                "m": m,
                "status": status,
                "seconds": dt,
            }
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            print(rec, flush=True)
            if status == "UNSAT":
                print("UNSAT with full reserve; trimming extras", flush=True)
                orig = set(trial[: n0 - 1])
                current = trial
                progressed = True
                while progressed:
                    progressed = False
                    # try dropping extras first
                    idxs = [i for i, p in enumerate(current) if p not in orig]
                    for i in idxs:
                        t2 = current[:i] + current[i + 1 :]
                        st, _, dt2 = solve_graph(t2)
                        if st == "UNSAT":
                            current = t2
                            progressed = True
                            print(f"  drop extra -> {len(current)} {dt2:.2f}s", flush=True)
                            break
                write_vtx(args.out, current)
                print(f"trimmed n={len(current)} (seed {n0})", flush=True)
                if len(current) < n0:
                    print(f"DENT n={len(current)}", flush=True)
                    break


if __name__ == "__main__":
    main()
