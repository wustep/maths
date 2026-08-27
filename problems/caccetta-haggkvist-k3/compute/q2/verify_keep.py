#!/usr/bin/env python3
"""Regenerate each stored cube CNF from the encoder and replay its DRAT.

Does not trust the CNF bytes in certs/ — those are gitignored scratch.
The certificate is (encode.py, k, keep/*.drat).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from holes import cube_range
from solve import find_bin
from encode import encode, write_cnf

HERE = Path(__file__).resolve().parent
KEEP = HERE / "certs" / "keep"

# (n, d) orders whose pigeonhole cubes are stored.
ORDERS = [
    (21, 7),
    (24, 8),
    (26, 9),
    (27, 9),
    (29, 10),
    (30, 10),
    (32, 11),
    (33, 11),
    (35, 12),
    (36, 12),
]


def needed_ks(n: int, d: int) -> list[int]:
    info = cube_range(n, d)
    return info["needed_cubes"]


def replay_one(n: int, d: int, k: int, drat_bin: Path) -> dict:
    drat_path = KEEP / f"ch-{n}-{d}-k{k}.drat"
    if not drat_path.is_file():
        return {"n": n, "d": d, "k": k, "ok": False, "error": "missing-drat"}
    clauses, nvars = encode(n, d, exact=True, sb=True, indeg0=k)
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        write_cnf(clauses, nvars, f)
        cnf_path = Path(f.name)
    raw = cnf_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    chk = subprocess.run(
        [str(drat_bin), str(cnf_path), str(drat_path)],
        capture_output=True,
        text=True,
    )
    cnf_path.unlink(missing_ok=True)
    text = chk.stdout + chk.stderr
    verified = "s VERIFIED" in text
    return {
        "n": n,
        "d": d,
        "k": k,
        "header": f"p cnf {nvars} {len(clauses)}",
        "cnf_sha256": digest,
        "drat_bytes": drat_path.stat().st_size,
        "drat": "VERIFIED" if verified else text[-300:],
        "ok": verified,
    }


def main():
    drat_bin = find_bin("drat-trim")
    rows = []
    bad = 0
    for n, d in ORDERS:
        ks = needed_ks(n, d)
        print(f"== n={n} d={d} k={ks[0]}..{ks[-1]} ==", flush=True)
        for k in ks:
            rec = replay_one(n, d, k, drat_bin)
            mark = "OK" if rec["ok"] else "FAIL"
            print(
                f"  k={k} {mark} {rec.get('header')} drat={rec.get('drat_bytes')}",
                flush=True,
            )
            rows.append(rec)
            if not rec["ok"]:
                bad += 1
    summary = {
        "orders": ORDERS,
        "checked": len(rows),
        "failures": bad,
        "rows": rows,
    }
    out = KEEP / "replay.json"
    out.write_text(json.dumps(summary, indent=2))
    print("wrote", out, "failures", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
