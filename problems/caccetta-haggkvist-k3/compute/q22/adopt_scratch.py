#!/usr/bin/env python3
"""Copy scratch certs/*.drat into keep/ after an independent replay.

Used for leftover n=131+ proofs written into q4 scratch or certs/.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from holes import cube_range
from solve import find_bin
from trim_keep import trim_keep_file
from verify_keep import replay_one

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
KEEP = CERTS / "keep"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--d", type=int, required=True)
    args = ap.parse_args()
    n, d = args.n, args.d
    ks = cube_range(n, d)["needed_cubes"]
    drat_bin = find_bin("drat-trim")
    rows = []
    adopted = 0
    missing = []
    failed = []
    for k in ks:
        scratch = CERTS / f"ch-{n}-{d}-k{k}.drat"
        dest = KEEP / scratch.name
        if dest.is_file():
            rec = replay_one(n, d, k, drat_bin)
            rec["action"] = "already-keep"
            rows.append(rec)
            if rec["ok"]:
                adopted += 1
            else:
                failed.append(k)
            print(f"  keep k={k} {'OK' if rec['ok'] else 'FAIL'}", flush=True)
            continue
        if not scratch.is_file():
            missing.append(k)
            print(f"  missing k={k}", flush=True)
            continue
        KEEP.mkdir(exist_ok=True)
        shutil.copy2(scratch, dest)
        if dest.stat().st_size >= 8 * 1024 * 1024:
            trim_keep_file(n, d, k)
        rec = replay_one(n, d, k, drat_bin)
        rec["action"] = "adopted"
        rows.append(rec)
        mark = "OK" if rec["ok"] else "FAIL"
        print(f"  adopt k={k} {mark} bytes={dest.stat().st_size}", flush=True)
        if rec["ok"]:
            adopted += 1
        else:
            failed.append(k)
            dest.unlink(missing_ok=True)
    out = {
        "n": n,
        "d": d,
        "needed": ks,
        "adopted_ok": adopted,
        "missing": missing,
        "failed": failed,
        "complete": adopted == len(ks) and not missing and not failed,
        "rows": rows,
    }
    path = KEEP / f"adopt_n{n}.json"
    path.write_text(json.dumps(out, indent=2))
    print("adopted", adopted, "of", len(ks), "missing", missing, "failed", failed)
    return 0 if out["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
