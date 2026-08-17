#!/usr/bin/env python3
"""Plot published / replayed Sidon second-term constants."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = Path(__file__).resolve().parents[1] / "figures"
FIG.mkdir(exist_ok=True)

# Published record (upper bound on the N^{1/4} coefficient)
history = [
    (1941, 1.0, "Erdős–Turán / Lindström"),
    (2021, 0.998, "Balogh–Füredi–Roy"),
    (2022, 0.99703, "O’Bryant"),
    (2025, 0.98183, "Carter–Hunter–O’Bryant"),
    (2026, 0.9435, "Hou–Zhao (arXiv)"),
]

# Our independent replay of Hou–Zhao Table 1 (m=32,L=4)
table1 = [
    (1, 0.9461473014450581),
    (2, 0.9450510576567568),
    (3, 0.9437979300977993),
    (4, 0.9436448861104898),
    (5, 0.9435665925888534),
    (6, 0.9435030630929332),
    (7, 0.9434969529873997),
    (8, 0.9434925900612208),
]

fig, ax = plt.subplots(figsize=(7.2, 4.2))
years, vals, labels = zip(*history)
ax.plot(years, vals, "o-", color="#1f4e79", lw=1.6, ms=6)
for y, v, lab in history:
    ax.annotate(lab, (y, v), textcoords="offset points", xytext=(6, 6), fontsize=8)
ax.set_xlabel("year")
ax.set_ylabel(r"published $C$ in $F(N)\leq\sqrt{N}+C\,N^{1/4}+O(1)$")
ax.set_title("Sidon second-term upper bound (published record)")
ax.set_ylim(0.93, 1.02)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "published_C.png", dpi=140)
plt.close()

fig, ax = plt.subplots(figsize=(7.2, 4.2))
Rs, gs = zip(*table1)
ax.plot(Rs, gs, "s-", color="#9b2226", lw=1.6, ms=6, label="independent QP replay")
ax.axhline(0.9435, color="#1f4e79", ls="--", lw=1, label="Hou–Zhao stated 0.9435")
ax.axhline(0.98183, color="#6c757d", ls=":", lw=1, label="CHO25 0.98183")
ax.set_xlabel("number of kernels $R$ (m=32, L=4)")
ax.set_ylabel(r"floating $\sqrt{ab}$")
ax.set_title("Hou–Zhao Table 1, independently replayed")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "table1_replay.png", dpi=140)
plt.close()

# L-lift of the published 8 kernels (independent QP)
Ls = list(range(4, 13))
gammas_L = [
    0.9434925900612208,
    0.943492509729883,
    0.9434925084844293,
    0.9434925084670628,
    0.943492508466575,
    0.9434925084665654,
    0.9434925084665631,
    0.9434925084665654,
    0.9434925084665631,
]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.plot(Ls, gammas_L, "o-", color="#0a9396", lw=1.6, ms=6)
ax.axhline(0.943492590713545, color="#9b2226", ls="--", lw=1, label="Hou–Zhao exact $\\gamma_0$ (L=4 cert.)")
ax.set_xlabel("boundary lengths $L$ (published 8 kernels, $m=32$)")
ax.set_ylabel(r"floating $\sqrt{ab}$")
ax.set_title("Longer boundary, same kernels")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "L_lift.png", dpi=140)
plt.close()
print("wrote", FIG / "published_C.png")
print("wrote", FIG / "table1_replay.png")
print("wrote", FIG / "L_lift.png")
