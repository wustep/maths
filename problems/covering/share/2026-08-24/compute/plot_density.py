#!/usr/bin/env python3
"""Plot documented vs search densities for the radius-2 covering quest."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "q1_density_vs_length.png"


def density(r: int, n: int) -> float:
    return (1 + n + n * (n - 1) // 2) / (1 << r)


def main() -> None:
    documented = [
        (8, 26, "table 26"),
        (9, 39, "table 39"),
        (10, 51, "table 51"),
    ]
    certified = (10, 50, "certified 50")
    unresolved = [
        (8, 25, "3 holes"),
        (9, 38, "8 holes"),
        (10, 49, "7 holes"),
    ]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for r, n, label in documented:
        ax.scatter(n, density(r, n), s=70, facecolors="none", edgecolors="#4a5568", linewidths=1.4, zorder=3)
        ax.annotate(f"({r},{n}) {label}", (n, density(r, n)), textcoords="offset points", xytext=(8, 6), fontsize=8, color="#4a5568")
    r, n, label = certified
    ax.scatter([n], [density(r, n)], s=110, c="#c05621", marker="*", zorder=4, label="certified")
    ax.annotate(f"({r},{n}) {label}", (n, density(r, n)), textcoords="offset points", xytext=(8, -12), fontsize=8, color="#c05621")
    for r, n, label in unresolved:
        ax.scatter(n, density(r, n), s=55, c="#2b6cb0", marker="x", linewidths=1.6, zorder=3)
        ax.annotate(f"({r},{n}) {label}", (n, density(r, n)), textcoords="offset points", xytext=(8, 6), fontsize=8, color="#2b6cb0")

    ax.set_xlabel("length n")
    ax.set_ylabel(r"covering density $(1+n+\binom{n}{2})/2^r$")
    ax.set_title("Certified point and unresolved targets from the same search")
    ax.set_xlim(22, 54)
    ax.set_ylim(1.15, 1.58)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
