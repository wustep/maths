#!/usr/bin/env python3
"""Regenerate and check the eight direct DRAT proofs for C7 cycle types."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    (1, 1),
    (2, 1),
    (2, 2),
    (3, 1),
    (3, 3),
    (4, 1),
    (4, 2),
    (5, 2),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--proof-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    q2_encoder = Path(__file__).resolve().parents[1] / "q2" / "orbit_sat.py"

    for cycles, selected in CASES:
        name = f"p7_c{cycles}_k{selected}"
        cnf = args.work_dir / f"{name}.cnf"
        build = Path("certs") / f"{name}_build.json"
        subprocess.run(
            [
                sys.executable,
                str(q2_encoder),
                "--n",
                "43",
                "--p",
                "7",
                "--cycles",
                str(cycles),
                "--fixed-cycle-count",
                str(selected),
                "--anchor-symbreak",
                "--cnf",
                str(cnf),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        expected = json.loads(build.read_text())["cnf_sha256"]
        actual = hashlib.sha256(cnf.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"CNF hash mismatch for {name}")
        compressed = args.proof_dir / f"{name}.drat.gz"
        proof = args.work_dir / f"{name}.drat"
        with gzip.open(compressed, "rb") as source:
            proof.write_bytes(source.read())
        result = subprocess.run(
            [str(args.drat_trim), str(cnf), str(proof)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode or "s VERIFIED" not in result.stdout:
            raise RuntimeError(f"DRAT check failed for {name}: {result.stdout[-1000:]}")
        print(f"VERIFIED {name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
