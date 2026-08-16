#!/usr/bin/env python3
"""Independent exact verifier for a finite seven-color Schur coloring."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from time import monotonic


def read_colors(path: Path) -> list[int]:
    tokens = path.read_text(encoding="ascii").split()
    try:
        colors = [int(token) for token in tokens]
    except ValueError as exc:
        raise ValueError(f"{path} contains a non-integer token") from exc
    if not colors:
        raise ValueError(f"{path} is empty")
    bad = [(index + 1, color) for index, color in enumerate(colors) if color not in range(7)]
    if bad:
        index, color = bad[0]
        raise ValueError(f"c({index})={color}, outside the required range 0..6")
    return colors


def verify(colors: list[int]) -> int:
    """Return the number of checked pairs, or raise on the first violation."""
    checked = 0
    n = len(colors)
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            checked += 1
            z = x + y
            if colors[x - 1] == colors[y - 1] == colors[z - 1]:
                raise ValueError(
                    f"monochromatic Schur triple ({x}, {y}, {z}) "
                    f"in color {colors[x - 1]}"
                )
    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("coloring", type=Path)
    parser.add_argument(
        "--expect-length",
        type=int,
        help="reject a coloring whose interval length is not exactly this value",
    )
    args = parser.parse_args()

    started = monotonic()
    colors = read_colors(args.coloring)
    if args.expect_length is not None and len(colors) != args.expect_length:
        raise ValueError(
            f"expected {args.expect_length} colors, found {len(colors)} in {args.coloring}"
        )
    checked = verify(colors)
    counts = Counter(colors)
    print(
        json.dumps(
            {
                "coloring": str(args.coloring),
                "interval": f"1..{len(colors)}",
                "colors": 7,
                "class_sizes": [counts[color] for color in range(7)],
                "schur_pairs_checked": checked,
                "elapsed_seconds": round(monotonic() - started, 6),
                "result": "valid",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
