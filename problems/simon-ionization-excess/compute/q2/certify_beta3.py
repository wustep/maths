#!/usr/bin/env python3
"""WITHDRAWN as a global bound on β_3.

The mid-radius face enumeration on a compact window is still a valid
tool (see certify_compact.py). The tail polynomial h(D_L, D_R) used
to lift that window to every Borel probability is false: h(0,1)≈0.991
but the HPS power-law trial has I/D≈0.921 when placed in that tail.
Also I_CC ≥ β D_C is false; the sub-measure bound is I_CC ≥ β D_C M_C.

`main()` rewrites certs/beta3_rad.json as withdrawn and exits 0.
Helpers `write_matrix` / `parse_faces` stay for test_faces_small.py.

Replay of the compact certificate: certify_compact.py.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def write_matrix(blob, gamma_target: float, path: Path) -> None:
    n = blob["n"]
    lines = [f"{n} {gamma_target:.16e}"]
    lines.append(" ".join(f"{float(c):.16e}" for c in blob["rmid2"]))
    for i in range(n):
        lines.append(" ".join(f"{float(blob['A_lo'][i][j]):.16e}" for j in range(n)))
    path.write_text("\n".join(lines) + "\n")


def parse_faces(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        k, _, v = line.partition(" ")
        if k in {
            "n",
            "interior_critical",
            "singular_or_illconditioned",
            "n_faces",
            "copositive",
        }:
            out[k] = int(float(v))
        else:
            out[k] = float(v)
    return out


def main() -> None:
    """Record the withdrawal. Do not rerun the false tail lift."""
    CERTS.mkdir(parents=True, exist_ok=True)
    cert = {
        "status": "withdrawn",
        "is_new_bound": False,
        "beats_1.1185": False,
        "reason": (
            "h(0,1)=1-(1/12)(1-fmin)≈0.991 exceeds the HPS power-law "
            "I/D≈0.921 on a measure supported in a fixed-window tail. "
            "The face enum on the middle window is not a global bound. "
            "See certs/beta3_compact.json (aspect-restricted, residue)."
        ),
        "withdrawn_gamma_inv": "1.116823910980300911670485397084439427267",
        "arxiv": "2504.18487v1",
        "replay": "problems/simon-ionization-excess/compute/q2/run_beta3.sh",
    }
    out = CERTS / "beta3_rad.json"
    out.write_text(json.dumps(cert, indent=2) + "\n")
    print("wrote", out)
    print("certify_beta3.py WITHDRAWN (not a leading-coefficient dent)")


if __name__ == "__main__":
    main()
