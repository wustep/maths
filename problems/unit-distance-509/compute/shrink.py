#!/usr/bin/env python3
"""Shrink a 5-chromatic unit-distance graph by SAT cores and deletions.

Replayable: every SAT call is logged to JSONL.  The graph is rebuilt from the
.vtx file with exact arithmetic; this script does not invent coordinates.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from pysat.solvers import Cadical195

from udg import coloring_cnf, degrees, find_triangle, load_vtx, unit_edges


def _solve_skip(payload: tuple) -> dict:
    n, edges, skip, triangle, timeout_note = payload
    skip_set = set(skip)
    _, clauses, _ = coloring_cnf(n, edges, skip=skip_set, triangle=triangle)
    t0 = time.perf_counter()
    with Cadical195() as s:
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve()
    dt = time.perf_counter() - t0
    return {
        "skip": list(skip),
        "status": "SAT" if sat else "UNSAT",
        "seconds": dt,
        "note": timeout_note,
    }


def extract_core(n, edges) -> tuple[list[int], float]:
    _, clauses, meta = coloring_cnf(n, edges, triangle=None, vertex_selectors=True)
    sel_base = meta["sel_base"]
    assumps = [sel_base + v + 1 for v in range(n)]
    t0 = time.perf_counter()
    with Cadical195() as s:
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve(assumptions=assumps)
        if sat:
            raise RuntimeError("4-colorable; no core")
        core_lits = s.get_core() or []
    dt = time.perf_counter() - t0
    core_set = set(core_lits)
    core = [v for v in range(n) if (sel_base + v + 1) in core_set]
    return core, dt


def write_sub_vtx(src: Path, dst: Path, keep: list[int]) -> None:
    lines = [ln for ln in src.read_text().splitlines() if ln.strip()]
    keep_set = set(keep)
    out = [lines[i] for i in range(len(lines)) if i in keep_set]
    dst.write_text("\n".join(out) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--log", type=Path, default=Path("shrink.jsonl"))
    ap.add_argument("--summary", type=Path, default=Path("shrink_summary.json"))
    ap.add_argument("--core-out", type=Path, default=None)
    ap.add_argument("--skip-singles", action="store_true")
    ap.add_argument("--skip-core", action="store_true")
    ap.add_argument("--only-degrees", type=int, nargs="*", default=None)
    args = ap.parse_args()

    t_all = time.perf_counter()
    pts = load_vtx(args.vtx)
    edges = unit_edges(pts)
    n = len(pts)
    deg = degrees(n, edges)
    tri = find_triangle(n, edges)
    print(f"loaded n={n} m={len(edges)} triangle={tri} mindeg={min(deg)} maxdeg={max(deg)}")

    logf = args.log.open("w", encoding="utf-8")

    def log(rec: dict) -> None:
        logf.write(json.dumps(rec) + "\n")
        logf.flush()
        print(rec)

    # Baseline
    base = _solve_skip((n, edges, [], tri, "baseline"))
    log({"phase": "baseline", **base})
    if base["status"] != "UNSAT":
        raise SystemExit("published graph is 4-colorable — this would refute it")

    smaller = None
    core = list(range(n))
    if not args.skip_core:
        core, dt = extract_core(n, edges)
        log({"phase": "vertex_core", "core_size": len(core), "seconds": dt, "core": core})
        if args.core_out and len(core) < n:
            write_sub_vtx(args.vtx, args.core_out, core)
            print(f"wrote smaller vtx {args.core_out} n={len(core)}")
        if len(core) < n:
            smaller = {"kind": "assumption_core", "n": len(core), "keep": core}

    # Single deletions
    if not args.skip_singles:
        candidates = list(range(n))
        if args.only_degrees is not None:
            allowed = set(args.only_degrees)
            candidates = [v for v in candidates if deg[v] in allowed]
        # Prefer low degree first (more likely deletable)
        candidates.sort(key=lambda v: (deg[v], v))
        print(f"single-deletion candidates: {len(candidates)}")
        payload = []
        for v in candidates:
            payload.append((n, edges, [v], tri, f"deg={deg[v]}"))
        n_sat = n_unsat = 0
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_solve_skip, p): p[2][0] for p in payload}
            for fut in as_completed(futs):
                v = futs[fut]
                rec = fut.result()
                rec["phase"] = "single_delete"
                rec["degree"] = deg[v]
                log(rec)
                if rec["status"] == "UNSAT":
                    n_unsat += 1
                    if smaller is None or rec.get("skip") and n - 1 < smaller["n"]:
                        keep = [i for i in range(n) if i != v]
                        smaller = {"kind": "single_delete", "n": n - 1, "deleted": v, "keep": keep}
                else:
                    n_sat += 1
        log({"phase": "single_delete_tally", "SAT": n_sat, "UNSAT": n_unsat})

    summary = {
        "vtx": str(args.vtx),
        "n": n,
        "m": len(edges),
        "core_size": len(core),
        "smaller": None
        if smaller is None
        else {k: smaller[k] for k in smaller if k != "keep"},
        "elapsed_seconds": time.perf_counter() - t_all,
    }
    if smaller is not None:
        keep = smaller["keep"]
        out = args.vtx.with_name(f"smaller_{smaller['n']}.vtx")
        write_sub_vtx(args.vtx, out, keep)
        summary["smaller_vtx"] = str(out)
        print(f"SMALLER GRAPH n={smaller['n']} -> {out}")
    else:
        print("no smaller subgraph found by core or single deletion")
    args.summary.write_text(json.dumps(summary, indent=2) + "\n")
    logf.close()


if __name__ == "__main__":
    main()
