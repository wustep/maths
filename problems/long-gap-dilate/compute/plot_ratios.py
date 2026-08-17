#!/usr/bin/env python3
"""Plot SAT G ratios and Shakan's 2. Residue picture, not a dent."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    rows = [json.loads(l) for l in Path("compute/certs/sat_G.jsonl").read_text().splitlines()]
    p = [r["p"] for r in rows]
    r_mean = [r["ratio_over_mean"] for r in rows]
    r_sqrt = [r["ratio_over_sqrt"] for r in rows]
    sh_mean = [2 - 2 * r["n"] / r["p"] for r in rows]  # Shakan's L bound = 2(1-n/p)

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.axhline(2.0, color="0.4", ls="--", lw=1, label="Shakan leading 2")
    ax.plot(p, r_mean, "o-", color="#1f4e79", label="G(p,n) / (p/n), n=round sqrt(p)")
    ax.plot(p, r_sqrt, "s--", color="#b85c38", label="G(p,n) / sqrt(p)  (Green C)")
    ax.plot(p, sh_mean, ":", color="0.45", label="Shakan 2(1-n/p)")
    ax.set_xlabel("prime p")
    ax.set_ylabel("ratio")
    ax.set_title("Exact min-max dilate gap, p <= 71 (SAT, enum-checked to p=41)")
    ax.legend(frameon=False)
    ax.set_ylim(1.0, 3.4)
    fig.tight_layout()
    Path("figures").mkdir(exist_ok=True)
    fig.savefig("figures/sat_ratios.png", dpi=140)
    print("wrote figures/sat_ratios.png")


if __name__ == "__main__":
    main()
