#!/usr/bin/env python3
"""Independent replay of the exact restricted Delsarte duals.

Does not import exact_duals.py.  Rebuilds Gegenbauer polynomials of
dimension 5 from the BDM recurrence and evaluates the rational
polynomials recorded in certs/restricted_delsarte.json.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

F = Fraction


def gegenbauer_dim5(max_deg: int):
    polys = [[F(1)]]
    if max_deg == 0:
        return polys
    polys.append([F(0), F(1)])
    for k in range(1, max_deg):
        pk, pkm = polys[k], polys[k - 1]
        acc = [F(0)] * (k + 2)
        for i, c in enumerate(pk):
            acc[i + 1] += F(2 * k + 3) * c
        for i, c in enumerate(pkm):
            acc[i] -= F(k) * c
        den = F(k + 3)
        polys.append([c / den for c in acc])
    return polys


def eval_poly(coeffs, t):
    s, pw = F(0), F(1)
    for c in coeffs:
        s += c * pw
        pw *= t
    return s


def main() -> int:
    cert_path = Path(__file__).resolve().parent / "certs" / "restricted_delsarte.json"
    certs = json.loads(cert_path.read_text())
    ok_all = True
    report = {}
    for name, C in certs.items():
        c = [F(x) for x in C["gegenbauer_coeffs"]]
        T = [F(t) for t in C["T"]]
        deg = len(c) - 1
        polys = gegenbauer_dim5(deg)
        fT = {}
        le0 = True
        for t in T:
            val = sum(c[k] * eval_poly(polys[k], t) for k in range(deg + 1))
            fT[str(t)] = str(val)
            if val > 0:
                le0 = False
        f1 = sum(c[k] * eval_poly(polys[k], F(1)) for k in range(deg + 1))
        f0 = c[0]
        bound = f1 / f0
        nonneg = all(x >= 0 for x in c)
        claimed = F(C["bound"])
        certified = bool(nonneg and le0 and f0 > 0 and bound == claimed)
        excludes = [k for k in (41, 42, 43, 44) if certified and bound < k]
        report[name] = {
            "certified": certified,
            "bound": str(bound),
            "float_bound": float(bound),
            "f_on_T": fT,
            "c_k_nonneg": nonneg,
            "excludes": excludes,
        }
        print(f"{name}: certified={certified} bound={bound} "
              f"({float(bound)}) excludes={excludes}")
        if not certified:
            ok_all = False
    out = Path(__file__).resolve().parent / "verify_certificates.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
