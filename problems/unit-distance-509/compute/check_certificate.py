#!/usr/bin/env python3
"""Independent checker: published coordinates -> unit edges -> 4-color CNF -> DRAT.

Exit 0 only if
  * the .vtx parses into exactly n points in Q(√3,√5,√11),
  * the exact unit-distance graph has m edges,
  * the 4-coloring CNF is the one whose DRAT proof drat-trim accepts.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from udg import coloring_cnf, find_triangle, load_vtx, unit_edges, write_dimacs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("drat", type=Path)
    ap.add_argument("--expect-n", type=int, required=True)
    ap.add_argument("--expect-m", type=int, required=True)
    ap.add_argument("--drat-trim", type=Path, default=Path(__file__).with_name("drat-trim"))
    ap.add_argument("--cnf-out", type=Path, default=None)
    args = ap.parse_args()

    pts = load_vtx(args.vtx)
    n = len(pts)
    if n != args.expect_n:
        print(f"FAIL n={n} expected {args.expect_n}")
        return 1
    edges = unit_edges(pts)
    m = len(edges)
    if m != args.expect_m:
        print(f"FAIL m={m} expected {args.expect_m}")
        return 1
    tri = find_triangle(n, edges)
    nvars, clauses, _ = coloring_cnf(n, edges, triangle=tri)
    cnf_path = args.cnf_out or args.vtx.with_suffix(".check.cnf")
    write_dimacs(
        cnf_path,
        nvars,
        clauses,
        comments=[f"4-color {args.vtx.name} n={n} m={m} triangle={tri}"],
    )
    print(f"ok n={n} m={m} triangle={tri} cnf={nvars}x{len(clauses)}")
    proc = subprocess.run(
        [str(args.drat_trim), str(cnf_path), str(args.drat), "-I", "-t", "600"],
        check=False,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if "s VERIFIED" not in proc.stdout and "s VERIFIED" not in proc.stderr:
        print("FAIL: drat-trim did not verify")
        return 1
    print("PASS: exact unit-distance graph is not 4-colorable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
