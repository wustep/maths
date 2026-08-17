#!/usr/bin/env python3
"""Print the best floating gammas from search_results.jsonl."""

from __future__ import annotations

import json
from pathlib import Path

rows = []
p = Path(__file__).resolve().parent / "search_results.jsonl"
if p.exists():
    for line in p.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))

print(f"n_records {len(rows)}")
if not rows:
    raise SystemExit(0)

rows.sort(key=lambda r: r.get("gamma", 1e9))
print("top 15")
for r in rows[:15]:
    print(f"  {r.get('gamma'):.12f}  {r.get('tag')}  R={r.get('R')} m={r.get('m')} L={r.get('L')}")

hz = [r for r in rows if r.get("tag", "").startswith("table1-R8") or "hz-r8-m32-L4" in r.get("tag", "")]
print("published_replay", hz[0]["gamma"] if hz else None)
print("best", rows[0]["gamma"], rows[0]["tag"])
print("best_minus_0.94349259", rows[0]["gamma"] - 0.94349259)
