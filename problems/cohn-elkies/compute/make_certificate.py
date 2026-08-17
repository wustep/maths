"""Build and exactly certify a d=2 Cohn–Elkies Laguerre–Gaussian function.

Reconstruction of Cohn–Elkies 2003 §7 / Table 4 (n=2, m=5) over Q.
Sign conditions are reduced to: two exact polynomial divisions, then
`count_roots` on the square-free quotients S and P.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import sympy as sp

from ce_laguerre import (
    T,
    build_G,
    build_H,
    qq,
    _as_qq,
    hex_R,
    center_density,
    ratio_vs_hex,
    _odd_indices,
    _even_indices,
)

CE_T_STR = ["2177/100", "2902/100", "5079/100", "6534/100", "9019/100"]


def double_factor(roots) -> sp.Poly:
    p = sp.Poly(1, T, domain=sp.QQ)
    for r in roots:
        p *= sp.Poly(T - r, T, domain=sp.QQ) ** 2
    return p


def isolate_last_odd_root(G: sp.Poly, t_roots) -> tuple[sp.Rational, sp.Rational]:
    """G / (t * ∏(t-t_i)^2) is square-free of degree 2m+1 and has one positive root."""
    D = double_factor(t_roots)
    num = G
    den = sp.Poly(T, T, domain=sp.QQ) * D
    U, rem = sp.div(num, den, domain=sp.QQ)
    if rem != 0:
        raise RuntimeError("G does not vanish to the expected order at 0 and t_i")
    U = sp.Poly(U, T, domain=sp.QQ)
    pos = []
    for r in sp.real_roots(U):
        val = float(r)
        if val > 1e-12:
            pos.append((val, r))
    if not pos:
        raise RuntimeError("U has no positive real root")
    pos.sort()
    print(f"  U positive roots: {[p[0] for p in pos]}", flush=True)
    r = pos[-1][1]  # last sign change
    # Isolating intervals for all real roots of U; take the rightmost positive one.
    ivs = U.intervals(eps=sp.QQ(1, 10**16))
    # ivs is (( (a,b), multiplicity ), ...)
    best = None
    for (a, b), _mult in ivs:
        a, b = _as_qq(a), _as_qq(b)
        if b <= 0:
            continue
        if best is None or a > best[0]:
            best = (a, b)
    if best is None:
        raise RuntimeError("no positive isolating interval")
    return best


def certify(G, H, R, t_roots) -> dict:
    F = sp.Poly(-G + H, T, domain=sp.QQ)
    hatF = sp.Poly(G + H, T, domain=sp.QQ)
    D = double_factor(t_roots)
    linR = sp.Poly(T - R, T, domain=sp.QQ)

    checks = {}

    def note(name, ok, extra=None):
        checks[name] = {"ok": bool(ok), "extra": extra}
        print(f"  [{('OK' if ok else 'FAIL'):4s}] {name}" + (f"  ({extra})" if extra else ""), flush=True)

    note("G(0)=0", G.eval(0) == 0, str(G.eval(0)))
    note("F(0)=hatF(0)", F.eval(0) == hatF.eval(0))
    note("F(0)>0", F.eval(0) > 0)
    note("hatF(R)=0", hatF.eval(R) == 0)
    note("hatF'(R)=0", hatF.diff(T).eval(R) == 0)
    note("F(R)<0", F.eval(R) < 0, str(F.eval(R)))

    for i, ti in enumerate(t_roots):
        note(f"G(t_{i})=0", G.eval(ti) == 0)
        note(f"G'(t_{i})=0", G.diff(T).eval(ti) == 0)
        note(f"H(t_{i})=0", H.eval(ti) == 0)
        note(f"H'(t_{i})=0", H.diff(T).eval(ti) == 0)

    Q, remQ = sp.div(hatF, linR**2, domain=sp.QQ)
    note("hatF divisible by (t-R)^2", remQ == 0)
    S, remS = sp.div(Q, D, domain=sp.QQ)
    note("Q divisible by double t_i factor", remS == 0)
    P, remP = sp.div(F, D, domain=sp.QQ)
    note("F divisible by double t_i factor", remP == 0)

    S = sp.Poly(S, T, domain=sp.QQ)
    P = sp.Poly(P, T, domain=sp.QQ)
    SZ = S.primitive()[1].set_domain(sp.ZZ)
    PZ = P.primitive()[1].set_domain(sp.ZZ)

    t0 = time.time()
    nS = int(SZ.count_roots(0, sp.oo))
    note("S has no positive real roots", nS == 0, f"count={nS} in {time.time()-t0:.2f}s")
    t0 = time.time()
    nP = int(PZ.count_roots(R, sp.oo))
    note("P has no roots in (R,oo)", nP == 0, f"count={nP} in {time.time()-t0:.2f}s")

    note("S(0)>0", S.eval(0) > 0)
    note("S.LC()>0", S.LC() > 0)
    note("P(R)<0", P.eval(R) < 0)
    note("P.LC()<0", P.LC() < 0)

    ok = all(v["ok"] for v in checks.values())
    return {
        "ok": ok,
        "checks": checks,
        "deg_S": int(S.degree()),
        "deg_P": int(P.degree()),
        "S_monomial": [str(c) for c in S.all_coeffs()],
        "P_monomial": [str(c) for c in P.all_coeffs()],
        "F0": str(F.eval(0)),
        "hatF0": str(hatF.eval(0)),
    }


def main():
    t_roots = [qq(s) for s in CE_T_STR]
    print("=== build G ===", flush=True)
    t0 = time.time()
    G, a_odd = build_G(5, t_roots)
    print(f"  {time.time()-t0:.3f}s  deg={G.degree()}", flush=True)

    print("=== isolate last odd root of G ===", flush=True)
    t0 = time.time()
    lo, hi = isolate_last_odd_root(G, t_roots)
    print(f"  isolating interval ({lo}, {hi})", flush=True)
    print(f"  floats ({float(lo):.16f}, {float(hi):.16f}) in {time.time()-t0:.3f}s", flush=True)
    print(f"  hex R = {hex_R():.16f}", flush=True)

    # Smallest simple dyadic/decimal rational strictly above hi
    # Use denominator 10^8 first; bump if needed.
    R = None
    for den in (10**k for k in range(6, 13)):
        num = int(hi * den) + 1  # hi is QQ; int() of a slightly larger float is unsafe
        # exact: ceil(hi*den) if not integer else hi*den + 1
        prod = hi * den
        if prod == sp.Integer(prod):
            num = int(prod) + 1
        else:
            num = int(sp.floor(prod)) + 1
        cand = qq(f"{num}/{den}")
        if cand > hi:
            R = cand
            print(f"  candidate R = {num}/{den} = {float(cand):.16f}", flush=True)
            break
    if R is None:
        raise RuntimeError("failed to pick R")

    print("=== build H ===", flush=True)
    t0 = time.time()
    H, b_even = build_H(5, t_roots, R, G)
    print(f"  {time.time()-t0:.3f}s", flush=True)

    print("=== certify signs ===", flush=True)
    t0 = time.time()
    crep = certify(G, H, R, t_roots)
    print(f"  certify wall {time.time()-t0:.3f}s  ok={crep['ok']}", flush=True)

    dens = center_density(R)
    rat = ratio_vs_hex(R)
    rec = {
        "description": (
            "Exact Cohn–Elkies admissible function in dimension 2, "
            "Laguerre–Gaussian ansatz with m=5 forced double roots from "
            "Cohn–Elkies 2003 Table 4 (two-decimal rationals). "
            "R is a rational strictly above the isolated last odd root of G."
        ),
        "m": 5,
        "t_roots": CE_T_STR,
        "R": str(R),
        "R_float": float(R),
        "last_odd_isolating_interval": [str(lo), str(hi)],
        "last_odd_interval_float": [float(lo), float(hi)],
        "hex_R": hex_R(),
        "hex_center_density": float(sp.sqrt(3) / 6),
        "center_density": dens,
        "ratio_vs_hex": rat,
        "published_CE2003_table3_center_density": 0.28868,
        "published_CE2003_table4_R": 7.25520,
        "beats_table4_R": bool(float(R) < 7.25520),
        "meets_table3_five_decimals": bool(dens <= 0.2886849999),
        "odd_indices": _odd_indices(5),
        "even_indices": _even_indices(5),
        "a_odd": [str(c) for c in a_odd],
        "b_even": [str(c) for c in b_even],
        "G_monomial": [str(c) for c in G.all_coeffs()],
        "H_monomial": [str(c) for c in H.all_coeffs()],
        "F_monomial": [str(c) for c in sp.Poly(-G + H, T, domain=sp.QQ).all_coeffs()],
        "hatF_monomial": [str(c) for c in sp.Poly(G + H, T, domain=sp.QQ).all_coeffs()],
        "certify": crep,
        "theorem": (
            "Cohn–Elkies 2003 Theorem 3.2: f = F(t) exp(-t/2) with t=2π|x|² "
            "satisfies f(0)=hat f(0)>0, f≤0 for |x|≥r, hat f≥0 everywhere, "
            "hence center density ≤ (r/2)^2 = R/(8π)."
        ),
    }
    out = Path("certs/ce_d2_m5.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rec, indent=2))
    print("WROTE", out)
    print(f"R={R} dens={dens:.16f} ratio={rat:.16f} beats_table4={rec['beats_table4_R']}")
    return 0 if crep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
