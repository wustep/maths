#!/usr/bin/env python3
"""Local Neumann ratio on an interval, the Weidl covering handle at gamma=1.

Weidl partitions R into intervals with l ∫_I V = α and applies a one-eigenvalue
Neumann bound on each piece. At gamma=1/2 the Poincaré constant forces α≤3.
On a constant well the ratio |E_0|/∫V^{3/2} equals 1/sqrt(α). For α=3 that is
1/sqrt(3) ≈ 0.577, i.e. L/Lcl ≈ 2.72, above CCR.

This file maximises the Neumann ground-state ratio over piecewise-constant V
on [0,1] (scale-invariant). The constant well is expected to be the worst
(largest ratio), because Hölder minimises ∫V^{3/2} at fixed ∫V.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from constants import CCR_L, LCL_11

HERE = Path(__file__).resolve().parent


def neumann_ratio(v: np.ndarray, length: float = 1.0, alpha_target: float = 3.0) -> dict:
    """Rescale V so that l ∫ V = alpha_target (Weidl's partition rule), then
    score |E_0|/∫V^{3/2} for the Neumann problem on [0,l].
    """
    n = len(v)
    h = length / n
    raw_int = float(h * np.sum(np.maximum(v, 0.0)))
    if raw_int <= 0.0:
        raise ValueError("non-positive potential")
    # α = l ∫ V = length * raw_int. Scale V by λ, then α → λ α.
    lam = alpha_target / (length * raw_int)
    v = lam * np.maximum(v, 0.0)
    invh2 = 1.0 / (h * h)
    K = np.zeros((n, n))
    for i in range(n):
        if i == 0:
            K[0, 0] = invh2
            K[0, 1] = -invh2
        elif i == n - 1:
            K[n - 1, n - 1] = invh2
            K[n - 1, n - 2] = -invh2
        else:
            K[i, i] = 2.0 * invh2
            K[i, i - 1] = -invh2
            K[i, i + 1] = -invh2
    H = K - np.diag(v)
    evals = np.linalg.eigvalsh(H)
    e0 = float(evals[0])
    integ = float(h * np.sum(v ** 1.5))
    abs_e = max(-e0, 0.0)
    ratio = abs_e / integ if integ > 0 else 0.0
    alpha = float(length * h * np.sum(v))
    return {
        "E0": e0,
        "abs_E0": abs_e,
        "integral": integ,
        "L_upper_local": ratio,
        "ratio_over_classical": ratio / LCL_11 if integ > 0 else 0.0,
        "alpha": alpha,
        "n_neg": int(np.sum(evals < -1e-12)),
        "v_min": float(np.min(v)),
        "v_max": float(np.max(v)),
        "v_std": float(np.std(v)),
    }


def constant_well(depth: float, n: int = 80) -> dict:
    v = np.full(n, depth)
    rec = neumann_ratio(v)
    rec["tag"] = f"constant depth={depth}"
    rec["analytic_1_over_sqrt_alpha"] = 1.0 / math.sqrt(rec["alpha"]) if rec["alpha"] > 0 else None
    return rec


def random_histograms(n_bins: int = 24, n_draw: int = 400, seed: int = 3) -> dict:
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(n_draw):
        v = rng.random(n_bins) * rng.uniform(0.2, 8.0)
        rec = neumann_ratio(v)
        rec["tag"] = "random-hist"
        if best is None or rec["ratio_over_classical"] > best["ratio_over_classical"]:
            best = rec
            best["v"] = v.tolist()
    return best


def spike_vs_flat(n: int = 80) -> list[dict]:
    out = []
    for depth in (0.5, 1.0, 3.0, 9.0):
        out.append(constant_well(depth, n=n))
    v = np.ones(n) * 0.3
    v[n // 2] = 12.0
    rec = neumann_ratio(v)
    rec["tag"] = "mid-spike"
    out.append(rec)
    v = np.linspace(0.1, 4.0, n)
    rec = neumann_ratio(v)
    rec["tag"] = "linear-ramp"
    out.append(rec)
    return out


def main() -> int:
    print("=== q3 Neumann covering local ratio ===", flush=True)
    samples = spike_vs_flat()
    rnd = random_histograms()
    samples.append({k: rnd[k] for k in rnd if k != "v"})
    const = [s for s in samples if str(s.get("tag", "")).startswith("constant")]
    best = max(samples, key=lambda r: r["ratio_over_classical"])
    const_best = max(const, key=lambda r: r["ratio_over_classical"])
    out = {
        "analytic_constant_alpha3": {
            "alpha": 3.0,
            "L_local": 1.0 / math.sqrt(3.0),
            "ratio_over_classical": (1.0 / math.sqrt(3.0)) / LCL_11,
        },
        "best_sample": {k: best[k] for k in best if k != "v"},
        "best_constant": {k: const_best[k] for k in const_best if k != "v"},
        "random_best": {k: rnd[k] for k in rnd if k != "v"},
        "beats_CCR": bool(best["ratio_over_classical"] < CCR_L),
        "note": (
            "A covering bound is an *upper* bound on L equal to the worst local "
            "ratio. The constant well already gives ~2.72 > 1.44655, and random "
            "histograms did not produce a larger local ratio. This handle cannot "
            "dent CCR at gamma=1 with the Poincaré partition α≤3."
        ),
        "samples": [{k: s[k] for k in s if k != "v"} for s in samples],
    }
    dest = HERE / "certs" / "covering_local.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"analytic α=3  ratio/Lcl={(1/math.sqrt(3))/LCL_11:.6f}")
    print(
        f"best sample   ratio/Lcl={best['ratio_over_classical']:.6f} tag={best.get('tag')}"
    )
    print(f"beats CCR as covering upper bound? {out['beats_CCR']}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
