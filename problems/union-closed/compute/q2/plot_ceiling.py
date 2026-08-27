"""Figure: f(b)=1-(1-b)h(b) and the 2-sample ceiling."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LN2 = math.log(2)


def h(p):
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p)
    m = (p > 0.0) & (p < 1.0)
    q = 1.0 - p[m]
    out[m] = -(p[m] * np.log(p[m]) + q * np.log(q)) / LN2
    return out


def main():
    thresh = 1.0 - 1.0 / np.sqrt(2.0)
    b = np.linspace(0.15, 0.50, 800)
    f = 1.0 - (1.0 - b) * h(b)
    bstar = 0.29649392356933757
    cstar = 0.38305135658682558

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(b, f, color="#1f4e79", lw=2.0, label=r"$f(b)=1-(1-b)h(b)$")
    ax.axvline(thresh, color="#888", ls="--", lw=1.0, label=r"$1-1/\sqrt{2}$")
    ax.axhline(cstar, color="#c45c26", ls=":", lw=1.2, label=f"ceiling {cstar:.6f}")
    ax.axhline(0.38304, color="#2a7f4f", ls=":", lw=1.2, label="claimed 0.38304")
    ax.plot([bstar], [cstar], "o", color="#c45c26", ms=5)
    ax.set_xlabel("b")
    ax.set_ylabel("equality mean on {b,1}")
    ax.set_ylim(0.3826, 0.3855)
    ax.set_xlim(0.15, 0.50)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title("2-sample bit protocols cannot pass this on {b,1}")
    fig.tight_layout()
    out = Path(__file__).resolve().parents[2] / "figures" / "q2_ceiling.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
