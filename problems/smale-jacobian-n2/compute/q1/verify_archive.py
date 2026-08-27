#!/usr/bin/env python3
"""Bind, inspect, safely extract, and check output from the external certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath


def sha256_stream(stream) -> str:
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def safe_members(archive: zipfile.ZipFile) -> list[str]:
    names = archive.namelist()
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe archive member: {name}")
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--extract", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.certificate.read_text())["external_exact_certificate"]
    with args.archive.open("rb") as source:
        archive_hash = sha256_stream(source)
    if archive_hash != manifest["sha256"]:
        raise ValueError(f"archive SHA-256 mismatch: {archive_hash}")

    with zipfile.ZipFile(args.archive) as archive:
        names = set(safe_members(archive))
        for name, expected in manifest["internal_sha256"].items():
            if name not in names:
                raise ValueError(f"missing certificate member: {name}")
            with archive.open(name) as source:
                actual = sha256_stream(source)
            if actual != expected:
                raise ValueError(f"internal SHA-256 mismatch for {name}: {actual}")
        if args.extract is not None:
            args.extract.mkdir(parents=True, exist_ok=True)
            archive.extractall(args.extract)

    if args.output is not None:
        output = args.output.read_text()
        missing = [marker for marker in manifest["expected_markers"] if marker not in output]
        if missing:
            raise ValueError(f"missing replay markers: {missing}")

    print(f"ARCHIVE_SHA256_PASS {archive_hash}")
    print(f"INTERNAL_SHA256_PASS files={len(manifest['internal_sha256'])}")
    if args.output is not None:
        print(f"REPLAY_MARKERS_PASS count={len(manifest['expected_markers'])}")


if __name__ == "__main__":
    main()
