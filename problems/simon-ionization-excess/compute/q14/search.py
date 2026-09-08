#!/usr/bin/env python3
"""Heuristic SDP search; only the independent exact verifiers certify a bound."""
import json
from fractions import Fraction as F
from pathlib import Path

import cvxpy as cp
import numpy as np

HERE = Path(__file__).resolve().parent


def kernel_floor(a, b, c, d):
    lo = min(a / d, c / b)
    hi = F(1) if max(a, c) <= min(b, d) else min(b / c, d / a)
    f = lambda t: (1 + t**3) / (1 + t**2)
    if hi <= F(5960, 10000):
        return f(hi)
    if lo >= F(5961, 10000):
        return f(lo)
    return F(8941, 10000)


def main():
    n = 37
    phi = F(912, 1000)
    # Rational edges, not a claim about the exact real geometric grid.
    edges = [F(round(10 ** (i / n) * 10**12), 10**12) for i in range(n + 1)]
    centers = [edges[i] * edges[i + 1] for i in range(n)]
    scales = [(edges[i] + edges[i + 1]) / 2 for i in range(n)]
    M = [[(kernel_floor(edges[i], edges[i+1], edges[j], edges[j+1]) - phi)
          * (centers[i] + centers[j]) / 2 / scales[i] / scales[j]
          for j in range(n)] for i in range(n)]
    A = np.array(M, dtype=float)
    P = cp.Variable((n, n), symmetric=True)
    t = cp.Variable()
    problem = cp.Problem(cp.Maximize(t), [P - t * np.eye(n) >> 0, A - P >= t])
    problem.solve(solver='CLARABEL', tol_gap_abs=1e-10, tol_feas=1e-10,
                  tol_gap_rel=1e-10, max_iter=150)
    print('status', problem.status, 'margin', t.value, flush=True)
    if P.value is None or t.value <= 0:
        raise SystemExit('No strict PSD-plus-nonnegative certificate found')
    denom = 10**10
    integers = [[int(round(P.value[i,j] * denom)) for j in range(n)] for i in range(n)]
    gram = np.linalg.cholesky(np.array(integers, dtype=float) / denom)
    gram_den = 10**9
    gram_int = [[int(round(gram[i,j] * gram_den)) for j in range(n)] for i in range(n)]
    blob = {'n': n, 'phi': str(phi), 'f_floor': '8941/10000',
            'edges': [str(x) for x in edges], 'P_denominator': denom,
            'P_numerators': integers,
            'B_denominator': gram_den, 'B_numerators': gram_int,
            'search_only': {'solver': 'CLARABEL', 'status': problem.status,
                            'margin': float(t.value), 'cvxpy_version': cp.__version__}}
    (HERE / 'certificate.json').write_text(json.dumps(blob, indent=2) + '\n')
    print('wrote certificate.json; not yet verified', flush=True)


if __name__ == '__main__':
    main()
