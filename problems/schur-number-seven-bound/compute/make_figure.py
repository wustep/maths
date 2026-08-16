#!/usr/bin/env python3
"""Draw the exceptional orbit in the reflection template for [1697]."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from maths.figures import save, style


def main() -> None:
    style()
    fig, ax = plt.subplots(figsize=(8.4, 4.7))

    ax.hlines(0, 1, 1697, color="#667085", linewidth=2)
    ax.scatter([566, 1132], [0, 0], s=130, color="#2563eb", zorder=5)
    ax.axvline(849, color="#98a2b3", linestyle="--", linewidth=1.4)
    ax.text(849, 0.08, "mirror midpoint 849", ha="center", color="#475467")

    reflection = FancyArrowPatch(
        (566, 0.03),
        (1132, 0.03),
        connectionstyle="arc3,rad=-0.42",
        arrowstyle="<->",
        mutation_scale=14,
        linewidth=2.2,
        color="#2563eb",
    )
    addition = FancyArrowPatch(
        (566, -0.03),
        (1132, -0.03),
        connectionstyle="arc3,rad=0.42",
        arrowstyle="->",
        mutation_scale=14,
        linewidth=2.2,
        color="#d92d20",
    )
    ax.add_patch(reflection)
    ax.add_patch(addition)

    ax.text(849, 0.32, r"reflection: $c(566)=c(1698-566)=c(1132)$",
            ha="center", color="#175cd3", weight="bold")
    ax.text(849, -0.34, r"addition: $566+566=1132$ forces $c(566)\ne c(1132)$",
            ha="center", color="#b42318", weight="bold")
    ax.text(
        849,
        -0.59,
        "Therefore the orbit {566, 1132} must be split; all other reflection pairs may remain folded.",
        ha="center",
        va="center",
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "#fffaeb", "edgecolor": "#f79009"},
    )

    ax.set_title("The exact obstruction to full reflection symmetry on [1697]")
    ax.set_xlim(-20, 1720)
    ax.set_ylim(-0.75, 0.62)
    ax.set_xticks([1, 566, 849, 1132, 1697])
    ax.set_yticks([])
    ax.set_xlabel("integer in the interval")
    ax.grid(axis="x", alpha=0.22)

    destination = Path(__file__).resolve().parents[1] / "figures" / "q1-symmetry-obstruction.png"
    save(destination, fig)
    print(destination)


if __name__ == "__main__":
    main()
