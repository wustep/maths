#!/usr/bin/env python3
"""Assemble the q7 leading-coefficient certificate.

A dent of q6's 1.1026 (and of printed HPS 1.1185) if every check passes.
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

    checks = {
        "identities_ok": ident.get("status") == "ok",
        "cut_exceeds_gamma": ident.get("cut_exceeds_compact_gamma"),
        "leading_beats_1.1026": leading["checks"]["beats_1.1026"],
        "leading_beats_1.1035": leading["checks"]["beats_1.1035"],
        "leading_beats_1.1057": leading["checks"]["beats_1.1057"],
        "leading_beats_1.1118": leading["checks"]["beats_1.1118"],
        "leading_beats_1.1185": leading["checks"]["beats_1.1185"],
        "leading_printed_ok": leading["checks"]["leading_lt_printed"],
        "stdlib_ok": std.get("ok"),
        "mass_opt_no_counterexample": not mass.get(
            "any_below_cut_with_aspect_ge_R"
        ),
    }
    ok = all(checks.values())
    blob = {
        "arxiv": "2504.18487v1",
        "status": "dent" if ok else "residue",
        "is_new_bound": ok,
        "beats_1.1026": bool(ok and leading["checks"]["beats_1.1026"]),
        "beats_1.1035": bool(ok and leading["checks"]["beats_1.1035"]),
        "beats_1.1057": bool(ok and leading["checks"]["beats_1.1057"]),
        "beats_1.1118": bool(ok and leading["checks"]["beats_1.1118"]),
        "beats_1.1185": bool(ok and leading["checks"]["beats_1.1185"]),
        "beats_1.108741_as_unrestricted": bool(
            ok and leading["checks"]["beats_1.108741_class_number"]
        ),
        "not_the_withdrawn_1.1168": True,
        "used_class": (
            f"aspect≤{ident['R_split']} compact γ, "
            "lifted by mass-opt dichotomy"
        ),
        "beta3_lower": ident["compact_gamma"],
        "leading_hi": leading["printed_leading"],
        "inequalities": leading["inequalities"],
        "checks": checks,
        "pieces": {
            "aspect_identities": "certs/aspect_identities.json",
            "leading": "certs/leading.json",
            "stdlib": "certs/lift_stdlib.json",
            "mass_opt": "certs/mass_opt.json",
            "row": ident.get("source"),
        },
        "reason": (
            "Same HPS §7 chain with a tighter compact γ at the split R "
            "where R/(R+1) still exceeds γ. Mass-stationary measures of "
            "aspect ≥ R have Q>R/(R+1). Atomic measures reduce to one of "
            "those two classes. General radial D_3: truncate then "
            "approximate by finite spherical shells. Not the withdrawn "
            "1.1168. Not a class-only use of the aspect-≤4 number 1.1087."
            if ok
            else "a check failed; do not claim a leading-coefficient dent"
        ),
    }
    out = CERTS / "lift.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("status:", blob["status"])
    print("checks:", checks)
    print("printed leading", blob["leading_hi"])
    print("wrote", out)
    if not ok:
        raise SystemExit("lift_cert.py residue")
    print("lift_cert.py PASS")


if __name__ == "__main__":
    main()
