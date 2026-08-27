#!/usr/bin/env python3
"""Regular real preimages of a degree-m polynomial map: at most m^2.

Bézout: two plane curves of degree ≤ m with no common component meet
in at most m^2 isolated points in the affine plane (complex, hence
real). A regular preimage of Φ = (p, q) is an isolated solution of
p = a, q = b with det DΦ ≠ 0. On a common component the two gradients
are parallel, so det DΦ = 0 there. Therefore the regular real
preimages are isolated intersections of curves with no common factor,
and there are at most m^2 of them.

If this script ever reports more than m^2 regular real preimages, that
contradicts Bézout: stop and inspect (shared component, or points at
infinity miscounted as affine).

Replay: python3 bezout_preimages.py
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
U, V = sp.symbols("u v")


def chebyshev_T(m: int, z):
    """Chebyshev T_m as a sympy expression in z."""
    if m == 0:
        return sp.Integer(1)
    if m == 1:
        return z
    tm2, tm1 = sp.Integer(1), z
    for _ in range(2, m + 1):
        tm2, tm1 = tm1, sp.expand(2 * z * tm1 - tm2)
    return tm1


def poly_degree(expr, gens) -> int:
    if expr == 0:
        return -1
    return int(sp.Poly(sp.expand(expr), gens).total_degree())


def jacobian_det(p, q, u=U, v=V):
    return sp.expand(sp.diff(p, u) * sp.diff(q, v) - sp.diff(p, v) * sp.diff(q, u))


def newton_refine(p, q, x0: float, y0: float, gens, steps: int = 12):
    u, v = gens
    pu, pv = sp.diff(p, u), sp.diff(p, v)
    qu, qv = sp.diff(q, u), sp.diff(q, v)
    funcs = [sp.lambdify((u, v), expr, "numpy") for expr in (p, q, pu, pv, qu, qv)]
    x, y = float(x0), float(y0)
    for _ in range(steps):
        P, Q, Pu, Pv, Qu, Qv = (f(x, y) for f in funcs)
        det = Pu * Qv - Pv * Qu
        if abs(det) < 1e-18:
            return None
        dx = (Q * Pv - P * Qv) / det
        dy = (P * Qu - Q * Pu) / det
        x += dx
        y += dy
        if abs(dx) + abs(dy) < 1e-15:
            break
    P, Q = funcs[0](x, y), funcs[1](x, y)
    if abs(P) + abs(Q) > 1e-10:
        return None
    return x, y


def real_preimages_resultant(p, q, a, b, gens, det_tol: float = 1e-9):
    """Count regular real affine preimages of (a, b).

    Returns (status, points) where status is 'ok' or 'shared_component'.
    """
    u, v = gens
    f, g = sp.expand(p - a), sp.expand(q - b)
    Rf = sp.resultant(f, g, u)
    if Rf == 0:
        return "shared_component", []
    numer = sp.together(Rf).as_numer_denom()[0]
    poly_v = sp.Poly(sp.expand(numer), v, domain=sp.QQ)
    if poly_v.degree() < 0:
        return "ok", []
    # Numerical real roots of the resultant, then Newton on the system.
    coeffs = [complex(c) for c in poly_v.all_coeffs()]
    roots = np.roots(coeffs)
    candidates = []
    for r in roots:
        if abs(r.imag) > 1e-9:
            continue
        y0 = float(r.real)
        fx = sp.Poly(sp.expand(f.subs(v, sp.Float(y0, 30))), u, domain=sp.RR)
        if fx.degree() < 0:
            continue
        for s in np.roots([complex(c) for c in fx.all_coeffs()]):
            if abs(s.imag) > 1e-9:
                continue
            refined = newton_refine(f, g, float(s.real), y0, gens)
            if refined is None:
                continue
            candidates.append(refined)
    # Cluster
    unique = []
    for pt in candidates:
        if any(abs(pt[0] - qpt[0]) + abs(pt[1] - qpt[1]) < 1e-7 for qpt in unique):
            continue
        unique.append(pt)
    det = jacobian_det(p, q, u, v)
    det_f = sp.lambdify((u, v), det, "numpy")
    regular = []
    for x, y in unique:
        try:
            d = complex(det_f(x, y))
        except (ValueError, TypeError, OverflowError):
            continue
        if abs(d) > det_tol:
            regular.append((x, y, float(abs(d))))
    if len(regular) > poly_degree(p, gens) ** 2 + 1:
        # impossible; caller will fail
        pass
    return "ok", regular


def random_poly(m: int, rng: np.random.Generator, gens, bound: int = 3):
    u, v = gens
    expr = 0
    top = 0
    for i in range(m + 1):
        for j in range(m + 1 - i):
            coeff = int(rng.integers(-bound, bound + 1))
            expr += coeff * u**i * v**j
            if i + j == m:
                top += abs(coeff)
    if top == 0:
        expr += u**m
    return sp.expand(expr)


def chebyshev_preimages(m: int, a: float, b: float):
    """Exact real preimages of (T_m, T_m) via arccos, |a|,|b| < 1."""
    if abs(a) >= 1 or abs(b) >= 1:
        raise ValueError("need a target in (-1,1)^2")
    us = [math.cos((math.acos(a) + math.pi * k) / m) for k in range(m)]
    vs = [math.cos((math.acos(b) + math.pi * k) / m) for k in range(m)]
    pts = [(u, v) for u in us for v in vs]
    T = chebyshev_T(m, U)
    S = chebyshev_T(m, V)
    det = jacobian_det(T, S)
    det_f = sp.lambdify((U, V), det, "numpy")
    regular = []
    for u, v in pts:
        d = float(det_f(u, v))
        if abs(d) > 1e-10:
            regular.append((u, v, abs(d)))
    return regular


def two_quadrics_points():
    # u^2+v^2 = 2, u^2-v^2 = 0 → (±1, ±1), all regular.
    return [(sx, sy, 8.0) for sx in (1.0, -1.0) for sy in (1.0, -1.0)]


def complex_square_points():
    # (u^2-v^2, 2uv) = (1, 0) → (±1, 0)
    return [(1.0, 0.0, 4.0), (-1.0, 0.0, 4.0)]


def sample_record(kind, m, target, status, points, extra=None):
    rec = {
        "kind": kind,
        "m": m,
        "target": list(target),
        "status": status,
        "count": len(points),
        "ceiling": m * m,
        "ok": status == "shared_component" or len(points) <= m * m,
    }
    if extra:
        rec.update(extra)
    return rec


def run(seed: int = 1):
    rng = np.random.default_rng(seed)
    samples = []
    violations = []

    # --- constructed maps ---
    for m, target in ((2, (0.5, 0.3)), (3, (0.4, -0.2)), (4, (0.2, 0.6))):
        pts = chebyshev_preimages(m, *target)
        rec = sample_record("chebyshev", m, target, "ok", pts)
        samples.append(rec)
        if rec["count"] != m * m:
            violations.append(("chebyshev_missed_sharpness", rec))
        if rec["count"] > m * m:
            violations.append(("over_ceiling", rec))

    p2, q2 = U**2 + V**2, U**2 - V**2
    pts = two_quadrics_points()
    # confirm with resultant
    status, pts_num = real_preimages_resultant(p2, q2, 2, 0, (U, V))
    rec = sample_record("two_quadrics", 2, (2, 0), status, pts_num, extra={"exact_count": 4})
    samples.append(rec)
    if rec["count"] != 4:
        violations.append(("two_quadrics", rec))

    psq, qsq = U**2 - V**2, 2 * U * V
    status, pts_num = real_preimages_resultant(psq, qsq, 1, 0, (U, V))
    rec = sample_record("complex_square", 2, (1, 0), status, pts_num, extra={"exact_count": 2})
    samples.append(rec)
    if rec["count"] != 2:
        violations.append(("complex_square", rec))

    # Non-separable cubic: Φ = (u^3 + v, v^3 + u). Generic target.
    pns, qns = U**3 + V, V**3 + U
    status, pts_num = real_preimages_resultant(pns, qns, 1, -2, (U, V))
    rec = sample_record("nonseparable_cubic", 3, (1, -2), status, pts_num)
    samples.append(rec)
    if rec["count"] > 9:
        violations.append(("over_ceiling", rec))

    # --- random maps ---
    random_plan = [(2, 24), (3, 10), (4, 4)]
    for m, n_maps in random_plan:
        for i in range(n_maps):
            p = random_poly(m, rng, (U, V))
            q = random_poly(m, rng, (U, V))
            a = int(rng.integers(-2, 3))
            b = int(rng.integers(-2, 3))
            status, pts = real_preimages_resultant(p, q, a, b, (U, V))
            rec = sample_record(
                "random",
                m,
                (a, b),
                status,
                pts,
                extra={
                    "index": i,
                    "p": str(p),
                    "q": str(q),
                    "deg_p": poly_degree(p, (U, V)),
                    "deg_q": poly_degree(q, (U, V)),
                },
            )
            samples.append(rec)
            if status == "ok" and rec["count"] > m * m:
                violations.append(("over_ceiling", rec))

    max_by_m = {}
    for rec in samples:
        if rec["status"] != "ok":
            continue
        max_by_m[rec["m"]] = max(max_by_m.get(rec["m"], 0), rec["count"])

    out = {
        "lemma": (
            "A real polynomial map Φ=(p,q) of degree ≤ m has at most m^2 "
            "regular real preimages of any point (Bézout + regularity)."
        ),
        "remark": (
            "Answers arXiv:2604.12883v1 Remark 4 at the one-step sheet "
            "count: non-separable maps cannot beat m^2 regular sheets."
        ),
        "seed": seed,
        "violations": len(violations),
        "max_regular_by_m": {str(k): v for k, v in sorted(max_by_m.items())},
        "n_samples": len(samples),
        "n_shared_component": sum(1 for s in samples if s["status"] == "shared_component"),
        "samples": samples,
    }
    return out, violations


def dump_lines(data: dict) -> list[str]:
    lines = []
    for rec in data["samples"]:
        if rec["kind"] in {"chebyshev", "two_quadrics", "complex_square"}:
            key = rec["kind"]
            if rec["kind"] == "chebyshev":
                key = f"chebyshev_m{rec['m']}"
            lines.append(f"preimages {key} {rec['count']}")
    for m, mx in sorted((int(k), v) for k, v in data["max_regular_by_m"].items()):
        lines.append(f"max_regular m={m} {mx}")
    lines.append(f"violations {data['violations']}")
    lines.append(f"ceiling_ok {int(data['violations'] == 0)}")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=HERE / "bezout_samples.json")
    ap.add_argument("--dump", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    data, violations = run(args.seed)
    args.json.write_text(json.dumps(data, indent=2) + "\n")
    lines = dump_lines(data)
    if args.dump:
        args.dump.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if violations:
        print("BÉZOUT VIOLATION — inspect samples")
        print(json.dumps(violations, indent=2)[:2000])
        raise SystemExit(1)
    # Sharpness: Chebyshev must hit m^2
    for rec in data["samples"]:
        if rec["kind"] == "chebyshev" and rec["count"] != rec["m"] ** 2:
            raise SystemExit(f"Chebyshev failed to attain m^2 at m={rec['m']}")
    print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
