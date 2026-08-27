#!/usr/bin/env python3
"""Assemble the q3 leading-coefficient certificate.

A dent of the printed 1.1185, if every check passes:
  β_3 ≥ compact γ (R=12) for every radial probability in HPS (4.1),
  hence N_c < 1.1118 Z + 3.966 Z^{1/3} (Z≥4)
in the same Section 7 chain.

The lift is the mass-opt dichotomy, not a new face enumeration:
  aspect ≤ 12  →  q2 compact γ
  mass-stationary aspect ≥ 12  →  Q > 12/13 > γ
  any atomic  →  Q ≥ its mass-opt ≥ γ
  general D_3  →  truncate, then atomic approximation (Q continuous
  on compact radial support).

Writes certs/lift.json.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def load(name: str) -> dict:
    return json.loads((CERTS / name).read_text())


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    ident = load("aspect_identities.json")
    leading = load("leading.json")
    std = load("lift_stdlib.json")
    mass = load("mass_opt.json")
    trial = load("trial_atomic.json")

    checks = {
        "identities_ok": ident.get("status") == "ok",
        "cut_exceeds_gamma": ident.get("cut_exceeds_compact_gamma"),
        "leading_beats_1.1185": leading["checks"]["beats_1.1185"],
        "leading_printed_ok": leading["checks"]["leading_lt_1.1118"],
        "stdlib_ok": std.get("ok"),
        "mass_opt_no_counterexample": not mass.get(
            "any_below_cut_with_aspect_ge_12"
        ),
        "trial_below_cut": trial.get("below_12_13"),
    }
    ok = all(checks.values())
    blob = {
        "arxiv": "2504.18487v1",
        "status": "dent" if ok else "residue",
        "is_new_bound": ok,
        "beats_1.1185_in_HPS_theorem": ok,
        "not_the_R4_number": True,
        "compact_class_only_without_lift": "1.108741 at aspect≤4",
        "used_class": "aspect≤12 compact γ, lifted by mass-opt dichotomy",
        "beta3_lower": ident["compact_gamma_R12"],
        "leading_hi": leading["printed_leading"],
        "inequalities": leading["inequalities"],
        "checks": checks,
        "pieces": {
            "aspect_identities": "certs/aspect_identities.json",
            "leading": "certs/leading.json",
            "stdlib": "certs/lift_stdlib.json",
            "mass_opt": "certs/mass_opt.json",
            "trial": "certs/trial_atomic.json",
            "q2_compact_R12": "../q2/certs/beta3_compact.json",
            "q2_faces_R12": "../q2/certs/beta3_mid_faces_R12_n22.txt",
        },
        "reason": (
            "Same HPS §7 chain with β_3 ≥ 0.899526 (R=12 compact γ). "
            "Mass-stationary measures of aspect ≥ 12 have Q>12/13. "
            "Atomic measures reduce to one of those two classes. "
            "General radial D_3 measures: truncate then approximate "
            "by finite spherical shells. Not the withdrawn 1.1168 lift, "
            "and not the unrestricted use of the aspect-≤4 number 1.1087."
            if ok
            else "a check failed; do not claim a leading-coefficient dent"
        ),
    }
    out = CERTS / "lift.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("status:", blob["status"])
    print("checks:", checks)
    print("wrote", out)
    if not ok:
        raise SystemExit("lift_cert.py residue")
    print("lift_cert.py PASS (dent of printed 1.1185)")


if __name__ == "__main__":
    main()
