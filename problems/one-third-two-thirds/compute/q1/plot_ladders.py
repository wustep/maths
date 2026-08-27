#!/usr/bin/env python3
"""Plot non-sum broken-rung ladder minima against 1/3 and 6/17."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
FIG = HERE.parent.parent / "figures"
FIG.mkdir(exist_ok=True)

blob = json.loads((HERE / "ladder_census.json").read_text())
rows = blob["census"]
xs = [r["n"] for r in rows]
ys = [r["min_delta"][0] / r["min_delta"][1] for r in rows]

fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.plot(xs, ys, "o-", color="#1f4e79", label="min $\\delta$ over non-sum ladders")
ax.axhline(1 / 3, color="#a31f34", ls="--", lw=1.0, label="$1/3$")
ax.axhline(6 / 17, color="#b36b00", ls=":", lw=1.0, label="$6/17$ ($W_{10}$, $L_9$)")
ax.set_xlabel("number of elements")
ax.set_ylabel("balance constant")
ax.set_xticks(xs)
ax.legend(frameon=False)
ax.set_title("Broken-rung ladders, exact non-sum minima")
fig.tight_layout()
out = FIG / "ladder_minima.png"
fig.savefig(out, dpi=140)
print("wrote", out)
