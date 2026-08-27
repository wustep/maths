#!/usr/bin/env python3
"""Second path: regular tetrahedron shows alpha_4,2 cannot exclude N=4 at Z=2.

Independent of alpha_n.py. Vertices (±1,±1,±1) with even number of minuses.
All |x|=sqrt(3), all pairwise |x-y|=sqrt(8). Then

    alpha = 6 * (3+3) / sqrt(8)  /  (3 * 4 * sqrt(3))
          = 9*sqrt(2) / (12*sqrt(3))
          = sqrt(6)/4.

Need alpha*3 < 2, i.e. 3*sqrt(6) < 8, i.e. 9*6 < 64, i.e. 54 < 64.

stdlib only.

Replay: python3 verify_tetra.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

TET = (
    (1.0, 1.0, 1.0),
    (1.0, -1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (-1.0, -1.0, 1.0),
)


def main() -> None:
    rs = [math.sqrt(sum(c * c for c in p)) for p in TET]
    if any(abs(r - math.sqrt(3.0)) > 1e-15 for r in rs):
        raise SystemExit("vertex radius is not sqrt(3)")
    dists = []
    num = 0.0
    for i, a in enumerate(TET):
        for b in TET[i + 1 :]:
            d = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
            dists.append(d)
            num += (rs[i] ** 2 + math.sqrt(sum(c * c for c in b)) ** 2) / d
    if any(abs(d - math.sqrt(8.0)) > 1e-15 for d in dists):
        raise SystemExit("pair distance is not sqrt(8)")
    den = 3.0 * sum(rs)
    alpha = num / den
    closed = math.sqrt(6.0) / 4.0
    if abs(alpha - closed) > 1e-14:
        raise SystemExit(f"alpha {alpha} != sqrt(6)/4 {closed}")
    if 54 >= 64:
        raise SystemExit("54 < 64 failed")
    # 3*alpha < 2 from the integer comparison, not from floats.
    if 3 * 3 * 6 >= 8 * 8:
        raise SystemExit("3 sqrt(6) < 8 failed")
    blob = {
        "is_new_bound": False,
        "statement": (
            "alpha_4,2 <= sqrt(6)/4, hence alpha_4,2 * 3 < 2. "
            "The s=2 pair geometry cannot exclude N=4 at Z=2 even with "
            "the kinetic remainder dropped."
        ),
        "alpha_tetrahedron": alpha,
        "closed_form": "sqrt(6)/4",
        "integer_comparison": "54 < 64",
        "certifies_dent": False,
    }
    CERTS.mkdir(parents=True, exist_ok=True)
    path = CERTS / "tetra.json"
    path.write_text(json.dumps(blob, indent=2) + "\n")
    print("alpha_4,2 <= sqrt(6)/4 =", closed)
    print("3*sqrt(6) < 8 because 54 < 64")
    print("wrote", path)


if __name__ == "__main__":
    main()
