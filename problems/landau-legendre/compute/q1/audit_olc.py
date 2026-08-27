#!/usr/bin/env python3
"""Project and audit public OLC worker rows from a pinned Git object."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

COMMIT = "5cdaa95f0a4b1428a05480cc1c69d556a8f9517a"
REPOSITORY = "https://github.com/sorenson64/olc"
SELECTOR = r"^(bigdawg|phi)/data[^/]*/[^/]+\.out$"
PATH_RE = re.compile(SELECTOR)
HEADER = "source_path\tsource_line\tnbegin\tnend\tfound\tR0\tR1\tR2\tR3\tR4\n"
PUBLISHED_N = 70_500_000_000_000


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def selected_blobs(repo: Path) -> list[tuple[str, str]]:
    resolved = git(repo, "rev-parse", "--verify", f"{COMMIT}^{{commit}}").decode().strip()
    if resolved != COMMIT:
        raise AssertionError(f"unexpected resolved commit {resolved}")
    records = git(repo, "ls-tree", "-r", "-z", COMMIT).split(b"\0")
    selected: list[tuple[str, str]] = []
    for record in records:
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, raw_oid = metadata.split()
        del mode
        path = raw_path.decode("utf-8")
        if PATH_RE.fullmatch(path):
            if object_type != b"blob":
                raise AssertionError(f"selected path is not a blob: {path}")
            selected.append((path, raw_oid.decode("ascii")))
    selected.sort()
    if not selected:
        raise AssertionError("the selector found no worker logs")
    return selected


def read_blobs(repo: Path, selected: list[tuple[str, str]]):
    process = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None
    try:
        for path, oid in selected:
            process.stdin.write((oid + "\n").encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii").split()
            if len(header) != 3 or header[1] != "blob":
                raise AssertionError(f"cannot read Git blob for {path}: {header}")
            size = int(header[2])
            blob = process.stdout.read(size)
            if len(blob) != size or process.stdout.read(1) != b"\n":
                raise AssertionError(f"truncated Git blob for {path}")
            yield path, oid, blob
    finally:
        process.stdin.close()
        if process.wait() != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)


def parse_blob(path: str, blob: bytes) -> tuple[list[tuple[int, ...]], int]:
    rows: list[tuple[int, ...]] = []
    ignored = 0
    for line_number, raw_line in enumerate(blob.splitlines(), 1):
        fields = raw_line.split()
        if not fields:
            continue
        if not fields[0].isdigit():
            ignored += 1
            continue
        if len(fields) != 16:
            raise AssertionError(f"{path}:{line_number}: expected 16 fields")
        try:
            integers = [int(field) for field in fields[:13]]
            mean_t = Decimal(fields[13].decode("ascii"))
            mean_k = Decimal(fields[14].decode("ascii"))
            worker_id = int(fields[15])
        except (ValueError, ArithmeticError) as error:
            raise AssertionError(f"{path}:{line_number}: malformed numeric row") from error
        if min(integers) < 0 or worker_id < 0 or not mean_t.is_finite() or not mean_k.is_finite():
            raise AssertionError(f"{path}:{line_number}: invalid numeric value")
        nbegin, nend, found = integers[:3]
        r_counts = integers[5:10]
        if not nbegin < nend:
            raise AssertionError(f"{path}:{line_number}: empty or reversed interval")
        rows.append((line_number, nbegin, nend, found, *r_counts))
    if not rows:
        raise AssertionError(f"{path}: no numeric rows")
    return rows, ignored


def coverage(intervals: set[tuple[int, int]]) -> list[list[int]]:
    components: list[list[int]] = []
    for start, end in sorted(intervals):
        if not components or start > components[-1][1]:
            components.append([start, end])
        elif end > components[-1][1]:
            components[-1][1] = end
    return components


def write_deterministic_gzip(path: Path, payload: bytes) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
            zipped.write(payload)


def build(repo: Path, rows_output: Path, summary_output: Path) -> dict[str, object]:
    selected = selected_blobs(repo)
    manifest = "".join(f"{path}\t{oid}\n" for path, oid in selected).encode("utf-8")
    projection = bytearray(HEADER.encode("ascii"))
    intervals: list[tuple[int, int]] = []
    starts: dict[int, set[int]] = defaultdict(set)
    program_files: Counter[str] = Counter()
    program_rows: Counter[str] = Counter()
    total_source_bytes = 0
    ignored_lines = 0
    bucket_failures = 0
    delta_failures = 0
    row_count = 0

    for path, oid, blob in read_blobs(repo, selected):
        del oid
        total_source_bytes += len(blob)
        rows, ignored = parse_blob(path, blob)
        ignored_lines += ignored
        program = path.split("/", 1)[0]
        program_files[program] += 1
        program_rows[program] += len(rows)
        previous_found = 0
        for line_number, nbegin, nend, found, r0, r1, r2, r3, r4 in rows:
            if found != r0 + r1 + r2 + r3 + r4:
                bucket_failures += 1
            if found - previous_found != 2 * (nend - nbegin):
                delta_failures += 1
            previous_found = found
            intervals.append((nbegin, nend))
            starts[nbegin].add(nend)
            projection.extend(
                f"{path}\t{line_number}\t{nbegin}\t{nend}\t{found}\t"
                f"{r0}\t{r1}\t{r2}\t{r3}\t{r4}\n".encode("ascii")
            )
            row_count += 1

    if bucket_failures or delta_failures:
        raise AssertionError(
            f"worker invariants failed: buckets={bucket_failures} deltas={delta_failures}"
        )
    unique_intervals = set(intervals)
    components = coverage(unique_intervals)
    holes = [[left[1], right[0]] for left, right in zip(components, components[1:])]
    covered = sum(end - begin for begin, end in components)
    summary: dict[str, object] = {
        "schema": "landau-legendre.olc-public-audit.v1",
        "repository": REPOSITORY,
        "commit": COMMIT,
        "selector": SELECTOR,
        "source_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
        "source_blob_bytes": total_source_bytes,
        "projection_sha256": hashlib.sha256(projection).hexdigest(),
        "file_count": len(selected),
        "row_count": row_count,
        "program_file_counts": dict(sorted(program_files.items())),
        "program_row_counts": dict(sorted(program_rows.items())),
        "ignored_nonrecord_lines": ignored_lines,
        "unique_start_count": len(starts),
        "conflicting_start_count": sum(len(ends) > 1 for ends in starts.values()),
        "unique_interval_count": len(unique_intervals),
        "duplicate_interval_rows": row_count - len(unique_intervals),
        "bucket_invariant_failures": bucket_failures,
        "delta_invariant_failures": delta_failures,
        "min_begin": min(begin for begin, _ in unique_intervals),
        "max_end_exclusive": max(end for _, end in unique_intervals),
        "covered_n_count": covered,
        "coverage_components": components,
        "coverage_holes": holes,
        "published_N": PUBLISHED_N,
        "public_projection_reaches_published_N": components[-1][1] > PUBLISHED_N,
    }
    write_deterministic_gzip(rows_output, bytes(projection))
    summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--rows-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()
    summary = build(args.repo, args.rows_output, args.summary_output)
    print(
        "PASS olc_source_audit",
        f"files={summary['file_count']}",
        f"rows={summary['row_count']}",
        f"components={len(summary['coverage_components'])}",
        f"max_end={summary['max_end_exclusive']}",
    )


if __name__ == "__main__":
    main()
