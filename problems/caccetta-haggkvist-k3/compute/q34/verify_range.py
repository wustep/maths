#!/usr/bin/env python3
"""Replay stored cubes for n in [n_min, n_max] against regenerated CNFs."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from holes import cube_range
from solve import find_bin
from verify_keep import replay_one


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-min", type=int, required=True)
    ap.add_argument("--n-max", type=int, required=True)
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    args = ap.parse_args()
    drat_bin = find_bin("drat-trim")
    rows = []
    bad = 0
    for n in range(args.n_min, args.n_max + 1):
        # leftover holes in this range are consecutive after n=72
        d = (n + 2) // 3
        ks = cube_range(n, d)["needed_cubes"]
        print(f"== n={n} d={d} k={ks[0]}..{ks[-1]} ==", flush=True)
        if args.jobs <= 1:
            recs = [replay_one(n, d, k, drat_bin) for k in ks]
        else:
            recs = []
            with ThreadPoolExecutor(max_workers=args.jobs) as ex:
                futs = {ex.submit(replay_one, n, d, k, drat_bin): k for k in ks}
                by_k = {}
                for fut in as_completed(futs):
                    rec = fut.result()
                    by_k[rec["k"]] = rec
                    mark = "OK" if rec["ok"] else "FAIL"
                    print(
                        f"  k={rec['k']} {mark} {rec.get('header')} "
                        f"drat={rec.get('drat_bytes')}",
                        flush=True,
                    )
                recs = [by_k[k] for k in ks]
        for rec in recs:
            if args.jobs <= 1:
                mark = "OK" if rec["ok"] else "FAIL"
                print(
                    f"  k={rec['k']} {mark} {rec.get('header')} "
                    f"drat={rec.get('drat_bytes')}",
                    flush=True,
                )
            rows.append(rec)
            if not rec["ok"]:
                bad += 1
    summary = {
        "n_min": args.n_min,
        "n_max": args.n_max,
        "checked": len(rows),
        "failures": bad,
        "rows": rows,
    }
    if args.json_out:
        from pathlib import Path

        Path(args.json_out).write_text(json.dumps(summary, indent=2))
    print("checked", len(rows), "failures", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
