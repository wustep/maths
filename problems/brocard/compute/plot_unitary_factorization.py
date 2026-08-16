#!/usr/bin/env python3
"""Plot exact unitary-divisor gaps and sign-vector growth for n=4..100."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
SRC = HERE / "q2-results.json"
OUT = HERE.parent / "figures" / "q2-unitary-factorization.png"


def main() -> None:
    data = json.loads(SRC.read_text())
    records = data["records"]
    ns = [int(r["n"]) for r in records]
    log_gaps = [float(r["log10_gap"]) for r in records]
    sign_bits = [int(r["prime_power_block_count"]) - 1 for r in records]
    solutions = {int(r["n"]) for r in records if r["is_consecutive"]}

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7.2, 6.2), sharex=True)
    ax0.plot(ns, log_gaps, color="#2b6cb0", linewidth=1.2)
    ax0.scatter(
        [n for n in ns if n in solutions],
        [log_gaps[ns.index(n)] for n in ns if n in solutions],
        c="#c53030",
        marker="*",
        s=90,
        zorder=3,
        label="gap 1 (n=4,5,7)",
    )
    ax0.set_ylabel(r"$\log_{10}$ of minimum unitary gap")
    ax0.set_title("Exact complementary unitary-divisor gaps of $n!/4$")
    ax0.legend(frameon=False, loc="upper left")
    ax0.grid(True, alpha=0.25)

    ax1.plot(ns, sign_bits, color="#2f855a", linewidth=1.2)
    ax1.set_xlabel("n")
    ax1.set_ylabel(r"sign vectors up to swap ($2^{\pi^*(n)-1}$ bits)")
    ax1.set_title("Binary assignments remaining after complementary splits")
    ax1.grid(True, alpha=0.25)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
