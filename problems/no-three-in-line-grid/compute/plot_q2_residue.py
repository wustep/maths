#!/usr/bin/env python3
"""Plot the q1-to-q2 SAT wall-clock residue for the saved n=71 CNF."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from maths.figures import save, style  # noqa: E402


HERE = Path(__file__).resolve().parent
PROBLEM = HERE.parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main() -> int:
    q1 = [
        ("q1 Kissat, diagonal 6", load("kissat-d6-seed-6106.json")),
        ("q1 Kissat, diagonal 7", load("kissat-d7-seed-7107.json")),
        ("q1 Kissat, diagonal 8", load("kissat-d8-seed-8108.json")),
        ("q1 CaDiCaL, unrestricted", load("cadical-seed-19572.json")),
    ]
    q2 = [
        ("q2 Kissat, unrestricted", load("q2-kissat-seed-20260816.json")),
        ("q2 CaDiCaL, unrestricted", load("q2-cadical-seed-271828.json")),
    ]
    runs = q1 + q2

    expected_hash = "9a87227d743e9a2e956ac427940f601e5722f9773a6035cacedbe43d3f824bd5"
    if any(run["status"] != "UNKNOWN" for _, run in runs):
        raise ValueError("this figure is specifically for an all-UNKNOWN residue")
    if any(run["cnf_sha256"] != expected_hash for _, run in q2):
        raise ValueError("q2 run did not use the recorded saved CNF")
    if any(not run["hard_timeout"] for _, run in q2):
        raise ValueError("q2 run was not parent-hard-limited")

    labels = [label for label, _ in runs]
    wall_seconds = [
        run.get("wall_seconds", run["solve_seconds"])
        for _, run in runs
    ]
    colors = ["#9ca3af"] * len(q1) + ["#2563eb", "#0f766e"]

    style()
    fig, ax = plt.subplots(figsize=(9.4, 5.7))
    positions = list(range(len(runs)))
    bars = ax.barh(positions, wall_seconds, color=colors, height=0.64)
    ax.invert_yaxis()
    ax.set_yticks(positions, labels)
    ax.set_xlim(0, 1320)
    ax.set_xticks([0, 300, 600, 900, 1200], ["0", "5", "10", "15", "20"])
    ax.set_xlabel("parent-observed wall clock (minutes)")
    ax.axvline(900, color="#b45309", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.axvline(1200, color="#b91c1c", linestyle="--", linewidth=1.2, alpha=0.8)

    for bar, seconds in zip(bars, wall_seconds, strict=True):
        ax.text(
            min(seconds + 18, 1250),
            bar.get_y() + bar.get_height() / 2,
            f"{seconds:.1f}s  UNKNOWN",
            va="center",
            fontsize=9.5,
            color="#374151",
        )

    ax.set_title("q2 reused the exact n=71 rct4 CNF for two longer searches", pad=22)
    ax.text(
        0.5,
        1.025,
        "792,274 variables Â· 1,931,230 clauses Â· SHA-256 9a87227d…f824bd5",
        transform=ax.transAxes,
        ha="center",
        fontsize=10,
        color="#4b5563",
    )
    fig.text(
        0.5,
        0.015,
        "Both q2 solvers were unrestricted within canonical rct4 and parent-terminated at 20 minutes. "
        "No model was emitted; UNKNOWN is not UNSAT.",
        ha="center",
        fontsize=9.5,
        color="#7f1d1d",
        fontweight="bold",
    )
    fig.subplots_adjust(left=0.31, bottom=0.16, top=0.84)
    save(PROBLEM / "figures" / "n71-rct4-q2-residue.png", fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
