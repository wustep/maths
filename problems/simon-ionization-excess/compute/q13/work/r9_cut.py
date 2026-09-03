#!/usr/bin/env python3
"""R=9 with the mass-opt cut cannot beat printed 1.1010."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE.parent / "certs"
Q11_LEAD = 1.1010


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for R in (8.0, 9.0, 9.5, 9.8, 9.9, 10.0):
        cut = R / (R + 1.0)
        inv = 1.0 / cut
        rows.append(
            {
                "R": R,
                "cut": cut,
                "leading_if_cut_binds": inv,
                "beats_1.1010_if_cut_binds": bool(inv < Q11_LEAD),
            }
        )
    blob = {
        "status": "residue",
        "reason": (
            "At R<=9 the mass-opt cut R/(R+1) is at most 0.9, so "
            "min(gamma, cut) <= 0.9 and the leading is at least 1.1111. "
            "That cannot beat printed 1.1010. Dead without a sharper cut. "
            "q7--q11 already recorded the same wall against 1.1026, "
            "1.1021, 1.1020, 1.1017, 1.1013, and 1.1010."
        ),
        "q11_printed": "1.1010",
        "rows": rows,
    }
    out = CERTS / "r9_cut.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps(blob, indent=2))
    if any(r["beats_1.1010_if_cut_binds"] for r in rows if r["R"] <= 9.0):
        raise SystemExit("r9_cut.py unexpected: R<=9 cut beats 1.1010")
    print("r9_cut.py PASS (dead line: R<=9 cut cannot beat 1.1010)")


if __name__ == "__main__":
    main()
