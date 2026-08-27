#!/usr/bin/env python3
"""Independently verify every least-prime witness and the near-miss table."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path

START_N = 2**32 - 100_000
END_N = 2**32 - 1
PRIME_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
PSI_12 = 318_665_857_834_031_151_167_461


def is_prime_u64(value: int) -> bool:
    if value < 2:
        return False
    if value >= 2**64 or value >= PSI_12:
        raise AssertionError("primality input is outside the certified range")
    for prime in PRIME_BASES:
        if value % prime == 0:
            return value == prime
    odd_part = value - 1
    twos = 0
    while odd_part % 2 == 0:
        odd_part //= 2
        twos += 1
    for base in PRIME_BASES:
        residue = pow(base, odd_part, value)
        if residue in (1, value - 1):
            continue
        for _ in range(twos - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


def least_prime_after(left: int, right: int) -> int:
    candidate = left + 1
    if candidate <= 2 < right:
        return 2
    if candidate % 2 == 0:
        candidate += 1
    while candidate < right:
        if is_prime_u64(candidate):
            return candidate
        candidate += 2
    raise AssertionError(f"no prime found in ({left}, {right})")


def make_entry(half: str, n: int, offset: int) -> dict[str, int | str]:
    width = n if half == "left" else n + 1
    endpoint = n * n if half == "left" else n * (n + 1)
    return {
        "half": half,
        "n": n,
        "offset": offset,
        "width": width,
        "prime": endpoint + offset,
        "slack": width - offset,
    }


def top_entries(items: list[dict[str, int | str]], count: int) -> list[dict[str, int | str]]:
    return sorted(
        items,
        key=lambda item: (
            -Fraction(int(item["offset"]), int(item["width"])),
            int(item["n"]),
        ),
    )[:count]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    claimed = json.loads(args.summary.read_text(encoding="utf-8"))
    if claimed.get("schema") != "landau-legendre.oppermann-edge.v1":
        raise AssertionError("unexpected summary schema")
    if claimed.get("start_n") != START_N or claimed.get("end_n") != END_N:
        raise AssertionError("unexpected certified range")
    top_count = claimed.get("top_count")
    if not isinstance(top_count, int) or top_count <= 0:
        raise AssertionError("invalid top_count")

    raw = args.csv.read_bytes()
    left_entries: list[dict[str, int | str]] = []
    right_entries: list[dict[str, int | str]] = []
    expected_n = START_N
    with args.csv.open(newline="", encoding="ascii") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["n", "left_offset", "right_offset"]:
            raise AssertionError("unexpected CSV header")
        for row in reader:
            n = int(row["n"])
            if n != expected_n:
                raise AssertionError(f"missing or duplicate n before {n}")
            left_offset = int(row["left_offset"])
            right_offset = int(row["right_offset"])
            square = n * n
            middle = n * (n + 1)
            next_square = (n + 1) * (n + 1)
            if not 0 < left_offset < n or not 0 < right_offset < n + 1:
                raise AssertionError(f"invalid strict offset at n={n}")
            if least_prime_after(square, middle) != square + left_offset:
                raise AssertionError(f"left witness is not least at n={n}")
            if least_prime_after(middle, next_square) != middle + right_offset:
                raise AssertionError(f"right witness is not least at n={n}")
            left_entries.append(make_entry("left", n, left_offset))
            right_entries.append(make_entry("right", n, right_offset))
            expected_n += 1
    if expected_n != END_N + 1:
        raise AssertionError("wrong CSV row count or endpoint")

    expected = {
        "schema": "landau-legendre.oppermann-edge.v1",
        "start_n": START_N,
        "end_n": END_N,
        "row_count": END_N - START_N + 1,
        "csv_sha256": hashlib.sha256(raw).hexdigest(),
        "top_count": top_count,
        "left_top": top_entries(left_entries, top_count),
        "right_top": top_entries(right_entries, top_count),
    }
    if claimed != expected:
        raise AssertionError("summary or near-miss ranking does not match verified rows")
    left_max = expected["left_top"][0]
    right_max = expected["right_top"][0]
    print(
        "PASS edge_slice",
        f"rows={expected['row_count']}",
        f"left_max={left_max['offset']}/{left_max['width']}@{left_max['n']}",
        f"right_max={right_max['offset']}/{right_max['width']}@{right_max['n']}",
    )


if __name__ == "__main__":
    main()
