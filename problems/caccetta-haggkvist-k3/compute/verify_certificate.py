#!/usr/bin/env python3
"""Replay a stored F₄ certificate against independently rebuilt matrices.

Exit 0 iff every coordinate of F(c, r) is < -margin.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs

MS = [np.array(M, dtype=float) for M in ac_slices()]
AR_A = np.array(AR, dtype=float)
BR_A = np.array(BR, dtype=float)


def F_coords(c, Q, b, cT, cV, d):
    sos = np.array([float(np.sum(Q * Mk)) for Mk in MS])
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    return sos + (np.array(b) @ (BR_A - c * AR_A)) + cT * it + cV * iv + d * fk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert", type=Path)
    ap.add_argument("--margin", type=float, default=1e-6)
    ap.add_argument("--c", type=float, default=None, help="override c")
    args = ap.parse_args()
    blob = json.loads(args.cert.read_text())
    cert = blob.get("certificate") or blob
    c = args.c if args.c is not None else cert["c"]
    Q = np.array(cert["Q"], dtype=float)
    Q = 0.5 * (Q + Q.T)
    ev = np.linalg.eigvalsh(Q)
    coords = F_coords(c, Q, cert["b"], cert["cT"], cert["cV"], cert["d"])
    worst = float(np.max(coords))
    ok = bool(np.all(coords < -args.margin) and ev.min() >= -1e-8)
    print(f"c={c:.10f}")
    print(f"min_eig(Q)={ev.min():+.6e}")
    print(f"worst F={worst:+.10f}  at r_{int(np.argmax(coords))}")
    print(f"all F < -{args.margin}? {bool(np.all(coords < -args.margin))}")
    print("OK" if ok else "FAIL")
    report = {
        "c": c,
        "min_eig": float(ev.min()),
        "worst_F": worst,
        "worst_index": int(np.argmax(coords)),
        "F": coords.tolist(),
        "ok": ok,
        "margin": args.margin,
    }
    out = Path(__file__).resolve().parent / "certs" / "verify_certificate.json"
    out.write_text(json.dumps(report, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
