#!/usr/bin/env python3
"""Plot q2 class minima: ladders through 22, three-rail through 15."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
FIG = HERE.parent.parent / "figures"
FIG.mkdir(exist_ok=True)

ladders = json.loads((HERE / "ladder_census.json").read_text())["census"]
rails = json.loads((HERE / "three_rail.json").read_text())["exhaustive"]

fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.plot(
    [r["n"] for r in ladders],
    [r["min_delta"][0] / r["min_delta"][1] for r in ladders],
    "o-",
    color="#1f4e79",
    label="broken-rung ladders (width 2)",
)
ax.plot(
    [r["n"] for r in rails],
    [r["min_delta"][0] / r["min_delta"][1] for r in rails],
    "s--",
    color="#2e7d32",
    label="three-rail (width 3)",
)
ax.axhline(1 / 3, color="#a31f34", ls="--", lw=1.0, label="$1/3$")
ax.axhline(6 / 17, color="#b36b00", ls=":", lw=1.0, label="$6/17$")
ax.set_xlabel("number of elements")
ax.set_ylabel("balance constant")
ax.set_xticks(range(7, 23))
ax.legend(frameon=False)
ax.set_title("Exact class minima, independently counted")
fig.tight_layout()
out = FIG / "q2_class_minima.png"
fig.savefig(out, dpi=140)
print("wrote", out)
