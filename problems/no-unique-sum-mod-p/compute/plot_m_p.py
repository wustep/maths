#!/usr/bin/env python3
"""Plot the exact m(p) table against log(p) and log(p)^2."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
PROBLEM_ROOT = HERE.parent
REPO_ROOT = PROBLEM_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from maths.figures import save, style  # noqa: E402


def fit_line(x_values: np.ndarray, y_values: np.ndarray) -> tuple[np.ndarray, float]:
    design = np.column_stack((np.ones_like(x_values), x_values))
    coefficients, *_ = np.linalg.lstsq(design, y_values, rcond=None)
    fitted = design @ coefficients
    residual = np.sum((y_values - fitted) ** 2)
    total = np.sum((y_values - np.mean(y_values)) ** 2)
    r_squared = 1.0 - residual / total
    return coefficients, float(r_squared)


def main() -> int:
    with (HERE / "m_p.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    primes = np.array([int(row["p"]) for row in rows], dtype=float)
    minima = np.array([int(row["m"]) for row in rows], dtype=float)
    logarithms = np.log(primes)
    squared_logarithms = logarithms**2

    style()
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4), sharey=True)
    for axis, x_values, x_label, color in (
        (axes[0], logarithms, r"$\log p$", "#2563eb"),
        (axes[1], squared_logarithms, r"$(\log p)^2$", "#7c3aed"),
    ):
        coefficients, r_squared = fit_line(x_values, minima)
        grid = np.linspace(float(np.min(x_values)), float(np.max(x_values)), 300)
        axis.scatter(
            x_values,
            minima,
            s=28,
            color=color,
            edgecolor="white",
            linewidth=0.45,
            zorder=3,
            label="exact values",
        )
        axis.plot(
            grid,
            coefficients[0] + coefficients[1] * grid,
            color="#111827",
            linewidth=1.4,
            alpha=0.8,
            label=rf"linear fit ($R^2={r_squared:.3f}$)",
        )
        for p, x_value, minimum in zip(primes, x_values, minima, strict=True):
            if p in (2, 3, 5, 31, 127, 199):
                axis.annotate(
                    f"{int(p)}",
                    (x_value, minimum),
                    xytext=(4, 4),
                    textcoords="offset points",
                    fontsize=8,
                    color="#374151",
                )
        axis.set_xlabel(x_label)
        axis.legend(loc="lower right")

    axes[0].set_ylabel(r"exact minimum $m(p)$")
    fig.suptitle(r"Unique-sum-free sets for every prime $p\leq 200$")
    fig.text(
        0.5,
        -0.01,
        "Least-squares lines describe this finite range only; they are not asymptotic claims.",
        ha="center",
        fontsize=9,
        color="#4b5563",
    )
    output = PROBLEM_ROOT / "figures" / "m_p.png"
    save(output, fig)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
