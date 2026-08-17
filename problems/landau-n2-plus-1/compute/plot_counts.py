#!/usr/bin/env python3
"""Compare the certified prime and Iwaniec P2 counts to Bateman–Horn / Iwaniec shape."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from n2p1_lib import C_Q, bateman_horn_integral, wolf_prediction_li

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
FIG.mkdir(exist_ok=True)


def load_n(path: Path) -> np.ndarray:
    vals = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        vals.append(int(s.split()[0]))
    return np.array(vals, dtype=np.int64)


def main() -> None:
    summary = json.loads((HERE / "n2p1.json").read_text())
    n_max = int(summary["n_max"])
    primes = load_n(HERE / "prime_n.txt")
    p2 = load_n(HERE / "p2_omega2.txt")

    # Checkpoints at round N, plus 2e5 to match the first certified prefix.
    ns = []
    for e in range(3, 7):
        ns.append(10**e)
        if e < 6:
            ns.append(2 * 10**e)
            ns.append(5 * 10**e)
    ns = [n for n in ns if n <= n_max]
    if n_max not in ns:
        ns.append(n_max)
    ns = sorted(set(ns))

    rows = []
    for N in ns:
        c_pr = int(np.searchsorted(primes, N, side="right"))
        c_p2 = int(np.searchsorted(p2, N, side="right"))
        bh = C_Q * bateman_horn_integral(N)
        wli = wolf_prediction_li(N)
        iwaniec_shape = N / (math.log(N) ** 1.5)
        rows.append(
            {
                "N": N,
                "primes": c_pr,
                "p2_composite": c_p2,
                "iwaniec_p2": c_pr + c_p2,
                "bateman_horn": bh,
                "wolf_li": wli,
                "prime_over_bh": c_pr / bh,
                "prime_over_wolf_li": c_pr / wli,
                "iwaniec_p2_over_shape": (c_pr + c_p2) / iwaniec_shape,
            }
        )

    out_json = HERE / "comparison.json"
    out_json.write_text(json.dumps({"n_max": n_max, "rows": rows}, indent=2) + "\n")

    fig, axes = plt.subplots(3, 1, figsize=(7.2, 8.4), sharex=True)
    ax0, ax1, ax2 = axes

    Nplot = np.array([r["N"] for r in rows], dtype=float)
    pr = np.array([r["primes"] for r in rows], dtype=float)
    bh = np.array([r["bateman_horn"] for r in rows], dtype=float)
    p2c = np.array([r["iwaniec_p2"] for r in rows], dtype=float)

    ax0.plot(Nplot, pr, "o-", color="#1d4ed8", label="certified primes n^2+1")
    ax0.plot(Nplot, bh, "s--", color="#c2410c", label="Bateman-Horn C_q integral")
    ax0.set_xscale("log")
    ax0.set_yscale("log")
    ax0.set_ylabel("count")
    ax0.legend(loc="upper left", fontsize=8)
    ax0.set_title("Primes n^2+1 versus Bateman-Horn / Landau-Shanks")
    ax0.grid(True, which="both", alpha=0.3)

    ratio = pr / bh
    ax1.axhline(1.0, color="#6b7280", linewidth=1)
    ax1.plot(Nplot, ratio, "o-", color="#1d4ed8")
    ax1.set_ylim(0.90, 1.05)
    ax1.set_ylabel("primes / BH")
    ax1.set_title("Certified count over Bateman-Horn (1 is the conjecture, not a theorem)")
    ax1.grid(True, which="both", alpha=0.3)

    ax2.plot(
        Nplot,
        p2c / (Nplot / np.log(Nplot) ** 1.5),
        "s--",
        color="#15803d",
    )
    ax2.set_xlabel("N")
    ax2.set_ylabel("P2 / shape")
    ax2.set_title("Iwaniec P2 count over N/(log N)^{3/2}: a shape check, not a bound")
    ax2.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    out = FIG / "counts_vs_bh.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")
    print(f"wrote {out_json}")
    for r in rows:
        print(
            f"N={r['N']:<8} primes={r['primes']:<7} BH={r['bateman_horn']:.1f} "
            f"ratio={r['prime_over_bh']:.5f} P2={r['iwaniec_p2']}"
        )


if __name__ == "__main__":
    main()
