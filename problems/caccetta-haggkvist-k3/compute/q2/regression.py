#!/usr/bin/env python3
"""Small SAT/UNSAT pairs plus the stored n=18 k=11 cube (do not regress)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from solve import run_one

HERE = Path(__file__).resolve().parent
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)

# (n, d, expected, secs, indeg0)
JOBS = [
    (6, 2, "UNSAT", 10, None),
    (9, 2, "SAT", 15, None),
    (9, 3, "UNSAT", 20, None),
    (18, 6, "UNSAT", 10, 11),
]


def main():
    rows = []
    bad = 0
    for n, d, expect, secs, k in JOBS:
        print(f"n={n} d={d} k={k} expect={expect} ...", flush=True)
        rec = run_one(
            n, d, secs, indeg0=k, exact_in=False, sb=True, proof=False, tag=None
        )
        ok = rec["status"] == expect
        if rec["status"] == "SAT":
            ok = ok and bool(rec.get("verified_model"))
        print(
            f"  {rec['status']} header={rec['header']} time={rec['time_s']} ok={ok}",
            flush=True,
        )
        rec["expect"] = expect
        rec["ok"] = ok
        rec.pop("arcs", None)
        rows.append(rec)
        if not ok:
            bad += 1
    path = OUT / "regression.json"
    path.write_text(json.dumps(rows, indent=2))
    print("wrote", path, "failures", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
