#!/usr/bin/env python3
"""Solve the n=18, d=6 exact statement as in-neighbourhood cubes.

Cube k means N+(0)={1..6} and N-(0)={7,...,6+k}.  The leftover
vertices are nonadjacent to 0.  Every C3-free 6-outregular oriented
graph on 18 vertices is isomorphic to one of these cubes.

k=11 is empty by a counting argument (each v in N+(0) has only 5
legal out-targets).  We still encode it; it should be UNSAT instantly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from solve import run_one

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--d", type=int, default=6)
    ap.add_argument("--time", type=int, default=180)
    ap.add_argument("--k-min", type=int, default=0)
    ap.add_argument("--k-max", type=int, default=None)
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--exact-in", action="store_true")
    args = ap.parse_args()
    k_max = args.k_max if args.k_max is not None else args.n - 1 - args.d
    CERTS.mkdir(exist_ok=True)
    rows = []
    for k in range(args.k_min, k_max + 1):
        print(f"== cube k={k} t={args.time}s ==", flush=True)
        rec = run_one(
            args.n,
            args.d,
            args.time,
            indeg0=k,
            exact_in=args.exact_in,
            sb=True,
            proof=args.proof,
            tag=None,
        )
        slim = {key: rec[key] for key in rec if key != "arcs"}
        print(
            f"  {slim.get('status')} {slim.get('header')} "
            f"time={slim.get('time_s')} drat={slim.get('drat')}",
            flush=True,
        )
        rows.append(slim)
        # keep a running log so a kill still leaves a residue
        (CERTS / "n18_cubes.json").write_text(json.dumps(rows, indent=2))
        if rec["status"] == "SAT" and rec.get("verified_model"):
            print("SAT MODEL — would disprove the exact statement", flush=True)
            (CERTS / "n18_sat_model.json").write_text(json.dumps(rec, indent=2))
            break
    all_unsat = all(r["status"] == "UNSAT" for r in rows)
    leftover = [r for r in rows if r["status"] != "UNSAT"]
    summary = {
        "n": args.n,
        "d": args.d,
        "k_range": [args.k_min, k_max],
        "all_unsat": all_unsat,
        "leftover": leftover,
        "rows": rows,
        "note": (
            "all cubes UNSAT with DRAT is a certificate of the exact statement"
            if all_unsat
            else "incomplete search is residue, not a bound"
        ),
    }
    path = CERTS / "n18_cubes_summary.json"
    path.write_text(json.dumps(summary, indent=2))
    print("wrote", path, "all_unsat=", all_unsat)


if __name__ == "__main__":
    main()
