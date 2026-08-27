"""c(β) on {b,1} through β=1.  Writes ../figures/q1_beta_curve.png."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
curve_path = HERE / "scan_beta.json"
data = json.loads(curve_path.read_text())
rows = data["ex4_curve"]
betas = np.array([r["beta"] for r in rows])
cs = np.array([r["mean"] for r in rows])

fig, ax = plt.subplots(figsize=(6.2, 3.6))
ax.plot(betas, cs, color="#1f4e79", lw=2.0, label="Example 4 first-crossing")
ax.axhline(0.38285, color="#b85c38", ls="--", lw=1.2, label="repo 0.38285 (β=1/5)")
ax.axhline(0.382709087918741, color="#888888", ls=":", lw=1.2, label="Liu 0.382709")
ax.axhline(0.38304, color="#2a7f4f", ls="--", lw=1.2, label="claimed 0.38304 (β=1)")
ax.set_xlabel("mix weight β on Example 4")
ax.set_ylabel("first mean with ratio < 1")
ax.set_xlim(0, 1)
ax.set_ylim(0.3818, 0.3833)
ax.legend(loc="lower right", fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
out = HERE.parents[1] / "figures" / "q1_beta_curve.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=140)
print("wrote", out)
