#!/usr/bin/env python3
"""Solve one exact order as in-neighbourhood cubes, high k first."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from holes import cube_range
from solve import run_one

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def solve_cube(n, d, k, secs, proof, exact_in, u_from_1, stable):
    extra = ["--stable"] if stable else None
    rec = run_one(
        n,
        d,
        secs,
        indeg0=k,
        exact_in=exact_in,
        sb=True,
        proof=proof,
        tag=None,
        u_from_1=u_from_1,
        extra_args=extra,
    )
    return {key: rec[key] for key in rec if key != "arcs"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=21)
    ap.add_argument("--d", type=int, default=7)
    ap.add_argument("--time", type=int, default=180)
    ap.add_argument("--k-min", type=int, default=None)
    ap.add_argument("--k-max", type=int, default=None)
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--exact-in", action="store_true")
    ap.add_argument("--u-from-1", type=int, default=None)
    ap.add_argument("--stable", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--json-name", default=None)
    args = ap.parse_args()
    info = cube_range(args.n, args.d)
    k_min = args.k_min if args.k_min is not None else info["k_min_pigeonhole"]
    k_max = args.k_max if args.k_max is not None else info["k_max_absolute"]
    CERTS.mkdir(exist_ok=True)
    ks = list(range(k_max, k_min - 1, -1))
    print(
        f"n={args.n} d={args.d} cubes k={k_min}..{k_max} high-first "
        f"needed={info['needed_cubes']}",
        flush=True,
    )
    rows = []
    stem = args.json_name or f"n{args.n}_cubes"

    def submit(k):
        print(f"== cube k={k} t={args.time}s ==", flush=True)
        slim = solve_cube(
            args.n, args.d, k, args.time, args.proof, args.exact_in, args.u_from_1, args.stable
        )
        print(
            f"  k={k} {slim.get('status')} {slim.get('header')} "
            f"time={slim.get('time_s')} conflicts={slim.get('conflicts')} "
            f"drat={slim.get('drat')}",
            flush=True,
        )
        return slim

    if args.jobs <= 1:
        for k in ks:
            rows.append(submit(k))
            (CERTS / f"{stem}.json").write_text(json.dumps(rows, indent=2))
            if rows[-1]["status"] == "SAT" and rows[-1].get("verified_model"):
                print("SAT MODEL — would disprove the exact statement", flush=True)
                (CERTS / f"n{args.n}_sat_model.json").write_text(
                    json.dumps(rows[-1], indent=2)
                )
                break
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            futs = {ex.submit(submit, k): k for k in ks}
            by_k = {}
            for fut in as_completed(futs):
                slim = fut.result()
                by_k[slim["indeg0"]] = slim
                rows = [by_k[k] for k in sorted(by_k, reverse=True)]
                (CERTS / f"{stem}.json").write_text(json.dumps(rows, indent=2))

    leftover = [r for r in rows if r["status"] != "UNSAT"]
    all_unsat = bool(rows) and not leftover
    summary = {
        "n": args.n,
        "d": args.d,
        "k_range": [k_min, k_max],
        "pigeonhole": info,
        "all_unsat": all_unsat,
        "leftover": leftover,
        "rows": rows,
        "note": (
            "all cubes UNSAT with DRAT is a certificate of the exact statement"
            if all_unsat
            else "incomplete search is residue, not a bound"
        ),
    }
    path = CERTS / f"{stem}_summary.json"
    path.write_text(json.dumps(summary, indent=2))
    print("wrote", path, "all_unsat=", all_unsat)


if __name__ == "__main__":
    main()
