"""Vector-valued Sidon smoothing: discrete program of Hou–Zhao, Lemma 2.1.

Independent implementation of the finite covering / energy quantities.
A feasible (kernels, mixing weights, boundary vectors) yields

    F(N) <= sqrt(N) + sqrt(a*b) N^{1/4} + O(1)

for all large N. Optimality of the boundary quadratic program is not required
for a valid bound; any covering-feasible weights give a legitimate b.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class SmoothingProgram:
    """One discrete Hou–Zhao instance (symmetric or left/right-split)."""

    m: int
    L: int
    lambdas: np.ndarray  # shape (R,), nonnegative, sum to 1
    kernels: np.ndarray  # shape (R, m), rows are probability vectors
    weights_left: np.ndarray  # shape (R, L*m)
    weights_right: np.ndarray  # shape (R, L*m); same as left in the symmetric case

    @property
    def R(self) -> int:
        return int(self.lambdas.shape[0])

    @property
    def n(self) -> int:
        return self.L * self.m


def covering_values(prog: SmoothingProgram, side: str = "left") -> np.ndarray:
    """Covering numbers M(q) for q = 0..n inclusive (paper (1))."""
    p = prog.kernels
    lam = prog.lambdas
    w = prog.weights_left if side == "left" else prog.weights_right
    if side == "right":
        p = p[:, ::-1]
    n = prog.n
    m = prog.m
    # M[q] = sum_r λ_r sum_i p[r,i] * (w[r, q+i] if q+i < n else 1)
    M = np.zeros(n + 1, dtype=float)
    ones = np.ones(m, dtype=float)
    for r in range(prog.R):
        W = np.concatenate([w[r], ones])
        M += lam[r] * np.correlate(W, p[r], mode="valid")
    return M


def energy_constants(prog: SmoothingProgram) -> tuple[float, float]:
    """Paper (2),(3), extended to independent left/right weights.

    Symmetric Hou–Zhao is the special case weights_left == weights_right:
        b = 1 + 2*( (1/m) sum λ ||w||^2 - L )
    Asymmetric:
        b = 1 - 2L + (1/m) sum λ (||wL||^2 + ||wR||^2)
    which reduces to the symmetric formula when wL = wR.
    """
    a = float(prog.m * np.dot(prog.lambdas, np.sum(prog.kernels**2, axis=1)))
    sl = np.sum(prog.weights_left**2, axis=1)
    sr = np.sum(prog.weights_right**2, axis=1)
    b = 1.0 - 2.0 * prog.L + float(np.dot(prog.lambdas, sl + sr) / prog.m)
    return a, b


def gamma_of(prog: SmoothingProgram) -> float:
    a, b = energy_constants(prog)
    if a <= 0 or b <= 0:
        return float("inf")
    return math.sqrt(a * b)


def check_program(prog: SmoothingProgram, tol: float = 1e-12) -> dict:
    """Numerical feasibility report. Does not claim a published constant."""
    lam = prog.lambdas
    p = prog.kernels
    ok_mix = bool(np.all(lam >= -tol) and abs(lam.sum() - 1.0) <= 1e-10)
    ok_kern = bool(
        np.all(p >= -tol)
        and np.allclose(p.sum(axis=1), 1.0, atol=1e-10)
    )
    ML = covering_values(prog, "left")
    MR = covering_values(prog, "right")
    a, b = energy_constants(prog)
    return {
        "ok_mix": ok_mix,
        "ok_kern": ok_kern,
        "min_cover_left": float(ML.min()),
        "min_cover_right": float(MR.min()),
        "feasible": bool(ML.min() >= -tol and MR.min() >= -tol and b > 0),
        "a": a,
        "b": b,
        "gamma": math.sqrt(a * b) if a > 0 and b > 0 else float("inf"),
    }


def build_covering_matrix(kernels: np.ndarray, lambdas: np.ndarray, L: int, reverse: bool = False):
    """Sparse-ish dense matrix for the finite covering Aw >= c (q = 0..n-1).

    q = n is the identity 1 >= 1 and is omitted.
    Column layout is kernel-major: variables (r, j) with j = 0..n-1.
    """
    p = kernels[:, ::-1] if reverse else kernels
    R, m = p.shape
    n = L * m
    A = np.zeros((n, R * n))
    c = np.ones(n)
    for q in range(n):
        for r in range(R):
            count = min(m, n - q)
            A[q, r * n + q : r * n + q + count] = lambdas[r] * p[r, :count]
            c[q] -= lambdas[r] * p[r, count:].sum()
    return A, c


def solve_boundary_qp(
    kernels: np.ndarray,
    lambdas: np.ndarray,
    L: int,
    asymmetric: bool = False,
    tol: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray, float, float, float]:
    """Solve the fixed-kernel convex boundary problem in floating point.

    Returns (w_left, w_right, a, b, gamma).
    """
    kernels = np.asarray(kernels, dtype=float)
    lambdas = np.asarray(lambdas, dtype=float)
    R, m = kernels.shape
    n = L * m

    if not asymmetric:
        A, c = build_covering_matrix(kernels, lambdas, L, reverse=False)
        w, primal = _solve_one_qp(A, c, lambdas, n, R)
        wL = w.reshape(R, n)
        wR = wL.copy()
    else:
        AL, cL = build_covering_matrix(kernels, lambdas, L, reverse=False)
        AR, cR = build_covering_matrix(kernels, lambdas, L, reverse=True)
        # Block-diagonal QP: variables [wL | wR], constraints stacked.
        A = np.zeros((2 * n, 2 * R * n))
        A[:n, : R * n] = AL
        A[n:, R * n :] = AR
        c = np.concatenate([cL, cR])
        # D is diag(λ_r I_n) on each side separately, so pass doubled lambdas
        lam2 = np.concatenate([lambdas, lambdas])
        w, primal = _solve_one_qp(A, c, lam2, n, 2 * R)
        wL = w[: R * n].reshape(R, n)
        wR = w[R * n :].reshape(R, n)

    a = float(m * np.dot(lambdas, np.sum(kernels**2, axis=1)))
    # primal is sum_blocks λ ||w||^2 over the blocks we passed to _solve_one_qp
    if not asymmetric:
        b = 1.0 + 2.0 * (primal / m - L)
    else:
        b = 1.0 - 2.0 * L + primal / m
    gamma = math.sqrt(a * b) if a > 0 and b > 0 else float("inf")
    return wL, wR, a, b, gamma


def _solve_one_qp(
    A: np.ndarray,
    c: np.ndarray,
    lambdas: np.ndarray,
    n: int,
    nblocks: int,
) -> tuple[np.ndarray, float]:
    """Minimize sum_r λ_r ||w_r||^2 subject to A w >= c, via the dual NNLS form."""
    from scipy.optimize import nnls

    # D = diag(λ_r I_n), B = A D^{-1/2}
    scales = np.repeat(1.0 / np.sqrt(lambdas), n)
    B = A * scales  # broadcast on columns
    G = B @ B.T
    try:
        chol = np.linalg.cholesky(G)
        target = np.linalg.solve(chol, c)
        nnls_matrix = 0.5 * chol.T
    except np.linalg.LinAlgError:
        Q, Rmat = np.linalg.qr(B.T, mode="reduced")
        target = Q @ np.linalg.solve(Rmat.T, c)
        nnls_matrix = 0.5 * B.T
    y, _ = nnls(nnls_matrix, target, maxiter=200 * A.shape[0])
    y = _polish_dual(G, c, y)

    aty = A.T @ y
    w = np.empty(nblocks * n)
    primal = 0.0
    for r in range(nblocks):
        wr = aty[r * n : (r + 1) * n] / (2.0 * lambdas[r])
        w[r * n : (r + 1) * n] = wr
        primal += lambdas[r] * float(np.dot(wr, wr))

    slack = A @ w - c
    if slack.min() < -1e-8:
        # Shift every finite weight by a common η to restore covering.
        # ρ_q = row-sum of A on the variable columns; adding η to all w
        # increases (Aw)_q by η * (sum of row q).
        rho = A.sum(axis=1)
        need = np.maximum(0.0, -slack)
        eta = 0.0
        for q, rq, nq in zip(range(len(rho)), rho, need):
            if nq > 0:
                if rq <= 1e-15:
                    raise RuntimeError(f"infeasible covering row {q}")
                eta = max(eta, nq / rq)
        if eta > 0:
            w = w + eta
            primal = 0.0
            for r in range(nblocks):
                wr = w[r * n : (r + 1) * n]
                primal += lambdas[r] * float(np.dot(wr, wr))
    return w, primal


def _polish_dual(G: np.ndarray, c: np.ndarray, y0: np.ndarray) -> np.ndarray:
    n = len(c)
    active = set(np.flatnonzero(y0 > 1e-10).tolist())
    for _ in range(4 * n):
        y = np.zeros(n)
        if active:
            idx = np.array(sorted(active), dtype=int)
            try:
                sol = np.linalg.solve(G[np.ix_(idx, idx)], 2.0 * c[idx])
            except np.linalg.LinAlgError:
                sol = np.linalg.lstsq(G[np.ix_(idx, idx)], 2.0 * c[idx], rcond=None)[0]
            if np.any(sol <= 0):
                bad = idx[sol <= 0]
                active.remove(int(bad[np.argmin(sol[sol <= 0])]))
                continue
            y[idx] = sol
        grad = 0.5 * (G @ y) - c
        inactive = [i for i in range(n) if i not in active]
        if inactive:
            worst = min(inactive, key=lambda i: grad[i])
            if grad[worst] < -1e-11:
                active.add(int(worst))
                continue
        return y
    return y0


def softmax(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def symmetric_kernel_from_logits(z: np.ndarray, m: int) -> np.ndarray:
    half = softmax(np.asarray(z, dtype=float))
    # If z is shorter than m/2, interpret as cosine modes.
    if half.size == m // 2:
        p = np.concatenate([half, half[::-1]])
        return p / p.sum()
    x = (np.arange(m) + 0.5) / m - 0.5
    basis = np.column_stack([np.cos(2 * np.pi * (k + 1) * x) for k in range(len(z))])
    t = basis @ np.asarray(z, dtype=float)
    t = t - t.max()
    p = np.exp(t)
    p = 0.5 * (p + p[::-1])
    return p / p.sum()


def general_kernel_from_logits(z: np.ndarray, m: int) -> np.ndarray:
    """Unconstrained (not necessarily symmetric) kernel from m logits."""
    if len(z) != m:
        raise ValueError("expected m logits")
    return softmax(np.asarray(z, dtype=float))
