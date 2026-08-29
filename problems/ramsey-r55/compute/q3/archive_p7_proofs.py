#!/usr/bin/env python3
"""Pack the checked C7 cube DRUPs into deterministic gzip tar shards."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--completion-proof", type=Path, required=True)
    parser.add_argument("--cert", type=Path, required=True)
    parser.add_argument("--shards", type=int, default=8)
    args = parser.parse_args()

    results = []
    for shard in range(args.shards):
        path = args.results_dir / f"prove{shard}.json"
        results.extend(json.loads(path.read_text()))
    results.sort(key=lambda row: row["index"])
    if [row["index"] for row in results] != list(range(787)):
        raise RuntimeError("proof results do not cover indices 0..786 exactly")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    archives = []
    for shard in range(args.shards):
        target = args.output_dir / f"p7_cubes_{shard}.tar.gz"
        with target.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as zipped:
                with tarfile.open(fileobj=zipped, mode="w|") as archive:
                    for row in results:
                        if row["index"] % args.shards != shard:
                            continue
                        source = args.proof_dir / f"{row['index']:03d}.drat"
                        data = source.read_bytes()
                        if hashlib.sha256(data).hexdigest() != row["sha256"]:
                            raise RuntimeError(f"proof hash mismatch at {row['index']}")
                        add_bytes(archive, source.name, data)
        archives.append(
            {
                "bytes": target.stat().st_size,
                "path": str(target),
                "sha256": sha256(target),
                "shard": shard,
            }
        )

    completion_target = args.output_dir / "p7_neighborhoods_complete.drat.gz"
    with args.completion_proof.open("rb") as source, completion_target.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as zipped:
            while block := source.read(1 << 20):
                zipped.write(block)

    cert = {
        "archives": archives,
        "completion_proof": {
            "bytes": completion_target.stat().st_size,
            "path": str(completion_target),
            "sha256": sha256(completion_target),
        },
        "cube_proofs": results,
        "shards": args.shards,
        "status": "DRUP_VERIFIED",
        "total": len(results),
    }
    args.cert.parent.mkdir(parents=True, exist_ok=True)
    args.cert.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in cert.items() if key != "cube_proofs"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
