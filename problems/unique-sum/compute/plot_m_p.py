#!/usr/bin/env python3
"""Plot the A398173 values of m(p) through p=53."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "green_m_p.csv"
OUT = HERE.parent / "figures" / "m_p.png"


def r2(y: np.ndarray, yhat: np.ndarray) -> float:
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - ss_res / ss_tot


def main() -> None:
    primes: list[int] = []
    values: list[int] = []
    with SRC.open() as handle:
        for row in csv.DictReader(handle):
            primes.append(int(row["p"]))
            values.append(int(row["m"]))
    p = np.array(primes, dtype=float)
    y = np.array(values, dtype=float)
    x1 = np.log(p)
    x2 = np.log(p) ** 2
    a1, b1 = np.polyfit(x1, y, 1)
    a2, b2 = np.polyfit(x2, y, 1)
    y1 = a1 * x1 + b1
    y2 = a2 * x2 + b2
    r2_log = r2(y, y1)
    r2_log2 = r2(y, y2)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True)
    ax0.scatter(x1, y, c="#2b6cb0", s=28, zorder=3)
    xs = np.linspace(x1.min(), x1.max(), 80)
    ax0.plot(xs, a1 * xs + b1, color="#c05621", linewidth=1.2)
    ax0.set_xlabel(r"$\log p$")
    ax0.set_ylabel(r"$m(p)$")
    ax0.set_title(rf"linear fit $R^2={r2_log:.3f}$")
    ax0.grid(True, alpha=0.25)

    ax1.scatter(x2, y, c="#2b6cb0", s=28, zorder=3)
    xs2 = np.linspace(x2.min(), x2.max(), 80)
    ax1.plot(xs2, a2 * xs2 + b2, color="#c05621", linewidth=1.2)
    ax1.set_xlabel(r"$(\log p)^2$")
    ax1.set_title(rf"log-squared fit $R^2={r2_log2:.3f}$")
    ax1.grid(True, alpha=0.25)

    fig.suptitle("$m(p)$ through $p=53$ (OEIS A398173)", fontsize=11)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    print(f"wrote {OUT}")
    print(f"R2_log={r2_log:.6f} R2_log2={r2_log2:.6f} n={len(primes)}")


if __name__ == "__main__":
    main()
