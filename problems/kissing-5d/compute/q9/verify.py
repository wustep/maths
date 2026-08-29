#!/usr/bin/env python3
"""Replay q9 certificates and sha256 against the q8 leftover CNFs."""

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
sys.path.insert(0, str(HERE.parent / "q8"))
sys.path.insert(0, str(HERE))

from configs import _dot  # noqa: E402
from sphere import extras_and_groups  # noqa: E402

K30_SHA = "cdec5e76ef58cddadf999f77ec31f7e319764ab867454cdac0ae74f2e53f078c"
GLOBAL_SHA = "5e3c482a76287dca23819cc77270760db57377ed9de50e9559c5d81db6dcac66"

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


def check_search(name: str):
    path = HERE / name
    if not path.exists():
        return {"present": False, "ok": True}
    data = json.loads(path.read_text())
    rec = {"present": True, "ok": True, "found_41": bool(data.get("found_41"))}
    if rec["found_41"] and not (HERE / "certs" / "code41.json").exists():
        rec["ok"] = False
        rec["reason"] = "found_41 without witness"
    if name == "orbits.json":
        if not data.get("transitive"):
            rec["ok"] = False
            rec["reason"] = "orbits not transitive"
        k30 = (data.get("orbits") or {}).get("k30_n0_5") or {}
        if k30.get("orbit_size") != 32 or not k30.get("transitive"):
            rec["ok"] = False
            rec["reason"] = "k30 orbit"
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
            if p.get("cnf_sha256") and p["cnf_sha256"] != K30_SHA:
                rec["ok"] = False
                rec["reason"] = "k30 sha"
    if name == "leftover_sat.json":
        if data.get("found_41") and data.get("sat") is False:
            rec["ok"] = False
            rec["reason"] = "found_41 vs sat"
        if data.get("cnf_sha256") and data["cnf_sha256"] != GLOBAL_SHA:
            rec["ok"] = False
            rec["reason"] = "global sha"
    if name == "replay_k30.json":
        if data.get("ok") is False:
            rec["ok"] = False
            rec["reason"] = "replay_k30"
    return rec


def main() -> int:
    G = extras_and_groups(4)
    report = {
        "graph": {
            "n_d5": 40,
            "n_extras": len(G["extras"]),
            "ok": len(G["extras"]) == 1440 and len(G["D"]) == 40,
        },
        "expected_k30_sha": K30_SHA,
        "expected_global_sha": GLOBAL_SHA,
    }
    ok = report["graph"]["ok"]
    report["code41"] = verify_code41(HERE / "certs" / "code41.json")
    if report["code41"].get("present") and not report["code41"].get("ok"):
        ok = False
    for name in (
        "orbits.json",
        "five_star_sat.json",
        "leftover_sat.json",
        "leftover_sat_status.json",
        "replay_k30.json",
    ):
        rec = check_search(name)
        report[name] = rec
        if rec.get("present") and not rec.get("ok"):
            ok = False
    for stem, sha in (
        ("five_k30_n0_5.cnf.json", K30_SHA),
        ("n1_k19_star5_no21_no13.cnf.json", GLOBAL_SHA),
    ):
        p = HERE / "certs" / stem
        if p.exists():
            data = json.loads(p.read_text())
            match = data.get("sha256") == sha
            report[stem] = {"present": True, "sha_match": match}
            if not match:
                ok = False
    report["ok"] = ok
    (HERE / "verify.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Q9_VERIFY", "OK" if ok else "FAIL")
    print(json.dumps({k: report[k] for k in ("graph", "code41", "ok")},
                     indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
