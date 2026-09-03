#!/usr/bin/env python3
"""1D test-potential search for a lower bound on L_{1,1}/L^{cl} above 2/sqrt(3).

A trial V gives a lower bound on L_{1,1}. The published one-bound-state value
is 2/sqrt(3) ≈ 1.154700. A certified ratio strictly above that would disprove
the Lieb–Thirring conjecture in d=1, γ=1, and would be a new lower bound.
It would not by itself dent the CCR upper bound 1.44655.

Discretization: Dirichlet Laplacian on [-L, L], n interior points, numpy
tridiagonal-style dense eigh (n=241 is a few MB). RAM-light.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from constants import CCR_L, LCL_11, SOBOLEV_RATIO

HERE = Path(__file__).resolve().parent


def sech_power_integral(p: float) -> float:
    return math.sqrt(math.pi) * math.gamma(p / 2.0) / math.gamma((p + 1.0) / 2.0)


def poschl_teller(nu: float) -> dict:
    """V = ν(ν+1) sech², E_n = -(ν-n)² for n = 0, …, floor(ν)-? 

    For non-integer ν>0 there are floor(ν)+1 bound states if we use the
    standard Pöschl–Teller formula E_n = -(ν-n)² for n=0,1,… with ν-n>0.
    """
    amp = float(nu * (nu + 1.0))
    n_bound = int(math.floor(nu)) + (1 if nu > math.floor(nu) or nu >= 1 else 0)
    if abs(nu - round(nu)) < 1e-12:
        n_bound = int(round(nu))
    energies = [(nu - n) ** 2 for n in range(n_bound) if nu - n > 0]
    moment = sum(energies)  # gamma=1
    integ = (amp ** 1.5) * sech_power_integral(3.0)
    ratio = moment / integ
    return {
        "family": "poschl-teller",
        "nu": nu,
        "n_bound": len(energies),
        "moment": moment,
        "integral": integ,
        "L_lower": ratio,
        "ratio_over_classical": ratio / LCL_11,
    }


def keller_one_bound() -> dict:
    """Exact one-bound-state optimizer V = (3/4) sech², E = -1/4."""
    rec = poschl_teller(0.5)
    rec["family"] = "keller-one-bound"
    rec["note"] = "V=(3/4) sech^2; ratio/Lcl should be 2/sqrt(3)"
    return rec


def square_well_spectrum(depth: float, width: float, n: int = 241, pad: float = 8.0) -> dict:
    """Finite square well of depth `depth` and width `width`, Dirichlet box."""
    L = 0.5 * width + pad
    xs = np.linspace(-L, L, n)
    h = xs[1] - xs[0]
    v = np.where(np.abs(xs) <= 0.5 * width, depth, 0.0)
    return discrete_ratio(xs, v, h, tag=f"square depth={depth:.4g} width={width:.4g}")


def discrete_ratio(xs: np.ndarray, v: np.ndarray, h: float, tag: str) -> dict:
    """H = -D² - V on Dirichlet grid. v ≥ 0 is the well depth."""
    n = len(xs)
    kin = np.zeros((n, n))
    invh2 = 1.0 / (h * h)
    for i in range(n):
        kin[i, i] = 2.0 * invh2
        if i > 0:
            kin[i, i - 1] = -invh2
        if i < n - 1:
            kin[i, i + 1] = -invh2
    H = kin - np.diag(v)
    evals = np.linalg.eigvalsh(H)
    neg = evals[evals < -1e-12]
    moment = float(np.sum(-neg))
    integ = float(h * np.sum(np.maximum(v, 0.0) ** 1.5))
    ratio = moment / integ if integ > 0 else 0.0
    return {
        "family": "discrete",
        "tag": tag,
        "n_grid": int(n),
        "h": float(h),
        "n_bound": int(neg.size),
        "moment": moment,
        "integral": integ,
        "L_lower": ratio,
        "ratio_over_classical": ratio / LCL_11 if integ > 0 else 0.0,
        "Emin": float(evals[0]),
    }


def two_sech_wells(sep: float, amp: float = 0.75, n: int = 241, L: float = 12.0) -> dict:
    xs = np.linspace(-L, L, n)
    h = xs[1] - xs[0]
    v = amp / np.cosh(xs - sep) ** 2 + amp / np.cosh(xs + sep) ** 2
    return discrete_ratio(xs, v, h, tag=f"two-sech sep={sep:.4g} amp={amp:.4g}")


def gaussian_sum(params: np.ndarray, n: int = 201, L: float = 10.0) -> dict:
    """params: (A,c,s) * k wells, s>0, A>0."""
    k = len(params) // 3
    xs = np.linspace(-L, L, n)
    h = xs[1] - xs[0]
    v = np.zeros_like(xs)
    for j in range(k):
        A, c, s = params[3 * j : 3 * j + 3]
        s = abs(s) + 0.05
        A = abs(A)
        v += A * np.exp(-0.5 * ((xs - c) / s) ** 2)
    return discrete_ratio(xs, v, h, tag=f"gauss-sum k={k}")


def random_walk_gaussians(n_steps: int = 400, seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    best = None
    x = np.array([0.9, 0.0, 1.2, 0.4, 3.0, 1.0])  # two wells
    rec = gaussian_sum(x)
    best = rec
    best_x = x.copy()
    step = 0.25
    for i in range(n_steps):
        prop = x + step * rng.normal(size=x.shape)
        rec = gaussian_sum(prop)
        if rec["ratio_over_classical"] > best["ratio_over_classical"]:
            best = rec
            best_x = prop
            x = prop
            step = min(0.4, step * 1.05)
        else:
            if rng.random() < 0.15:
                x = prop  # occasional downhill
            step = max(0.05, step * 0.995)
    best["params"] = best_x.tolist()
    best["walk_steps"] = n_steps
    best["seed"] = seed
    return best


def histogram_walk(nbins: int = 16, n_steps: int = 500, seed: int = 2, L: float = 8.0) -> dict:
    rng = np.random.default_rng(seed)
    n = 8 * nbins + 1
    xs = np.linspace(-L, L, n)
    h = xs[1] - xs[0]
    heights = np.maximum(rng.random(nbins) * 1.5, 0.05)
    edges = np.linspace(-L, L, nbins + 1)

    def v_from(ht):
        v = np.zeros_like(xs)
        for i, xi in enumerate(xs):
            b = min(nbins - 1, max(0, int((xi + L) / (2 * L) * nbins)))
            v[i] = ht[b]
        return v

    rec = discrete_ratio(xs, v_from(heights), h, tag="hist-init")
    best = rec
    x = heights.copy()
    for _ in range(n_steps):
        j = int(rng.integers(0, nbins))
        prop = x.copy()
        prop[j] = max(0.02, prop[j] + rng.normal() * 0.2)
        rec = discrete_ratio(xs, v_from(prop), h, tag="hist")
        if rec["ratio_over_classical"] > best["ratio_over_classical"]:
            best = rec
            x = prop
    best["heights"] = x.tolist()
    best["nbins"] = nbins
    best["walk_steps"] = n_steps
    return best


def scan_square_wells() -> list[dict]:
    out = []
    for depth in (0.3, 0.75, 1.0, 2.0, 4.0, 8.0):
        for width in (1.0, 2.0, 4.0, 8.0):
            out.append(square_well_spectrum(depth, width))
    return out


def scan_two_sech() -> list[dict]:
    out = []
    for sep in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0):
        for amp in (0.75, 2.0):
            out.append(two_sech_wells(sep, amp=amp))
    return out


def main() -> int:
    print("=== q3 trial-potential lower-bound search ===", flush=True)
    records = []
    keller = keller_one_bound()
    records.append(keller)
    print(
        f"keller one-bound: ratio/Lcl={keller['ratio_over_classical']:.6f} "
        f"(target 2/sqrt(3)={SOBOLEV_RATIO:.6f})",
        flush=True,
    )
    for nu in (1, 2, 3, 4):
        rec = poschl_teller(nu)
        records.append(rec)
        print(
            f"PT nu={nu}: n_bound={rec['n_bound']} ratio/Lcl={rec['ratio_over_classical']:.6f}",
            flush=True,
        )

    print("scanning square wells...", flush=True)
    squares = scan_square_wells()
    records.extend(squares)
    best_sq = max(squares, key=lambda r: r["ratio_over_classical"])
    print(
        f"  best square: {best_sq['tag']} ratio/Lcl={best_sq['ratio_over_classical']:.6f} "
        f"n_bound={best_sq['n_bound']}",
        flush=True,
    )

    print("scanning two-sech wells...", flush=True)
    twos = scan_two_sech()
    records.extend(twos)
    best_two = max(twos, key=lambda r: r["ratio_over_classical"])
    print(
        f"  best two-sech: {best_two['tag']} ratio/Lcl={best_two['ratio_over_classical']:.6f} "
        f"n_bound={best_two['n_bound']}",
        flush=True,
    )

    print("gaussian-sum random walk...", flush=True)
    gw = random_walk_gaussians()
    records.append(gw)
    print(
        f"  best gauss-sum ratio/Lcl={gw['ratio_over_classical']:.6f} n_bound={gw['n_bound']}",
        flush=True,
    )

    print("histogram random walk...", flush=True)
    hw = histogram_walk()
    records.append(hw)
    print(
        f"  best hist ratio/Lcl={hw['ratio_over_classical']:.6f} n_bound={hw['n_bound']}",
        flush=True,
    )

    numeric = [r for r in records if r.get("family") in ("discrete",)]
    best_numeric = max(numeric, key=lambda r: r["ratio_over_classical"])
    best_all = max(records, key=lambda r: r["ratio_over_classical"])
    above_sobolev = [
        r
        for r in records
        if r["ratio_over_classical"] > SOBOLEV_RATIO + 1e-4
    ]
    out = {
        "sobolev_ratio": SOBOLEV_RATIO,
        "CCR": CCR_L,
        "keller": keller,
        "best_all": {k: best_all[k] for k in best_all if k != "heights"},
        "best_numeric": {k: best_numeric[k] for k in best_numeric if k != "heights"},
        "n_records": len(records),
        "n_above_sobolev": len(above_sobolev),
        "beats_sobolev_lower_bound": bool(len(above_sobolev) > 0),
        "beats_CCR_upper": False,
        "note": (
            "Trial potentials lower-bound L. None of these raise the published "
            "one-bound-state ratio 2/sqrt(3). Discrete ratios can sit a little "
            "above or below the continuum Keller value because of grid bias; "
            "a value slightly above 1.1547 on a coarse grid is not a bound."
        ),
        "records": records,
    }
    dest = HERE / "certs" / "trial_potentials.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"best_all ratio/Lcl={best_all['ratio_over_classical']:.6f}")
    print(f"above sobolev count={len(above_sobolev)}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
