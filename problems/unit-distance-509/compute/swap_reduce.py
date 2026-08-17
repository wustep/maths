#!/usr/bin/env python3
"""Replace an original vertex by a reduced extra-set, then try a second deletion.

Pipeline
  1. Confirm (G-v) ∪ R is UNSAT, R = unused lattice/ρ points of degree ≥ min_deg.
  2. Binary-chunk reduce R to a small extra set E that still witnesses UNSAT.
  3. Scan single deletions of remaining original vertices in (G-v) ∪ E.
     If some w can go, the surviving graph has size 507+|E|.  A dent needs
     507+|E| < 509, i.e. |E| ≤ 1 after a second deletion, or |E|=0 which is
     impossible by vertex-criticality.

Coordinates in R come only from Parts' lattice and ρ.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

from lattice import generate_disk, rotate_rho
from udg import (
    F,
    coloring_cnf,
    degrees,
    find_triangle,
    load_vtx,
    sqdist,
    unit_edges,
    write_vtx,
)


def solve_graph(pts) -> tuple[str, int, float]:
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


def collect_reserve(pts, r_max: float, min_deg: int):
    have = set(pts)
    floats = [(p[0].to_float(), p[1].to_float()) for p in pts]
    disk = [p for _, p in generate_disk(r_max)]
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
    one = F.from_int(1)
    kept = []
    for p in extras:
        xf, yf = p[0].to_float(), p[1].to_float()
        d = 0
        for i, (xi, yi) in enumerate(floats):
            dx, dy = xf - xi, yf - yi
            if abs(dx * dx + dy * dy - 1.0) < 1e-8 and sqdist(p, pts[i]) == one:
                d += 1
        if d >= min_deg:
            kept.append(p)
    return kept


def reduce_extras(base, extras, logf) -> list:
    """Binary-chunk reduce extras while (base ∪ extras) stays UNSAT."""
    E = list(extras)
    status, m, dt = solve_graph(base + E)
    logf.write(json.dumps({"phase": "reduce_start", "n_extra": len(E), "status": status, "m": m, "seconds": dt}) + "\n")
    logf.flush()
    print(f"reduce start extras={len(E)} {status} {dt:.2f}s", flush=True)
    if status != "UNSAT":
        return E
    chunk = max(1, len(E) // 2)
    while chunk >= 1:
        i = 0
        while i + chunk <= len(E):
            trial = E[:i] + E[i + chunk :]
            status, m, dt = solve_graph(base + trial)
            rec = {
                "phase": "chunk",
                "chunk": chunk,
                "i": i,
                "n_extra": len(E),
                "try_extra": len(trial),
                "status": status,
                "seconds": dt,
            }
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            print(rec, flush=True)
            if status == "UNSAT":
                E = trial
            else:
                i += chunk
        chunk = chunk // 2
    return E


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--r-max", type=float, default=2.55)
    ap.add_argument("--min-deg", type=int, default=4)
    ap.add_argument("--v", type=int, nargs="*", default=None)
    ap.add_argument("--first", type=int, default=6)
    ap.add_argument("--second-scan", action="store_true")
    ap.add_argument("--log", type=Path, default=Path("swap_reduce.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("swap_reduced.vtx"))
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    n0 = len(pts)
    deg = degrees(n0, unit_edges(pts))
    reserve = collect_reserve(pts, args.r_max, args.min_deg)
    print(f"n0={n0} reserve={len(reserve)}", flush=True)
    targets = args.v if args.v is not None else sorted(range(n0), key=lambda i: (deg[i], i))[: args.first]

    best = None
    with args.log.open("w", encoding="utf-8") as logf:
        logf.write(json.dumps({"phase": "start", "n0": n0, "reserve": len(reserve), "targets": targets}) + "\n")
        for v in targets:
            base = [p for i, p in enumerate(pts) if i != v]
            status, m, dt = solve_graph(base + reserve)
            rec = {"phase": "full_reserve", "v": v, "deg": deg[v], "n": n0 - 1 + len(reserve), "m": m, "status": status, "seconds": dt}
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            print(rec, flush=True)
            if status != "UNSAT":
                continue
            E = reduce_extras(base, reserve, logf)
            rec = {"phase": "extras_reduced", "v": v, "n_extra": len(E), "n": n0 - 1 + len(E)}
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            print(rec, flush=True)
            graph = base + E
            write_vtx(args.out.with_name(f"swap_v{v}_e{len(E)}.vtx"), graph)
            if best is None or len(graph) < best[0]:
                best = (len(graph), graph, v, E)
                write_vtx(args.out, graph)
            if args.second_scan and E:
                # try deleting another original
                n_base = n0 - 1
                for w in range(n_base):
                    trial = [p for i, p in enumerate(graph) if i != w]
                    st, m2, dt2 = solve_graph(trial)
                    rec = {"phase": "second_delete", "v": v, "w_in_base": w, "n": len(trial), "status": st, "seconds": dt2}
                    logf.write(json.dumps(rec) + "\n")
                    logf.flush()
                    if st == "UNSAT":
                        print(f"SECOND DELETE w={w} n={len(trial)} extras={len(E)}", flush=True)
                        write_vtx(args.out.with_name(f"dent_v{v}_w{w}.vtx"), trial)
                        if len(trial) < n0:
                            print(f"DENT n={len(trial)}", flush=True)
                            write_vtx(args.out, trial)
                            return
                print(f"no second original deletion for v={v} with |E|={len(E)}", flush=True)
    if best:
        print(f"best replacement n={best[0]} (dropped v={best[2]}, |E|={len(best[3])})", flush=True)
    else:
        print("no replaceable target with this reserve", flush=True)


if __name__ == "__main__":
    main()
