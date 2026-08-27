#!/usr/bin/env python3
"""Stdlib rebuild of the mid-radius matrix for the winning row.

Different code path from q2/beta3_kernel.py (no mpmath). Rebuilds
edges, F, A, c, P, err and checks they match the stored C matrix
and the stored compact γ.

Writes certs/rebuild.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def best_row() -> dict:
    ok = []
    for p in CERTS.glob("raise_*.json"):
        blob = json.loads(p.read_text())
        if (
            blob.get("certified")
            and blob.get("cut", 0) > blob.get("compact_gamma", 1)
            and blob.get("split_inv", 2) < 1.1035
        ):
            blob["_path"] = str(p)
            ok.append(blob)
    ok.sort(key=lambda r: r["split_inv"])
    return ok[0]


def t0() -> float:
    u = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0)
    return u - 1.0 / u


def f_ratio(t: float) -> float:
    if t <= 0.0:
        return 1.0
    return (1.0 + t**3) / (1.0 + t**2)


def fmin_on(tlo: float, thi: float, t_star: float, fmin: float) -> float:
    if thi <= t_star:
        return f_ratio(thi)
    if tlo >= t_star:
        return f_ratio(tlo)
    return fmin


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    row = best_row()
    R = float(row["R"])
    n = int(row["n"])
    target = float(row["target"])
    mat = HERE / row["matrix"]
    toks = mat.read_text().split()
    n_m = int(float(toks[0]))
    tgt_m = float(toks[1])
    c_m = [float(x) for x in toks[2 : 2 + n_m]]
    A_m = [float(x) for x in toks[2 + n_m : 2 + n_m + n_m * n_m]]
    if n_m != n or abs(tgt_m - target) > 1e-12:
        raise SystemExit("matrix header mismatch")

    t_star = t0()
    fmin = 1.5 * t_star
    edges = [R ** (i / n) for i in range(n + 1)]
    c = [edges[i] * edges[i + 1] for i in range(n)]
    A = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            corners = []
            for r in (edges[i], edges[i + 1]):
                for u in (edges[j], edges[j + 1]):
                    mn, mx = (r, u) if r <= u else (u, r)
                    corners.append(mn / mx)
            tlo, thi = min(corners), max(corners)
            if edges[i] <= edges[j + 1] and edges[j] <= edges[i + 1]:
                thi = 1.0
            fij = fmin_on(tlo, thi, t_star, fmin)
            A[i][j] = fij * 0.5 * (c[i] + c[j])

    max_c = max(abs(c[i] - c_m[i]) / max(c_m[i], 1e-30) for i in range(n))
    max_A = 0.0
    for i in range(n):
        for j in range(n):
            old = A_m[i * n + j]
            max_A = max(max_A, abs(A[i][j] - old) / max(abs(old), 1e-30))

    q = R ** (1.0 / n)
    P = (q - 1.0) / (q + 1.0)
    err = P * (1.0 - fmin)
    gamma = target - err
    # stored err is an interval upper bound, so rebuilt float err should
    # sit at or below it
    err_hi = float(row["err_P_hi"])
    gamma_stored = float(row["compact_gamma"])
    err_ok = err <= err_hi + 1e-14
    # rebuilt γ (float) should be at least the stored lower bound, up to
    # rounding of the interval upper on P
    gamma_ok = gamma + 1e-12 >= gamma_stored
    match_ok = max_c < 1e-12 and max_A < 5e-12
    ok = match_ok and err_ok and gamma_ok and (1.0 / gamma_stored) < 1.1035

    blob = {
        "R": R,
        "n": n,
        "target": target,
        "max_rel_c": max_c,
        "max_rel_A": max_A,
        "q": q,
        "P": P,
        "fmin": fmin,
        "err_float": err,
        "err_hi_stored": err_hi,
        "gamma_float": gamma,
        "gamma_stored": gamma_stored,
        "match_ok": match_ok,
        "err_ok": err_ok,
        "gamma_ok": gamma_ok,
        "ok": ok,
    }
    out = CERTS / "rebuild.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps(blob, indent=2))
    print("wrote", out)
    if not ok:
        raise SystemExit("verify_rebuild.py FAIL")
    print("verify_rebuild.py PASS")


if __name__ == "__main__":
    main()
