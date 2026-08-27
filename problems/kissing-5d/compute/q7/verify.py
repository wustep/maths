#!/usr/bin/env python3
"""Replay q7 certificates.

- Any claimed 41-set is checked with exact inner products.
- Dual JSON under certs/ is rebuilt from the Gegenbauer recurrence.
- Search JSON is checked for internal consistency.
- Orbit transitivity and star-cover minima are re-read, not re-proved
  here (run orbits.py / star_cover_min.py in run_all.sh).
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
sys.path.insert(0, str(HERE))

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
    norms = {sum(x * x for x in v) for v in vecs}
    if norms == {F(2)}:
        thresh = F(1)
    elif norms == {F(32)}:
        thresh = F(16)
    else:
        return {"present": True, "ok": False, "reason": "norm"}
    for a in range(41):
        for b in range(a + 1, 41):
            if _dot(vecs[a], vecs[b]) > thresh:
                return {"present": True, "ok": False, "reason": "pair"}
    return {"present": True, "ok": True, "found_41": True,
            "norm": str(next(iter(norms)))}


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
    if name == "orbits.json":
        if not data.get("transitive"):
            rec["ok"] = False
            rec["reason"] = "orbits not transitive"
        if data.get("aut_order") != 3840:
            rec["ok"] = False
            rec["reason"] = "aut_order"
    if name == "star_cover_min.json":
        if data.get("min_star_cover_5") != 5:
            rec["ok"] = False
            rec["reason"] = "min_star_cover_5"
        if data.get("k19_empty_by_cover_5"):
            rec["ok"] = False
            rec["reason"] = "false combinatorial empty"
    if name == "five_star_sat.json":
        for p in data.get("pools", []):
            if p.get("sat") is False:
                trim = (p.get("drat_trim") or {}).get("status")
                if trim not in (None, "VERIFIED"):
                    rec["ok"] = False
                    rec["reason"] = f"drat-trim {trim} on {p.get('name')}"
                if p.get("found_41"):
                    rec["ok"] = False
                    rec["reason"] = "unsat pool claims found_41"
    if name == "leftover_sat.json":
        if data.get("found_41") and data.get("sat") is False:
            rec["ok"] = False
            rec["reason"] = "found_41 vs sat"
    return rec


def main() -> int:
    G = extras_and_groups(4)
    report = {
        "graph": {
            "n_d5": 40,
            "n_extras": len(G["extras"]),
            "ok": len(G["extras"]) == 1440 and len(G["D"]) == 40,
        },
        "duals": verify_duals(),
    }
    ok = report["graph"]["ok"] and report["duals"].get("ok", True)
    report["code41"] = verify_code41(HERE / "certs" / "code41.json")
    if report["code41"].get("present") and not report["code41"].get("ok"):
        ok = False
    for name in (
        "orbits.json",
        "star_cover_min.json",
        "five_star_sat.json",
        "leftover_sat.json",
        "leftover_sat_status.json",
        "leftover_global.json",
        "leftover_global_mode3.json",
        "dual_more.json",
        "replay_five_star.json",
    ):
        rec = check_search(name)
        report[name] = rec
        if rec.get("present") and not rec.get("ok"):
            ok = False
    report["ok"] = ok
    (HERE / "verify.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Q7_VERIFY", "OK" if ok else "FAIL")
    print(json.dumps({k: report[k] for k in ("graph", "code41", "ok")},
                     indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
