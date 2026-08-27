#!/usr/bin/env python3
"""Replay exact certificates written by this folder.

Rebuilds Gegenbauer polynomials from the BDM recurrence and checks any
dual JSON under certs/.  Also replays polar-vertex maximality: for each
recorded max vertex, rebuilds the five tight planes from the published
coordinates and checks |x|^2 and the remaining inequalities over Q.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import CONFIGS, _dot
from polar_vertices import SCALE, as_int_rows, cramer_column, det5

F = Fraction
HERE = Path(__file__).resolve().parent


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


def verify_duals():
    cert_path = HERE / "certs"
    if not cert_path.exists():
        return {"present": False, "duals": {}}
    report = {}
    ok_all = True
    for path in sorted(cert_path.glob("*.json")):
        data = json.loads(path.read_text())
        items = data.items() if "gegenbauer_coeffs" not in data else [(path.stem, data)]
        # allow either a single dual or a name->dual map
        if "gegenbauer_coeffs" in data:
            items = [(path.stem, data)]
        else:
            items = [(k, v) for k, v in data.items()
                     if isinstance(v, dict) and "gegenbauer_coeffs" in v]
        for name, C in items:
            c = [F(x) for x in C["gegenbauer_coeffs"]]
            T = [F(t) for t in C["T"]]
            deg = len(c) - 1
            polys = gegenbauer_dim5(deg)
            le0 = True
            fT = {}
            for t in T:
                val = sum(c[k] * eval_poly(polys[k], t) for k in range(deg + 1))
                fT[str(t)] = str(val)
                if val > 0:
                    le0 = False
            f1 = sum(c)
            bound = f1 / c[0]
            claimed = F(C["bound"])
            certified = bool(all(x >= 0 for x in c) and le0 and c[0] > 0
                             and bound == claimed)
            excludes = [k for k in (41, 42, 43, 44) if certified and bound < k]
            report[name] = {
                "certified": certified,
                "bound": str(bound),
                "excludes": excludes,
                "f_on_T": fT,
            }
            print(f"dual {name}: certified={certified} bound={bound} "
                  f"excludes={excludes}")
            if not certified:
                ok_all = False
    return {"present": True, "ok": ok_all, "duals": report}


def verify_l5_hits():
    path = HERE / "integer_restricted.json"
    if not path.exists():
        return {"present": False}
    from math import comb
    from delsarte import eval_poly, gegenbauer_dim5
    data = json.loads(path.read_text())
    T = [F(t) for t in data["T_L5"]["T"]]
    polys = gegenbauer_dim5(14)
    ok = True
    report = {}
    for Ns in ("41", "42", "43"):
        N = int(Ns)
        hits = data["T_L5"]["N"][Ns]["integer"]["hits"]
        good = []
        for h in hits:
            if sum(h[str(t)] for t in T) != comb(N, 2):
                ok = False
                good.append(False)
                continue
            A = {t: F(2 * h[str(t)], N) for t in T}
            row_ok = True
            for pk in polys:
                s = eval_poly(pk, F(1))
                for t, at in A.items():
                    s += at * eval_poly(pk, t)
                if s < 0:
                    row_ok = False
            good.append(row_ok)
            if not row_ok:
                ok = False
        report[Ns] = {"n_hits": len(hits), "all_ok": all(good)}
    return {"present": True, "ok": ok, "N": report}


def verify_polar_vertex(name, rec):
    if not rec.get("maximal_as_spherical_code"):
        return {"checked": False, "reason": "not claimed maximal"}
    mv = rec.get("max_vertex")
    if not mv:
        return {"checked": False, "reason": "no max_vertex"}
    pts = CONFIGS[name]()
    rows = as_int_rows(pts)
    idxs = mv["support"]
    A = [rows[i] for i in idxs]
    d = det5(A)
    rhs = (SCALE,) * 5
    z = [cramer_column(A, j, rhs) for j in range(5)]
    if z != mv["z"] or d != mv["d"]:
        return {"checked": True, "ok": False, "reason": "z/d mismatch"}
    # feasibility
    for p in rows:
        ip = sum(z[j] * p[j] for j in range(5))
        if d > 0 and ip > d * SCALE:
            return {"checked": True, "ok": False, "reason": "inequality"}
        if d < 0 and ip < d * SCALE:
            return {"checked": True, "ok": False, "reason": "inequality"}
    z2 = sum(t * t for t in z)
    if z2 * 1 >= 2 * d * d:
        return {"checked": True, "ok": False, "reason": "norm2 >= 2"}
    return {
        "checked": True,
        "ok": True,
        "norm2": rec["max_norm2"],
        "lt_2": True,
    }


def main() -> int:
    report = {"duals": verify_duals()}
    polar_path = HERE / "polar_vertices.json"
    ok = report["duals"].get("ok", True)
    cert_polar = HERE / "certs" / "polar_maximal.json"
    if cert_polar.exists():
        C = json.loads(cert_polar.read_text())
        if C.get("max_norm2") != "5/4" or not C.get("maximal"):
            ok = False
        report["polar_cert"] = {"ok": C.get("maximal") is True}
    if polar_path.exists():
        polar = json.loads(polar_path.read_text())
        preplay = {}
        for name, rec in polar.items():
            preplay[name] = verify_polar_vertex(name, rec)
            print(f"polar {name}: {preplay[name]}")
            if rec.get("maximal_as_spherical_code") and not preplay[name].get("ok"):
                ok = False
        report["polar"] = preplay
    report["l5_hits"] = verify_l5_hits()
    if report["l5_hits"].get("present") and not report["l5_hits"].get("ok"):
        ok = False
    out = HERE / "verify.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
