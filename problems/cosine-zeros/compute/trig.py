#!/usr/bin/env python3
"""Shared cosine-sum primitives for the Littlewood zero problem.

Conventions match Juškevičius–Sahasrabudhe and Bedert:
    D_n(x) = sum_{k=0}^n cos(k x)
    s(x)   = 1 / (2 sin(x/2))     (x in (0, 2π))
    E(g)   = {x in (0, π] : |g(x) - 1/2| < s(x)}
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np


def dirichlet(n: int, x: np.ndarray) -> np.ndarray:
    """Vectorised D_n(x) = sum_{k=0}^n cos(k x)."""
    x = np.asarray(x, dtype=float)
    out = np.empty_like(x)
    small = np.abs(x) < 1e-12
    out[small] = n + 1.0
    xs = x[~small]
    out[~small] = 0.5 + np.sin((n + 0.5) * xs) / (2.0 * np.sin(xs / 2.0))
    return out


def envelope_s(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return 1.0 / (2.0 * np.sin(np.clip(x, 1e-15, math.pi) / 2.0))


def g_from_mask(mask: np.ndarray, x: np.ndarray) -> np.ndarray:
    """g(x) = sum_k mask[k] cos(k x), mask[k] in {0,1}."""
    x = np.asarray(x, dtype=float)
    k = np.arange(len(mask), dtype=float)
    # (m+1) x len(x) is fine up to a few million fused multiply-adds
    return np.cos(np.outer(k, x)).T @ mask.astype(float)


def g_on_uniform_grid(mask: np.ndarray, n_grid: int) -> tuple[np.ndarray, np.ndarray]:
    """g at x_j = π (j+1/2) / n_grid via a zero-padded real FFT."""
    m = len(mask) - 1
    # rfft of length 2 n_grid gives frequencies 0, 1, ..., n_grid at spacing π/n_grid
    # We want points in (0, π]: use N = 2 n_grid, sample bins 1..n_grid
    N = int(2 ** math.ceil(math.log2(max(2 * n_grid, 2 * m + 4))))
    coeff = np.zeros(N, dtype=float)
    coeff[: m + 1] = mask.astype(float)
    # inverse rfft: values of ∑ mask[k] exp(2π i k t / N) at t=0..N-1
    # that's g-like at x = 2π t / N. We want x in (0, π], i.e. t = 1..N/2
    spec = np.fft.irfft(np.fft.rfft(coeff), n=N) * N  # ∑ mask[k] cos(2π k t/N) + i sin... wait
    # rfft/irfft of a real even-extended signal:
    # easier: evaluate Re(FFT of padded mask) at the right nodes.
    F = np.fft.fft(coeff)
    # F[t] = ∑_k mask[k] exp(-2π i k t / N)
    # Re F[t] = ∑ mask[k] cos(2π k t / N)
    # x = 2π t / N ∈ (0, π]  ⇔  t = 1..N/2
    half = N // 2
    g = np.real(F[1 : half + 1])
    xs = 2.0 * math.pi * np.arange(1, half + 1) / N
    # downsample to ~n_grid points
    step = max(1, half // n_grid)
    return xs[::step], g[::step]


def measure_E(
    mask: np.ndarray,
    n_grid: int = 50_000,
    x_min: float = 1e-12,
) -> dict:
    """Trapezoid estimate of |E(g)| on (0, π]. Numerical, not a certificate."""
    m = len(mask) - 1
    xs, g = g_on_uniform_grid(mask, n_grid=n_grid)
    keep = xs >= x_min
    xs = xs[keep]
    g = g[keep]
    s = envelope_s(xs)
    inside = np.abs(g - 0.5) < s
    # variable spacing still uniform
    dx = float(xs[1] - xs[0]) if len(xs) > 1 else math.pi
    meas = float(inside.sum() * dx)
    cut = 1.0 / math.sqrt(max(m, 1))
    near = xs <= cut
    meas_near = float((inside & near).sum() * dx)
    meas_far = float((inside & ~near).sum() * dx)
    return {
        "m": m,
        "support": int(mask.sum()),
        "E_est": meas,
        "E_near": meas_near,
        "E_far": meas_far,
        "cut": cut,
        "random_benchmark": math.log(max(m, 2)) / math.sqrt(max(m, 1)),
        "inv_sqrt": 1.0 / math.sqrt(max(m, 1)),
        "frac_inside": float(inside.mean()),
        "n_grid_used": int(len(xs)),
    }


def random_mask(m: int, rng: np.random.Generator, p: float = 0.5) -> np.ndarray:
    return (rng.random(m + 1) < p).astype(np.uint8)


def thue_morse_mask(m: int) -> np.ndarray:
    k = np.arange(m + 1)
    bits = np.zeros(m + 1, dtype=np.uint8)
    kk = k.copy()
    while kk.any():
        bits ^= (kk & 1).astype(np.uint8)
        kk >>= 1
    return bits


def quadratic_residue_mask(m: int) -> np.ndarray:
    """1 on 0 and on quadratic residues modulo the next prime > m, clipped to [0,m]."""
    # simple: residues mod m+1 if that's prime-ish; else use p = next odd
    p = m + 1
    if p % 2 == 0:
        p += 1
    # not necessarily prime; still a multiplicative-looking set
    mask = np.zeros(m + 1, dtype=np.uint8)
    mask[0] = 1
    for a in range(1, p):
        r = (a * a) % p
        if r <= m:
            mask[r] = 1
    return mask


def interval_mask(m: int) -> np.ndarray:
    return np.ones(m + 1, dtype=np.uint8)


def evens_mask(m: int) -> np.ndarray:
    mask = np.zeros(m + 1, dtype=np.uint8)
    mask[0::2] = 1
    return mask


def low_half_mask(m: int) -> np.ndarray:
    mask = np.zeros(m + 1, dtype=np.uint8)
    mask[: m // 2 + 1] = 1
    return mask


def sturmian_mask(m: int, alpha: float = (math.sqrt(5) - 1) / 2, beta: float = 0.5) -> np.ndarray:
    k = np.arange(m + 1)
    return ((k * alpha) % 1.0 < beta).astype(np.uint8)
