#!/usr/bin/env python3
"""Verify the committed OLC row projection without an upstream clone."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

COMMIT = "5cdaa95f0a4b1428a05480cc1c69d556a8f9517a"
REPOSITORY = "https://github.com/sorenson64/olc"
SELECTOR = r"^(bigdawg|phi)/data[^/]*/[^/]+\.out$"
PATH_RE = re.compile(SELECTOR)
HEADER = "source_path\tsource_line\tnbegin\tnend\tfound\tR0\tR1\tR2\tR3\tR4\n"
PUBLISHED_N = 70_500_000_000_000


def merge_coverage(intervals: set[tuple[int, int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        elif end > merged[-1][1]:
            merged[-1][1] = end
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    raw_projection = gzip.decompress(args.rows.read_bytes())
    lines = raw_projection.decode("ascii").splitlines()
    if not lines or lines[0] + "\n" != HEADER:
        raise AssertionError("unexpected projection header")

    intervals: list[tuple[int, int]] = []
    starts: dict[int, set[int]] = defaultdict(set)
    program_files: Counter[str] = Counter()
    program_rows: Counter[str] = Counter()
    seen_files: set[str] = set()
    previous_path = ""
    previous_line = 0
    previous_found = 0
    bucket_failures = 0
    delta_failures = 0

    for projected in lines[1:]:
        fields = projected.split("\t")
        if len(fields) != 10:
            raise AssertionError("malformed projected row")
        path = fields[0]
        if not PATH_RE.fullmatch(path):
            raise AssertionError(f"path outside selector: {path}")
        line_number, nbegin, nend, found, r0, r1, r2, r3, r4 = map(int, fields[1:])
        if path < previous_path or (path == previous_path and line_number <= previous_line):
            raise AssertionError("projection is not in canonical source order")
        if path != previous_path:
            previous_found = 0
            previous_line = 0
            if path in seen_files:
                raise AssertionError("a source file occurs in two blocks")
            seen_files.add(path)
            program_files[path.split("/", 1)[0]] += 1
        if not nbegin < nend:
            raise AssertionError("empty or reversed projected interval")
        if found != r0 + r1 + r2 + r3 + r4:
            bucket_failures += 1
        if found - previous_found != 2 * (nend - nbegin):
            delta_failures += 1
        previous_path = path
        previous_line = line_number
        previous_found = found
        intervals.append((nbegin, nend))
        starts[nbegin].add(nend)
        program_rows[path.split("/", 1)[0]] += 1

    unique_intervals = set(intervals)
    components = merge_coverage(unique_intervals)
    holes = [[left[1], right[0]] for left, right in zip(components, components[1:])]
    derived = {
        "projection_sha256": hashlib.sha256(raw_projection).hexdigest(),
        "file_count": len(seen_files),
        "row_count": len(intervals),
        "program_file_counts": dict(sorted(program_files.items())),
        "program_row_counts": dict(sorted(program_rows.items())),
        "unique_start_count": len(starts),
        "conflicting_start_count": sum(len(ends) > 1 for ends in starts.values()),
        "unique_interval_count": len(unique_intervals),
        "duplicate_interval_rows": len(intervals) - len(unique_intervals),
        "bucket_invariant_failures": bucket_failures,
        "delta_invariant_failures": delta_failures,
        "min_begin": min(begin for begin, _ in unique_intervals),
        "max_end_exclusive": max(end for _, end in unique_intervals),
        "covered_n_count": sum(end - begin for begin, end in components),
        "coverage_components": components,
        "coverage_holes": holes,
        "public_projection_reaches_published_N": components[-1][1] > PUBLISHED_N,
    }
    expected_constants = {
        "schema": "landau-legendre.olc-public-audit.v1",
        "repository": REPOSITORY,
        "commit": COMMIT,
        "selector": SELECTOR,
        "published_N": PUBLISHED_N,
    }
    for key, value in expected_constants.items():
        if summary.get(key) != value:
            raise AssertionError(f"unexpected summary constant {key}")
    for key, value in derived.items():
        if summary.get(key) != value:
            raise AssertionError(f"summary mismatch for {key}")
    for digest_key in ("source_manifest_sha256", "projection_sha256"):
        digest = summary.get(digest_key)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise AssertionError(f"malformed digest {digest_key}")
    if not isinstance(summary.get("source_blob_bytes"), int) or summary["source_blob_bytes"] <= 0:
        raise AssertionError("invalid source byte count")
    if summary.get("ignored_nonrecord_lines") != 0:
        raise AssertionError("unexpected ignored worker-log lines")
    if bucket_failures or delta_failures:
        raise AssertionError("a projected worker invariant failed")
    print(
        "PASS olc_public_projection",
        f"files={len(seen_files)}",
        f"rows={len(intervals)}",
        f"components={len(components)}",
        f"holes={len(holes)}",
        f"max_end={components[-1][1]}",
        "scope=committed-projection-only",
    )


if __name__ == "__main__":
    main()
