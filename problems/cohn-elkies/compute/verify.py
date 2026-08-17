#!/usr/bin/env python3
"""Independent replay of certs/ce_d2_m5.json.

Rebuilds G,H from stored rational Laguerre coefficients (does not re-solve
the interpolation system), divides out the known double roots, and counts
real roots of the quotients. Exit 0 only if Theorem 3.2 applies.

Usage:
    /tmp/ce-venv/bin/python verify.py
    /tmp/ce-venv/bin/python verify.py certs/ce_d2_m5.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import sympy as sp

T = sp.symbols("t")


def qq(s) -> sp.Rational:
    if isinstance(s, sp.Rational):
        return s
    if isinstance(s, int):
        return sp.QQ(s)
    num, den = sp.fraction(sp.together(sp.sympify(s)))
    return sp.QQ(int(num), int(den))


def laguerre(n: int) -> sp.Poly:
    if n == 0:
        return sp.Poly(1, T, domain=sp.QQ)
    if n == 1:
        return sp.Poly(1 - T, T, domain=sp.QQ)
    Lm2 = sp.Poly(1, T, domain=sp.QQ)
    Lm1 = sp.Poly(1 - T, T, domain=sp.QQ)
    for k in range(1, n):
        num = sp.Poly(2 * k + 1 - T, T, domain=sp.QQ) * Lm1 - k * Lm2
        Lm2, Lm1 = Lm1, sp.Poly(num, T, domain=sp.QQ) / (k + 1)
        Lm1 = sp.Poly(Lm1, T, domain=sp.QQ)
    return Lm1


def combine(indices, coeffs) -> sp.Poly:
    acc = sp.Poly(0, T, domain=sp.QQ)
    for k, c in zip(indices, coeffs):
        acc += qq(c) * laguerre(int(k))
    return sp.Poly(acc, T, domain=sp.QQ)


def double_factor(roots) -> sp.Poly:
    p = sp.Poly(1, T, domain=sp.QQ)
    for r in roots:
        p *= sp.Poly(T - r, T, domain=sp.QQ) ** 2
    return p


def check(path: Path) -> int:
    rec = json.loads(path.read_text())
    t_roots = [qq(s) for s in rec["t_roots"]]
    R = qq(rec["R"])
    G = combine(rec["odd_indices"], rec["a_odd"])
    H = combine(rec["even_indices"], rec["b_even"])
    F = sp.Poly(-G + H, T, domain=sp.QQ)
    hatF = sp.Poly(G + H, T, domain=sp.QQ)

    fails = []

    def need(name, ok):
        print(f"  [{'OK' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    need("G(0)=0", G.eval(0) == 0)
    need("F(0)=hatF(0)", F.eval(0) == hatF.eval(0))
    need("F(0)>0", F.eval(0) > 0)
    need("hatF(R)=0", hatF.eval(R) == 0)
    need("hatF'(R)=0", hatF.diff(T).eval(R) == 0)
    need("F(R)<0", F.eval(R) < 0)
    for i, ti in enumerate(t_roots):
        need(f"G double at t_{i}", G.eval(ti) == 0 and G.diff(T).eval(ti) == 0)
        need(f"H double at t_{i}", H.eval(ti) == 0 and H.diff(T).eval(ti) == 0)

    D = double_factor(t_roots)
    Q, remQ = sp.div(hatF, sp.Poly(T - R, T, domain=sp.QQ) ** 2, domain=sp.QQ)
    need("hatF = (t-R)^2 Q", remQ == 0)
    S, remS = sp.div(Q, D, domain=sp.QQ)
    need("Q = D * S", remS == 0)
    P, remP = sp.div(F, D, domain=sp.QQ)
    need("F = D * P", remP == 0)

    S = sp.Poly(S, T, domain=sp.QQ)
    P = sp.Poly(P, T, domain=sp.QQ)
    nS = int(S.primitive()[1].set_domain(sp.ZZ).count_roots(0, sp.oo))
    nP = int(P.primitive()[1].set_domain(sp.ZZ).count_roots(R, sp.oo))
    need("S has no positive real root", nS == 0)
    need("P has no root in (R, oo)", nP == 0)
    need("S(0)>0 and S.LC()>0", S.eval(0) > 0 and S.LC() > 0)
    need("P(R)<0 and P.LC()<0", P.eval(R) < 0 and P.LC() < 0)

    dens = float(R / (8 * sp.pi))
    hex_d = float(sp.sqrt(3) / 6)
    ratio = dens / hex_d
    print(f"  R = {R} = {float(R):.16f}")
    print(f"  center density <= {dens:.16f}")
    print(f"  hexagonal      = {hex_d:.16f}")
    print(f"  ratio          = {ratio:.16f}")
    print(f"  published CE2003 Table 3 center density = 0.28868")
    print(f"  published CE2003 Table 4 2πr²           = 7.25520")
    need("meets Table 3 (δ ≤ 0.288685)", dens <= 0.288685)
    need("beats Table 4 (R < 7.25520)", float(R) < 7.25520)
    need("stored density matches", abs(dens - rec["center_density"]) < 1e-12)

    if fails:
        print("FAILED:", fails)
        return 1
    print("ALL CHECKS PASSED")
    return 0


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent / "certs" / "ce_d2_m5.json"
    print("verifying", path)
    return check(path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
