#!/usr/bin/env python3
"""Try to replace original vertices by unused lattice / ρ points.

G itself is already non-4-colorable, so G ∪ extras reduces back to G by
deleting the extras.  A smaller graph has to *swap*: drop one or more
original vertices and keep some extras so that the new set is still
non-4-colorable and ends up with n < 509 after extras are trimmed.

All extras are exact points of Parts' (a,b,c,d)/12 lattice or ρ of those.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
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


def collect_extras(pts, r_max: float, top_k: int, min_deg: int):
    have = set(pts)
    floats = [(p[0].to_float(), p[1].to_float()) for p in pts]
    disk = [p for _, p in generate_disk(r_max)]
    seen = set(have)
    cands = []
    for p in disk:
        if p not in seen:
            seen.add(p)
            cands.append(p)
    for p in disk:
        q = rotate_rho(p)
        if q not in seen:
            seen.add(q)
            cands.append(q)
    one = F.from_int(1)
    scored = []
    for p in cands:
        xf, yf = p[0].to_float(), p[1].to_float()
        deg = 0
        for i, (xi, yi) in enumerate(floats):
            dx, dy = xf - xi, yf - yi
            if abs(dx * dx + dy * dy - 1.0) < 1e-8 and sqdist(p, pts[i]) == one:
                deg += 1
        if deg >= min_deg:
            scored.append((deg, p))
    scored.sort(key=lambda t: -t[0])
    return scored[:top_k]


def _one_swap(payload):
    """payload: (pts_minus_v_plus_extras as serializable? too big)

    We pass (drop_indices, extra_pts) and the seed path is global via rebuild.
    Simpler: pass nothing heavy — caller runs sequentially for swaps, pool only
    for inner greedy.  Here a single solve of a given point list.
    """
    raise NotImplementedError


def trim_extras(pts, n_original: int, logf) -> list:
    """Delete vertices while UNSAT; prefer extras (indices >= n_original)."""
    current = list(pts)
    # map extras to the tail; after deletions we just prefer high index... 
    # Re-identify extras as points not in the original prefix snapshot.
    original_set = set(pts[:n_original])

    changed = True
    while changed:
        changed = False
        edges = unit_edges(current)
        n = len(current)
        deg = degrees(n, edges)
        tri = find_triangle(n, edges)
        # try extras first (not in original_set), low degree first
        order = sorted(
            range(n),
            key=lambda v: (0 if current[v] not in original_set else 1, deg[v], v),
        )
        for v in order:
            trial = [p for i, p in enumerate(current) if i != v]
            status, m, dt = solve_graph(trial)
            rec = {
                "phase": "trim",
                "n": n,
                "try_n": n - 1,
                "status": status,
                "seconds": dt,
                "dropped_extra": current[v] not in original_set,
            }
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            if status == "UNSAT":
                current = trial
                changed = True
                print(f"  trim -> {n-1} ({'extra' if rec['dropped_extra'] else 'orig'}) {dt:.2f}s", flush=True)
                break
    return current


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--top-k", type=int, default=12)
    ap.add_argument("--r-max", type=float, default=2.55)
    ap.add_argument("--min-deg", type=int, default=8)
    ap.add_argument("--max-drop", type=int, default=1, help="original vertices dropped per swap")
    ap.add_argument("--limit-drop-candidates", type=int, default=40)
    ap.add_argument("--log", type=Path, default=Path("expand_reduce.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("reduced.vtx"))
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    n0 = len(pts)
    extras_scored = collect_extras(pts, args.r_max, args.top_k, args.min_deg)
    extras = [p for _, p in extras_scored]
    print(
        f"seed n={n0} extras={len(extras)} degs={[d for d,_ in extras_scored]}",
        flush=True,
    )

    # original vertices, low degree first
    edges0 = unit_edges(pts)
    deg0 = degrees(n0, edges0)
    drop_order = sorted(range(n0), key=lambda v: (deg0[v], v))[: args.limit_drop_candidates]

    best = None
    with args.log.open("w", encoding="utf-8") as logf:
        logf.write(
            json.dumps(
                {
                    "phase": "start",
                    "n_seed": n0,
                    "n_extra": len(extras),
                    "extra_degs": [d for d, _ in extras_scored],
                }
            )
            + "\n"
        )
        # Single-original swaps: (G - {v}) ∪ extras
        for v in drop_order:
            trial = [p for i, p in enumerate(pts) if i != v] + extras
            status, m, dt = solve_graph(trial)
            rec = {
                "phase": "swap1",
                "dropped": v,
                "drop_deg": deg0[v],
                "n": len(trial),
                "m": m,
                "status": status,
                "seconds": dt,
            }
            logf.write(json.dumps(rec) + "\n")
            logf.flush()
            print(rec, flush=True)
            if status == "UNSAT":
                print(f"swap of v={v} is UNSAT; trimming extras", flush=True)
                # n_original in trial is n0-1 (all remaining originals sit in prefix)
                trimmed = trim_extras(trial, n_original=n0 - 1, logf=logf)
                rec2 = {"phase": "trimmed", "dropped": v, "n": len(trimmed)}
                logf.write(json.dumps(rec2) + "\n")
                logf.flush()
                print(rec2, flush=True)
                if best is None or len(trimmed) < best[0]:
                    best = (len(trimmed), trimmed, v)
                    write_vtx(args.out, trimmed)
                    if len(trimmed) < n0:
                        print(f"DENT n={len(trimmed)}", flush=True)
                        break

        if best is None:
            print("no single-original swap stayed 5-chromatic", flush=True)
        else:
            print(f"best n={best[0]} after dropping original {best[2]}", flush=True)

    if best:
        Path(str(args.log) + ".summary.json").write_text(
            json.dumps({"best_n": best[0], "dropped": best[2], "seed_n": n0}, indent=2) + "\n"
        )


if __name__ == "__main__":
    main()
