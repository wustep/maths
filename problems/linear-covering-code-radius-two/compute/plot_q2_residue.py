#!/usr/bin/env python3
"""Plot the bounded q2 n=49 search outcomes and exact local barrier."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from maths.figures import save, style


def main() -> None:
    data = json.loads((HERE / "q2_search_results.json").read_text())
    short_names = [
        "direct\nanneal",
        "anneal +\nbreakout",
        "multi-\ncolumn",
        "tabu",
        "heavy\nperturb",
        "GL(10,2)\ncrossover",
        "lifted\nfrom q1",
        "lifted\nfrom 7",
    ]
    values = [run["best_uncovered"] for run in data["runs"]]

    style()
    fig, axis = plt.subplots(figsize=(10.8, 4.8))
    x_values = list(range(len(values)))
    colors = ["#dc2626" if value == min(values) else "#6b7280" for value in values]
    axis.plot(x_values, values, color="#9ca3af", linewidth=1.4, zorder=1)
    axis.scatter(x_values, values, c=colors, s=82, zorder=3)
    for x_value, value in zip(x_values, values, strict=True):
        axis.annotate(
            str(value),
            (x_value, value),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontweight="bold",
            color="#991b1b" if value == min(values) else "#374151",
        )

    axis.axhline(0, color="#2563eb", linestyle="--", linewidth=1.5, label="witness threshold")
    axis.axhline(20, color="#f59e0b", linestyle=":", linewidth=1.5,
                 label="best nontrivial one-swap from 7-hole residue")
    axis.annotate(
        "exact local barrier: every one-swap leaves —¥20",
        (6.95, 20),
        xytext=(-8, 7),
        textcoords="offset points",
        ha="right",
        color="#92400e",
        fontsize=9,
    )
    axis.set_xticks(x_values, short_names)
    axis.set_ylabel("uncovered syndromes (lower is better)")
    axis.set_ylim(-1, 22.5)
    axis.set_title("q2 bounded search for a 49-column radius-2 matrix")
    axis.legend(loc="upper left", frameon=False)
    fig.text(
        0.5,
        0.01,
        "A positive deficit is a search residue, not a nonexistence proof.",
        ha="center",
        color="#4b5563",
        fontsize=9,
    )
    fig.subplots_adjust(bottom=0.19)
    output = HERE.parent / "figures" / "q2_n49_search_residue.png"
    save(output, fig)
    print(output)


if __name__ == "__main__":
    main()
