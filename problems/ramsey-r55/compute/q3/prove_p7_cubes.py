#!/usr/bin/env python3
"""Generate checked plain-CDCL DRAT proofs for shards of the 787 C7 cubes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from p7_neighborhoods import literals, write_cube


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-cnf", type=Path, required=True)
    parser.add_argument("--neighborhoods", type=Path, required=True)
    parser.add_argument("--kissat", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--proof-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.neighborhoods.read_text())
    rows: list[str] = data["rows"]
    projected: list[int] = data["projected_variables"]
    args.proof_dir.mkdir(parents=True, exist_ok=True)
    args.work_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for index in range(args.shard, len(rows), args.shards):
        started = time.monotonic()
        cube = args.work_dir / "cube.cnf"
        raw = args.work_dir / "raw.drat"
        trimmed = args.proof_dir / f"{index:03d}.drat"
        write_cube(args.base_cnf, cube, literals(rows[index], projected))
        solved = subprocess.run(
            [str(args.kissat), "--plain", str(cube), str(raw)],
            check=False,
            capture_output=True,
            text=True,
        )
        if solved.returncode != 20 or "s UNSATISFIABLE" not in solved.stdout:
            raise RuntimeError(
                f"cube {index}: kissat exit {solved.returncode}: "
                f"{solved.stdout[-500:]} {solved.stderr[-500:]}"
            )
        checked = subprocess.run(
            [
                str(args.drat_trim),
                str(cube),
                str(raw),
                "-l",
                str(trimmed),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if checked.returncode or "s VERIFIED" not in checked.stdout:
            raise RuntimeError(
                f"cube {index}: drat-trim exit {checked.returncode}: "
                f"{checked.stdout[-1000:]} {checked.stderr[-500:]}"
            )
        if "0 RAT lemmas" not in checked.stdout:
            raise RuntimeError(f"cube {index}: trimmed proof is not DRUP")
        digest = hashlib.sha256(trimmed.read_bytes()).hexdigest()
        result = {
            "bytes": trimmed.stat().st_size,
            "index": index,
            "sec": round(time.monotonic() - started, 3),
            "sha256": digest,
            "status": "DRUP_VERIFIED",
        }
        results.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
        raw.unlink()
        cube.unlink()

    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
