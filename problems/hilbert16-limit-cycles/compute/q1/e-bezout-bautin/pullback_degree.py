#!/usr/bin/env python3
"""adj(DΦ) pullback and the degree bound deg Y ≤ n m + (m−1).

For Φ = (p, q) of degree ≤ m and a planar field X = (P, Q) of
degree ≤ n, the polynomial pullback of arXiv:2604.12883 Remark 4 is

    Y := adj(DΦ) (X ∘ Φ),

i.e.

    u̇ = q_v P(Φ) − p_v Q(Φ),
    v̇ = −q_u P(Φ) + p_u Q(Φ),

so that DΦ · Y = (det DΦ) (X ∘ Φ). The 2×2 cofactors have degree
≤ m−1 and X∘Φ has degree ≤ n m, hence deg Y ≤ n m + (m−1).

This is the same degree budget as the separable Chebyshev
construction. Combined with the Bézout sheet ceiling m^2, the
factor m^2 is optimal among all polynomial maps of degree m, not
only the separable ones.

Replay: python3 pullback_degree.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
U, V, X, Ys = sp.symbols("u v x y")


def chebyshev_T(m: int, z):
    if m == 0:
        return sp.Integer(1)
    if m == 1:
        return z
    tm2, tm1 = sp.Integer(1), z
    for _ in range(2, m + 1):
        tm2, tm1 = tm1, sp.expand(2 * z * tm1 - tm2)
    return tm1


def total_deg(expr, gens) -> int:
    expr = sp.expand(expr)
    if expr == 0:
        return -1
    return int(sp.Poly(expr, gens).total_degree())


def adj_pullback(p, q, P, Q):
    """Return (Yu, Yv, det, identity_residual)."""
    pu, pv = sp.diff(p, U), sp.diff(p, V)
    qu, qv = sp.diff(q, U), sp.diff(q, V)
    det = sp.expand(pu * qv - pv * qu)
    Pc = sp.expand(P.subs({X: p, Ys: q}))
    Qc = sp.expand(Q.subs({X: p, Ys: q}))
    Yu = sp.expand(qv * Pc - pv * Qc)
    Yv = sp.expand(-qu * Pc + pu * Qc)
    # DΦ · Y − det (X ∘ Φ) must be (0,0)
    Du = sp.expand(pu * Yu + pv * Yv - det * Pc)
    Dv = sp.expand(qu * Yu + qv * Yv - det * Qc)
    return Yu, Yv, det, Du, Dv


def random_poly(deg, rng, gens, bound=2):
    expr = 0
    u, v = gens
    top = 0
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            coeff = int(rng.integers(-bound, bound + 1))
            expr += coeff * u**i * v**j
            if i + j == deg:
                top += abs(coeff)
    if top == 0:
        expr += u**deg
    return sp.expand(expr)


def check_example(name, p, q, P, Q, n, m):
    Yu, Yv, det, Du, Dv = adj_pullback(p, q, P, Q)
    if Du != 0 or Dv != 0:
        raise RuntimeError(f"{name}: pullback identity failed")
    degY = max(total_deg(Yu, (U, V)), total_deg(Yv, (U, V)))
    bound = n * m + (m - 1)
    return {
        "name": name,
        "n": n,
        "m": m,
        "deg_p": total_deg(p, (U, V)),
        "deg_q": total_deg(q, (U, V)),
        "deg_X": max(total_deg(P, (X, Ys)), total_deg(Q, (X, Ys))),
        "deg_Y": degY,
        "bound": bound,
        "identity_ok": True,
        "ok": degY <= bound,
    }


def run(seed: int = 1):
    rng = np.random.default_rng(seed)
    examples = []

    # Exact symbolic families
    for n, m in ((1, 2), (2, 2), (2, 3), (3, 3)):
        Tm_u = chebyshev_T(m, U)
        Tm_v = chebyshev_T(m, V)
        P = X**n + Ys
        Q = Ys**n + X
        examples.append(
            check_example(f"chebyshev_n{n}_m{m}", Tm_u, Tm_v, P, Q, n, m)
        )
        p = U**m + V
        q = V**m + U
        examples.append(
            check_example(f"nonsep_um_plus_v_n{n}_m{m}", p, q, P, Q, n, m)
        )

    # Random maps
    for n, m, k in ((2, 2, 8), (2, 3, 5), (3, 2, 5), (3, 3, 3)):
        for i in range(k):
            p = random_poly(m, rng, (U, V))
            q = random_poly(m, rng, (U, V))
            P = random_poly(n, rng, (X, Ys))
            Q = random_poly(n, rng, (X, Ys))
            rec = check_example(f"random_n{n}_m{m}_{i}", p, q, P, Q, n, m)
            rec["p"] = str(p)
            rec["q"] = str(q)
            examples.append(rec)

    failed = [e for e in examples if not e["ok"]]
    out = {
        "lemma": "deg adj(DΦ) X∘Φ ≤ n m + (m-1) for deg Φ ≤ m, deg X ≤ n",
        "identity": "DΦ · Y = (det DΦ) (X ∘ Φ)",
        "n_examples": len(examples),
        "failures": len(failed),
        "examples": examples,
    }
    return out, failed


def dump_lines(data: dict) -> list[str]:
    lines = []
    for e in data["examples"]:
        if e["name"].startswith("random"):
            continue
        lines.append(f"deg {e['name']} {e['deg_Y']} bound {e['bound']}")
    lines.append(f"pullback_failures {data['failures']}")
    lines.append(f"pullback_ok {int(data['failures'] == 0)}")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=HERE / "pullback_degree.json")
    ap.add_argument("--dump", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    data, failed = run(args.seed)
    args.json.write_text(json.dumps(data, indent=2) + "\n")
    lines = dump_lines(data)
    if args.dump:
        args.dump.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if failed:
        raise SystemExit(f"degree bound failed on {len(failed)} examples")
    print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
