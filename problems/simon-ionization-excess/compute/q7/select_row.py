#!/usr/bin/env python3
"""Pick the best certified compact row (smallest split_inv with cut>γ)."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q6_LEAD = 1.1026


def load_rows() -> list[dict]:
    rows = []
    for p in sorted(CERTS.glob("raise_*.json")):
        blob = json.loads(p.read_text())
        blob["_path"] = str(p.relative_to(HERE))
        rows.append(blob)
    return rows


def best_row() -> dict:
    ok = []
    for r in load_rows():
        if not r.get("certified"):
            continue
        g = r.get("compact_gamma")
        cut = r.get("cut")
        inv = r.get("split_inv")
        if g is None or cut is None or inv is None:
            continue
        if cut <= g:
            continue
        if inv >= Q6_LEAD:
            continue
        ok.append(r)
    if not ok:
        raise SystemExit("no certified row beats 1.1026")
    ok.sort(key=lambda r: r["split_inv"])
    return ok[0]


def main() -> None:
    row = best_row()
    print(
        f"best R={row['R']} n={row['n']} target={row['target']} "
        f"γ={row['compact_gamma']:.8f} 1/γ={row['split_inv']:.8f}"
    )
    print("path", row["_path"])


if __name__ == "__main__":
    main()
