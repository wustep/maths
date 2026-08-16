#!/usr/bin/env python3
"""Color 3704 as 0 after flipping one 2-class point; report leftover 7-APs."""

from __future__ import annotations

import json
from pathlib import Path

from vdw import first_mono_ap, load_coloring

HERE = Path(__file__).resolve().parent
# 0-based indices of the d=617 AP through 3703 (the new last point)
# 1-based: 2,619,1236,1853,2470,3087,3704
BLOCK = [1, 618, 1235, 1852, 2469, 3086]  # exclude the new point


def main() -> None:
    seed = load_coloring(str(HERE / "coloring_3703.txt"))
    rows = []
    for pos in BLOCK:
        colors = seed[:]
        colors[pos] ^= 1
        colors.append(0)
        hit = first_mono_ap(colors, 7)
        rows.append(
            {
                "flip_1based": pos + 1,
                "ok": hit is None,
                "hit": None if hit is None else {"start": hit[0] + 1, "diff": hit[1]},
            }
        )
        print(rows[-1], flush=True)
    (HERE / "single_class_flip.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
