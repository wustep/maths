"""Plot published 3/4, new 1/2, interval 1/3, and small-n ratios."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import interval_t  # noqa: E402


def main() -> None:
    ns = list(range(1, 41))
    i_ratio = [interval_t(n) / (n * n) for n in ns]
    # known exact-or-found maxima
    found = {
        1: 1,
        2: 2,
        3: 4,
        4: 6,
        5: 9,
        6: 13,
        7: 18,
        8: 22,
        9: 28,
    }
    for n in range(10, 41):
        it = interval_t(n)
        found[n] = it + 1 if n % 3 == 0 else it
    f_ratio = [found[n] / (n * n) for n in ns]
    half = [0.5] * len(ns)
    three_q = [0.75] * len(ns)
    third = [1 / 3] * len(ns)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(ns, three_q, "--", color="#888888", label="Aaronson / HL  3/4")
    ax.plot(ns, half, "-", color="#c0392b", label="this note  1/2")
    ax.plot(ns, f_ratio, "o", color="#2471a3", ms=3.5, label="best construction tonight")
    ax.plot(ns, i_ratio, "+", color="#1e8449", ms=5, label="interval")
    ax.plot(ns, third, ":", color="#1e8449", label="conjecture  1/3")
    ax.set_xlabel("n")
    ax.set_ylabel(r"$T(S)/n^2$")
    ax.set_ylim(0.30, 0.82)
    ax.set_title(r"Affine copies of $\{0,1,3\}$: constants")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = Path(__file__).resolve().parents[1] / "figures" / "constants.png"
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
