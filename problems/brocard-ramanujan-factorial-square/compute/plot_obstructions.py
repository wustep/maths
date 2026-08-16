#!/usr/bin/env python3
"""Plot the finite modular cover and the large-slice survivor decay."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
PROBLEM_ROOT = HERE.parent
REPO_ROOT = PROBLEM_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from maths.figures import save, style  # noqa: E402


def main() -> None:
    data = json.loads((HERE / "q1-results.json").read_text())
    cover = data["small_modular_cover"]
    selected = cover["selected"]
    lower, upper = cover["range_inclusive"]
    ns = np.arange(lower, upper + 1)
    matrix = np.array(
        [[1 if int(n) in item["all_bad_n"] else 0 for n in ns] for item in selected]
    )

    style()
    fig, (cover_ax, decay_ax) = plt.subplots(
        2,
        1,
        figsize=(9.0, 6.8),
        gridspec_kw={"height_ratios": [1.05, 1.0], "hspace": 0.42},
    )

    cover_ax.imshow(
        matrix,
        aspect="auto",
        interpolation="nearest",
        extent=(lower - 0.5, upper + 0.5, len(selected) - 0.5, -0.5),
        cmap=colors.ListedColormap(["#f3f4f6", "#2563eb"]),
    )
    cover_ax.set_yticks(range(len(selected)))
    cover_ax.set_yticklabels([f"p = {item['prime']}" for item in selected])
    cover_ax.set_xlabel("n")
    cover_ax.set_title("Four exact moduli cover every n from 8 through 150")
    cover_ax.grid(False)
    cover_ax.axvspan(15.5, 31.5, facecolor="none", edgecolor="#dc2626", linewidth=1.8)
    cover_ax.text(
        23.5,
        len(selected) - 0.58,
        "maximal p=151 run: 16–31",
        ha="center",
        va="bottom",
        color="#b91c1c",
        fontsize=9,
    )

    large = data["berndt_galway_method_slice"]
    survivor_counts = [large["start_count"]] + [step["survivors"] for step in large["steps"]]
    display_counts = [max(0.5, count) for count in survivor_counts]
    prime_numbers = [0] + list(range(1, len(large["steps"]) + 1))
    decay_ax.plot(prime_numbers, display_counts, marker="o", markersize=4, color="#7c3aed")
    decay_ax.set_yscale("log")
    decay_ax.set_xlabel("number of prime moduli applied")
    decay_ax.set_ylabel("surviving n (log scale)")
    decay_ax.set_title(
        f"Berndt–Galway residue sieve on 8 ≤ n ≤ {large['range_inclusive'][1]:,}"
    )
    if large["survivor_count"] == 0:
        decay_ax.annotate(
            "0 survivors",
            xy=(prime_numbers[-1], display_counts[-1]),
            xytext=(-75, 22),
            textcoords="offset points",
            arrowprops={"arrowstyle": "->", "color": "#4c1d95"},
            color="#4c1d95",
        )

    output = PROBLEM_ROOT / "figures" / "q1-modular-obstructions.png"
    save(output, fig)
    print(output)


if __name__ == "__main__":
    main()
