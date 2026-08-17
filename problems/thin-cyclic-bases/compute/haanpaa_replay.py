#!/usr/bin/env python3
"""Replay Haanpää 2004 Table 3 cyclic sum covers (published small-n record)."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import is_sum_cover, counting_lower

# Haanpää, J. Integer Seq. 7 (2004), Table 3 — cyclic rows only.
TABLE = [
    (3, [0, 1]),
    (5, [0, 1, 2]),
    (9, [0, 1, 3, 4]),
    (13, [0, 1, 2, 6, 9]),
    (19, [0, 1, 3, 12, 14, 15]),
    (21, [0, 1, 3, 7, 11, 15, 19]),
    (30, [0, 1, 3, 9, 11, 12, 16, 26]),
    (35, [0, 1, 3, 13, 15, 17, 27, 29, 30]),
    (43, [0, 1, 2, 3, 10, 15, 21, 25, 31, 36]),
    (51, [0, 1, 3, 7, 10, 15, 18, 22, 24, 25, 38]),
    (63, [0, 1, 3, 8, 12, 18, 22, 27, 29, 30, 43, 50]),
    (67, [0, 1, 2, 3, 4, 5, 6, 16, 24, 33, 40, 49, 57]),
]


def main():
    rows = []
    for n, A in TABLE:
        ok = is_sum_cover(A, n)
        m = len(set(A))
        rec = {
            "n": n,
            "m": m,
            "ok": ok,
            "ratio": m / math.sqrt(n),
            "counting": counting_lower(n),
            "A": A,
        }
        print(
            f"{'OK' if ok else 'FAIL'} n={n} m={m} ratio={rec['ratio']:.4f} "
            f"count={rec['counting']}"
        )
        rows.append(rec)
        if ok:
            Path("compute/certs").mkdir(parents=True, exist_ok=True)
            Path(f"compute/certs/haanpaa_n{n}.json").write_text(
                json.dumps(
                    {
                        "family": "haanpaa-2004-table3",
                        "n": n,
                        "m": m,
                        "A": A,
                        "ratio": rec["ratio"],
                    },
                    indent=2,
                )
            )
    Path("compute/haanpaa_replay.json").write_text(json.dumps(rows, indent=2))
    if not all(r["ok"] for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
