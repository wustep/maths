#!/usr/bin/env python3
"""Plot the exact unitary-divisor gap and the remaining sign-vector growth."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
PROBLEM_ROOT = HERE.parent
REPO_ROOT = PROBLEM_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from maths.figures import save, style  # noqa: E402


def main() -> None:
    data = json.loads((HERE / "q2-results.json").read_text())
    records = data["records"]
    ns = [record["n"] for record in records]
    log_gaps = [record["log10_gap"] for record in records]
    choices = [int(record["sign_vectors_up_to_swap"]) for record in records]
    solutions = [record for record in records if record["is_consecutive"]]

    style()
    fig, (gap_ax, choice_ax) = plt.subplots(
        2,
        1,
        figsize=(9.0, 6.8),
        gridspec_kw={"height_ratios": [1.2, 1.0], "hspace": 0.42},
    )

    gap_ax.plot(ns, log_gaps, color="#2563eb", linewidth=1.2, marker=".", markersize=3)
    gap_ax.scatter(
        [record["n"] for record in solutions],
        [record["log10_gap"] for record in solutions],
        marker="*",
        s=115,
        color="#dc2626",
        zorder=4,
        label="gap 1 (the three known solutions)",
    )
    gap_ax.set_ylabel(r"$\log_{10}(b-a)$")
    gap_ax.set_title("Closest exact prime-power split of n!/4")
    gap_ax.legend(loc="upper left")
    gap_ax.set_xlim(ns[0], ns[-1])

    choice_ax.plot(ns, choices, color="#7c3aed", linewidth=1.5)
    choice_ax.fill_between(ns, choices, 1, color="#ddd6fe", alpha=0.55)
    choice_ax.set_yscale("log", base=2)
    choice_ax.set_xlabel("n")
    choice_ax.set_ylabel("sign assignments (up to swap)")
    choice_ax.set_title("The exact reformulation still leaves exponentially many assignments")
    choice_ax.set_xlim(ns[0], ns[-1])
    last = records[-1]
    choice_ax.annotate(
        f"{int(last['sign_vectors_up_to_swap']):,} at n={last['n']}",
        xy=(last["n"], int(last["sign_vectors_up_to_swap"])),
        xytext=(-155, -8),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#4c1d95"},
        color="#4c1d95",
    )

    output = PROBLEM_ROOT / "figures" / "q2-unitary-factorization.png"
    save(output, fig)
    print(output)


if __name__ == "__main__":
    main()
