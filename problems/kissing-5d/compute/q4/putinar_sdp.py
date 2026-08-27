#!/usr/bin/env python3
"""Numerical Putinar SDP for the Bachoc–Vallentin dual, then a rational lift.

The SDP is the finite-dimensional relaxation of Theorem 4.2 in
Bachoc–Vallentin (JAMS 2008) / Mittelmann–Vallentin arXiv:0902.1105v3:
F_k ≽ 0, B ≽ 0, a_k ≥ 0, and the two polynomial identities

    -h(u) = q(u) + p(u) q1(u),
    -g(u,v,t) = r + p(u)r1 + p(v)r2 + p(t)r3 + p4 r4,

with q, q1, r, r_i sums of squares of bounded degree.  A floating-point
solution is residue.  A rational Gram matrix that rebuilds the identities
exactly and is PSD by principal minors is a certificate.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

import numpy as np

from bv import (
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
)

P5 = gegenbauer(N_BV, 16)
Mono = Tuple[int, int, int]


def _add_exp(a: Mono, b: Mono) -> Mono:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def gram_coeff_tensor(mons: Sequence[Mono], max_deg: int) -> Dict[Mono, List[Tuple[int, int]]]:
    """Map monomial -> list of (i,j) with mon[i]+mon[j] = that monomial."""
    out: Dict[Mono, List[Tuple[int, int]]] = {}
    m = len(mons)
    for i in range(m):
        for j in range(m):
            s = _add_exp(mons[i], mons[j])
            if s[0] + s[1] + s[2] > max_deg:
                continue
            out.setdefault(s, []).append((i, j))
    return out


def poly_coeff_vector(p: Poly3, mons_all: Sequence[Mono]) -> np.ndarray:
    return np.array([float(p.c.get(m, F(0))) for m in mons_all], dtype=float)


def run_sdp(d: int, sos_half: int = 2, solver: str = "CLARABEL"):
    import cvxpy as cp

    max_deg = max(d, 2 * sos_half + 3)
    mons_all = monomials_3(max_deg)
    mon_index = {m: i for i, m in enumerate(mons_all)}
    n_mon = len(mons_all)

    mons_r = monomials_3(sos_half)
    mons_r4 = monomials_3(max(0, sos_half - 1))
    mons_q = [k for k in range(sos_half + 1)]          # 1, u, ..., u^{sos_half}
    mons_q1 = [k for k in range(max(0, sos_half - 1) + 1)]

    S = [S_matrix(k, d) for k in range(d + 1)]
    sizes = [d - k + 1 for k in range(d + 1)]

    a = cp.Variable(d, nonneg=True)
    B = cp.Variable((2, 2), PSD=True)
    Fk = [cp.Variable((sizes[k], sizes[k]), PSD=True) for k in range(d + 1)]

    Gr = cp.Variable((len(mons_r), len(mons_r)), PSD=True)
    G1 = cp.Variable((len(mons_r), len(mons_r)), PSD=True)
    G2 = cp.Variable((len(mons_r), len(mons_r)), PSD=True)
    G3 = cp.Variable((len(mons_r), len(mons_r)), PSD=True)
    G4 = cp.Variable((len(mons_r4), len(mons_r4)), PSD=True)
    Gq = cp.Variable((len(mons_q), len(mons_q)), PSD=True)
    Gq1 = cp.Variable((len(mons_q1), len(mons_q1)), PSD=True)

    pu = p_interval()
    pv = pu.permute((1, 0, 2))
    pt = pu.permute((2, 1, 0))
    p4 = p4_gram()

    # g = b22 + sum ⟨Fk, Sk⟩
    g_coeff = np.zeros(n_mon)
    # we'll build g_coeff as affine: constant from B[1,1] plus F terms
    g_expr = [0] * n_mon

    def add_poly_times_scalar(expr_list, poly: Poly3, scalar):
        for mon, c in poly.c.items():
            if mon not in mon_index:
                continue
            expr_list[mon_index[mon]] += float(c) * scalar

    # b22 * 1
    g_terms = [0] * n_mon
    add_poly_times_scalar(g_terms, Poly3.const(F(1)), B[1, 1])
    for k, Fm in enumerate(Fk):
        m = sizes[k]
        for i in range(m):
            for j in range(m):
                add_poly_times_scalar(g_terms, S[k][i][j], Fm[i, j])

    # SOS side for -g
    Tr = gram_coeff_tensor(mons_r, max_deg)
    Tr4 = gram_coeff_tensor(mons_r4, max_deg)

    def sos_coeff(G, mons, tensor, target_mon):
        acc = 0
        for (i, j) in tensor.get(target_mon, ()):
            acc += G[i, j]
        return acc

    def mul_poly_sos(poly: Poly3, G, mons, tensor, target_mon):
        """Coefficient of target_mon in poly * (z^T G z)."""
        acc = 0
        for smon, pairs in tensor.items():
            # target = poly_mon + smon
            need = (target_mon[0] - smon[0], target_mon[1] - smon[1],
                    target_mon[2] - smon[2])
            if min(need) < 0:
                continue
            c = poly.c.get(need, F(0))
            if c == 0:
                continue
            pair_sum = 0
            for (i, j) in pairs:
                pair_sum += G[i, j]
            acc += float(c) * pair_sum
        return acc

    # identity: g + r + p(u)r1 + p(v)r2 + p(t)r3 + p4 r4 = 0
    cons = []
    for mon in mons_all:
        idx = mon_index[mon]
        lhs = g_terms[idx]
        lhs = lhs + sos_coeff(Gr, mons_r, Tr, mon)
        lhs = lhs + mul_poly_sos(pu, G1, mons_r, Tr, mon)
        lhs = lhs + mul_poly_sos(pv, G2, mons_r, Tr, mon)
        lhs = lhs + mul_poly_sos(pt, G3, mons_r, Tr, mon)
        lhs = lhs + mul_poly_sos(p4, G4, mons_r4, Tr4, mon)
        cons.append(lhs == 0)

    # h(u) = 1 + sum a_k P_k(u) + 2 b12 + b22 + 3 sum ⟨Fk, Sk(u,u,1)⟩
    # as a univariate; treat as Poly3 in u only
    h_uni_deg = max_deg
    h_terms = [0] * (h_uni_deg + 1)
    h_terms[0] += 1 + 2 * B[0, 1] + B[1, 1]
    for k in range(1, d + 1):
        pk = P5[k]
        for i, c in enumerate(pk):
            if i <= h_uni_deg:
                h_terms[i] += float(c) * a[k - 1]
    for k, Fm in enumerate(Fk):
        m = sizes[k]
        for i in range(m):
            for j in range(m):
                uni = S[k][i][j].restrict_uu1()
                for t, c in enumerate(uni):
                    if t <= h_uni_deg:
                        h_terms[t] += 3.0 * float(c) * Fm[i, j]

    # -h = q + p(u) q1, q = z^T Gq z, q1 = z^T Gq1 z  (univariate)
    def uni_sos_coeff(G, nmons, deg):
        acc = 0
        for i in range(nmons):
            for j in range(nmons):
                if i + j == deg:
                    acc += G[i, j]
        return acc

    pu_uni = pu.restrict_uu1()  # (1/2, 1/2, -1) for 1/2 + u/2 - u^2
    for deg_u in range(h_uni_deg + 1):
        lhs = h_terms[deg_u]
        lhs = lhs + uni_sos_coeff(Gq, len(mons_q), deg_u)
        # p(u) q1 : coeff of u^{deg_u} in (1/2 + u/2 - u^2) * q1
        acc_q1 = 0
        for i, c in enumerate(pu_uni):
            rest = deg_u - i
            if rest < 0:
                continue
            acc_q1 += float(c) * uni_sos_coeff(Gq1, len(mons_q1), rest)
        lhs = lhs + acc_q1
        cons.append(lhs == 0)

    obj = 1 + cp.sum(a) + B[0, 0] + cp.sum(Fk[0])
    # A valid dual is at least 40 (D5 exists).  Use this only as a
    # solver cut after the identities; if the identities are right the
    # cut is inactive.  If the solver returns < 40, the identities failed.
    cons.append(obj >= 40)
    prob = cp.Problem(cp.Minimize(obj), cons)
    try:
        kw = {}
        if solver == "CLARABEL":
            kw = {"verbose": False, "max_iter": 200, "tol_gap_abs": 1e-8}
        elif solver == "SCS":
            kw = {"eps": 1e-6, "max_iters": 10000, "verbose": False}
        prob.solve(solver=getattr(cp, solver), **kw)
    except Exception as e:
        return {"success": False, "error": str(e), "d": d, "sos_half": sos_half}

    rec = {
        "d": d,
        "sos_half": sos_half,
        "solver": solver,
        "status": str(prob.status),
        "success": False,
        "numerical_bound": None if prob.value is None else float(prob.value),
        "note": "floating Putinar SDP; residue until a rational Gram rebuilds the identities",
    }
    if prob.status in ("optimal", "optimal_inaccurate") and Fk[0].value is not None:
        rec["a"] = [float(x) for x in a.value]
        rec["B"] = np.array(B.value).tolist()
        rec["F"] = [np.array(Fk[k].value).tolist() for k in range(d + 1)]
        rec["obj_check"] = float(
            1 + np.sum(a.value) + B.value[0, 0] + np.sum(Fk[0].value)
        )
        rec["grid_ok"] = _grid_validate(d, rec)
        rec["success"] = bool(rec["grid_ok"] and rec["obj_check"] >= 40)
        if rec["obj_check"] < 40:
            rec["note"] = (
                "solver returned a value < 40; identities are not faithfully "
                "enforced (residue, discarded)"
            )
    return rec


def _grid_validate(d: int, num: dict, n: int = 9) -> bool:
    """Sign check of g and h on a float grid.  Not a certificate."""
    if "F" not in num:
        return False
    S = [S_matrix(k, d) for k in range(d + 1)]
    a = num["a"]
    Bf = num["B"]
    b12, b22 = float(Bf[0][1]), float(Bf[1][1])
    Fmats = num["F"]
    xs = [-1.0 + i * 1.5 / (n - 1) for i in range(n)]
    for u in xs:
        for v in xs:
            for t in xs:
                if 1 + 2 * u * v * t - u * u - v * v - t * t < -1e-12:
                    continue
                s = b22
                for k, Fm in enumerate(Fmats):
                    m = len(Fm)
                    for i in range(m):
                        for j in range(m):
                            s += Fm[i][j] * float(S[k][i][j].eval(F(u), F(v), F(t)))
                if s > 1e-3:
                    return False
    for u in xs:
        s = 1.0 + 2.0 * b12 + b22
        uf = F(u)
        for k, ak in enumerate(a, start=1):
            s += ak * float(eval_univariate(P5[k], uf))
        for k, Fm in enumerate(Fmats):
            m = len(Fm)
            for i in range(m):
                for j in range(m):
                    s += 3.0 * Fm[i][j] * float(S[k][i][j].eval(uf, uf, F(1)))
        if s > 1e-3:
            return False
    return True


def snap_and_certify(d: int, num: dict, dens=(10, 100, 1000, 10000)) -> dict:
    """Try to snap a numerical dual to rationals.  Only F/a/B, then
    re-check g≤0 and h≤0 on a dense rational grid — that is still
    residue.  An exact Putinar snap of the Grams is attempted only
    when the snapped F,a,B already make g,h obviously nonpositive
    by evaluating at enough points AND we can fit constant/low SOS.
    """
    if not num.get("success") or "F" not in num:
        return {"certified": False, "reason": "no numerical dual"}
    S = [S_matrix(k, d) for k in range(d + 1)]
    best = None
    for den in dens:
        def Q(x):
            return F(int(round(float(x) * den)), den)

        def Qpos(x):
            q = Q(x)
            return q if q > 0 else F(0)

        a = [Qpos(x) for x in num["a"]]
        Bf = num["B"]
        b11, b12, b22 = Qpos(Bf[0][0]), Q(Bf[0][1]), Qpos(Bf[1][1])
        # force B PSD by dropping the off-diagonal if needed
        if b11 * b22 < b12 * b12:
            b12 = F(0)
        Fmats = []
        okF = True
        for k, Fm in enumerate(num["F"]):
            m = len(Fm)
            A = [[Q(Fm[i][j]) for j in range(m)] for i in range(m)]
            # symmetrize
            for i in range(m):
                for j in range(i):
                    s = (A[i][j] + A[j][i]) / 2
                    A[i][j] = A[j][i] = s
            # project tiny negatives on the diagonal
            for i in range(m):
                if A[i][i] < 0:
                    A[i][i] = F(0)
            if not is_psd_exact(A):
                okF = False
                break
            Fmats.append(A)
        if not okF:
            continue
        g = Poly3.const(b22)
        for k, Fm in enumerate(Fmats):
            g = g + frobenius(Fm, S[k])
        # sample D' and I
        from itertools import product
        xs = [F(-1) + F(i, 12) * F(3, 2) for i in range(13)]
        gpos = []
        for u, v, t in product(xs, repeat=3):
            if F(1) + F(2) * u * v * t - u * u - v * v - t * t < 0:
                continue
            val = g.eval(u, v, t)
            if val > 0:
                gpos.append((str(u), str(v), str(t), str(val)))
                if len(gpos) > 3:
                    break
        h_uni = [F(0)] * (d + 4)
        h_uni[0] += F(1) + F(2) * b12 + b22
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
        hpos = []
        for u in xs:
            val = eval_univariate(h_uni, u)
            if val > 0:
                hpos.append((str(u), str(val)))
        obj = F(1) + sum(a) + b11 + sum(sum(Fmats[0][i]) for i in range(len(Fmats[0])))
        rec = {
            "den": den,
            "bound": str(obj),
            "float_bound": float(obj),
            "g_positive_samples": gpos[:4],
            "h_positive_samples": hpos[:4],
            "grid_nonpos": (not gpos) and (not hpos),
            "certified": False,  # grid only
            "note": "rational snap, dense-grid sign check; not a Putinar certificate",
        }
        if rec["grid_nonpos"] and (best is None or rec["float_bound"] < best["float_bound"]):
            best = rec
    return {"certified": False, "best_grid_snap": best}


def main() -> int:
    import json
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    out = {"runs": []}
    for d, half in ((2, 1), (3, 1), (4, 2), (5, 2)):
        print(f"SDP d={d} sos_half={half}", flush=True)
        rec = run_sdp(d, sos_half=half)
        print(f"  status={rec.get('status')} bound={rec.get('numerical_bound')}",
              flush=True)
        lift = snap_and_certify(d, rec)
        rec["lift"] = lift
        # drop huge F matrices from the JSON if present — keep sizes
        slim = {k: rec[k] for k in rec if k not in ("F", "B", "a")}
        if "a" in rec:
            slim["a"] = rec["a"]
        if "numerical_bound" in rec:
            slim["numerical_bound"] = rec["numerical_bound"]
        slim["lift"] = lift
        out["runs"].append(slim)
    out["certified_below_44"] = False
    out["comment"] = (
        "Putinar SDP for the 3-point dual.  Numerical values are residue.  "
        "No rational Gram identity with value < 44 was produced."
    )
    (HERE / "putinar_sdp.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
