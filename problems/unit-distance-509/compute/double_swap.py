#!/usr/bin/env python3
"""Search for one extra that replaces two original vertices.

Rebuilds the unit-distance graph of G once.  Each extra's exact neighbours
in G are computed once.  A trial (G-{v,w}) ∪ {e} is the original edge set
plus those extra edges, with v and w skipped in the SAT instance.

A hit is a dent: n = 507 + 1 = 508.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations
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


def _solve_skip(n, edges, skip, triangle):
    _, clauses, _ = coloring_cnf(n, edges, skip=set(skip), triangle=triangle)
    t0 = time.perf_counter()
    with Cadical195() as s:
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve()
    return ("SAT" if sat else "UNSAT"), time.perf_counter() - t0


def _job(payload):
    n, edges, skip, triangle, meta = payload
    status, dt = _solve_skip(n, edges, skip, triangle)
    return status, dt, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--r-max", type=float, default=2.55)
    ap.add_argument("--min-deg", type=int, default=6)
    ap.add_argument("--pair-deg", type=int, default=4)
    ap.add_argument("--require-adj", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--log", type=Path, default=Path("double_swap.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("double_swap.vtx"))
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    n0 = len(pts)
    edges0 = unit_edges(pts)
    deg = degrees(n0, edges0)
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
    scored = []
    for p in extras:
        xf, yf = p[0].to_float(), p[1].to_float()
        ns = []
        for i, (xi, yi) in enumerate(floats):
            dx, dy = xf - xi, yf - yi
            if abs(dx * dx + dy * dy - 1.0) < 1e-8 and sqdist(p, pts[i]) == one:
                ns.append(i)
        if len(ns) >= args.min_deg:
            scored.append((len(ns), p, ns))
    scored.sort(key=lambda t: -t[0])
    lows = [i for i in range(n0) if deg[i] <= args.pair_deg]
    pairs = list(combinations(lows, 2))
    print(f"extras {len(scored)} pairs {len(pairs)} lows {len(lows)}", flush=True)

    # triangle in G; if it uses a dropped vertex the encoder will ignore it
    tri = find_triangle(n0, edges0)
    jobs = []
    for ei, (d, extra, ns) in enumerate(scored):
        extra_edges = edges0 + [(i, n0) for i in ns]
        for v, w in pairs:
            if args.require_adj and not (v in ns and w in ns):
                continue
            jobs.append(
                (
                    n0 + 1,
                    extra_edges,
                    (v, w),
                    tri,
                    {"v": v, "w": w, "ei": ei, "extra_deg": d, "share": (v in ns) + (w in ns)},
                )
            )
    print(f"jobs {len(jobs)}", flush=True)

    hits = 0
    tested = 0
    with args.log.open("w", encoding="utf-8") as logf:
        logf.write(json.dumps({"phase": "start", "n_extra": len(scored), "n_pairs": len(pairs), "jobs": len(jobs)}) + "\n")
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_job, j): j[4] for j in jobs}
            for fut in as_completed(futs):
                status, dt, meta = fut.result()
                tested += 1
                rec = {**meta, "status": status, "seconds": dt}
                logf.write(json.dumps(rec) + "\n")
                if tested % 50 == 0:
                    logf.flush()
                    print(f"tested {tested}/{len(jobs)} hits {hits}", flush=True)
                if status == "UNSAT":
                    hits += 1
                    logf.flush()
                    print(f"HIT {rec}", flush=True)
                    v, w, ei = meta["v"], meta["w"], meta["ei"]
                    extra = scored[ei][1]
                    trial = [p for i, p in enumerate(pts) if i != v and i != w] + [extra]
                    write_vtx(args.out, trial)
                    print("DENT n=508", flush=True)
                    return
        print(f"done tested={tested} hits={hits}", flush=True)


if __name__ == "__main__":
    main()
