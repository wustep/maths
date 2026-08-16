#!/usr/bin/env python3
"""Schematic of the n=71 rct4 reduction and the bounded UNKNOWN runs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "n71-rct4-residue.png"


def box(ax, xy, w, h, text, fc="#edf2f7"):
    patch = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.08", linewidth=1.0, edgecolor="#2d3748", facecolor=fc)
    ax.add_patch(patch)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=8.5, color="#1a202c")


def main() -> None:
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.2, 4.4))

    ax0.set_xlim(0, 10)
    ax0.set_ylim(0, 10)
    ax0.axis("off")
    ax0.set_title("Canonical rct4 reduction at n=71")
    box(ax0, (1.2, 8.1), 7.6, 1.3, "71×71 board\nanti-diagonal fixed empty")
    box(ax0, (1.2, 5.9), 7.6, 1.5, "1,225 four-orbits + 35 two-orbits\n= 1,260 Boolean variables")
    box(ax0, (1.2, 3.7), 7.6, 1.5, "1,074,372 maximal lines\n→ 281,834 weighted inequalities")
    box(ax0, (1.2, 1.5), 7.6, 1.5, "CNF: 792,274 vars, 1,931,230 clauses\nneed 35·4 + 1·2 = 142 points")
    for y0, y1 in ((8.1, 7.4), (5.9, 5.2), (3.7, 3.0)):
        ax0.annotate("", xy=(5, y1), xytext=(5, y0), arrowprops=dict(arrowstyle="->", color="#4a5568", lw=1.2))

    labels = ["CP-SAT\nunrestricted", "Kissat\ndiag 6", "Kissat\ndiag 7", "Kissat\ndiag 8", "CaDiCaL\nunrestricted"]
    times = [301.1, 120.15, 120.13, 120.15, 120.14]
    colors = ["#c05621"] + ["#2b6cb0"] * 4
    ax1.bar(range(len(times)), times, color=colors, width=0.72)
    ax1.set_xticks(range(len(times)), labels, fontsize=7.5)
    ax1.set_ylabel("measured wall seconds")
    ax1.set_title("Every bounded run ended UNKNOWN")
    ax1.set_ylim(0, 360)
    for i, t in enumerate(times):
        ax1.text(i, t + 8, f"{t:.1f}s\nUNKNOWN", ha="center", va="bottom", fontsize=7, color="#2d3748")
    ax1.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
