#!/usr/bin/env python3
"""Plot the exact L5 and D5 Delsarte duals on [-1, 1/2]."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_certificates import eval_poly, gegenbauer_dim5

F = Fraction


def f_on_grid(c, xs):
    deg = len(c) - 1
    polys = gegenbauer_dim5(deg)
    ys = []
    for x in xs:
        t = F(x).limit_denominator(10_000_000)
        ys.append(float(sum(c[k] * eval_poly(polys[k], t) for k in range(deg + 1))))
    return np.array(ys)


def main() -> None:
    certs = json.loads(
        (Path(__file__).resolve().parent / "certs" / "restricted_delsarte.json").read_text()
    )
    xs = np.linspace(-1.0, 0.5, 801)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for name, style in (
        ("D5_inner_products", {"color": "#1f4e79", "ls": "-"}),
        ("L5_inner_products", {"color": "#b85c38", "ls": "--"}),
    ):
        c = [F(v) for v in certs[name]["gegenbauer_coeffs"]]
        ys = f_on_grid(c, xs)
        label = "D5 dual, bound 42" if name.startswith("D5") else r"L5 dual, bound $239925/5456$"
        ax.plot(xs, ys, label=label, **style)
        T = [float(F(t)) for t in certs[name]["T"]]
        ax.scatter(T, f_on_grid(c, T), s=28, zorder=3, color=style["color"])
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(0.5, color="k", lw=0.4, ls=":")
    ax.set_xlim(-1.02, 0.55)
    ax.set_xlabel(r"inner product $t$")
    ax.set_ylabel(r"$f(t)$")
    ax.set_title("Exact restricted Delsarte duals in dimension 5")
    ax.legend(frameon=False)
    fig.tight_layout()
    out = Path(__file__).resolve().parent.parent / "figures" / "restricted_duals.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
