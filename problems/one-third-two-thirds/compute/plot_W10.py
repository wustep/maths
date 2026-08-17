#!/usr/bin/env python3
"""Hasse diagram of W10."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Rank layout (longest chain below).
pos = {
    0: (0.4, 0.0),
    1: (2.2, 0.0),
    2: (0.0, 1.1),
    3: (1.2, 1.1),
    4: (2.0, 2.2),
    5: (1.0, 2.2),
    6: (2.2, 3.3),
    8: (0.6, 4.4),
    7: (2.6, 4.4),
    9: (1.6, 5.5),
}
covers = [
    (0, 2),
    (0, 3),
    (1, 4),
    (1, 5),
    (2, 4),
    (3, 5),
    (3, 8),
    (4, 6),
    (5, 9),
    (6, 7),
    (6, 8),
    (7, 9),
]

fig, ax = plt.subplots(figsize=(4.8, 5.6))
for a, b in covers:
    xa, ya = pos[a]
    xb, yb = pos[b]
    ax.plot([xa, xb], [ya, yb], color="0.25", lw=1.4, zorder=1)
for i, (x, y) in pos.items():
    ax.scatter([x], [y], s=280, c="white", edgecolors="k", lw=1.2, zorder=2)
    ax.text(x, y, str(i), ha="center", va="center", fontsize=11, zorder=3)
ax.set_axis_off()
ax.set_title(r"$W_{10}$, $e=187$, $\delta=6/17<14/39$, width 3")
fig.tight_layout()
figdir = Path(__file__).resolve().parent.parent / "figures"
figdir.mkdir(exist_ok=True)
fig.savefig(figdir / "W10.png", dpi=140)
print("wrote figures/W10.png")
