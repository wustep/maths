#!/usr/bin/env python3
"""Second split of the leftover n=18 cubes k=0 and k=1.

U = V \\ ({0} ∪ N+(0) ∪ N-(0)).  Vertex 1 needs 6 out-neighbours from
(N+(0)\\{1}) ∪ U.  |N+(0)\\{1}| = 5, so t = |N+(1) ∩ U| is in 1..6.
Fix those t heads as the first t labels of U.
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
    ap.add_argument("--k", type=int, default=0)
    ap.add_argument("--time", type=int, default=180)
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--t-min", type=int, default=1)
    ap.add_argument("--t-max", type=int, default=6)
    args = ap.parse_args()
    CERTS.mkdir(exist_ok=True)
    rows = []
    for t in range(args.t_min, args.t_max + 1):
        print(f"== k={args.k} t={t} ==", flush=True)
        rec = run_one(
            18,
            6,
            args.time,
            indeg0=args.k,
            exact_in=False,
            sb=True,
            proof=args.proof,
            tag=None,
            u_from_1=t,
        )
        slim = {x: rec[x] for x in rec if x not in ("arcs", "kissat_lines")}
        print(
            f"  {slim.get('status')} {slim.get('header')} time={slim.get('time_s')} drat={slim.get('drat')}",
            flush=True,
        )
        rows.append(slim)
        (CERTS / f"n18_k{args.k}_t_cubes.json").write_text(json.dumps(rows, indent=2))
        if rec["status"] == "SAT" and rec.get("verified_model"):
            print("SAT MODEL", flush=True)
            (CERTS / f"n18_k{args.k}_sat.json").write_text(json.dumps(rec, indent=2))
            break
    path = CERTS / f"n18_k{args.k}_t_cubes.json"
    print("wrote", path)


if __name__ == "__main__":
    main()
