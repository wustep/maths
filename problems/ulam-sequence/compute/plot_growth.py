#!/usr/bin/env python3
"""Plot CS majorant growth constants vs word length L."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
FIG.mkdir(exist_ok=True)


def load_rows() -> list[dict]:
    rows = []
    for p in sorted(HERE.glob("cs_L*.json")):
        try:
            rec = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if "C2" in rec and "L" in rec:
            rows.append(rec)
    for p in sorted(HERE.glob("cs_F_L*.json")):
        try:
            rec = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if "CF" in rec and "L" in rec:
            # merge CF into an existing L row or add
            found = False
            for r in rows:
                if r.get("L") == rec["L"]:
                    r.setdefault("CF", rec["CF"])
                    found = True
                    break
            if not found:
                rows.append(rec)
    rows.sort(key=lambda r: r["L"])
    return rows


def main() -> None:
    rows = load_rows()
    Ls = [r["L"] for r in rows]
    C2 = [r.get("C2") for r in rows]
    CF = [r.get("CF") for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    if any(c is not None for c in C2):
        ax.plot(
            [L for L, c in zip(Ls, C2) if c is not None],
            [c for c in C2 if c is not None],
            "o-",
            label=r"$\max\|W\|_2^{1/L}$",
        )
    if any(c is not None for c in CF):
        ax.plot(
            [L for L, c in zip(Ls, CF) if c is not None],
            [c for c in CF if c is not None],
            "s--",
            label=r"$\max\|W\|_F^{1/L}$ (exact integer)",
        )
    ax.axhline(1.4655712318767682, color="C3", ls=":", label="Eggleton $\\rho\\approx 1.46557$")
    ax.axhline(1.454, color="C1", ls="--", label="CS 2025 published $1.454$")
    ax.axhline(1.443, color="C2", ls="-.", label="this work 1.443 (all n >= 1)")
    ax.axhline(1.4146717609798722, color="0.4", ls=":", label=r"method barrier $\rho(T_3T_1^2)^{1/3}$")
    ax.set_xlabel("admissible word length $L$")
    ax.set_ylabel("growth constant")
    ax.set_title("Ulam majorant growth: longer CS words")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_ylim(1.40, 1.50)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = FIG / "cs_growth_constants.png"
    fig.savefig(out, dpi=140)
    print("wrote", out, "from", len(rows), "rows")


if __name__ == "__main__":
    main()
