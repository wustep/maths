#!/usr/bin/env python3
"""Third split of leftover (k, t=6): s = |N+(2) ∩ (N+(1) ∩ U)|."""

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
    ap.add_argument("--t", type=int, default=6)
    ap.add_argument("--time", type=int, default=180)
    ap.add_argument("--proof", action="store_true")
    args = ap.parse_args()
    CERTS.mkdir(exist_ok=True)
    rows = []
    for s in range(0, args.t + 1):
        print(f"== k={args.k} t={args.t} s={s} ==", flush=True)
        rec = run_one(
            18,
            6,
            args.time,
            indeg0=args.k,
            exact_in=False,
            sb=True,
            proof=args.proof,
            tag=None,
            u_from_1=args.t,
            nplus1_from_2=s,
        )
        slim = {x: rec[x] for x in rec if x not in ("arcs", "kissat_lines")}
        print(
            f"  {slim.get('status')} {slim.get('header')} time={slim.get('time_s')} drat={slim.get('drat')}",
            flush=True,
        )
        rows.append(slim)
        path = CERTS / f"n18_k{args.k}_t{args.t}_s_cubes.json"
        path.write_text(json.dumps(rows, indent=2))
        if rec["status"] == "SAT" and rec.get("verified_model"):
            print("SAT MODEL", flush=True)
            break
    print("wrote", path)


if __name__ == "__main__":
    main()
