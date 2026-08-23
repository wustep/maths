#!/usr/bin/env python3
"""Independent exact audit of the preserved q3 two-violation residue."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


EXPECTED_SHA256 = "539c5240eacc3c33fbc0543fb0767d8f4f8a5ca163941a695b21a53b09044db1"
EXPECTED_VIOLATIONS = [
    [537, 537, 1074, 6],
    [537, 640, 1177, 6],
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("coloring", type=Path)
    args = parser.parse_args()

    raw = args.coloring.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"unexpected SHA-256 {digest}")
    colors = [int(token) for token in raw.split()]
    if len(colors) != 1697 or any(color not in range(7) for color in colors):
        raise ValueError("expected exactly 1697 colors in 0..6")

    checked = 0
    bad: list[list[int]] = []
    for x in range(1, len(colors) + 1):
        for y in range(x, len(colors) - x + 1):
            checked += 1
            z = x + y
            if colors[x - 1] == colors[y - 1] == colors[z - 1]:
                bad.append([x, y, z, colors[x - 1]])
    if bad != EXPECTED_VIOLATIONS:
        raise ValueError(f"unexpected violations {bad}")

    counts = Counter(colors)
    print(
        json.dumps(
            {
                "class_sizes": [counts[color] for color in range(7)],
                "coloring": str(args.coloring),
                "length": len(colors),
                "pairs_checked": checked,
                "result": "residue-two-violations",
                "sha256": digest,
                "violations": bad,
                "warning": "This is not a Schur coloring and proves no lower bound.",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
