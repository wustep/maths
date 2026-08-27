#!/usr/bin/env python3
"""Stdlib second path: compact-row arithmetic and 12/13 algebra.

No mpmath, no numpy, no shared helpers. Reads the q2 compact JSON
and the stored faces dump. Confirms
  compact_gamma = certified_phi − err_P_hi
  1/compact_gamma < 1.1185
  12/13 > compact_gamma
and that the faces file still says copositive with min_mMm_safe>0.

Writes certs/lift_stdlib.json.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q2 = HERE.parent / "q2" / "certs"
FACES = Q2 / "beta3_mid_faces_R12_n22.txt"


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    compact = json.loads((Q2 / "beta3_compact.json").read_text())
    row = next(r for r in compact["configs"] if r["R"] == 12)
    faces = {}
    for line in FACES.read_text().splitlines():
        k, _, v = line.partition(" ")
        faces[k] = v.strip()

    phi = float(row["certified_phi"])
    err = float(row["err_P_hi"])
    gamma = float(row["compact_gamma"])
    inv = float(row["compact_inv"])
    recon = phi - err
    # allow tiny decimal-string noise
    recon_ok = abs(recon - gamma) < 5e-12
    cut = 12.0 / 13.0
    copositive = int(float(faces["copositive"])) == 1
    min_safe = float(faces["min_mMm_safe"])
    singular = int(float(faces["singular_or_illconditioned"]))
    n = int(float(faces["n"]))
    target = float(faces["gamma_target"])

    ok = (
        recon_ok
        and inv < 1.1185
        and cut > gamma
        and copositive
        and min_safe > 0.0
        and n == 22
        and abs(target - phi) < 1e-12
    )
    blob = {
        "recon_gamma": recon,
        "stored_gamma": gamma,
        "recon_ok": recon_ok,
        "inv": inv,
        "inv_lt_1.1185": inv < 1.1185,
        "cut_12_13": cut,
        "cut_gt_gamma": cut > gamma,
        "faces": {
            "n": n,
            "copositive": copositive,
            "min_mMm_safe": min_safe,
            "singular_or_illconditioned": singular,
            "gamma_target": target,
        },
        "ok": ok,
        "note": (
            "The five singular faces are skipped by the C enumerator "
            "(no interior critical point). Copositivity uses vertices "
            "and the well-conditioned interior critical points."
        ),
    }
    out = CERTS / "lift_stdlib.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("recon", recon, "stored", gamma, "ok", recon_ok)
    print("1/γ", inv, "<1.1185", inv < 1.1185, "12/13>γ", cut > gamma)
    print("faces copositive", copositive, "min_safe", min_safe, "singular", singular)
    print("wrote", out)
    if not ok:
        raise SystemExit("verify_lift.py FAIL")
    print("verify_lift.py PASS")


if __name__ == "__main__":
    main()
