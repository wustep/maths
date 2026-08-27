#!/usr/bin/env python3
"""Turn C enumerator stdout into the JSON certificates verify_winners reads."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def parse_broken(cell: str) -> list[int]:
    if cell in ("-", "", "None"):
        return []
    return [int(x) for x in cell.split(",") if x != ""]


def parse_frac(cell: str) -> list[int]:
    a, b = cell.split("/")
    return [int(a), int(b)]


def parse_down(cell: str) -> list[int] | None:
    if cell in ("-", ""):
        return None
    return [int(x) for x in cell.split(",")]


def collect_ladder(path: Path) -> dict:
    rows = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("n\t"):
            continue
        n, mn, broken, e, n_non, n_below = line.split("\t")
        rows.append(
            {
                "n": int(n),
                "min_delta": parse_frac(mn),
                "broken": parse_broken(broken),
                "e": int(e),
                "n_non_sum": int(n_non),
                "n_below_1_3": int(n_below),
                "source": "C exhaustive; Python replay of the witness",
            }
        )
    return {
        "census": rows,
        "note": "Non-sum broken-rung ladder minima. Stamp-based C enumerator.",
    }


def collect_rail(path: Path) -> dict:
    rows = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("n\t"):
            continue
        n, mn, b4, b5, e, n_non, n617, n13 = line.split("\t")
        rows.append(
            {
                "n": int(n),
                "min_delta": parse_frac(mn),
                "broken4": parse_broken(b4),
                "broken5": parse_broken(b5),
                "e": int(e),
                "n_non_sum": int(n_non),
                "n_below_6_17": int(n617),
                "n_below_1_3": int(n13),
                "complete": True,
            }
        )
    return {
        "exhaustive": rows,
        "note": "Three-rail non-sum minima. C exhaustive.",
    }


def collect_interval(path: Path) -> dict:
    rows = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("n\t"):
            continue
        parts = line.split("\t")
        (
            n,
            n_all,
            n_non,
            n_ns,
            mn,
            min_e,
            min_ns,
            min_ns_e,
            n_below,
            min_down,
            min_ns_down,
        ) = parts
        row = {
            "n": int(n),
            "n_natural_interval": int(n_all),
            "n_nonchain": int(n_non),
            "n_not_semiorder": int(n_ns),
            "n_below_1_3": int(n_below),
            "min_delta": parse_frac(mn),
            "min_e": int(min_e),
            "min_down": parse_down(min_down),
            "complete": True,
        }
        if min_ns != "-":
            row["min_not_semi"] = parse_frac(min_ns)
            row["min_ns_e"] = int(min_ns_e)
            row["min_not_semi_down"] = parse_down(min_ns_down)
        rows.append(row)
    return {"census": rows, "oeis": "A367494"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("ladder", "rail", "interval"))
    ap.add_argument("log")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    src = Path(args.log)
    if args.kind == "ladder":
        blob = collect_ladder(src)
        dest = Path(args.out) if args.out else HERE / "ladder_census.json"
    elif args.kind == "rail":
        blob = collect_rail(src)
        dest = Path(args.out) if args.out else HERE / "three_rail.json"
    else:
        blob = collect_interval(src)
        dest = Path(args.out) if args.out else HERE / "interval_orders.json"
    dest.write_text(json.dumps(blob, indent=2) + "\n")
    print(f"wrote {dest} ({len(blob.get('census') or blob.get('exhaustive'))} rows)")


if __name__ == "__main__":
    main()
