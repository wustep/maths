#!/usr/bin/env python3
"""Atom-pair min(p,1-p) as a function of the third dimension."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from box_dp import box_counts

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    families = [(2, 3), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5)]
    cmax = { (2, 3): 10, (2, 4): 7, (2, 5): 6, (2, 6): 5, (3, 4): 5, (3, 5): 4 }
    data = {}
    for a, b in families:
        xs, ys = [], []
        for c in range(1, cmax[(a, b)] + 1):
            e, uv, vu, _, _ = box_counts(a, b, c)
            xs.append(c)
            ys.append(min(uv, vu) / e)
            print(f"C{a}xC{b}xC{c} {ys[-1]:.6f}")
        data[f"{a}x{b}"] = {"c": xs, "minp": ys}

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for key, rec in data.items():
        ax.plot(rec["c"], rec["minp"], marker="o", label=rf"$C_{{{key[0]}}}\times C_{{{key[2]}}}\times C_c$")
    ax.axhline(1 / 3, color="k", ls="--", lw=1, label=r"$1/3$")
    ax.set_xlabel(r"third dimension $c$")
    ax.set_ylabel(r"$\min\{\Pr(u\prec v),\Pr(v\prec u)\}$")
    ax.set_title("Atom pair of the first two factors, after thickening")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_ylim(0.30, 0.48)
    fig.tight_layout()
    figdir = Path(__file__).resolve().parent.parent / "figures"
    figdir.mkdir(exist_ok=True)
    fig.savefig(figdir / "thickening.png", dpi=140)
    Path(__file__).resolve().parent.joinpath("thickening.json").write_text(
        json.dumps(data, indent=2) + "\n"
    )
    print("wrote figures/thickening.png")


if __name__ == "__main__":
    main()
