#!/usr/bin/env python3
"""Plot the replayed n=71 certificate."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
WITNESS = HERE.parent / "n71-142.txt"
OUTPUT = HERE.parent.parent / "figures" / "n71-142.png"


def main() -> None:
    points = [tuple(map(int, line.split())) for line in WITNESS.read_text().splitlines() if line.strip()]
    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]

    figure, axis = plt.subplots(figsize=(7.2, 7.2))
    axis.scatter(x_values, y_values, s=17, color="#b42318", edgecolors="none", zorder=3)
    axis.set_xlim(-1, 71)
    axis.set_ylim(-1, 71)
    axis.set_aspect("equal")
    axis.set_xticks(range(0, 71, 10))
    axis.set_yticks(range(0, 71, 10))
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_title("Heule's n=71 rct4 configuration (142 points)")
    axis.grid(True, color="#d0d5dd", linewidth=0.5, alpha=0.7)
    for spine in axis.spines.values():
        spine.set_color("#667085")
    figure.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=180)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
