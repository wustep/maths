#!/usr/bin/env python3
"""Dump the 355-point T^5 remainder for the C searches."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from graphio import write_adj
from t5_36 import build_pool


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    write_adj(HERE / "t5_355_adj.txt", adj, n)
    pub = {}
    for name, rec in G["published"].items():
        pub[name] = {
            "remainder_size": rec["remainder_size"],
            "remainder_clique": rec["remainder_clique"],
        }
    (HERE / "t5_published.json").write_text(json.dumps(pub, indent=2) + "\n")
    print(f"n={n} wrote t5_355_adj.txt t5_published.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
