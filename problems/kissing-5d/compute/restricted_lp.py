#!/usr/bin/env python3
"""Exact-enough Delsarte LP for spherical codes in S^4 with a finite inner-product set.

For a putative N-point code whose distinct inner products lie in T ⊂ [-1, 1/2],
the average neighbours A_t ≥ 0 satisfy

    sum_{t in T} A_t = N - 1,
    A_{-1} ≤ 1   (if -1 ∈ T),
    1 + sum_t A_t P_k^{(5)}(t) ≥ 0    for all k ≥ 1.

The dual is a polynomial f = sum_{k=0}^d c_k P_k^{(5)}, c_k ≥ 0, with
f(t) ≤ 0 on T  (and an extra slack for the A_{-1}≤1 capacity).  Then
N ≤ f(1)/c_0, or a slight variant when A_{-1} is capped.

We solve the primal in high-precision floats (HiGHS via scipy) and, when
the bound is strictly below an integer K, emit a rational dual polynomial
that excludes codes of size ≥ K with those inner products.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction

# Inner products that appear in the four known 40-point codes
# (Cohn–Rajagopal Table 2.1).
T_D5 = [F(-1), F(-1, 2), F(0), F(1, 2)]
T_L5 = [F(-1), F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 2)]
T_Q5 = [F(-1), F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]
T_ALL = sorted(set(T_D5 + T_L5 + T_Q5 + [
    F(-3, 4), F(-1, 4),  # L5 / R5
]))
# T_ALL = {-1, -4/5, -3/4, -1/2, -3/10, -1/4, 0, 1/5, 1/2}


def _lp_max_N(T, deg: int, cap_antipode: bool = True):
    """Maximise N = 1 + sum A_t by scipy linprog."""
    from scipy.optimize import linprog

    T = list(T)
    m = len(T)
    polys = gegenbauer_dim5(deg)
    # variables: A_t (m of them)
    # max 1 + 1·A
    c = -np.ones(m)  # minimize -sum A
    # A_{-1} ≤ 1
    bounds = []
    for t in T:
        if cap_antipode and t == F(-1):
            bounds.append((0.0, 1.0))
        else:
            bounds.append((0.0, None))
    # Delsarte: 1 + sum A_t P_k(t) ≥ 0  for k=1..deg
    A_ub = []
    b_ub = []
    for k in range(1, deg + 1):
        row = [-float(eval_poly(polys[k], t)) for t in T]
        A_ub.append(row)
        b_ub.append(float(eval_poly(polys[k], F(1))))  # = 1
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=bounds, method="highs")
    if not res.success:
        return {"success": False, "message": res.message}
    N = 1.0 + float(-res.fun)
    A = {str(t): float(res.x[i]) for i, t in enumerate(T)}
    return {"success": True, "N_bound": N, "A": A, "deg": deg}


def dual_search(T, deg: int, cap_antipode: bool = True):
    """Minimise f(1)/c_0 over c_k ≥ 0, f(t)≤0 on T.

    If -1 ∈ T and we cap A_{-1}≤1, the identity used is
        N f_0 ≤ f(1) + A_{-1} ( -f(-1) )_+   wait:
    Standard (no cap): N ≤ f(1)/f_0 if f≤0 on T.
    With cap: write f(-1) = p - q, p,q≥0, and N ≤ (f(1) + q)/f_0
    because the antipodal term contributes at most max(f(-1), 0) ≤ q if we
    drop a nonpositive f(-1) or add the positive part once.
    Simpler: force f(-1) ≤ 0 as well (ordinary Delsarte) — slightly weaker
    but exact and clean.
    """
    from scipy.optimize import linprog

    T = list(T)
    # variables c_0, ..., c_deg  (c_k is the Gegenbauer coeff)
    # f(t) = sum c_k P_k(t)
    # minimise f(1)  subject to c_0 = 1, c_k ≥ 0, f(t) ≤ 0 on T.
    # Then N ≤ f(1).
    n = deg + 1
    polys = gegenbauer_dim5(deg)
    Ptab = np.array([[float(eval_poly(polys[k], t)) for k in range(n)] for t in T])
    # f(1) = sum c_k  (since P_k(1)=1)
    cobj = np.ones(n)
    # c_0 = 1
    A_eq = np.zeros((1, n))
    A_eq[0, 0] = 1.0
    b_eq = np.array([1.0])
    # f(t) ≤ 0
    A_ub = Ptab
    b_ub = np.zeros(len(T))
    bounds = [(0.0, None)] * n
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    if not res.success:
        return {"success": False, "message": res.message}
    coeffs = res.x
    bound = float(res.fun)  # f(1) with f0=1
    fT = {str(t): float(Ptab[i] @ coeffs) for i, t in enumerate(T)}
    return {
        "success": True,
        "deg": deg,
        "bound": bound,
        "c": [float(x) for x in coeffs],
        "f_on_T": fT,
    }


def rational_dual(T, deg: int, den: int = 10_000):
    """Round a numerical dual to a rational polynomial and certify it exactly."""
    num = dual_search(T, deg)
    if not num["success"]:
        return num
    # c_0 = 1 exactly; round others to den
    c = [F(1)]
    for x in num["c"][1:]:
        c.append(F(int(round(x * den)), den))
        if c[-1] < 0:
            c[-1] = F(0)
    polys = gegenbauer_dim5(deg)
    # f(t) = sum c_k P_k(t)
    fT = {}
    ok = True
    for t in T:
        val = sum(c[k] * eval_poly(polys[k], t) for k in range(deg + 1))
        fT[str(t)] = str(val)
        if val > 0:
            ok = False
    f1 = sum(c)  # P_k(1)=1
    bound = f1  # c0=1
    return {
        "certified": ok,
        "deg": deg,
        "c": [str(x) for x in c],
        "f_on_T": fT,
        "f(1)/f0": str(bound),
        "float_bound": float(bound),
        "excludes": [k for k in (41, 42, 43, 44) if ok and bound < k],
    }


def main() -> int:
    families = {
        "D5_inner_products": T_D5,
        "L5_inner_products": T_L5,
        "Q5_inner_products": T_Q5,
        "all_known_40_inner_products": T_ALL,
        "three_distance_pm_half_zero": T_D5,
    }
    report = {}
    for name, T in families.items():
        entry = {
            "T": [str(t) for t in T],
            "primal": {},
            "dual": {},
            "rational_dual": {},
        }
        for deg in (6, 10, 14, 18):
            entry["primal"][str(deg)] = _lp_max_N(T, deg)
            entry["dual"][str(deg)] = dual_search(T, deg)
        # try to certify the deg-14 dual
        entry["rational_dual"] = rational_dual(T, 14, den=1000)
        if not entry["rational_dual"].get("certified"):
            entry["rational_dual_coarse"] = rational_dual(T, 10, den=100)
        report[name] = entry
        rd = entry["rational_dual"]
        print(f"{name}: rational certified={rd.get('certified')} "
              f"bound={rd.get('float_bound')} excludes={rd.get('excludes')}")

    out = Path(__file__).resolve().parent / "restricted_lp.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
