#!/usr/bin/env python3
"""Incremental Cadical deletion / core scan.

One solver, vertex selectors as assumptions.  Each G-v is a new assumption
set, so the CDCL trail is reused.  Logs JSONL.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195

from udg import coloring_cnf, degrees, load_vtx, unit_edges, write_edge_list


def write_sub_vtx(src: Path, dst: Path, keep: list[int]) -> None:
    lines = [ln for ln in src.read_text().splitlines() if ln.strip()]
    keep_set = set(keep)
    dst.write_text("\n".join(lines[i] for i in range(len(lines)) if i in keep_set) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--log", type=Path, default=Path("shrink_incr.jsonl"))
    ap.add_argument("--summary", type=Path, default=Path("shrink_incr_summary.json"))
    ap.add_argument("--no-core", action="store_true")
    ap.add_argument("--no-singles", action="store_true")
    args = ap.parse_args()

    t_all = time.perf_counter()
    pts = load_vtx(args.vtx)
    edges = unit_edges(pts)
    n = len(pts)
    deg = degrees(n, edges)
    print(f"n={n} m={len(edges)} mindeg={min(deg)} maxdeg={max(deg)}")

    nvars, clauses, meta = coloring_cnf(n, edges, triangle=None, vertex_selectors=True)
    sel_base = meta["sel_base"]
    all_assumps = [sel_base + v + 1 for v in range(n)]

    logf = args.log.open("w", encoding="utf-8")

    def log(rec: dict) -> None:
        logf.write(json.dumps(rec) + "\n")
        logf.flush()
        print(json.dumps(rec), flush=True)

    # Cadical supports assumption-based incremental SAT without incr=True
    # (that flag is unimplemented in python-sat's Cadical195 wrapper).
    s = Cadical195()
    for cl in clauses:
        s.add_clause(cl)

    t0 = time.perf_counter()
    sat = s.solve(assumptions=all_assumps)
    dt = time.perf_counter() - t0
    log({"phase": "baseline", "status": "SAT" if sat else "UNSAT", "seconds": dt})
    if sat:
        raise SystemExit("graph is 4-colorable")

    core = list(range(n))
    if not args.no_core:
        t0 = time.perf_counter()
        core_lits = s.get_core() or []
        dt = time.perf_counter() - t0
        core_set = set(core_lits)
        core = [v for v in range(n) if (sel_base + v + 1) in core_set]
        log({"phase": "vertex_core", "core_size": len(core), "seconds": dt, "core": core})

    smaller = None
    if len(core) < n:
        smaller = {"kind": "assumption_core", "n": len(core), "keep": core}

    n_sat = n_unsat = 0
    unsat_deletes = []
    if not args.no_singles:
        order = sorted(range(n), key=lambda v: (deg[v], v))
        for k, v in enumerate(order):
            assumps = [sel_base + u + 1 for u in range(n) if u != v]
            t0 = time.perf_counter()
            sat = s.solve(assumptions=assumps)
            dt = time.perf_counter() - t0
            rec = {
                "phase": "single_delete",
                "v": v,
                "degree": deg[v],
                "status": "SAT" if sat else "UNSAT",
                "seconds": dt,
                "k": k,
            }
            log(rec)
            if sat:
                n_sat += 1
            else:
                n_unsat += 1
                unsat_deletes.append(v)
                if smaller is None or n - 1 < smaller["n"]:
                    smaller = {
                        "kind": "single_delete",
                        "n": n - 1,
                        "deleted": v,
                        "keep": [i for i in range(n) if i != v],
                    }
        log({"phase": "single_delete_tally", "SAT": n_sat, "UNSAT": n_unsat, "unsat_deletes": unsat_deletes})

    s.delete()
    summary = {
        "vtx": str(args.vtx),
        "n": n,
        "m": len(edges),
        "core_size": len(core),
        "n_deletable": n_unsat,
        "smaller": None if smaller is None else {k: smaller[k] for k in smaller if k != "keep"},
        "elapsed_seconds": time.perf_counter() - t_all,
    }
    if smaller is not None:
        out = args.vtx.with_name(f"smaller_{smaller['n']}.vtx")
        write_sub_vtx(args.vtx, out, smaller["keep"])
        summary["smaller_vtx"] = str(out)
        # also dump edges of the smaller graph
        keep_set = set(smaller["keep"])
        imap = {old: new for new, old in enumerate(smaller["keep"])}
        sub_edges = [(imap[a], imap[b]) for a, b in edges if a in keep_set and b in keep_set]
        write_edge_list(args.vtx.with_name(f"smaller_{smaller['n']}.edges"), smaller["n"], sub_edges)
        print(f"SMALLER n={smaller['n']} -> {out}")
    else:
        print("no smaller subgraph by core or single deletion")
    args.summary.write_text(json.dumps(summary, indent=2) + "\n")
    logf.close()


if __name__ == "__main__":
    main()
