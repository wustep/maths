#!/usr/bin/env python3
"""Known SAT/UNSAT pairs for the sequential-counter encoding.

These recover the 2026-08-17 census plus Hoàng–Reed / HKN small orders.
A SAT model is checked by verify_model.check.  UNSAT is by kissat.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from solve import run_one

HERE = Path(__file__).resolve().parent
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)

# (n, d, expected, secs, indeg0 or None)
JOBS = [
    (5, 1, "SAT", 10, None),   # directed C5
    (5, 2, "UNSAT", 10, None),
    (6, 1, "SAT", 10, None),
    (6, 2, "UNSAT", 10, None),  # CH r=2
    (9, 2, "SAT", 15, None),    # circulant
    (9, 3, "UNSAT", 20, None),
    (12, 3, "SAT", 20, None),
    (12, 4, "UNSAT", 30, None),  # Hoàng–Reed
    (15, 5, "UNSAT", 30, None),
    (16, 6, "UNSAT", 20, None),
]


def main():
    rows = []
    bad = 0
    for n, d, expect, secs, k in JOBS:
        print(f"n={n} d={d} expect={expect} ...", flush=True)
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
