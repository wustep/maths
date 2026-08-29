#!/usr/bin/env python3
"""Replay the local-completion DRUP and all 787 archived conquer DRUPs."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

from p7_neighborhoods import enumerate_rows, literals, local_formula, write_cube, write_dimacs


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(drat_trim: Path, cnf: Path, proof: Path) -> None:
    result = subprocess.run(
        [str(drat_trim), str(cnf), str(proof)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode or "s VERIFIED" not in result.stdout:
        raise RuntimeError(
            f"proof check failed for {proof}: {result.stdout[-1000:]} {result.stderr[-500:]}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--neighborhoods", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--proof-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--archive-shard", type=int)
    args = parser.parse_args()

    neighborhoods = json.loads(args.neighborhoods.read_text())
    manifest = json.loads(args.manifest.read_text())
    args.work_dir.mkdir(parents=True, exist_ok=True)

    obj, projected, local_clauses = local_formula()
    rows = enumerate_rows(projected, local_clauses)
    if rows != neighborhoods["rows"]:
        raise RuntimeError("local neighborhood enumeration changed")
    full_cnf = args.work_dir / "p7_c6_k3.cnf"
    # local_formula built the complete q2 maximum-cycle object as a side effect.
    from orbit_sat import write_dimacs as write_full_dimacs

    full_hash = write_full_dimacs(obj, full_cnf)
    expected_full = json.loads((args.neighborhoods.parent / "p7_c6_k3_build.json").read_text())
    if full_hash != expected_full["cnf_sha256"]:
        raise RuntimeError("full CNF hash mismatch")

    blockers = [[-lit for lit in literals(row, projected)] for row in rows]
    completion_cnf = args.work_dir / "p7_neighborhoods_complete.cnf"
    nvars = max(abs(lit) for clause in local_clauses for lit in clause)
    completion_hash = write_dimacs(completion_cnf, nvars, local_clauses + blockers)
    if completion_hash != neighborhoods["completion_cnf_sha256"]:
        raise RuntimeError("local completion CNF hash mismatch")
    if args.archive_shard in (None, 0):
        completion_gz = args.proof_dir / "p7_neighborhoods_complete.drat.gz"
        expected_completion = manifest["completion_proof"]
        if sha256(completion_gz) != expected_completion["sha256"]:
            raise RuntimeError("completion proof archive hash mismatch")
        completion = args.work_dir / "p7_neighborhoods_complete.drat"
        with gzip.open(completion_gz, "rb") as source:
            completion.write_bytes(source.read())
        check(args.drat_trim, completion_cnf, completion)
        print("VERIFIED local neighborhood completion", flush=True)

    expected = {row["index"]: row for row in manifest["cube_proofs"]}
    seen: set[int] = set()
    cube_cnf = args.work_dir / "cube.cnf"
    cube_proof = args.work_dir / "cube.drat"
    archive_rows = manifest["archives"]
    if args.archive_shard is not None:
        archive_rows = [row for row in archive_rows if row["shard"] == args.archive_shard]
        if len(archive_rows) != 1:
            raise RuntimeError("archive shard not found")
    for archive_row in archive_rows:
        archive_path = args.proof_dir / Path(archive_row["path"]).name
        if sha256(archive_path) != archive_row["sha256"]:
            raise RuntimeError(f"archive hash mismatch: {archive_path}")
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive:
                if not member.isfile() or not member.name.endswith(".drat"):
                    raise RuntimeError(f"unexpected archive member: {member.name}")
                index = int(Path(member.name).stem)
                if index in seen or index not in expected:
                    raise RuntimeError(f"unexpected cube proof index: {index}")
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError(f"cannot read {member.name}")
                data = source.read()
                if hashlib.sha256(data).hexdigest() != expected[index]["sha256"]:
                    raise RuntimeError(f"cube proof hash mismatch: {index}")
                cube_proof.write_bytes(data)
                write_cube(full_cnf, cube_cnf, literals(rows[index], projected))
                check(args.drat_trim, cube_cnf, cube_proof)
                seen.add(index)
                print(f"VERIFIED cube {index + 1}/787", flush=True)
    expected_seen = set(range(787))
    if args.archive_shard is not None:
        expected_seen = {index for index in expected_seen if index % manifest["shards"] == args.archive_shard}
    if seen != expected_seen:
        raise RuntimeError("cube proof coverage is incomplete")
    if args.archive_shard is None:
        print("VERIFIED all 787 C7 conquer cubes", flush=True)
    else:
        print(f"VERIFIED C7 conquer shard {args.archive_shard}: {len(seen)} cubes", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
