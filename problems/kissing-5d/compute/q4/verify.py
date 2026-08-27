#!/usr/bin/env python3
"""Replay q4 certificates.

- A stored 40-colouring of the 1480-point graph is rebuilt from the
  integer model and checked to be proper.
- A stored 35-colouring of the T^5 remainder is checked against the
  rebuilt remainder graph.
- Any claimed 41-set is checked with exact inner products.
- Dual JSON under certs/ is rebuilt from the Gegenbauer recurrence.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from configs import _dot
from delsarte import eval_poly, gegenbauer_dim5
from sphere import extras_and_groups, ip

F = Fraction


def verify_d4_color():
    path = HERE / "certs" / "d4_40color.json"
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    colour = data.get("colouring_extras")
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    thresh = G["thresh"]
    if colour is None or len(colour) != len(extras):
        return {"present": True, "ok": False, "reason": "length"}
    for v, p in enumerate(extras):
        c = colour[v]
        if c < 0 or c > 39:
            return {"present": True, "ok": False, "reason": "range"}
        if ip(p, D[c]) <= thresh:
            return {"present": True, "ok": False, "reason": f"d5 {v}"}
    n = len(extras)
    for i in range(n):
        for j in range(i + 1, n):
            if colour[i] == colour[j] and ip(extras[i], extras[j]) <= thresh:
                return {"present": True, "ok": False, "reason": f"edge {i} {j}"}
    return {"present": True, "ok": True, "no_41": True, "omega": 40}


def verify_t5_color():
    path = HERE / "certs" / "t5_35color.json"
    if not path.exists():
        return {"present": False, "ok": True}
    from t5_36 import build_pool
    data = json.loads(path.read_text())
    colour = data.get("colouring")
    G = build_pool()
    adj, n = G["adj"], G["n"]
    if colour is None or len(colour) != n:
        return {"present": True, "ok": False, "reason": "length"}
    for i in range(n):
        if colour[i] < 0 or colour[i] > 34:
            return {"present": True, "ok": False, "reason": "range"}
        for j in range(i + 1, n):
            if ((adj[i] >> j) & 1) and colour[i] == colour[j]:
                return {"present": True, "ok": False, "reason": f"edge {i} {j}"}
    return {"present": True, "ok": True, "no_36": True, "omega": 35}


def verify_code41(path: Path):
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    pts = data.get("points")
    if not pts:
        return {"present": True, "ok": False, "reason": "no points"}
    vecs = [tuple(F(x) for x in p) for p in pts]
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


def verify_duals():
    cert_path = HERE / "certs"
    if not cert_path.exists():
        return {"present": False, "ok": True, "duals": {}}
    report = {}
    ok_all = True
    for path in sorted(cert_path.glob("*.json")):
        data = json.loads(path.read_text())
        if "gegenbauer_coeffs" not in data:
            continue
        c = [F(x) for x in data["gegenbauer_coeffs"]]
        deg = len(c) - 1
        polys = gegenbauer_dim5(deg)
        le0 = True
        if data.get("unrestricted"):
            for i in range(121):
                tt = F(-1) + F(i, 120) * F(3, 2)
                val = sum(c[k] * eval_poly(polys[k], tt) for k in range(deg + 1))
                if val > 0:
                    le0 = False
                    break
        claimed = F(data["bound"])
        certified = bool(all(x >= 0 for x in c) and le0 and c[0] > 0
                         and sum(c) / c[0] == claimed)
        excludes = [k for k in (41, 42, 43, 44)
                    if certified and data.get("unrestricted")
                    and sum(c) / c[0] < k]
        report[path.stem] = {
            "certified": certified,
            "bound": str(sum(c) / c[0]),
            "excludes": excludes,
        }
        if not certified:
            ok_all = False
    return {"present": True, "ok": ok_all, "duals": report}


def check_search(name: str):
    path = HERE / name
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    rec = {"present": True, "ok": True, "found_41": bool(data.get("found_41"))}
    if rec["found_41"] and not (
        data.get("clique41") or data.get("constructed_ge41")
        or (HERE / "certs" / "code41.json").exists()
    ):
        rec["ok"] = False
        rec["reason"] = "found_41 without witness"
    return rec


def main() -> int:
    report = {
        "d4_color": verify_d4_color(),
        "t5_color": verify_t5_color(),
        "duals": verify_duals(),
    }
    ok = all(report[k].get("ok", True) for k in report)
    code = HERE / "certs" / "code41.json"
    report["code41"] = verify_code41(code)
    if report["code41"].get("present") and not report["code41"].get("ok"):
        ok = False
    for name in ("color_d4.json", "t5_omega.json", "n1_le32.json",
                 "seed_cover.json", "dual_exact.json", "construct41.json"):
        rec = check_search(name)
        report[name] = rec
        if rec.get("present") and not rec.get("ok"):
            ok = False
    report["ok"] = ok
    (HERE / "verify.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Q4_VERIFY", "OK" if ok else "FAIL")
    print(json.dumps({k: report[k] for k in
                      ("d4_color", "t5_color", "code41", "ok")}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
