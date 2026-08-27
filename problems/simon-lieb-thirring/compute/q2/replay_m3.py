#!/usr/bin/env python3
"""Float replay of Carvalho Corso–Ried M_3 (arXiv:2403.04347v2).

Theorem 1.3 + (1.4) at γ=3. Not a bound. The certified evaluation lives
in verify_m3.py.

    h(z) = B(z) exp(θ(z)),   B(z)=(z−iα)/(z+iα),   α=4/3,
    Re θ(x+iy) from Lemma 4.6 (minus the integral).
    M_3 = (16π/81) · A³ / B²,
    A = ||h(· − 2i/3)||_∞,  B = ||h(· − i)||_2,  ||h_0||_∞ = 1.

Then C_1 = M_3 by their (1.12), and L/Lcl = (9√3/4) C_1.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

GAMMA = 3.0
ALPHA = 2.0 - 2.0 / GAMMA  # 4/3
TWO_OVER_GAMMA = 2.0 / GAMMA  # 2/3
FOUR_MINUS = 4.0 - TWO_OVER_GAMMA  # 10/3

# Shared k-grid for Re θ. Near 0 use the cubic series; tail is exp-small.
_K_NEAR = np.linspace(1e-8, 0.25, 400)
_K_MID = np.geomspace(0.25, 40.0, 2400)
_K = np.unique(np.concatenate([_K_NEAR, _K_MID]))
_DK = np.diff(_K)
_K_C = 0.5 * (_K[:-1] + _K[1:])
_G_C = np.pi * (
    2.0 * np.exp(-ALPHA * _K_C)
    + np.exp(-TWO_OVER_GAMMA * _K_C)
    - np.exp(-FOUR_MINUS * _K_C)
)
_COSHM1 = np.cosh(2.0 * _K_C) - 1.0
_K_DEN = _K_C * _COSHM1


def g_of_k(k: float) -> float:
    ak = abs(k)
    return math.pi * (
        2.0 * math.exp(-ALPHA * ak)
        + math.exp(-TWO_OVER_GAMMA * ak)
        - math.exp(-FOUR_MINUS * ak)
    )


def re_theta_arr(x: np.ndarray, y: float) -> np.ndarray:
    """Lemma 4.6: Re θ = −(1/π) ∫ g(k)(cos(kx) sinh(ky)−ky)/(k(cosh(2k)−1)) dk."""
    x = np.asarray(x, dtype=np.float64)
    # num[i,j] = cos(k_j x_i) sinh(k_j y) - k_j y
    kx = x[:, None] * _K_C[None, :]
    num = np.cos(kx) * np.sinh(_K_C * y) - _K_C * y
    integ = (num * (_G_C / _K_DEN)[None, :]) @ _DK
    return -integ / math.pi


def re_theta(x: float, y: float) -> tuple[float, float]:
    val = float(re_theta_arr(np.array([x]), y)[0])
    tail = (g_of_k(40.0) * (abs(math.sinh(40.0 * y)) + 40.0 * abs(y))) * math.exp(-80.0)
    return val, tail / math.pi


def abs_B_arr(x: np.ndarray, y: float) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return np.hypot(x, y - ALPHA) / np.hypot(x, y + ALPHA)


def abs_h_arr(x: np.ndarray, y: float) -> np.ndarray:
    return abs_B_arr(x, y) * np.exp(re_theta_arr(x, y))


def abs_B(x: float, y: float) -> float:
    return math.hypot(x, y - ALPHA) / math.hypot(x, y + ALPHA)


def abs_h(x: float, y: float) -> tuple[float, float]:
    rt, err = re_theta(x, y)
    return abs_B(x, y) * math.exp(rt), err


def scan_A(n: int = 4001, xmax: float = 40.0) -> dict:
    """||h(· − 2i/γ)||_∞ by a dense scan plus a refined local max."""
    y = -TWO_OVER_GAMMA
    xs = np.linspace(-xmax, xmax, n)
    vals = abs_h_arr(xs, y)
    i0 = int(np.argmax(vals))
    lo = xs[max(0, i0 - 4)]
    hi = xs[min(len(xs) - 1, i0 + 4)]
    grid = np.linspace(lo, hi, 801)
    fine = abs_h_arr(grid, y)
    j = int(np.argmax(fine))
    return {
        "A_scan": float(np.max(vals)),
        "A_refined": float(fine[j]),
        "x_at_max": float(grid[j]),
        "y": y,
    }


def integrate_B2(xmax: float = 60.0, n: int = 20001) -> dict:
    """Trapezoid of |h(x−i)|² plus a crude exponential tail."""
    y = -1.0
    x = np.linspace(-xmax, xmax, n)
    vals = abs_h_arr(x, y)
    h2 = vals * vals
    core = float(np.trapezoid(h2, x))
    c_eff = float(max(vals[0], vals[-1])) * math.exp(math.pi * xmax)
    tail = 2.0 * (c_eff**2) * math.exp(-2.0 * math.pi * xmax) / (2.0 * math.pi)
    return {
        "B2_core": core,
        "B2_tail_model": tail,
        "B2": core + tail,
        "B": math.sqrt(max(core + tail, 0.0)),
        "xmax": xmax,
        "n": n,
        "h_at_xmax": float(vals[-1]),
        "h_at_0": float(vals[n // 2]),
    }


def m3_from_AB(A: float, B: float) -> float:
    return (16.0 * math.pi / 81.0) * (A**3) / (B**2)


def main() -> int:
    print("CCR M_3 float replay (not a bound)", flush=True)
    print(f"  α={ALPHA}  g(0)={g_of_k(0.0)}  (should be 2π={2*math.pi})", flush=True)
    rt0, e0 = re_theta(0.0, 0.0)
    print(f"  Re θ(0)={rt0:.3e}±{e0:.1e}  (should be 0)", flush=True)
    ah0, _ = abs_h(0.0, 0.0)
    print(f"  |h(0)|={ah0:.12f}  (should be 1)", flush=True)

    print("scanning A = ||h(·-2i/3)||_∞ ...", flush=True)
    rec_a = scan_A()
    print(
        f"  A_refined={rec_a['A_refined']:.12f} at x={rec_a['x_at_max']:.6f}  "
        f"scan={rec_a['A_scan']:.12f}",
        flush=True,
    )

    print("integrating B² = ∫ |h(x-i)|² dx ...", flush=True)
    rec_b = integrate_B2()
    print(
        f"  B={rec_b['B']:.12f}  core={rec_b['B2_core']:.12f}  "
        f"tail_model={rec_b['B2_tail_model']:.3e}",
        flush=True,
    )

    A = rec_a["A_refined"]
    B = rec_b["B"]
    M3 = m3_from_AB(A, B)
    L = (9.0 * math.sqrt(3.0) / 4.0) * M3
    K = 16.0 / (243.0 * M3 * M3)
    paper_M3 = 0.371185695
    paper_L = 1.44655
    out = {
        "note": "Float replay of arXiv:2403.04347v2 Theorem 1.3 / (1.4) at γ=3. Not a bound.",
        "alpha": ALPHA,
        "A": rec_a,
        "B": rec_b,
        "M_3_float": M3,
        "paper_M_3": paper_M3,
        "M_3_minus_paper": M3 - paper_M3,
        "C_1_if_eq_M3": M3,
        "L_over_Lcl_float": L,
        "K_over_Kcl_float": K,
        "paper_L": paper_L,
        "q1_certified_L": 1.45576,
        "published_FHJN_L": 1.456,
    }
    dest = HERE / "replay_m3.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"M_3_float={M3:.12f}  paper={paper_M3}")
    print(f"L/Lcl_float={L:.12f}  paper={paper_L}")
    print(f"ΔM_3={M3-paper_M3:+.3e}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
