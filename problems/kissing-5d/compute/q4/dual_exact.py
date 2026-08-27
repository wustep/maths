#!/usr/bin/env python3
"""Hunt an exact unrestricted 3-point dual for τ_5 with value < 44.

1-point Delsarte on [-1, 1/2] is the Odlyzko–Sloane number ≈ 46.34 and
cannot exclude 41–44.  This file records that number in one shot, then
implements exact Bachoc–Vallentin S_k^5 matrices over Q and searches
for a Putinar certificate of a dual with value < 44.

A numerical SDP / grid dual without an exact positivity certificate is
residue.  Mittelmann–Vallentin s_14(5)=44.998… is the published
numerical floor of this hierarchy at degree 14; a dual < 44 would need
a feasible exact certificate, not a finer Gegenbauer rationalization.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(HERE))

from bv import (  # noqa: E402
    F,
    N_BV,
    Poly3,
    S_matrix,
    eval_univariate,
    frobenius,
    gegenbauer,
    is_psd_exact,
    monomials_3,
    p4_gram,
    p_interval,
    self_tests,
)
from delsarte import gegenbauer_dim5, eval_poly  # noqa: E402
from unrestricted_dual import certify_interval, rationalize  # noqa: E402

P5 = gegenbauer(N_BV, 16)


def interval_grid(n: int):
    return [F(-1) + F(i, n - 1) * F(3, 2) for i in range(n)]


def domain_points(n: int):
    xs = interval_grid(n)
    out = []
    for u, v, t in product(xs, repeat=3):
        if F(1) + F(2) * u * v * t - u * u - v * v - t * t >= 0:
            out.append((u, v, t))
    return out


def numerical_delsarte(deg: int, ngrid: int = 241):
    """One-shot continuum 1-point number.  Not the object of this hunt."""
    from scipy.optimize import linprog
    T = interval_grid(ngrid)
    polys = gegenbauer_dim5(deg)
    n = deg + 1
    Ptab = np.array([[float(eval_poly(polys[k], t)) for k in range(n)] for t in T])
    res = linprog(
        np.ones(n), A_ub=Ptab, b_ub=np.zeros(len(T)),
        A_eq=np.array([[1.0] + [0.0] * deg]), b_eq=np.array([1.0]),
        bounds=[(0.0, None)] * n, method="highs",
    )
    if not res.success:
        return {"success": False, "message": res.message}
    return {"success": True, "deg": deg, "bound": float(res.fun),
            "c": [float(x) for x in res.x]}


def pack_sym(k: int, d: int):
    """Index map for the upper triangle of a (d-k+1)×(d-k+1) matrix."""
    m = d - k + 1
    idx = {}
    t = 0
    for i in range(m):
        for j in range(i, m):
            idx[(i, j)] = t
            t += 1
    return m, idx, t


def unpack_diag(vals, k: int, d: int):
    m = d - k + 1
    A = [[F(0)] * m for _ in range(m)]
    for i in range(m):
        A[i][i] = F(vals[i])
    return A


# ---------------------------------------------------------------------------
# Precompute S_k on a grid (floats) for a numerical / residue dual
# ---------------------------------------------------------------------------

def precompute(d: int, nI: int, nD: int):
    I = interval_grid(nI)
    D = domain_points(nD)
    S = [S_matrix(k, d) for k in range(d + 1)]
    # ⟨E_{pq}, S_k⟩ at each domain point, and at (u,u,1)
    Sk_D = []
    Sk_I = []
    for k in range(d + 1):
        m = d - k + 1
        # D: list of (nDpts, m, m)
        MD = np.zeros((len(D), m, m), dtype=float)
        for p, (u, v, t) in enumerate(D):
            for i in range(m):
                for j in range(m):
                    MD[p, i, j] = float(S[k][i][j].eval(u, v, t))
        Sk_D.append(MD)
        MI = np.zeros((len(I), m, m), dtype=float)
        for p, u in enumerate(I):
            for i in range(m):
                for j in range(m):
                    MI[p, i, j] = float(S[k][i][j].eval(u, u, F(1)))
        Sk_I.append(MI)
    PkI = np.array([[float(eval_univariate(P5[k], u)) for k in range(d + 1)]
                    for u in I])
    return {"I": I, "D": D, "S": S, "Sk_D": Sk_D, "Sk_I": Sk_I, "PkI": PkI}


def diagonal_lp(d: int, cache) -> dict:
    """Grid dual with diagonal F_k and diagonal B.  Residue unless lifted."""
    from scipy.optimize import linprog
    I, D = cache["I"], cache["D"]
    # vars: a_1..a_d, b11, b22, then diag(F_0), ..., diag(F_d)
    # b12 = 0
    sizes = [d - k + 1 for k in range(d + 1)]
    off = {"a": 0, "b11": d, "b22": d + 1}
    foff = []
    cur = d + 2
    for k, m in enumerate(sizes):
        foff.append(cur)
        cur += m
    nvars = cur
    cobj = np.zeros(nvars)
    for k in range(1, d + 1):
        cobj[off["a"] + k - 1] = 1.0
    cobj[off["b11"]] = 1.0
    # ⟨F0, J⟩ = sum of all entries = sum of diagonal if F0 diagonal
    for i in range(sizes[0]):
        cobj[foff[0] + i] = 1.0

    A_ub = []
    b_ub = []
    # g(u,v,t) = b22 + sum_k sum_i F_k_ii S_k_ii(u,v,t) ≤ 0
    for p in range(len(D)):
        row = np.zeros(nvars)
        row[off["b22"]] = 1.0
        for k, m in enumerate(sizes):
            for i in range(m):
                row[foff[k] + i] = cache["Sk_D"][k][p, i, i]
        A_ub.append(row)
        b_ub.append(0.0)
    # h(u) = 1 + sum a_k P_k + b22 + 3 sum ⟨F,S(u,u,1)⟩ ≤ 0
    for p, u in enumerate(I):
        row = np.zeros(nvars)
        for k in range(1, d + 1):
            row[off["a"] + k - 1] = cache["PkI"][p, k]
        row[off["b22"]] = 1.0
        for k, m in enumerate(sizes):
            for i in range(m):
                row[foff[k] + i] = 3.0 * cache["Sk_I"][k][p, i, i]
        A_ub.append(row)
        b_ub.append(-1.0)

    bounds = [(0.0, None)] * nvars
    res = linprog(cobj, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=bounds, method="highs")
    rec = {
        "success": bool(res.success),
        "grid_bound": None if not res.success else 1.0 + float(res.fun),
        "message": None if res.success else str(res.message),
        "nI": len(I), "nD": len(D),
    }
    if res.success:
        rec["a"] = [float(res.x[off["a"] + k]) for k in range(d)]
        rec["b11"] = float(res.x[off["b11"]])
        rec["b22"] = float(res.x[off["b22"]])
        rec["F_diag"] = [
            [float(res.x[foff[k] + i]) for i in range(sizes[k])]
            for k in range(d + 1)
        ]
    return rec


def slsqp_chol(d: int, cache, maxiter: int = 80) -> dict:
    """Full PSD F_k via Cholesky; grid inequalities.  Residue."""
    from scipy.optimize import minimize
    I, D = cache["I"], cache["D"]
    sizes = [d - k + 1 for k in range(d + 1)]

    def nL(m):
        return m * (m + 1) // 2

    # layout: a_1..a_d (as squares via free reals), L_B (3), L_k for each F_k
    off_a = 0
    off_B = d
    off_F = []
    cur = d + 3
    for m in sizes:
        off_F.append(cur)
        cur += nL(m)
    nvars = cur

    def chol_apply(vec, m, off):
        L = np.zeros((m, m))
        t = 0
        for i in range(m):
            for j in range(i + 1):
                L[i, j] = vec[off + t]
                t += 1
        return L @ L.T

    def unpack(x):
        a = x[off_a:off_a + d] ** 2
        B = chol_apply(x, 2, off_B)
        Fs = [chol_apply(x, sizes[k], off_F[k]) for k in range(d + 1)]
        return a, B, Fs

    def objective(x):
        a, B, Fs = unpack(x)
        return 1.0 + float(np.sum(a)) + B[0, 0] + float(np.sum(Fs[0]))

    cons = []

    def make_g(p):
        def g(x):
            a, B, Fs = unpack(x)
            s = B[1, 1]
            for k, Fk in enumerate(Fs):
                s += float(np.sum(Fk * cache["Sk_D"][k][p]))
            return -s  # g ≤ 0  →  -g ≥ 0
        return g

    def make_h(p):
        def h(x):
            a, B, Fs = unpack(x)
            s = 1.0 + B[1, 1] + 2.0 * B[0, 1]
            for k in range(1, d + 1):
                s += a[k - 1] * cache["PkI"][p, k]
            for k, Fk in enumerate(Fs):
                s += 3.0 * float(np.sum(Fk * cache["Sk_I"][k][p]))
            return -s
        return h

    # subsample constraints so SLSQP stays small
    step_D = max(1, len(D) // 80)
    step_I = max(1, len(I) // 25)
    for p in range(0, len(D), step_D):
        cons.append({"type": "ineq", "fun": make_g(p)})
    for p in range(0, len(I), step_I):
        cons.append({"type": "ineq", "fun": make_h(p)})

    x0 = np.zeros(nvars)
    # a small Levenshtein-like start: a1=a2=…=0, put mass on a_d
    if d >= 1:
        x0[0] = 1.0
    res = minimize(objective, x0, method="SLSQP", constraints=cons,
                   options={"maxiter": maxiter, "ftol": 1e-9, "disp": False})
    rec = {
        "success": bool(res.success),
        "grid_bound": None if not np.isfinite(res.fun) else float(res.fun),
        "message": str(res.message),
        "n_cons": len(cons),
    }
    if res.success or np.isfinite(res.fun):
        a, B, Fs = unpack(res.x)
        rec["a"] = [float(t) for t in a]
        rec["B"] = B.tolist()
        rec["F"] = [Fk.tolist() for Fk in Fs]
        rec["grid_bound"] = float(res.fun)
    return rec


# ---------------------------------------------------------------------------
# Exact Putinar with constant multipliers (linear over Q after a float LP)
# ---------------------------------------------------------------------------

def _poly_coeffs_upto(p: Poly3, deg: int) -> Dict:
    out = {}
    for d in range(deg + 1):
        for i in range(d + 1):
            for j in range(d - i + 1):
                k = d - i - j
                out[(i, j, k)] = p.c.get((i, j, k), F(0))
    return out


def exact_constant_putinar(d: int) -> dict:
    """Match g and h to a constant-multiplier Putinar form, F_k diagonal.

    -g = γ0 + γ1 (p(u)+p(v)+p(t)) + γ2 p4     (γ_i ≥ 0)
    -h = δ0 + δ1 p(u)                          (δ_i ≥ 0)

    p4 has degree 3, so this is only available for d ≥ 3.  At d < 3 we
    drop the p4 term.  A hit is an exact unrestricted dual.
    """
    from scipy.optimize import linprog
    S = [S_matrix(k, d) for k in range(d + 1)]
    sizes = [d - k + 1 for k in range(d + 1)]
    # vars: a_1..a_d, b11, b12, b22, all F_k diagonals, γ0,γ1,γ2, δ0,δ1
    off_a = 0
    off_b11, off_b12, off_b22 = d, d + 1, d + 2
    foff = []
    cur = d + 3
    for m in sizes:
        foff.append(cur)
        cur += m
    off_g0, off_g1, off_g2 = cur, cur + 1, cur + 2
    off_d0, off_d1 = cur + 3, cur + 4
    nvars = cur + 5

    # Build g as a Poly3 in the dual variables: we equate coefficients.
    # g = b22 + sum_k sum_i F_k_ii S_k_ii
    # We collect, for each monomial of deg ≤ d, a linear form in the vars.
    deg = d
    mons = monomials_3(deg)
    # A_eq g: for each mon, coeff_g(mon) + γ0[mon=1] + γ1 coeff_{p_sum}(mon)
    #         + γ2 coeff_p4(mon) = 0
    p_sum = p_interval() + p_interval().permute((1, 0, 2)) + p_interval().permute((2, 1, 0))
    p4 = p4_gram()
    # rows for g-identity
    rows = []
    rhs = []
    for mon in mons:
        row = np.zeros(nvars)
        row[off_b22] += float(1 if mon == (0, 0, 0) else 0)
        for k, m in enumerate(sizes):
            for i in range(m):
                row[foff[k] + i] += float(S[k][i][i].c.get(mon, F(0)))
        # + γ0 + γ1 p_sum + γ2 p4   should cancel g, i.e. g + that = 0
        row[off_g0] += float(1 if mon == (0, 0, 0) else 0)
        row[off_g1] += float(p_sum.c.get(mon, F(0)))
        row[off_g2] += float(p4.c.get(mon, F(0)))
        rows.append(row)
        rhs.append(0.0)

    # h(u) + δ0 + δ1 p(u) = 0 as a univariate of degree ≤ d
    # h = 1 + sum a_k P_k + 2 b12 + b22 + 3 sum F_k_ii S_k_ii(u,u,1)
    pu = p_interval()
    pu_uni = pu.restrict_uu1()
    for deg_u in range(d + 1):
        row = np.zeros(nvars)
        # constant 1
        if deg_u == 0:
            row_c = 1.0
        else:
            row_c = 0.0
        # a_k * P_k[deg_u]
        for k in range(1, d + 1):
            pk = P5[k]
            coeff = float(pk[deg_u]) if deg_u < len(pk) else 0.0
            row[off_a + k - 1] += coeff
        if deg_u == 0:
            row[off_b22] += 1.0
            row[off_b12] += 2.0
        for k, m in enumerate(sizes):
            for i in range(m):
                uni = S[k][i][i].restrict_uu1()
                coeff = float(uni[deg_u]) if deg_u < len(uni) else 0.0
                row[foff[k] + i] += 3.0 * coeff
        row[off_d0] += 1.0 if deg_u == 0 else 0.0
        row[off_d1] += float(pu_uni[deg_u]) if deg_u < len(pu_uni) else 0.0
        rows.append(row)
        rhs.append(-row_c)  # move the constant 1 to the right: ... = -1 at deg 0

    cobj = np.zeros(nvars)
    for k in range(d):
        cobj[off_a + k] = 1.0
    cobj[off_b11] = 1.0
    for i in range(sizes[0]):
        cobj[foff[0] + i] = 1.0

    bounds = [(0.0, None)] * nvars
    # b12 is free (we set it free; B PSD is not implied — we force b12=0
    # by bound so B = diag(b11,b22) is PSD).
    bounds[off_b12] = (0.0, 0.0)
    if d < 3:
        bounds[off_g2] = (0.0, 0.0)

    A_eq = np.array(rows)
    b_eq = np.array(rhs)
    res = linprog(cobj, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    rec = {
        "d": d,
        "success": bool(res.success),
        "bound": None if not res.success else 1.0 + float(res.fun),
        "message": None if res.success else str(res.message),
    }
    if not res.success:
        return rec

    # Rationalize and replay the identities exactly.
    denoms = (1, 10, 100, 1000, 10000, 100000)
    best = None
    for den in denoms:
        def Q(x):
            return F(int(round(float(x) * den)), den) if x > 0 else F(0)

        a = [Q(res.x[off_a + k]) for k in range(d)]
        b11, b12, b22 = Q(res.x[off_b11]), F(0), Q(res.x[off_b22])
        Fdiags = [[Q(res.x[foff[k] + i]) for i in range(sizes[k])]
                  for k in range(d + 1)]
        gam = [Q(res.x[off_g0]), Q(res.x[off_g1]), Q(res.x[off_g2])]
        delt = [Q(res.x[off_d0]), Q(res.x[off_d1])]
        Fmats = [unpack_diag(fd, k, d) for k, fd in enumerate(Fdiags)]
        # rebuild g, h
        g = Poly3.const(b22)
        for k, Fm in enumerate(Fmats):
            g = g + frobenius(Fm, S[k])
        residual_g = g + Poly3.const(gam[0]) + p_sum.scale(gam[1]) + p4.scale(gam[2])
        # h as Poly3 in u (v=t=0 extras unused): use univariate
        h_uni = [F(0)] * (d + 1)
        h_uni[0] += F(1) + F(2) * b12 + b22
        for k, ak in enumerate(a, start=1):
            pk = P5[k]
            for i, c in enumerate(pk):
                if i < len(h_uni):
                    h_uni[i] += ak * c
        for k, Fm in enumerate(Fmats):
            comb = frobenius(Fm, S[k])
            uni = comb.restrict_uu1()
            for i, c in enumerate(uni):
                if i < len(h_uni):
                    h_uni[i] += F(3) * c
        # + δ0 + δ1 p(u)
        h_uni[0] += delt[0]
        for i, c in enumerate(pu_uni):
            if i < len(h_uni):
                h_uni[i] += delt[1] * c
        g_ok = (not residual_g.c)
        h_ok = all(c == 0 for c in h_uni)
        if not (g_ok and h_ok):
            continue
        if any(not is_psd_exact(Fm) for Fm in Fmats):
            continue
        if b11 < 0 or b22 < 0:
            continue
        obj = F(1) + sum(a) + b11 + sum(Fmats[0][i][i] for i in range(sizes[0]))
        rec_hit = {
            "den": den,
            "bound": str(obj),
            "float_bound": float(obj),
            "a": [str(x) for x in a],
            "b11": str(b11), "b12": "0", "b22": str(b22),
            "F_diag": [[str(x) for x in row] for row in Fdiags],
            "gamma": [str(x) for x in gam],
            "delta": [str(x) for x in delt],
            "putinar": "constant-multipliers",
            "unrestricted": True,
            "certified": True,
            "excludes": [k for k in (41, 42, 43, 44) if obj < k],
        }
        if best is None or rec_hit["float_bound"] < best["float_bound"]:
            best = rec_hit
        break
    rec["certified"] = best
    return rec


def rank1_ansatz_search(d: int) -> dict:
    """A few exact rank-1 F_k with constant Putinar; hand rationals."""
    S = [S_matrix(k, d) for k in range(min(d, 2) + 1)]
    hits = []
    # Try F_0 = α J (all-ones), other F_k = 0, a = Levenshtein-like
    # g = b22 + α ⟨J, S_0⟩ = b22 + α (1^T S_0 1)
    # 1^T S_0 1 at d=1 is S00+2 S01+S11 = 1 + 2(u+v+t)/3 + (uv+ut+vt)/3
    # This is not a nonpositive combination of p, p4 at small α.
    # Record evaluations at a few rational points of D' instead: not a cert.
    sample = [
        (F(-1), F(-1), F(-1)),
        (F(-1), F(-1), F(1, 2)),
        (F(-1), F(0), F(0)),
        (F(0), F(0), F(0)),
        (F(1, 2), F(1, 2), F(-1, 2)),
        (F(1, 2), F(1, 2), F(1, 2)),
        (F(-1, 2), F(0), F(1, 2)),
    ]
    for alpha in (F(0), F(1, 100), F(1, 10), F(1, 4), F(1, 2), F(1)):
        if d < 1:
            continue
        F0 = [[alpha, alpha], [alpha, alpha]] if d >= 1 else [[alpha]]
        # need size (d+1)
        m = d + 1
        F0 = [[alpha] * m for _ in range(m)]
        if not is_psd_exact(F0):
            continue
        Sk = S_matrix(0, d)
        gfun = frobenius(F0, Sk)
        # max of g on the sample (b22=0)
        mx = max(gfun.eval(*pt) for pt in sample)
        hits.append({
            "alpha": str(alpha),
            "sample_max_g": str(mx),
            "sample_max_g_float": float(mx),
            "certified": False,
            "note": "rank-1 all-ones F0; sample of D' only, not a theorem",
        })
    return {"tried": len(hits), "hits": hits}


def try_lift_diagonal(d: int, lp: dict) -> dict:
    """Rationalize a diagonal grid dual and test constant Putinar exactly."""
    if not lp.get("success"):
        return {"certified": False, "reason": "no grid dual"}
    sizes = [d - k + 1 for k in range(d + 1)]
    S = [S_matrix(k, d) for k in range(d + 1)]
    p_sum = p_interval() + p_interval().permute((1, 0, 2)) + p_interval().permute((2, 1, 0))
    p4 = p4_gram()
    best = None
    for den in (10, 100, 1000, 10000):
        def Q(x):
            return F(int(round(float(x) * den)), den) if x > 0 else F(0)
        a = [Q(x) for x in lp["a"]]
        b22 = Q(lp["b22"])
        b11 = Q(lp["b11"])
        Fdiags = [[Q(x) for x in row] for row in lp["F_diag"]]
        Fmats = [unpack_diag(fd, k, d) for k, fd in enumerate(Fdiags)]
        g = Poly3.const(b22)
        for k, Fm in enumerate(Fmats):
            g = g + frobenius(Fm, S[k])
        # Try to solve g + γ0 + γ1 p_sum + γ2 p4 = 0 over Q by matching
        # a few monomials (least squares then snap).
        mons = monomials_3(max(d, 3))
        A = []
        rhs = []
        for mon in mons:
            A.append([
                float(1 if mon == (0, 0, 0) else 0),
                float(p_sum.c.get(mon, F(0))),
                float(p4.c.get(mon, F(0))),
            ])
            rhs.append(-float(g.c.get(mon, F(0))))
        A = np.array(A)
        rhs = np.array(rhs)
        try:
            sol, *_ = np.linalg.lstsq(A, rhs, rcond=None)
        except np.linalg.LinAlgError:
            continue
        residual = A @ sol - rhs
        if np.max(np.abs(residual)) > 1e-9:
            continue
        # snap γ
        for gden in (1, 10, 100, 1000, 10000):
            gam = [F(int(round(float(sol[i]) * gden)), gden) for i in range(3)]
            if any(x < 0 for x in gam):
                continue
            residual_g = g + Poly3.const(gam[0]) + p_sum.scale(gam[1]) + p4.scale(gam[2])
            if residual_g.c:
                continue
            obj = F(1) + sum(a) + b11 + sum(Fmats[0][i][i] for i in range(sizes[0]))
            # univariate h ≤ 0 via Sturm after building the 1-point polynomial
            # h = 1 + sum a P + b22 + 3 ⟨F,S(u,u,1)⟩
            # We need h ≤ 0 on I.  Use certify_interval on the Gegenbauer
            # expansion of h, but h is not necessarily a nonnegative
            # combination of P_k.  Use Sturm on h itself by treating it
            # as a 1-var polynomial: no roots in (-1,1/2) and h(endpoints)≤0.
            from unrestricted_dual import (
                _poly_eval, _sign_vars, _sturm_chain, squarefree,
            )
            h_uni = [F(0)] * (d + 3)
            h_uni[0] += F(1) + b22
            for k, ak in enumerate(a, start=1):
                pk = P5[k]
                for i, c in enumerate(pk):
                    if i >= len(h_uni):
                        h_uni.extend([F(0)] * (i + 1 - len(h_uni)))
                    h_uni[i] += ak * c
            for k, Fm in enumerate(Fmats):
                uni = frobenius(Fm, S[k]).restrict_uu1()
                for i, c in enumerate(uni):
                    if i >= len(h_uni):
                        h_uni.extend([F(0)] * (i + 1 - len(h_uni)))
                    h_uni[i] += F(3) * c
            fa = _poly_eval(h_uni, F(-1))
            fb = _poly_eval(h_uni, F(1, 2))
            fm = _poly_eval(h_uni, F(-1, 4))
            if fa > 0 or fb > 0 or fm > 0:
                continue
            sf = squarefree(h_uni)
            chain = _sturm_chain(sf)
            eps = F(1, 10 ** 9)
            nroots = _sign_vars(chain, F(-1) + eps) - _sign_vars(chain, F(1, 2) - eps)
            if nroots != 0:
                continue
            hit = {
                "den": den,
                "gden": gden,
                "bound": str(obj),
                "float_bound": float(obj),
                "certified": True,
                "unrestricted": True,
                "excludes": [k for k in (41, 42, 43, 44) if obj < k],
                "putinar_g": True,
                "sturm_h": True,
                "a": [str(x) for x in a],
                "F_diag": [[str(x) for x in row] for row in Fdiags],
            }
            best = hit
            break
        if best:
            break
    return {"certified": bool(best), "hit": best}


def levenshtein_as_bv() -> dict:
    """The odd Levenshtein dual is a feasible BV dual with all F_k = 0."""
    # Independently, levenshtein.py gives L_5(5,1/2)=48.
    return {
        "name": "Levenshtein_L5_as_BV",
        "bound": "48",
        "float_bound": 48.0,
        "certified": True,
        "unrestricted": True,
        "F_k": "zero",
        "comment": "F_k=0 reduces BV to Delsarte; L_5(5,1/2)=48",
        "excludes": [],
    }


def main() -> int:
    report: dict = {
        "bv_self_tests": [],
        "delsarte_1point": {},
        "levenshtein_as_bv": levenshtein_as_bv(),
        "diagonal_grid": {},
        "slsqp_grid": {},
        "constant_putinar": {},
        "rank1_ansatz": {},
        "lift_attempts": {},
        "best_certified_unrestricted": None,
        "excludes_any_k": [],
        "certified_below_44": False,
    }

    print("== BV self-tests ==", flush=True)
    tests = self_tests()
    for name, ok in tests:
        print(f"  {'OK' if ok else 'FAIL'} {name}", flush=True)
        report["bv_self_tests"].append({"name": name, "ok": ok})
    if not all(ok for _, ok in tests):
        report["comment"] = "S_k^5 self-tests failed; no dual claimed."
        (HERE / "dual_exact.json").write_text(json.dumps(report, indent=2) + "\n")
        return 1

    print("== 1-point Delsarte (Odlyzko–Sloane floor) ==", flush=True)
    num = numerical_delsarte(12)
    cert = None
    if num.get("success"):
        # one rationalization attempt, not a campaign
        c = rationalize(num["c"], 1000)
        cert = certify_interval(c)
    report["delsarte_1point"] = {
        "numerical_deg12": None if not num.get("success") else num["bound"],
        "rational_den1000_certified": bool(cert and cert.get("certified")),
        "rational_bound": None if not cert else cert.get("float_bound"),
        "comment": (
            "Odlyzko–Sloane continuum number ≈46.34.  A 1-point dual "
            "cannot go below that, hence cannot exclude 41–44."
        ),
    }
    print(f"  num={report['delsarte_1point']['numerical_deg12']} "
          f"rational={report['delsarte_1point']['rational_bound']}", flush=True)

    best = {
        "source": "Levenshtein_L5_as_BV",
        "bound": "48",
        "float_bound": 48.0,
        "certified": True,
        "unrestricted": True,
        "excludes": [],
    }

    for d in (1, 2, 3, 4):
        print(f"== degree d={d} ==", flush=True)
        nI, nD = (17, 7) if d <= 3 else (13, 6)
        cache = precompute(d, nI, nD)
        print(f"  grid |I|={len(cache['I'])} |D'|={len(cache['D'])}", flush=True)

        lp = diagonal_lp(d, cache)
        report["diagonal_grid"][str(d)] = {
            "success": lp.get("success"),
            "grid_bound": lp.get("grid_bound"),
            "note": "diagonal F_k on a finite grid; residue until lifted",
        }
        print(f"  diagonal grid bound={lp.get('grid_bound')}", flush=True)

        lift = try_lift_diagonal(d, lp)
        report["lift_attempts"][str(d)] = {
            "certified": lift.get("certified"),
            "hit": lift.get("hit"),
        }
        if lift.get("certified") and lift["hit"]:
            print(f"  LIFT certified bound={lift['hit']['float_bound']} "
                  f"excl={lift['hit']['excludes']}", flush=True)
            if lift["hit"]["float_bound"] < best["float_bound"]:
                best = {
                    "source": f"diagonal-Putinar d={d}",
                    **lift["hit"],
                }

        put = exact_constant_putinar(d)
        report["constant_putinar"][str(d)] = {
            "success": put.get("success"),
            "numerical_bound": put.get("bound"),
            "certified": put.get("certified"),
        }
        print(f"  constant Putinar num={put.get('bound')} "
              f"cert={bool(put.get('certified'))}", flush=True)
        if put.get("certified"):
            hit = put["certified"]
            print(f"    certified {hit['float_bound']} excl={hit['excludes']}",
                  flush=True)
            if hit["float_bound"] < best["float_bound"]:
                best = {"source": f"constant-Putinar d={d}", **hit}

        if d <= 3:
            sl = slsqp_chol(d, cache)
            report["slsqp_grid"][str(d)] = {
                "success": sl.get("success"),
                "grid_bound": sl.get("grid_bound"),
                "message": sl.get("message"),
                "note": "Cholesky F_k on a subsampled grid; residue",
            }
            print(f"  SLSQP grid bound={sl.get('grid_bound')} "
                  f"ok={sl.get('success')}", flush=True)

    report["rank1_ansatz"] = rank1_ansatz_search(2)

    report["best_certified_unrestricted"] = best
    report["excludes_any_k"] = best.get("excludes") or []
    report["certified_below_44"] = bool(best.get("float_bound") is not None
                                        and best["float_bound"] < 44)
    report["comment"] = (
        "Exact S_k^5 matrices over Q, replayed by q4/bv.py self-tests.  "
        "1-point Delsarte is the Odlyzko–Sloane number ≈46.34 and cannot "
        "exclude 41–44.  Low-degree exact Bachoc–Vallentin duals with "
        "constant-multiplier Putinar / Sturm were searched at d=1,2,3,4; "
        "diagonal and Cholesky grid duals are residue.  Nothing certified "
        "below 44.  Mittelmann–Vallentin s_14(5)=44.998… remains the "
        "published upper bound; that number is a high-accuracy SDP, not "
        "an exact SOS certificate, and the hierarchy at d=14 cannot go "
        "below its own optimum ≈44.998."
    )

    if report["certified_below_44"] and best.get("unrestricted"):
        (HERE / "certs").mkdir(exist_ok=True)
        cert = dict(best)
        # store F as strings if present
        (HERE / "certs" / "bv_dual.json").write_text(
            json.dumps(cert, indent=2) + "\n"
        )
        if best.get("gegenbauer_coeffs"):
            (HERE / "certs" / "unrestricted_delsarte.json").write_text(
                json.dumps(cert, indent=2) + "\n"
            )

    (HERE / "dual_exact.json").write_text(json.dumps(report, indent=2) + "\n")
    print("best", best)
    print("certified_below_44", report["certified_below_44"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
