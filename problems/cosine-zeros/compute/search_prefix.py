#!/usr/bin/env python3
"""Search prefix sets S ⊂ [0,m] for small |E(g_S)|.

JS prove that a random S has 𝔼|E| = Θ(log m / √m). A special S with
|E| = o(log m / √m) would improve the construction-side barrier.
This script is a search, not a claim: printed numbers are trapezoid
estimates on a fixed grid.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

from trig import (
    evens_mask,
    interval_mask,
    low_half_mask,
    measure_E,
    quadratic_residue_mask,
    random_mask,
    sturmian_mask,
    thue_morse_mask,
)


def local_search(mask: np.ndarray, rng: np.random.Generator, flips: int, n_grid: int) -> tuple[np.ndarray, float]:
    best = mask.copy()
    best_E = measure_E(best, n_grid=n_grid)["E_est"]
    cur = best.copy()
    cur_E = best_E
    m = len(mask) - 1
    for _ in range(flips):
        i = int(rng.integers(0, m + 1))
        cur[i] ^= 1
        est = measure_E(cur, n_grid=n_grid)["E_est"]
        if est <= cur_E * 1.002:  # allow tiny uphill
            cur_E = est
            if est < best_E:
                best_E = est
                best = cur.copy()
        else:
            cur[i] ^= 1
    return best, best_E


def evaluate_family(m: int, rng: np.random.Generator, n_grid: int) -> list[dict]:
    families = {
        "interval": interval_mask(m),
        "evens": evens_mask(m),
        "low_half": low_half_mask(m),
        "thue_morse": thue_morse_mask(m),
        "quad_res": quadratic_residue_mask(m),
        "sturmian_gold": sturmian_mask(m),
        "sturmian_sqrt2": sturmian_mask(m, alpha=math.sqrt(2) - 1, beta=0.5),
        "random_p50": random_mask(m, rng, 0.5),
        "random_p25": random_mask(m, rng, 0.25),
        "random_p75": random_mask(m, rng, 0.75),
    }
    # several random draws
    rows = []
    for name, mask in families.items():
        rec = measure_E(mask, n_grid=n_grid)
        rec["family"] = name
        rows.append(rec)
    random_Es = []
    for i in range(8):
        rec = measure_E(random_mask(m, rng, 0.5), n_grid=n_grid)
        rec["family"] = f"random_draw_{i}"
        rows.append(rec)
        random_Es.append(rec["E_est"])
    # local search from the best random
    seed = random_mask(m, rng, 0.5)
    improved, _ = local_search(seed, rng, flips=min(2 * m, 200), n_grid=max(n_grid // 2, 8_000))
    rec = measure_E(improved, n_grid=n_grid)
    rec["family"] = "local_search"
    rec["random_mean"] = float(np.mean(random_Es))
    rec["random_min"] = float(np.min(random_Es))
    rows.append(rec)
    return rows


def main() -> int:
    rng = np.random.default_rng(20260817)
    out_dir = Path(__file__).resolve().parent
    all_rows = []
    for m in (32, 64, 128, 256, 512):
        n_grid = 16_384 if m <= 128 else 32_768
        print(f"=== m={m}  benchmark logm/sqrt(m)={math.log(m)/math.sqrt(m):.5f} ===", flush=True)
        rows = evaluate_family(m, rng, n_grid=n_grid)
        # print the interesting ones
        interesting = [r for r in rows if not r["family"].startswith("random_draw_")]
        interesting.sort(key=lambda r: r["E_est"])
        for r in interesting:
            ratio = r["E_est"] / r["random_benchmark"]
            print(
                f"  {r['family']:18s}  |S|={r['support']:4d}  E={r['E_est']:.5f}  "
                f"E_far={r['E_far']:.5f}  E/(log/√m)={ratio:.3f}",
                flush=True,
            )
        all_rows.extend(rows)
    dest = out_dir / "prefix_search.json"
    dest.write_text(json.dumps(all_rows, indent=2))
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
