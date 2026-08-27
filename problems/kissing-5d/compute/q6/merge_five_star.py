#!/usr/bin/env python3
"""Merge the two C 5-star shards."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    a = json.loads((HERE / "five_star_extras_s0.json").read_text())
    b = json.loads((HERE / "five_star_extras_s1.json").read_text())
    pools = a["pools"] + b["pools"]
    keys = [tuple(p["stars"]) for p in pools]
    n_complete = sum(1 for p in pools if p["complete"] and not p["found_41"])
    n_incomplete = sum(1 for p in pools if not p["complete"] and not p["found_41"])
    n_hit = sum(1 for p in pools if p["found_41"])
    report = {
        "n_pools": len(pools),
        "n_expected": 252,
        "n_unique": len(set(keys)),
        "n_bb_complete_empty": n_complete,
        "n_incomplete": n_incomplete,
        "n_hit": n_hit,
        "max_best": max(p["best"] for p in pools) if pools else 0,
        "tot_nodes": a.get("tot_nodes", 0) + b.get("tot_nodes", 0),
        "found_41": bool(n_hit),
        "shards": [a["shard"], b["shard"]],
        "node_limit": a["node_limit"],
        "pools": pools,
        "comment": (
            "Merged C leftover-tight B&B on 5-star pools.  "
            "complete+empty is no leftover 41-set in that pool, not ω.  "
            "Did not claim tau5=40."
        ),
    }
    (HERE / "five_star_extras.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "n_pools": report["n_pools"],
        "n_unique": report["n_unique"],
        "n_bb_complete_empty": n_complete,
        "n_incomplete": n_incomplete,
        "n_hit": n_hit,
        "max_best": report["max_best"],
        "found_41": report["found_41"],
    }, indent=2))
    return 0 if n_hit == 0 and len(set(keys)) == len(keys) else 1


if __name__ == "__main__":
    raise SystemExit(main())
