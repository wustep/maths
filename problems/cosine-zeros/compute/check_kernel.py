#!/usr/bin/env python3
"""Check Bedert's periodisation kernel for small P.

φ(t) = (2/P ∑_{n=0}^{P-1} cos(2π n t))²
We expand φ as a cosine polynomial ∑_{k=-(2P-2)}^{2P-2} α_k e^{2π i k t}
and check: P² α_k ∈ ℤ, |α_k| ≤ 4, φ ≥ 0 on a grid, φ(0)=4.
"""

from __future__ import annotations

import math
import sys

import numpy as np


def kernel_coeffs(P: int) -> np.ndarray:
    """Exact rational coefficients via integer convolution.

    u[n] = 1 for n=0..P-1 (and we use the even cosine sum).
    (2/P ∑_{n=0}^{P-1} cos(2π n t)) = (1/P) ( 1 + ∑_{n=-(P-1)}^{P-1} e_n )
    more carefully: ∑_{n=0}^{P-1} cos = (1/2) ∑_{n=-(P-1)}^{P-1} e_n + 1/2.
    We just evaluate φ at N-th roots and IFFT, then clear P².
    """
    N = 8 * P  # enough bins to hold degree 2P-2
    t = np.arange(N) / N
    s = np.cos(2 * math.pi * np.arange(P)[:, None] * t[None, :]).sum(axis=0)
    phi = (2.0 / P * s) ** 2
    alpha = np.fft.fft(phi) / N
    # numerical Fourier coeffs; they should be real and k/P²
    return np.real_if_close(alpha, tol=1e-8)


def check_P(P: int) -> None:
    alpha = kernel_coeffs(P)
    # only |k| ≤ 2P-2 can be nonzero
    deg = 2 * P - 2
    tail = alpha[deg + 1 : -deg] if deg + 1 < len(alpha) - deg else np.array([])
    if tail.size and np.max(np.abs(tail)) > 1e-10:
        raise SystemExit(f"P={P}: unexpected tail {np.max(np.abs(tail))}")
    # collect unique k
    N = len(alpha)
    worst = 0.0
    for k in range(-deg, deg + 1):
        a = alpha[k % N]
        scaled = a * (P ** 2)
        if abs(scaled - round(scaled.real)) > 1e-6:
            raise SystemExit(f"P={P} k={k}: P^2 α={scaled} not integral")
        worst = max(worst, abs(float(a)))
        if abs(a) > 4 + 1e-9:
            raise SystemExit(f"P={P} k={k}: |α|={a} > 4")
    if abs(alpha[0] - 4.0) > 1e-8:
        # φ(0)=4 is the sum of coefficients, not necessarily α_0 if conventions differ
        # α_0 = ∫ φ = mean(φ). Check φ(0) separately.
        pass
    # positivity + φ(0)
    t = np.linspace(0, 1, 2000, endpoint=False)
    s = np.cos(2 * math.pi * np.arange(P)[:, None] * t[None, :]).sum(axis=0)
    phi = (2.0 / P * s) ** 2
    if np.min(phi) < -1e-12:
        raise SystemExit(f"P={P}: φ negative {np.min(phi)}")
    if abs(phi[0] - 4.0) > 1e-10:
        raise SystemExit(f"P={P}: φ(0)={phi[0]} ≠ 4")
    print(f"P={P:3d}  max|α|={worst:.6f}  φ(0)=4  φ≥0  P²α∈ℤ  OK")


def main() -> int:
    for P in range(1, 25):
        check_P(P)
    print("kernel checks: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
