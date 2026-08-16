#!/usr/bin/env python3
"""Draw the n=71 rct4 encoding and timeout residue."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from maths.figures import save, style  # noqa: E402


HERE = Path(__file__).resolve().parent
PROBLEM = HERE.parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def box(ax, x: float, y: float, width: float, height: float, text: str, color: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.4,
        edgecolor=color,
        facecolor=color + "18",
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=10)


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "#4b5563"})


def main() -> int:
    cp = load("cpsat-seed-20260816.json")
    sat_runs = [
        load("kissat-d6-seed-6106.json"),
        load("kissat-d7-seed-7107.json"),
        load("kissat-d8-seed-8108.json"),
        load("cadical-seed-19572.json"),
    ]
    if cp["status"] != "UNKNOWN" or any(run["status"] != "UNKNOWN" for run in sat_runs):
        raise ValueError("this plot is specifically for the all-UNKNOWN residue")

    exemplar = sat_runs[-1]
    line_stats = exemplar["line_statistics"]
    style()
    fig, ax = plt.subplots(figsize=(9.2, 5.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    fig.suptitle("The n=71 canonical-rct4 search residue", fontsize=15, y=0.97)
    ax.text(
        0.5,
        0.90,
        "Exact geometric reduction and independently bounded solver runs; no SAT/UNSAT conclusion",
        ha="center",
        va="center",
        color="#374151",
        fontsize=10.5,
    )

    blue = "#2563eb"
    teal = "#0f766e"
    amber = "#b45309"
    red = "#b91c1c"

    box(ax, 0.04, 0.66, 0.19, 0.13, "71×71 grid\n5,041 cells", blue)
    box(
        ax,
        0.30,
        0.66,
        0.21,
        0.13,
        f"canonical rct4\n{exemplar['original_variables']:,} orbit variables",
        teal,
    )
    box(
        ax,
        0.58,
        0.66,
        0.17,
        0.13,
        f"{line_stats['maximal_lines']:,}\nmaximal lines",
        amber,
    )
    box(
        ax,
        0.81,
        0.66,
        0.15,
        0.13,
        f"{line_stats['retained_signatures']:,}\nunique inequalities",
        amber,
    )
    arrow(ax, (0.23, 0.725), (0.30, 0.725))
    arrow(ax, (0.51, 0.725), (0.58, 0.725))
    arrow(ax, (0.75, 0.725), (0.81, 0.725))

    box(
        ax,
        0.08,
        0.39,
        0.34,
        0.14,
        f"CP-SAT model\n{cp['solve_seconds']:.1f} s, 4 workers → UNKNOWN",
        red,
    )
    box(
        ax,
        0.58,
        0.39,
        0.34,
        0.14,
        f"DIMACS CNF\n{exemplar['cnf_variables']:,} vars · {exemplar['cnf_clauses']:,} clauses",
        teal,
    )
    arrow(ax, (0.405, 0.66), (0.25, 0.53))
    arrow(ax, (0.885, 0.66), (0.75, 0.53))

    labels = ["Kissat d=6", "Kissat d=7", "Kissat d=8", "CaDiCaL unrestricted"]
    x_positions = [0.04, 0.285, 0.53, 0.775]
    for x, label, run in zip(x_positions, labels, sat_runs, strict=True):
        box(
            ax,
            x,
            0.13,
            0.19,
            0.14,
            f"{label}\n{run['solve_seconds']:.1f} s → UNKNOWN",
            red,
        )
    arrow(ax, (0.75, 0.39), (0.75, 0.30))

    ax.text(
        0.5,
        0.045,
        "UNKNOWN means timeout only. It is neither an rct4 obstruction nor evidence that D(71)<142.",
        ha="center",
        va="center",
        fontsize=10,
        color="#7f1d1d",
        fontweight="bold",
    )
    save(PROBLEM / "figures" / "n71-rct4-residue.png", fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
