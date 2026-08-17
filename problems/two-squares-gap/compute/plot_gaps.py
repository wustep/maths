#!/usr/bin/env python3
"""Plot consecutive two-square gap / n^{1/4} and the 1/10, Jameson, BC lines."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import generate_two_squares_upto  # noqa: E402


def main() -> None:
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("figures/gap_ratios.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    ss = generate_two_squares_upto(N)
    xs = []
    ratios = []
    # subsample: keep running max and a thinned cloud
    run_max = 0.0
    run_x = []
    run_y = []
    two_sqrt2 = 2.0 * math.sqrt(2.0)
    for a, b in zip(ss, ss[1:]):
        if b > N:
            break
        r = (b - a) / (b ** 0.25)
        if r > run_max:
            run_max = r
            run_x.append(b)
            run_y.append(r)
        if b % max(1, N // 8000) < (b - a) + 1:
            xs.append(b)
            ratios.append(r)

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.scatter(xs, ratios, s=6, c="#4c6ef5", alpha=0.25, linewidths=0, label="consecutive gaps")
    ax.plot(run_x, run_y, color="#c92a2a", lw=1.4, label="running max")
    ax.axhline(two_sqrt2, color="#212529", ls="--", lw=1, label=r"Bambah–Chowla $2\sqrt{2}$")
    ax.axhline(0.1, color="#2f9e44", ls=":", lw=1.4, label=r"Green target $1/10$")
    ax.set_xscale("log")
    ax.set_xlim(2, N)
    ax.set_ylim(0, 3.0)
    ax.set_xlabel(r"right endpoint $s_{k+1}$")
    ax.set_ylabel(r"$(s_{k+1}-s_k)/s_{k+1}^{1/4}$")
    ax.set_title("Consecutive two-square gaps, scaled by $X^{1/4}$")
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
