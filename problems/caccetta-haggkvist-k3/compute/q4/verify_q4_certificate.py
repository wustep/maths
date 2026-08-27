#!/usr/bin/env python3
"""Replay a q4 F₄ certificate against matrices rebuilt from labeled flags.

Exit 0 iff every F-coordinate is < -margin and Q (and Qe if present) are PSD.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PARENT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(HERE))
from extra_forms import (  # noqa: E402
    CSS_BETA_HKN,
    check_kappa4,
    compute_AC_eta,
    compute_beta_regularity,
    compute_eta_regularity,
    fork_coeffs as fork_coeffs_css,
    ind2_coeffs,
)
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs  # noqa: E402


def sos_eta(Qe, AC):
    return np.einsum("ij,ijk->k", Qe, AC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert", type=Path)
    ap.add_argument("--margin", type=float, default=1e-6)
    args = ap.parse_args()
    ok_k, _ = check_kappa4()
    if not ok_k:
        print("FAIL: rebuilt 4Ψ(κ) does not match HKN (4.7)")
        sys.exit(1)
    blob = json.loads(args.cert.read_text())
    cert = blob.get("certificate") or blob
    c = float(cert["c"])
    css_beta = float(cert.get("css_beta", CSS_BETA_HKN))
    Q = np.array(cert["Q"], dtype=float)
    Q = 0.5 * (Q + Q.T)
    ev = np.linalg.eigvalsh(Q)
    AC, _ = compute_AC_eta()
    Qe = cert.get("Qe")
    Qe = None if Qe is None else np.array(Qe, dtype=float)
    eve = None
    if Qe is not None:
        Qe = 0.5 * (Qe + Qe.T)
        eve = np.linalg.eigvalsh(Qe)
    MS = [np.array(M, dtype=float) for M in ac_slices()]
    sos = np.array([float(np.sum(Q * Mk)) for Mk in MS])
    if Qe is not None:
        sos = sos + sos_eta(Qe, AC)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c) if abs(css_beta - 1.0) < 1e-15 else fork_coeffs_css(c, css_beta))
    AR_A = np.array(AR, dtype=float)
    BR_A = np.array(BR, dtype=float)
    coords = sos + (np.array(cert["b"]) @ (BR_A - c * AR_A)) + float(cert["cT"]) * it
    coords = coords + float(cert["cV"]) * iv + float(cert["d"]) * fk
    extra = cert.get("extra") or []
    if extra:
        rows = [np.array(ind2_coeffs(c), dtype=float)]
        ar1, br1, ar2, br2, _ = compute_beta_regularity()
        for i in range(8):
            rows.append(br1[i] - c * ar1[i])
            rows.append(br2[i] - c * ar2[i])
        ear1, ebr1, ear2, ebr2, _ = compute_eta_regularity()
        for i in range(9):
            rows.append(ebr1[i] - c * ear1[i])
            rows.append(ebr2[i] - c * ear2[i])
        # extra may be a prefix (ind2 only, or ind2+beta, ...)
        for coeff, row in zip(extra, rows):
            coords = coords + float(coeff) * row
    worst = float(np.max(coords))
    psd = ev.min() >= -1e-8 and (eve is None or eve.min() >= -1e-8)
    ok = bool(np.all(coords < -args.margin) and psd)
    print(f"c={c:.10f} css_beta={css_beta}")
    print(f"min_eig(Q)={ev.min():+.6e}")
    if eve is not None:
        print(f"min_eig(Qe)={eve.min():+.6e}")
    print(f"worst F={worst:+.10f}  at r_{int(np.argmax(coords))}")
    print(f"all F < -{args.margin}? {bool(np.all(coords < -args.margin))}")
    print("OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
