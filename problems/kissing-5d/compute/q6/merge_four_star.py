#!/usr/bin/env python3
"""Merge the two C 4-star shards and check the 210-pool census."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    a = json.loads((HERE / "four_star_extras_s0.json").read_text())
    b = json.loads((HERE / "four_star_extras_s1.json").read_text())
    pools = a["pools"] + b["pools"]
    keys = [tuple(p["stars"]) for p in pools]
    assert len(keys) == 210, len(keys)
    assert len(set(keys)) == 210
    assert all(p["complete"] and not p["found_41"] and p["best"] == 19 for p in pools)
    report = {
        "n_pools": 210,
        "n_expected": 210,
        "n_bb_complete_empty": 210,
        "n_incomplete": 0,
        "n_hit": 0,
        "max_best": 19,
        "tot_nodes": a["tot_nodes"] + b["tot_nodes"],
        "found_41": False,
        "shards": [a["shard"], b["shard"]],
        "node_limit": a["node_limit"],
        "pools": pools,
        "comment": (
            "Merged C leftover-tight B&B on every 4-star leftover pool.  "
            "complete+empty is no leftover 41-set hosted by four "
            "coordinate-stars (not a claim on extras ω).  Did not claim "
            "tau5=40."
        ),
    }
    (HERE / "four_star_extras.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n_pools": 210,
        "n_bb_complete_empty": 210,
        "max_best": 19,
        "tot_nodes": report["tot_nodes"],
        "found_41": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
