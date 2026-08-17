#!/usr/bin/env python3
"""
Recompute and optimize the BSKK Fourier exponent for 0/1 coefficients.

BSKK Invent. Math. 233 (2023) §3.2 table, N=2:
    s=134, gamma=0.50057, theta=gamma/s=0.003736, P=210=2*3*5*7.

Uniform on {0,1}: |muhat(xi)| = |cos(pi * xi)|.
    S(Q, ell, s) = sum_{k=0}^{Q-1} |cos(pi (k/Q + ell/R))|^s
    alpha(s, gamma; P) = max_{QR=P, Q>1} max_ell Q^{gamma-1} S
Theorem 7: alpha<1 and gamma>=1/2 give admissible theta=gamma/s.

For fixed (P,s),
    gamma_max = min_{Q,ell} 1 - log(S)/log(Q).
"""

from __future__ import annotations

import itertools
import json
import math
import os
import sys

import numpy as np

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]


def divisors_of(n: int) -> list[int]:
    d = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            d.append(i)
            if i * i != n:
                d.append(n // i)
        i += 1
    return sorted(d)


def abs_cos_table(P: int) -> dict:
    """For each Q|P, Q>1, and each ell in 0..R-1, the length-Q array
    |cos(pi (k/Q + ell/R))|, k=0..Q-1."""
    tables = {}
    for Q in divisors_of(P):
        if Q == 1:
            continue
        R = P // Q
        k = np.arange(Q, dtype=np.float64)
        cols = []
        for ell in range(R):
            # k/Q + ell/R
            arg = k / Q + ell / R
            cols.append(np.abs(np.cos(np.pi * arg)))
        tables[Q] = np.stack(cols, axis=0)  # shape (R, Q)
    return tables


def gamma_max_from_tables(tables: dict, s: int) -> tuple[float, dict]:
    best = float("inf")
    bind = None
    for Q, mat in tables.items():
        # mat: (R, Q)
        S = np.sum(np.power(mat, s), axis=1)  # (R,)
        # skip all-zero rows (shouldn't happen)
        pos = S > 0
        if not np.any(pos):
            continue
        gvals = 1.0 - np.log(S[pos]) / math.log(Q)
        j = int(np.argmin(gvals))
        g = float(gvals[j])
        if g < best:
            best = g
            ells = np.nonzero(pos)[0]
            ell = int(ells[j])
            bind = {
                "Q": int(Q),
                "ell": ell,
                "S": float(S[pos][j]),
                "sqrtQ": float(math.sqrt(Q)),
            }
    return best, bind


def alpha_at(tables: dict, s: int, gamma: float) -> float:
    worst = 0.0
    for Q, mat in tables.items():
        S = np.sum(np.power(mat, s), axis=1)
        val = np.max((Q ** (gamma - 1.0)) * S)
        if val > worst:
            worst = float(val)
    return worst


def scan_P(P: int, s_values) -> list[dict]:
    tables = abs_cos_table(P)
    rows = []
    for s in s_values:
        g, bind = gamma_max_from_tables(tables, s)
        ok = g >= 0.5
        rows.append(
            {
                "P": P,
                "s": int(s),
                "gamma_max": g,
                "theta": (g / s) if ok else 0.0,
                "feasible": bool(ok),
                "bind": bind,
            }
        )
    return rows


def four_prime_products(pmax_prime: int, Pmax: int) -> list[tuple[int, tuple]]:
    primes = [p for p in SMALL_PRIMES if p <= pmax_prime]
    out = []
    for combo in itertools.combinations(primes, 4):
        P = 1
        for p in combo:
            P *= p
        if P <= Pmax:
            out.append((P, combo))
    out.sort()
    return out


def main() -> None:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("=== published row N=2, P=210, s=134 ===", flush=True)
    tables210 = abs_cos_table(210)
    g134, bind134 = gamma_max_from_tables(tables210, 134)
    alpha_pub = alpha_at(tables210, 134, 0.50057)
    pub = {
        "published_s": 134,
        "published_gamma": 0.50057,
        "published_theta": 0.003736,
        "computed_gamma_max": g134,
        "computed_theta_at_gmax": g134 / 134.0,
        "bind": bind134,
        "alpha_at_published_gamma": alpha_pub,
        "published_gamma_feasible": alpha_pub < 1.0,
        "alpha_at_gmax": alpha_at(tables210, 134, g134),
        "alpha_at_gmax_minus": alpha_at(tables210, 134, g134 - 1e-8),
    }
    print(json.dumps(pub, indent=2), flush=True)

    print("\n=== P=210, scan s=1..250 ===", flush=True)
    rows210 = scan_P(210, range(1, 251))
    feas210 = [r for r in rows210 if r["feasible"]]
    feas210.sort(key=lambda r: -r["theta"])
    print(f"feasible s-count: {len(feas210)}", flush=True)
    print("best 12 at P=210:", flush=True)
    for r in feas210[:12]:
        b = r["bind"]
        print(
            f"  s={r['s']:4d}  gamma={r['gamma_max']:.10f}  "
            f"theta={r['theta']:.10f}  bindQ={b['Q']} S={b['S']:.8g}",
            flush=True,
        )

    print("\n=== scan 4-prime products ===", flush=True)
    products = four_prime_products(31, 15015)
    print(f"products: {len(products)}", flush=True)
    s_grid = list(range(1, 41)) + list(range(42, 81, 2)) + list(range(84, 201, 4))
    best_global = None
    perP = []
    for P, combo in products:
        rows = scan_P(P, s_grid)
        feas = [r for r in rows if r["feasible"]]
        if not feas:
            continue
        top = max(feas, key=lambda r: r["theta"])
        top = dict(top)
        top["primes"] = combo
        perP.append(top)
        if best_global is None or top["theta"] > best_global["theta"]:
            best_global = top
            print(
                f"  new best P={P} {combo} s={top['s']} "
                f"theta={top['theta']:.10f} gamma={top['gamma_max']:.10f}",
                flush=True,
            )

    perP.sort(key=lambda r: -r["theta"])
    print("\n=== top 20 (P,s) by theta ===", flush=True)
    for r in perP[:20]:
        print(
            f"  P={r['P']:6d} {r['primes']}  s={r['s']:4d}  "
            f"gamma={r['gamma_max']:.10f}  theta={r['theta']:.10f}",
            flush=True,
        )

    refined = []
    if best_global is not None:
        Pstar = best_global["P"]
        print(f"\n=== refine P={Pstar} s=1..250 ===", flush=True)
        refined_rows = [r for r in scan_P(Pstar, range(1, 251)) if r["feasible"]]
        refined_rows.sort(key=lambda r: -r["theta"])
        refined = refined_rows[:25]
        for r in refined[:12]:
            b = r["bind"]
            print(
                f"  s={r['s']:4d}  gamma={r['gamma_max']:.10f}  "
                f"theta={r['theta']:.10f}  bindQ={b['Q']}",
                flush=True,
            )

    # Also refine P=210 vs the published number
    beat_210 = None
    if feas210:
        beat_210 = feas210[0]
        print(
            f"\nP=210 best theta={beat_210['theta']:.10f} "
            f"(published 0.003736) s={beat_210['s']}",
            flush=True,
        )

    result = {
        "published": pub,
        "best_at_210": beat_210,
        "best_global": best_global,
        "top20": perP[:20],
        "refined_around_best": refined,
        "feas210_top20": feas210[:20],
    }
    out_path = os.path.join(out_dir, "fourier_theta.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(f"\nwrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
