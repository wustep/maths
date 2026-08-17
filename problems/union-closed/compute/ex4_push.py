"""Push Liu's 2-point analysis using Example-4 CIID instead of Example-5.

Liu's critical complement-atom x* ≈ 0.6908 makes Example-5 meet h(I)=h(x²).
Example 4 drives Π_{1-x,1-x}(0,0) to 1/2, so h=1 > h(x²).  That extra
slack should move the critical mean.

We scan the 2-atomic families
  (A) support {b, 1}   (Sawin ray)
  (B) support {s, 1} with s = 1-x ∈ (0, 1/2]   (Liu complement ray)
  (C) general 2-atomic
and binary-search the largest c such that some mix
  (1-β) iid + β Example-4-C3
has ratio ≥ 1 on the whole scan with mean ≤ c.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from entropy import a_example4, h, h_or_example4, h_or_indep, pi_example4

LN2 = math.log(2)


def c3_ex4(x, y, p, n=21):
    # Linear in the C3 parameter u = P(x,x) ∈ [p², p], so the min is an endpoint.
    fn = h_or_example4
    best = 1e9
    for u in (p * p, p):
        pxx, pxy, pyy = u, p - u, 1.0 - 2.0 * p + u
        val = pxx * fn(x, x) + 2.0 * pxy * fn(x, y) + pyy * fn(y, y)
        if val < best:
            best = val
    return best


def iid_prod(x, y, p):
    return (
        p * p * h_or_indep(x, x)
        + 2 * p * (1 - p) * h_or_indep(x, y)
        + (1 - p) * (1 - p) * h_or_indep(y, y)
    )


def eh_of(x, y, p):
    return p * h(x) + (1 - p) * h(y)


def pack(x, y, p):
    eh = eh_of(x, y, p)
    if eh <= 1e-16:
        return None
    return {
        "x": x,
        "y": y,
        "p": p,
        "mean": p * x + (1 - p) * y,
        "eh": eh,
        "eiid": iid_prod(x, y, p),
        "e4": c3_ex4(x, y, p),
    }


def ratio(rec, beta):
    num = (1 - beta) * rec["eiid"] + beta * rec["e4"]
    return num / rec["eh"]


def min_ratio(recs, beta, c):
    m = 1e9
    arg = None
    for r in recs:
        if r["mean"] <= c + 1e-15:
            val = ratio(r, beta)
            if val < m:
                m = val
                arg = r
    return m, arg


def best_beta_and_c(recs, c_lo, c_hi, betas):
    """Largest c in [c_lo, c_hi] for which some beta has min-ratio ≥ 1."""
    # For each beta, binary-search c
    best = {"c": c_lo, "beta": None, "min_ratio": None, "arg": None}
    for beta in betas:
        lo, hi = c_lo, c_hi
        ok = None
        for _ in range(28):
            mid = 0.5 * (lo + hi)
            m, arg = min_ratio(recs, beta, mid)
            if m >= 1.0:
                ok = (mid, m, arg)
                lo = mid
            else:
                hi = mid
        if ok and ok[0] > best["c"]:
            best = {
                "c": ok[0],
                "beta": beta,
                "min_ratio": ok[1],
                "arg": {
                    k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                    for k, v in ok[2].items()
                },
            }
    return best


def build_recs():
    recs = []
    # Ray A: {b, 1}
    for b in np.linspace(0.05, 0.49, 220):
        for a in np.linspace(0.0, 0.49, 160):
            r = pack(b, 1.0, 1.0 - a)  # P(S=b)=1-a, P(S=1)=a
            if r:
                recs.append(r)
    # Ray B: {s, 1} with s in (0, 0.5]  (same as A actually if s=b)
    # already covered.
    # Ray C: {0, x}
    for x in np.linspace(0.05, 0.95, 220):
        for p in np.linspace(0.05, 0.99, 160):
            r = pack(x, 0.0, p)
            if r:
                recs.append(r)
    # General 2-atomic, moderate grid
    xs = np.linspace(0.0, 1.0, 55)
    for i, x in enumerate(xs):
        for y in xs[i:]:
            for p in np.linspace(0.0, 1.0, 45):
                r = pack(float(x), float(y), float(p))
                if r:
                    recs.append(r)
    return recs


def liu_style_analytic_ex4():
    """Solve the 2-point {0,x} critical equations for Example 4.

    On P(X=x)=p, P(X=0)=1-p  (S ∈ {1-x, 1}):
      mean = 1 - p x
      eh = p h(x)
      eiid = p² h(x²)
      e4 = p² h( x² + a(1-x)² x (1-x) )
    Equality iid: p = h(x)/h(x²)
    We then choose β so the derivative along d(px)=0 vanishes, and
    report c = 1-px.  Also scan x to maximise c among points where
    the mixed derivative test is satisfied and nearby ratios stay ≥ 1.
    """
    xs = np.linspace(0.50, 0.78, 400)
    rows = []
    for x in xs:
        hx, hx2 = h(x), h(x * x)
        if hx2 <= 1e-15 or hx <= 1e-15:
            continue
        p = hx / hx2
        if not (0.0 < p < 1.0):
            continue
        s = 1.0 - x
        pi = x * x + a_example4(s) ** 2 * x * (1.0 - x)
        e4 = p * p * h(pi)
        eiid = p * p * hx2
        eh = p * hx
        mean = 1.0 - p * x
        # β such that d((1-β)eiid + β e4 - eh)=0 along d(px)=0
        # finite diff in (p, x)
        eps = 1e-7

        def stats(pp, xx):
            if xx <= 0 or xx >= 1 or pp <= 0 or pp >= 1:
                return None
            hxx, hxx2 = h(xx), h(xx * xx)
            ss = 1.0 - xx
            pii = xx * xx + a_example4(ss) ** 2 * xx * (1.0 - xx)
            return (
                pp * hxx,
                pp * pp * hxx2,
                pp * pp * h(pii),
                pp * xx,
            )

        s0 = stats(p, x)
        sp = stats(p + eps, x)
        sx = stats(p, x + eps)
        if not (s0 and sp and sx):
            continue
        deh_p = (sp[0] - s0[0]) / eps
        diid_p = (sp[1] - s0[1]) / eps
        d4_p = (sp[2] - s0[2]) / eps
        dmu_p = (sp[3] - s0[3]) / eps
        deh_x = (sx[0] - s0[0]) / eps
        diid_x = (sx[1] - s0[1]) / eps
        d4_x = (sx[2] - s0[2]) / eps
        dmu_x = (sx[3] - s0[3]) / eps
        # direction da=dmu_x, db=-dmu_p
        da, db = dmu_x, -dmu_p
        A = diid_p * da + diid_x * db
        B = d4_p * da + d4_x * db
        C = deh_p * da + deh_x * db
        denom = B - A
        beta = (C - A) / denom if abs(denom) > 1e-18 else None
        r_iid = eiid / eh
        r_4 = e4 / eh
        rows.append(
            {
                "x": float(x),
                "p": float(p),
                "mean": float(mean),
                "pi": float(pi),
                "r_iid": float(r_iid),
                "r_ex4": float(r_4),
                "beta": None if beta is None else float(beta),
                "h_x2": float(hx2),
                "h_pi": float(h(pi)),
            }
        )
    # pick the row with β in (0,1) maximising mean, and the Liu-style
    # row nearest where r_ex4 is closest to 1 (both couplings tight)
    interior = [r for r in rows if r["beta"] is not None and 0 < r["beta"] < 1]
    tight = min(rows, key=lambda r: abs(r["r_ex4"] - 1.0))
    best_mean = max(interior, key=lambda r: r["mean"]) if interior else None
    return {
        "n": len(rows),
        "liu_style_tight_ex4": tight,
        "best_mean_with_beta_in_01": best_mean,
        "sample": rows[::40],
    }


def main():
    print("analytic Example-4 2-point...", flush=True)
    analytic = liu_style_analytic_ex4()
    print("tight", analytic["liu_style_tight_ex4"], flush=True)
    print("best mean", analytic["best_mean_with_beta_in_01"], flush=True)

    print("building scan...", flush=True)
    recs = build_recs()
    print("n recs", len(recs), flush=True)
    betas = [0.0, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.20, 0.25, 0.30]
    # also the analytic beta if we have one
    if analytic["best_mean_with_beta_in_01"] and analytic["best_mean_with_beta_in_01"][
        "beta"
    ]:
        betas.append(analytic["best_mean_with_beta_in_01"]["beta"])
    print("searching betas...", flush=True)
    best = best_beta_and_c(recs, 0.3819, 0.3860, betas)
    print("best", best, flush=True)

    # evaluate Liu's quoted β=0.10005 and a few c's
    table = {}
    for beta in [0.0, 0.08, 0.10, 0.12, 0.16, 0.20]:
        table[str(beta)] = {}
        for c in [0.38196601125, 0.38234553337, 0.38270908792, 0.38280, 0.38300, 0.38350]:
            m, arg = min_ratio(recs, beta, c)
            table[str(beta)][str(c)] = {
                "min_ratio": m,
                "arg_mean": None if arg is None else arg["mean"],
                "arg_x": None if arg is None else arg["x"],
                "arg_y": None if arg is None else arg["y"],
                "arg_p": None if arg is None else arg["p"],
            }

    out = {
        "analytic": analytic,
        "scan_best": best,
        "table": table,
        "n_recs": len(recs),
    }
    path = Path(__file__).resolve().parent / "ex4_push.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
