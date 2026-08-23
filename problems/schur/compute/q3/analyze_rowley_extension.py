#!/usr/bin/env python3
"""Audit Rowley's 1696 coloring and all seven one-point extensions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def read_colors(path: Path) -> list[int]:
    colors = [int(token) for token in path.read_text(encoding="ascii").split()]
    if len(colors) != 1696 or any(color not in range(7) for color in colors):
        raise ValueError("expected exactly 1696 colors in 0..6")
    return colors


def violations(colors: list[int]) -> list[list[int]]:
    bad: list[list[int]] = []
    n = len(colors)
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            if colors[x - 1] == colors[y - 1] == colors[x + y - 1]:
                bad.append([x, y, x + y, colors[x - 1]])
    return bad


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("coloring", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    colors = read_colors(args.coloring)
    base_bad = violations(colors)
    if base_bad:
        raise ValueError(f"published base has violation {base_bad[0]}")

    reflection_mismatches = [
        [x, 1697 - x]
        for x in range(1, 849)
        if colors[x - 1] != colors[1697 - x - 1]
    ]
    extensions: list[dict[str, object]] = []
    for color in range(7):
        bad = violations(colors + [color])
        if any(z != 1697 or bad_color != color for _, _, z, bad_color in bad):
            raise AssertionError("the valid base acquired a non-boundary conflict")
        pairs = [[x, y] for x, y, _, _ in bad]
        touched = {value for pair in pairs for value in pair}
        if len(touched) != 2 * len(pairs):
            raise AssertionError("boundary conflicts are not vertex-disjoint")
        extensions.append(
            {
                "appended_color": color,
                "boundary_conflicts": len(bad),
                "disjoint_pair_edit_lower_bound": len(bad),
                "first_pairs": pairs[:10],
            }
        )

    audit = {
        "base_class_sizes": [Counter(colors)[color] for color in range(7)],
        "base_length": len(colors),
        "base_schur_pairs_checked": 719104,
        "extensions": extensions,
        "reflection_about_1697_mismatches": reflection_mismatches,
        "result": "no_direct_one_point_extension",
    }
    rendered = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
