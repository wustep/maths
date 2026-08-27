#!/usr/bin/env python3
"""Replay every committed ladder-census row from its broken-rung set."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ladders import named, PUBLISHED  # noqa: E402


def main():
    blob = json.loads((HERE / "ladder_census.json").read_text())
    for row in blob["census"]:
        got = named(row["n"], tuple(row["broken"]))
        if got["delta"] != row["min_delta"] or got["e"] != row["e"]:
            raise AssertionError(f"n={row['n']}: {got} vs {row}")
        if got["n_summands"] != 1:
            raise AssertionError(f"n={row['n']} splits")
        pub = PUBLISHED.get(row["n"])
        if pub and pub[0] and row["n"] <= 14:
            if tuple(row["min_delta"]) != pub[0]:
                raise AssertionError(f"n={row['n']} drifted from Gupta Table 1")
        print(
            f"n={row['n']} {row['min_delta'][0]}/{row['min_delta'][1]} "
            f"L_{row['n']},{','.join(map(str, row['broken']))} e={row['e']} OK"
        )
    print("LADDER TABLE OK", len(blob["census"]), "rows")


if __name__ == "__main__":
    main()
