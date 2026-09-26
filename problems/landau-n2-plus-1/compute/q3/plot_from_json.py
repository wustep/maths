#!/usr/bin/env python3
"""Plot comparison rows already stored in n2p1.json / comparison.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=HERE)
    parser.add_argument("--fig", type=Path, default=None)
    args = parser.parse_args()
    d = args.dir.resolve()
    summary = json.loads((d / "n2p1.json").read_text())
    rows = summary.get("comparison_rows")
    if not rows:
        rows = json.loads((d / "comparison.json").read_text())["rows"]

    fig, axes = plt.subplots(3, 1, figsize=(7.2, 8.4), sharex=True)
    ax0, ax1, ax2 = axes
    Nplot = np.array([r["N"] for r in rows], dtype=float)
    pr = np.array([r["primes"] for r in rows], dtype=float)
    bh = np.array([r["bateman_horn"] for r in rows], dtype=float)
    p2c = np.array([r["iwaniec_p2"] for r in rows], dtype=float)

    ax0.plot(Nplot, pr, "o-", color="#1d4ed8", label="certified primes n^2+1")
    ax0.plot(Nplot, bh, "s--", color="#c2410c", label="Bateman-Horn C_q integral")
    ax0.set_xscale("log")
    ax0.set_yscale("log")
    ax0.set_ylabel("count")
    ax0.legend(loc="upper left", fontsize=8)
    ax0.set_title("Primes n^2+1 versus Bateman-Horn / Landau-Shanks")
    ax0.grid(True, which="both", alpha=0.3)

    ax1.axhline(1.0, color="#6b7280", linewidth=1)
    ax1.plot(Nplot, pr / bh, "o-", color="#1d4ed8")
    ax1.set_ylim(0.90, 1.05)
    ax1.set_ylabel("primes / BH")
    ax1.set_title("Certified count over Bateman-Horn (1 is the conjecture, not a theorem)")
    ax1.grid(True, which="both", alpha=0.3)

    ax2.plot(
        Nplot,
        p2c / (Nplot / np.log(Nplot) ** 1.5),
        "s--",
        color="#15803d",
    )
    ax2.set_xlabel("N")
    ax2.set_ylabel("P2 / shape")
    ax2.set_title("Iwaniec P2 count over N/(log N)^{3/2}: a shape check, not a bound")
    ax2.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    fig_path = args.fig if args.fig is not None else d / "counts_vs_bh.png"
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_path, dpi=140)
    print(f"wrote {fig_path}")
    for r in rows:
        print(
            f"N={r['N']:<8} primes={r['primes']:<7} BH={r['bateman_horn']:.1f} "
            f"ratio={r['prime_over_bh']:.5f} P2={r['iwaniec_p2']}"
        )


if __name__ == "__main__":
    main()
