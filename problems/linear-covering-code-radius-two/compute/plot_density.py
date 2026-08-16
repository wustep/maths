#!/usr/bin/env python3
"""Plot documented, certified, and unresolved q1 density points."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from maths.figures import save, style


def density(length: int, redundancy: int) -> float:
    return (1 + length + length * (length - 1) // 2) / (1 << redundancy)


def main() -> None:
    style()
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.8), sharey=True)
    panels = {
        8: {"published": 26, "residue": [(25, 3)]},
        9: {"published": 39, "residue": [(38, 8)]},
        10: {"published": 51, "certified": 50, "residue": [(49, 7)]},
    }

    for axis, (redundancy, data) in zip(axes, panels.items(), strict=True):
        published = data["published"]
        axis.scatter(
            [published],
            [density(published, redundancy)],
            s=75,
            color="#6b7280",
            label="documented code",
            zorder=3,
        )
        axis.annotate(
            f"n={published}",
            (published, density(published, redundancy)),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
        )
        if "certified" in data:
            certified = data["certified"]
            axis.plot(
                [published, certified],
                [density(published, redundancy), density(certified, redundancy)],
                color="#2563eb",
                linewidth=2,
                zorder=2,
            )
            axis.scatter(
                [certified],
                [density(certified, redundancy)],
                s=95,
                color="#2563eb",
                marker="*",
                label="q1 certified code",
                zorder=4,
            )
            axis.annotate(
                f"n={certified}",
                (certified, density(certified, redundancy)),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                color="#1d4ed8",
                fontweight="bold",
            )
        for target, uncovered in data["residue"]:
            axis.scatter(
                [target],
                [density(target, redundancy)],
                s=75,
                color="#dc2626",
                marker="x",
                linewidths=2.2,
                label="unresolved target",
                zorder=3,
            )
            axis.annotate(
                f"n={target}\n{uncovered} missed",
                (target, density(target, redundancy)),
                xytext=(0, -28),
                textcoords="offset points",
                ha="center",
                color="#991b1b",
                fontsize=9,
            )
        axis.axhline(1.0, color="#111827", linestyle="--", linewidth=1)
        axis.set_title(f"redundancy r={redundancy}")
        axis.set_xlabel("length n")
        axis.set_xticks(sorted({published, *[item[0] for item in data["residue"]], *([data["certified"]] if "certified" in data else [])}))

    axes[0].set_ylabel(r"formal density $(1+n+\binom{n}{2})/2^r$")
    axes[0].set_ylim(0.97, 1.58)
    handles, labels = [], []
    for axis in axes:
        for handle, label in zip(*axis.get_legend_handles_labels(), strict=True):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Radius-2 linear covering-code search: certified point and residues")
    fig.subplots_adjust(bottom=0.24, wspace=0.16)
    output = HERE.parent / "figures" / "q1_density_vs_length.png"
    save(output, fig)
    print(output)


if __name__ == "__main__":
    main()
