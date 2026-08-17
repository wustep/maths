"""Quantitative version of Liu Lemma 8.

Compute the CIID/iid ratio r* at the Yu–Cambie optimizer μ*, then
evaluate how far one can push the mean past c* on the 2-atomic family
{b, 1} and the complement family {0, x} before the mixed ratio drops
to 1.

This is *not* by itself a proof for every measure.  It produces the
explicit numbers that Lemma 8's compactness argument is hiding, and
records whether a tiny explicit c' > c* is visible on the known
extremal rays.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from mpmath import mp, mpf, log, findroot, nstr

from entropy import a_example4, h, h_or_example4, h_or_example5, h_or_indep, h_or_maxent

mp.dps = 60
LN2 = log(2)


def hm(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return -(p * log(p) + (1 - p) * log(1 - p)) / LN2


def cambie():
    def eq(b):
        return hm(b) * (2 - hm(b)) - hm((1 - b) ** 2)

    b = findroot(eq, mpf("0.33"))
    a = 1 - hm(b) / hm((1 - b) ** 2)
    c = a + (1 - a) * b
    return a, b, c


def rstar_example4(a, b):
    """r* = h(Π_{b,b}^{ex4}(0,0)) / h(b̄²)  at the independent C3 coupling."""
    # Π(b,b)(0,0) = b̄² + a(b)² (b̄ - b̄²)
    t = float(b)
    ab = a_example4(t)
    bbar = 1 - t
    pi = bbar * bbar + ab * ab * (bbar - bbar * bbar)
    return h(pi) / h(bbar * bbar), pi, ab


def two_point_one(a, b, w_iid, w_max, w_ex4, w_ex5):
    """μ = a δ_1 + (1-a) δ_b.  Independent C3 for CIID; worst maxent = P(1,1)=0."""
    eh = (1 - a) * h(b)
    eiid = (1 - a) ** 2 * h_or_indep(b, b)  # rest involve 1, h(OR with 1)=0
    # maxent worst: P(1,1)=0, P(1,b)=a, P(b,b)=1-2a
    emax = (1 - 2 * a) * h_or_maxent(b, b)  # h(min(2b,1/2))
    e4 = (1 - a) ** 2 * h_or_example4(b, b)  # independent C3
    e5 = (1 - a) ** 2 * h_or_example5(b, b)
    num = w_iid * eiid + w_max * emax + w_ex4 * e4 + w_ex5 * e5
    mean = a + (1 - a) * b
    return mean, num / eh if eh > 0 else None, eh


def two_point_zero(p, x, w_iid, w_max, w_ex4, w_ex5):
    """Complement form: P(X=x)=p, P(X=0)=1-p, i.e. S ∈ {1-x, 1}."""
    # S = 1-X
    s_hi = 1.0 - x
    # P(S = s_hi) = p, P(S=1) = 1-p
    return two_point_one(1.0 - p, s_hi, w_iid, w_max, w_ex4, w_ex5)


def scan_ray_b1(w, b_lo=0.25, b_hi=0.40, n=400):
    """Along the Sawin ray: support {b,1}, mean-matching a = (c-b)/(1-b) with c free.

    For each b, take the a that makes iid ratio = 1 (the Gilmer-type
    2-point), and also a sweep of a so mean runs through [b, 0.42].
    """
    rows = []
    for i in range(n + 1):
        b = b_lo + (b_hi - b_lo) * i / n
        for a in [k / 80 for k in range(0, 41)]:
            if a >= 0.5:
                continue
            mean, r, eh = two_point_one(a, b, *w)
            if r is None:
                continue
            rows.append({"b": b, "a": a, "mean": mean, "ratio": r})
    return rows


def scan_ray_0x(w, n=400):
    rows = []
    for i in range(n + 1):
        x = 0.55 + 0.20 * i / n
        for p in [k / 80 for k in range(20, 81)]:
            mean, r, eh = two_point_zero(p, x, *w)
            if r is None:
                continue
            rows.append({"x": x, "p": p, "mean": mean, "ratio": r})
    return rows


def frontier(rows, target=1.0):
    """Largest mean at which ratio ≤ target, and smallest ratio for mean ≤ c*+eps."""
    bad = [r for r in rows if r["ratio"] <= target]
    if not bad:
        return None
    return max(bad, key=lambda r: r["mean"])


def min_ratio_below(rows, c):
    sub = [r for r in rows if r["mean"] <= c]
    if not sub:
        return None
    return min(sub, key=lambda r: r["ratio"])


def main():
    a_star, b_star, c_star = cambie()
    r4, pi4, ab = rstar_example4(float(a_star), float(b_star))
    # example 5 at the same point
    pi5 = (1 - float(b_star)) ** 2 + (
        (1 - float(b_star)) * float(b_star)
    ) ** 2  # s̄t̄ + f(s̄)f(t̄), f(u)=u(1-u), u=s̄
    # wait: f(s̄)= s̄ * s, Π= s̄² + (s̄ s)²
    s = float(b_star)
    sb = 1 - s
    pi5 = sb * sb + (sb * s) ** 2
    r5 = h(pi5) / h(sb * sb)

    report = {
        "a_star": float(a_star),
        "b_star": float(b_star),
        "c_star": float(c_star),
        "rstar_ex4": r4,
        "pi_ex4": pi4,
        "a_of_b": ab,
        "rstar_ex5": r5,
        "pi_ex5": pi5,
        "gap_ex4": r4 - 1.0,
        "gap_ex5": r5 - 1.0,
    }

    # Liu's published mix on the two rays
    mixes = {
        "sawin": (1 - 0.03560698, 0.03560698, 0.0, 0.0),
        "liu_ex5": (0.89994744, 0.0, 0.0, 0.10005256),
        "lemma8_tiny_ex4": (0.96439302 * 0.99, 0.03560698 * 0.99, 0.01, 0.0),
        "lemma8_ex4_03": (0.96439302 * 0.97, 0.03560698 * 0.97, 0.03, 0.0),
        "ex4_only_mix": (0.90, 0.0, 0.10, 0.0),
        "triple": (0.87, 0.03, 0.10, 0.0),
    }
    report["rays"] = {}
    for name, w in mixes.items():
        ray1 = scan_ray_b1(w)
        ray0 = scan_ray_0x(w)
        f1 = frontier(ray1)
        f0 = frontier(ray0)
        m1 = min_ratio_below(ray1, float(c_star) + 1e-9)
        m0 = min_ratio_below(ray0, float(c_star) + 1e-9)
        m1b = min_ratio_below(ray1, 0.382709087918735)
        m0b = min_ratio_below(ray0, 0.382709087918735)
        report["rays"][name] = {
            "weights": w,
            "frontier_b1": f1,
            "frontier_0x": f0,
            "min_below_cstar_b1": m1,
            "min_below_cstar_0x": m0,
            "min_below_liu_b1": m1b,
            "min_below_liu_0x": m0b,
        }
        print(
            name,
            "front_b1",
            None if f1 is None else (f1["mean"], f1["ratio"]),
            "front_0x",
            None if f0 is None else (f0["mean"], f0["ratio"]),
        )

    out = Path(__file__).resolve().parent / "lemma8_quant.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("r*_ex4", r4, "r*_ex5", r5)
    print("wrote", out)


if __name__ == "__main__":
    main()
