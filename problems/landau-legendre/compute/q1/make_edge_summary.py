#!/usr/bin/env python3
"""Derive the hash and exact near-miss rankings from an edge CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path

START_N = 2**32 - 100_000
END_N = 2**32 - 1


def entry(half: str, n: int, offset: int) -> dict[str, int | str]:
    width = n if half == "left" else n + 1
    left_endpoint = n * n if half == "left" else n * (n + 1)
    return {
        "half": half,
        "n": n,
        "offset": offset,
        "width": width,
        "prime": left_endpoint + offset,
        "slack": width - offset,
    }


def rank(items: list[dict[str, int | str]], top_count: int) -> list[dict[str, int | str]]:
    return sorted(
        items,
        key=lambda item: (
            -Fraction(int(item["offset"]), int(item["width"])),
            int(item["n"]),
        ),
    )[:top_count]


def build_summary(csv_path: Path, top_count: int) -> dict[str, object]:
    raw = csv_path.read_bytes()
    left: list[dict[str, int | str]] = []
    right: list[dict[str, int | str]] = []
    expected_n = START_N
    with csv_path.open(newline="", encoding="ascii") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["n", "left_offset", "right_offset"]:
            raise AssertionError("unexpected CSV header")
        for row in reader:
            n = int(row["n"])
            left_offset = int(row["left_offset"])
            right_offset = int(row["right_offset"])
            if n != expected_n:
                raise AssertionError(f"nonconsecutive n at {n}")
            if not 0 < left_offset < n or not 0 < right_offset < n + 1:
                raise AssertionError(f"offset outside a half-interval at n={n}")
            left.append(entry("left", n, left_offset))
            right.append(entry("right", n, right_offset))
            expected_n += 1
    if expected_n != END_N + 1:
        raise AssertionError("CSV has the wrong final n")
    return {
        "schema": "landau-legendre.oppermann-edge.v1",
        "start_n": START_N,
        "end_n": END_N,
        "row_count": END_N - START_N + 1,
        "csv_sha256": hashlib.sha256(raw).hexdigest(),
        "top_count": top_count,
        "left_top": rank(left, top_count),
        "right_top": rank(right, top_count),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()
    if args.top <= 0:
        raise SystemExit("--top must be positive")
    payload = json.dumps(build_summary(args.csv, args.top), indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
