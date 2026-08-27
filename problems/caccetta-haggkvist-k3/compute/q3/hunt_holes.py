#!/usr/bin/env python3
"""Walk remaining exact holes after q2, high-k cubes first, store DRATs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from holes import cube_range, remaining_after_q2
from run_cubes import solve_cube

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
KEEP = CERTS / "keep"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--time", type=int, default=180)
    ap.add_argument("--n-max", type=int, default=60)
    ap.add_argument("--n-min", type=int, default=38)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--stop-on-unknown", action="store_true")
    args = ap.parse_args()

    holes = [
        row
        for row in remaining_after_q2(n_max=args.n_max)
        if row["n"] >= args.n_min
    ]
    print(f"remaining holes n={args.n_min}..{args.n_max}: {[r['n'] for r in holes]}", flush=True)
    CERTS.mkdir(exist_ok=True)
    KEEP.mkdir(exist_ok=True)

    closed = []
    residue = []
    for row in holes:
        n, d = row["n"], row["d"]
        info = cube_range(n, d)
        ks = info["needed_cubes"]
        print(f"\n==== n={n} d={d} cubes {ks[0]}..{ks[-1]} ====", flush=True)
        rows = []
        leftover = []
        if args.jobs <= 1:
            for k in reversed(ks):
                slim = solve_cube(n, d, k, args.time, True, False, None, False, True)
                print(
                    f"  k={k} {slim.get('status')} time={slim.get('time_s')} "
                    f"conflicts={slim.get('conflicts')} drat={slim.get('drat')}",
                    flush=True,
                )
                rows.append(slim)
                if slim["status"] != "UNSAT" or slim.get("drat") != "VERIFIED":
                    leftover.append(slim)
                    if args.stop_on_unknown:
                        break
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(max_workers=args.jobs) as ex:
                futs = {
                    ex.submit(
                        solve_cube, n, d, k, args.time, True, False, None, False, True
                    ): k
                    for k in reversed(ks)
                }
                by_k = {}
                for fut in as_completed(futs):
                    slim = fut.result()
                    by_k[slim["indeg0"]] = slim
                    print(
                        f"  k={slim['indeg0']} {slim.get('status')} "
                        f"time={slim.get('time_s')} conflicts={slim.get('conflicts')} "
                        f"drat={slim.get('drat')}",
                        flush=True,
                    )
                rows = [by_k[k] for k in sorted(by_k, reverse=True)]
                leftover = [
                    r
                    for r in rows
                    if r["status"] != "UNSAT" or r.get("drat") != "VERIFIED"
                ]

        rec = {
            "n": n,
            "d": d,
            "pigeonhole": info,
            "all_unsat": not leftover,
            "leftover": leftover,
            "rows": rows,
        }
        (CERTS / f"n{n}_cubes_summary.json").write_text(json.dumps(rec, indent=2))
        (KEEP / f"n{n}_cubes_summary.json").write_text(json.dumps(rec, indent=2))
        if leftover:
            residue.append({"n": n, "d": d, "leftover": leftover})
            print(f"RESIDUE n={n} leftover={len(leftover)}", flush=True)
            if args.stop_on_unknown:
                break
        else:
            closed.append(n)
            print(f"CLOSED n={n}", flush=True)

    prev_path = KEEP / "summary.json"
    prev_closed = []
    if prev_path.is_file():
        try:
            prev = json.loads(prev_path.read_text())
            prev_closed = list(prev.get("closed") or [])
        except json.JSONDecodeError:
            prev_closed = []
    all_closed = sorted(set(prev_closed) | set(closed))
    summary = {
        "closed": all_closed,
        "this_run": closed,
        "residue": [{"n": r["n"], "d": r["d"], "n_leftover": len(r["leftover"])} for r in residue],
        "f4": 0.34645,
        "published_hkn": 0.3465,
        "note": (
            "closed = every needed cube UNSAT with stored DRAT. "
            "A leftover is residue, not a bound. F4 unchanged."
        ),
    }
    path = KEEP / "summary.json"
    path.write_text(json.dumps(summary, indent=2))
    print("wrote", path, "closed", closed)
    return 0 if not residue else 1


if __name__ == "__main__":
    raise SystemExit(main())
