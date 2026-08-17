#!/usr/bin/env python3
"""Multi-scale vector smoothing.

Same Cauchy–Schwarz + Sidon energy argument as Hou–Zhao Lemma 2.1, but
kernels may have different bin counts m_r (hence different physical widths
H_r = m_r h on a common block size h). Derivation is in ATTACK.md.

    A = sum_r λ_r ||p^{(r)}||_2^2
    B = sum_r λ_r ( m_r (1-2 L_r) + 2 ||w^{(r)}||_2^2 )
    F(N) <= sqrt(N) + sqrt(A B) N^{1/4} + O(1)

when the covering inequalities hold. Equal (m,L) recovers Hou–Zhao.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import nnls


def covering_M(lambdas, kernels, weights) -> np.ndarray:
    """M(q) for q = 0..n_max inclusive. w_j = 1 for j >= n_r."""
    n_max = max(len(w) for w in weights)
    m_max = max(len(p) for p in kernels)
    M = np.zeros(n_max + 1)
    for lam, p, w in zip(lambdas, kernels, weights):
        W = np.concatenate([w, np.ones(m_max)])
        # correlate against this kernel; pad M to n_max+1
        vals = np.correlate(W, p, mode="valid")
        # valid length = len(W)-len(p)+1 = n_r + m_max - m_r + 1
        take = min(len(vals), n_max + 1)
        M[:take] += lam * vals[:take]
        if take < n_max + 1:
            M[take:] += lam  # entire kernel in the tail
    return M


def constants_AB(lambdas, kernels, weights, Ls):
    A = 0.0
    B = 0.0
    for lam, p, w, L, m in zip(lambdas, kernels, weights, Ls, [len(p) for p in kernels]):
        A += lam * float(np.dot(p, p))
        B += lam * (m * (1.0 - 2.0 * L) + 2.0 * float(np.dot(w, w)))
    return A, B


def solve_multiscale(lambdas, kernels, Ls, tol=1e-10):
    """Min B (i.e. min sum λ ||w||^2) subject to covering, kernels/L fixed."""
    lambdas = np.asarray(lambdas, dtype=float)
    kernels = [np.asarray(p, dtype=float) for p in kernels]
    R = len(kernels)
    ms = [len(p) for p in kernels]
    ns = [L * m for L, m in zip(Ls, ms)]
    n_max = max(ns)
    # variable layout: concat_r w_r, length sum ns
    offsets = np.cumsum([0] + ns)
    dim = int(offsets[-1])
    # constraints q = 0..n_max-1 (q=n_max is 1>=1)
    ncon = n_max
    A = np.zeros((ncon, dim))
    c = np.ones(ncon)
    for q in range(ncon):
        for r in range(R):
            p = kernels[r]
            m = ms[r]
            n = ns[r]
            off = int(offsets[r])
            for i in range(m):
                j = q + i
                if j < n:
                    A[q, off + j] += lambdas[r] * p[i]
                else:
                    c[q] -= lambdas[r] * p[i]
    # D = block diag(λ_r I_{n_r}); we minimize sum 2 λ ||w||^2, same as min sum λ ||w||^2
    scales = np.concatenate([np.full(ns[r], 1.0 / math.sqrt(lambdas[r])) for r in range(R)])
    Bmat = A * scales
    G = Bmat @ Bmat.T
    try:
        chol = np.linalg.cholesky(G)
        target = np.linalg.solve(chol, c)
        nnls_matrix = 0.5 * chol.T
    except np.linalg.LinAlgError:
        Q, Rmat = np.linalg.qr(Bmat.T, mode="reduced")
        target = Q @ np.linalg.solve(Rmat.T, c)
        nnls_matrix = 0.5 * Bmat.T
    y, _ = nnls(nnls_matrix, target, maxiter=200 * ncon)
    aty = A.T @ y
    wflat = np.empty(dim)
    for r in range(R):
        sl = slice(int(offsets[r]), int(offsets[r + 1]))
        wflat[sl] = aty[sl] / (2.0 * lambdas[r])
    slack = A @ wflat - c
    if slack.min() < -1e-8:
        rho = A.sum(axis=1)
        eta = 0.0
        for rq, nq in zip(rho, np.maximum(0.0, -slack)):
            if nq > 0:
                if rq <= 1e-15:
                    raise RuntimeError("infeasible multi-scale covering")
                eta = max(eta, nq / rq)
        wflat = wflat + eta
    weights = [wflat[int(offsets[r]) : int(offsets[r + 1])] for r in range(R)]
    Aconst, Bconst = constants_AB(lambdas, kernels, weights, Ls)
    M = covering_M(lambdas, kernels, weights)
    gamma = math.sqrt(Aconst * Bconst) if Aconst > 0 and Bconst > 0 else float("inf")
    return {
        "weights": weights,
        "A": Aconst,
        "B": Bconst,
        "gamma": gamma,
        "min_cover": float(M.min()),
        "feasible": bool(M.min() >= -1e-9 and Bconst > 0),
    }


def softmax(z):
    z = np.asarray(z, dtype=float)
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def sym_kernel(theta, m):
    x = (np.arange(m) + 0.5) / m - 0.5
    basis = np.column_stack([np.cos(2 * np.pi * (k + 1) * x) for k in range(len(theta))])
    t = basis @ np.asarray(theta, dtype=float)
    t = t - t.max()
    p = np.exp(t)
    p = 0.5 * (p + p[::-1])
    return p / p.sum()
