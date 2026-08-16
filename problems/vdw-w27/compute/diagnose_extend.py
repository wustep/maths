#!/usr/bin/env python3
"""List the 7-APs that block each color of position 3704 on the 3703 residue coloring."""

from __future__ import annotations

import json
from pathlib import Path

from vdw import enumerate_new_aps_through, load_coloring

HERE = Path(__file__).resolve().parent


def main() -> None:
    prefix = load_coloring(str(HERE / "coloring_3703.txt"))
    n = len(prefix) + 1
    point = n - 1
    blocked = {0: [], 1: []}
    for color in (0, 1):
        colors = prefix + [color]
        for ap in enumerate_new_aps_through(n, point, 7):
            c0 = colors[ap[0]]
            if all(colors[j] == c0 for j in ap[1:]):
                blocked[color].append(
                    {
                        "diff": ap[1] - ap[0],
                        "points_1based": [p + 1 for p in ap],
                        "color": c0,
                    }
                )
    payload = {
        "prefix_length": len(prefix),
        "blocked_color0": blocked[0],
        "blocked_color1": blocked[1],
    }
    (HERE / "extend_obstruction.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="ascii"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
