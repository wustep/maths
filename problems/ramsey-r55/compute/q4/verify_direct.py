#!/usr/bin/env python3
"""Regenerate leftover CNFs and check every stored direct DRAT."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from cases import all_cases


ROOT = Path(__file__).resolve().parent
ENCODER = ROOT.parent / "q2" / "orbit_sat.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stored_proofs() -> list[dict]:
    rows = []
    for case in all_cases():
        cert = ROOT / "certs" / f"{case['name']}.json"
        proof = ROOT / "certs" / "proofs" / f"{case['name']}.drat.gz"
        if not cert.exists() or not proof.exists():
            continue
        rec = json.loads(cert.read_text())
        if rec.get("status") != "UNSAT" or not rec.get("proof_verified"):
            continue
        rows.append({**case, "cert": rec, "proof": proof})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--proof-dir", type=Path, default=ROOT / "certs" / "proofs")
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)

    proofs = stored_proofs()
    if not proofs:
        print("no stored direct proofs", flush=True)
        return 0

    for case in proofs:
        name = case["name"]
        cnf = args.work_dir / f"{name}.cnf"
        cmd = [
            sys.executable,
            str(ENCODER),
            "--n", "43",
            "--p", str(case["p"]),
            "--cycles", str(case["cycles"]),
            "--fixed-cycle-count", str(case["fixed_cycle_count"]),
            "--cnf", str(cnf),
        ]
        if case["p5_symbreak"]:
            cmd.append("--p5-symbreak")
        else:
            cmd.append("--anchor-symbreak")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        expected = case["cert"]["build"]["cnf_sha256"]
        actual = sha256(cnf)
        if actual != expected:
            raise RuntimeError(f"CNF hash mismatch for {name}")
        proof = args.work_dir / f"{name}.drat"
        with gzip.open(case["proof"], "rb") as source:
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
