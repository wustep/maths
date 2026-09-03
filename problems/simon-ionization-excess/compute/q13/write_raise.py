#!/usr/bin/env python3
"""Build raise_*.json from a complete Gray-code faces dump.

Stdlib only. Does not re-enumerate. Exit 0 iff copositive and
cut > gamma.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


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
            "gray_i",
        }:
            out[k] = int(float(v))
        else:
            out[k] = float(v)
    return out


def main() -> None:
    R = 10.0
    n = 37
    target = 0.9119
    tag = "R10_n37_t0p9119"
    mat = CERTS / f"beta3_mid_{tag}.txt"
    fac = CERTS / f"beta3_mid_faces_{tag}.txt"
    faces = parse_faces(fac)
    nfaces = (1 << n) - 1
    if int(faces.get("n", 0)) != n:
        raise SystemExit("faces n mismatch")
    if abs(float(faces["gamma_target"]) - target) > 1e-12:
        raise SystemExit("faces target mismatch")
    if int(faces.get("gray_i", 0)) < nfaces:
        raise SystemExit(
            f"incomplete dump gray_i={faces.get('gray_i')} < {nfaces}"
        )
    certified = bool(faces.get("copositive") and faces.get("min_mMm_safe", -1) >= 0)
    # P = (q-1)/(q+1), q = R^{1/n}. Hair of 2 ulp vs mpmath interval.
    q = math.exp(math.log(R) / n)
    P = (q - 1.0) / (q + 1.0)
    t0 = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0)
    t0 = t0 - 1.0 / t0
    fmin = 1.5 * t0
    err_hi = P * (1.0 - fmin) * (1.0 + 2e-15) + 2e-16
    gamma = target - err_hi if certified else None
    inv = (1.0 / gamma) if gamma else None
    cut = R / (R + 1.0)
    blob = {
        "source": f"assemble_mid R={R} n={n} (matrix stored; Gray faces)",
        "R": R,
        "n": n,
        "target": target,
        "faces": faces,
        "certified": certified,
        "err_P_hi": err_hi,
        "P_max_hi": P * (1.0 + 2e-15) + 1e-16,
        "compact_gamma": gamma,
        "compact_inv": inv,
        "cut": cut,
        "split_gamma": (min(gamma, cut) if gamma else None),
        "split_inv": (1.0 / min(gamma, cut) if gamma else None),
        "matrix": str(mat.relative_to(HERE)),
        "faces_path": str(fac.relative_to(HERE)),
    }
    out = CERTS / f"raise_{tag}.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps({k: blob[k] for k in (
        "certified", "compact_gamma", "compact_inv", "split_inv", "cut"
    )}, indent=2))
    print("wrote", out)
    if not certified:
        raise SystemExit("write_raise.py FAIL (not copositive)")
    if gamma is None or cut <= gamma:
        raise SystemExit("write_raise.py FAIL (cut does not exceed gamma)")
    if inv is None or inv >= 1.1010:
        raise SystemExit("write_raise.py FAIL (does not beat 1.1010)")
    print("write_raise.py PASS")


if __name__ == "__main__":
    main()
