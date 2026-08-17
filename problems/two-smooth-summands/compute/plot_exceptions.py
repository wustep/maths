#!/usr/bin/env python3
"""Plot certified G(y) against Balog's scale and the 2/5 exception F values."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
FIG = ROOT.parent / "figures"
FIG.mkdir(exist_ok=True)

rows = json.loads((ROOT / "certs" / "g_certified.json").read_text())["rows"]
# unique y in order
seen = set()
ys, Gs = [], []
for r in rows:
    if r["y"] in seen:
        continue
    seen.add(r["y"])
    ys.append(r["y"])
    Gs.append(r["G"])

balog = [(y ** (1 / 0.2695691820)) for y in ys]

fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.loglog(ys, Gs, "o-", color="#1d3557", label="certified $G(y)$")
ax.loglog(ys, balog, "--", color="#e07a5f", label=r"$y^{1/(4/(9\sqrt{e}))}$ (Balog scale)")
ax.set_xlabel("smoothness bound $y$")
ax.set_ylabel("first missing sum $G(y)$")
ax.set_title("Certified $G(y)$ sits far above Balog's inverse scale")
ax.legend(frameon=False)
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "g_of_y.png", dpi=140)
print("wrote", FIG / "g_of_y.png")

exc = json.loads((ROOT / "certs" / "f_exceptions_exact.json").read_text())
ns = [r["n"] for r in exc["exact_2_5"]["exceptions"]]
Fs = [r["F"] for r in exc["exact_2_5"]["exceptions"]]
fig2, ax2 = plt.subplots(figsize=(7.2, 4.4))
xs = list(range(2, 500))
ax2.plot(xs, [x ** 0.4 for x in xs], color="#e07a5f", label=r"$n^{2/5}$")
ax2.plot(xs, [math.sqrt(x) for x in xs], color="#81b29a", label=r"$n^{1/2}$")
ax2.scatter(ns, Fs, color="#1d3557", zorder=3, label="exceptions to F(n) <= n^{2/5}")
ax2.set_xlim(0, 500)
ax2.set_ylim(0, 16)
ax2.set_xlabel("$n$")
ax2.set_ylabel("$F(n)$")
ax2.set_title("n^{2/5} exceptions stop at n=479 on [2, 10^6]")
ax2.legend(frameon=False)
fig2.tight_layout()
fig2.savefig(FIG / "exceptions_two_fifths.png", dpi=140)
print("wrote", FIG / "exceptions_two_fifths.png")
