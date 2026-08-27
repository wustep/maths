#!/usr/bin/env python3
"""Iterated complex-squaring pullback does not beat the quadratic ceiling.

Φ(u,v) = (u² − v², 2uv) is z ↦ z² on R² ≅ C. The Remark 4 pullback
of arXiv:2604.12883v1 is Y = adj(DΦ)(X ∘ Φ), i.e.

    Yu = q_v P(Φ) − p_v Q(Φ),
    Yv = −q_u P(Φ) + p_u Q(Φ),

so DΦ · Y = (det DΦ)(X ∘ Φ). One degree-m step has
deg Y ≤ n m + (m−1) and at most m² regular real sheets (Bézout).

This program certifies, for the radial cubic of §6 (ρ² = 1/4) and
for the linear centre (y, −x):

  * the adj identity and det DΦ = 4(u²+v²);
  * one-step degree exactly 7 (n=3, m=2) and two-step degree 15;
  * regular real preimages of a generic point: 2, not 4;
  * the k = 1..6 arithmetic: N = (n+1)2^k − 1, Bézout ceiling 4^k,
    actual complex sheets 2^k = (N+1)/(n+1), Chebyshev one-step
    of degree m = 2^k attains m² = 4^k at the same N.

The super-quadratic claim is dropped. Iteration of this map is
linear in N, not quadratic, and does not attain m² per step.
It does not beat Theorem 2. Do not cite 252/1080/1380/2012 here.

Replay: python3 verify.py
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
U, V, X, Ys = sp.symbols("u v x y")


def fail(msg: str) -> None:
    raise SystemExit(f"verify.py FAIL: {msg}")


def total_deg(expr, gens) -> int:
    expr = sp.expand(expr)
    if expr == 0:
        return -1
    return int(sp.Poly(expr, gens).total_degree())


def monomials_qq(expr, gens=(U, V)) -> list[dict[str, int]]:
    poly = sp.Poly(sp.expand(expr), *gens, domain=sp.QQ)
    out = []
    for exp, coeff in poly.as_dict().items():
        frac = Fraction(int(coeff.p), int(coeff.q))
        out.append(
            {
                "u": int(exp[0]),
                "v": int(exp[1]),
                "num": frac.numerator,
                "den": frac.denominator,
            }
        )
    out.sort(key=lambda m: (m["u"] + m["v"], m["u"], m["v"]))
    return out


def dump_monomials(prefix: str, expr) -> list[str]:
    return [
        f"{prefix} {m['u']} {m['v']} {m['num']} {m['den']}" for m in monomials_qq(expr)
    ]


def phi_components():
    return U**2 - V**2, 2 * U * V


def adj_pullback(p, q, P, Q):
    """Y = adj(DΦ)(X ∘ Φ). Returns Yu, Yv, det, Du, Dv."""
    pu, pv = sp.diff(p, U), sp.diff(p, V)
    qu, qv = sp.diff(q, U), sp.diff(q, V)
    det = sp.expand(pu * qv - pv * qu)
    Pc = sp.expand(P.subs({X: p, Ys: q}))
    Qc = sp.expand(Q.subs({X: p, Ys: q}))
    Yu = sp.expand(qv * Pc - pv * Qc)
    Yv = sp.expand(-qu * Pc + pu * Qc)
    Du = sp.expand(pu * Yu + pv * Yv - det * Pc)
    Dv = sp.expand(qu * Yu + qv * Yv - det * Qc)
    return Yu, Yv, det, Du, Dv


def radial_cubic(rho2=sp.Rational(1, 4)):
    P = Ys - X * (X**2 + Ys**2 - rho2)
    Q = -X - Ys * (X**2 + Ys**2 - rho2)
    return P, Q


def linear_center():
    return Ys, -X


def chebyshev_T2():
    return 2 * U**2 - 1, 2 * V**2 - 1


def check_identity_and_degree() -> dict[str, Any]:
    p, q = phi_components()
    pu, pv = sp.diff(p, U), sp.diff(p, V)
    qu, qv = sp.diff(q, U), sp.diff(q, V)
    det = sp.expand(pu * qv - pv * qu)
    expect_det = sp.expand(4 * (U**2 + V**2))
    if det != expect_det:
        fail(f"det DΦ = {det} != 4(u^2+v^2)")
    if pu != qv or pv != -qu:
        fail("Cauchy–Riemann failed: Φ is not holomorphic as written")
    if pu != 2 * U or qv != 2 * U or pv != -2 * V or qu != 2 * V:
        fail("DΦ entries")

    P, Q = radial_cubic()
    Yu, Yv, det_r, Du, Dv = adj_pullback(p, q, P, Q)
    if Du != 0 or Dv != 0:
        fail("radial adj identity failed")
    deg_r = max(total_deg(Yu, (U, V)), total_deg(Yv, (U, V)))
    bound_one = 3 * 2 + (2 - 1)
    if deg_r != 7 or bound_one != 7:
        fail(f"radial one-step deg {deg_r} bound {bound_one}")

    P1, Q1 = linear_center()
    Yu1, Yv1, _, Du1, Dv1 = adj_pullback(p, q, P1, Q1)
    if Du1 != 0 or Dv1 != 0:
        fail("linear adj identity failed")
    deg_1 = max(total_deg(Yu1, (U, V)), total_deg(Yv1, (U, V)))
    bound_lin = 1 * 2 + (2 - 1)
    if deg_1 != 3 or bound_lin != 3:
        fail(f"linear one-step deg {deg_1}")
    if sp.expand(Yu1 - 2 * V * (U**2 + V**2)) != 0:
        fail("linear Yu != 2v(u^2+v^2)")
    if sp.expand(Yv1 + 2 * U * (U**2 + V**2)) != 0:
        fail("linear Yv != -2u(u^2+v^2)")

    # Two-step: pull the degree-7 field back by the same Φ.
    Y2u, Y2v, _, D2u, D2v = adj_pullback(
        p, q, Yu.subs({U: X, V: Ys}), Yv.subs({U: X, V: Ys})
    )
    if D2u != 0 or D2v != 0:
        fail("two-step adj identity failed")
    deg_2 = max(total_deg(Y2u, (U, V)), total_deg(Y2v, (U, V)))
    bound_two = 7 * 2 + (2 - 1)
    if deg_2 != 15 or bound_two != 15:
        fail(f"two-step deg {deg_2} bound {bound_two}")

    t2u, t2v = chebyshev_T2()
    Ytu, Ytv, _, Dtu, Dtv = adj_pullback(t2u, t2v, P, Q)
    if Dtu != 0 or Dtv != 0:
        fail("T2 adj identity failed")
    deg_t2 = max(total_deg(Ytu, (U, V)), total_deg(Ytv, (U, V)))
    if deg_t2 != 7:
        fail(f"T2 one-step deg {deg_t2} != 7")

    return {
        "paper": "arXiv:2604.12883v1 Remark 4 / Theorem 2 / §6",
        "Phi": "u^2-v^2, 2uv",
        "det": "4(u^2+v^2)",
        "cauchy_riemann": True,
        "identity": "DPhi · Y = (det DPhi) (X o Phi)",
        "radial": {
            "rho2": [1, 4],
            "identity_ok": True,
            "deg_Y": deg_r,
            "bound": bound_one,
            "exact": True,
            "Yu": dump_monomials("Yu", Yu),
            "Yv": dump_monomials("Yv", Yv),
            "Yu_monomials": monomials_qq(Yu),
            "Yv_monomials": monomials_qq(Yv),
        },
        "linear": {
            "P": "y",
            "Q": "-x",
            "identity_ok": True,
            "deg_Y": deg_1,
            "bound": bound_lin,
            "Yu_closed": "2v(u^2+v^2)",
            "Yv_closed": "-2u(u^2+v^2)",
            "Yu_monomials": monomials_qq(Yu1),
            "Yv_monomials": monomials_qq(Yv1),
        },
        "two_step_radial": {
            "deg_Y": deg_2,
            "bound": bound_two,
            "identity_ok": True,
            "N_formula": "(n+1) 2^k - 1",
        },
        "chebyshev_T2_one_step": {
            "deg_Y": deg_t2,
            "bound": 7,
            "identity_ok": True,
        },
        "Yu": Yu,
        "Yv": Yv,
        "Yu1": Yu1,
        "Yv1": Yv1,
    }


def real_regular_preimages(p, q, a, b, gens=(U, V)):
    """Exact algebraic real regular preimages of (a, b)."""
    sols = sp.solve([sp.expand(p - a), sp.expand(q - b)], list(gens), dict=True)
    det = sp.expand(sp.diff(p, gens[0]) * sp.diff(q, gens[1]) - sp.diff(p, gens[1]) * sp.diff(q, gens[0]))
    regular = []
    complex_all = 0
    for s in sols:
        uu, vv = sp.simplify(s[gens[0]]), sp.simplify(s[gens[1]])
        complex_all += 1
        if not (uu.is_real and vv.is_real):
            continue
        d = sp.simplify(det.subs({gens[0]: uu, gens[1]: vv}))
        if d == 0:
            continue
        regular.append((uu, vv, d))
    return regular, complex_all


def count_square_half_zero() -> int:
    """Φ(u,v)=(1/2,0): 2uv=0 and u²−v²=1/2. Two real regular points."""
    # 2uv=0 ⇒ u=0 or v=0.
    # u=0 ⇒ −v²=1/2, no real. v=0 ⇒ u²=1/2, two reals. det=4u²=2≠0.
    # v = 0, u^2 = 1/2 > 0: two reals. u = 0: -v^2 = 1/2, none.
    return 2


def count_square_quarter_quarter() -> int:
    """Φ(u,v)=(1/4,1/4): one positive t=u² from 64t²−16t−1=0, two reals."""
    t = sp.symbols("t")
    poly = sp.Poly(64 * t**2 - 16 * t - 1, t, domain=sp.QQ)
    disc = 16**2 + 4 * 64 * 1
    if disc != 512:
        fail(f"discriminant {disc}")
    roots = sp.solve(poly.as_expr(), t)
    pos = [r for r in roots if r.is_real and r > 0]
    neg = [r for r in roots if r.is_real and r < 0]
    if len(pos) != 1 or len(neg) != 1:
        fail(f"u^2 roots pos={pos} neg={neg}")
    # product of roots = −1/64 < 0, so opposite signs: already checked.
    # v = 1/(8u) for each real u = ±sqrt(t+). Two points, origin excluded.
    return 2


def count_phi2_half_zero() -> int:
    """Φ²(u,v)=(1/2,0): 4uv(u²−v²)=0 and Re(z^4)=1/2. Four real regular."""
    # q2 = 4uv(u²−v²)=0 ⇒ u=0 or v=0 or u²=v².
    # u=0: v^4=1/2, two reals. v=0: u^4=1/2, two reals.
    # u²=v² and uv≠0: −4u^4=1/2, no real.
    return 4


def count_chebyshev_t2(a: Fraction, b: Fraction) -> int:
    """T2(t)=2t^2-1. Each of a,b in (-1,1) has two real preimages; 4 sheets."""
    if abs(a) >= 1 or abs(b) >= 1:
        fail("T2 target not in (-1,1)^2")
    rhs_u = (a + 1) / 2
    rhs_v = (b + 1) / 2
    if not (0 < rhs_u < 1 and 0 < rhs_v < 1):
        fail("T2 preimages not in (-1,1)")
    # T2' = 4t vanishes only at 0; t^2 = (c+1)/2 != 0.
    return 4


def polar_count(k: int, target=(0.5, 0.0)) -> int:
    """z ↦ z^{2^k} preimages of a nonzero point: the 2^k roots, all regular."""
    a, b = target
    w_mod = math.hypot(a, b)
    if w_mod == 0:
        fail("polar target is 0")
    w_arg = math.atan2(b, a)
    n = 1 << k
    r = w_mod ** (1.0 / n)
    pts = []
    for j in range(n):
        th = (w_arg + 2 * math.pi * j) / n
        pts.append((r * math.cos(th), r * math.sin(th)))
    # Iterate Φ, k times, and land on the target.
    for u0, v0 in pts:
        u, v = u0, v0
        for _ in range(k):
            u, v = u * u - v * v, 2 * u * v
        if abs(u - a) + abs(v - b) > 1e-9:
            fail(f"polar iterate k={k} missed target from {(u0, v0)}")
        if u0 * u0 + v0 * v0 < 1e-18:
            fail("polar preimage at origin")
    # Distinct.
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1 :]:
            if abs(x1 - x2) + abs(y1 - y2) < 1e-9:
                fail(f"polar k={k} collision")
    return len(pts)


def check_preimages() -> dict[str, Any]:
    p, q = phi_components()
    n_half = count_square_half_zero()
    n_qq = count_square_quarter_quarter()
    n_phi2 = count_phi2_half_zero()
    n_t2 = count_chebyshev_t2(Fraction(1, 2), Fraction(1, 2))

    half_pts, half_c = real_regular_preimages(p, q, sp.Rational(1, 2), 0)
    qq_pts, qq_c = real_regular_preimages(p, q, sp.Rational(1, 4), sp.Rational(1, 4))
    if len(half_pts) != 2 or n_half != 2:
        fail(f"(1/2,0) real regular {len(half_pts)}")
    if len(qq_pts) != 2 or n_qq != 2:
        fail(f"(1/4,1/4) real regular {len(qq_pts)}")
    if half_c != 4 or qq_c != 4:
        fail("complex Bézout count for degree 2 is not 4")

    p0, q0 = p, q
    p2 = sp.expand(p0.xreplace({U: p0, V: q0}))
    q2 = sp.expand(q0.xreplace({U: p0, V: q0}))
    expect_p2 = sp.expand(U**4 - 6 * U**2 * V**2 + V**4)
    expect_q2 = sp.expand(4 * U**3 * V - 4 * U * V**3)
    if p2 != expect_p2 or q2 != expect_q2:
        fail(f"Phi^2 components {p2}, {q2}")
    phi2_pts, phi2_c = real_regular_preimages(p2, q2, sp.Rational(1, 2), 0)
    if len(phi2_pts) != 4 or n_phi2 != 4:
        fail(f"Phi^2 (1/2,0) real regular {len(phi2_pts)}")
    # Complexified (u,v) in C^2: Bézout allows 16. The holomorphic
    # count z^4 = 1/2 in C ≅ R^2 is 4, and those 4 are the real ones.
    if phi2_c > 16:
        fail(f"Phi^2 complex count {phi2_c} above Bézout 16")

    t2u, t2v = chebyshev_T2()
    t2_pts, t2_c = real_regular_preimages(t2u, t2v, sp.Rational(1, 2), sp.Rational(1, 2))
    if len(t2_pts) != 4 or n_t2 != 4:
        fail(f"T2 (1/2,1/2) real regular {len(t2_pts)}")

    polar = []
    for k in range(1, 7):
        c = polar_count(k)
        if c != 1 << k:
            fail(f"polar k={k} count {c}")
        polar.append({"k": k, "count": c, "expected": 1 << k})

    return {
        "square_half_0": {
            "target": [1, 2, 0, 1],
            "real_regular": 2,
            "complex_affine": 4,
            "bezout_m2": 4,
            "attains_m2": False,
            "points": [
                {"u": str(uu), "v": str(vv), "det": str(d)} for uu, vv, d in half_pts
            ],
        },
        "square_quarter_quarter": {
            "target": [1, 4, 1, 4],
            "real_regular": 2,
            "complex_affine": 4,
            "bezout_m2": 4,
            "attains_m2": False,
            "u2_quadratic": "64t^2 - 16t - 1",
            "disc": 512,
        },
        "phi2_half_0": {
            "target": [1, 2, 0, 1],
            "real_regular": 4,
            "complexified_uv_at_most": 16,
            "holomorphic_in_C": 4,
            "note": "z^4 = 1/2 has 4 points in R^2 ≅ C, not 16",
        },
        "chebyshev_T2_half_half": {
            "target": [1, 2, 1, 2],
            "real_regular": 4,
            "attains_m2": True,
            "note": "T2 x T2 is 4-to-1 on (-1,1)^2; components independent",
        },
        "polar_z_to_z_2k_of_half": polar,
        "honesty": {
            "real_plane_z_squared_is_2_to_1": True,
            "separable_T2_is_4_to_1_on_minus1_1_square": True,
            "CR_couples_the_components": True,
        },
    }


def reduced_ratio(num: int, den: int) -> tuple[int, int]:
    g = math.gcd(num, den)
    return num // g, den // g


def check_arithmetic(n: int = 3) -> dict[str, Any]:
    rows = []
    for k in range(1, 7):
        N = (n + 1) * (1 << k) - 1
        bezout = 1 << (2 * k)  # 4^k
        complex_sheets = 1 << k  # 2^k
        cheb_m = 1 << k
        cheb_sheets = cheb_m * cheb_m
        if N != (n + 1) * cheb_m - 1:
            fail("N mismatch vs one-step Chebyshev of degree 2^k")
        if complex_sheets * (n + 1) != N + 1:
            fail("2^k != (N+1)/(n+1)")
        if bezout != cheb_sheets:
            fail("4^k != m^2")
        b_n, b_d = reduced_ratio(bezout, N * N)
        c_n, c_d = reduced_ratio(complex_sheets, N * N)
        rows.append(
            {
                "k": k,
                "N": N,
                "sheet_ceiling_bezout": bezout,
                "actual_complex": complex_sheets,
                "chebyshev_m": cheb_m,
                "chebyshev_sheets": cheb_sheets,
                "bezout_over_N2": [b_n, b_d],
                "complex_over_N2": [c_n, c_d],
                "complex_eq_(N+1)/(n+1)": True,
            }
        )
    return {
        "n": n,
        "N_formula": "(n+1) 2^k - 1",
        "rows": rows,
        "conclusion": {
            "beats_theorem2": False,
            "attains_m2_per_step": False,
            "actual_complex_growth": "linear",
            "complex_sheets_formula": "(N+1)/(n+1)",
            "bezout_ceiling_growth": "quadratic",
            "answers_remark4": "negative_for_complex_squaring",
            "do_not_claim_252_1080_1380_2012": True,
        },
    }


def dump_lines(ident: dict[str, Any], pre: dict[str, Any], arith: dict[str, Any]) -> list[str]:
    lines = [
        "det 4(u^2+v^2)",
        "cr p_u=q_v=2u p_v=-q_u=-2v",
        "identity_radial 1",
        "identity_linear 1",
        f"deg_radial {ident['radial']['deg_Y']} bound {ident['radial']['bound']}",
        f"deg_linear {ident['linear']['deg_Y']} bound {ident['linear']['bound']}",
        f"deg_two_step_radial {ident['two_step_radial']['deg_Y']} bound {ident['two_step_radial']['bound']}",
        f"deg_chebyshev_T2 {ident['chebyshev_T2_one_step']['deg_Y']} bound 7",
    ]
    lines.extend(dump_monomials("Yu", ident["Yu"]))
    lines.extend(dump_monomials("Yv", ident["Yv"]))
    lines.extend(dump_monomials("Yu_linear", ident["Yu1"]))
    lines.extend(dump_monomials("Yv_linear", ident["Yv1"]))
    lines.append("preimages_square 1/2 0 2")
    lines.append("preimages_square 1/4 1/4 2")
    lines.append("preimages_square2 1/2 0 4")
    lines.append("preimages_chebyshev_T2 1/2 1/2 4")
    for row in pre["polar_z_to_z_2k_of_half"]:
        lines.append(f"polar_count {row['k']} {row['count']}")
    for row in arith["rows"]:
        lines.append(
            f"k {row['k']} N {row['N']} bezout {row['sheet_ceiling_bezout']} "
            f"complex {row['actual_complex']} chebyshev {row['chebyshev_sheets']}"
        )
        bn, bd = row["bezout_over_N2"]
        cn, cd = row["complex_over_N2"]
        lines.append(f"ratio_bezout {row['k']} {bn}/{bd}")
        lines.append(f"ratio_complex {row['k']} {cn}/{cd}")
    lines.append("complex_sheets_eq_(N+1)/(n+1) 1")
    lines.append("beats_theorem2 0")
    lines.append("attains_m2_per_step 0")
    lines.append("growth_complex linear")
    lines.append("growth_bezout_ceiling quadratic")
    lines.append("do_not_claim_252_1080_1380_2012 1")
    return lines


def write_json(name: str, payload: dict[str, Any]) -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    path = CERTS / name
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", type=Path, default=None)
    args = ap.parse_args()

    ident = check_identity_and_degree()
    pre = check_preimages()
    arith = check_arithmetic(3)

    ident_out = {k: v for k, v in ident.items() if k not in {"Yu", "Yv", "Yu1", "Yv1"}}
    # monomials already stored as lists of dicts; drop the dump-string copies
    ident_out["radial"] = {
        k: v for k, v in ident["radial"].items() if k not in {"Yu", "Yv"}
    }

    write_json("identity.json", ident_out)
    write_json(
        "degree.json",
        {
            "one_step_formula": "deg Y <= n m + (m-1) = (n+1)m - 1",
            "n": 3,
            "m": 2,
            "radial_deg": ident["radial"]["deg_Y"],
            "radial_bound": 7,
            "linear_deg": ident["linear"]["deg_Y"],
            "linear_bound": 3,
            "two_step_deg": ident["two_step_radial"]["deg_Y"],
            "two_step_bound": 15,
            "chebyshev_T2_deg": ident["chebyshev_T2_one_step"]["deg_Y"],
            "k_step_bound": "(n+1) 2^k - 1",
        },
    )
    write_json("preimages.json", pre)
    write_json("arithmetic.json", arith)

    core = {
        "det": "4(u^2+v^2)",
        "identity_radial": True,
        "identity_linear": True,
        "deg_radial": 7,
        "deg_linear": 3,
        "deg_two_step_radial": 15,
        "preimages_half_0": 2,
        "preimages_quarter_quarter": 2,
        "preimages_phi2_half_0": 4,
        "preimages_chebyshev_T2": 4,
        "beats_theorem2": False,
        "attains_m2_per_step": False,
        "growth_complex": "linear",
        "Yu_monomials": ident["radial"]["Yu_monomials"],
        "Yv_monomials": ident["radial"]["Yv_monomials"],
        "rows": [
            {
                "k": r["k"],
                "N": r["N"],
                "bezout": r["sheet_ceiling_bezout"],
                "complex": r["actual_complex"],
                "chebyshev": r["chebyshev_sheets"],
            }
            for r in arith["rows"]
        ],
    }
    write_json("core.json", core)

    lines = dump_lines(ident, pre, arith)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text)
    print(text, end="")
    print("verify.py: ok")
    print(f"  deg radial Y = {ident['radial']['deg_Y']}")
    print(f"  sheets Φ = 2, T2 = 4, Φ^2 = 4")
    print("  beats Theorem 2 = 0")


if __name__ == "__main__":
    main()
