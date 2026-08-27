#!/usr/bin/env python3
"""Measure the Rédei/Wronskian degree wall, and the unused rising-factorial slice.

For each stored SAT witness, rebuild χ^m = t^p g + h at m = G+1 and record
deg W versus 2k-1. Then rebuild the full rising-factorial w(d,t) and read off
the actual Alon degrees of u,v versus the worst-case k = nm-p+1.

A smaller deg(u),deg(v) than k, uniformly, would be a handle on C>2.
Isolated small-p coincidences are not a dent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pathutil
from gaplib import max_gap_dilates, shakan_lower, uniq_mod


def poly_mul(a: list[int], b: list[int], p: int) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if not ai:
            continue
        for j, bj in enumerate(b):
            if bj:
                out[i + j] = (out[i + j] + ai * bj) % p
    return out


def poly_add(a: list[int], b: list[int], p: int) -> list[int]:
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        av = a[i] if i < len(a) else 0
        bv = b[i] if i < len(b) else 0
        out[i] = (av + bv) % p
    return out


def poly_deg(a: list[int]) -> int:
    for i in range(len(a) - 1, -1, -1):
        if a[i]:
            return i
    return -1


def poly_deriv(a: list[int], p: int) -> list[int]:
    if len(a) <= 1:
        return [0]
    return [(i * a[i]) % p for i in range(1, len(a))]


def poly_scale(a: list[int], c: int, p: int) -> list[int]:
    return [(c * x) % p for x in a]


def chi_poly(A: list[int], p: int) -> list[int]:
    """χ(t) = ∏(t+a)."""
    w = [1]
    for a in A:
        w = poly_mul(w, [a % p, 1], p)
    return w


def pow_poly(base: list[int], e: int, p: int) -> list[int]:
    out = [1]
    for _ in range(e):
        out = poly_mul(out, base, p)
    return out


def split_tp(f: list[int], p: int) -> tuple[list[int], list[int]]:
    """Write f = t^p g + h with deg h < p (as polynomials, not functions)."""
    h = f[:p] + [0] * max(0, p - len(f))
    h = h[:p]
    g = f[p:] if len(f) > p else [0]
    if not g:
        g = [0]
    return g, h


def wronskian(g: list[int], h: list[int], p: int) -> list[int]:
    gp, hp = poly_deriv(g, p), poly_deriv(h, p)
    return poly_add(poly_mul(hp, g, p), poly_scale(poly_mul(h, gp, p), p - 1, p), p)


def rising(x_const: int, x_d: int, x_t: int, m: int, p: int) -> list[list[int]]:
    """∏_{j=1..m} (x_const + x_d d + x_t t) as 2-var array W[deg_d][deg_t]."""
    # start at 1
    W = [[1]]
    for j in range(1, m + 1):
        c0 = (x_const + j) % p
        W = mul_linear(W, c0, x_d % p, x_t % p, p)
    return W


def mul_linear(W: list[list[int]], c0: int, cd: int, ct: int, p: int) -> list[list[int]]:
    di = len(W)
    dj = max((len(row) for row in W), default=1)
    out = [[0] * (dj + 1) for _ in range(di + 1)]
    for i in range(di):
        for j, coef in enumerate(W[i]):
            if not coef:
                continue
            out[i][j] = (out[i][j] + coef * c0) % p
            out[i + 1][j] = (out[i + 1][j] + coef * cd) % p
            out[i][j + 1] = (out[i][j + 1] + coef * ct) % p
    return out


def mul_2d(A: list[list[int]], B: list[list[int]], p: int) -> list[list[int]]:
    di, dj = len(A), max((len(r) for r in A), default=1)
    ei, ej = len(B), max((len(r) for r in B), default=1)
    out = [[0] * (dj + ej - 1) for _ in range(di + ei - 1)]
    for i in range(di):
        for j, a in enumerate(A[i]):
            if not a:
                continue
            for k in range(ei):
                for l, b in enumerate(B[k]):
                    if b:
                        out[i + k][j + l] = (out[i + k][j + l] + a * b) % p
    return out


def build_w_rising(A: list[int], m: int, p: int) -> list[list[int]]:
    """w = d * ∏_a (t + da + 1)_m."""
    W = [[0], [1]]  # the front factor d
    for a in A:
        factor = rising(0, a, 1, m, p)
        W = mul_2d(W, factor, p)
    return W


def alon_degrees(W: list[list[int]], p: int) -> dict:
    """Split w = (t^p-t)u + (d^p-d)v + r by reducing t^p→t, d^p→d.
    Report support of the unreduced high parts (the actual u,v before reduction
    of leftover), and whether the reduced remainder is zero.
    """
    # remainder after t^p=t, d^p=d
    R = [[0] * p for _ in range(p)]
    # collect coefficients that came from t-degree >= p or d-degree >= p
    max_u_tot = -1
    max_v_tot = -1
    n_high_t = 0
    n_high_d = 0
    for i, row in enumerate(W):
        for j, coef in enumerate(row):
            c = coef % p
            if not c:
                continue
            ii, jj = i, j
            high_t = jj >= p
            high_d = ii >= p
            if high_t:
                n_high_t += 1
                max_u_tot = max(max_u_tot, i + (j - p))
            if high_d:
                n_high_d += 1
                max_v_tot = max(max_v_tot, (i - p) + j)
            while ii >= p:
                ii = ii - p + 1
            while jj >= p:
                jj = jj - p + 1
            if ii < p and jj < p:
                R[ii][jj] = (R[ii][jj] + c) % p
    nz = sum(1 for i in range(p) for j in range(p) if R[i][j])
    deg_d = max((i for i, row in enumerate(W) if any(x % p for x in row)), default=-1)
    deg_t = max((j for row in W for j, x in enumerate(row) if x % p), default=-1)
    return {
        "remain_nz": nz,
        "deg_d": deg_d,
        "deg_t": deg_t,
        "n_high_t": n_high_t,
        "n_high_d": n_high_d,
        "max_u_tot": max_u_tot,
        "max_v_tot": max_v_tot,
    }


def analyze_witness(A: list[int], p: int, m: int) -> dict:
    A = uniq_mod(A, p)
    n = len(A)
    k = n * m - p + 1
    chi = chi_poly(A, p)
    f = pow_poly(chi, m, p)
    g, h = split_tp(f, p)
    W = wronskian(g, h, p)
    degW = poly_deg(W)
    degg, degh = poly_deg(g), poly_deg(h)
    rec = {
        "p": p,
        "n": n,
        "m": m,
        "k": k,
        "deg_chi_m": poly_deg(f),
        "deg_g": degg,
        "deg_h": degh,
        "deg_W": degW,
        "bound_2k_1": 2 * k - 1,
        "need_nm1": (m - 1) * n,
        "W_slack": (2 * k - 1) - degW if degW >= 0 else None,
        "k_ge_p": k >= p,
        "middle_empty": k >= p,
    }
    # rising factorial Alon degrees, only when nm+1 is small enough to expand
    if n * m + 1 <= 2 * p + 4 and n * m <= 80:
        Wr = build_w_rising(A, m, p)
        rec["rising"] = alon_degrees(Wr, p)
        rec["rising"]["k"] = k
        rec["rising"]["worse_than_k"] = {
            "u": rec["rising"]["max_u_tot"] - (k if k >= 0 else 0),
            "v": rec["rising"]["max_v_tot"] - (k if k >= 0 else 0),
        }
    return rec


def load_sat_rows() -> list[dict]:
    path = pathutil.ROOT / "certs" / "sat_G.jsonl"
    rows = []
    for line in path.read_text().splitlines():
        rec = json.loads(line)
        if rec["p"] >= 11:
            rows.append(rec)
    return rows


def main():
    out = []
    for rec in load_sat_rows():
        p, A, G = rec["p"], rec["witness"], rec["G"]
        m = G + 1
        row = analyze_witness(A, p, m)
        row["G"] = G
        row["shakan"] = shakan_lower(p, rec["n"])
        # also peek at C=2.5 and C=3 scales when those m stay < p
        n = rec["n"]
        extras = {}
        for tag, C in (("C25", 2.5), ("C3", 3.0)):
            mC = int(C * p / n)
            if 2 <= mC < p:
                extras[tag] = {
                    "m": mC,
                    "k": n * mC - p + 1,
                    "k_ge_p": n * mC - p + 1 >= p,
                }
        row["larger_C"] = extras
        out.append(row)
        print(
            f"p={p:3d} n={n:2d} m={m:3d} k={row['k']:3d} degW={row['deg_W']:3d} "
            f"2k-1={row['bound_2k_1']:3d} need={row['need_nm1']:3d} "
            f"k>=p={row['k_ge_p']} rising={row.get('rising')}",
            flush=True,
        )
    dest = pathutil.CERTS / "wronskian_slice.json"
    dest.write_text(json.dumps(out, indent=2))
    print("wrote", dest)


if __name__ == "__main__":
    main()
