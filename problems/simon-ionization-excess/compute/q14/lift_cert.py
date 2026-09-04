#!/usr/bin/env python3
"""Assemble the q14 leading-coefficient certificate."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def load(name: str) -> dict:
    return json.loads((CERTS / name).read_text())


def main() -> None:
    span = load("span_bound.json")
    std = load("span_stdlib.json")
    rust = load("span_rs.json")
    leading = load("leading.json")
    checks = {
        "interval_span_ok": span.get("ok"),
        "frozen_q13_faces_ok": all(span.get("face_checks", {}).values()),
        "monotonicity_ok": all(span.get("monotone_checks", {}).values()),
        "stdlib_independent_ok": std.get("ok"),
        "rust_independent_ok": rust.get("ok"),
        "cut_exceeds_gamma": float(span["cut"]) > float(span["beta3_lower"]),
        "leading_printed_ok": leading["checks"]["leading_lt_printed"],
        "leading_beats_q13_1.1006": leading["checks"]["beats_1.1006"],
        "leading_beats_HPS_1.1185": leading["checks"]["beats_1.1185"],
    }
    ok = all(checks.values())
    blob = {
        "arxiv": "2504.18487v1",
        "status": "dent" if ok else "residue",
        "is_new_bound": ok,
        "beats_q13_1.1006": bool(ok and checks["leading_beats_q13_1.1006"]),
        "beta3_lower": span["beta3_lower"],
        "leading_hi": leading["printed_leading"],
        "inequalities": leading["inequalities"],
        "checks": checks,
        "pieces": {
            "interval_span": "certs/span_bound.json",
            "stdlib_decimal": "certs/span_stdlib.json",
            "rust": "certs/span_rs.json",
            "section_7": "certs/leading.json",
            "frozen_faces": span["q13_faces"],
            "frozen_matrix": span["q13_matrix"],
        },
        "reason": (
            "The complete q13 R=10, n=37 faces still certify the discrete "
            "target phi=0.9119. The continuous reweighting loss uses the "
            "certified finite F range [f_min,f(q^2/R)] instead of the coarse "
            "[f_min,1]. The resulting compact gamma remains below the "
            "mass-stationary cut 10/11, so the q3 global lift and HPS Section "
            "7 apply unchanged."
            if ok
            else "a required check failed; do not claim a q14 bound"
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
