#!/usr/bin/env python3
"""Replay q5 certificates.

- Any claimed 41-set is checked with exact inner products.
- Dual JSON under certs/ is rebuilt from the Gegenbauer recurrence.
- Type census and leftover SAT/T5 JSON are checked for internal
  consistency (no found_41 without a witness).
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q4 = ROOT / "q4"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))

from configs import _dot  # noqa: E402
from delsarte import eval_poly, gegenbauer_dim5  # noqa: E402
from sphere import extras_and_groups  # noqa: E402

F = Fraction


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


def verify_types():
    path = HERE / "extras_types.json"
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    G = extras_and_groups(4)
    ok = (
        data.get("n_d5") == 40
        and data.get("n_extras") == 1440
        and data.get("n_groups") == 240
        and data.get("n_four_seeds") == 160
        and data.get("n_six_seeds") == 80
        and len(G["extras"]) == 1440
        and not data.get("type_A_clique", {}).get("found_41")
    )
    return {"present": True, "ok": ok, "type_A_omega":
            data.get("type_A_clique", {}).get("best")}


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
        report[path.stem] = {
            "certified": certified,
            "bound": str(sum(c) / c[0]),
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
    if rec["found_41"] and not (HERE / "certs" / "code41.json").exists():
        rec["ok"] = False
        rec["reason"] = "found_41 without witness"
    if data.get("below_44") and not data.get("best_certified"):
        rec["ok"] = False
        rec["reason"] = "below_44 without a bound"
    return rec


def main() -> int:
    report = {
        "types": verify_types(),
        "duals": verify_duals(),
    }
    ok = all(report[k].get("ok", True) for k in report)
    report["code41"] = verify_code41(HERE / "certs" / "code41.json")
    if report["code41"].get("present") and not report["code41"].get("ok"):
        ok = False
    for name in (
        "extras_types.json",
        "seed_graph.json",
        "n1_leftover_sat_k19.json",
        "t5_36_proof.json",
        "t5_share_pruned.json",
        "dual_more.json",
        "construct_more.json",
        "extras_clique.json",
        "t5_share23_c.json",
    ):
        rec = check_search(name)
        report[name] = rec
        if rec.get("present") and not rec.get("ok"):
            ok = False
    report["ok"] = ok
    (HERE / "verify.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Q5_VERIFY", "OK" if ok else "FAIL")
    print(json.dumps({k: report[k] for k in ("types", "code41", "ok")},
                     indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
