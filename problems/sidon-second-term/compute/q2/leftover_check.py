#!/usr/bin/env python3
"""Confirm that q1 refine / dropped-symmetry never finished.

Stdlib only. Reads ../q1/search.jsonl. Incomplete search is not a bound.
"""

from __future__ import annotations

import json
from pathlib import Path

Q1_LOG = Path(__file__).resolve().parents[1] / "q1" / "search.jsonl"


def main() -> None:
    tags = [json.loads(line).get("tag") for line in Q1_LOG.read_text().splitlines()]
    starts = {"nosym-start", "refine-start"}
    finished = {"nosym-lbfgs-L6", "nosym-meta", "refine-lbfgs"}
    present_start = starts & set(tags)
    present_fin = finished & set(tags)
    has_finer = any(t and str(t).startswith("finer") for t in tags)
    has_widths = any(t and str(t).startswith("widths") for t in tags)
    print("q1_rows", len(tags))
    print("starts", sorted(present_start))
    print("finished", sorted(present_fin))
    print("has_finer", has_finer)
    print("has_widths", has_widths)
    if present_start != starts or present_fin:
        raise SystemExit("FAIL q1 refine/nosym not in the expected incomplete state")
    if has_finer or has_widths:
        raise SystemExit("FAIL unexpected finer/widths rows in q1 log")
    print("q1 refine and nosym are incomplete (residue, not a bound)")
    print("PASS")


if __name__ == "__main__":
    main()
