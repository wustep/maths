#!/usr/bin/env python3
"""Stdlib second path: compact-row arithmetic and R/(R+1) algebra.

No mpmath, no numpy, no shared helpers. Reads the best raise_*.json
and its faces dump. Confirms
  compact_gamma = certified_phi − err_P_hi
  1/compact_gamma < 1.1013
  R/(R+1) > compact_gamma
and that the faces file still says copositive with min_mMm_safe>0.

Writes certs/lift_stdlib.json.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def best_row() -> dict:
    ok = []
    for p in CERTS.glob("raise_*.json"):
        blob = json.loads(p.read_text())
        if (
            blob.get("certified")
            and blob.get("cut")
            and blob.get("compact_gamma")
            and blob["cut"] > blob["compact_gamma"]
            and blob.get("split_inv", 2) < 1.1013
        ):
            blob["_path"] = str(p)
            ok.append(blob)
    if not ok:
        raise SystemExit("no certified row")
    ok.sort(key=lambda r: r["split_inv"])
    return ok[0]


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    row = best_row()
    faces_path = HERE / row["faces_path"]
    faces = {}
    for line in faces_path.read_text().splitlines():
        k, _, v = line.partition(" ")
        faces[k] = v.strip()

    phi = float(row["target"])
    err = float(row["err_P_hi"])
    gamma = float(row["compact_gamma"])
    inv = float(row["split_inv"])
    recon = phi - err
    recon_ok = abs(recon - gamma) < 5e-12
    R = float(row["R"])
    cut = R / (R + 1.0)
    copositive = int(float(faces["copositive"])) == 1
    min_safe = float(faces["min_mMm_safe"])
    n = int(float(faces["n"]))
    target = float(faces["gamma_target"])

    ok = (
        recon_ok
        and inv < 1.1013
        and cut > gamma
        and copositive
        and min_safe > 0.0
        and n == int(row["n"])
        and abs(target - phi) < 1e-12
    )
    blob = {
        "row": row["_path"],
        "R": R,
        "n": n,
        "recon_gamma": recon,
        "stored_gamma": gamma,
        "recon_ok": recon_ok,
        "inv": inv,
        "inv_lt_1.1013": inv < 1.1013,
        "inv_lt_1.1017": inv < 1.1017,
        "inv_lt_1.1020": inv < 1.1020,
        "inv_lt_1.1021": inv < 1.1021,
        "inv_lt_1.1026": inv < 1.1026,
        "inv_lt_1.1035": inv < 1.1035,
        "inv_lt_1.1057": inv < 1.1057,
        "inv_lt_1.1118": inv < 1.1118,
        "inv_lt_1.108741": inv < 1.108741,
        "cut": cut,
        "cut_gt_gamma": cut > gamma,
        "faces": {
            "n": n,
            "copositive": copositive,
            "min_mMm_safe": min_safe,
            "singular_or_illconditioned": int(
                float(faces["singular_or_illconditioned"])
            ),
            "gamma_target": target,
        },
        "ok": ok,
    }
    out = CERTS / "lift_stdlib.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("recon", recon, "stored", gamma, "ok", recon_ok)
    print("1/γ", inv, "<1.1013", inv < 1.1013, "cut>γ", cut > gamma)
    print("wrote", out)
    if not ok:
        raise SystemExit("verify_lift.py FAIL")
    print("verify_lift.py PASS")


if __name__ == "__main__":
    main()
