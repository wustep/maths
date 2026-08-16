#!/usr/bin/env python3
"""Plot the cyclic-1680 multiplier landscape used for q2's new phase."""

from __future__ import annotations

from math import gcd
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from maths.figures import save, style
from q2_alternate_template_search import build
from search_almost_symmetric_pysat import old_coloring


def main() -> None:
    labels, edges, _point_orbit = build(1697, ())
    keys = np.asarray(labels, dtype=np.int32)
    old = np.asarray(old_coloring(), dtype=np.int8)
    binary = np.asarray([edge for edge in edges if len(edge) == 2], dtype=np.int32)
    ternary = np.asarray([edge for edge in edges if len(edge) == 3], dtype=np.int32)

    scores: list[tuple[int, int]] = []
    for multiplier in range(1, 1681):
        if gcd(multiplier, 1681) != 1:
            continue
        assignment = old[(multiplier * keys) % 1681]
        violations = int(
            np.count_nonzero(
                assignment[binary[:, 0]] == assignment[binary[:, 1]]
            )
        )
        violations += int(
            np.count_nonzero(
                (assignment[ternary[:, 0]] == assignment[ternary[:, 1]])
                & (assignment[ternary[:, 1]] == assignment[ternary[:, 2]])
            )
        )
        scores.append((violations, multiplier))

    values = np.asarray([score for score, _multiplier in scores])
    best_score, best_multiplier = min(scores)
    q1_phase_score = 3841

    style()
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    bins = np.arange(150, 3951, 100)
    ax.hist(values, bins=bins, color="#84adff", edgecolor="#175cd3", alpha=0.82)
    ax.axvline(best_score, color="#039855", linewidth=2.3)
    ax.axvline(q1_phase_score, color="#d92d20", linewidth=2.3, linestyle="--")
    ax.annotate(
        f"best cyclic copy\n$m={best_multiplier}$, {best_score} defects",
        xy=(best_score, 8),
        xytext=(560, 115),
        arrowprops={"arrowstyle": "->", "color": "#027a48", "linewidth": 1.7},
        color="#027a48",
        weight="bold",
    )
    ax.annotate(
        f"q1 hybrid phase\n{q1_phase_score} defects",
        xy=(q1_phase_score, 5),
        xytext=(3030, 105),
        arrowprops={"arrowstyle": "->", "color": "#b42318", "linewidth": 1.7},
        color="#b42318",
        weight="bold",
    )
    ax.set_title("A different phase family for the almost-reflected [1697] search")
    ax.set_xlabel("monochromatic folded edges before search")
    ax.set_ylabel("unit multipliers of the cyclic 1680 coloring")
    ax.set_xlim(0, 4050)
    ax.text(
        0.98,
        0.94,
        "1,640 unit multipliers modulo $1681=41^2$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        color="#475467",
    )

    destination = (
        Path(__file__).resolve().parents[1]
        / "figures"
        / "q2-alternate-seed-landscape.png"
    )
    save(destination, fig)
    print(destination)


if __name__ == "__main__":
    main()
