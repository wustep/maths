"""Plot first-crossing c(β) for Example 4 vs Example 5 on the {b,1} ray."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

here = Path(__file__).resolve().parent
data = json.loads((here / "first_crossing.json").read_text())

fig, ax = plt.subplots(figsize=(7.2, 4.2))
for proto, color, label in (
    ("ex5", "#b23a3a", "Example 5  (Liu)"),
    ("ex4", "#1f4e79", "Example 4  (tonight)"),
):
    xs = [r["beta"] for r in data[proto]["curve"]]
    ys = [r["c"] for r in data[proto]["curve"]]
    ax.plot(xs, ys, color=color, lw=2.0, label=label)

ax.axhline(0.382709087918741, color="#b23a3a", ls="--", lw=1.0, alpha=0.7)
ax.axhline(0.382345533366703, color="#666666", ls=":", lw=1.0)
ax.axhline(0.381966011250105, color="#999999", ls=":", lw=1.0)
ax.text(0.405, 0.38272, "Liu 0.382709", color="#b23a3a", fontsize=8, va="bottom")
ax.text(0.405, 0.38236, "Yu–Cambie 0.382346", color="#555555", fontsize=8, va="bottom")
ax.text(0.405, 0.38198, "Gilmer/AHS φ", color="#777777", fontsize=8, va="bottom")
ax.set_xlabel(r"mix weight $\beta$ on the conditionally-iid protocol")
ax.set_ylabel(r"first mean on $\{b,1\}$ with ratio $<1$")
ax.set_xlim(0, 0.40)
ax.set_ylim(0.3816, 0.3832)
ax.legend(frameon=False, loc="lower right")
ax.set_title("Union-closed frequency constant on the Liu–Yu–Cambie ray")
fig.tight_layout()
out = here.parent / "figures" / "ray_crossing.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, dpi=140)
print("wrote", out)
