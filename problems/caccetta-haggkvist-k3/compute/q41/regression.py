#!/usr/bin/env python3
"""Small SAT/UNSAT pairs plus soundness at n=73 (encoder is not vacuous)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from solve import run_one
from cyclic_soundness import run as cyclic_run

HERE = Path(__file__).resolve().parent
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)

# (n, d, expected, secs, indeg0)
JOBS = [
    (6, 2, "UNSAT", 10, None),
    (9, 2, "SAT", 15, None),
    (9, 3, "UNSAT", 20, None),
    (18, 6, "UNSAT", 10, 11),
    (21, 6, "SAT", 30, 6),  # cyclic degree with SB; encoder is not vacuous
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
    print("cyclic soundness at n=73 d=24 ...", flush=True)
    cyc = cyclic_run(73, 24)
    print(
        f"  circulant_ok={cyc['circulant_ok']} "
        f"cnf_nosb={cyc['cnf_accepts_placed_circulant_nosb']} "
        f"cnf_sb={cyc['cnf_accepts_sorted_circulant_sb']} "
        f"k={cyc['k']} ok={cyc['ok']}",
        flush=True,
    )
    rows.append(cyc)
    if not cyc["ok"]:
        bad += 1
    path = OUT / "regression.json"
    path.write_text(json.dumps(rows, indent=2))
    KEEP = HERE / "certs" / "keep"
    KEEP.mkdir(exist_ok=True)
    (KEEP / "soundness_n73_d24.json").write_text(json.dumps(cyc, indent=2))
    print("wrote", path, "failures", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
