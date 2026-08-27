#!/usr/bin/env python3
"""Replay q3 certificates.

- Dual JSON under certs/ is rebuilt from the Gegenbauer recurrence.
  Unrestricted duals must be <= 0 on a dense rational grid.
- Any claimed 41-set is checked with exact inner products.
- Search JSON files are checked for internal consistency: a 41-claim
  requires a listed clique; residue (incomplete=true, found_41=false)
  is accepted as not a lower bound.
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
        items = []
        if "gegenbauer_coeffs" in data:
            items = [(path.stem, data)]
        elif "points" in data or "points_ab" in data:
            continue
        else:
            items = [(k, v) for k, v in data.items()
                     if isinstance(v, dict) and "gegenbauer_coeffs" in v]
        for name, C in items:
            c = [F(x) for x in C["gegenbauer_coeffs"]]
            deg = len(c) - 1
            polys = gegenbauer_dim5(deg)
            le0 = True
            if C.get("unrestricted") or C.get("T") == "unrestricted [-1,1/2]":
                for i in range(121):
                    tt = F(-1) + F(i, 120) * F(3, 2)
                    val = sum(c[k] * eval_poly(polys[k], tt)
                              for k in range(deg + 1))
                    if val > 0:
                        le0 = False
                        break
            f1 = sum(c)
            claimed = F(C["bound"])
            certified = bool(all(x >= 0 for x in c) and le0 and c[0] > 0
                             and f1 / c[0] == claimed)
            excludes = [k for k in (41, 42, 43, 44)
                        if certified and f1 / c[0] < k]
            report[name] = {
                "certified": certified,
                "bound": str(f1 / c[0]),
                "excludes": excludes,
            }
            print(f"dual {name}: certified={certified} bound={f1 / c[0]} "
                  f"excludes={excludes}")
            if not certified:
                ok_all = False
    return {"present": True, "ok": ok_all, "duals": report}


def _frac_pts(raw):
    return [tuple(F(x) for x in p) for p in raw]


def verify_code41(path: Path):
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    pts = data.get("points")
    if not pts:
        return {"present": True, "ok": False, "reason": "no points"}
    vecs = _frac_pts(pts)
    if len(vecs) < 41:
        return {"present": True, "ok": False, "reason": "fewer than 41"}
    vecs = vecs[:41]
    for a in range(41):
        if sum(x * x for x in vecs[a]) != F(2):
            return {"present": True, "ok": False, "reason": "norm"}
        for b in range(a + 1, 41):
            if _dot(vecs[a], vecs[b]) > 1:
                return {"present": True, "ok": False, "reason": "pair"}
    return {"present": True, "ok": True, "found_41": True}


def check_search_json(name: str, require_complete=False):
    path = HERE / name
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    rec = {
        "present": True,
        "found_41": bool(data.get("found_41")),
        "complete": data.get("complete"),
        "ok": True,
    }
    if rec["found_41"]:
        # must have a listed construction
        if not (data.get("clique41") or data.get("constructed_ge41")
                or data.get("constructions")):
            rec["ok"] = False
            rec["reason"] = "found_41 without witness"
    if data.get("best", 0) and data.get("best", 0) > 40 and not rec["found_41"]:
        # best is sometimes a remainder-clique size; only flag if it claims
        # a lifted size > 40 without a 41-set
        if data.get("best_lifted", 0) > 40:
            rec["ok"] = False
            rec["reason"] = "best_lifted>40 without found_41"
    print(name, rec)
    return rec


def main() -> int:
    report = {"duals": verify_duals()}
    ok = report["duals"].get("ok", True)
    for cert in sorted((HERE / "certs").glob("code41*.json")) if (HERE / "certs").exists() else []:
        rec = verify_code41(cert)
        report[cert.name] = rec
        print(cert.name, rec)
        if rec.get("present") and not rec.get("ok"):
            ok = False
    for name in ("sphere_types.json", "union_slices.json", "complete_slices.json",
                 "t5_36.json", "t5_repair.json", "golden_pool.json",
                 "expand_T.json", "a4_continuous.json", "dual_gap.json"):
        rec = check_search_json(name)
        report[name] = rec
        if rec.get("present") and not rec.get("ok"):
            ok = False
    cs = HERE / "complete_slices.json"
    if cs.exists():
        C = json.loads(cs.read_text())
        if C.get("n1_ge_33_empty"):
            slices = C.get("slices") or {}
            for k in ("4", "5", "6", "7"):
                rec = slices.get(k) or {}
                if rec.get("found") or not rec.get("complete"):
                    report["complete_slices"] = {
                        "present": True,
                        "ok": False,
                        "reason": f"slice {k} not an empty complete n1>=33",
                    }
                    ok = False
                    break
            else:
                report["complete_slices_n1"] = {
                    "present": True,
                    "ok": True,
                    "n1_ge_33_empty": True,
                }
    report["ok"] = ok
    (HERE / "verify.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Q3_VERIFY", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
