#!/usr/bin/env python3
"""Lieb still gives the best integers at Z=2..6 under the q9 envelope.

A leading coefficient above 1 cannot bound N0(Z)-Z. The simplified
q9 form N_c < 1.1017 Z + 3.936 Z^{1/3} sits above 2Z+1 on this
range, so it excludes no new integer.

Writes certs/smallz.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE.parent / "certs"


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = []
    any_new = False
    for Z in range(2, 7):
        lieb = 2 * Z + 1
        hps = 1.1017 * Z + 3.936 * (Z ** (1.0 / 3.0))
        nam = 1.22 * Z + 3.0 * (Z ** (1.0 / 3.0))
        lieb_int = 2 * Z  # N_c <= 2Z from N_c < 2Z+1
        hps_int = math.floor(hps - 1e-12)
        new_int = hps_int < lieb_int
        any_new = any_new or new_int
        rows.append(
            {
                "Z": Z,
                "Lieb_2Z+1": lieb,
                "Lieb_integer_Nc_le": lieb_int,
                "q9_1.1017_3.936": hps,
                "Nam_1.22_3": nam,
                "q9_excludes_new_integer": new_int,
            }
        )
    blob = {
        "status": "residue",
        "reason": (
            "Lieb N_c<2Z+1 still excludes the most integers at Z=2..6. "
            "The q9 simplified envelope sits above 2Z+1 there. A leading "
            "coefficient >1 cannot bound N0(Z)-Z."
        ),
        "rows": rows,
    }
    out = CERTS / "smallz.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps(blob, indent=2))
    if any_new:
        raise SystemExit("smallz.py unexpected: q9 envelope beats Lieb integers")
    print("smallz.py PASS (finite-Z integers still residue)")


if __name__ == "__main__":
    main()
