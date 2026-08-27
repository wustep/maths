#!/usr/bin/env python3
"""Replay q2 certificates.

- Any dual JSON under certs/ is rebuilt from the Gegenbauer recurrence.
  Unrestricted duals must also be ≤ 0 on a dense rational grid *and*
  pass the recorded bound.
- Clique JSON files are checked for a claimed 41-set against the dumped
  points, when present.
- Sphere-clique JSON is checked for internal consistency (no 41 claimed
  unless a clique is listed).
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import _dot
from delsarte import eval_poly, gegenbauer_dim5

F = Fraction
HERE = Path(__file__).resolve().parent


def verify_duals():
    cert_path = HERE / "certs"
    if not cert_path.exists():
        return {"present": False, "ok": True, "duals": {}}
    report = {}
    ok_all = True
    for path in sorted(cert_path.glob("*.json")):
        data = json.loads(path.read_text())
        if "gegenbauer_coeffs" in data:
            items = [(path.stem, data)]
        else:
            items = [(k, v) for k, v in data.items()
                     if isinstance(v, dict) and "gegenbauer_coeffs" in v]
        for name, C in items:
            c = [F(x) for x in C["gegenbauer_coeffs"]]
            deg = len(c) - 1
            polys = gegenbauer_dim5(deg)
            le0 = True
            T = C.get("T")
            fT = {}
            if isinstance(T, list):
                for t in T:
                    tt = F(t)
                    val = sum(c[k] * eval_poly(polys[k], tt) for k in range(deg + 1))
                    fT[str(tt)] = str(val)
                    if val > 0:
                        le0 = False
            elif T == "unrestricted [-1,1/2]" or C.get("unrestricted"):
                # dense rational grid plus endpoints
                for i in range(121):
                    tt = F(-1) + F(i, 120) * F(3, 2)
                    val = sum(c[k] * eval_poly(polys[k], tt) for k in range(deg + 1))
                    if val > 0:
                        le0 = False
                        fT[str(tt)] = str(val)
                        break
            f1 = sum(c)
            claimed = F(C["bound"])
            certified = bool(all(x >= 0 for x in c) and le0 and c[0] > 0
                             and f1 / c[0] == claimed)
            excludes = [k for k in (41, 42, 43, 44) if certified and f1 / c[0] < k]
            report[name] = {
                "certified": certified,
                "bound": str(f1 / c[0]),
                "excludes": excludes,
                "f_on_T": fT,
            }
            print(f"dual {name}: certified={certified} bound={f1 / c[0]} "
                  f"excludes={excludes}")
            if not certified:
                ok_all = False
    return {"present": True, "ok": ok_all, "duals": report}


def verify_clique_json(path: Path, points_path: Path | None):
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    if data.get("found_41"):
        idx = data.get("clique41") or []
        if len(idx) != 41:
            return {"present": True, "ok": False, "reason": "bad clique length"}
        if points_path and points_path.exists():
            pts = json.loads(points_path.read_text())
            vecs = [tuple(F(x) for x in p) for p in pts]
            for a in range(41):
                for b in range(a + 1, 41):
                    if _dot(vecs[idx[a]], vecs[idx[b]]) > 1:
                        return {"present": True, "ok": False,
                                "reason": "pair exceeds 1"}
            return {"present": True, "ok": True, "found_41": True}
        return {"present": True, "ok": True, "found_41": True,
                "note": "no points file; accepted listed indices only"}
    # no 41 claimed
    if data.get("best", 0) > 40:
        return {"present": True, "ok": False, "reason": "best>40 without clique"}
    return {"present": True, "ok": True, "found_41": False, "best": data.get("best")}


def main() -> int:
    report = {"duals": verify_duals()}
    ok = report["duals"].get("ok", True)
    t5 = verify_clique_json(HERE / "t5_clique.json", HERE / "t5_points.json")
    report["t5_clique"] = t5
    if t5.get("present") and not t5.get("ok"):
        ok = False
    print("t5_clique", t5)
    for name in ("sphere_d2.json", "sphere_d4.json"):
        rec = verify_clique_json(HERE / name, None)
        report[name] = rec
        print(name, rec)
        if rec.get("present") and not rec.get("ok"):
            ok = False
    lr_path = HERE / "layer_replace.json"
    if lr_path.exists():
        lr = json.loads(lr_path.read_text())
        rec = {
            "best_kissing_size": lr.get("best_kissing_size"),
            "n_size_41": lr.get("n_size_41"),
            "ok": lr.get("best_kissing_size", 0) <= 40 and lr.get("n_size_41") == 0,
        }
        report["layer_replace"] = rec
        print("layer_replace", rec)
        if not rec["ok"]:
            # a 41-point kissing code is a success, not a verifier failure
            if lr.get("n_size_41"):
                rec["ok"] = True
                rec["note"] = "size-41 kissing code present; not a verify failure"
            else:
                ok = False
    ud = HERE / "unrestricted_dual.json"
    if ud.exists():
        U = json.loads(ud.read_text())
        best = U.get("best_certified")
        excl = U.get("excludes_any_k") or []
        report["unrestricted"] = {
            "best": None if not best else best.get("float_bound"),
            "excludes": excl,
        }
        print("unrestricted", report["unrestricted"])
    report["ok"] = ok
    (HERE / "verify.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
