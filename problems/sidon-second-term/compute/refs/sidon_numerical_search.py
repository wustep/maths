#!/usr/bin/env python3
"""Exploratory R-scan for vector-valued Sidon smoothing.

This script concerns only the number of kernels R.  At the fixed values
m=32 and L=4 it
  * re-evaluates the stored floating-point candidates for R=1,...,8;
  * appends the independently verified exact R=8 value used in the paper;
  * can optionally rerun the deterministic continuation R=4,...,8.

There is deliberately no m-scan or grid-refinement output here.  The script
is not part of the proof.  It requires NumPy and SciPy; the separate exact
verifier uses fractions.Fraction only.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize, nnls

L_DEFAULT = 4
M_BASE = 32
TOL = 1e-9

ORIGINAL_HALF = np.array([
    0.0028968428, 0.0051751920, 0.0074723226, 0.0099735224,
    0.0125402983, 0.0153605108, 0.0183190707, 0.0216173705,
    0.0251799203, 0.0292487097, 0.0338329439, 0.0392967245,
    0.0458879397, 0.0544053990, 0.0660112082, 0.1127820246,
], dtype=float)

R2_HALF = np.array([
    0.01012956292039764, 0.01276280970241953,
    0.00852333347425290, 0.01453721423844140,
    0.01341338746556762, 0.01836361888597935,
    0.01786390549010228, 0.02342840992968761,
    0.02322364784385900, 0.03018883697882030,
    0.03016562227614859, 0.03982968282044382,
    0.03997628360728978, 0.05606805092365411,
    0.05658635555372749, 0.10493927788920861,
], dtype=float)

R3_HALF = np.array([
    0.01196778335277488, 0.01842110061141250,
    0.01615610204164875, 0.03294851621879124,
    0.03019555528341641, 0.03536889408843083,
    0.02871263073446423, 0.03433702664322726,
    0.03462985739708360, 0.04714240948439398,
    0.04504051008653005, 0.04809346766608080,
    0.03345225757165944, 0.03052252331873537,
    0.02122423529859202, 0.03178713020275865,
], dtype=float)

# Each row describes the next six-mode symmetric profile added in the
# continuation R=3 -> 4 -> ... -> 8.
ADDED_MODE_THETAS = np.array([
    [ 0.88319769, -0.83644267,  0.68175867, -0.45139419,  0.32959643, -0.11889704],
    [ 0.09366511, -0.20117506, -0.00750039, -0.16432276,  0.11876636,  0.07906431],
    [ 0.25469162, -0.21613820,  0.03966313, -0.02193528, -0.03649952, -0.03749029],
    [ 0.06484576, -0.06315701, -0.01849113, -0.00897898, -0.04065849, -0.01077720],
    [ 0.30399350, -0.37460678,  0.05084514, -0.15641904,  0.13043933,  0.03571992],
], dtype=float)

STORED_WEIGHTS = {
    1: np.array([1.0]),
    2: np.array([0.38487515584879206, 0.61512484415120794]),
    3: np.array([0.3898642811677684, 0.2692885943264559, 0.3408471245057757]),
    4: np.array([0.38137605, 0.27224110, 0.23310174, 0.11328111]),
    5: np.array([0.37842079, 0.22665586, 0.14370636, 0.15031953, 0.10089747]),
    6: np.array([0.39301985, 0.14305559, 0.04833725, 0.13732456, 0.21147697, 0.06678579]),
    7: np.array([0.39896364, 0.08476367, 0.02703736, 0.12986183, 0.22233959, 0.07024896, 0.06678495]),
    8: np.array([0.39490875, 0.08624912, 0.00135342, 0.12911860, 0.20451562, 0.02832639, 0.09217142, 0.06335669]),
}

TABLE1_CLASSES = {
    1: "free symmetric histogram",
    2: "one free histogram and one uniform kernel",
    3: "continued R=2 system plus one symmetric profile",
    4: "add the first six-mode symmetric profile",
    5: "add the second six-mode symmetric profile",
    6: "add the third six-mode symmetric profile",
    7: "add the fourth six-mode symmetric profile",
    8: "add the fifth six-mode symmetric profile",
}

# Display-only copy of the value printed by the exact rational verifier.
# This floating-point constant is not used in the proof.
EXACT_R8_GAMMA = 0.943492590713545


@dataclass
class BoundaryResult:
    gamma: float
    a: float
    b: float
    primal: float
    dual: float
    minimum_slack: float


def symmetric_from_half(half: np.ndarray) -> np.ndarray:
    half = np.asarray(half, dtype=float)
    half = 0.5 * half / half.sum()
    return np.concatenate([half, half[::-1]])


def mode_kernel(theta: np.ndarray, m: int = M_BASE) -> np.ndarray:
    theta = np.asarray(theta, dtype=float)
    x = (np.arange(m) + 0.5) / m - 0.5
    basis = np.column_stack([
        np.cos(2 * np.pi * (k + 1) * x) for k in range(len(theta))
    ])
    z = basis @ theta
    z -= z.max()
    p = np.exp(z)
    p = 0.5 * (p + p[::-1])
    return p / p.sum()



def polish_dual_active_set(G: np.ndarray, c: np.ndarray, y0: np.ndarray) -> np.ndarray:
    """Polish the NNLS active set for 1/4 y^T G y-c^T y, y>=0."""
    n = len(c)
    active = set(np.flatnonzero(y0 > 1e-10).tolist())
    for _ in range(4 * n):
        y = np.zeros(n)
        if active:
            idx = np.array(sorted(active), dtype=int)
            GA = G[np.ix_(idx, idx)]
            rhs = 2.0 * c[idx]
            try:
                sol = np.linalg.solve(GA, rhs)
            except np.linalg.LinAlgError:
                sol = np.linalg.lstsq(GA, rhs, rcond=None)[0]
            bad = idx[sol <= 0]
            if len(bad):
                # Remove the most negative coefficient and resolve.
                active.remove(int(bad[np.argmin(sol[sol <= 0])]))
                continue
            y[idx] = sol
        grad = 0.5 * (G @ y) - c
        inactive = np.array([i for i in range(n) if i not in active], dtype=int)
        if len(inactive):
            worst = inactive[np.argmin(grad[inactive])]
            if grad[worst] < -1e-11:
                active.add(int(worst))
                continue
        return y
    raise RuntimeError("dual active-set polishing did not converge")


def solve_boundary_qp(
    kernels: list[np.ndarray],
    lambdas: np.ndarray,
    L: int = L_DEFAULT,
) -> BoundaryResult:
    """Solve the fixed-kernel convex boundary problem to numerical tolerance."""
    kernels = [np.asarray(p, dtype=float) for p in kernels]
    lambdas = np.asarray(lambdas, dtype=float)
    if len(kernels) != len(lambdas):
        raise ValueError("kernel and weight counts differ")
    if np.any(lambdas <= 0):
        raise ValueError("omit zero-weight kernels before solving")
    if abs(lambdas.sum() - 1.0) > 1e-12:
        raise ValueError("mixing weights do not sum to one")
    if L <= 0:
        raise ValueError("L must be positive")
    m = len(kernels[0])
    if any(len(p) != m for p in kernels):
        raise ValueError("kernels have different grid sizes")
    for r, p in enumerate(kernels, start=1):
        if not np.all(np.isfinite(p)):
            raise ValueError(f"kernel {r} contains a non-finite entry")
        if np.any(p < -1e-14):
            raise ValueError(f"kernel {r} has a negative entry")
        if abs(p.sum() - 1.0) > 1e-10:
            raise ValueError(f"kernel {r} is not normalized")
        if np.max(np.abs(p - p[::-1])) > 1e-10:
            raise ValueError(f"kernel {r} is not symmetric")
    n = L * m

    A = np.zeros((n, len(kernels) * n))
    c = np.ones(n)
    for q in range(n):
        for r, (p, lam) in enumerate(zip(kernels, lambdas)):
            count = min(m, n - q)
            A[q, r * n + q : r * n + q + count] = lam * p[:count]
            c[q] -= lam * p[count:].sum()

    # Rectangular factor B=A D^{-1/2}.  We first use the unperturbed
    # Cholesky factorization of G=B B^T.  If numerical conditioning prevents
    # Cholesky, a rectangular QR factorization constructs an equivalent NNLS
    # target without adding a jitter term or changing the quadratic program.
    B = np.concatenate([
        A[:, r * n : (r + 1) * n] / math.sqrt(lam)
        for r, lam in enumerate(lambdas)
    ], axis=1)
    G = B @ B.T
    try:
        chol = np.linalg.cholesky(G)
        target = np.linalg.solve(chol, c)
        nnls_matrix = 0.5 * chol.T
    except np.linalg.LinAlgError:
        Q, Rmat = np.linalg.qr(B.T, mode="reduced")
        target_coeff = np.linalg.solve(Rmat.T, c)
        target = Q @ target_coeff  # B @ target = c
        if np.linalg.norm(B @ target - c, ord=np.inf) > 1e-10:
            raise RuntimeError("failed to construct the unperturbed NNLS target")
        nnls_matrix = 0.5 * B.T
    y, _ = nnls(nnls_matrix, target, maxiter=100 * n)
    y = polish_dual_active_set(G, c, y)

    aty = A.T @ y
    primal = 0.0
    blocks = []
    for r, lam in enumerate(lambdas):
        w = aty[r * n : (r + 1) * n] / (2 * lam)
        blocks.append(w)
        primal += lam * np.dot(w, w)

    slack = A @ np.concatenate(blocks) - c
    dual = np.dot(c, y) - 0.25 * np.dot(y, G @ y)
    if slack.min() < -TOL:
        raise RuntimeError(f"boundary solution is not feasible: {slack.min()}")
    if abs(primal - dual) > TOL * max(1.0, abs(primal)):
        raise RuntimeError(f"unexpected primal-dual gap: {primal - dual}")

    a = m * sum(lam * np.dot(p, p) for p, lam in zip(kernels, lambdas))
    b = 1 + 2 * (primal / m - L)
    return BoundaryResult(
        gamma=math.sqrt(a * b),
        a=a,
        b=b,
        primal=primal,
        dual=dual,
        minimum_slack=float(slack.min()),
    )


def stored_candidates() -> dict[int, tuple[list[np.ndarray], np.ndarray]]:
    original = symmetric_from_half(ORIGINAL_HALF)
    free = symmetric_from_half(R2_HALF)
    uniform = np.ones(M_BASE) / M_BASE
    third = symmetric_from_half(R3_HALF)
    candidates: dict[int, tuple[list[np.ndarray], np.ndarray]] = {
        1: ([original], STORED_WEIGHTS[1].copy()),
        2: ([free, uniform], STORED_WEIGHTS[2].copy()),
        3: ([free, uniform, third], STORED_WEIGHTS[3].copy()),
    }
    kernels = [free, uniform, third]
    for R, theta in enumerate(ADDED_MODE_THETAS, start=4):
        kernels = kernels + [mode_kernel(theta)]
        weights = STORED_WEIGHTS[R].astype(float)
        weights /= weights.sum()
        candidates[R] = ([p.copy() for p in kernels], weights)
    return candidates


def r_scan_rows(max_R: int = 8) -> list[tuple[int, float]]:
    """Re-evaluate the stored floating candidates used in Table 1."""
    if not 1 <= max_R <= 8:
        raise ValueError("max_R must lie between 1 and 8")
    candidates = stored_candidates()
    rows = []
    for R in range(1, max_R + 1):
        kernels, weights = candidates[R]
        rows.append((R, solve_boundary_qp(kernels, weights).gamma))
    return rows


def table1_rows(max_R: int = 8) -> list[tuple[int, str, float, str]]:
    """Return exactly the rows displayed in the manuscript's Table 1.

    The first max_R rows are floating-point re-evaluations of stored
    candidates.  When max_R=8, the final row is the independently verified
    exact rational certificate.
    """
    rows = [
        (R, TABLE1_CLASSES[R], gamma, "stored floating candidate")
        for R, gamma in r_scan_rows(max_R)
    ]
    if max_R == 8:
        rows.append((
            8,
            "rounded exact rational certificate",
            EXACT_R8_GAMMA,
            "exact rational certificate",
        ))
    return rows


def print_table1(max_R: int = 8, latex: bool = False) -> None:
    """Print Table 1 either as plain text or as LaTeX rows."""
    rows = table1_rows(max_R)
    if latex:
        for R, description, gamma, status in rows:
            digits = 15 if status == "exact rational certificate" else 10
            suffix = r"\ldots" if status == "exact rational certificate" else ""
            print(f"${R}$ & {description} & ${gamma:.{digits}f}{suffix}$ " + r"\\")
        return
    print("Table 1: single-kernel and multi-kernel comparisons (m=32, L=4)")
    for R, description, gamma, status in rows:
        marker = " [exact]" if status == "exact rational certificate" else ""
        print(f"R={R}: {gamma:.15f}  {description}{marker}")



def softmax(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    z -= z.max()
    e = np.exp(z)
    e = np.maximum(e, 1e-300)
    return e / e.sum()


def rerun_r_continuation(max_R: int = 8, maxfev: int = 800) -> None:
    """Re-optimize the stored R=4,...,8 continuation deterministically."""
    candidates = stored_candidates()
    kernels, weights = candidates[3]
    print(f"R=3  gamma={solve_boundary_qp(kernels, weights).gamma:.10f}")
    for R in range(4, max_R + 1):
        theta0 = ADDED_MODE_THETAS[R - 4]
        target_weights = STORED_WEIGHTS[R].astype(float)
        target_weights /= target_weights.sum()
        logits0 = np.log(target_weights[:-1] / target_weights[-1])
        x0 = np.concatenate([theta0, logits0])

        def objective(x: np.ndarray) -> float:
            new_kernel = mode_kernel(x[:6])
            mix = softmax(np.concatenate([x[6:], [0.0]]))
            return solve_boundary_qp(kernels + [new_kernel], mix).gamma

        result = minimize(
            objective,
            x0,
            method="Powell",
            options={
                "maxiter": 50,
                "maxfev": maxfev,
                "xtol": 2e-6,
                "ftol": 2e-10,
            },
        )
        value = objective(result.x)
        new_kernel = mode_kernel(result.x[:6])
        weights = softmax(np.concatenate([result.x[6:], [0.0]]))
        kernels = kernels + [new_kernel]
        print(
            f"R={R}  gamma={value:.10f}  "
            f"nfev={result.nfev}  success={result.success}"
        )



def main() -> None:
    parser = argparse.ArgumentParser(
        description="R-scan for the fixed grid m=32, L=4"
    )
    parser.add_argument(
        "--rerun-r4-to-r8",
        action="store_true",
        help="re-optimize the deterministic continuation R=4,...,max-R",
    )
    parser.add_argument("--max-R", type=int, default=8, choices=range(1, 9))
    parser.add_argument("--maxfev", type=int, default=800)
    parser.add_argument(
        "--latex-table1",
        action="store_true",
        help="print the R-scan rows in LaTeX form",
    )
    args = parser.parse_args()

    print_table1(args.max_R, latex=args.latex_table1)

    if args.rerun_r4_to_r8:
        if args.max_R < 4:
            raise ValueError("--rerun-r4-to-r8 requires --max-R at least 4")
        print("\nDeterministic R-continuation re-optimization")
        rerun_r_continuation(args.max_R, args.maxfev)


if __name__ == "__main__":
    main()
